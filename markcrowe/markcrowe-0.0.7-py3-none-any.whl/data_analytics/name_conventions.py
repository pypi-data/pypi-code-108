import re as RegularExpression


def camel_to_snake_case(name: str) -> str:
    """
    Convert CamelCase to snake_case
    :param name: string
    :return: snake_case string
    """
    name = RegularExpression.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return RegularExpression.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def english_to_kebab_case(name: str) -> str:
    """
    Convert CamelCase to snake_case
    :param name: string
    :return: snake_case string
    """
    return name.lower().replace(" ", "-")
