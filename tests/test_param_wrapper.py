from argparse import Namespace

from starlette.requests import Request

from src.spic.params import extractor

BTS_BASE = [1, 2, 3]

BASE = {
    "str": "string",
    "str-b": "byte-string",
    "cast-b": "byte-string",
    "bool1": "true",
    "bool2": "True",
    "int": "1",
    "float": "2.2",
    "bts": BTS_BASE,
}

HeaderTestReq = Namespace(**{"headers": BASE})

QueryTestReq = Namespace(**{"query_params": BASE})

CookieTestReq = Namespace(**{"cookies": BASE})


@extractor
def wrapped(request: dict, key):
    return request.get(key)


def test_generic_extracts_bool():
    assert wrapped(None, BASE, "bool1", bool) is True
    assert wrapped(None, BASE, "bool2", bool) is True


def test_generic_extracts_str():
    assert wrapped(None, BASE, "str", str) == "string"


def test_generic_preserves_bts():
    assert wrapped(None, BASE, "str-b", bytes) == b"byte-string"


def test_generic_casts_bts():
    assert wrapped(None, BASE, "cast-b", bytes) == b"byte-string"


def test_generic_extracts_numeric():
    assert wrapped(None, BASE, "float", float) == 2.2
    assert wrapped(None, BASE, "int", int) == 1


def test_generic_extracts_bytes():
    assert wrapped(None, BASE, "bts", bytes) == bytes(BTS_BASE)
