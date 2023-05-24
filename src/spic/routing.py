from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Set

from beartype import beartype
from rich.console import Console

from .defaults import DefaultConsole
from .encoders import json
from .enums import LogLevel
from .func_handler import wrap_endpoint_handler
from .inspect import Preamble, get_path_param_names, inspect_dataclass, inspect_function
from .middleware import Middleware
from .types import C, Decorator, P
from .utils import log_level, safe_path_esc_vars, when_none


@dataclass
class PreRoute:
    path: str
    method: str
    func: C
    content_encoder: Callable[[Any], bytes] = json
    kwargs: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class Route:
    path: str
    methods: list[str]

    # mapping by method
    func: Mapping[str, C]
    path_params: Mapping[str, Set[str]]
    preamble: Mapping[str, Preamble]

    content_encoder: Callable[[Any], bytes] = json
    include_in_schema: bool = field(default=True)


def resolve_path(s: str):
    if s.startswith("/"):
        return s[1:]
    return s


class Router:
    log_level: LogLevel
    console: Console
    middlewares: list[Middleware] = []
    type_validation: bool = False

    prefix: str
    _routes: list[PreRoute]

    hashed: Mapping[str, Route] = {}

    def __init__(self, prefix: str = None, log_level: LogLevel = None, console: Console = None):
        self._routes = []
        self.prefix = when_none(prefix, "/")
        self.log_level = when_none(log_level, LogLevel.follow)
        self.console = when_none(console, DefaultConsole)

    def __repr__(self) -> str:
        return f"Router(id={id(self)}, prefix='{self.prefix}', log_level={self.log_level})"

    def middleware(self, func):
        self.middlewares.append(Middleware(func=func))
        return func

    # def build_middleware_chain(self):
    #     for n, mw in enumerate(self.middlewares):
    #         if not mw.inst_of_intra:
    @property
    def validation(self):
        return self.type_validation

    def enable_validation(self):
        self.type_validation = True

    def _generate_routes(self):
        hashed: dict[str, list[PreRoute]] = {}

        for route in self._routes:
            hashed[route.path] = [*hashed.get(route.path, []), route]

        svc_routes: list[Route] = []
        prefix = self.prefix + "/" if not self.prefix.endswith("/") else ""
        for path, routes in hashed.items():
            handlers = {}
            for route in routes:
                target = resolve_path(safe_path_esc_vars(prefix + resolve_path(path)))
                path_params = get_path_param_names(
                    target,
                )
                preamble = inspect_function(route.func)

                exists = handlers.get(target)

                if self.validation:
                    route.func = beartype(route.func)
                    for cls in preamble.classes:
                        cls.meta.T = beartype(cls.meta.T)

                if not exists:
                    exists = Route(
                        path=target,
                        func={
                            route.method: wrap_endpoint_handler(
                                route.func,
                                preamble,
                                # path_params,
                                route.content_encoder,
                                self.log_level,
                                self.console,
                            )
                        },
                        methods=[route.method],
                        path_params={route.method: path_params},
                        preamble={route.method: preamble},
                        **route.kwargs,
                    )
                else:
                    exists.methods.append(route.method)
                    exists.func[route.method] = wrap_endpoint_handler(
                        route.func,
                        preamble,
                        # path_params,
                        route.content_encoder,
                        self.log_level,
                        self.console,
                    )
                    exists.path_params[route.method] = path_params
                    exists.preamble[route.method] = preamble
                handlers[target] = exists
            svc_routes += list(handlers.values())
        log_level(self.console, self.log_level, LogLevel.trace, f"{self} - Routes Added", svc_routes)
        return svc_routes

    def hash_routes(self):
        svc_routes = self._generate_routes()
        for svc in svc_routes:
            self.hashed[svc.path] = svc

    def _decorate(self, path: str, method: str, model: Any = None, include_in_schema: bool = True):
        if model:
            inspect_dataclass(model)

        def wrapper(func: C):
            self._routes.append(
                PreRoute(
                    path=path,
                    method=method,
                    func=func,
                    kwargs={
                        "include_in_schema": include_in_schema,
                    },
                )
            )
            return func

        return wrapper

    def get(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="GET", **kwargs)

    def post(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="POST", **kwargs)

    def delete(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="DELETE", **kwargs)

    def create(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="CREATE", **kwargs)

    def options(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="OPTIONS", **kwargs)

    def connect(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="CONNECT", **kwargs)

    def patch(self, path: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method="PATCH", **kwargs)

    def custom(self, path: str, method: str, *args: P.args, **kwargs: P.kwargs) -> Decorator:
        return self._decorate(*args, path=path, method=method, **kwargs)
