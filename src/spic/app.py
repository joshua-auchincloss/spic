from http import HTTPStatus
from typing import cast

from beartype.roar import BeartypeCallException, BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation
from hypercorn.typing import HTTPScope, Scope
from rich.console import Console

from .__about__ import __version__
from .defaults import DefaultConsole
from .emit import _emit
from .enums import LogLevel
from .exceptions import HTTPError, JSONError, SerializableValidationErrors, send_error
from .func_handler import ManyValidationErrors
from .middleware import Middleware
from .openapi import OAPI_VERSION, OpenAPISchema, get_schema_from_route
from .request import Request
from .routing import Router
from .types import P
from .utils import log_level, safe_path, when_none


class Spic:
    title: str
    root_path = ""
    routes = []
    router: Router
    console: Console
    schema: OpenAPISchema
    middlewares: list[Middleware] = []
    log_level: LogLevel
    type_validation: bool

    def __init__(
        self,
        title: str = None,
        console: Console = None,
        prefix: str = None,
        version: str = None,
        log_level: LogLevel = LogLevel.follow,
        type_validation: bool = None,
    ):
        self.log_level = log_level
        if console is None:
            console = DefaultConsole
        self.console = console
        self.root_path = prefix
        self.title = when_none(title, "SPIC app")
        self.version = when_none(version, f"spic-{__version__}")
        self.router = Router(
            prefix=prefix,
            console=self.console,
            log_level=self.log_level,
        )
        self.type_validation = when_none(type_validation, True)

    async def __call__(self, scope: Scope, receive, send):
        if scope["type"] != "http":
            msg = "Only the HTTP protocol is supported"
            raise Exception(msg)
        scope = cast(HTTPScope, scope)
        path = safe_path(scope.get("path", "/"))[1:]
        mtd = scope.get("method")
        route = self.router.hashed.get(path)
        if route is None:
            __err__ = f"no path matching {path} with the attempted method ({mtd})"
            await send_error(
                send,
                HTTPError(status_code=HTTPStatus.NOT_FOUND, message=__err__),
                l_level=self.log_level,
                trace=self.console,
            )
            return

        elif mtd not in route.methods:
            __err__ = f"invalid method ({mtd}) for path: {path}"
            await send_error(
                send,
                HTTPError(status_code=HTTPStatus.METHOD_NOT_ALLOWED, message=__err__),
                l_level=self.log_level,
                trace=self.console,
            )
            return
        handler = route.func.get(mtd)
        if handler is None or not callable(handler):
            __err__ = "internal server error"
            await send_error(
                send,
                HTTPError(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message=__err__),
                l_level=self.log_level,
                trace=self.console,
            )
            return
        _ = await receive()
        request = Request(**scope)
        try:
            response = await handler(request)
            await _emit(send, response, trace=self.console, l_level=self.log_level)
            return

        except HTTPError as e:
            await self.send_error(send, e)
            return

        except ManyValidationErrors as invalid:
            await self.send_error(
                send,
                JSONError(
                    status_code=HTTPStatus.BAD_REQUEST, message=SerializableValidationErrors(errors=invalid.errors)
                ),
            )
            return

        except (BeartypeCallHintReturnViolation, BeartypeCallException, BeartypeCallHintParamViolation) as invalid:
            root = invalid.culprits  # this is fallback only - we excpect errors to be caught as ManyValidationErrors
            log_level(self.console, self.log_level, LogLevel.trace, "TYPE EXCEPTION", invalid)
            __err__ = f"""invalid parameters for method\nroot:{
                    root
                }\nargs:{
                    invalid.args
                }\nnotes:{
                    invalid._culprits_weakref_and_repr
                }"""
            await self.send_error(send, HTTPError(status_code=HTTPStatus.BAD_REQUEST, message=__err__))
            return
        except Exception as e:
            self.console.log("[bold red]EXCEPTION CAUGHT[/bold red]", e, style="red")
            __err__ = "internal server error"
            await self.send_error(
                send,
                HTTPError(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message=__err__),
            )
            return

    async def send_error(self, send, exception: HTTPError):
        await send_error(
            send,
            exception,
            trace=self.console,
            l_level=self.log_level,
        )

    async def match_paths(self, path):
        pass

    @property
    def base_schema(self):
        return {"openapi": OAPI_VERSION, "info": {"title": self.title, "version": self.version}, "paths": {}}

    def finalize_schema(self):
        schema = self.schema

        for route in self.routes:
            if route.include_in_schema:
                schema.paths[route.path] = get_schema_from_route(route)

        self.schema = schema

    def include_router(self, router: Router):
        if self.type_validation:
            router.enable_validation()

        log_level(
            self.console,
            self.log_level,
            LogLevel.trace,
            f"ADDING ROUTER ({router.prefix})",
        )

        routes = router._generate_routes()
        for route in routes:
            self.router.hashed[route.path] = route

        log_level(self.console, self.log_level, LogLevel.trace, "ROUTER ADDED SUCCESSFULLY", router)

    def collapse(self):
        self.add_schema_to_app()
        self.routes += self.router._generate_routes()
        self.finalize_schema()
        self.router.hash_routes()

    def get(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def post(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def delete(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def create(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def options(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def connect(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def patch(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def custom(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def add_schema_to_app(self):
        self.schema = OpenAPISchema(**self.base_schema)

        def openapi_schema():
            return self.schema

        return self.router.get(path="schema", include_in_schema=False)(openapi_schema)
