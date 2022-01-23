# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import logging
from collections import OrderedDict
from enum import (
    Enum,
    EnumMeta,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import attr
import inflection
import numpy as np
from cached_property import cached_property
from graphql import (
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLType,
    GraphQLUnionType,
)
from typing_utils import get_origin

from qctrl.builders.doc import (
    ClassAttribute,
    ClassDocstring,
)
from qctrl.dynamic import register_dynamic_class
from qctrl.utils import (
    _is_deprecated,
    _is_undefined,
)

from .graphql_utils import BaseTypeRegistry
from .graphql_utils.handlers import (
    NamedInputObjectHandler,
    NamedObjectHandler,
)
from .graphql_utils.handlers.mixins import ScalarMixin

LOGGER = logging.getLogger(__name__)


class TypeOverrideMixin:  # pylint:disable=too-few-public-methods
    """Handler mixin to provide the type hint
    to be used for an overridden type.
    """

    _type_hint = None

    @property
    def type_hint(self):  # pylint:disable=missing-function-docstring
        if self._type_hint is None:
            raise RuntimeError

        return self._type_hint


class TypeRegistry(BaseTypeRegistry):
    """Builds dataclasses from GraphQL types."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._types = {}

    def has_override(self, type_name: str) -> bool:
        """
        Checks if there is an override registered for
        the given type.
        """
        return type_name in self._overrides

    def get_override(self, type_name: str) -> TypeOverrideMixin:
        """
        Returns the Override for the given type,
        assuming one exists.
        """
        if not self.has_override(type_name):
            raise KeyError(f"override does not exist: {type_name}")

        return self._overrides[type_name]

    @cached_property
    def _overrides(self):
        """Collects all type overrides from the environment."""
        _overrides = {}

        for handler in self.env.iter_handlers(TypeOverrideMixin):
            if isinstance(handler, NamedObjectHandler):
                _overrides[handler.object_name] = handler

            if isinstance(handler, NamedInputObjectHandler):
                _overrides[handler.input_object_name] = handler

        return _overrides

    @cached_property
    def _scalar_types(self):
        """Collects all scalar handlers from the environment."""
        _scalar_types = {}

        for handler in self.env.iter_handlers(ScalarMixin):
            _scalar_types[handler.scalar_name] = handler.scalar_type_hint

        return _scalar_types

    def get_scalar_type_hint(self, field_type: GraphQLScalarType) -> Optional[type]:
        """Returns the type hint for the given scalar type."""
        return self._scalar_types.get(field_type.name)

    def get_type_hint(self, field_type: GraphQLType, **build_opts) -> type:
        """Returns the type hint for the GraphQL type. If there is no
        corresponding type, a new type is created. If the type needs to be
        created, `build_opts` are passed to the `build` method.

        Parameters
        ----------
        field_type: GraphQLType
            gql field type (i.e GraphQLNonNull, GraphQLScalarType)
        build_opts: Dict
            options for forging class.

        Returns
        -------
        type
            type hint for the field.
        """
        LOGGER.debug("getting type hint for: %s", field_type)

        # non-null
        if isinstance(field_type, GraphQLNonNull):
            return self.get_type_hint(field_type.of_type, **build_opts)

        # scalar
        if isinstance(field_type, GraphQLScalarType):
            type_hint = self.get_scalar_type_hint(field_type)

            if type_hint is None:
                LOGGER.warning("unhandled scalar type: %s", field_type)

            return type_hint

        # list
        if isinstance(field_type, GraphQLList):
            return List[self.get_type_hint(field_type.of_type, **build_opts)]

        # overridden type
        if self.has_override(field_type.name):
            override = self.get_override(field_type.name)
            return override.type_hint

        # existing type
        if self.has_type(field_type.name):
            return self.get_type(field_type.name)

        # build new type
        return self.build(field_type, **build_opts)

    def get_doc_field_type(self, field_type: GraphQLType) -> Optional[str]:
        """
        Returns the field type string to be used in a docstring.

        Parameters
        ----------
        field_type: GraphQLType
            gql field type (i.e GraphQLNonNull, GraphQLScalarType)

        Returns
        -------
        str, optional
            field type in string.
        """
        # non-null
        if isinstance(field_type, GraphQLNonNull):
            return self.get_doc_field_type(field_type.of_type)

        # scalar
        if isinstance(field_type, GraphQLScalarType):
            type_hint = self.get_scalar_type_hint(field_type)

            if type_hint is None:
                LOGGER.warning("unhandled scalar type: %s", field_type)

            else:
                if type_hint.__module__ == "builtins":
                    type_hint = type_hint.__qualname__
                else:
                    type_hint = type_hint.__module__ + "." + type_hint.__qualname__

            return type_hint

        # list
        if isinstance(field_type, GraphQLList):
            sub_type = self.get_doc_field_type(field_type.of_type)
            return f"List[{sub_type}]"

        # overridden type
        if self.has_override(field_type.name):
            override = self.get_override(field_type.name)
            return override.type_hint.__name__

        # get existing type
        if self.has_type(field_type.name):
            cls = self.get_type(field_type.name)

            # e.g qctrl.dynamic.types.filter_function.Drive
            # cls.__module = qctrl.dynamic.types.filter_function
            # cls.__name__ = Drive
            return cls.__module__ + "." + cls.__name__

        # unable to determine class name
        return None

    def has_type(self, type_name: str) -> bool:
        """
        Checks if the type has been registered.
        """
        return type_name in self._types

    def get_type(self, type_name: str) -> type:
        """
        Returns the type associated with the type name.
        """
        return self._types[type_name]

    def get_type_map(self) -> Dict[str, type]:
        """Returns the type map."""
        return self._types

    @staticmethod
    def parse_name(name: str) -> Tuple[str, List[str]]:
        """
        Parses the GraphQL object name and returns
        a tuple of the base name and the namespace.
        Example:
        Core__Special__Type => ("Type", ["Core", "Special"])
        """
        parts = name.split("__")
        return parts[-1], parts[:-1]

    def build(self, obj: GraphQLType, base: type = None) -> Union[type, Tuple[type]]:
        """
        Builds a new data class from the GraphQL type.
        """
        LOGGER.debug("building type for %s - %s", obj, type(obj))

        # handle non-null
        if isinstance(obj, GraphQLNonNull):
            return self.build(obj.of_type, base)

        # handle enum
        if isinstance(obj, GraphQLEnumType):
            # Create "attributes" for the enum values to ensure they're
            # documented.
            attrs = []
            for name, value in obj.values.items():
                attrs.append(ClassAttribute(name, description=value.description))
            docstring = ClassDocstring(description=obj.description, attrs=attrs)
            cls = self._create_enum(obj.name, obj.values, base, str(docstring))
            return cls

        if isinstance(obj, GraphQLUnionType):
            return tuple(self.build(union_type, base) for union_type in obj.types)

        # handle complex type with sub fields
        fields = OrderedDict()
        docstring = ClassDocstring(description=obj.description)

        # for each sub field
        for field_name, field in obj.fields.items():

            is_optional = False

            if _is_deprecated(field):
                LOGGER.debug("%s.%s is deprecated - skipping", obj.name, field_name)
                continue

            attr_name = self.env.field_to_attr(field_name)

            # get type hint for sub field
            type_hint = self.get_type_hint(field.type)

            # build field definition
            field_def = dict(
                kw_only=True,
                type=type_hint,
            )

            # if building non-input type, all sub-fields are
            # optional as it's possible to request partial data
            if not isinstance(obj, GraphQLInputObjectType):
                is_optional = True
                field_def.update(dict(default=None))

            # otherwise, check if sub field has default value
            elif isinstance(field, GraphQLInputField):

                # check for default value
                if not _is_undefined(field.default_value):
                    # attribute is optional if it has default value
                    is_optional = True
                    field_def.update(dict(default=field.default_value))

                # if nullable, make optional
                elif not isinstance(field.type, GraphQLNonNull):
                    # attribute is optional if it is nullable
                    is_optional = True
                    field_def.update(dict(default=None))

            # add type validator
            validator = self._get_validator(type_hint, is_optional)
            field_def.update(dict(validator=validator))

            # add field definition
            fields[attr_name] = attr.ib(**field_def)

            # add attr for docstring
            docstring.attrs.append(
                ClassAttribute(
                    attr_name,
                    attr_type=self.get_doc_field_type(field.type),
                    description=field.description,
                    optional=is_optional,
                )
            )

        # create new attr class
        cls = self._create_attr_class(obj.name, fields, base, str(docstring))
        return cls

    @staticmethod
    def _get_validator(type_hint, is_optional):
        # get origin type from type hints if exists (i.e.: list for List[])
        base_type = get_origin(type_hint) or type_hint
        type_checking = [base_type]

        # accepts dict as custom types input
        if attr.has(base_type):
            type_checking.append(dict)

        # handle optional attributes
        if is_optional:
            type_checking.append(type(None))

        # accept ndarrays where list type is accepted
        if list in type_checking:
            type_checking.append(np.ndarray)
            type_checking.append(tuple)

        # accept float values where complex type are accepted
        if complex in type_checking:
            type_checking.append(float)
            type_checking.append(np.complexfloating)

        # accept int values where float type are accepted
        if float in type_checking:
            type_checking.append(int)
            type_checking.append(np.floating)

        if int in type_checking:
            type_checking.append(np.integer)

        # Enum values can be set as string
        if isinstance(type_hint, EnumMeta):
            type_checking.append(str)

        validator = attr.validators.instance_of(tuple(type_checking))
        return validator

    @staticmethod
    def _get_submodule(namespace: List[str]) -> str:
        submodule = "types"

        if namespace:
            submodule = f"{submodule}.{'.'.join(map(inflection.underscore, namespace))}"

        return submodule

    def _create_enum(
        self,
        object_name: str,
        values: Dict[str, Any],
        base: type = None,
        docstring: str = None,
    ) -> type:
        """
        Creates a new enum class and registers it.
        """
        name, namespace = self.parse_name(object_name)
        cls = Enum(name, values, type=base)

        if docstring:
            cls.__doc__ = str(docstring)

        self._register(
            cls,
            name=object_name,
            submodule=self._get_submodule(namespace),
        )

        return cls

    def _create_attr_class(
        self,
        object_name: str,
        fields: OrderedDict,
        base: type = None,
        docstring: str = None,
    ) -> type:
        """
        Creates a new attr class and registers it.
        """
        name, namespace = self.parse_name(object_name)

        if base:
            cls = attr.make_class(name, fields, bases=(base,))
        else:
            cls = attr.make_class(name, fields)

        if docstring:
            cls.__doc__ = str(docstring)

        self._register(
            cls,
            name=object_name,
            submodule=self._get_submodule(namespace),
        )

        return cls

    def _register(self, cls: type, name: str = None, submodule: str = None) -> None:
        """
        Registers the new type class.

        Raises
        -------
        KeyError
            duplicate type name.
        """
        key = name or cls.__name__

        if key in self._types:
            raise KeyError(f"duplicate type name: {key}")

        self._types[key] = cls
        register_dynamic_class(cls, submodule)
