from typing import Any, Iterable, Mapping, Tuple
from urllib.parse import parse_qs

from hypercorn.typing import ASGIVersions
from serde import field

from .utils import schema


@schema
class Request:
    method: str
    path: str
    raw_path: str
    query_string: str
    root_path: str
    scheme: str
    server: str

    asgi: ASGIVersions = field(default_factory=dict)

    client: Tuple[str, int] | None = field(default=None)
    state: Any = field(default_factory=dict)

    type: str = field(default="http", alias="type")
    extensions: dict[str, dict] = field(default_factory=dict)
    http_version: str = field(default="1.1")
    headers: Iterable[Tuple[bytes, bytes]] = field(default_factory=dict)

    _query_params: Mapping[str, str | list[str]] = field(default_factory=dict)
    _query_params_init: bool = field(default=False)

    def __post_init__(
        self,
    ):
        self.headers = {k.decode(): v.decode() for k, v in self.headers}

    @property
    def query_params(self):
        """query_params with keys encoded in utf-8 format

        Returns:
            dict: str-bytes, list[str]
        """
        if not self._query_params_init:
            self._query_params = parse_qs(self.query_string)
            for k, v in self._query_params.items():
                if len(v) == 1:
                    self._query_params[k] = v[0]
        return self._query_params
