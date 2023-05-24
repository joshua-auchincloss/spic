from http import HTTPStatus

from rich.console import Console

from .emit import emit
from .enums import LogLevel
from .exceptions import HTTPError


def error(code: int, detail: str = None, trace: Console = None, l_level: LogLevel = None):
    @emit(l_level=l_level, trace=trace)
    def inner(send):
        return send, HTTPError(status_code=code, detail=detail)

    return inner


NoImplmt = error(HTTPStatus.NOT_IMPLEMENTED, "no implementation")
