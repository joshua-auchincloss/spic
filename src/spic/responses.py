from dataclasses import dataclass, field
from http import HTTPStatus
from typing import TypedDict, cast

from .enums import RegisteredContent
from .types import Hdr

_HdrInternal = list[tuple[bytes, bytes]]


class ResponseStart(TypedDict):
    """Response start model, containing default args,
    status, and header typing

    Args:
        TypedDict (ResponseBody): model
    """

    type: str
    status: int
    headers: _HdrInternal


class ResponseBody(TypedDict):
    """Response body model, containing default body
    args, body bytes, and header typing

    Args:
        TypedDict (ResponseBody): model
    """

    type: str
    body: bytes
    headers: _HdrInternal


@dataclass
class Response:
    """This is a low-level response class. If you are looking to retrieve parameters
    from an endpoint at runtime, take a look at `slip.params.Request`

    Returns:
        Response: self
    """

    content: bytes | str = field(default=b"")
    headers: Hdr = field(default_factory=dict)
    content_type: str = field(default=RegisteredContent.TEXT)
    status_code: int = field(default=HTTPStatus.OK)

    __content_len_init__: bool = field(default=False)
    __content_length__: bytes = field(default_factory=lambda: b"0")

    @property
    def start(self) -> ResponseStart:
        headers = {k.lower(): v for k, v in self.headers.items()}
        if "content-type" not in headers:
            headers["content-type"] = self.content_type.value
        return {
            "type": "http.response.start",
            "status": self.status_code,
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        }

    @property
    def content_length(self) -> bytes:
        if not self.__content_len_init__:
            self.__content_length__ = "{:.0f}".format(
                len(self.content),
            ).encode()

        return self.__content_length__

    @property
    def body(self) -> ResponseBody:
        """The request body

        Returns:
            ResponseBody: TypedDict representing the object returned by the raw response body
        """
        if not isinstance(self.content, bytes):
            if isinstance(self.content, str):
                self.content = cast(str, self.content).encode()
            elif isinstance(self.content, (int, float)):
                self.content = f"{self.content:.0f}"

        return {
            "type": "http.response.body",
            "body": self.content,
            "headers": [
                (
                    b"content-length",
                    self.content_length,
                )
            ],
        }
