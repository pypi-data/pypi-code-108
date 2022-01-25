from datetime import date

FIELD_TYPES_BY_CLASS = {int: "int", float: "float", date: "date"}


def get_field_type(v):
    prefix = ""

    if isinstance(v, list):
        prefix = "m"
        v = v[0] if len(v) > 0 else None

    field_type = FIELD_TYPES_BY_CLASS.get(v.__class__, "string")
    return f"{prefix}{field_type}"
