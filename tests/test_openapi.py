from src.spic.encoders import json
from src.spic.openapi.models import *  # noqa: F403


def test_model_example_instantiation():
    eg = Example(summary="")  # noqa: F405
    json(eg)


def test_model_contact_instantiation():
    eg = Contact(name="", url="", email="")  # noqa: F405
    json(eg)


def test_model_license_instantiation():
    eg = License(name="", url="")  # noqa: F405
    json(eg)


def test_model_info_instantiation():
    eg = Info(title="", version="")  # noqa: F405
    json(eg)


def test_model_servervariable_instantiation():
    eg = ServerVariable(default="")  # noqa: F405
    json(eg)


def test_model_server_instantiation():
    eg = Server(url="")  # noqa: F405
    json(eg)


def test_model_reference_instantiation():
    eg = Reference(ref="$")  # noqa: F405
    json(eg)


def test_model_discriminator_instantiation():
    eg = Discriminator(property_name="d")  # noqa: F405
    json(eg)


def test_model_xml_instantiation():
    eg = XML()  # noqa: F405
    json(eg)


def test_model_externaldocumentation_instantiation():
    eg = ExternalDocumentation(url="")  # noqa: F405
    json(eg)


def test_model_schema_instantiation():
    eg = Schema()  # noqa: F405
    json(eg)


def test_model_encoding_instantiation():
    eg = Encoding()  # noqa: F405
    json(eg)


def test_model_mediatype_instantiation():
    eg = MediaType()  # noqa: F405
    json(eg)


def test_model_style_instantiation():
    eg = Style()  # noqa: F405
    json(eg)


def test_model_parameterbase_instantiation():
    eg = ParameterBase(name="")  # noqa: F405
    json(eg)


def test_model_requestbody_instantiation():
    eg = RequestBody(content={})  # noqa: F405
    json(eg)


def test_model_link_instantiation():
    eg = Link()  # noqa: F405
    json(eg)


def test_model_operation_instantiation():
    eg = Operation()  # noqa: F405
    json(eg)


def test_model_routeschema_instantiation():
    eg = RouteSchema()  # noqa: F405
    json(eg)


def test_model_openapischema_instantiation():
    eg = OpenAPISchema(  # noqa: F405
        openapi="",
        info=Info(  # noqa: F405
            title="",
            version="",
        ),
        paths={},
    )
    json(eg)
