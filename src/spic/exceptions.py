from dataclasses import dataclass
from datetime import datetime

from beartype import beartype
from beartype.vale import Is
from serde import SerdeError, is_serializable
from serde.json import to_json

from .emit import _emit
from .responses import RegisteredContent, Response
from .types import P
from .utils import schema


@dataclass
class HTTPError(Exception):
    status_code: int
    message: str


@beartype
class JSONError(HTTPError):
    message: Is[lambda ob: is_serializable(ob)]
    status_code: int


def send_error(send, exception: HTTPError, *args: P.args, **kwargs: P.kwargs):
    response = Response(
        exception.message,
    )
    if isinstance(exception, JSONError):
        try:
            response = Response(content=to_json(exception.message), content_type=RegisteredContent.JSON)
        except SerdeError:
            pass
    response.status_code = exception.status_code
    return _emit(send, response, *args, **kwargs)


TYPES_TO_JS_TYPE = {
    str: "string",
    int: "number",
    float: "number",
    bool: "boolean",
    datetime: "string",
    dict: "object",
    list: "array",
}


@schema
class StructuredValidationError:
    key: str
    expected: str
    given: str
    sources: list[str]


class ManyValidationErrors(BaseException):
    errors: list[StructuredValidationError]

    def __init__(self, errors: list[StructuredValidationError]):
        self.errors = errors


@schema
class SerializableValidationErrors:
    errors: list[StructuredValidationError]
