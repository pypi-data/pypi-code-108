from iosdebug.processing.starting.get_mock_functions_variants import (
    get_mock_functions_variants,
)
from iosdebug.processing.starting.get_updated_mocked_implementation import (
    get_updated_mocked_implementation,
)
from iosdebug.processing.starting.create_basic_mock_implementation import (
    create_basic_mock_implementation,
)
from iosdebug.processing.starting.get_original_registration import (
    get_original_registrations,
)
from iosdebug.processing.starting.get_stored_mock_implementation import (
    get_stored_mock_implementation,
)
from iosdebug.templates import FUNCTION_TEMPLATE, TEMPLATE


def write_mock_implementations(
    path_to_content_map, protocol_to_protocol_functions, root_path
):
    print("Creating mock implementations...")
    original_registrations = get_original_registrations(
        path_to_content_map, protocol_to_protocol_functions
    )
    for protocol in protocol_to_protocol_functions:
        for path in path_to_content_map:
            if "protocol " + protocol in path_to_content_map[path]:
                stored_impl = get_stored_mock_implementation(root_path, protocol)
                if stored_impl:
                    mock_variants = get_mock_functions_variants({protocol: stored_impl})
                    updated_impl = get_updated_mocked_implementation(
                        protocol_to_protocol_functions[protocol],
                        stored_impl,
                        mock_variants[protocol],
                    )
                    processed_template = (
                        "\n// MARK: - Mock implementation" + updated_impl
                    )
                else:
                    functions = []
                    for function in protocol_to_protocol_functions[protocol]:
                        processed_func_template = create_basic_mock_implementation(
                            function
                        )
                        functions.append(processed_func_template)

                    processed_template = TEMPLATE
                    processed_template = processed_template.replace(
                        "<PROTOCOL>", protocol
                    )

                    processed_template = processed_template.replace(
                        "<FUNCTIONS>", "\n\n    ".join(functions)
                    )

                try:
                    original_registration = original_registrations[protocol]
                    original_registration_initial_spaces = len(
                        original_registration
                    ) - len(original_registration.lstrip())
                    indentation_difference = original_registration_initial_spaces - 4
                    lines = original_registration.split("\n")
                    matched_indent = [line[indentation_difference:] for line in lines]
                    original_registration = "\n".join(matched_indent)

                    processed_template = processed_template.replace(
                        "<ORIGINAL_REGISTRATION>", original_registration
                    )
                except KeyError:
                    print("No registration found for protoco " + protocol)
                    processed_template = processed_template.replace(
                        "<ORIGINAL_REGISTRATION>",
                        "// !!! No original registration found !!!",
                    )

                with open(path, "a") as file:
                    file.write(processed_template)
    print("Mock implementations created.")
