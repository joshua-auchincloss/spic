from ..request import Request as BaseRequest
from .params import (
    Param,
    ParamTypes,
    _Body,
    _Cookie,
    _Header,
    _Query,
    _Request,
    cookie_extractor,
    extractor,
    header_extractor,
    normalize_header,
    query_extractor,
)

Query = _Query()
Header = _Header()
Cookie = _Cookie()
Body = _Body()
RequestInternal = _Request()
Request = RequestInternal[BaseRequest]

_map = {
    Cookie.source: Cookie,
    Header.source: Header,
    Query.source: Query,
    RequestInternal.source: RequestInternal,
}


def rev(typ: ParamTypes):
    return _map.get(typ)
