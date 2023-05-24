from ..routing import Route
from .models import Operation, RouteSchema


def get_sub_by_mtd(_: Route, __: str):
    return Operation()


def get_schema_from_route(route: Route):
    mtds = [mtd.lower() for mtd in route.methods]
    scheme = RouteSchema(**{m: get_sub_by_mtd(route, m) for m in mtds})
    return scheme
