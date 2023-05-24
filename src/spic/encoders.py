from collections.abc import Iterable, Mapping
from dataclasses import is_dataclass
from typing import Callable
from typing import Mapping as TMapping

from serde import is_serializable
from serde.json import to_json as dc_to_json
from serde.msgpack import to_msgpack as dc_to_msg
from srsly import json_dumps as mapping_to_json

from .core_exceptions import NoImplmt
from .enums import RegisteredContent
from .responses import Response
from .types import P, T
from .utils import merged_mapping

CONTENT = "Content-Type"


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

    else:
        try:
            json = mapping_to_json(obj)
        except:  # noqa: E722
            raise NoImplmt() from obj
    return json
