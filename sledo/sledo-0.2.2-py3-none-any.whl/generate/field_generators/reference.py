import re
from typing import Dict
from schema import Schema


class ReferenceFieldGenerator():
    option_schema = Schema({
        "field": str,
        "field_attr": str,
    })

    def __init__(self, options: Dict[str, str]):
        self.options = self.option_schema.validate(options)


# e.g. $order.date
reference_regexp = re.compile("^\$(.+)\.(.+)$")


def to_ref(raw: str):
    match = reference_regexp.match(raw)

    if match is None:
        raise Exception(f"Value '{raw}' is not a valid reference!")

    return ReferenceFieldGenerator({
        "field": match[1],
        "field_attr": match[2]
    })
