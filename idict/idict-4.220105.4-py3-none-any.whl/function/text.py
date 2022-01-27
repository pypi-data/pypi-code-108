import json


def value2text(input="value", output="text", **kwargs):
    """
    >>> import numpy as np
    >>> X = [[0, "a", 1.6], [3.2, "b", 2], [8, "c", 3]]
    >>> value2text(value=X)
    {'text': '[[0, "a", 1.6], [3.2, "b", 2], [8, "c", 3]]', '_history': Ellipsis}
    """
    return {output: json.dumps(kwargs[input]), "_history": ...}


value2text.metadata = {
    "id": "------------------------json--value2text",
    "name": "value2text",
    "description": "Generate a JSON-formatted text representing the given object.",
    "parameters": ...,
    "code": ...,
}
