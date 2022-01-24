# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Cloud operations simple application check

This group serves to help validate simple applications in an effort to try and automate the validation process for cloud operations.
"""

import ast
import codecs
import logging
import os
import platform
import re
import sys

import bs4
import semver

import splunk_appinspect
from splunk_appinspect.app_util import find_readmes
from splunk_appinspect.check_routine import blacklist_conf, find_spl_command_usage
from splunk_appinspect.lookup import LookupHelper
from splunk_appinspect.regex_matcher import RegexBundle, RegexMatcher
from splunk_appinspect.splunk.splunk_default_source_type_list import (
    SPLUNK_DEFAULT_SOURCE_TYPE,
)
from splunk_appinspect.telemetry_configuration_file import TelemetryConfigurationFile

if not platform.system() == "Windows":
    import magic


logger = logging.getLogger(__name__)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.19")
def check_default_data_ui_file_white_list(app, reporter):
    """
    Check that directories under `default/data/ui` contain only allowed files
    """
    ignored_file_names = ["readme"]
    ignored_file_types = [".md", ".txt", ".old", ".bak", ".back", ".template"]
    allowed_file_types = {
        "default/data/ui/views": [".html", ".xml"],
        "default/data/ui/panels": [".html", ".xml"],
        "default/data/ui/nav": [".html", ".xml"],
        "default/data/ui/html": [".html", ".xml"],
        "default/data/ui/alerts": [".html", ".xml"],
        "default/data/ui/quickstart": [".html", ".xml"],
    }

    for basedir in allowed_file_types:
        if not app.directory_exists(basedir):
            continue

        combined_allowed_types = allowed_file_types[basedir] + ignored_file_types
        for directory, filename, ext in app.iterate_files(
            basedir=basedir,
            excluded_types=combined_allowed_types,
            excluded_bases=ignored_file_names,
        ):
            file_path = os.path.join(directory, filename)
            reporter_output = (
                f"File {file_path} is not allowed in {basedir}. Please remove it."
                " If this file is a backup or template file, please"
                " rename it with `.bak` or `.template` suffix."
            )
            reporter.fail(reporter_output, file_path)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.5.4")
def check_default_data_ui_manager_for_plain_text_credentials(app, reporter):
    """Check `default/data/ui/manager` for any files that
    use password/key/secret and other keywords.
    """
    if app.directory_exists("default", "data", "ui", "manager"):
        compiled_regex = re.compile(
            r"(pass|passwd|password|token|auth|priv|access|secret|login|community|key|privpass)\s*",
            re.IGNORECASE,
        )
        for directory, filename, ext in app.iterate_files(
            basedir="default/data/ui/manager"
        ):
            file_path = os.path.join(directory, filename)
            if ext == ".xml":
                full_filepath = app.get_filename(directory, filename)
                soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
                # element has 3 attributes: name, type, label
                # text should be the text string in element
                type_list = soup.find_all("element", {"type": re.compile("^password$")})
                attr_list = soup.find_all(
                    "element", {"name": compiled_regex}
                ) + soup.find_all("element", {"label": compiled_regex})
                if type_list:
                    reporter_output = (
                        "This app uses 'type=password'. Please check"
                        " whether the app encrypts this password in"
                        f" scripts. File: {file_path}"
                    )
                    reporter.manual_check(reporter_output, file_path)
                elif attr_list or _is_text_with_password_(soup, compiled_regex):
                    reporter_output = (
                        "This app uses password/key/secret or other"
                        " keywords. Please check whether they are"
                        " secret credentials. If yes, please make"
                        " sure the app uses 'type=password'"
                        " attribute and the 'storage/passwords'"
                        f" endpoint to encrypt it. File: {file_path}"
                    )
                    reporter.manual_check(reporter_output, file_path)
            else:
                reporter_output = (
                    "This file is in default/data/ui/manager but is not an .xml file."
                    f" Please investigate this file: {file_path}"
                )
                reporter.manual_check(reporter_output, file_path)
    else:
        reporter_output = "The `default/data/ui/manager` directory does not" " exist."
        reporter.not_applicable(reporter_output)


def _is_text_with_password_(soup, compiled_regex):
    for element in soup.find_all("element"):
        if element.find(text=compiled_regex):
            return True
    return False


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.19")
def check_lookups_white_list(app, reporter):
    """Check that `lookups/` contains only approved file types (.csv,
    .csv.default, .csv.gz, .csv.tgz, .kmz) or files formatted as valid csv."""
    allowed_file_types = [".csv", ".csv.default", ".csv.gz", ".csv.tgz", ".kmz"]
    if app.directory_exists("lookups"):
        for directory, filename, _ in app.iterate_files(basedir="lookups"):
            # if ext not in allowed_file_types:
            # Pretty messy way to determine if the allowed extension is a dotted
            # file, on account that iterate files will only return the last
            # level of the extension I.E. .csv.gz returns .gz instead of
            # .csv.gz
            does_file_name_end_with_extension = [
                allowed_file_type
                for allowed_file_type in allowed_file_types
                if filename.endswith(allowed_file_type)
            ]

            if not does_file_name_end_with_extension:
                # Validate using LookupHelper.is_valid_csv(), if not valid csv
                # then fail this lookup
                app_file_path = os.path.join(directory, filename)
                full_filepath = app.get_filename(app_file_path)
                try:
                    is_valid, rationale = LookupHelper.is_valid_csv(full_filepath)
                    if not is_valid:
                        reporter_output = (
                            "This file is not an approved file type "
                            "and is not formatted as valid csv. "
                            f"Details: {rationale} File: {app_file_path}"
                        )
                        reporter.fail(reporter_output, app_file_path)
                except Exception as err:
                    # FIXME: tests needed
                    logger.warning(
                        "Error validating lookup. File: %s Error: %s.",
                        full_filepath,
                        err,
                    )
                    reporter_output = (
                        "Error opening and validating lookup."
                        " Please investigate/remove this lookup."
                        f" File: {app_file_path}"
                    )
                    reporter.fail(reporter_output, app_file_path)
    else:
        reporter_output = "The `lookups` directory does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "splunk_appinspect", "private_app")
@splunk_appinspect.cert_version(min="1.1.19")
def check_metadata_white_list(app, reporter):
    """Check that the `metadata/` directory only contains .meta files."""
    allowed_file_types = [".meta"]
    if app.directory_exists("metadata"):
        for directory, filename, ext in app.iterate_files(basedir="metadata"):
            file_path = os.path.join(directory, filename)
            if ext not in allowed_file_types:
                reporter_output = (
                    "A file within the `metadata` directory was found"
                    " with an extension other than `.meta`."
                    f" Please remove this file: {file_path}"
                )
                reporter.fail(reporter_output, file_path)
    else:
        reporter_output = "The `metadata` directory does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.19")
def check_static_directory_file_white_list(app, reporter):
    """Check that the `static/` directory contains only known file types."""
    allowed_file_types = [
        ".css",
        ".csv",
        ".eot",
        ".gif",
        ".htm",
        ".html",
        ".ico",
        ".jpeg",
        ".jpg",
        ".kmz",
        ".less",
        ".map",
        ".md",
        ".otf",
        ".pdf",
        ".png",
        ".rst",
        ".sass",
        ".scss",
        ".svg",
        ".ttf",
        ".txt",
        ".woff",
        ".woff2",
        ".xcf",
        ".xhtml",
        ".xml",
    ]
    if app.directory_exists("static"):
        for directory, filename, ext in app.iterate_files(basedir="static"):
            file_path = os.path.join(directory, filename)
            if ext not in allowed_file_types:
                # Fail if there exists thumbs.db file
                if filename.lower() == "thumbs.db":
                    reporter_output = f"A prohibited file was found in the `static` directory. File: {file_path}"
                    reporter.fail(reporter_output, file_path)
                elif platform.system() == "Windows":
                    reporter_output = (
                        f"Please investigate this file manually. File: {file_path}"
                    )
                    reporter.manual_check(reporter_output, file_path)
                else:
                    # Inspect the file types by `file` command
                    current_file_relative_path = os.path.join(directory, filename)
                    current_file_full_path = app.get_filename(
                        current_file_relative_path
                    )
                    if current_file_relative_path in app.info_from_file:
                        file_output = app.info_from_file[current_file_relative_path]
                    else:
                        file_output = magic.from_file(current_file_full_path)
                    file_output_regex = re.compile(
                        "(.)*ASCII text(.)*|(.)*Unicode(.)*text(.)*",
                        re.DOTALL | re.IGNORECASE | re.MULTILINE,
                    )
                    # If it is not a text file, then manually check it
                    if not re.match(file_output_regex, file_output):
                        reporter_output = (
                            "This file does not appear to be a text file. Please provide a text file."
                            f"File: {file_path}"
                        )
                        reporter.manual_check(reporter_output, file_path)
    else:
        reporter_output = "The `static` directory does not exist."
        reporter.not_applicable(reporter_output)


# ------------------------------------------------------------------------------
# Grey List Checks Go Here
# ------------------------------------------------------------------------------
# -------------------
# authorize.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.20")
def check_authorize_conf_admin_all_objects_privileges(app, reporter):
    """Check that authorize.conf does not grant excessive administrative
    permissions to the user.
    """
    config_file_paths = app.get_config_file_paths("authorize.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            authorize_conf_file = app.authorize_conf(dir=directory)
            properties_to_validate = [
                "admin_all_objects",
                "change_authentication",
                "importRoles",
            ]
            import_roles_to_prevent = {"admin", "sc_admin", "splunk-system-role"}
            for section in authorize_conf_file.sections():
                # Ignore capability stanzas
                if section.name.startswith("capability::"):
                    continue
                for property_to_validate in properties_to_validate:
                    if not section.has_option(property_to_validate):
                        continue
                    option = section.get_option(property_to_validate)
                    lineno = option.lineno
                    value = option.value
                    if property_to_validate == "importRoles":
                        # Check importRoles for inheriting of blacklisted roles
                        # using set intersection of importRoles & blacklisted roles
                        bad_roles = set(value.split(";")) & import_roles_to_prevent
                        for bad_role in bad_roles:
                            reporter_output = (
                                f"{file_path} [{section.name}] attempts to"
                                f" inherit from the `{bad_role}` role. File: "
                                f"{file_path}, Line: {lineno}."
                            )
                            reporter.fail(reporter_output, file_path, lineno)
                    elif value == "enabled":
                        reporter_output = (
                            f"{file_path} [{section.name}] contains `{property_to_validate} ="
                            f" enabled`. File: {file_path}, Line: {lineno}."
                        )
                        reporter.fail(reporter_output, file_path, lineno)
    else:
        reporter_output = "authorize.conf does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_authorize_conf_for_tokens_auth(app, reporter):
    """Check that authorize.conf does not contain a `tokens_auth` stanza"""
    config_file_paths = app.get_config_file_paths("authorize.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            authorize_conf_file = app.authorize_conf(dir=directory)
            for section in authorize_conf_file.sections():
                if section.name == "tokens_auth":
                    reporter_output = (
                        f"The {directory}/authorize.conf specifies [tokens_auth] stanza, "
                        "which is not allowed in Splunk Cloud. Please remove "
                        f"this stanza. File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "authorize.conf does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.20")
def check_alert_actions_conf_for_alert_execute_cmd_properties(app, reporter):
    """Check that commands referenced in the `alert.execute.cmd` property of all
    alert actions are checked for compliance with Splunk Cloud security policy.
    """
    if app.file_exists("default", "alert_actions.conf"):
        filename = os.path.join("default", "alert_actions.conf")
        alert_actions = app.get_alert_actions()
        for alert_action in alert_actions.get_alert_actions():
            if alert_action.alert_execute_cmd_specified():
                lineno = alert_action.args["alert.execute.cmd"][1]
                if alert_action.alert_execute_cmd.endswith(".path"):
                    reporter_output = (
                        f"Alert action [{alert_action.name}] has an alert.execute.cmd"
                        f" specified with command: `{alert_action.alert_execute_cmd}`."
                        " Splunk Cloud prohibits path pointer files because they can be directly"
                        " used to target executables outside the directory of the app."
                        f" File: {filename}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, filename, lineno)
                else:
                    reporter_output = (
                        f"Alert action [{alert_action.name}] has an alert.execute.cmd"
                        f" specified. Please check this command: `{alert_action.alert_execute_cmd}`."
                    )
                    reporter.manual_check(reporter_output)
    else:
        reporter_output = "alert_actions.conf does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# commands.conf
# -------------------
@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.6.1")
def check_command_scripts_exist_for_cloud(app, reporter):
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
                reporter.warn(reporter_message, file_path, lineno)

            # v2 command
            elif command.is_v2():
                _check_v2_command(command, app, reporter, is_filename_with_path_suffix)

            # v1 command
            else:
                _check_v1_command(command, reporter)
    else:
        reporter.not_applicable("No `commands.conf` file exists.")


def _check_v1_command(command, reporter):
    file_path = os.path.join("default", "commands.conf")
    lineno = command.lineno
    count_v1_exes = command.count_v1_exes()

    # file extension is not in v1 extension list
    if count_v1_exes == 0 and _is_python_script(command.file_name_exe.file_path):
        reporter_message = (
            "Custom Search Command Protocol v1 only support .py or .pl script, but the "
            f"stanza [{command.name}] in commands.conf doesn't use a .py or .pl script. "
            f"Please correct script extension: `{command.file_name_exe.file_name}`. "
            f"File: {file_path}, Line: {lineno}."
        )
        reporter.warn(reporter_message, file_path, lineno)


def _check_v2_command(command, app, reporter, is_filename_with_path_suffix):
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

    # For the v2 command, the Splunk software attempts to run no extension
    # or unrecognized executable directly, without an interpreter. On UNIX-based
    # platforms, this means that the executable must have the executable bit set.
    # https://docs.splunk.com/Documentation/Splunk/7.0.0/Search/Customcommandlocation
    excluded_extensions = [".py", ".pl", ".js"]
    directly_executing_scripts = [
        script
        for script in command.executable_files
        if script.ext not in excluded_extensions
        and (
            platform.system() == "Windows"
            or app.is_executable(script.file_path, is_full_path=True)
        )
    ]
    # `filename = *.path`
    if filename_is_specified and is_filename_with_path_suffix:
        lineno = command.args["filename"][1]
        reporter_message = (
            "The custom command is chunked and "
            f"the stanza [{command.name}] in commands.conf has "
            "field of `filename` with value ends with `.path`. "
            "Please manual check whether this path pointer files "
            "are inside of app container and use relative path. "
            f"File: {file_path}, Line: {lineno}."
        )
        reporter.manual_check(reporter_message, file_path, lineno)

    elif directly_executing_scripts:
        reporter_message = (
            f"The custom command [{command.name}] doesn't use a .py, .pl, .js "
            "script, which can be executed by Splunk directly "
            "without an interpreter. Please manual check the "
            f"script `{command.file_name_exe.file_name}`. "
            f"File: {file_path}, Line: {lineno}."
        )
        reporter.manual_check(reporter_message, file_path, lineno)

    # file extension is not in v2 extension list
    elif count_v2_exes == 0:
        reporter_message = (
            "Because the custom command is chunked, the "
            f"stanza [{command.name}] in commands.conf must "
            "use a .py, .pl, .cmd, .bat, .exe, .js, .sh or no "
            f"extension script. File: {file_path}, Line: {lineno}."
        )
        reporter.warn(reporter_message, file_path, lineno)


def _is_python_script(file_path):
    with open(file_path, "rb") as f:
        code = f.read()

    try:
        ast.parse(code)
    except Exception:
        return False

    return len(code) != 0


# -------------------
# distsearch.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_distsearch_conf_for_concerning_replicated_file_size(app, reporter):
    """Check if concerningReplicatedFileSize in distsearch.conf is larger
    than 50 MB.
    """
    path = os.path.join("default", "distsearch.conf")
    if app.file_exists(path):
        distsearch_conf_file = app.distsearch_conf()
        option_exist = distsearch_conf_file.has_option(
            "replicationSettings", "concerningReplicatedFileSize"
        )
        concerningReplicatedFileSize = (
            distsearch_conf_file.get(
                "replicationSettings", "concerningReplicatedFileSize"
            )
            if option_exist
            else 500
        )
        if option_exist and int(concerningReplicatedFileSize) <= 50:
            pass
        else:
            reporter_output = (
                "The app contains default/distsearch.conf and"
                " the value of concerningReplicatedFileSize,"
                f" {concerningReplicatedFileSize} MB, is larger than"
                " 50 MB. The best practice is files which are >50MB should not"
                " be pushed to search peers via bundle replication."
                " By the way, concerningReplicatedFileSize defaults to 500 MB"
                " so it will be warned in default as long as distsearch.conf exists."
            )
            reporter.warn(reporter_output, path)
    else:
        reporter_output = "distsearch.conf does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# indexes.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.20")
def check_indexes_conf_only_uses_splunk_db_variable(app, reporter):
    """Check that indexes defined in `indexes.conf` use relative paths starting
    with $SPLUNK_DB.
    """
    properties_to_validate = [
        "bloomHomePath",
        "coldPath",
        "homePath",
        "summaryHomePath",
        "thawedPath",
        "tstatsHomePath",
    ]
    path_pattern_string = r"^\$SPLUNK_DB"

    config_file_paths = app.get_config_file_paths("indexes.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            indexes_conf_file = app.indexes_conf(directory)

            not_using_splunk_db_matches = [
                (section.name, property_key, property_lineno)
                for section in indexes_conf_file.sections()
                for property_key, property_value, property_lineno in section.items()
                if (
                    property_key in properties_to_validate
                    and re.search(path_pattern_string, property_value) is None
                )
            ]

            for (
                stanza_name,
                property_matched,
                property_lineno,
            ) in not_using_splunk_db_matches:
                reporter_output = (
                    f"The stanza [{stanza_name}] has the property {property_matched} and is"
                    " using a path that does not contain $SPLUNK_DB."
                    " Please use a path that contains $SPLUNK_DB."
                    f" File: {file_path}, Line: {property_lineno}."
                )
                reporter.fail(reporter_output, file_path, property_lineno)

    else:
        reporter_output = "indexes.conf does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.20")
def check_for_index_volume_usage(app, reporter):
    """Check that `indexes.conf` does not declare volumes."""
    path_pattern_string = "^volume:"

    config_file_paths = app.get_config_file_paths("indexes.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            indexes_conf_file = app.indexes_conf(directory)

            volume_stanza_names = [
                (section.name, section.lineno)
                for section in indexes_conf_file.sections()
                if re.search(path_pattern_string, section.name)
            ]
            for stanza_name, stanza_lineno in volume_stanza_names:
                reporter_output = (
                    f"The stanza [{stanza_name}] was declared as volume. "
                    f"File: {file_path}, Line: {stanza_lineno}."
                )
                reporter.fail(reporter_output, file_path, stanza_lineno)

    else:
        reporter_output = "indexes.conf does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# inputs.conf
# -------------------
@splunk_appinspect.tags("cloud", "inputs_conf", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_for_inputs_fifo_usage(app, reporter):
    """Check the `[fifo]` stanza in `inputs.conf` is not pointing to a path
    within a cloud replicated scope defined by `distsearch.conf`. `[fifo]` usually
    points to a file whose size may inflate. This kind of files MUST NOT be replicated across cloud
    environments since they will significantly consume network bandwidth."""
    # This check is too tedious to read.
    # Please refer to https://jira.splunk.com/browse/ACD-3408 for the logic behind this check.
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_configuration_file = app.inputs_conf(directory)
            fifo_stanzas = [
                stanza
                for stanza in inputs_configuration_file.sections()
                if re.search(r"^fifo:\/\/", stanza.name)
            ]
            for stanza in fifo_stanzas:
                reporter_output = (
                    f"{directory}/inputs.conf contains a [fifo://]"
                    " stanza that is not allowed in Cloud environment."
                    f" Please remove this stanza: [{stanza.name}]."
                )
                reporter.fail(reporter_output, file_path, stanza.lineno)
    else:
        reporter.not_applicable("The default/inputs.conf does not exist.")


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_tcp(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not contain a `tcp` stanza."""
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name.startswith("tcp://"):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies `tcp`,"
                        " which is prohibited in Splunk Cloud. An alternative"
                        f" is to use `tcp-ssl`. Stanza [{section.name}]."
                        f" File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_splunk_tcp(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not contain a `splunktcp`
    stanza.
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if re.search("^splunktcp(?!-ssl)", section.name):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies"
                        " `splunktcp`, which is prohibited in Splunk"
                        " Cloud. An alternative is to use"
                        f" `splunktcp-ssl`. Stanza: [{section.name}]."
                        f" File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_fschange(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not contain a `fschange`
    stanza.
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name.startswith("fschange"):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies `fschange`"
                        " , which is prohibited in Splunk Cloud. "
                        f"Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "inputs_conf", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_http_global_usage(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not contain a `[http]`
    stanza.
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name == "http":
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies a"
                        " global `[http]` stanza. This is prohibited"
                        " in Splunk Cloud instances. Please change"
                        " this functionality to target local"
                        " settings by using [http://name] instead."
                        f" Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "inputs_conf", "private_app")
@splunk_appinspect.cert_version(min="2.2.0")
def check_inputs_conf_for_http_local_stanza_usage(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` contains accurate `[http://name]`
    stanza if it exists.
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if (
                    section.name.startswith("http://")
                    and re.search(r"^http:\/\/.+", section.name) is None
                ):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies a"
                        " local `[http://]` stanza. This setting should"
                        " specify the name, using [http://name] instead."
                        f" Stanza: [{section.name}]. File: {file_path},"
                        f" Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_splunktcptoken(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not contain a `splunktcptoken`
    stanza.
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name.startswith("splunktcptoken"):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies"
                        " `splunktcptoken`, which is prohibited in"
                        f" Splunk Cloud. Stanza: [{section.name}]."
                        f" File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.1")
def check_inputs_conf_for_batch(app, reporter):
    """Check that batch input accesses files in a permitted way.

    To be permissible, the batch input must meet the following criteria:
        1) The file path needs to match a file in the directory "$SPLUNK_HOME/var/spool/splunk/"
        2) The file name needs to be application specific "$SPLUNK_HOME/etc/apps/<my_app>"
        3) The file name should not end with "stash" or "stash_new"
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            batch_input_regex_string = r"^batch[:][\/][\/][$]SPLUNK_HOME[/\\]var[/\\]spool[/\\]splunk[/\\][.][.][.]stash(?!_new).+$"
            batch_input_regex_string_for_app_dir = (
                r"^batch[:][\/][\/][$]SPLUNK_HOME[/\\]etc[/\\]apps[/\\]"
                + re.escape(app.name)
                + r"[/\\].*$"
            )
            batch_input_regex = re.compile(batch_input_regex_string)
            batch_input_regex_for_app_dir = re.compile(
                batch_input_regex_string_for_app_dir
            )
            for section in inputs_conf.sections():
                if section.name.startswith("batch://"):
                    match = batch_input_regex.match(section.name)
                    match_for_app_dir = batch_input_regex_for_app_dir.match(
                        section.name
                    )
                    if not match and not match_for_app_dir:
                        reporter_output = (
                            "The batch input is prohibited in Splunk Cloud"
                            " because it is destructive unless used for"
                            " event spooling using application-specific"
                            ' stash files (e.g.,"batch://$SPLUNK_HOME/'
                            'var/spool/splunk/...stash_APP_SPECIFIC_WORD" or'
                            " batch://$SPLUNK_HOME/etc/apps/<my_app>)."
                            f" Stanza: [{section.name}]. File: {file_path}, "
                            f"Line: {section.lineno}."
                        )
                        reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "splunk_appinspect", "private_app")
@splunk_appinspect.cert_version(min="2.2.0")
def check_inputs_conf_batch_has_required_attributes(app, reporter):
    """Check that batch input has required attributes.
    The following key/value pairs are required for batch inputs:
    move_policy = sinkhole
    """
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if not config_file_paths:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)
        return

    for directory, filename in iter(config_file_paths.items()):
        file_path = os.path.join(directory, filename)
        inputs_conf = app.inputs_conf(directory)
        for section in inputs_conf.sections():
            if section.name.startswith("batch") and (
                not section.has_option("move_policy")
                or section.get_option("move_policy").value != "sinkhole"
            ):
                reporter_output = (
                    "The `move_policy = sinkhole` key value pair is missing in"
                    f" stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                    " You must include this pair when you define batch inputs."
                )
                reporter.fail(reporter_output, file_path, section.lineno)


@splunk_appinspect.tags("cloud", "splunk_appinspect", "private_app")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_udp(app, reporter):
    """Check that inputs.conf does not have any UDP inputs."""
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name.startswith("udp"):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies `udp`,"
                        " which is prohibited in Splunk Cloud."
                        f" Stanza: [{section.name}]. File: {file_path},"
                        f" Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_inputs_conf_for_ssl(app, reporter):
    """Check that inputs.conf does not have any SSL inputs."""
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name == "SSL":
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies "
                        " `SSL`, which is prohibited in Splunk Cloud."
                        f" Stanza: [{section.name}]. File: {file_path},"
                        f" Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_inputs_conf_for_remote_queue_monitor(app, reporter):
    """Check that inputs.conf does not have any remote_queue inputs."""
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                if section.name.startswith("remote_queue:"):
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies `remote_queue`,"
                        " which is prohibited in Splunk Cloud."
                        f" Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.6.1")
def check_scripted_inputs_cmd_path_pattern(app, reporter):
    """Check the cmd path pattern of scripted input defined in inputs.conf."""
    scripted_inputs_cmd_path_pattern = "script://(.*)$"
    absolute_path = [r"\$SPLUNK_HOME", "etc", "apps", app.name, "bin", ""]
    absolute_path_1 = "/".join(absolute_path)
    absolute_path_2 = "(\\\\|\\\\\\\\)".join(absolute_path)
    absolute_path_pattern = f"^({absolute_path_1}|{absolute_path_2})"
    relative_path_pattern = r"^\.(/bin/|(\\|\\\\)bin(\\|\\\\))"
    with_path_suffix_pattern = r".*\.path$"

    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                # find cmd path of [script://xxx] stanzas in inputs.conf
                path = re.findall(scripted_inputs_cmd_path_pattern, section.name)
                manual_check_report = (
                    f"The `{directory}/inputs.conf` specifies a `script` input stanza."
                    " The cmd path of scripted input ends with `.path`."
                    " Please manual check whether this path pointer files"
                    " are inside of app container and use relative path."
                    f" Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                )
                warn_report_output = (
                    f"The `{directory}/inputs.conf` specifies a `script` input stanza."
                    " The best pattern of cmd path of scripted input is"
                    " $SPLUNK_HOME/etc/apps/AppName/bin/."
                    f" Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                )
                fail_report_output = (
                    f"The `{directory}/inputs.conf` specifies a `script` input stanza."
                    " This cmd path of scripted input is prohibited in Splunk Cloud."
                    f" Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                )
                if path:
                    path = path[0]
                    if re.match(absolute_path_pattern, path):
                        if re.match(with_path_suffix_pattern, path):
                            reporter.manual_check(
                                manual_check_report, file_path, section.lineno
                            )
                    elif re.match(relative_path_pattern, path):
                        if re.match(with_path_suffix_pattern, path):
                            reporter.manual_check(
                                manual_check_report, file_path, section.lineno
                            )
                        else:
                            reporter.warn(warn_report_output, file_path, section.lineno)
                    else:
                        reporter.fail(fail_report_output, file_path, section.lineno)
                else:
                    reporter_output = (
                        "The scripted input does not exist in inputs.conf."
                    )
                    reporter.not_applicable(reporter_output)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.1.0")
def check_scripted_inputs_python_version(app, reporter):
    """Check that python version is python3 for scripted inputs defined in inputs.conf."""
    scripted_inputs_cmd_path_pattern = "script://(.*)$"

    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            for section in inputs_conf.sections():
                # find cmd path of [script://xxx] stanzas in inputs.conf
                path = re.findall(scripted_inputs_cmd_path_pattern, section.name)
                if path:
                    path = path[0]
                    if path.endswith(".py"):
                        if (
                            not section.options.get("python.version")
                            or section.options.get("python.version").value != "python3"
                        ):
                            fail_report_output = (
                                "The input stanza needs python.version flag set to python3 "
                                f"Stanza: [{section.name}]. File: {file_path}, Line: {section.lineno}."
                            )
                            reporter.fail(fail_report_output, file_path, section.lineno)
    else:
        reporter_output = "`default/inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_modular_inputs_scripts_exist_for_cloud(app, reporter):
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

                reporter_output = (
                    "No executable exists for the modular input "
                    f"'{mi.name}'. File: {file_path}, Line: {mi.lineno}."
                )
                reporter.warn(reporter_output, file_path, mi.lineno)
        else:
            reporter_output = "No modular inputs were detected."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = f"No `{modular_inputs.specification_filename}` was detected."
        reporter.not_applicable(reporter_output)


# -------------------
# setup.xml
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.1.0")
def check_setup_xml_in_default(app, reporter):
    """Check that `setup.xml` does not exist in the app default folder"""
    if app.file_exists("default", "setup.xml"):
        reporter_output = (
            "Do not use `default/setup.xml` in the Cloud environment "
            "since it behaves incorrectly on distributed Splunk Cloud deployments. "
            "Consider leveraging HTML and JS and using setup view instead. "
            "For example: https://dev.splunk.com/enterprise/docs/developapps/manageknowledge/setuppage/"
        )
        reporter.fail(reporter_output)


# -------------------
# transforms.conf
# -------------------
@splunk_appinspect.tags("cloud", "manual", "python_version")
@splunk_appinspect.cert_version(min="1.1.20")
def check_transforms_conf_for_external_cmd(app, reporter, target_splunk_version):
    """Check that `transforms.conf` does not contain any transforms with malicious
    command scripts specified by `external_cmd=<string>` attribute, or does not contain
    a scripted lookup with python2 only script.
    """
    config_file_paths = app.get_config_file_paths("transforms.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            transforms_conf = app.transforms_conf(directory)
            external_command_stanzas = [
                section
                for section in transforms_conf.sections()
                if section.has_option("external_cmd")
            ]
            application_files = []
            if external_command_stanzas:
                application_files = list(app.iterate_files(types=[".py"]))
            for external_command_stanza in external_command_stanzas:
                # find `external_cmd` in the sections of transforms.conf
                external_command = external_command_stanza.get_option(
                    "external_cmd"
                ).value
                external_command_lineno = external_command_stanza.get_option(
                    "external_cmd"
                ).lineno
                external_command_regex_string = r"^[^\s]+\.py(?=\s)"
                external_command_regex = re.compile(external_command_regex_string)
                script_filename_matches = external_command_regex.search(
                    external_command
                )
                if script_filename_matches:
                    # if the script type is python
                    script_filename = script_filename_matches.group(0)
                    # find the python file based on the script name
                    if target_splunk_version >= "splunk_8_0" and (
                        not external_command_stanza.has_option("python.version")
                        or external_command_stanza.get_option(
                            "python.version"
                        ).value.lower()
                        != "python3"
                    ):
                        reporter_output = (
                            f" The `transforms.conf` stanza [{external_command_stanza.name}]"
                            " is using python script as external command."
                            " but not specifying `python.version=python3`."
                            " Please specify `python.version=python3.`"
                        )
                        reporter.fail(reporter_output, file_path)
                        continue
                    script_matches = [
                        file for file in application_files if file[1] == script_filename
                    ]
                    if not script_matches:
                        reporter_output = (
                            f" The `transforms.conf` stanza [{external_command_stanza.name}] is using the"
                            f" `external_cmd` property, but the {script_filename} file can't be found in the app."
                            f" File: {file_path}, Line: {external_command_lineno}."
                        )
                        reporter.fail(
                            reporter_output, file_path, external_command_lineno
                        )
                    elif target_splunk_version >= "splunk_8_0" and sys.version_info >= (
                        3,
                    ):
                        rela_py_file_path = os.path.join(
                            script_matches[0][0], script_matches[0][1]
                        )
                        fd = open(os.path.join(app.app_dir, rela_py_file_path))
                        try:
                            ast.parse(fd.read())
                        except Exception:
                            reporter.fail(
                                f"Scripted lookup {external_command_stanza.name} "
                                "specifies a script that is not Python 3 compatible, "
                                "Please upgrade your Python script to be Python 3 "
                                "compatible.",
                                rela_py_file_path,
                            )
                else:
                    # manual check other `external_type`, such as executable
                    reporter_output = (
                        f"The `transforms.conf` stanza [{external_command_stanza.name}] is"
                        " using the `external_cmd` property."
                        f" Please investigate. Command: {external_command}. "
                        f"File: {file_path}, Line: {external_command_lineno}."
                    )
                    reporter.manual_check(
                        reporter_output, file_path, external_command_lineno
                    )
    else:
        reporter_output = "`default/transforms.conf` does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# audit.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_audit_conf_black_list(app, reporter):
    """Check that app does not contain audit.conf, as it is prohibited in
    Splunk Cloud due to its ability to configure/disable cryptographic signing
    and certificates.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "audit.conf",
        "Splunk Cloud does not permit apps to control whether to perform"
        " cryptographic signing of events in _audit nor which certificates"
        " to use to that end.",
    )


# -------------------
# authentication.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.0")
def check_stanza_of_authentication_conf(app, reporter):
    """Check that only role-mapping stanza is allowed in authenticaiton.conf as long as it doesn't map users to a cloud-internal role."""
    if app.file_exists("default", "authentication.conf"):
        authentication_conf = app.authentication_conf()
        # Maps a Splunk role (from authorize.conf) to LDAP groups, SAML groups or groups passed in headers from proxy server
        # [roleMap_<authSettings-key>], [roleMap_<saml-authSettings-key>], [roleMap_proxySSO],
        # <Splunk RoleName> = <Group String>
        # Maps a SAML user to Splunk role(from authorize.conf), Realname and Email
        # [userToRoleMap_<saml-authSettings-key>]
        # <SAML User> = <Splunk RoleName>::<Realname>::<Email>
        # Maps a ProxySSO user to Splunk role (from authorize.conf)
        # [userToRoleMap_proxySSO]
        # <ProxySSO User> = <Splunk RoleName>
        allowed_stanzas = ["roleMap_", "userToRoleMap_"]
        stanza_list = app.authentication_conf().section_names()
        file_name = "default/authentication.conf"
        for stanza in stanza_list:
            for allowed_stanza in allowed_stanzas:
                if stanza.startswith(allowed_stanza):
                    reporter_output = "Splunk admin role is prohibited from configuring in role-mapping."
                    if stanza.startswith("roleMap_"):
                        # check if option-key equal to 'admin'
                        if authentication_conf.get_section(stanza).has_option("admin"):
                            line_number = (
                                authentication_conf.get_section(stanza)
                                .get_option("admin")
                                .lineno
                            )
                            reporter.fail(reporter_output, file_name, line_number)
                    else:
                        # check if option-value equal to 'admin' or startswith 'admin::'
                        for _, option_v in authentication_conf.get_section(
                            stanza
                        ).options.items():
                            if option_v.value == "admin" or option_v.value.startswith(
                                "admin::"
                            ):
                                line_number = option_v.lineno
                                reporter.fail(reporter_output, file_name, line_number)
                    break
            else:
                reporter_output = (
                    "Only role-mapping stanza is allowed in "
                    f"authentication.conf, but [{stanza}] is found."
                )
                line_number = authentication_conf.get_section(stanza).lineno
                reporter.fail(reporter_output, file_name, line_number)

    else:
        reporter_output = "`default/authentication.conf` does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# bookmarks.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_bookmarks_conf_black_list(app, reporter):
    """Check that app does not contain bookmarks.conf as this
    feature is not available in Splunk Cloud.
    """
    blacklist_conf(
        app,
        reporter.warn,
        "bookmarks.conf",
        "bookmarks feature is not available in Splunk Cloud.",
    )


# -------------------
# crawl.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_introspection_of_cloud_filesystem(app, reporter):
    """Check that app does not contain crawl.conf
    as it allows Splunk to introspect the filesystem which is not
    permitted in Splunk Cloud.
    """
    # This check is redundant with deprecated features in Splunk 6.0, however
    # Cloud Ops permits deprecated features that aren't harmful, so this check
    # is necessary to prevent usage in Cloud.
    blacklist_conf(
        app,
        reporter.fail,
        "crawl.conf",
        "crawl.conf allows Splunk to introspect the file system. Please do not use it.",
    )


# -------------------
# datatypesbnf.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_datatypesbnf_conf_black_list(app, reporter):
    """Check that app does not contain datatypesbnf.conf, as it is prohibited
    in Splunk Cloud.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "datatypesbnf.conf",
        "datatypesbnf.conf is not permitted for Splunk Cloud pending further"
        " evaluation.",
    )


# -------------------
# default-mode.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_default_mode_conf_black_list(app, reporter):
    """Check that app does not contain default-mode.conf is as it is
    prohibited in Splunk Cloud due to the fact that Splunk Light Forwarders and
    Splunk Universal Forwarders are not run in Splunk Cloud.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "default-mode.conf",
        "default-mode.conf describes the alternate setups used by the Splunk"
        " Light Forwarder and Splunk Universal Forwarder, which are not run in"
        " Splunk Cloud.",
    )


# -------------------
# deployment.conf
# -------------------
@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_5_0", "removed_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.5.0")
def check_deployment_conf_black_list(app, reporter):
    """Check that app does not contain deployment.conf. Apps should leave
    deployment configuration up to Splunk administrators.

    Also, deployment.conf has been removed and replaced by:
      1) deploymentclient.conf - for configuring Deployment Clients
      2) serverclass.conf - for Deployment Server server class configuration.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "deployment.conf",
        "deployment.conf has been removed and replaced by 1)"
        " deploymentclient.conf - for configuring Deployment Clients and 2)"
        " serverclass.conf - for Deployment Server server class configuration."
        " Note that both deploymentclient.conf and serverclass.conf are"
        " prohibited for Splunk Cloud and App Certification, however.",
    )


# -------------------
# deploymentclient.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_deploymentclient_conf_black_list(app, reporter):
    """Check that app does not contain deploymentclient.conf as it configures
    the deployment server client. Apps should leave deployment configuration up
    to Splunk administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "deploymentclient.conf",
        "deploymentclient.conf configures the client of the deployment server,"
        " which is not permitted.",
    )


# -------------------
# health.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_health_conf_black_list(app, reporter):
    """Check that app does not contain health.conf as sc_admin is not able
    to see or configure health report in Cloud.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "health.conf",
        "Currently sc_admin is not able to see or configure the "
        "health report in Cloud.",
    )


# -------------------
# instance.cfg.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_instance_cfg_conf_black_list(app, reporter):
    """Check that app does not contain instance.cfg.conf. Apps should not
    configure server/instance specific settings.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "instance.cfg.conf",
        "instance.cfg.conf configures server/instance specific settings to set"
        " a GUID per server. Apps leave configuration up to Splunk administrators"
        " and should not configure these settings.",
    )


# -------------------
# literals.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_literals_conf_black_list(app, reporter):
    """Check that app does not contain literals.conf. Apps should not
    alter/override text strings displayed in Splunk Web.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "literals.conf",
        "literals.conf allows overriding of text, such as search error"
        " strings, displayed in Splunk Web. Apps should not alter these"
        " strings as Splunk users/administrators may rely on them.",
    )


# -------------------
# messages.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_messages_conf_black_list(app, reporter):
    """Check that app does not contain messages.conf. Apps should not
    alter/override messages/externalized strings.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "messages.conf",
        "messages.conf allows overriding of messages/externalized strings. "
        "Apps should not alter these as Splunk users/administrators may rely "
        "on them.",
    )


# -------------------
# passwords.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_that_passwords_conf_not_exist(app, reporter):
    """Check that the app does not have default/passwords.conf, otherwise, warn it."""
    path = os.path.join("default", "passwords.conf")
    if app.file_exists(path):
        reporter_output = "There exists a default/passwords.conf which won't work at the app, please remove it."
        reporter.warn(reporter_output, path)
    else:
        reporter_output = "passwords.conf does not exist."
        reporter.not_applicable(reporter_output)


# -------------------
# props.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_that_no_configurations_of_default_source_type_in_props_conf(app, reporter):
    """Check that the app does not contain configurations of default source type in props.conf,
    which will overwrite the configurations of default source types in system/default/props.conf
    then it will affect other apps in splunk enterprise/cloud.
    """
    # Now this list is for Splunk 7.2.0 and 8.0.0,
    # it needs to be updated while Splunk Version updates
    # Notice: remove [default] stanza here because there exist another check to fail it,
    # to avoid confusing user appearance of warning and failure at the same time
    list_of_default_source_type = SPLUNK_DEFAULT_SOURCE_TYPE
    try:
        config_file_paths = app.get_config_file_paths("props.conf")
        if config_file_paths:
            for directory, filename in iter(config_file_paths.items()):
                file_path = os.path.join(directory, filename)
                props_config = app.props_conf(directory)
                section_names = props_config.section_names()
                for section_name in section_names:
                    if section_name in list_of_default_source_type:
                        reporter_output = (
                            f"In {file_path}, stanza {section_name} has been configured, which"
                            " will overwrite its default configuration in system/default/props.conf"
                            " then it will affect other apps in splunk enterprise/cloud."
                        )
                        reporter.warn(reporter_output, file_path)
        else:
            reporter_output = "No props.conf file exists."
            reporter.not_applicable(reporter_output)
    except Exception as error:
        logger.error("unexpected error occurred: %s", str(error))
        raise


# -------------------
# pubsub.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_pubsub_conf_black_list(app, reporter):
    """Check that app does not contain pubsub.conf as it defines a custom
    client for the deployment server. Apps should leave deployment
    configuration up to Splunk administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "pubsub.conf",
        "pubsub.conf defines a custom client for the deployment server, "
        "this is not permitted.",
    )


# -------------------
# segmenters.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_segmenters_conf_black_list(app, reporter):
    """Check that app does not contain segmenters.conf with splunk stanza. A misconfigured
    segmenters.conf can result in unsearchable data that could only be
    addressed by re-indexing and segmenters.conf configuration is system-wide.
    """
    conf_filename = "segmenters.conf"
    section_names = [
        "default",
        "full",
        "indexing",
        "search",
        "standard",
        "inner",
        "outer",
        "none",
        "whitespace-only",
        "meta-tokenizer",
    ]
    if app.file_exists("default", conf_filename):
        file_path = os.path.join("default", conf_filename)
        conf = app.get_config(conf_filename)
        for section_name in section_names:
            if (
                conf.has_section(section_name)
                and len(conf.get_section(section_name).items()) > 0
            ):
                lineno = conf.get_section(section_name).lineno
                reporter_output = (
                    f"{section_name} stanza was found in {file_path}. "
                    "Please remove any [default], [full], [indexing], [search], [standard], [inner], [outer], [none], "
                    "[whitespace-only], [meta-tokenizer]  stanzas or properties "
                    "outside of a stanza (treated as default/global) "
                    "from conf files defined by Splunk."
                    f"File: {file_path}, Line: {lineno}."
                )
                reporter.fail(reporter_output, file_path, lineno)
                break


# -------------------
# serverclass.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_serverclass_conf_black_list(app, reporter):
    """Check that app does not contain serverclass.conf as it defines
    deployment server classes for use with deployment server. Apps should
    leave deployment configuration up to Splunk administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "serverclass.conf",
        "serverclass.conf configures server classes for use with a deployment "
        "server and is not permitted.",
    )


# -------------------
# serverclass.seed.xml.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_serverclass_seed_xml_conf_black_list(app, reporter):
    """Check that app does not contain serverclass.seed.xml.conf as it
    configures deploymentClient to seed a Splunk installation with applications
    at startup time. Apps should leave deployment configuration up to Splunk
    administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "serverclass.seed.xml.conf",
        "serverclass.seed.xml.conf configures deploymentClient to seed a "
        "Splunk installation with applications at startup time, which is not "
        "permitted.",
    )


# -------------------
# source-classifier.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_source_classifier_conf_black_list(app, reporter):
    """Check that app does not contain source-classifier.conf.conf as it
    configures system-wide settings for ignoring terms (such as sensitive
    data).
    """
    blacklist_conf(
        app,
        reporter.fail,
        "source-classifier.conf",
        "source-classifier.conf configures system-wide terms to ignore when"
        " generating a sourcetype model, which is not permitted.",
    )


# -------------------
# sourcetypes.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_sourcetypes_conf_black_list(app, reporter):
    """Check that app does not contain sourcetypes.conf as it is a
    machine-generated file that stores source type learning rules. props.conf
    should be used to define sourcetypes.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "sourcetypes.conf",
        "sourcetypes.conf stores source type learning rules, which is not "
        "permitted.",
    )


# -------------------
# splunk-launch.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_splunk_launch_conf_black_list(app, reporter):
    """Check that app does not contain splunk-launch.conf as it defines
    environment values used at startup time. System-wide environment variables
    should be left up to Splunk administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "splunk-launch.conf",
        "splunk-launch.conf configures environment values used at startup "
        "time, which is not permitted.",
    )


# -------------------
# telemetry.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "telemetry", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_telemetry_conf_black_list(app, reporter):
    """Check that app does not contain telemetry.conf as it controls a
    Splunk-internal feature that should not be configured by apps.
    """
    telemetry_config = TelemetryConfigurationFile()
    if not telemetry_config.check_whitelist(app):
        blacklist_conf(
            app,
            reporter.fail,
            "telemetry.conf",
            "telemetry.conf configures Splunk-internal settings, which is not "
            "permitted.",
        )
    else:
        # This app is whitelisted for telemetry check. Pass it.
        pass


# -------------------
# user-seed.conf
# -------------------
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_user_seed_conf_black_list(app, reporter):
    """Check that app does not contain user-seed.conf as it is used to
    preconfigure default login and password information.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "user-seed.conf",
        "user-seed.conf configures default login and password information, which "
        "is not permitted.",
    )


# -------------------
# wmi.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_wmi_conf_black_list(app, reporter):
    """Check that app does not contain wmi.conf is as it is prohibited in
    Splunk Cloud due to its ability to configure Splunk to ingest data via
    Windows Management Instrumentation, which should be done via forwarder.
    Forwarders are not permitted in Splunk Cloud.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "wmi.conf",
        "wmi.conf configures Splunk to ingest data via Windows Management "
        "Instrumentation, which is not permitted in Splunk Cloud.",
    )


# -------------------
# workload_pools.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_workload_pools_conf_black_list(app, reporter):
    """Check that app does not contain workload_pools.conf in Cloud. App should
    not modify workload categories/pools. It should be only controlled by cloud
    administrators.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "workload_pools.conf",
        "workload_pools.conf configures workload categories/pools, which "
        "is not permitted in Splunk Cloud.",
    )


# -------------------
# workload_rules.conf
# -------------------
@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.2")
def check_workload_rules_conf_black_list(app, reporter):
    """Check that app does not contain workload_rules.conf in Cloud as it
    automatically trigger actions on running search processes.
    """
    blacklist_conf(
        app,
        reporter.fail,
        "workload_rules.conf",
        "workload_rules.conf defines rules to trigger actions on running "
        "search processes, which is not permitted in Splunk Cloud.",
    )


# ------------------------------------------------------------------------------
# Manual Checks Go Here
# ------------------------------------------------------------------------------


@splunk_appinspect.tags("splunk_appinspect", "manual", "cloud")
@splunk_appinspect.cert_version(min="1.1.19")
def check_for_binary_files_without_source_code(app, reporter):
    """Check that all executable binary files have matching source code. For any binary files, there
    should be a source code provided with the same name. Or, there should be a decalaration of what the
    binary file is all about in the app's REAMDE. Details for passing this check will be returned if you fail
    it."""
    if platform.system() == "Windows":
        # FIXME: tests needed
        reporter.manual_check(
            "Matching source check will be done manually during code review."
        )
    else:
        source_types = [".cpp", ".c", ".java", ".h"]
        source_name_pool = {}
        app_files_iterator = app.iterate_files(types=source_types)
        for directory, file, _ in app_files_iterator:
            current_file_relative_path = os.path.join(directory, file)
            source_name_without_extension = os.path.basename(
                current_file_relative_path
            ).split(".")[0]
            source_name_pool[source_name_without_extension] = current_file_relative_path

        # excluding docx, python and egg files to reduce false positives, and covered elsewhere
        exclude_types = [".docx", ".egg", ".py"]

        readme_names = find_readmes(app)
        readmes_dict = {}
        for readme_name in readme_names:
            full_file_path = os.path.join(app.app_dir, readme_name)
            with codecs.open(full_file_path, encoding="utf-8", errors="ignore") as file:
                readmes_dict[readme_name] = file.read().lower()
        app_files_iterator = app.iterate_files(excluded_types=exclude_types)
        file_output_regex = re.compile(
            "^((?!ASCII text executable)(?!Unicode text executable)(?!UTF-8 text executable)(?!Perl script text executable).)*executable(.)*"
            + "|(.)*shared object(.)*"
            + "|(.)*binary(.)*"
            + "|^((?!Zip archive data).)*archive(.)*",
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )

        for directory, file, _ in app_files_iterator:
            current_file_relative_path = os.path.join(directory, file)
            current_file_full_path = app.get_filename(current_file_relative_path)

            try:
                # file_output = subprocess.check_output(["file", "-b", current_file_full_path])
                # using magic library to substitute the original file cmd
                if current_file_relative_path in app.info_from_file:
                    file_output = app.info_from_file[current_file_relative_path]
                else:
                    file_output = magic.from_file(current_file_full_path)
            except Exception as error:
                # in case of any further exception, throw a manual check instead of an internal error
                # Exception could be UnicodeException, it doesn't have returncode, cmd or output attributes
                return_code = getattr(error, "returncode", "N/A")
                cmd = getattr(error, "cmd", "N/A")
                output = getattr(error, "output", "N/A")
                reporter.manual_check(
                    (
                        f"Please manually check {current_file_relative_path} ({return_code} {cmd} {output}) "
                        'Note if you are using macOS, you might need to "brew install libmagic". '
                        f"File: {current_file_relative_path}"
                    ),
                    current_file_relative_path,
                )
            else:
                if re.match(file_output_regex, file_output):
                    binary_name = os.path.basename(current_file_relative_path).split(
                        "."
                    )[0]
                    if binary_name in source_name_pool:
                        reporter_output = (
                            "Please ensure the binary files are safe. Source file: "
                            f" Bianry file: {current_file_relative_path}"
                            f" Format: {file_output}"
                            f" Source file: {source_name_pool[binary_name]}"
                        )
                        reporter.manual_check(
                            reporter_output, current_file_relative_path
                        )
                    elif readme_names:
                        readme_find = False
                        for readme_name, readme_content in iter(readmes_dict.items()):
                            if (
                                binary_name in readme_content
                                or "# binary file declaration" in readme_content
                            ):
                                reporter_output = (
                                    "Please ensure the binary files are safe. Related info might be included in App README."
                                    f" Binary file: {current_file_relative_path}  Format: {file_output}  README: {readme_name}"
                                )
                                reporter.manual_check(
                                    reporter_output, current_file_relative_path
                                )
                                readme_find = True
                                break
                        if not readme_find:
                            reporter_output = (
                                f"File: {current_file_relative_path}"
                                f" is a binary file (Format: {file_output}) but fail to"
                                " find any source file nor reference info."
                                " Please attach source code of this binary in the package,"
                                ' OR include any information of those binaries under "# Binary File Declaration" section'
                                " (You might need create one) in your App's REAMDE."
                                " We will manually review the source code of the binary."
                            )
                            reporter.fail(reporter_output)
                    else:
                        reporter_output = (
                            f"File: {current_file_relative_path}"
                            f" is a binary file (Format: {file_output}) but fail to"
                            " find any source file nor reference info."
                            " Please attach source code of this binary in the package,"
                            " OR create an App's README under root directory"
                            ' and include any information of those binaries under "# Binary File Declaration" section'
                            " (You might need create one) in README."
                            " We will manually review the source code of the binary."
                        )
                        reporter.fail(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.6.1")
def check_that_app_contains_any_windows_specific_components(app, reporter):
    """Check that the app contains MS Windows specific components, which will not
    function correctly in Splunk Cloud whose OS should be Linux x64.
    """
    if platform.system() == "Windows":
        # FIXME: tests needed
        reporter.manual_check(
            "Matching source check will be done manually during code review."
        )
    else:
        ms_windows_info = ["DOS batch file", "MS Windows", "CRLF line terminators"]
        ms_windows_file_types_in_crlf = [".ps1", ".psm1"]
        excluded_types = [".ico"]
        # only consider default directory here because local directory will be failed
        inputs_conf_path = os.path.join("default", "inputs.conf")
        for path, info in iter(app.info_from_file.items()):
            # check if inputs.conf exists
            _, ext = os.path.splitext(path)
            if inputs_conf_path == path:
                inputs_configuration_file = app.inputs_conf()

                banned_stanzas = [
                    stanza
                    for stanza in inputs_configuration_file.sections()
                    if re.search(r"^monitor:\/\/([a-zA-Z]\:|\.)\\", stanza.name)
                    or re.search(r"^script:\/\/([a-zA-Z]\:|\.)\\", stanza.name)
                    or re.search(r"^perfmon:\/\/", stanza.name)
                    or re.search(r"^MonitorNoHandle:\/\/", stanza.name)
                    or re.search(r"^WinEventLog:\/\/", stanza.name)
                    or re.search(r"^admon:\/\/", stanza.name)
                    or re.search(r"^WinRegMon:\/\/", stanza.name)
                    or re.search(r"^WinHostMon:\/\/", stanza.name)
                    or re.search(r"^WinPrintMon:\/\/", stanza.name)
                    or re.search(r"^WinNetMon:\/\/", stanza.name)
                    or re.search(r"^powershell2:\/\/", stanza.name)
                    or re.search(r"^powershell:\/\/", stanza.name)
                ]

                for stanza in banned_stanzas:
                    reporter_output = (
                        "default/inputs.conf contains a stanza for Windows inputs"
                        " that will not work correctly in Splunk Cloud."
                        " (http://docs.splunk.com/Documentation/Splunk/7.1.3/Admin/Inputsconf)"
                        f" Stanza: [{stanza.name}]. File: {path}, Line: {stanza.lineno}."
                    )
                    reporter.warn(reporter_output, path, stanza.lineno)
            else:
                for sub_info in ms_windows_info:
                    if sub_info in info:
                        if ext in excluded_types or (
                            sub_info == "CRLF line terminators"
                            and ext not in ms_windows_file_types_in_crlf
                        ):
                            continue
                        reporter_output = (
                            f"The app works for MS Windows platform because {path} exists,"
                            f" which is {info}. It is only valid at MS Windows platform."
                            f" File: {path}"
                        )
                        reporter.warn(reporter_output, path)
                        break


# This is a Cloud check that isn't tagged cloud because it always returns
# manual_check and prevents us from auto-vetting.
@splunk_appinspect.tags("splunk_appinspect", "manual")
@splunk_appinspect.cert_version(min="1.1.19")
def check_for_reverse_shells(reporter):
    """Check that the app does not contain reverse shells."""
    reporter_output = "Please check for reverse shells."
    reporter.manual_check(reporter_output)


# This is a Cloud check that isn't tagged cloud because it always returns
# manual_check and prevents us from auto-vetting.
@splunk_appinspect.tags("splunk_appinspect", "manual")
@splunk_appinspect.cert_version(min="1.1.19")
def check_for_auto_update_features(app, reporter):
    """Check that the app does not implement auto-update features."""
    bin_directories = [
        bin_directory
        for arch in app.arch_bin_dirs
        for bin_directory in app.arch_bin_dirs[arch]
    ]
    app_has_auto_update_capability = False
    for bin_directory in bin_directories:
        bin_directory_iterator = app.iterate_files(basedir=bin_directory)
        for directory, _, _ in bin_directory_iterator:
            app_has_auto_update_capability = True
            reporter_output = (
                f"Please check the {directory} directory for app"
                " auto-update features, which is prohibited."
            )
            reporter.manual_check(reporter_output, directory)
            break
    # If an app has nothing in the /bin directory and nothing in any of
    # the architecture-specific directories, it does not have the capacity to
    # update itself.
    if not app_has_auto_update_capability:
        reporter_output = (
            "No scripts found in /bin or architecture-specific" " directories in app."
        )
        reporter.not_applicable(reporter_output)


# This is a Cloud check that isn't tagged cloud because it always returns
# manual_check and prevents us from auto-vetting.
@splunk_appinspect.tags("splunk_appinspect", "manual")
@splunk_appinspect.cert_version(min="1.1.19")
def check_for_known_vulnerabilities_in_third_party_libraries(reporter):
    """Check third party libraries for known vulnerabilities. Splunk Cloud
    Application Security policy defines "Included application libraries have
    multiple vulnerabilities not covered by the components in Transit" as a
    moderate security risk and may or may not be permitted based on
    cumulative risk score.
    """
    reporter_output = (
        "Please check for known vulnerabilities in third-party"
        " libraries. Use these links:"
        " https://web.nvd.nist.gov/view/vuln/search."
        " and https://nvd.nist.gov/cvss.cfm"
    )
    reporter.manual_check(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.22")
def check_for_perl(app, reporter):
    """Check if the app contains Perl scripts. Perl scripts will be inspected
    for compliance with Splunk Cloud security policy.
    """
    application_files = list(app.iterate_files(types=[".cgi", ".pl", ".pm"]))
    if application_files:
        for directory, file, _ in application_files:
            current_file_relative_path = os.path.join(directory, file)
            reporter_output = f"File: {current_file_relative_path}"
            reporter.manual_check(reporter_output, current_file_relative_path)

    else:
        reporter_output = "No Perl scripts found in app."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.22")
def check_for_java(app, reporter):
    """Check whether the app contains java files. Java files will be inspected
    for compliance with Splunk Cloud security policy.
    """
    application_files = list(app.iterate_files(types=[".class", ".jar", ".java"]))
    if application_files:
        for directory, file, _ in application_files:
            current_file_relative_path = os.path.join(directory, file)
            reporter_output = f"java file found. File: {current_file_relative_path}"
            reporter.manual_check(reporter_output, current_file_relative_path)
    else:
        reporter_output = "No java files found in app."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_for_implementing_tscollect(app, reporter):
    """Check that use of
    ['tscollect'](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tscollect)
    in .conf filesl and dashboard xmls then fail it.
    """
    reporter_output = (
        "Find `tscollect` which is not allowed in Splunk Cloud because it can eat up disk space "
        "with usage of `tscollect`. Please don't use `tscollect` in Splunk Cloud. "
    )
    findings = find_spl_command_usage(app, "tscollect")
    for filepath, lineno in findings:
        reporter.fail(reporter_output, filepath, lineno)


@splunk_appinspect.tags("cloud", "private_app", "future")
@splunk_appinspect.cert_version(min="2.11.1")
def check_python_sdk_version(app, reporter):
    """Check that Splunk SDK for Python is up-to-date."""
    # Minimum Splunk SDK for Python version supported
    min_ver = semver.VersionInfo.parse("1.6.15")
    ver_rex = r"\"User-Agent\": \"splunk-sdk-python/([\d.]+.*)\""
    splunklib_exists = False
    py_files = list(app.iterate_files(types=[".py"]))
    # Look for the setting of the User-Agent header in binding.py
    rexs = [RegexBundle(ver_rex)]
    matcher = RegexMatcher(rexs)
    if py_files:
        for directory, file, _ in py_files:
            # At a minimum the Python SDK should have a binding.py with
            # a User-Agent that will contain the version number
            if file != "binding.py":
                continue
            file_path = os.path.join(directory, file)
            full_file_path = app.get_filename(file_path)
            match_result = matcher.match_file(filepath=full_file_path)
            for lineno, result in match_result:
                splunklib_exists = True
                file_path = os.path.join(directory, file)
                # Parse the found version into semver, correcting for
                # bad versions like "0.1" without a patch version
                try:
                    ver = re.search(ver_rex, result).groups()[0]
                    if len(ver.split(".")) == 2:
                        ver += ".0"  # correct for versions without a patch
                    parsed_ver = semver.VersionInfo.parse(ver)
                except Exception as err:
                    reporter_output = (
                        "Issue parsing version found in for the Splunk SDK for "
                        f"Python ({ver}). File: {file_path}. Error: {err}."
                    )
                    reporter.warn(reporter_output, file_path)
                    continue
                if parsed_ver < min_ver:
                    # Found splunklib version is less than the minimum
                    reporter_output = (
                        "Detected an outdated version of the Splunk SDK for "
                        f"Python ({ver}). Please upgrade to version "
                        f"{min_ver[0]}.{min_ver[1]}.{min_ver[2]} or later. "
                        f"File: {file_path}."
                    )
                    reporter.warn(reporter_output, file_path)
    # binding.py not found
    if not splunklib_exists:
        reporter_output = "Splunk SDK for Python not found."
        reporter.not_applicable(reporter_output)
