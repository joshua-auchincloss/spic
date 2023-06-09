from asyncio import iscoroutinefunction
from dataclasses import dataclass
from typing import Optional, TypeVar

from rich.console import Console
from serde import field, serde

from .enums import LogLevel
from .types import LA, Lazy, P

T = TypeVar("T")


def safe_path(st: str):
    return st.split("?")[0]


def safe_path_esc_vars(st: str):
    return st.split(":")[0]


def when_none(value: Optional[T] = None, default: T = None):
    if value is None:
        return default
    return value


def run(func: Lazy) -> LA:
    iscoro = iscoroutinefunction(func)

    async def inner(*args, **kwargs):
        if iscoro:
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    return inner


def schema(cls=None, *args: P.args, **kwargs: P.kwargs):
    def inner(adaptor):
        return serde(*args, **kwargs)(dataclass(adaptor))

    if cls is None:
        return inner
    return inner(cls)


def is_none(value):
    return (value is None) | (value == [])


def skip_empty(*args: P.args, **kwargs: P.kwargs):
    return field(*args, **kwargs, skip_if=is_none)


# LEVEL_TO = {
#     LogLevel.trace:   DEBUG,
#     LogLevel.follow:   INFO,
#     LogLevel.headless: None
# }


def log_level(console: Console, l_level: LogLevel, gte: LogLevel, *args: P.args, **kwargs: P.kwargs):
    if l_level.value >= gte.value and console is not None:
        console.log(*args, **kwargs)
