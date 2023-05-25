from warnings import warn

from .models import OAPI_VERSION, OpenAPISchema
from .utils import build_references_examples_to_model, get_schema_from_route, get_sub_by_mtd

warn(
    """slip.openapi is EXPERIMENTAL and may not function as intended. use with caution""",
    stacklevel=2,
)
