# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Configuration file standards

Ensure that all configuration files located in the **/default** folder are well formed and valid.
"""
import collections
import logging
import os
import re

import splunk_appinspect
from splunk_appinspect import app_util
from splunk_appinspect.splunk_defined_conf_file_list import SPLUNK_DEFINED_CONFS

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.cert_version(min="1.6.1")
@splunk_appinspect.tags("splunk_appinspect")
def check_validate_no_duplicate_stanzas_in_conf_files(app, reporter):
    """Check that no duplicate
    [stanzas](https://docs.splunk.com/Splexicon:Stanza) exist in .conf files.
    """
    stanzas_regex = r"^\[(.*)\]"
    stanzas = app.search_for_pattern(
        stanzas_regex, types=[".conf"], basedir=["default", "local"]
    )
    stanzas_found = collections.defaultdict(list)

    for fileref_output, match in stanzas:
        filepath, line_number = fileref_output.rsplit(":", 1)
        file_stanza = (filepath, match.group())
        stanzas_found[file_stanza].append(line_number)

    for key, linenos in iter(stanzas_found.items()):
        if len(linenos) > 1:
            for lineno in linenos:
                reporter_output = (
                    f"Duplicate {key[1]} stanzas were found. "
                    f"File: {key[0]}, Line: {lineno}."
                )
                reporter.fail(reporter_output, key[0], lineno)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.12")
def check_config_file_parsing(app, reporter, included_tags):
    """Check that all config files parse cleanly- no trailing whitespace after
    continuations, no duplicated stanzas or options.
    """
    for directory, filename, _ in app.iterate_files(
        types=[".conf"], basedir=["default", "local"]
    ):
        try:
            file_path = os.path.join(directory, filename)
            conf = app.get_config(filename, dir=directory)
            for err, lineno, section in conf.errors:
                reporter_output = (
                    f"{err} at line {lineno} in [{section}] of {filename}. "
                    f"File: {file_path}, Line: {lineno}."
                )
                if err.startswith(("Duplicate stanza", "Repeat item")):
                    if "cloud" in included_tags:
                        reporter.warn(reporter_output, file_path, lineno)
                        continue
                reporter.fail(reporter_output, file_path, lineno)
        except Exception as error:
            logger.error("unexpected error occurred: %s", str(error))
            raise


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.0")
def check_no_default_stanzas(app, reporter):
    """Check that app does not contain any .conf files that create global
    definitions using the `[default]` stanza.
    """
    # Added whitelist support because people are making poor life choices and
    # building splunk features that require the use of the `default` stanza
    # The white list conf files using the default stanza will be supported, but
    # not condoned
    conf_file_whitelist = ["savedsearches.conf"]

    for directory, filename, _ in app.iterate_files(
        types=[".conf"], basedir=["default", "local"]
    ):
        if filename not in conf_file_whitelist:
            file_path = os.path.join(directory, filename)
            try:
                conf = app.get_config(filename, dir=directory)
                for section_name in ["default", "general", "global", "stash"]:

                    if conf.has_section(section_name) and _is_not_empty_section(
                        conf.get_section(section_name)
                    ):
                        if _is_splunk_defined_conf(filename):
                            lineno = conf.get_section(section_name).lineno
                            reporter_output = (
                                f"{section_name} stanza was found in {file_path}. "
                                "Please remove any [default], [general], [global], [stash] stanzas or properties "
                                "outside of a stanza (treated as default/global) "
                                "from conf files defined by Splunk."
                                "These stanzas/properties are not permitted "
                                "because they modify global settings outside the context of the app."
                                f"File: {file_path}, Line: {lineno}."
                            )
                            reporter.fail(reporter_output, file_path, lineno)
            except Exception as error:
                logger.error("unexpected error occurred: %s", str(error))
                raise


def _is_not_empty_section(section):
    return len(section.items()) > 0


def _is_splunk_defined_conf(file_name):
    return file_name in SPLUNK_DEFINED_CONFS


@splunk_appinspect.tags("inputs_conf")
@splunk_appinspect.cert_version(min="1.2.1")
def check_inputs_conf_for_global_settings(app, reporter):
    """Check that `default/inputs.conf` or `local/inputs.conf` does not use any global settings."""
    # Global settings should be grouped under the "default" stanza for the
    # ConfigurationFile object that this library uses
    config_file_paths = app.get_config_file_paths("inputs.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            inputs_conf = app.inputs_conf(directory)
            global_stanza_name = "default"
            if inputs_conf.has_section(global_stanza_name):
                for option_name, option_value, option_lineno in inputs_conf.get_section(
                    global_stanza_name
                ).items():
                    reporter_output = (
                        f"The `{directory}/inputs.conf` specifies"
                        " global settings. These are prohibited in"
                        " Splunk Cloud instances. Please remove this"
                        " functionality."
                        f" Property: {option_name} = {option_value}."
                        f" File: {file_path}, Line: {option_lineno}."
                    )
                    reporter.fail(reporter_output, file_path, option_lineno)
    else:
        reporter_output = "`inputs.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.0")
def check_manipulation_outside_of_app_container(app, reporter):
    """Check that app conf files do not point to files outside the app container.
    Because hard-coded paths won't work in Splunk Cloud, we don't consider to
    check absolute paths.
    """
    reporter_template = (
        "Manipulation outside of the app container was found in "
        "file {}; See stanza `{}`, "
        "key `{}` value `{}`. File: {}, Line: {}."
    )
    app_name = app.package.working_artifact_name

    conf_parameter_arg_regex = re.compile(r""""[^"]+"|'[^']+'|[^"'\s]+""")
    conf_check_list = {
        "app.conf": ["verify_script"],
        "distsearch.conf": ["genKeyScript"],
        "restmap.conf": ["pythonHandlerPath"],
        "authentication.conf": ["scriptPath"],
        "server.conf": ["certCreateScript"],
        "limits.conf": ["search_process_mode"],
    }
    for directory, filename, _ in app.iterate_files(
        types=[".conf"], basedir=["default", "local"]
    ):
        if filename not in conf_check_list:
            continue
        conf = app.get_config(filename, dir=directory)
        for section in conf.sections():
            full_filepath = os.path.join(directory, filename)
            for option in section.settings():
                key = option.name
                value = option.value
                lineno = option.lineno
                if key not in conf_check_list[filename]:
                    continue
                for path in conf_parameter_arg_regex.findall(value):
                    if app_util.is_manipulation_outside_of_app_container(
                        path, app_name
                    ):
                        reporter_output = reporter_template.format(
                            full_filepath,
                            section.name,
                            key,
                            value,
                            full_filepath,
                            lineno,
                        )
                        reporter.fail(reporter_output, full_filepath, lineno)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.2.0")
def check_collections_conf_for_specified_name_field_type(app, reporter):
    """Check that the `filed.<name>` type in collections.conf does not include `boolean`.
    Use `bool` instead.
    """
    if app.file_exists("default", "collections.conf"):
        filename = os.path.join("default", "collections.conf")
        collections_conf = app.collections_conf()
        for section in collections_conf.sections():
            for key, value, lineno in collections_conf.items(section.name):
                if key.startswith("field.") and value == "boolean":
                    reporter_output = (
                        "The field type for filed.<name> in collections.conf includes"
                        " `number|bool|string|time`, use bool to instead of boolean"
                        f" Stanza: [{section.name}]."
                        f" File: {filename}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, filename, lineno)
