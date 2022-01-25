"""
This function gets called during every request by the
extra_html and extra_scripts to validate all the custom html and scripts for a specific path.
"""
import logging

logger = logging.getLogger(__name__)

ERROR_MESSAGE = "could not get loaded. '%s' attribute is missing or is an invalid option."


def set_default_option(values, key, allowed_values, default_value):
    """
    Set the default option if the values[key] does not match the allowed values.

    Parameters:
        values (dict): a dict with values to set option default
        key (string): a key when to set option default
        allowed_values (array): an array of allowed values
        default_value (string): a value default to set in values with key

    Returns:
        dict: a dict with values seted according option default
    """
    if values.get(key) not in allowed_values:
        values[key] = default_value

    return values


def check_attributes_required(values, attributes, error_message_prefix):
    """
    Validate the existence of at least one attribute in attributes.

    Parameters:
        values (dict): a dict with values to validate according to attributes
        attributes (array): a array with attributes to validate
        error_message_prefix (string): a string prefix to error message

    Returns:
        bool: a boolean indicating whether at least one attribute is in attributes.
    """
    for attribute in attributes:
        if attribute in values:
            return True

    logger.error(
        "{prefix} {error_message}".format(prefix=error_message_prefix, error_message=ERROR_MESSAGE),
        attributes
    )

    return False
