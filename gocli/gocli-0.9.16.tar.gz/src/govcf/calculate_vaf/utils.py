def int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        pass


def int_or_zero(value):
    try:
        return int(value)
    except (TypeError, ValueError):  # pragma: no cover
        return 0
