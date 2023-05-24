from typing import Annotated, Any, Awaitable, Callable, Mapping, Optional, Tuple, Type, TypeVar, cast
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


AnnotatedTypeNames = {"AnnotatedMeta", "_AnnotatedAlias"}


def get_origin(tp: Type[Any]) -> Optional[Type[Any]]:
    if type(tp).__name__ in AnnotatedTypeNames:
        return cast(Type[Any], Annotated)
    return _get_origin(tp) or getattr(tp, "__origin__", None)


def _generic_get_args(tp: Type[Any]) -> Tuple[Any, ...]:
    if hasattr(tp, "_nparams"):
        return (Any,) * tp._nparams
    try:
        if tp == Tuple[()] and tp == tuple[()]:  # type: ignore[misc]
            return ((),)
    except TypeError:  # pragma: no cover
        pass
    return ()


def get_args(tp: Type[Any]) -> Tuple[Any, ...]:
    if type(tp).__name__ in AnnotatedTypeNames:
        return tp.__args__ + tp.__metadata__
    # the fallback is needed for the same reasons as `get_origin` (see above)
    return _get_args(tp) or getattr(tp, "__args__", ()) or _generic_get_args(tp)
