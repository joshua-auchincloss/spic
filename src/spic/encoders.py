from collections.abc import Iterable, Mapping
from dataclasses import is_dataclass
from typing import Any, Callable
from typing import Mapping as TMapping

from serde import is_serializable
from serde.json import to_json as dc_to_json

from .enums import FormatMessageOps, RegisteredContent
from .exception_handlers import NoImplmt
from .responses import Response
from .types import P, T, create_raises_dep_error
from .utils import merged_mapping

try:
    from serde.msgpack import to_msgpack as dc_to_msg
except ImportError:
    dc_to_msg = create_raises_dep_error("pyserde[msgpack]")
try:
    from srsly import json_dumps as mapping_to_json
except ImportError:
    mapping_to_json = create_raises_dep_error("srsly")
try:
    from google.protobuf.json_format import MessageToDict, MessageToJson
    from google.protobuf.message import Message
except ImportError:
    MessageToDict = create_raises_dep_error("protobuf")
    MessageToJson = create_raises_dep_error("protobuf")

    class Message:
        __call__ = create_raises_dep_error("protobuf")


def content_media_handler(content_type: RegisteredContent, *resp_args: P.args, **resp_kwargs: P.kwargs):
    defaults = {}

    def call(encode: Callable[[T], bytes]):
        def inner(obj: T):
            content = encode(obj)
            return Response(
                *resp_args, content=content, content_type=content_type, **merged_mapping(defaults, resp_kwargs)
            )

        return inner

    return call


@content_media_handler(RegisteredContent.TEXT)
def text(obj):
    return str(obj)


@content_media_handler(RegisteredContent.MSGPACK)
def msgpack(obj):
    if is_dataclass(obj):
        msg = dc_to_msg(obj)
    else:
        raise NoImplmt() from obj
    return msg


def message_to(obj: Message, op: FormatMessageOps, *args: P.args, **kwargs: P.kwargs):
    func = MessageToJson if op is FormatMessageOps.to_json else MessageToDict
    try:
        return func(obj, *args, **kwargs)
    except:  # noqa: E722
        raise NoImplmt() from None


def _grpc_conversion(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    if isinstance(obj, list):
        json = mapping_to_json([message_to(o, FormatMessageOps.to_dict) for o in obj])
    else:
        json = message_to(obj, FormatMessageOps.to_json, *args, **kwargs)
    return json


@content_media_handler(RegisteredContent.JSON)
def grpc(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    return _grpc_conversion(obj, *args, **kwargs)


@content_media_handler(RegisteredContent.JSON)
def json(obj):
    if isinstance(obj, str):
        json = obj.encode()
    elif isinstance(obj, (bytes)):
        json = obj
    elif is_dataclass(obj) and is_serializable(obj):
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
    elif isinstance(
        obj,
        (
            Mapping,
            TMapping,
            Iterable,
            dict,
            bool,
            int,
            float,
        ),
    ):
        json = mapping_to_json(obj)
    elif isinstance(obj, Message):
        json = _grpc_conversion(obj)
    else:
        try:
            json = mapping_to_json(obj)
        except:  # noqa: E722
            raise NoImplmt() from obj
    return json
