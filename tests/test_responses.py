from dataclasses import dataclass

from pydantic import BaseModel
from serde import serde

from src.spic.encoders import content_media_handler, json, msgpack
from src.spic.enums import RegisteredContent
from src.spic.params import Query
from src.spic.responses import Response


@serde
@dataclass
class DCTest:
    test_str: Query[str]
    test_int: Query[int]


DC = DCTest("test-value", 42)


@serde
@dataclass
class DCNestTest:
    dc: DCTest


class BMTest(BaseModel):
    test_str: Query[str]
    test_int: Query[int]


def compared_response(content, media_type: RegisteredContent):
    return Response(content=content, content_type=media_type)


def asserting_eq(res1: Response, res2: Response):
    assert res1.body == res2.body
    assert res1.content_type == res2.content_type


def serialize_json_primitive(primitive, expect):
    asserting_eq(json(primitive), compared_response(expect, RegisteredContent.JSON))


def serialize_msgpack_primitive(primitive, expect):
    asserting_eq(msgpack(primitive), compared_response(expect, RegisteredContent.MSGPACK))


def test_serialize_bool():
    serialize_json_primitive(True, b"true")


def test_serialize_str():
    serialize_json_primitive("string", b"string")


def test_serialize_int():
    serialize_json_primitive(2, b"2")


def test_serialize_float():
    serialize_json_primitive(3.4, b"3.4")


def test_serialize_dataclass():
    serialize_json_primitive(DC, b'{"test_str":"test-value","test_int":42}')


def test_serialize_nesting_dataclass():
    dcx = DCNestTest(DC)
    serialize_json_primitive(dcx, b'{"dc":{"test_str":"test-value","test_int":42}}')


def test_serialize_dataclass_msgpack():
    serialize_msgpack_primitive(DC, b"\x82\xa8test_str\xaatest-value\xa8test_int*")


def test_serialize_base_model():
    BM = BMTest(test_str=DC.test_str, test_int=DC.test_int)
    serialize_json_primitive(BM, b'{"test_str": "test-value", "test_int": 42}')
