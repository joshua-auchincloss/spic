from src.spic.encoders import _grpc_conversion, grpc, json
from .protos.gen.hello_pb2 import Hey

MSG = Hey(hi="string")
EXPECT = '{\n  "hi": "string"\n}'

def test_grpc_conversion():
    json = _grpc_conversion(MSG)
    assert json == EXPECT

def test_grpc_response():
    response = grpc(MSG)
    assert response.content == EXPECT

def test_json_calls_grpc():
    response = json(MSG)
    assert response.content == EXPECT
