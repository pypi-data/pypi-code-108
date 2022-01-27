"""Tools for describing Sym Resources."""

import inspect
import json
import re
from typing import Optional, Type, Union

from .errors import SymSDKError


class InvalidSRNError(SymSDKError):
    """Raised when an invalid :class:`~sym.sdk.resource.SRN` is supplied."""

    def __init__(self, srn: str, hint: str = None):
        self.srn = srn
        super().__init__(
            message=f"Invalid SRN '{srn}'.",
            hint=(
                hint
                or "SRNs must match the following structure: <ORG>:<MODEL>:<SLUG>:<VERSION>[:<IDENTIFIER>], where org, model, slug, and version are required."
            ),
            doc_url="https://docs.symops.com/docs/sym-concepts",
        )


class InvalidSlugError(InvalidSRNError):
    """Raised when a component of a :class:`~sym.sdk.resource.SRN` is an invalid slug."""

    def __init__(self, srn: str, component: str):
        super().__init__(
            srn,
            f"The {component} must be a valid slug (alphanumeric characters and dashes only).",
        )


class InvalidVersionError(InvalidSRNError):
    """Raised when a :class:`~sym.sdk.resource.SRN` has an invalid version."""

    def __init__(self, srn: str):
        super().__init__(
            srn,
            "The version must be semver with no tags (e.g. 1.0.0).",
        )


class TrailingSeparatorError(InvalidSRNError):
    """Raised when a :class:`~sym.sdk.resource.SRN` contains a trailing separator."""

    def __init__(self, srn: str):
        super().__init__(srn, "SRNs cannot have a trailing separator.")


class MultipleErrors(InvalidSRNError):
    """Raised when a :class:`~sym.sdk.resource.SRN` has multiple validation errors."""

    def __init__(self, srn: str):
        super().__init__(srn)
        self.errors = []

    def add(self, component: str, err_class: Type[InvalidSRNError]):
        # Check if the error class takes one or two args.
        # If one, just pass the SRN. If two, also pass the component name.
        arity = len(inspect.getfullargspec(err_class.__init__).args)
        self.errors.append(err_class(self.srn) if arity == 2 else err_class(self.srn, component))
        self.hint = "\n- ".join(
            ["There were multiple validation errors."] + [x.hint for x in self.errors]
        )

    def check(self):
        if len(self.errors) == 1:
            raise self.errors[0]
        elif self.errors:
            raise self


class SRN:
    """Sym Resource Name (:class:`~sym.sdk.resource.SRN`) is a unique identifier for a Sym Resource.

    SRNs have the following structure::

        <ORG>:<MODEL>:<SLUG>:<VERSION>[:<IDENTIFIER>]

    Where VERSION is either a semver string, or "latest".

    For example, the :class:`~sym.sdk.resource.SRN` for the v1.0.0 sym:approval
    template is::

        sym:template:approval:1.0.0

    Or the :class:`~sym.sdk.resource.SRN` for a :class:`~sym.sdk.flow.Flow`
    instance (with a UUID as an instance identifier) could be::

        sym:flow:test-flow:0.1.0:d47782bc-88be-44df-9e34-5fae0dbdea22
    """

    SEPARATOR = ":"
    """The default separator for :class:`~sym.sdk.flow.Flow` components."""

    SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9-_]+$")
    """The pattern for validating slug components."""
    VERSION_PATTERN = re.compile(r"^(latest|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$")
    """The pattern for validating the version component."""

    _COMPONENTS = {
        "org": (SLUG_PATTERN, InvalidSlugError),
        "model": (SLUG_PATTERN, InvalidSlugError),
        "slug": (SLUG_PATTERN, InvalidSlugError),
        "version": (VERSION_PATTERN, InvalidVersionError),
        "identifier": (SLUG_PATTERN, InvalidSlugError),
    }

    @classmethod
    def parse(cls, raw: str) -> "SRN":
        """Parses and validates the given string as an :class:`~sym.sdk.resource.SRN`.

        Args:
            raw: A raw string representing a :class:`~sym.sdk.resource.SRN`.

        Returns:
            A :class:`~sym.sdk.resource.SRN` instance.

        Raises:
            :class:`~sym.sdk.resource.TrailingSeparatorError`:      The string has a trailing separator.
            :class:`~sym.sdk.resource.InvalidSRNError`:             The string is missing components, or at least one component is invalid.
            :class:`~sym.sdk.resource.InvalidSlugError`:            The string has an invalid slug component.
            :class:`~sym.sdk.resource.InvalidVersionError`:         The string has an invalid version component.
        """
        raw = str(raw)

        if raw.endswith(cls.SEPARATOR):
            raise TrailingSeparatorError(raw)

        parts = dict(zip(cls._COMPONENTS.keys(), raw.split(cls.SEPARATOR)))
        if len(parts) < 4:
            missing = ", ".join(cls._COMPONENTS.keys() - parts.keys() - {"identifier"})
            raise InvalidSRNError(raw, f"This SRN is missing the following components: {missing}")

        return cls(*parts.values())

    @classmethod
    def __get_validators__(cls):
        yield cls.parse

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        """A hook to allow Pydantic to export a JSON Schema for SRN fields.

        https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
        """
        slug = cls.SLUG_PATTERN.pattern[1:-1]
        version_pattern = cls.VERSION_PATTERN.pattern[1:-1]
        field_schema.update(
            type="string",
            description="A Sym Resource Name (SRN) is a unique identifier for a Sym Resource.",
            pattern=f"{slug}:{slug}:{slug}:{version_pattern}(:{slug})?",
            examples=["sym:event:approval:1.0.0:requested"],
        )

    def __init__(
        self,
        org: str,
        model: str,
        slug: str,
        version: str,
        identifier: Optional[str] = None,
    ):
        self._org = org
        self._model = model
        self._slug = slug
        self._version = version
        self._identifier = identifier

        self._validate()

    def __str__(self):
        return self.SEPARATOR.join(
            [x for x in [self._get(k) for k in self._COMPONENTS.keys()] if x is not None]
        )

    def __repr__(self) -> str:
        components = ", ".join(
            [
                f"{k}={v}"
                for (k, v) in [(k, self._get(k)) for k in self._COMPONENTS.keys()]
                if v is not None
            ]
        )
        return f"SRN({components})"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return (
            self._org == other._org
            and self._model == other._model
            and self._slug == other._slug
            and self._version == other._version
            and self._identifier == other._identifier
        )

    def _get(self, name: str):
        return getattr(self, f"_{name}")

    def _validate(self):
        errors = MultipleErrors(str(self))
        for name, (pattern, error_class) in self._COMPONENTS.items():
            if self._get(name) is not None and not pattern.match(self._get(name)):
                errors.add(name, error_class)
        errors.check()

    def copy(
        self,
        organization: Optional[str] = None,
        model: Optional[str] = None,
        slug: Optional[str] = None,
        version: Optional[str] = None,
        identifier: Optional[str] = None,
    ):
        """Creates a copy of this :class:`~sym.sdk.resource.SRN`.

        Optionally can create a new :class:`~sym.sdk.resource.SRN` with
        modified components from the current, as specified by the keyword arguments.
        """

        components = [
            organization or self._org,
            model or self._model,
            slug or self._slug,
            version or self._version,
        ]
        if identifier:
            components.append(identifier)
        elif self._identifier:
            components.append(self._identifier)

        return self.__class__(*components)

    @property
    def organization(self) -> str:
        """The slug for the organization this :class:`~sym.sdk.resource.SRN`
        belongs to.

        For example, for the sym:approval :class:`~sym.sdk.templates.template.Template`,
        the organization slug is `sym`.
        """

        return self._org

    @property
    def model(self) -> str:
        """The model name for this :class:`~sym.sdk.resource.SRN`.

        For example, for the sym:approval :class:`~sym.sdk.templates.template.Template`,
        the model name is `template`.
        """

        return self._model

    @property
    def slug(self) -> str:
        """This :class:`~sym.sdk.resource.SRN`'s slug.

        For example, for the sym:approval :class:`~sym.sdk.templates.template.Template`, the slug is `approval`.
        """
        return self._slug

    @property
    def version(self) -> str:
        """A semver string representing the version of this :class:`~sym.sdk.resource.SRN`.

        For example, the first version of the sym:approval :class:`~sym.sdk.templates.template.Template`
        is `1.0.0`.
        """

        return self._version

    @property
    def identifier(self) -> Optional[str]:
        """An arbitrary string identifying an instance of the resource.

        This is often a UUID.
        """
        return self._identifier


class SymBaseResource:
    """The base class that all Sym SDK models inherit from."""

    def __str__(self) -> str:
        return json.dumps(self.dict(), indent=2)

    def __repr__(self) -> str:
        return str(self)

    def dict(self):
        return {
            k: v.dict() if isinstance(v, SymBaseResource) else v
            for k in dir(self)
            if not k.startswith("_")
            and isinstance((v := getattr(self, k)), (SymBaseResource, str, int, dict, list))
        }

    def __eq__(self, other):
        if not isinstance(other, SymBaseResource):
            return False
        return self.dict() == other.dict()


class SymResource(SymBaseResource):
    """A piece of infrastructure provisioned with
    Sym's `Terraform provider <https://docs.symops.com/docs/terraform-provider>`_.

    For example, a :class:`~sym.sdk.flow.Flow` is a Resource.

    Read more about `Sym Resources <https://docs.symops.com/docs/sym-concepts>`_.
    """

    def __init__(self, srn: Union[SRN, str]):
        self._srn = SRN.parse(str(srn))

    def __getattr__(self, name: str):
        return getattr(self.srn, name)

    def __eq__(self, other):
        if not isinstance(other, SymResource):
            return False
        return self.srn == other.srn

    def __hash__(self):
        return hash(str(self.srn))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.srn})"

    @property
    def srn(self) -> SRN:
        """A :class:`~sym.sdk.resource.SRN` object that represents the unique identifier
        for this resource.
        """
        return self._srn

    @property
    def name(self) -> str:
        """An alias for this resource's slug, represented by its
        :class:`~sym.sdk.resource.SRN`.
        """
        return self.srn.slug
