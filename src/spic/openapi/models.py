from typing import Dict

from serde import field

from ..types import Prim
from ..utils import schema

OAPI_VERSION = "3.1.0"
RENAME = {"rename_all": "camelcase"}


@schema(**RENAME)
class Example:
    summary: str = field(default=None)
    description: str = field(default=None)
    value: Dict = field(default=None)
    external_value: str = field(default=None)


@schema(**RENAME)
class Contact:
    name: str = field(default=None)
    url: str = field(default=None)
    email: str = field(default=None)


@schema(**RENAME)
class License:
    name: str
    url: str = field(default=None)


@schema(**RENAME)
class Info:
    title: str
    version: str

    description: str | None = field(default=None)
    terms_of_service: str | None = field(default=None)
    contact: Contact | None = field(default=None)
    license: License | None = field(default=None)


@schema(**RENAME)
class ServerVariable:
    default: str

    enum: list[str] | None = field(default=None)
    description: str | None = field(default=None)


@schema(**RENAME)
class Server:
    url: str
    description: str | None = field(default=None)
    variables: Dict[str, ServerVariable] | None = field(default=None)


@schema(**RENAME)
class Reference:
    ref: str = field(alias="$ref")


@schema(**RENAME)
class Discriminator:
    property_name: str
    mapping: Dict[str, str] | None = field(default=None)


@schema(**RENAME)
class XML:
    name: str | None = field(default=None)
    namespace: str | None = field(default=None)
    prefix: str | None = field(default=None)
    attribute: bool | None = field(default=None)
    wrapped: bool | None = field(default=None)


@schema(**RENAME)
class ExternalDocumentation:
    url: str

    description: str | None = field(default=None)


@schema(**RENAME)
class Schema:
    ref: str | None = field(default=None, alias="$ref")
    title: str | None = field(default=None)
    description: str | None = field(default=None)
    type: str = field(default="object")
    xml: XML | None = field(default=None)
    example: Dict[str, Prim] = field(default_factory=dict)
    deprecated: bool | None = field(default=False)

    additional_properties: dict = field(default_factory=dict)


@schema(**RENAME)
class Encoding:
    content_type: str | None = field(default=None)
    headers: Dict[str, Prim | Reference] | None = field(default=None)
    style: str | None = field(default=None)
    explode: bool | None = field(default=None)
    allow_reserved: bool | None = field(default=None)


@schema(**RENAME)
class MediaType:
    # { "application/json": Example } | { "application/json": Reference }

    schema: Schema | Reference | None = field(default=None)
    example: Example | None = field(default=None)
    examples: Dict[str, Example | Reference] | None = field(default=None)
    encoding: Dict[str, Encoding] | None = field(default=None)


@schema(**RENAME)
class Style:
    matrix: list[str] | str = field(default_factory=list)
    label: str | None = field(default=None)
    form: dict | None = field(default=None)
    simple: list[dict] | None = field(default=None)
    space_delimited: list[dict] | dict | None = field(default=None)
    pipe_delimited: list[dict] | dict | None = field(default=None)
    deep_object: dict = field(default=None)


@schema(**RENAME)
class ParameterBase:
    name: str
    _in: str = field(alias="in", default="query")

    required: bool = field(default=True)

    description: str | None = field(default=None)

    deprecated: bool = field(default=False)
    allow_empty_value: bool = field(default=False)

    style: str | Style | None = field(default=None)
    explode: bool | None = field(default=None)

    allow_reserved: bool | None = field(default=None)
    schema: Schema | Reference | None = field(default=None)

    example: Dict | None = field(default=None)

    # { "application/json": Example } | { "application/json": Reference }
    examples: Dict[str, Example | Reference] | None = field(default=None)
    content: Dict[str, MediaType] | None = field(default=None)


@schema(**RENAME)
class RequestBody:
    content: Dict[str, MediaType]

    description: str | None = field(default=None)
    required: bool | None = field(default=None)


@schema(**RENAME)
class Link:
    operation_ref: str | None = field(default=None)
    operation_id: str | None = field(default=None)
    parameters: Dict[str, str | Dict] = field(default_factory=dict)
    request_body: str | Dict | None = field(default=None)
    description: str | None = field(default=None)
    server: Server | None = field(default=None)


@schema(**RENAME)
class Operation:
    tags: list[str] | None = field(default=None)
    summary: str | None = field(default=None)
    description: str | None = field(default=None)
    external_docs: ExternalDocumentation | None = field(default=None)
    operation_id: str | None = field(default=None)
    parameters: list[ParameterBase | Reference] | None = field(default=None)
    request_body: RequestBody | Reference | None = field(default=None)
    responses: Dict[str, Dict] | None = field(default=None)
    callbacks: Dict[str, Dict[str, str] | Reference] | None = field(default=None)
    deprecated: bool | None = field(default=None)
    security: list[Dict[str, list[str]]] | None = field(default=None)
    servers: list[Server] | None = field(default=None)


@schema(**RENAME)
class RouteSchema:
    ref: str | None = field(default=None, alias="$ref")

    summary: str | None = field(default=None)
    description: str | None = field(default=None)

    get: Operation | None = field(default=None)
    put: Operation | None = field(default=None)
    post: Operation | None = field(default=None)
    delete: Operation | None = field(default=None)
    options: Operation | None = field(default=None)
    connect: Operation | None = field(default=None)
    head: Operation | None = field(default=None)
    patch: Operation | None = field(default=None)
    trace: Operation | None = field(default=None)

    servers: list[Server] | None = field(default=None)
    parameters: list[ParameterBase | Reference] | None = field(default=None)


@schema(**RENAME)
class OpenAPISchema:
    openapi: str
    info: Info
    paths: Dict[str, RouteSchema]

    json_schema_dialect: str | None = field(default=None)

    servers: list[Server] = field(default_factory=list)
    security: list[Dict[str, list[str]]] = field(default_factory=list)
    tags: list[Dict] = field(default_factory=list)
    external_docs: ExternalDocumentation | None = field(default=None)
