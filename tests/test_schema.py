import pytest

from src.spic.app import Spic

from .methods import BaseTests


@pytest.fixture
def schema_client():
    slip = Spic(title="test")
    slip.collapse()
    return BaseTests(slip)


# def test_schema_ok(schema_client: BaseTests):
#     schema_client.basic_get_test("/schema")
