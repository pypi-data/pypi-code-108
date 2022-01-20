"""Utitlity functions for the backend framework."""
from __future__ import annotations

import asyncio
import inspect
import threading
import warnings
from itertools import chain, starmap
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal  # type: ignore


class _BaseReport(BaseModel):  # type: ignore
    """Dummy replacement for the deprogressapi basereport."""

    pass


try:
    from deprogressapi import BaseReport  # type: ignore # noqa: F811
except (ImportError, ModuleNotFoundError):
    BaseReport = _BaseReport
    _with_progress_api = False
else:
    _with_progress_api = True


if TYPE_CHECKING:
    import docstring_parser
    import isort.identify

    from demessaging.config import ClassConfig, FunctionConfig


def get_fields(
    name: str,
    sig: inspect.Signature,
    docstring: docstring_parser.Docstring,
    config: Union[FunctionConfig, ClassConfig],
) -> Dict[str, Tuple[Any, Any]]:
    """Get the model fields from a function signature.

    Parameters
    ----------
    name: str
        The name of the function or class
    sig: inspect.Signature
        The signature of the callable
    docstring: docstring_parser.Docstring
        The parser that analyzed the docstring
    config: FunctionConfig or ClassConfig
        The configuration for the callable

    Returns
    -------
    dict
        A mapping from field name to field parameters to be used in
        :func:`pydantic.create_model`.
    """
    fields: Dict[str, Tuple[Any, Any]] = {
        "func_name": (
            Literal[name],  # type: ignore
            Field(description=f"The name of the function. Must be {name!r}"),
        ),
    }
    for key, param in sig.parameters.items():
        if key == "self":
            continue
        field_kws: Dict[str, Any] = {}
        if param.default is not param.empty:
            field_kws["default"] = param.default
        param_doc = next(
            (p for p in docstring.params if p.arg_name == key), None
        )
        if param_doc is not None:
            field_kws["description"] = param_doc.description

        if key in config.field_params:
            field_kws.update(config.field_params[key])

        if key in config.annotations:
            fields[key] = (config.annotations[key], Field(**field_kws))
        elif param.annotation is param.empty:
            warnings.warn(
                f"Missing signature for {key}, so no validation will "
                "be made for this parameter!",
                RuntimeWarning,
            )
            fields[key] = (Any, Field(**field_kws))
        else:
            fields[key] = (param.annotation, Field(**field_kws))

        # test for dasf-progress-api reports and add them to the config
        if param.annotation is not param.empty and _is_progress_report(
            param.annotation
        ):
            if param.default is not param.empty:
                config.reporter_args[key] = param.default
            else:
                config.reporter_args[key] = param.annotation()

    return fields


def _is_progress_report(cls_: Type) -> bool:
    if not _with_progress_api:
        return False
    else:
        from deprogressapi import BaseReport

        if get_origin(cls_):
            # we do have a Union-type
            return any(
                inspect.isclass(c) and issubclass(c, BaseReport)
                for c in get_args(cls_)
            )
        elif inspect.isclass(cls_):
            return issubclass(cls_, BaseReport)
        else:
            return False


def get_desc(docstring: docstring_parser.Docstring) -> str:
    """Get the description of an object.

    Parameters
    ----------
    docstring: docstring_parser.Docstring
        The parser that analyzed the docstring.

    Returns
    -------
    str
        The description of the callable.
    """
    desc = ""
    if docstring.short_description:
        desc += docstring.short_description
    if docstring.long_description:
        if docstring.blank_after_short_description:
            desc += "\n\n"
        else:
            desc += "\n"
        desc += docstring.long_description
    return desc.strip()


def camelize(w: str) -> str:
    """Camelize a word by making the first letter upper case."""
    return w and (w[:1].upper() + w[1:])


def snake_to_camel(*words: str) -> str:
    """Transform a list of words into its camelized version."""
    return "".join(
        map(camelize, chain.from_iterable(w.split("_") for w in words))
    )


class AsyncIoThread(threading.Thread):
    """A thread that runs an async function.

    See: func: `run_async` for the implementation."""

    def __init__(self, func: Callable, args: Tuple, kwargs: Dict):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.__func(*self.__args, **self.__kwargs))


def run_async(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run an async function and wait for the result.

    This function works within standard python scripts, and during a running
    jupyter session."""
    # check if we have a running loop (which is the case for a jupyter
    # notebook)
    loop: Any
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():  # jupyter notebook
        thread = AsyncIoThread(func, args, kwargs)
        thread.start()
        thread.join()  # wait for the thread to finish
        return thread.result
    else:  # standard python script
        return asyncio.run(func(*args, **kwargs))


class ImportMixin:
    """Mixin class for :class:`isort.identify.Import`.

    A response to https://github.com/PyCQA/isort/issues/1641.
    """

    def statement(self: isort.identify.Import) -> str:  # type: ignore
        import_cmd = "cimport" if self.cimport else "import"
        if self.attribute:
            import_string = f"from {self.module} {import_cmd} {self.attribute}"
        else:
            import_string = f"{import_cmd} {self.module}"
        if self.alias:
            import_string += f" as {self.alias}"
        return import_string


def get_module_imports(mod: Any) -> str:
    """Get all the imports from a module

    Parameters
    ----------
    mod: module
        The module to use
    """
    try:
        from isort.api import find_imports_in_code
        from isort.identify import Import as BaseImport
    except (ImportError, ModuleNotFoundError):
        return ""

    code = inspect.getsource(mod)

    class Import(ImportMixin, BaseImport):
        pass

    # We could use the :meth:`~isort.identify.Import.statement` method here,
    # but this would not work always (see
    # https://github.com/PyCQA/isort/issues/1641)
    imports = starmap(Import, find_imports_in_code(code))

    return "\n".join(i.statement() for i in imports)
