"""Misc helpers used in the application"""

# system imports
from datetime import date, timedelta
from argparse import ArgumentTypeError


def parse_key_val_var(var_str):
    """Convert key=val string to tuple.

    Arguments:
        var_str -- String in the format 'foo=bar'
    """
    items = var_str.split('=')
    return (items[0].strip(), items[1].strip())


def convert_key_value_vars_to_dict(var_list):
    """Convert list of 'key=val' strings to dict.

    Arguments:
        var_list -- List like ['foo=bar', 'bar=baz']"""
    variables = {}
    for var in var_list:
        key, value = parse_key_val_var(var)
        variables[key] = value
    return variables


def get_date_object_for_alias(alias):
    """Get a datetime object for a given alias.
    If alias is already a datetime object it will just be returned.

    Arguments:
        alias - String or date object
    """
    if isinstance(alias, date):
        return alias # it's already a date
    if alias == 'today':
        return date.today()
    if alias == 'yesterday':
        return date.today() - timedelta(days=1)
    if alias == 'tomorrow':
        return date.today() + timedelta(days=1)
    return None

def argparse_valid_iso_date(date_str):
    """Validator used by argparse to make sure given date string is in ISO format.

    Arguments:
        date_str -- date string
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError as err:
        raise ArgumentTypeError(f'not a valid date: {date_str}') from err
