from typing import ParamSpec

from httpx import Response
from starlette.testclient import TestClient

P = ParamSpec("P")


class BaseTests(TestClient):
    @staticmethod
    def asserting(response: Response, status: int = 200):
        assert response.status_code == status

    def basic_get_test(self, endpoint: str, *args: P.args, **kwargs: P.kwargs):
        response = self.get(endpoint, *args, **kwargs)
        self.asserting(response)
