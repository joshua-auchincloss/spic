from http import HTTPStatus

from ..enums import ParamTypes
from ..exceptions import TYPES_TO_JS_TYPE
from ..func_handler import exec_from_fld
from ..inspect import Field
from ..routing import Preamble, Route
from .models import (
    XML,
    Components,
    MediaType,
    OpenAPISchema,
    Operation,
    ParameterBase,
    Property,
    Reference,
    Response,
    RouteSchema,
    Schema,
)


def example_ref(comp: str):
    return f"#/components/examples/{comp}"


def schema_ref(comp: str):
    return f"#/components/schemas/{comp}"


VALIDATION_ERR_EG_REF = Reference(ref=example_ref("JSONErrror"))
VALIDATION_ERR_SCHEMA_REF = Reference(ref=schema_ref("JSONErrror"))

InvalidRaised = Response(
    description="Validation exception",
    content={
        "application/json": MediaType(
            schema=VALIDATION_ERR_EG_REF,
        )
    },
)


def get_param_from_field(field: Field, key: str):
    params: list[ParameterBase] = []
    found = exec_from_fld(field)
    t = TYPES_TO_JS_TYPE.get(found.T, "object")
    if len(found.param) == 1:
        params.append(
            ParameterBase(
                name=key, _in=found.param[0].source.value, required=True, schema=Schema(_type=t, default="abc")
            )
        )
    else:
        for possible in found.param:
            params.append(
                ParameterBase(
                    name=key, _in=possible.source.value, required=False, schema=Schema(_type=t, default="abc")
                )
            )
    return params


def to_param(preamble: Preamble):
    params: list[ParameterBase] = []
    for param in preamble.fields:
        extracted = get_param_from_field(param.obj, param.meta.key)
        params += extracted
    for cls in preamble.classes:
        for param in cls.obj:
            extracted = get_param_from_field(param, param.name)
            params += extracted
    return params


def get_sub_by_mtd(route: Route, method: str):
    preamble = route.preamble.get(method.upper())
    params = to_param(preamble)
    responses = {}
    if len(params) > 0:
        responses[HTTPStatus.BAD_REQUEST.value] = InvalidRaised
    return Operation(parameters=params, responses=responses)


def get_schema_from_route(route: Route) -> tuple[list[Reference], RouteSchema]:
    mtds = [mtd.lower() for mtd in route.methods]
    refs = []
    scheme = RouteSchema(**{m: get_sub_by_mtd(route, m) for m in mtds})
    return refs, scheme


def build_references_examples_to_model(model: OpenAPISchema, references: dict[str, Schema]):
    if model.components is None:
        components = Components(
            schemas={},
            examples={},
        )
    else:
        components = model.components
    for ref, schema in references.items():
        components.schemas[ref.split("/")[-1]] = schema
    components.schemas["JSONError"] = Schema(
        title="JSONError",
        _type="object",
        xml=XML(name="error", namespace="validation"),
        description="returned upon request to server with missing or invalid params",
        example={"errors": [{"value": "X-Header-Arg", "source": "header", "expected": "string", "given": "none"}]},
        properties={"errors": Property(_type="array", items=Reference(ref=schema_ref("ValidationErrorObject")))},
    )
    components.schemas["ValidationErrorObject"] = Schema(
        title="ValidationErrorObject",
        _type="object",
        xml=XML(name="error", namespace="validation"),
        description="returned upon request to server with missing or invalid params",
        example={"value": "X-Header-Arg", "source": "header", "expected": "string", "given": "none"},
        properties={
            "value": Property(
                _type="string",
            ),
            "source": Property(_type="string", example="query", enum=ParamTypes),
            "given": Property(_type="string", example="none"),
            "expected": Property(_type="string", example="string"),
        },
    )
    components.examples["JSONError"] = {
        "errors": [{"value": "X-Header-Arg", "source": "header", "expected": "string", "given": "none"}]
    }
    model.components = components
    return model
