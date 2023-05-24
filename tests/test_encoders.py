from dataclasses import dataclass

from pydantic import BaseModel
from serde import serde
from srsly import json_dumps

from src.spic.encoders import content_encoding, json, msgpack, text
from src.spic.enums import RegisteredContent
from src.spic.params import Query
from src.spic.responses import Response

from .methods import raises_no_implmt


@serde
@dataclass
class DCTest:
    test_str: Query[str]
    test_int: Query[int]


@serde
@dataclass
class DCNestTest:
    dc: DCTest


# no serde
@dataclass
class InvalidT:
    field: str = ""


class BMTest(BaseModel):
    test_str: Query[str]
    test_int: Query[int]


@dataclass
class ClassWithCustAttr:
    test_str: str
    test_int: int

    @property
    def dict(self):
        return {
            "test_str": self.test_str,
            "test_int": self.test_int,
        }

    @property
    def json(self):
        return json_dumps(self.dict)


@dataclass
class ClassWithCustAttrDictOnly:
    test_str: str
    test_int: int

    @property
    def dict(self):
        return {
            "test_str": self.test_str,
            "test_int": self.test_int,
        }


@dataclass
class ClassWithCustCallableDictOnly:
    test_str: str
    test_int: int

    def dict(self):
        return {
            "test_str": self.test_str,
            "test_int": self.test_int,
        }


DC = DCTest("test-value", 42)
BM = BMTest(test_str=DC.test_str, test_int=DC.test_int)
TE = InvalidT(field="field")
DC_CUST = ClassWithCustAttr(test_str=DC.test_str, test_int=DC.test_int)
DC_CUST_DICT = ClassWithCustAttrDictOnly(test_str=DC.test_str, test_int=DC.test_int)
DC_CUST_DICT_CALL = ClassWithCustCallableDictOnly(test_str=DC.test_str, test_int=DC.test_int)


def compared_response(content, media_type: RegisteredContent):
    return Response(content=content, content_type=media_type)


def asserting_eq(res1: Response, res2: Response):
    assert res1.body == res2.body
    assert res1.content_type == res2.content_type


def test_content_encoder_wrapping():
    @content_encoding(RegisteredContent.TEXT)
    def handler(_):
        return "EXPECT"

    response = handler("")
    assert response.content == "EXPECT"
    headers = {o[0]: o[1] for o in response.start.get("headers")}
    assert b"content-type" in headers
    assert headers.get(b"content-type") == RegisteredContent.TEXT.value.encode()


def serialize_json_primitive(primitive, expect):
    asserting_eq(json(primitive), compared_response(expect, RegisteredContent.JSON))


def serialize_msgpack_primitive(primitive, expect):
    asserting_eq(msgpack(primitive), compared_response(expect, RegisteredContent.MSGPACK))


def serialize_text_primitive(primitive, expect):
    asserting_eq(text(primitive), compared_response(expect, RegisteredContent.TEXT))


def test_serialize_bool():
    serialize_json_primitive(True, b"true")


def test_serialize_str():
    serialize_json_primitive("string", b"string")


def test_serialize_int():
    serialize_json_primitive(2, b"2")


def test_serialize_float():
    serialize_json_primitive(3.4, b"3.4")


def test_serialize_byte_passthrough():
    btstr = b'{"field":"value"}'
    serialize_json_primitive(btstr, btstr)


def test_serialize_dataclass():
    serialize_json_primitive(DC, b'{"test_str":"test-value","test_int":42}')


def test_serialize_json_property():
    serialize_json_primitive(DC_CUST, b'{"test_str":"test-value","test_int":42}')


def test_serialize_dict_property():
    serialize_json_primitive(DC_CUST_DICT, b'{"test_str":"test-value","test_int":42}')


def test_serialize_dict_calls():
    serialize_json_primitive(DC_CUST_DICT_CALL, b'{"test_str":"test-value","test_int":42}')


def test_serialize_dataclass_list():
    serialize_json_primitive([DC], b'[{"test_str":"test-value","test_int":42}]')


def test_serialize_dataclass_generator():
    serialize_json_primitive((i for i in [DC]), b'[{"test_str":"test-value","test_int":42}]')


def test_serialize_nesting_dataclass():
    dcx = DCNestTest(DC)
    serialize_json_primitive(dcx, b'{"dc":{"test_str":"test-value","test_int":42}}')


def test_serialize_dataclass_msgpack():
    serialize_msgpack_primitive(DC, b"\x82\xa8test_str\xaatest-value\xa8test_int*")


def test_serialize_dataclass_msgpack_list():
    serialize_msgpack_primitive([DC], b"\x91\x82\xa8test_str\xaatest-value\xa8test_int*")


def test_serialize_empty_list_msgpack():
    serialize_msgpack_primitive([], b"\x90")


def test_serialize_untyped_list_msgpack():
    serialize_msgpack_primitive([1, 2, 3], b"\x93\x01\x02\x03")


def test_serialize_mixed_list_msgpack():
    serialize_msgpack_primitive([1, True, 3], b"\x93\x01\xc3\x03")


def test_serialize_base_model():
    serialize_json_primitive(BM, b'{"test_str": "test-value", "test_int": 42}')


def test_serialize_empty_list():
    serialize_json_primitive(
        [],
        b"[]",
    )


def test_text_str():
    serialize_text_primitive("str", b"str")


def test_text_bytes():
    serialize_text_primitive(b"str", b"str")


def test_text_int():
    serialize_text_primitive(1, b"1")


def test_text_float():
    serialize_text_primitive(1.2, b"1.2")


def test_text_none():
    serialize_text_primitive(None, b"")


def test_json_raises_no_implmt_from_no_serde():
    raises_no_implmt(json, TE)


def test_text_raises_no_implmt_from_invalid_type():
    raises_no_implmt(text, TE)


def test_msgpack_raises_no_implmt_from_invalid_type():
    raises_no_implmt(msgpack, TE)
