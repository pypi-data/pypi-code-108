def makeStorageKey(value: str) -> str:
    """Make Storage Key

    Create a key from a string that will ensure similar names can not exist,
    for example.

    * Linux: Node
    * Linux Node
    * linux Node

    :param value: String value to sanitize
    :return: String
    """
    value = "".join([c if c.isalnum() else "_" for c in value]).lower()
    while "_" in value:
        value = value.replace("_", "")
    return value
