"""Configuration classes for the de-messaging backend module."""
from __future__ import annotations

import importlib
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic import BaseSettings, Field, validator

from demessaging.backend.utils import BaseReport
from demessaging.template import Template

if TYPE_CHECKING:
    from demessaging.backend.class_ import BackendClass
    from demessaging.backend.function import BackendFunction


T = TypeVar("T", bound=Callable[..., Any])


class ApiRegistry(BaseModel):
    """A registry for imports and encoders"""

    @validator("imports")
    @classmethod
    def can_import_import(cls, imports: Dict[str, str]) -> Dict[str, str]:
        errors: List[ImportError] = []
        for key in imports:
            try:
                importlib.import_module(key)
            except ImportError as e:
                errors.append(e)
            except Exception:
                raise
        if errors:
            raise ValueError(
                "Could not import all modules!\n    "
                + "\n    ".join(map(str, errors))
            )
        return imports

    json_encoders: Dict[Any, Callable[[Any], Any]] = Field(
        default_factory=dict,
        description=(
            "Custom encoders for datatypes. See "
            "https://pydantic-docs.helpmanual.io/usage/exporting_models/#json_encoders"  # noqa: E501
        ),
    )

    imports: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Modules to import at the top of every file. The first "
            "item is the module, the second is the alias"
        ),
    )

    objects: List[str] = Field(
        default_factory=list,
        description=(
            "Source code for objects that should be inlined in the generated "
            "Python API."
        ),
    )

    def register_import(
        self, module: str, alias: Optional[str] = None
    ) -> None:
        """Register a module that needs to be imported in generated API files.

        Parameters
        ----------
        module: str
            The name of the module, e.g. matplotlib.pyplot
        """
        self.imports[module] = alias or ""

    def register_encoder(
        self, Class: Any, encoder: Callable[[Any], Any]
    ) -> None:
        """Register an encoder for the backend config.

        This function can be used to register a custom encoder for a type.
        You should use this for any object that cannot be decoded by default
        using the standard json.dumps.

        Under the hood, this is then transformed as the ``json_encoders``
        configuration value for pydantic (see
        https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeljson)

        Parameters
        ----------
        Class: object
            The type that can be encoded by the given encoder
        encoder: function
            A function that takes one argument, an instance of `Class` and
            converts it to a JSON-conform representation
        """
        self.json_encoders[Class] = encoder

    def register_type(self, obj: T) -> T:
        """Register a class or function to be available in the generated API.

        Use this function if you want to have certain functions of classes
        available in the generated API module, but they should not be
        transformed to a call to the backend module.
        """
        self.objects.append(inspect.getsource(obj))
        return obj

    def hard_code(self, python_code: str) -> None:
        """Register some code to be implemented in the generated module.

        Parameters
        ----------
        python_code: str
            The code that is supposed to be executed on a module level.
        """
        self.objects.append(python_code)
        return


registry = ApiRegistry()


def _get_registry() -> ApiRegistry:
    """Convenience function to get :attr:`registry`.

    Without this, the default value for the config classes `registry` attribute
    would always be empty.
    """
    return registry


class BaseConfig(BaseModel):
    """Configuration base class for functions, modules and classes."""

    doc: str = Field(
        "",
        description=(
            "The documentation of the object. If empty, this will be taken "
            "from the corresponding ``__doc__`` attribute."
        ),
    )

    registry: ApiRegistry = Field(
        default_factory=_get_registry,
        description="Utilities for imports and encoders.",
    )

    template: Template = Field(
        Template(name="empty"),
        description=(
            "The :class:`demessaging.template.Template` that is used "
            "to render this object for the generated API."
        ),
    )

    def render(self, **context) -> str:
        """Generate the code to call this function in the frontend."""
        context["config"] = self
        code = self.template.render(**context)
        return code


class FunctionConfig(BaseConfig):
    """Configuration class for a backend module function."""

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    name: str = Field(
        "",
        description=(
            "The name of the function. If empty, this will be taken from the "
            "functions ``__name__`` attribute."
        ),
    )

    signature: Optional[inspect.Signature] = Field(
        None,
        description=(
            "The calling signature for the function. If empty, this will be "
            "taken from the function itself."
        ),
    )

    validators: Dict[str, classmethod] = Field(
        default_factory=dict,
        description="custom validators for the constructor parameters",
    )

    field_params: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "custom Field overrides for the constructor parameters. See "
            ":func:`pydantic.Fields.Field`"
        ),
    )

    returns: Dict[str, Any] = Field(
        default_factory=dict, description="custom returns overrides."
    )

    annotations: Dict[str, Any] = Field(
        default_factory=dict,
        description="custom annotations for function parameters",
    )

    template: Template = Field(
        Template(name="function.py"),
        description=(
            "The :class:`demessaging.template.Template` that is used "
            "to render the function for the generated API."
        ),
    )

    reporter_args: Dict[str, BaseReport] = Field(
        default_factory=dict,
        description="Arguments that use the dasf-progress-api",
    )


class ClassConfig(BaseConfig):
    """Configuration class for a backend module class."""

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    name: str = Field(
        "",
        description=(
            "The name of the function. If empty, this will be taken from the "
            "classes ``__name__`` attribute."
        ),
    )

    init_doc: str = Field(
        "",
        description=(
            "The documentation of the function. If empty, this will be taken "
            "from the classes ``__init__`` method."
        ),
    )

    signature: Optional[inspect.Signature] = Field(
        None,
        description=(
            "The calling signature for the function. If empty, this will be "
            "taken from the function itself."
        ),
    )

    methods: List[str] = Field(
        default_factory=list,
        description="methods to use within the backend modules",
    )

    validators: Dict[str, classmethod] = Field(
        default_factory=dict,
        description="custom validators for the constructor parameters",
    )

    field_params: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "custom Field overrides for the constructor parameters. "
            "See :func:`pydantic.Fields.Field`"
        ),
    )

    annotations: Dict[str, Any] = Field(
        default_factory=dict,
        description="custom annotations for constructor parameters",
    )

    template: Template = Field(
        Template(name="class_.py"),
        description=(
            "The :class:`demessaging.template.Template` that is used "
            "to render the class for the generated API."
        ),
    )

    reporter_args: Dict[str, BaseReport] = Field(
        default_factory=dict,
        description="Arguments that use the dasf-progress-api",
    )


class PulsarConfig(BaseSettings):
    """A configuration class to connect to the pulsar messaging framework."""

    class Config:
        env_prefix = "de_backend_"

    topic: str = Field(
        description=(
            "The topic identifier under which to register at the pulsar."
        )
    )

    host: str = Field(
        "rz-vm154.gfz-potsdam.de", description="The remote host of the pulsar"
    )

    port: str = Field(
        "8082", description="The port of the pulsar at the given :attr:`host`"
    )

    persistent: str = Field("non-persistent")

    tenant: str = Field("public")

    namespace: str = Field("digital-earth")

    max_workers: int = Field(
        default=None,
        description=(
            "(optional) number of concurrent workers for handling requests, "
            "default: number of processors on the machine, multiplied by 5"
        ),
    )

    queue_size: int = Field(
        default=None,
        description=(
            "(optional) size of the request queue, if MAX_WORKERS is set, "
            "this needs to be at least as big as MAX_WORKERS, "
            "otherwise an AttributeException is raised"
        ),
    )


class ModuleConfig(BaseConfig, PulsarConfig):
    """Configuration class for a backend module."""

    class Config:
        arbitrary_types_allowed = True

    # it should be Type[BackendFunction], Type[BaseModel], but that's
    #  not well supported by pydantic
    if TYPE_CHECKING:
        members: List[
            Union[
                str,
                Callable,
                Type[object],
                Type[
                    BackendFunction  # pylint: disable=used-before-assignment  # noqa: E501
                ],
                Type[BackendClass],  # pylint: disable=used-before-assignment
            ]
        ]

    members: List[Union[str, Callable, Type[object], Any]] = Field(  # type: ignore  # noqa: E501
        default_factory=list, description="List of members for this module"
    )

    imports: str = Field(
        "",
        description="Imports that should be added to the generate API module.",
    )

    template: Template = Field(
        Template(name="module.py"),
        description=(
            "The :class:`demessaging.template.Template` that is used "
            "to render the module for the generated API."
        ),
    )

    @property
    def pulsar_config(self) -> PulsarConfig:
        """Get the configuration dictionary for the pulsar."""
        fields = PulsarConfig.__fields__
        vals = self.dict()
        return PulsarConfig.construct(
            **{field: vals[field] for field in fields}
        )


def configure(js: Optional[str] = None, **kwargs) -> Callable[[T], T]:
    """Configuration decorator for function or modules.

    Use this function as a decorator for classes or functions in the backend
    module like so::

        >>> @configure(field_params={"a": {"gt": 0}}, returns={"gt": 0})
        ... def sqrt(a: float) -> float:
        ...     import math
        ...
        ...     return math.sqrt(a)
    """

    def decorator(obj: T) -> T:
        ConfClass: Union[Type[ClassConfig], Type[FunctionConfig]]
        if inspect.isclass(obj):
            ConfClass = ClassConfig
        else:
            ConfClass = FunctionConfig
        if js:
            config = ConfClass.parse_raw(js)
        else:
            config = ConfClass(**kwargs)
        obj.__pulsar_config__ = config  # type: ignore
        return obj

    return decorator
