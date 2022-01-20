import re
from iosdebug.processing.starting.create_basic_mock_implementation import (
    create_basic_mock_implementation,
)
from iosdebug.templates import FUNCTION_TEMPLATE


def get_updated_mocked_implementation(functions, mocked_impl, mock_functions):
    added_functions = []
    deleted_functions = []
    current_function_declarations = [func.declaration for func in functions]

    for function in functions:
        if function.declaration not in mocked_impl:
            added_functions.append(function)

    for function in mock_functions:
        if function not in current_function_declarations:
            deleted_functions.append(function)

    updated_mock_impl = mocked_impl

    for function in deleted_functions:
        function = function.replace("(", "\\(").replace(")", "\\)")
        updated_mock_impl = re.sub(
            r"[\s]+func " + function + r" {[\s\S]+?\n    }", "", updated_mock_impl
        )

    for function in added_functions:
        processed_func_template = create_basic_mock_implementation(function)
        extension_regex = r"extension .* {[\s\S]+?\n}"
        extension = re.findall(extension_regex, updated_mock_impl)[0]
        updated_extension = extension.replace(
            "\n}", "\n\n    " + processed_func_template + "\n}"
        )
        updated_mock_impl = re.sub(
            extension_regex, updated_extension, updated_mock_impl
        )

    return updated_mock_impl
