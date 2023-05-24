from dataclasses import Field as _Field
from dataclasses import dataclass, fields, is_dataclass
from inspect import get_annotations
from re import findall
from typing import Annotated, Set

from beartype.vale import Is

from .types import C


def get_path_param_names(path: str, pattern: str = None) -> Set[str]:
    if not path:  # None or ""
        path = "/"

    if pattern is None:
        pattern = "/"

    if pattern[0] != "/":
        pattern = ("/" + pattern).lower()

    return set(findall(":([^/:]*)", path))


@dataclass
class Meta:
    key: str
    T: type


@dataclass
class Field:
    meta: Meta
    obj: _Field


@dataclass
class Class:
    meta: Meta
    obj: Annotated[object, Is[lambda obj: is_dataclass(obj)]]


@dataclass
class Preamble:
    fields: list[Field]
    classes: list[Class]


def inspect_dataclass(dc):
    return fields(dc)


def inspect_function(func: C) -> Preamble:
    fields = []
    classes = []
    for key, field in get_annotations(func).items():
        meta = Meta(
            key=key,
            T=field,
        )
        if is_dataclass(field):
            classes.append(
                Class(
                    meta=meta,
                    obj=inspect_dataclass(
                        field,
                    ),
                ),
            )
            continue
        if isinstance(field, Field):
            field.name = key
            fields.append(Field(meta=meta, obj=field))
            continue
        fieldbase = _Field(
            default=None,
            default_factory=None,
            init=True,
            repr=True,
            hash=field in (str, int, bool, float, dict, set),
            compare=False,
            metadata={},
            kw_only=False,
        )
        fieldbase.name = key
        fieldbase.type = field
        fields.append(Field(meta=meta, obj=fieldbase))
    return Preamble(fields=fields, classes=classes)
