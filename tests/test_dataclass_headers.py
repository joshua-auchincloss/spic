from dataclasses import dataclass

import pytest
from starlette.testclient import TestClient

from src.spic.app import Spic
from src.spic.params import Header


@dataclass
class Test:
    arg_str: Header[str]
    arg_int: Header[int]
    arg_float: Header[float]
    arg_bool: Header[bool]


@pytest.fixture
def client():
    slip = Spic(title="test")

    @slip.get("args-headers")
    def arg_str(query: Test):
        assert query.arg_bool is True
        assert query.arg_float == 3.4
        assert query.arg_str == "sre"
        assert query.arg_int == 4
        return "200"

    slip.collapse()

    client = TestClient(slip)
    return client


def test_basic_app(client):
    assert (
        client.get(
            "/args-headers", headers={"arg-Str": "sre", "Arg-int": "4", "arg-Float": "3.4", "aRg-BOol": "true"}
        ).status_code
        == 200
    )
