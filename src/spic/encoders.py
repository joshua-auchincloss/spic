from collections.abc import Generator, Mapping
from typing import Callable
from typing import Mapping as TMapping

from .enums import RegisteredContent
from .exception_handlers import NoImplmt
from .responses import Response
from .types import P, T, create_raises_dep_error

try:  # no cov
    from serde import is_serializable
    from serde.se import to_dict as dc_to_dict  # no cov
except ImportError:  # no cov
    dc_to_dict = create_raises_dep_error("pyserde")  # no cov
try:
    from msgpack import packb  # no cov
except ImportError:  # no cov
    packb = create_raises_dep_error("msgpack")  # no cov
try:  # no cov
    from srsly import json_dumps as mapping_to_json  # no cov
    from srsly import yaml_dumps
except ImportError:  # no cov
    mapping_to_json = create_raises_dep_error("srsly")  # no cov
try:  # no cov
    from google.protobuf.json_format import MessageToDict  # no cov
    from google.protobuf.message import Message  # no cov
except ImportError:  # no cov
    MessageToDict = create_raises_dep_error("protobuf")  # no cov
    MessageToJson = create_raises_dep_error("protobuf")  # no cov

    class Message:
        __call__ = create_raises_dep_error("protobuf")


def unsafe_can_dc(obj):
    return is_serializable(obj) or is_serializable(obj[0])


def can_cast_to_dc(obj, isli=None):
    if isli:
        return unsafe_can_dc(obj)
    return is_serializable(obj)


def content_encoding(content_type: RegisteredContent, *resp_args: P.args, **resp_kwargs: P.kwargs):
    def call(encode: Callable[[T], bytes]):
        def inner(obj: T):
            resp = Response(*resp_args, content=b"", content_type=content_type, **resp_kwargs)
            if obj is None:
                if content_type == RegisteredContent.JSON:
                    resp.content = b"OKOK"
                return resp
            elif isinstance(obj, Generator):
                obj = list(obj)
            resp.content = encode(obj)
            resp.content_type = content_type
            return resp

        return inner

    return call


@content_encoding(RegisteredContent.TEXT)
def text(obj):
    if isinstance(obj, (bool, int, float, str, bytes)):
        return obj
    raise NoImplmt() from None


def _msgpack_obj(obj):
    isli = isinstance(obj, list)
    if isli and len(obj) == 0:
        return packb(obj)
    elif can_cast_to_dc(obj, isli):
        return packb(dc_to_dict(obj))
    try:
        return packb(obj)
    except:  # noqa: E722
        raise NoImplmt() from None


@content_encoding(RegisteredContent.MSGPACK)
def msgpack(obj):
    return _msgpack_obj(obj)


def unsafe_is_msg(obj):
    if isinstance(obj, Message):
        return True
    return isinstance(obj, list) & isinstance(obj[0], Message)


def _grpc_conversion(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    isli = isinstance(obj, list)
    if isli and len(obj) == 0:
        return []
    elif isli and unsafe_is_msg(obj):
        tgt: list[str] = [MessageToDict(o, *args, **kwargs) for o in obj]
    elif isinstance(obj, Message):
        tgt: str = MessageToDict(obj, *args, **kwargs)
    else:
        raise NoImplmt() from None
    return tgt


@content_encoding(RegisteredContent.JSON)
def grpc(obj: Message | list[Message], *args: P.args, **kwargs: P.kwargs):
    data = _grpc_conversion(obj, *args, **kwargs)
    return mapping_to_json(data)


@content_encoding(RegisteredContent.YAML)
def yaml(obj):
    isli = isinstance(obj, list)
    if isinstance(obj, str):
        tgt = obj
    elif isinstance(obj, bytes):
        tgt = obj
    elif isli and len(obj) == 0:
        tgt = ""
    elif can_cast_to_dc(obj, isli):
        tgt = yaml_dumps(dc_to_dict(obj))
    elif unsafe_is_msg(obj):
        tgt = yaml_dumps(_grpc_conversion(obj))
    else:
        raise NoImplmt() from None
    return tgt


@content_encoding(RegisteredContent.JSON)
def json(obj):
    isli = isinstance(obj, list)
    if obj is None:
        tgt = ""
    elif isinstance(obj, str):
        tgt = obj
    elif isinstance(obj, (bytes)):
        tgt = obj
    elif isli and len(obj) == 0:
        tgt = "[]"
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
        tgt = mapping_to_json(obj)
    elif can_cast_to_dc(obj, isli):
        tgt = mapping_to_json(dc_to_dict(obj))
    elif hasattr(obj, "json"):
        if callable(obj.json):
            tgt = obj.json()
        else:
            tgt = obj.json
    elif hasattr(obj, "dict"):
        if callable(obj.dict):
            tgt = mapping_to_json(obj.dict())
        else:
            tgt = mapping_to_json(obj.dict)
    elif isli and unsafe_is_msg(obj) or isinstance(obj, Message):
        tgt = mapping_to_json(_grpc_conversion(obj))
    else:
        try:
            tgt = mapping_to_json(obj)
        except:  # noqa: E722
            raise NoImplmt() from None
    return tgt
