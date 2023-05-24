from asyncio import iscoroutinefunction
from dataclasses import dataclass
from typing import Optional, TypeVar

from rich.console import Console
from serde import serde

from .enums import LogLevel
from .types import LA, Hdr, Lazy, P

# from logging import getLogger, INFO, ERROR, CRITICAL, DEBUG

# logger = getLogger(__name__)

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


def merged_mapping(hdr1: Hdr, hdr2: Hdr):
    return {**when_none(hdr2, {}), **when_none(hdr1, {})}


def schema(cls=None, *args: P.args, **kwargs: P.kwargs):
    def inner(adaptor):
        return serde(*args, **kwargs)(dataclass(adaptor))

    if cls is None:
        return inner
    return inner(cls)


# LEVEL_TO = {
#     LogLevel.trace:   DEBUG,
#     LogLevel.follow:   INFO,
#     LogLevel.headless: None
# }


def log_level(console: Console, l_level: LogLevel, gt: LogLevel, *args: P.args, **kwargs: P.kwargs):
    if l_level.value >= gt.value and console is not None:
        console.log(*args, **kwargs)
    # level = LEVEL_TO[l_level]
    # if level:
    #     logger.log(level, *args, **kwargs)
