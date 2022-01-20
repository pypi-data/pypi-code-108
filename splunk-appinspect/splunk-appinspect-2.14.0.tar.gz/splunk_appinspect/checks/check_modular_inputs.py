# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Modular inputs structure and standards

Modular inputs are configured in an **inputs.conf.spec** file located in the **/README** directory of the app. For more, see [Modular inputs overview](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsIntro), [Modular inputs configuration](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsSpec), and [Modular inputs basic example](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsBasicExample#Basic_implementation_requirements).
"""
import logging
import os

import splunk_appinspect

report_display_order = 12

logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
@splunk_appinspect.display(report_display_order=1)
def check_inputs_conf(app, reporter):
    """Check that a valid `inputs.conf.spec` file are located in the `README/`
    directory.
    """
    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        pass
    else:
        reporter_output = (
            f"No `{modular_inputs.specification_filename}` file exists. Please check that "
            " a valid `inputs.conf.spec` file is located in the `README/`directory."
        )
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
@splunk_appinspect.display(report_display_order=2)
def check_inputs_conf_spec_has_stanzas(app, reporter):
    """Check that README/inputs.conf.spec contains stanzas."""
    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        file_path = os.path.join(
            modular_inputs.specification_directory_path,
            modular_inputs.specification_filename,
        )

        inputs_specification_file = modular_inputs.get_specification_file()
        inputs_specification_file_stanzas_count = len(
            list(inputs_specification_file.sections())
        )
        if inputs_specification_file_stanzas_count == 0:
            reporter_output = (
                f"The inputs.conf.spec {modular_inputs.get_specification_app_filepath} "
                f"does not specify any stanzas. File: {file_path}"
            )
            reporter.fail(reporter_output, file_path)
        else:
            pass  # Success - stanzas were found
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(
    "splunk_appinspect", "cloud", "modular_inputs", "python3_version", "private_app"
)
@splunk_appinspect.cert_version(min="2.1.0")
def check_inputs_conf_spec_stanzas_has_python_version_property(
    app, reporter, target_splunk_version
):
    """Check that all the modular inputs defined in inputs.conf.spec are explicitly
    set the python.version to python3.
    """
    if target_splunk_version < "splunk_8_0":
        return

    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        if modular_inputs.has_modular_inputs():
            file_path = os.path.join(
                modular_inputs.specification_directory_path,
                modular_inputs.specification_filename,
            )

            global_default_python = None
            for modular_input in modular_inputs.get_modular_inputs():
                if modular_input.count_cross_plat_exes() > 0:
                    config_file_paths = app.get_config_file_paths("inputs.conf")
                    for directory, filename in config_file_paths.items():
                        inputs_conf = app.inputs_conf(directory)
                        if inputs_conf.has_section("default"):
                            default_section = inputs_conf.get_section("default")
                            if default_section.has_option("python.version"):
                                global_default_python = default_section.get_option(
                                    "python.version"
                                ).value

                        if inputs_conf.has_section(
                            modular_input.name
                        ) and inputs_conf.get_section(modular_input.name).has_option(
                            "python.version"
                        ):

                            if (
                                inputs_conf.get(modular_input.name, "python.version")
                                != "python3"
                            ):
                                reporter_output = (
                                    f'Modular input "{modular_input.name}" is defined in {file_path}, '
                                    "python.version should be explicitly set to python3."
                                )
                                reporter.fail(
                                    reporter_output, file_path, modular_input.lineno
                                )
                            break
                    else:
                        if (
                            not global_default_python
                            or global_default_python != "python3"
                        ):
                            reporter_output = (
                                f'Modular input "{modular_input.name}" is defined in {file_path}, '
                                "python.version should be explicitly set to python3 under each stanza."
                            )
                            reporter.fail(
                                reporter_output, file_path, modular_input.lineno
                            )

        else:
            reporter_output = "No modular inputs were detected."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
def check_inputs_conf_spec_stanzas_have_properties(app, reporter):
    """Check that modular inputs specify arguments."""
    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        if modular_inputs.has_modular_inputs():
            file_path = os.path.join(
                modular_inputs.specification_directory_path,
                modular_inputs.specification_filename,
            )
            for modular_input in modular_inputs.get_modular_inputs():
                if not modular_input.args_exist():
                    lineno = modular_input.lineno
                    reporter_output = (
                        f"The stanza [{modular_input.name}] does not include any args. "
                        f"File: {file_path}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, file_path, lineno)
                else:
                    pass  # SUCCESS - The modular input has arguments
        else:
            reporter_output = "No modular inputs were detected."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
def check_inputs_conf_spec_has_no_duplicate_stanzas(app, reporter):
    """Check that modular inputs do not have duplicate stanzas."""
    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        inputs_specification_file = modular_inputs.get_specification_file()
        file_path = os.path.join(
            modular_inputs.specification_directory_path,
            modular_inputs.specification_filename,
        )

        for (
            error,
            line_number,
            section,
        ) in inputs_specification_file.errors:
            if error.startswith("Duplicate stanza"):
                reporter_output = f"{error}  File: {file_path}  Stanza: {section}  Line: {line_number}"
                reporter.warn(reporter_output, file_path, line_number)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` was detected."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
def check_inputs_conf_spec_has_no_duplicate_properties(app, reporter):
    """Check that modular input stanzas do not contain duplicate arguments."""
    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        inputs_specification_file = modular_inputs.get_specification_file()
        file_path = os.path.join(
            modular_inputs.specification_directory_path,
            modular_inputs.specification_filename,
        )

        for (
            error,
            line_number,
            section,
        ) in inputs_specification_file.errors:
            if error.startswith("Repeat item name"):
                reporter_output = f"{error}  File: {file_path}  Stanza: {section}  Line: {line_number}"
                reporter.warn(reporter_output, file_path, line_number)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` was detected."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
def check_inputs_conf_spec_stanza_args_broken_correctly(app, reporter):
    """Check lines breaks are included in configuration when using a modular
    input.
    """

    modular_inputs = app.get_modular_inputs()

    if modular_inputs.has_specification_file():
        raw_specification_file = modular_inputs.get_raw_specification_file()
        file_path = os.path.join(
            modular_inputs.specification_directory_path,
            modular_inputs.specification_filename,
        )

        # From https://github.com/splunk/splunk-app-validator
        if len(raw_specification_file.decode().split("\n")) > 1:
            pass
        else:
            reporter_output = (
                f"The inputs.conf.spec has incorrect line breaks. File: {file_path}"
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` was detected."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "modular_inputs")
@splunk_appinspect.cert_version(min="1.1.0")
def check_modular_inputs_scripts_exist(app, reporter):
    """Check that there is a script file in `bin/` for each modular input
    defined in `README/inputs.conf.spec`.
    """

    modular_inputs = app.get_modular_inputs()
    if modular_inputs.has_specification_file():
        if modular_inputs.has_modular_inputs():
            file_path = os.path.join("README", "inputs.conf.spec")
            for mi in modular_inputs.get_modular_inputs():

                # a) is there a cross plat file (.py) in default/bin?
                if mi.count_cross_plat_exes() > 0:
                    continue

                win_exes = mi.count_win_exes()
                linux_exes = mi.count_linux_exes()
                win_arch_exes = mi.count_win_arch_exes()
                linux_arch_exes = mi.count_linux_arch_exes()
                darwin_arch_exes = mi.count_darwin_arch_exes()

                # b) is there a file per plat in default/bin?
                if win_exes > 0 or linux_exes > 0:
                    continue

                # c) is there a file per arch?
                if win_arch_exes > 0 or linux_arch_exes > 0 or darwin_arch_exes > 0:
                    continue
                else:
                    reporter_output = (
                        "No executable exists for the modular input"
                        f" '{mi.name}'. File: {file_path}, Line: {mi.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, mi.lineno)
        else:
            reporter_output = "No modular inputs were detected."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` was detected."
        reporter.not_applicable(reporter_output)
