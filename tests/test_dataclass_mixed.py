from dataclasses import dataclass

import pytest
from starlette.testclient import TestClient

from src.spic.app import Spic
from src.spic.params import Header, Query
from src.spic.routing import Router


@dataclass
class Test:
    arg_h_str: Header[str]
    arg_h_int: Header[int]
    arg_h_float: Header[float]
    arg_h_bool: Header[bool]
    arg_q_str: Query[str]
    arg_q_int: Query[int]
    arg_q_float: Query[float]
    arg_q_bool: Query[bool]


@pytest.fixture
def client():
    slip = Spic(title="test")

    @slip.get("args-mixed")
    def arg_str(query: Test):
        assert query.arg_h_bool is True
        assert query.arg_h_float == 3.4
        assert query.arg_h_str == "sre"
        assert query.arg_h_int == 4
        assert query.arg_q_bool is True
        assert query.arg_q_float == 3.4
        assert query.arg_q_str == "sre"
        assert query.arg_q_int == 4
        return "200"

    slip.collapse()

    client = TestClient(slip)
    return client


def test_basic_app(client):
    assert (
        client.get(
            "/args-mixed?arg_q_str=sre&arg_q_int=4&arg_q_float=3.4&arg_q_bool=true",
            headers={"Arg-H-Str": "sre", "Arg-H-Int": "4", "Arg-H-Float": "3.4", "Arg-H-Bool": "true"},
        ).status_code
        == 200
    )
