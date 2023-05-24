from typing import Any, Callable

from rich.console import Console

from .enums import LogLevel
from .responses import Response
from .types import Decorator, Lazy, P
from .utils import log_level, run

Emittable = tuple[Any, Response]


async def _emit(send, response: Response, trace: Console, l_level: LogLevel = LogLevel.follow):
    await send(response.start)
    log_level(
        trace,
        l_level,
        LogLevel.trace,
        "[bold blue]response.http.start [/bold blue] SEND OK - [",
        response.status_code,
        "]",
    )
    await send(response.body)
    log_level(
        trace,
        l_level,
        LogLevel.trace,
        "[bold blue]response.http.body [/bold blue] START SEND OK - [",
        response.status_code,
        "]",
    )


def emit(func: Callable[P, Emittable] = None, l_level: LogLevel = None, trace: Console = None) -> Decorator:
    def wrapper(fun):
        func: Lazy = run(fun)

        async def inner(*args: P.args, **kwargs: P.kwargs):
            send, response = await func(*args, **kwargs)
            return await _emit(send=send, response=response, trace=trace, l_level=l_level)

        return inner

    if func is not None and callable(func):
        return wrapper(func)
    return wrapper
