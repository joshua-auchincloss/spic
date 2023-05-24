from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from hypercorn.typing import ASGIReceiveCallable, ASGISendCallable, Scope

from .inspect import inspect_function
from .request import Request

IntraMiddleware = Callable[[Scope, ASGIReceiveCallable, ASGISendCallable], Awaitable[None]]
Next = Callable[[Request], Any]
RequestMiddleware = Callable[[Request, Next], Awaitable[None]]


async def sample_request_middleware(request: Request, nxt: Next):
    return await nxt(request)


@dataclass
class Middleware:
    func: IntraMiddleware | RequestMiddleware

    @property
    def inst_of_intra(self):
        preamble = inspect_function(self.func)
        for cls in preamble.classes:
            if cls.meta.T is Request:
                return False
        return True
