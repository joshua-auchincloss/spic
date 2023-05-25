from typing import ParamSpec

from httpx import Response
from starlette.testclient import TestClient

from src.spic.exceptions import HTTPError

P = ParamSpec("P")


async def send(*_, **__):
    pass


receive = send


class BaseTests(TestClient):
    async def wait_startup(self) -> None:
        message = await self.send({"type": "lifespan.startup"})
        assert message["type"] == ("lifespan.startup.complete",)

    @staticmethod
    def asserting(response: Response, status: int = 200):
        assert response.status_code == status

    def basic_get_test(self, endpoint: str, *args: P.args, **kwargs: P.kwargs):
        response = self.get(endpoint, *args, **kwargs)
        self.asserting(response)


def raises_no_implmt(serialize, primitive):
    try:
        serialize(primitive)
        __err__ = "no implmt not raised"
        raise ValueError(__err__) from None
    except HTTPError:
        return
    except:  # noqa: E722
        __err__ = "no implmt not caught"
        raise ValueError(__err__) from None
