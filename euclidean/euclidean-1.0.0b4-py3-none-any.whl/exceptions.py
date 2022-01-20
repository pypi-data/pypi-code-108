def unexpected_type_error(arg_name, expected_type, actual_value):
    return TypeError(
        "'{name}' must be {type!r} (got {value!r} that is a "
        "{actual!r}).".format(
            name=arg_name,
            type=expected_type,
            actual=actual_value.__class__,
            value=actual_value,
        ),
        arg_name,
        expected_type,
        actual_value,
    )
