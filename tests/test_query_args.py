import pytest

from src.spic.app import Spic
from src.spic.params import Query

from .methods import BaseTests


@pytest.fixture
def q_client():
    slip = Spic(title="test")

    @slip.get("arg-q-str")
    def arg_str(string_q: Query[str]):
        assert isinstance(string_q, str)
        assert string_q == "str"
        return string_q

    @slip.get("arg-q-int")
    def arg_int(intv_q: Query[int]):
        # raise ValueError(intv_q)

        assert isinstance(intv_q, int)
        assert intv_q == 3
        return intv_q

    @slip.get("arg-q-bool")
    def arg_bool(boolv_q: Query[bool]):
        assert isinstance(boolv_q, bool)
        return boolv_q

    @slip.get("arg-q-float")
    def arg_float(flt_q: Query[float]):
        assert isinstance(flt_q, float)
        return flt_q

    slip.collapse()

    return BaseTests(slip)


def test_query_str(q_client):
    # raise SystemExit(1, f"{id(Query), Query}")
    q_client.basic_get_test("/arg-q-str?string_q=str")


def test_query_int(q_client):
    q_client.basic_get_test("/arg-q-int?intv_q=3")


def test_query_bool(q_client):
    q_client.basic_get_test("/arg-q-bool?boolv_q=True")
    q_client.basic_get_test("/arg-q-bool?boolv_q=true")


def test_query_with_dash(q_client):
    q_client.basic_get_test("/arg-q-bool?boolv-q=True")


def test_query_float(q_client):
    q_client.basic_get_test("/arg-q-float?flt_q=3")
