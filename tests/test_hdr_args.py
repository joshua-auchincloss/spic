import pytest

from src.spic.app import Spic
from src.spic.params import Header

from .methods import BaseTests


@pytest.fixture
def hdr_client():
    app = Spic(title="test")

    @app.get("arg-hdr-str")
    def header_str(string_hdr: Header[str]):
        assert isinstance(string_hdr, str)
        return string_hdr

    @app.get("arg-hdr-int")
    def header_int(intg_hdr: Header[int]):
        assert isinstance(intg_hdr, int)
        return intg_hdr

    @app.get("arg-hdr-bool")
    def header_bool(boolv_hdr: Header[bool]):
        assert isinstance(boolv_hdr, bool)
        return boolv_hdr

    @app.get("arg-hdr-float")
    def header_float(flt_hdr: Header[float]):
        assert isinstance(flt_hdr, float)
        return flt_hdr

    @app.get("basic-header")
    def header_basic(flt: Header[float]):
        assert isinstance(flt, float)
        return flt

    app.collapse()

    client = BaseTests(app)
    return client


def test_header_str(hdr_client):
    hdr_client.basic_get_test("/arg-hdr-str", headers={"String-Hdr": "str"})


def test_header_int(hdr_client):
    hdr_client.basic_get_test("/arg-hdr-int", headers={"Intg-Hdr": "3"})


def test_header_bool(hdr_client):
    hdr_client.basic_get_test("/arg-hdr-bool", headers={"Boolv-Hdr": "True"})


def test_header_float(hdr_client):
    hdr_client.basic_get_test("/arg-hdr-float", headers={"Flt-Hdr": "4.3"})


def test_header_single_wrd(hdr_client):
    hdr_client.basic_get_test("/basic-header", headers={"flt": "4.3"})
