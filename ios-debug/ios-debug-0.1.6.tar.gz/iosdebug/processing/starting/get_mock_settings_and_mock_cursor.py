from iosdebug.templates import (
    MOCK_MANAGER_SETTINGS_TEMPLATE,
    FUNCTION_SETTINGS_TEMPLATE,
    MOCK_MANAGER_TEMPLATE,
)


def get_mock_settings_and_mock_cursor(
    protocol_to_protocol_functions, protocol_to_mock_function_variants
):
    mock_settings = []
    mock_cursors = []
    for repository in protocol_to_protocol_functions:
        funcs = protocol_to_protocol_functions[repository]
        func_annotations = []
        for func in funcs:
            if func.params:
                external_param_names = []
                for param in func.params:
                    external_param_name = param.split()[0]
                    if ":" not in external_param_name:
                        external_param_name += ":"
                    external_param_names.append(external_param_name)
            else:
                external_param_names = ""
            func_annotation = func.name + "(" + "".join(external_param_names) + ")"
            if func_annotation not in func_annotations:
                func_annotations.append(
                    func.name + "(" + "".join(external_param_names) + ")"
                )

        function_settings = []
        function_cursors = []
        for index, annotation in enumerate(func_annotations):
            func_declaration = funcs[index].declaration
            mocked_variants = protocol_to_mock_function_variants[repository][
                func_declaration
            ]
            function_settings.append(
                FUNCTION_SETTINGS_TEMPLATE.replace(
                    "<FUNCTION_ANNOTATION>",
                    annotation
                    # TODO: Implement getting mocked variants
                ).replace("<SETTINGS_VALUES>", "[" + ", ".join(mocked_variants) + "]")
            )
            function_cursors.append(
                FUNCTION_SETTINGS_TEMPLATE.replace(
                    "<FUNCTION_ANNOTATION>", annotation
                ).replace("<SETTINGS_VALUES>", "0")
            )

        processed_template = MOCK_MANAGER_SETTINGS_TEMPLATE.replace(
            "<PROTOCOL>", "Mock" + repository + "Impl"
        )
        processed_template_settings = processed_template.replace(
            "<FUNCTION_SETTINGS>", ",\n    ".join(function_settings)
        )
        processed_template_cursors = processed_template.replace(
            "<FUNCTION_SETTINGS>", ",\n    ".join(function_cursors)
        )

        mock_settings.append(processed_template_settings)
        mock_cursors.append(processed_template_cursors)

    processed_mock_manager = MOCK_MANAGER_TEMPLATE.replace(
        "<MOCK_CURSORS>", ",\n         ".join(mock_cursors)
    )
    processed_mock_manager = processed_mock_manager.replace(
        "<MOCK_SETTINGS>", ",\n         ".join(mock_settings)
    )
    return processed_mock_manager
