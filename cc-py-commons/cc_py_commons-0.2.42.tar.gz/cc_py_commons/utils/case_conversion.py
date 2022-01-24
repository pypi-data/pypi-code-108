import inflection
import re

def to_camel_case(input_dict):
    """ 
    Converts a dict with keys in snake case to dict with keys
    in camel case
    """
    new_dict = {}
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            parsed_key = camelize(key)
            new_dict[parsed_key] = value
    return new_dict

def to_snake_case(input_dict):
    """
    Converts a dict with keys in camel case to dict with keys
    in snake case
    """
    new_dict = {}
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            parsed_key = camel_to_snake_case(key)
            new_dict[parsed_key] = value
    return new_dict

def camel_to_snake_case(string):
   return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()

def camelize(key):
    parts = iter(key.split("_"))
    return next(parts) + "".join(i.title() for i in parts)

def add_undescore_before_numbers(input_dict):
    """
    Handle an issue with the inflection library while converting camel case 
    to underscore
    """
    updated_dict = {}
    for key, value in input_dict.items():
        match = re.search(r"\d", key)
        if match is not None:
            number_position = match.start()
            updated_key = key[:number_position] + '_' + key[number_position:]
            updated_dict[updated_key] = value
        else:
            updated_dict[key] = value

    return updated_dict
