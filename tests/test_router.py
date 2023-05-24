from starlette.testclient import TestClient

from src.spic.app import Spic
from src.spic.routing import Router

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
slip.collapse()

client = TestClient(slip)


def test_routes():
    assert client.get("/health").status_code == 200
    assert client.get("/prefix/health").status_code == 200
