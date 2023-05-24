from http import HTTPStatus

from .exceptions import HTTPError


def error(code: int, detail: str = None):
    def inner():
        return HTTPError(status_code=code, message=detail)

    return inner


NoImplmt = error(HTTPStatus.NOT_IMPLEMENTED, "no implementation")
"""Will always trace exceptions because it means we dont support the type serialization
"""
