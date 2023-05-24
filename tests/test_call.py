import pytest

from src.spic.app import Spic


@pytest.fixture
def test_caller():
    app = Spic()

    @app.get("/health")
    def health():
        return {"st": "ok"}

    return app


SAMPLE = {
    "path": "/health",
    "status": 200,
    "headers": [],
    "body": b"",
    "type": "http",
    "method": "get",
}

__CALLER__ = {"called": False}


def set_called():
    __CALLER__["called"] = True


async def receive(something):  # noqa: ARG001
    pass


async def send(something):
    assert something is not None
    set_called()


@pytest.mark.asyncio
async def test_call(test_caller):
    await test_caller(SAMPLE, receive, send)

    assert __CALLER__.get("called")
