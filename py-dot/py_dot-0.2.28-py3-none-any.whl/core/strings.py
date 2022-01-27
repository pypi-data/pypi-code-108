import base64
import re


def to_snake(value: str) -> str:
    """ String to snake_case

    - camelCase: camel_case
    - space case: space_case
    - kebab-case: kebab_case

    :param value: Target Value
    :return:
    """
    words = re.findall(r'([A-Z]?[^_\-\sA-Z]+)', value)
    return '_'.join(map(lambda x: x.lower(), words))


def to_base64(value: str):
    encoded_value = base64.urlsafe_b64encode(value.encode('utf-8'))
    return str(encoded_value, 'utf-8')


def from_base64(value: str):
    decoded_value = base64.urlsafe_b64decode(value)
    return str(decoded_value, 'utf-8')