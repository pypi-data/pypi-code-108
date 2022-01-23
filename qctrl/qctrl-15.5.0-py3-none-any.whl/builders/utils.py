"""Module for utility."""
import re

import inflection


def _get_function_name(mutation_name: str) -> str:
    """
    Returns the corresponding function name
    for the given mutation name.
    """
    name = re.sub("^core__", "", mutation_name)
    return inflection.underscore(name)
