from dataclasses import dataclass

import pytest

from src.spic.app import Spic
from src.spic.params import Query

from .methods import BaseTests, receive, send


@dataclass
class Test:
    arg_str: Query.type(str)
    arg_int: Query.type(int)
    arg_float: Query.type(float)
    arg_bool: Query.type(bool)


@pytest.fixture
async def client():
    slip = Spic(title="test")

    @slip.get("args-query")
    def arg_str(query: Test):
        assert query.arg_bool is True
        assert query.arg_float == 3.4
        assert query.arg_str == "sre"
        assert query.arg_int == 4
        return "200"

    await slip({"type": "lifespan"}, receive, send)
    client = BaseTests(slip)
    return client


def test_basic_app(client):
    assert client.get("/args-query?arg_str=sre&arg_int=4&arg_float=3.4&arg_bool=true").status_code == 200
