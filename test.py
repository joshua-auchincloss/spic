from dataclasses import dataclass

from beartype import beartype

from src.spic.app import Spic
from src.spic.enums import LogLevel
from src.spic.openapi.models import Server, ServerVariable
from src.spic.params import Header, Query
from src.spic.routing import Router


@dataclass
class Test:
    arg_str: Header[str]
    arg_int: Header[int]
    arg_float: Header[float]
    arg_bool: Header[bool]


@dataclass
class InvalidT:
    field: str


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


slip = Spic(
    title="test",
    # log_level=LogLevel.trace,
    servers=[
        Server(url="/", description="main server", variables={"var1": ServerVariable(default="abc", enum=LogLevel)})
    ],
)

slip.router.static("/static", "./COVERAGE.md")
slip.router.static_dir("/static2", "./tests")


rtr = Router()


@rtr.get("health")
def health():
    return "ok"


slip.include_router(rtr)
TE = InvalidT(field="field")


@slip.get("/arg-q-bool")
def arg_bool(boolv_q: Query[bool]):
    assert isinstance(boolv_q, bool)  # noqa: S101
    return boolv_q


@slip.get("/invalid")
def invalid():
    return TE


@slip.get("/args-headers")
def arg_str(query: Test):
    assert query.arg_bool is True  # noqa: S101
    assert query.arg_float == float(3.4)  # noqa: S101
    assert query.arg_str == "sre"  # noqa: S101
    assert query.arg_int == int(4)  # noqa: S101
    return "200"


@slip.get("/arg-str")
def arg_str_2(s: Query.type(str)):
    s: list[str]
    return {"param": s}


rtr2 = Router(prefix="/prefix")


@rtr2.get("health")
def health_2():
    return "ok"


drain = Router("/test")


@slip.get("/health")
def test_mtd():
    return {"status": "healthy"}


@drain.get("/")
def test_mtd_2(_: Qu):
    return ""


@drain.get("/args:arg1:arg2:arg3", model=Qu)
@beartype
def test_mtd_3(model: Qu):
    return model


slip.include_router(drain)
# slip.collapse()
