from dataclasses import dataclass
from inspect import Signature
from typing import Annotated, Any

from beartype.door import is_bearable
from rich.console import Console

from .defaults import DEFAULT_LOG_LEVEL
from .encoders import json
from .enums import LogLevel
from .exceptions import TYPES_TO_JS_TYPE, ManyValidationErrors, StructuredValidationError
from .inspect import Field, Preamble
from .params import Param, ParamTypes, rev
from .request import Request
from .responses import Response
from .types import get_args, get_origin
from .utils import log_level, run


@dataclass
class ClsExecArg:
    T: type
    key: str
    param: list[Param]

    def get_from_request(
        self, request: Request, l_level: LogLevel = DEFAULT_LOG_LEVEL, console: Console = None
    ) -> tuple[Any, ParamTypes] | tuple[None, list[ParamTypes]]:
        log_level(console, l_level, LogLevel.follow, self, " - getting params -", self.param)
        for param in self.param:  # O(1) at best O(n) at worst
            value = param.request_extractor(request, self.key, self.T)
            if value:
                return (value, param.source)
        return (None, [s.source for s in self.param])


@dataclass
class ClsCollect:
    T: type
    key: str
    param: list[ClsExecArg]


__err__ = "invalid types - only use (Query.type, Header.type, Body.type, or Cookie.type)"


def exec_from_fld(field: Field, l_level: LogLevel = DEFAULT_LOG_LEVEL, console: Console = None) -> ClsExecArg:
    if field.type is None or field.type is Signature.empty:
        msg = "no signature"
        raise ValueError(msg)
    elif get_origin(field.type) is not Annotated:
        raise ValueError("")
    log_level(console, l_level, LogLevel.trace, "EXTRACTING FIELD", field)
    args = get_args(field.type)  # Annotated[str, Query] -> (str, Query, *...)
    if len(args) <= 1:
        msg = "must select a proper type"
        raise ValueError(msg)
    typ, *origin = args
    for src in origin:
        if src not in ParamTypes:
            raise ValueError(__err__)
    reverse = [rev(o) for o in origin]
    if any(r is None for r in reverse):
        raise ValueError(__err__)
    log_level(console, l_level, LogLevel.trace, "QUERY EXTRACTOR", field, "ORIGIN", origin, "TYPE", typ)
    return ClsExecArg(key=field.name, T=typ, param=reverse)


def saturate_kwargs_errs(
    request: Request, kwargs: dict, sources: list[ClsExecArg], console: Console, l_level: LogLevel
) -> list[StructuredValidationError] | None:
    errors: list[StructuredValidationError] = []
    for gen in sources:
        log_level(
            console,
            l_level,
            LogLevel.trace,
            "EXTRACTING FROM REQUEST",
            gen,
        )
        value, source = gen.get_from_request(request)
        if not is_bearable(value, gen.T):
            __err__ = StructuredValidationError(
                key=gen.key, expected=TYPES_TO_JS_TYPE[gen.T], given=str(value), sources=source
            )
            errors.append(__err__)
        else:
            kwargs[gen.key] = value
    if len(errors) != 0:
        return errors
    return None


def wrap_endpoint_handler(
    func,
    preamble: Preamble,
    # path_params: Set[str],  # todo: integrate
    content_media_encoder=json,
    l_level: LogLevel = DEFAULT_LOG_LEVEL,
    console: Console = None,
):
    func = run(func)

    cls_kwargs: list[ClsCollect] = []
    kwarg_gen: list[ClsExecArg] = []

    for cls in preamble.classes:
        cls_objs = []
        for obj in cls.obj:
            cls_objs.append(exec_from_fld(obj))
        cls_kwargs.append(
            ClsCollect(
                T=cls.meta.T,
                key=cls.meta.key,
                param=cls_objs,
            )
        )

    for field in preamble.fields:
        kwarg_gen.append(exec_from_fld(field.obj))

    async def request_handler(request: Request):
        kwargs = {}
        errs: list[StructuredValidationError] = []
        kwarg_gen_errs = saturate_kwargs_errs(
            request=request, kwargs=kwargs, sources=kwarg_gen, console=console, l_level=l_level
        )
        if kwarg_gen_errs is not None:
            errs += kwarg_gen_errs
        for cls in cls_kwargs:
            cls_kw = {}
            cls_errs = saturate_kwargs_errs(
                request=request, kwargs=cls_kw, sources=cls.param, console=console, l_level=l_level
            )
            if cls_errs is None:
                kwargs[cls.key] = cls.T(**cls_kw)
            else:
                errs += cls_errs
        if len(errs) != 0:
            log_level(console, l_level, LogLevel.trace, "[bold red]VALIDATION ERRORS[/bold red]", errs)
            raise ManyValidationErrors(errors=errs)
        log_level(console, l_level, LogLevel.trace, "EXECUTING HANDLER WITH KWARGS", kwargs)
        response = await func(**kwargs)
        if not isinstance(response, Response):
            return content_media_encoder(response)
        return response

    return request_handler
