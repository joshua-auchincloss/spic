from enum import Enum
from typing import Annotated, Any, Callable

from ..request import Request
from ..utils import T


class ParamTypes(Enum):
    Header = "header"
    Cookie = "cookie"
    Body = "body"
    Query = "query"
    Request = "request"


TypeExtractor = Callable[[Any], T]
RequestExtractor = Callable[[Request, str, TypeExtractor], T]


class Param:
    source: ParamTypes
    request_extractor: RequestExtractor

    def __init__(self) -> None:
        pass

    @classmethod
    def new(cls, source: ParamTypes, request_extractor: RequestExtractor):
        cls = cls()
        cls.source = source
        cls.request_extractor = request_extractor
        return cls

    def type(self, typ: T) -> T:
        return self[typ]

    @classmethod
    def __repr__(cls):
        return f"Param(id={hex(id(cls))}, source={cls.source}, request_extractor={cls.request_extractor})"

    def __getitem__(self, typ: T) -> Annotated[T, ParamTypes]:
        return Annotated[typ, self.source]


def casting(t: TypeExtractor, o: T) -> T:
    if isinstance(o, str) and t == bytes:
        return o.encode()
    elif isinstance(o, bytes) and t == str:
        return o.decode()
    return t(o)


def extractor(func) -> RequestExtractor:
    def wrap(cls, request: Request, key: str, extract: TypeExtractor):  # noqa: ARG001
        if extract is Request:
            return request
        value = func(request, key)
        if value is None:
            return value  # defaults
        if not isinstance(value, extract):
            if not (isinstance(value, list) and extract is not bytes):
                return casting(extract, value)
            else:
                return [casting(extract, v) for v in value]
        return value

    return wrap


@extractor
def cookie_extractor(request: Request, key: str):
    return request.cookies.get(key)


def normalize_header(key: str):
    words = key.split("_")
    return "-".join([w.title() for w in words]) if len(words) > 1 else "".join(words)


def normalize_query(key: str):
    key = key.lower().replace("_", "-")
    return key


@extractor
def header_extractor(request: Request, key: str):
    key = normalize_query(key)
    return request.headers.get(key)


@extractor
def query_extractor(request: Request, key: str):
    value = request.query_params.get(key.encode())
    if value:
        return value
    return request.query_params.get(normalize_query(key).encode())


@extractor
def request_extractor(_: Request, __: str = None):
    pass  # never called


class _Request(Param):
    source = ParamTypes.Request
    request_extractor = request_extractor

    def __getitem__(self, key) -> Annotated[Request, ParamTypes.Request]:
        return Annotated[Request, ParamTypes.Request]


class _Cookie(Param):
    source = ParamTypes.Cookie
    request_extractor = cookie_extractor


class _Header(Param):
    source = ParamTypes.Header
    request_extractor = header_extractor


class _Query(Param):
    source = ParamTypes.Query
    request_extractor = query_extractor


class _Body(Param):
    source = ParamTypes.Body
    request_extractor = query_extractor
