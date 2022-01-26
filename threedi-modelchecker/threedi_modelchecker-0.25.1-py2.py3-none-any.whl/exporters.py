from threedi_modelchecker.checks.base import BaseCheck
from typing import NamedTuple


def print_errors(errors):
    """Simply prints all errors to stdout

    :param errors: iterator of BaseModelError
    """
    for error in errors:
        print(format_check_results(*error))


def export_to_file(errors, file):
    """Write errors to a new file, separated with newlines.

    File cannot be an already existing file.

    :param errors: iterator of BaseModelError
    :param file:
    :return: None
    :raise FileExistsError: if the file already exists
    """
    with open(file, "w") as f:
        for error in errors:
            f.write(format_check_results(*error) + "\n")


def format_check_results(check: BaseCheck, invalid_row: NamedTuple):
    OUTPUT_FORMAT = "{level}{error_code:04d} (id={row_id:d}) {description!s}"
    return OUTPUT_FORMAT.format(
        level=check.level.name[:1],
        error_code=check.error_code,
        row_id=invalid_row.id,
        description=check.description(),
    )
