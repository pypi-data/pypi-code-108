# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Custom search command structure and standards

Custom search commands are defined in a **commands.conf** file in the **/default** directory of the app. For more, see [About writing custom search commands](http://docs.splunk.com/Documentation/Splunk/latest/Search/Aboutcustomsearchcommands) and [commands.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Commandsconf).
"""
import logging
import os
import re
import sys

import splunk_appinspect

report_display_order = 20
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect", "custom_search_commands")
@splunk_appinspect.cert_version(min="1.1.7")
@splunk_appinspect.display(report_display_order=1)
def check_command_conf_exists(app, reporter):
    """Check that `commands.conf` exists at `default/commands.conf`."""
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        pass
    else:
        reporter_message = "No commands.conf exists."
        reporter.not_applicable(reporter_message)


@splunk_appinspect.tags("splunk_appinspect", "custom_search_commands")
@splunk_appinspect.cert_version(min="1.1.7")
@splunk_appinspect.display(report_display_order=2)
def check_default_meta_exists(app, reporter):
    """Check that a valid
    [default.meta](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Defaultmetaconf)
    file exists when using a custom search command.
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        try:
            if app.get_config("default.meta", "metadata"):
                pass
        except IOError:
            reporter_message = "No default.meta exists."
            reporter.fail(reporter_message)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "python3_version", "private_app")
@splunk_appinspect.cert_version(min="2.1.0")
def check_command_scripts_python_version(app, reporter, target_splunk_version):
    """Check that commands.conf must explicitly define the python.version
    to be python3 for each python-scripted custom command.
    """
    if target_splunk_version < "splunk_8_0":
        return

    custom_commands = app.get_custom_commands()
    if not custom_commands.configuration_file_exists():
        reporter.not_applicable("`commands.conf` does not exist.")
        return
    for command in custom_commands.get_commands():
        file_path = os.path.join("default", "commands.conf")
        if (
            not command.chunked or command.chunked == "false"
        ) and command.file_name.endswith(".py"):
            if "python.version" not in command.args:
                reporter.fail(
                    f"Custom command {command.name} doesn't define python.version,"
                    " python.version should be explicitly set to python3.",
                    file_path,
                )
                continue
            value, lineno = command.args["python.version"]
            if value != "python3":
                reporter.fail(
                    f"Custom command {command.name} doesn't define python.version as python3,"
                    " python.version should be explicitly set to python3.",
                    file_path,
                    lineno,
                )
                continue
            if sys.version_info >= (3,) and len(command.v1_exes) > 0:
                # The following logic will only take effect when running interpreter
                # is Python 3
                python_script_resource = command.v1_exes[0]
                if python_script_resource.exists():
                    import ast

                    fd = open(python_script_resource.file_path)
                    try:
                        ast.parse(fd.read())
                    except Exception as ex:
                        reporter.fail(
                            f"Custom command {command.name} defines a script that is not Python 3 compatible. "
                            f'The error is "{ex}". ',
                            "Upgrade your Python script to be Python 3 compatible.",
                            os.path.join("bin", command.file_name),
                        )


@splunk_appinspect.tags("splunk_appinspect", "custom_search_commands", "manual")
@splunk_appinspect.cert_version(min="1.1.7")
@splunk_appinspect.display(report_display_order=2)
def check_command_scripts_exist(app, reporter):
    """Check that custom search commands have an executable or script per
    stanza.
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        for command in custom_commands.get_commands():

            lineno = command.lineno

            with_path_suffix_pattern = r".*\.path$"
            is_filename_with_path_suffix = re.match(
                with_path_suffix_pattern, command.file_name
            )

            # can't find scripts in `bin/` or `<PLATFORM>/bin`
            if not is_filename_with_path_suffix and not command.file_name_exe:
                reporter_message = (
                    f"The script of command [{command.name}] was not found "
                    "or the script type is not supported. "
                    f"File: {file_path}, Line: {lineno}."
                )
                reporter.fail(reporter_message, file_path, lineno)

            # v2 command
            elif command.is_v2():
                _check_v2_command(command, reporter, is_filename_with_path_suffix)

            # v1 command
            else:
                _check_v1_command(command, reporter)
    else:
        reporter.not_applicable("No `commands.conf` file exists.")


def _check_v1_command(command, reporter):
    file_path = os.path.join("default", "commands.conf")
    lineno = command.lineno
    count_v1_exes = command.count_v1_exes()

    # file extension is not in v1 extensions
    if count_v1_exes == 0:
        reporter_message = (
            f"The stanza [{command.name}] in commands.conf must use a .py or "
            f".pl script. File: {file_path}, Line: {lineno}."
        )
        reporter.fail(reporter_message, file_path, lineno)


def _check_v2_command(command, reporter, is_filename_with_path_suffix):
    file_path = os.path.join("default", "commands.conf")
    lineno = command.lineno
    filename_is_specified = command.file_name_specified()
    count_v2_exes = (
        command.count_win_exes()
        + command.count_linux_exes()
        + command.count_linux_arch_exes()
        + command.count_win_arch_exes()
        + command.count_darwin_arch_exes()
    )

    # `filename = *.path`
    if filename_is_specified and is_filename_with_path_suffix:
        lineno = command.args["filename"][1]
        reporter_message = (
            "The custom command is chunked and "
            f"the stanza [{command.name}] in commands.conf has field of "
            "`filename` with value ends with `.path`. "
            "Please manual check whether this path pointer files "
            "are inside of app container and use relative path. "
            f"File: {file_path}, Line: {lineno}."
        )
        reporter.manual_check(reporter_message, file_path, lineno)
    # file extension is not in v2 extensions
    elif count_v2_exes == 0:
        reporter_message = (
            "Because the custom command is chunked, "
            f"the stanza [{command.name}] in commands.conf must use a .py, "
            ".pl, .cmd, .bat, .exe, .js, .sh or no extension "
            f"script. File: {file_path}, Line: {lineno}."
        )
        reporter.fail(reporter_message, file_path, lineno)


@splunk_appinspect.tags(
    "splunk_appinspect", "custom_search_commands", "custom_search_commands_v2"
)
@splunk_appinspect.cert_version(min="1.1.7")
def check_ignored_parameters_v2_command(app, reporter):
    """Check for ignored arguments in `commands.conf` when `chunked=true`.
    [Commands.conf reference](https://docs.splunk.com/Documentation/Splunk/6.4.2/Admin/Commandsconf)
    """

    # TODO: When the version of Splunk being targeted is available check
    # chunked only on 6.3 and above.
    chunked_attributes_regex = r"(filename)|(chunked)|(is_risky)|(maxchunksize)|(maxwait)|(python\.version)|(command\.arg\.\d+)"
    rex = re.compile(chunked_attributes_regex)

    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        for command in custom_commands.get_commands():
            if command.is_v2():
                # Fail with error if a setting that is not supported is found.
                for a in command.args:
                    if rex.search(a.lower()) is None:
                        lineno = command.args[a][1]
                        reporter_message = (
                            f"The setting {a} is not supported because chunked"
                            f" is set to be true in the command : {command.name}."
                            f" File: {file_path}, Line: {lineno}."
                        )
                        reporter.fail(reporter_message, file_path, lineno)
    else:
        reporter.not_applicable("No `commands.conf` file exists.")


# TODO: When the version of Splunk being targeted is available check
# chunked only on 6.3 and above.
@splunk_appinspect.tags(
    "splunk_appinspect", "custom_search_commands", "custom_search_commands_v2"
)
@splunk_appinspect.cert_version(min="1.1.20")
def check_ignored_parameters_v1_command(app, reporter):
    """Check that the custom commands attributes `maxwait` and `maxchunksize`
    are only used when `chunked = true`.
    [Commands.conf reference](https://docs.splunk.com/Documentation/Splunk/6.4.2/Admin/Commandsconf)
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        for command in custom_commands.get_commands():
            if not command.is_v2():
                # Warn that v2 args will be ignored
                for a in command.args:
                    if a in ("maxwait", "maxchunksize"):
                        lineno = command.args[a][1]
                        reporter_message = (
                            f"The field {a} will be ignored because chunked is"
                            f" not specified in the command : {command.name}."
                            f" File: {file_path}, Line: {lineno}."
                        )
                        reporter.fail(reporter_message, file_path, lineno)
    else:
        reporter.not_applicable("No `commands.conf` file exists.")


@splunk_appinspect.tags(
    "splunk_appinspect", "custom_search_commands", "custom_search_commands_v2"
)
@splunk_appinspect.cert_version(min="1.1.7")
def check_passauth_and_enableheader(app, reporter):
    """Check that custom search commands using `passauth` have `enableheader`
    set to true.
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        for command in custom_commands.get_commands():
            if not command.is_v2():
                if (
                    command.passauth == "true"
                    and command.enableheader
                    and not command.enableheader == "true"
                ):
                    lineno = command.args["enableheader"][1]
                    reporter_message = (
                        "Because enableheader is not set to true,"
                        f" passauth will be ignored for {command.name}."
                        f" File: {file_path}, Line: {lineno}."
                    )
                    reporter.warn(reporter_message, file_path, lineno)


@splunk_appinspect.tags(
    "splunk_appinspect", "custom_search_commands", "custom_search_commands_v2"
)
@splunk_appinspect.cert_version(min="1.1.7")
def check_requires_srinfo_and_enableheader(app, reporter):
    """Check that custom search commands using `requires_srinfo` have
    `enableheader` set to true.
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        command_list = custom_commands.get_commands()

        for command in command_list:
            if not command.is_v2():
                if (
                    command.requires_srinfo == "true"
                    and command.enableheader
                    and not command.enableheader == "true"
                ):
                    lineno = command.args["enableheader"][1]
                    reporter_message = (
                        "Because enableheader is not set to true,"
                        f" requires_srinfo will be ignored for {command.name}."
                        f" File: {file_path}, Line: {lineno}."
                    )
                    reporter.warn(reporter_message, file_path, lineno)


@splunk_appinspect.tags(
    "splunk_appinspect", "custom_search_commands", "custom_search_commands_v2"
)
@splunk_appinspect.cert_version(min="1.1.7")
def check_requires_preop_and_streaming_preop(app, reporter):
    """Check that custom search commands using `requires_preop` have
    `streaming_preop` set to true.
    """
    custom_commands = app.get_custom_commands()
    if custom_commands.configuration_file_exists():
        file_path = os.path.join("default", "commands.conf")
        command_list = custom_commands.get_commands()

        for command in command_list:
            if not command.is_v2():
                if command.requires_preop == "true" and command.streaming_preop == "":
                    lineno = command.args["requires_preop"][1]
                    reporter_message = (
                        "Because requires_preop is not set to true,"
                        f" streaming_preop will be ignored for {command.name}."
                        f" File: {file_path}, Line: {lineno}."
                    )
                    reporter.warn(reporter_message, file_path, lineno)
