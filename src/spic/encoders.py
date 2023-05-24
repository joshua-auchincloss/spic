from collections.abc import Generator, Mapping
from dataclasses import is_dataclass
from typing import Callable
from typing import Mapping as TMapping

from serde import is_serializable
from serde.json import to_json as dc_to_json

from .enums import FormatMessageOps, RegisteredContent
from .exception_handlers import NoImplmt
from .responses import Response
from .types import P, T, create_raises_dep_error

try:  # no cov
    from serde.msgpack import to_msgpack as dc_to_msg  # no cov
except ImportError:  # no cov
    dc_to_msg = create_raises_dep_error("pyserde[msgpack]")  # no cov
try:
    from msgpack import packb  # no cov
except ImportError:  # no cov
    packb = create_raises_dep_error("msgpack")  # no cov
try:  # no cov
    from srsly import json_dumps as mapping_to_json  # no cov
except ImportError:  # no cov
    mapping_to_json = create_raises_dep_error("srsly")  # no cov
try:  # no cov
    from google.protobuf.json_format import MessageToDict, MessageToJson  # no cov
    from google.protobuf.message import Message  # no cov
except ImportError:  # no cov
    MessageToDict = create_raises_dep_error("protobuf")  # no cov
    MessageToJson = create_raises_dep_error("protobuf")  # no cov

    class Message:
        __call__ = create_raises_dep_error("protobuf")


def content_encoding(content_type: RegisteredContent, *resp_args: P.args, **resp_kwargs: P.kwargs):
    def call(encode: Callable[[T], bytes]):
        def inner(obj: T):
            if isinstance(obj, Generator):
                obj = list(obj)
            content = encode(obj)
            return Response(*resp_args, content=content, content_type=content_type, **resp_kwargs)

        return inner

    return call


@content_encoding(RegisteredContent.TEXT)
def text(obj):
    if isinstance(obj, (bool, int, float, str, bytes)):
        return obj
    elif obj is None:
        return ""
    raise NoImplmt() from None


def _msgpack_obj(obj):
    if is_dataclass(obj) and is_serializable(obj):
        return dc_to_msg(obj)
    try:
        return packb(obj)
    except:  # noqa: E722
        raise NoImplmt() from None


@content_encoding(RegisteredContent.MSGPACK)
def msgpack(obj):
    if not isinstance(obj, list):
        return _msgpack_obj(obj)
    elif len(obj) == 0:
        return packb(obj)
    elif is_dataclass(obj[0]) and is_serializable(obj[0]):
        return dc_to_msg(obj)
    return _msgpack_obj(obj)


def message_to(obj: Message, op: FormatMessageOps, *args: P.args, **kwargs: P.kwargs) -> dict | str:
    func = MessageToJson if op is FormatMessageOps.to_json else MessageToDict
    return func(obj, *args, **kwargs)


def _grpc_conversion(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    isli = isinstance(obj, list)
    if isli and len(obj) != 0 and isinstance(obj[0], Message):
        json: str = mapping_to_json([message_to(o, FormatMessageOps.to_dict) for o in obj])
    elif isli and len(obj) == 0:
        json: str = "[]"
    elif isinstance(obj, Message):
        json: str = message_to(obj, FormatMessageOps.to_json, *args, **kwargs)
    else:
        raise NoImplmt() from None
    return json


@content_encoding(RegisteredContent.JSON)
def grpc(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    return _grpc_conversion(obj, *args, **kwargs)


@content_encoding(RegisteredContent.JSON)
def json(obj):
    if isinstance(obj, str):
        json = obj
    elif isinstance(obj, (bytes)):
        json = obj
    elif isinstance(obj, list) and len(obj) == 0:
        json = "[]"
    elif (is_dataclass(obj) and is_serializable(obj)) or (
        isinstance(obj, list) and is_dataclass(obj[0]) and is_serializable(obj[0])
    ):
        json = dc_to_json(obj)
    elif hasattr(obj, "json"):
        if callable(obj.json):
            json = obj.json()
        else:
            json = obj.json
    elif hasattr(obj, "dict"):
        if callable(obj.dict):
            json = mapping_to_json(obj.dict())
        else:
            json = mapping_to_json(obj.dict)
    elif isinstance(obj, (Message)) or (isinstance(obj, list) and isinstance(obj[0], Message)):
        json = _grpc_conversion(obj)
    elif isinstance(
        obj,
        (
            Mapping,
            TMapping,
            dict,
            bool,
            int,
            float,
        ),
    ):
        json = mapping_to_json(obj)
    else:
        try:
            json = mapping_to_json(obj)
        except:  # noqa: E722
            raise NoImplmt() from None
    return json
