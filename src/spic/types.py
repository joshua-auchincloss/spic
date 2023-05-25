from typing import Annotated, Awaitable, Callable, Mapping, Optional, Tuple, Type, TypeVar, cast
from typing import get_args as _get_args
from typing import get_origin as _get_origin

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
C = Callable[P, T]

Decorator = TypeVar("Decorator", bound=C)

LA = Callable[P, Awaitable[T]]
LS = Callable[P, T]

Lazy = LA | LS

Hdr = Mapping[str, str]

Prim = str | bool | int | float | bytes | dict
PrimI = list[Prim]

Any = dict[str, Prim | PrimI] | PrimI | Prim | None


AnnotatedTypeNames = {"AnnotatedMeta", "_AnnotatedAlias"}


def get_origin(tp: Type[Any]) -> Optional[Type[Any]]:
    if type(tp).__name__ in AnnotatedTypeNames:
        return cast(Type[Any], Annotated)
    return _get_origin(tp) or getattr(tp, "__origin__", None)


def _generic_get_args(tp: Type[Any]) -> Tuple[Any, ...]:
    if hasattr(tp, "_nparams"):
        return (Any,) * tp._nparams
    try:
        if tp == Tuple[()] and tp == tuple[()]:
            return ((),)
    except TypeError:
        pass
    return ()


def get_args(tp: Type[Any]) -> Tuple[Any, ...]:
    if type(tp).__name__ in AnnotatedTypeNames:
        return tp.__args__ + tp.__metadata__
    return _get_args(tp) or getattr(tp, "__args__", ()) or _generic_get_args(tp)


class DependencyError(Exception):
    def __init__(self, pkg: str):
        self.pkg = pkg


def create_raises_dep_error(pkg: str):
    def handle(*_, **__):
        raise DependencyError(pkg)

    return handle
