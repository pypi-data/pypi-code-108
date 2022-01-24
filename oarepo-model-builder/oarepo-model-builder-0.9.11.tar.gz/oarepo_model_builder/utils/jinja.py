def package_name(value):
    return value.rsplit('.', maxsplit=1)[0]


def base_name(value):
    return value.rsplit('.', maxsplit=1)[-1]


def in_different_package(current_package_name, value):
    return current_package_name != package_name(value)


def with_defined_prefix(always_defined_import_prefixes, value):
    return package_name(value) in always_defined_import_prefixes
