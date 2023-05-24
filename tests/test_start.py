from starlette.testclient import TestClient

from src.spic.app import Spic

slip = Spic(title="test")


@slip.get("/health")
def mtd():
    return "healthy"


slip.collapse()

client = TestClient(slip)


def test_basic_app():
    assert client.get("/health").status_code == 200
