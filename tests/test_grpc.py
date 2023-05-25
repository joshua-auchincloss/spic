from src.spic.encoders import _grpc_conversion, grpc, json

from .methods import raises_no_implmt
from .protos.gen.hello_pb2 import Hey

MSG = Hey(hi="string")
EXPECT = '{"hi":"string"}'
EXPECT_DICT = {"hi": "string"}
EXPECT_LI = '[{"hi":"string"}]'


def test_grpc_conversion():
    json = _grpc_conversion(MSG)
    assert json == EXPECT_DICT


def test_grpc_response():
    response = grpc(MSG)
    assert response.content == EXPECT


def test_json_calls_grpc():
    response = json(MSG)
    assert response.content == EXPECT


def test_grpc_list():
    response = grpc([MSG])
    assert response.content == EXPECT_LI


def test_json_calls_grpc_list():
    response = json([MSG])
    assert response.content == EXPECT_LI


def test_grpc_empty_list():
    response = grpc([])
    assert response.content == "[]"


def test_text_raises_no_implmt_non_grpc_type():
    raises_no_implmt(grpc, "s")
    raises_no_implmt(grpc, 2)
    raises_no_implmt(grpc, 2.4)
    raises_no_implmt(grpc, b"s")
    raises_no_implmt(grpc, False)
