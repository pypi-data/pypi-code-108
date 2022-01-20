"""Common messages functions."""
import logging
from string import Formatter
from typing import (
    Any,
    Union,
)

import jsonschema

SCHEMA_CUSTOM_MESSAGE_KEY = "x-validation-message"

LOGGER = logging.getLogger(__name__)


class TranslateMessage(dict):
    """This class is used to format strings with a default fallback option,
    when a key is not present on the dict to replace the placeholder, the
    current key is kept to be translated on the client side.
    """

    def __missing__(self, key):
        """Overrides the dict.__missing__ method to return the key name as a
        string format placeholder when key is not present in the dict.

        Parameters
        ----------
        key : str
            The key we are looking for.

        Returns
        -------
        str
            The missing message.
        """

        return "{" + key + "}"

    def translate(self, message: str) -> str:
        """Translates string value using .vformat insted of .format allowing a
        custom dict to be used.

        Parameters
        ----------
        message: str
            The incoming message.

        Returns
        -------
        str
            The formatted message
        """
        # pylint:disable=lost-exception,bare-except
        try:
            message = str(message)
            message = Formatter().vformat(message, (), self).strip()
            message = message.replace("  ", " ")
        except:
            LOGGER.error("Failed to translate message %s", message)
        finally:
            return message


class Messages:
    """Validation messages consolidation with format logic built-in."""

    required = "{field_name} is required."
    data_type = "{field_name} must be a valid {type}."
    items_between = (
        "The number of {field_name} has to be between {min_length} and {max_length}."
    )
    value_between = "The {field_name} value has to be between {minimum} and {maximum}."
    max_length = "Ensure {field_name} has no more than {max_length} characters."
    min_length = "Ensure {field_name} has no less than {min_length} characters."
    minimum = "Ensure {field_name} value is greater than or equal to {minimum}."
    maximum = "Ensure {field_name} value is less than or equal to {maximum}."
    equal = "Ensure {field_name} value is equal to {target}."
    enum = "{field_name} value is not a valid choice."
    not_found = "{field_name} is not found."
    max_items = "Ensure {field_name} has no more than {maximum} {items}."
    min_items = "Ensure {field_name} has at least {minimum} {items}."
    generic = "{field_name} must be {required}."
    generic_all = "All {items} must have {expected}."
    not_supported = "Field {field_name} is not supported."
    not_allowed = "{items} are not allowed."
    greater_than = "Ensure {field_name} value is greater than {minimum}."
    items_less_than = "The number of {field_name} has to be less than {max_length}."
    items_greater_than = (
        "The number of {field_name} has to be greater than {min_length}."
    )
    items_one_less_than = (
        "The number of {field_name} has to be one less than {min_length}."
    )
    verify = "Verify {field_name} and try again."
    reset_password = (
        "If a matching account was found, an email was sent to {email} to "
        "allow you to reset your password."
    )
    confirm_email = (
        "If a matching account was found and it has not been confirmed yet, "
        "an email was sent to {email} to allow you to confirm your email address."
    )
    in_ascending_order = "{field_name} must be in ascending order."
    invalid_client_version = (
        "Minimun version required is {minimum_version}, "
        "but Q-CTRL Python package {client_version} used."
    )

    def __init__(self, **kwargs):
        self._translate_message = TranslateMessage(kwargs)

    def __getattribute__(self, name: str) -> Any:
        """Overrides object.__getattribute__ and format messages before
        returning the value.

        Parameters
        ----------
        name: str
            The name of the attribute.

        Returns
        -------
        Any
            The value of the attribute.
        """

        if name != "_translate_message":
            message = object.__getattribute__(self, name)
            return self._translate_message.translate(message)
        return object.__getattribute__(self, name)


def get_custom_error_message(
    exc: jsonschema.exceptions.ValidationError,
) -> Union[None, str]:
    """Given a jsonschema ValidationError, returns the custom error message
    associated with the error (if any).

    Parameters
    ----------
    exc: jsonschema.exceptions.ValidationError
        The incoming exception.

    Returns
    -------
    Union[None, str]
        The extracted error message.
    """
    return exc.schema.get(SCHEMA_CUSTOM_MESSAGE_KEY, {}).get(exc.validator)


def inject_into_jsonschema(  # pylint:disable=too-many-branches
    schema: dict, **message_kwargs
):
    """Injects custom error messages into the jsonschema provided. If schema
    validation fails, use `get_custom_error_message` to retrieve the custom
    error message (if any).

    Parameters
    ----------
    schema: dict
    **message_kwargs :


    Returns
    -------
    """
    _type = schema.get("type")
    error_messages = {}

    # if object, inject into properties
    if _type == "object":
        properties = schema.get("properties", {})

        for field_name, field_schema in properties.items():
            inject_into_jsonschema(field_schema, field_name=field_name)

    # if array, inject into items
    elif _type == "array":
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")

        if min_items is not None:
            error_messages["minItems"] = Messages(
                min_length=min_items, **message_kwargs
            ).min_length

        if max_items is not None:
            error_messages["maxItems"] = Messages(
                max_length=max_items, **message_kwargs
            ).max_length

        item_schema = schema.get("items", {})

        # if validation for each item is given individually (as a list)
        if isinstance(item_schema, list):
            for item_schema in item_schema:
                inject_into_jsonschema(item_schema, **message_kwargs)

        # otherwise, validation applies to all items (as a dict)
        else:
            inject_into_jsonschema(item_schema, **message_kwargs)

    # all other types
    elif _type is not None:
        error_messages["type"] = Messages(type=_type, **message_kwargs).data_type

        exclusive_minimum = schema.get("exclusiveMinimum")
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")

        if exclusive_minimum is not None:
            error_messages["exclusiveMinimum"] = Messages(
                minimum=exclusive_minimum, **message_kwargs
            ).greater_than

        if minimum is not None:
            error_messages["minimum"] = Messages(
                minimum=minimum, **message_kwargs
            ).minimum

        if maximum is not None:
            error_messages["maximum"] = Messages(
                maximum=maximum, **message_kwargs
            ).maximum

    # add custom error messages to schema
    if error_messages:
        schema.update({SCHEMA_CUSTOM_MESSAGE_KEY: error_messages})
