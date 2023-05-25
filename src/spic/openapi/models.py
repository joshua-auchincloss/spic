from enum import Enum

from serde import Untagged

from ..types import Any, Prim
from ..utils import schema, skip_empty

OAPI_VERSION = "3.0.0"
RENAME = {"rename_all": "camelcase", "serialize_class_var": True, "tagging": Untagged}

E = list[str] | dict[str, str | int] | None


class ValidEnum:
    enum: E

    def __init__(self, enum):
        if enum is None:
            return
        if not isinstance(enum, list):
            if issubclass(enum, Enum):
                enum = {e.name: e.value for e in enum}
        self.enum = enum


@schema(
    **RENAME,
)
class Example:
    summary: str = skip_empty(default=None)
    description: str = skip_empty(default=None)
    value: dict = skip_empty(default=None)
    external_value: str = skip_empty(default=None)


@schema(**RENAME)
class Contact:
    name: str = skip_empty(default=None)
    url: str = skip_empty(default=None)
    email: str = skip_empty(default=None)


@schema(**RENAME)
class License:
    name: str
    url: str = skip_empty(default=None)


@schema(**RENAME)
class Info:
    title: str
    version: str

    description: str | None = skip_empty(default=None)
    terms_of_service: str | None = skip_empty(default=None)
    contact: Contact | None = skip_empty(default=None)
    _license: License | None = skip_empty(default=None, rename="license")


@schema(**RENAME)
class ServerVariable(ValidEnum):
    default: str

    enum: E = skip_empty(default=None)
    description: str | None = skip_empty(default=None)

    def __post_init__(self):
        super().__init__(self.enum)


@schema(**RENAME)
class Server:
    url: str
    description: str | None = skip_empty(default=None)
    variables: dict[str, ServerVariable] | None = skip_empty(default=None)


@schema(**RENAME)
class Reference:
    ref: str = skip_empty(rename="$ref")


ExampleT = Example | None
ExamplesT = dict[str, Example] | dict[str, Reference] | None


@schema(**RENAME)
class Discriminator:
    property_name: str
    mapping: dict[str, str] | None = skip_empty(default=None)


@schema(**RENAME)
class XML:
    name: str | None = skip_empty(default=None)
    namespace: str | None = skip_empty(default=None)
    prefix: str | None = skip_empty(default=None)
    attribute: bool | None = skip_empty(default=None)
    wrapped: bool | None = skip_empty(default=None)


@schema(**RENAME)
class ExternalDocumentation:
    url: str
    description: str | None = skip_empty(default=None)


@schema(**RENAME)
class Property(ValidEnum):
    _type: str = skip_empty(default="object", rename="type")
    format: str | None = skip_empty(default=None)
    example: ExampleT | Any = skip_empty(default=None)
    enum: E = skip_empty(default=None)
    items: Reference | None = skip_empty(default=None)

    def __post_init__(self):
        super().__init__(self.enum)


@schema(**RENAME)
class Schema:
    title: str | None = skip_empty(default=None)
    description: str | None = skip_empty(default=None)
    _type: str = skip_empty(default="object", rename="type")
    example: ExampleT | Any = skip_empty(default=None)
    examples: ExamplesT | Any = skip_empty(default=None)
    default: Any = skip_empty(default=None)
    deprecated: bool | None = skip_empty(default=False)
    properties: dict[str, Property] | None = skip_empty(default=None)
    xml: XML | None = skip_empty(default=None)
    additional_properties: dict | None = skip_empty(default=None)


@schema(**RENAME)
class Encoding:
    content_type: str | None = skip_empty(default=None)
    headers: dict[str, Prim | Reference] | None = skip_empty(default=None)
    style: str | None = skip_empty(default=None)
    explode: bool | None = skip_empty(default=None)
    allow_reserved: bool | None = skip_empty(default=None)


@schema(**RENAME)
class MediaType:
    # { "application/json": Example }

    schema: Schema | Reference | None = skip_empty(default=None)
    example: ExampleT = skip_empty(default=None)
    examples: ExamplesT = skip_empty(default=None)
    encoding: dict[str, Encoding] | None = skip_empty(default=None)


@schema(**RENAME)
class Style:
    matrix: list[str] | str = skip_empty(default_factory=list)
    label: str | None = skip_empty(default=None)
    form: dict | None = skip_empty(default=None)
    simple: list[dict] | None = skip_empty(default=None)
    space_delimited: list[dict] | dict | None = skip_empty(default=None)
    pipe_delimited: list[dict] | dict | None = skip_empty(default=None)
    deep_object: dict = skip_empty(default=None)


@schema(**RENAME)
class ParameterBase:
    name: str
    _in: str = skip_empty(rename="in", default="query")

    required: bool = skip_empty(default=True)

    description: str | None = skip_empty(default=None)

    deprecated: bool = skip_empty(default=False)
    allow_empty_value: bool = skip_empty(default=False)

    style: str | Style | None = skip_empty(default=None)
    explode: bool | None = skip_empty(default=None)

    allow_reserved: bool | None = skip_empty(default=None)
    schema: Schema | Reference | None = skip_empty(default=None)

    example: ExampleT = skip_empty(default=None)

    # { "application/json": Example } | { "application/json": Reference }
    examples: dict[str, Example] | dict[str, Reference] | None = skip_empty(default=None)
    content: dict[str, MediaType] | None = skip_empty(default=None)


Params = list[ParameterBase] | list[Reference] | None


@schema(**RENAME)
class RequestBody:
    content: dict[str, MediaType]

    description: str | None = skip_empty(default=None)
    required: bool | None = skip_empty(default=None)


@schema(**RENAME)
class Link:
    operation_ref: str | None = skip_empty(default=None)
    operation_id: str | None = skip_empty(default=None)
    parameters: dict[str, str | dict] = skip_empty(default_factory=dict)
    request_body: str | dict | None = skip_empty(default=None)
    description: str | None = skip_empty(default=None)
    server: Server | None = skip_empty(default=None)


@schema(**RENAME)
class Response:
    description: str
    content: dict[str, MediaType]


@schema(**RENAME)
class Operation:
    tags: list[str] | None = skip_empty(default=None)
    summary: str | None = skip_empty(default=None)
    description: str | None = skip_empty(default=None)
    external_docs: ExternalDocumentation | None = skip_empty(default=None)
    operation_id: str | None = skip_empty(default=None)
    parameters: Params = skip_empty(default=None)
    request_body: RequestBody | Reference | None = skip_empty(default=None)
    responses: dict[str, Response] | None = skip_empty(default=None)
    callbacks: dict[str, dict[str, str] | Reference] | None = skip_empty(default=None)
    deprecated: bool | None = skip_empty(default=None)
    security: list[dict[str, list[str]]] | None = skip_empty(default=None)
    servers: list[Server] | None = skip_empty(default=None)


@schema(**RENAME)
class RouteSchema:
    ref: str | None = skip_empty(default=None, rename="$ref")

    summary: str | None = skip_empty(default=None)
    description: str | None = skip_empty(default=None)

    get: Operation | None = skip_empty(default=None)
    put: Operation | None = skip_empty(default=None)
    post: Operation | None = skip_empty(default=None)
    delete: Operation | None = skip_empty(default=None)
    options: Operation | None = skip_empty(default=None)
    connect: Operation | None = skip_empty(default=None)
    head: Operation | None = skip_empty(default=None)
    patch: Operation | None = skip_empty(default=None)
    trace: Operation | None = skip_empty(default=None)

    servers: list[Server] | None = skip_empty(default=None)
    parameters: Params = skip_empty(default=None)


@schema(**RENAME)
class Components:
    schemas: dict[str, Schema] | None = skip_empty(default=None)
    examples: dict[str, Any] | None = skip_empty(default=None)


@schema(**RENAME)
class OpenAPISchema:
    openapi: str
    info: Info
    paths: dict[str, RouteSchema]

    json_schema_dialect: str | None = skip_empty(default=None)

    servers: list[Server] = skip_empty(default_factory=list)
    security: list[dict[str, list[str]]] = skip_empty(default_factory=list)
    tags: list[dict] = skip_empty(default_factory=list)
    external_docs: ExternalDocumentation | None = skip_empty(default=None)
    components: Components | None = skip_empty(default=None)
