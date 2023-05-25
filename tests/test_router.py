import pytest

from src.spic.app import Spic
from src.spic.routing import Router

from .methods import BaseTests, receive, send


@pytest.fixture
async def test_cli():
    slip = Spic(title="test")

    rtr = Router()

    @rtr.get("health")
    def health():
        return "ok"

    rtr2 = Router(prefix="/prefix")

    @rtr2.get("health")
    def health_rtr():
        return "ok"

    slip.include_router(rtr)
    slip.include_router(rtr2)

    await slip({"type": "lifespan"}, receive, send)
    client = BaseTests(slip)
    return client


def test_routes(test_cli):
    assert test_cli.get("/health").status_code == 200
    assert test_cli.get("/prefix/health").status_code == 200
