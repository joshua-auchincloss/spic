from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from hypercorn.typing import ASGIReceiveCallable, ASGISendCallable, Scope

from .inspect import inspect_function
from .request import Request

SyncSpawn = Callable[[], Awaitable[None]]
CallSoon = SyncSpawn
Intra = tuple[Scope, ASGIReceiveCallable, ASGISendCallable, SyncSpawn, CallSoon]
IntraMiddleware = Callable[[Scope, ASGIReceiveCallable, ASGISendCallable], Awaitable[None]]
Next = Callable[[Request], Any]
RequestMiddleware = Callable[[Request, Next], Awaitable[None]]


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
