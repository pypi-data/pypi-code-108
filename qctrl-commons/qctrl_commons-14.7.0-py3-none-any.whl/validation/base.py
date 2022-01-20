"""Validation utilities for GraphQL"""
import logging
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
)

import jsonschema

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.messages import (
    get_custom_error_message,
    inject_into_jsonschema,
)

LOGGER = logging.getLogger(__name__)


class BaseMutationInputValidator:
    """Base class for custom validation of GraphQL mutation queries.

    Subclasses should define methods with the prefix
    `check` that perform validation. Each method should
    accept a single argument which is the `input` dict
    being validated. These methods should raise a
    ValidationError if validation fails.

    For simple field validation using jsonschema, override
    the `properties` class attribute with a jsonschema for
    any fields expected to be in the `input` dict e.g.

    properties = {
        "age": {
            "type": "number"
        },
        "name": {
            "type": "string"
        }
    }
    """

    properties: Optional[Dict[str, Any]] = None

    def __call__(self, input_: Dict[str, Any]) -> Union[None, List]:
        """Runs validation for the `input` dict.

        Parameters
        ----------
        input_ : dict
            dict of values from the GraphQL
            mutation query

        Returns
        -------
        Union[None, List]
            a list of errors or None.

        Raises
        ------
        QctrlFieldError
            when any validation fails
        """
        errors = []

        # collect any errors from the check methods
        for func in self._get_check_methods():
            try:
                func(self, input_)
            except QctrlFieldError as exc:
                errors.append(exc)

        return errors if errors else None

    @classmethod
    def _get_check_methods(cls) -> Iterator:
        """Collects and returns validation methods: any method beginning with
        `check`.

        Yields
        ------
        Iterator
            The `check` method.
        """
        for attr in dir(cls):
            value = getattr(cls, attr)

            if attr.startswith("check") and callable(value):
                yield value

    @property
    def schema(self) -> dict:
        """Returns a jsonschema with custom error messages for validating the
        input dict.

        Returns
        -------
        dict
            The serialized schema.
        """
        result = {"type": "object"}

        if self.properties:
            result.update({"properties": self.properties.copy()})

        inject_into_jsonschema(result)
        return result

    def check_schema(self, input_: dict) -> None:
        """Built-in check method to validate the `input` dict against the
        jsonschema generated from the `properties` class attribute.

        Parameters
        ----------
        input_: dict

        Raises
        ------
        QctrlFieldError
            If the schema is not valid.
        """
        try:
            jsonschema.validate(input_, self.schema)
        except jsonschema.exceptions.ValidationError as exc:
            error_message = get_custom_error_message(exc)
            # no custom error message available - construct
            # default error message
            if not error_message:
                field_name = ".".join(exc.absolute_path)
                error_message = f"{field_name}: {exc.message}"

            raise QctrlFieldError(message=str(error_message)) from exc
