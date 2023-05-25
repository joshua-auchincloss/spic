from asyncio import Event
from http import HTTPStatus
from typing import TYPE_CHECKING, Awaitable, Callable

from beartype.roar import BeartypeCallException, BeartypeCallHintParamViolation, BeartypeCallHintReturnViolation
from hypercorn.typing import AppWrapper, ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope
from hypercorn.utils import LifespanFailureError
from rich.console import Console

from .__about__ import __version__
from .defaults import DEFAULT_LOG_LEVEL, DefaultConsole
from .emit import _emit
from .encoders import yaml
from .enums import LogLevel
from .exceptions import HTTPError, JSONError, SerializableValidationErrors, send_error
from .func_handler import ManyValidationErrors
from .openapi import OAPI_VERSION, OpenAPISchema, build_references_examples_to_model, get_schema_from_route
from .openapi.models import ExternalDocumentation, Info, Reference, Server
from .request import Request
from .routing import Router
from .types import P
from .utils import log_level, run, safe_path, when_none

if TYPE_CHECKING:
    from typing import TypeVar

    from .middleware import Middleware
    from .types import Lazy

    SpicApp = TypeVar("SpicApp", bound="Spic")
    LifespanFunc = Callable[[SpicApp], None | Awaitable[None]]


class Spic(AppWrapper):
    title: str
    root_path = ""
    routes = []
    startup: list["LifespanFunc"] = []
    shutdown: list["LifespanFunc"] = []
    router: Router
    console: Console
    schema: OpenAPISchema
    middlewares: list["Middleware"] = []
    log_level: LogLevel
    type_validation: bool
    servers: list[Server]
    tags: list[dict]
    external_docs: ExternalDocumentation
    bootstrap: object = None

    __started: Event = Event()

    def __init__(
        self,
        title: str = None,
        console: Console = None,
        prefix: str = None,
        version: str = None,
        log_level: LogLevel = None,
        type_validation: bool = None,
        servers: list[Server] = None,
        tags: list[dict] = None,
        external_docs: ExternalDocumentation = None,
    ):
        self.log_level = when_none(log_level, DEFAULT_LOG_LEVEL)
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
        self.servers = when_none(servers, [])
        self.tags = when_none(tags, [])
        self.external_docs = external_docs
        self.startup.append(self.collapse)

    async def __call__(
        self,
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
        # sync_spawn: Callable = None,
        # call_soon: Callable = None,
    ):
        # print(scope)
        if scope["type"] == "http":
            await self.handle_http(scope, receive, send)
            return
        elif "lifespan" in scope["type"]:
            if self.__started.is_set() and scope["type"] == "lifespan.shutdown":
                await self._handle_lifespan(send, self._call_shutdown, "shutdown")
                return
            else:
                await self._handle_lifespan(send, self._call_startup, "startup")
                self.__started.set()
                return
        else:
            msg = "Only the HTTP protocol is supported"
            raise Exception(msg)

    async def handle_http(self, scope: HTTPScope, receive, send):
        path = safe_path(scope.get("path", "/"))[1:]
        mtd = scope.get("method")
        route = self.router.hashed.get(path)
        if route is None:
            __err__ = f"no path matching {path} with the attempted method ({mtd})"
            await self.send_error(
                send,
                HTTPError(status_code=HTTPStatus.NOT_FOUND, message=__err__),
            )
            return

        elif mtd not in route.methods:
            __err__ = f"invalid method ({mtd}) for path: {path}"
            await self.send_error(
                send,
                HTTPError(status_code=HTTPStatus.METHOD_NOT_ALLOWED, message=__err__),
            )
            return
        handler = route.func.get(mtd)
        self._log(LogLevel.trace, "HANDLER", handler)
        if handler is None or not callable(handler):
            __err__ = "internal server error"
            await self.send_error(
                send,
                HTTPError(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message=__err__),
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
            self._log(LogLevel.trace, "TYPE EXCEPTION", invalid)
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
            if self.log_level.value >= LogLevel.follow.value:
                raise e
            return

    async def send_error(self, send, exception: HTTPError):
        await send_error(
            send,
            exception,
            trace=self.console,
            l_level=self.log_level,
        )

    async def _handle_lifespan(self, send, call: Callable[[], Awaitable[list[LifespanFailureError]]], lifespan: str):
        attempted, failed = await call()
        fail_ct = len(failed)
        iserr = fail_ct != 0
        resp = {"type": f"lifespan.{lifespan}.complete"}
        if iserr:
            resp["type"] = f"lifespan.{lifespan}.failed"
            resp["message"] = [m.message for m in failed]
        col_st = "[bold green]" if not iserr else "[bold red]"
        col_end = "[/bold green]" if not iserr else "[/bold red]"
        self._log(
            LogLevel.follow,
            f"application {lifespan} events completed with {col_st}{fail_ct}{col_end} errors / [green]{attempted}[/green] attempts",  # noqa: E501
        )
        await send(resp)
        if lifespan == "startup" and len(failed) != 0:
            raise failed[0]

    async def _lifespan_op(self, op: "LifespanFunc", stage: str):
        try:
            await run(op)(self)
        except Exception as e:
            raise LifespanFailureError(stage, "failed to start due to start op - " + str(e)) from e

    async def _call_lifecycle_with_attempts(
        self, ops: list["LifespanFunc"], lifespan: str
    ) -> tuple[int, list[LifespanFailureError]]:
        tried = len(ops)
        failed: list[LifespanFailureError] = []
        for op in ops:
            try:
                await self._lifespan_op(op, lifespan)
            except LifespanFailureError as e:
                self._log(LogLevel.follow, f"{lifespan} lifespan exception", e)
                failed.append(e)
        return (tried, failed)

    async def _call_startup(self):
        response = await self._call_lifecycle_with_attempts(self.startup, "startup")
        self.__started.set()
        return response

    async def _call_shutdown(self):
        return await self._call_lifecycle_with_attempts(self.shutdown, "shutdown")

    @property
    def base_schema(self):
        return {
            "openapi": OAPI_VERSION,
            "info": Info(title=self.title, version=self.version),
            "paths": {},
            "tags": self.tags,
            "servers": self.servers,
            "external_docs": self.external_docs,
        }

    def finalize_schema(self):
        schema = self.schema
        refs: list[Reference] = []
        for route in self.routes:
            if route.include_in_schema:
                ref, path = get_schema_from_route(route)
                schema.paths["/" + route.path] = path
                refs += ref
        ref_m = {}
        for ref in refs:
            ref_m[ref.ref] = ref
        schema = build_references_examples_to_model(schema, ref_m)
        self.schema = schema

    def include_router(self, router: Router):
        if self.type_validation:
            router.enable_validation()

        self._log(
            LogLevel.trace,
            f"ADDING ROUTER ({router.prefix})",
        )

        routes = router._generate_routes()
        for route in routes:
            self.router.hashed[route.path] = route

        self._log(LogLevel.trace, "ROUTER ADDED SUCCESSFULLY", router)

    async def collapse(self, _):  # placeholder since this is an on-startup function
        self.add_schema_to_app()
        self.routes += self.router._generate_routes()
        self.finalize_schema()
        self.router.hash_routes()

    def on_startup(self, func: "Lazy"):
        self.startup.append(func)

    def on_shutdown(self, func: "Lazy"):
        self.shutdown.append(func)

    def get(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.get(*args, **kwargs)

    def post(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.post(*args, **kwargs)

    def delete(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.delete(*args, **kwargs)

    def create(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.create(*args, **kwargs)

    def options(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.options(*args, **kwargs)

    def connect(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.connect(*args, **kwargs)

    def patch(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.patch(*args, **kwargs)

    def custom(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.custom(*args, **kwargs)

    def static(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.static(*args, **kwargs)

    def static_dir(self, *args: P.args, **kwargs: P.kwargs):
        return self.router.static_dir(*args, **kwargs)

    def add_schema_to_app(self):
        self.schema = OpenAPISchema(**self.base_schema)

        def openapi_schema():
            return self.schema

        self.get(path="openapi.json", include_in_schema=False)(openapi_schema)
        self.get(path="openapi.yaml", include_in_schema=False, content_encoder=yaml)(openapi_schema)

    def _log(self, gte: LogLevel, *args, **kwargs):
        log_level(self.console, self.log_level, gte, *args, **kwargs)
