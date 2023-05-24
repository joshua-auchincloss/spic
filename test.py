from dataclasses import dataclass
from typing import Annotated

from beartype import beartype
from serde import serde

from src.spic.app import Spic
from src.spic.params import Header, Query
from src.spic.routing import Router


@dataclass
class Test:
    arg_str: Header[str]
    arg_int: Header[int]
    arg_float: Header[float]
    arg_bool: Header[bool]


# @serde
@dataclass
class Qu:
    arg1: Query[str]
    arg2: Query[str]
    arg3: Query[int]
    header_str: Header.type(str)

    def dict(self):
        return {
            "arg1": self.arg1,
            "arg2": self.arg2,
            "arg3": self.arg3,
            "header_str": self.header_str,
        }


slip = Spic(title="test")


rtr = Router()


@rtr.get("health")
def health():
    return "ok"


slip.include_router(rtr)


@slip.get("/arg-q-bool")
def arg_bool(boolv_q: Query[bool]):
    assert isinstance(boolv_q, bool)
    return boolv_q


@slip.get("/args-headers")
def arg_str(query: Test):
    assert query.arg_bool is True
    assert query.arg_float == 3.4
    assert query.arg_str == "sre"
    assert query.arg_int == 4
    return "200"


@slip.get("/arg-str")
def arg_str(s: Query.type(str)):
    s: list[str]
    return {"param": s}


rtr2 = Router(prefix="/prefix")


@rtr2.get("health")
def health():
    return "ok"


drain = Router("/test")


@slip.get("/health")
def test_mtd():
    return {"status": "healthy"}


@drain.get("/")
def test_mtd(qu: Qu):
    return ""


@drain.get("/args:arg1:arg2:arg3", model=Qu)
@beartype
def test_mtd_2(model: Qu):
    return model


slip.include_router(drain)
slip.collapse()
