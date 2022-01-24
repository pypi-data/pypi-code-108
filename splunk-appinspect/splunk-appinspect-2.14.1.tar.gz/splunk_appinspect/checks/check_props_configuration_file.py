# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Props Configuration file standards

Ensure that all props.conf files located in the `default` (or `local`) folder are well
formed and valid.

- [props.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Propsconf)
- [transforms.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Transformsconf)
"""
import logging
import os
import re

import splunk_appinspect
from splunk_appinspect.configuration_file import ConfigurationFile, ConfigurationSection
from splunk_appinspect.splunk_pretrained_sourcetypes_list import (
    SPLUNK_PRETRAINED_SOURCETYPES,
)

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.8")
def check_props_conf_has_transforms_option_and_transforms_conf_exist(app, reporter):
    """Check that there is a 'transforms.conf' file when TRANSFORM- options
    are defined in `props.conf`.
    """
    settings_key_regex_pattern = "TRANSFORMS-"

    if app.file_exists("default", "props.conf"):
        file_path = os.path.join("default", "props.conf")
        props_config = app.props_conf()
        sections_with_transforms = list(
            props_config.sections_with_setting_key_pattern(settings_key_regex_pattern)
        )

        if sections_with_transforms:
            for section in sections_with_transforms:
                for setting in section.settings_with_key_pattern(
                    settings_key_regex_pattern
                ):
                    if app.file_exists("default", "transforms.conf"):
                        pass
                    else:
                        reporter_output = (
                            "No transforms.conf exists for "
                            f"[{section.name}], {setting.name}. "
                            f"File: {file_path}, Line: {section.lineno}."
                        )
                        reporter.fail(reporter_output, file_path, section.lineno)
        else:
            reporter_output = "No TRANSFORMS- properties were declared."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.8")
def check_props_conf_has_transforms_option_and_transforms_conf_has_matching_stanza(
    app, reporter
):
    """Check that TRANSFORM- options in `props.conf` have associated stanzas in
    `transforms.conf` file.
    """
    settings_key_regex_pattern = "TRANSFORMS-"

    if app.file_exists("default", "props.conf"):
        file_path = os.path.join("default", "props.conf")
        props_config = app.props_conf()
        props_sections_with_transforms = list(
            props_config.sections_with_setting_key_pattern(settings_key_regex_pattern)
        )

        if props_sections_with_transforms:
            if app.file_exists("default", "transforms.conf"):
                transforms_config = app.transforms_conf()
                for props_section in props_sections_with_transforms:
                    for setting in props_section.settings_with_key_pattern(
                        settings_key_regex_pattern
                    ):
                        for props_transforms_stanza_name in setting.value.split(","):
                            if transforms_config.has_section(
                                props_transforms_stanza_name.strip()
                            ):
                                pass  # Do nothing, test passed
                            else:
                                reporter_output = (
                                    "Transforms.conf does not contain"
                                    f" a [{props_transforms_stanza_name.strip()}] stanza to match"
                                    f" props.conf [{props_section.name}] {setting.name}={setting.value}."
                                    f" File: {file_path}, Line: {props_section.lineno}."
                                )
                                reporter.fail(
                                    reporter_output, file_path, props_section.lineno
                                )
            else:
                reporter_output = f"No transforms.conf exists. File: {file_path}"
                reporter.fail(reporter_output, file_path)
        else:
            reporter_output = "No TRANSFORMS- properties were declared."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.8")
def check_props_conf_has_report_option_and_transforms_conf_exist(app, reporter):
    """Check that there is a 'transforms.conf' file when REPORT- options are
    defined in `props.conf`.
    """
    settings_key_regex_pattern = "REPORT-"

    config_file_paths = app.get_config_file_paths("props.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            props_config = app.props_conf(directory)
            sections_with_transforms = list(
                props_config.sections_with_setting_key_pattern(
                    settings_key_regex_pattern
                )
            )

            if sections_with_transforms:
                for section in sections_with_transforms:
                    for setting in section.settings_with_key_pattern(
                        settings_key_regex_pattern
                    ):
                        if app.file_exists(directory, "transforms.conf"):
                            pass
                        else:
                            reporter_output = (
                                "No transforms.conf exists for "
                                f"[{section.name}], {setting.name}. "
                                f"File: {file_path}, Line: {section.lineno}."
                            )
                            reporter.fail(reporter_output, file_path, section.lineno)
            else:
                reporter_output = "No REPORT- properties were declared."
                reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


# TODO: Add documentation link
@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.8")
def check_props_conf_has_report_option_and_transforms_conf_has_matching_stanza(
    app, reporter
):
    """Check that each REPORT- in `props.conf` has an associated stanza in
    `transforms.conf` file.
    """
    settings_key_regex_pattern = "REPORT-"

    config_file_paths = app.get_config_file_paths("props.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            props_config = app.props_conf(directory)
            props_sections_with_transforms = list(
                props_config.sections_with_setting_key_pattern(
                    settings_key_regex_pattern
                )
            )

            if props_sections_with_transforms:
                if app.file_exists(directory, "transforms.conf"):
                    transforms_config = app.transforms_conf(dir=directory)
                    for props_section in props_sections_with_transforms:
                        for setting in props_section.settings_with_key_pattern(
                            settings_key_regex_pattern
                        ):
                            for props_transforms_stanza_name in setting.value.split(
                                ","
                            ):
                                if transforms_config.has_section(
                                    props_transforms_stanza_name.strip()
                                ):
                                    pass  # Do nothing, test passed
                                else:
                                    reporter_output = (
                                        "Transforms.conf does not contain"
                                        f" a [{props_transforms_stanza_name.strip()}] stanza to match"
                                        f" props.conf [{props_section.name}] {setting.name}={setting.value}."
                                        f" File: {file_path}, Line: {props_section.lineno}."
                                    )
                                    reporter.fail(
                                        reporter_output, file_path, props_section.lineno
                                    )
                else:
                    reporter_output = f"No transforms.conf exists. File: {file_path}"
                    reporter.fail(reporter_output, file_path)
            elif directory == "default":
                reporter_output = "No REPORT- properties were declared."
                reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.8")
def check_props_conf_has_report_option_and_transforms_conf_has_required_option(
    app, reporter
):
    """Check that REPORT- options in props.conf, have either DELIMS or REGEX
    options in the matching transforms.conf stanza. If it has REGEX option, further
    check whether is has at least one capturing group.
    """
    settings_key_regex_pattern = "REPORT-"

    config_file_paths = app.get_config_file_paths("props.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            props_config: ConfigurationFile = app.props_conf(directory)
            props_sections_with_transforms = list(
                props_config.sections_with_setting_key_pattern(
                    settings_key_regex_pattern
                )
            )

            if props_sections_with_transforms:
                if app.file_exists(directory, "transforms.conf"):
                    transforms_config: ConfigurationFile = app.transforms_conf(
                        directory
                    )
                    for props_section in props_sections_with_transforms:
                        # Check if KV_MODE = xml or json, if so these are extracted automatically so N/A
                        # See: ACD-1516
                        if props_section.has_option(
                            "KV_MODE"
                        ) and props_section.get_option("KV_MODE").value in [
                            "json",
                            "xml",
                        ]:
                            KV_MODE_value = props_section.get_option("KV_MODE").value
                            reporter_output = (
                                "REPORT- property stanza has KV_MODE"
                                f" = {KV_MODE_value} so DELIMS/REGEX not required."
                            )
                            reporter.not_applicable(reporter_output)
                            continue
                        for setting in props_section.settings_with_key_pattern(
                            settings_key_regex_pattern
                        ):
                            for props_transforms_stanza_name in setting.value.split(
                                ","
                            ):
                                if transforms_config.has_section(
                                    props_transforms_stanza_name.strip()
                                ):
                                    props_transforms_stanza: ConfigurationSection = (
                                        transforms_config.get_section(
                                            props_transforms_stanza_name.strip()
                                        )
                                    )
                                    if props_transforms_stanza.has_setting_with_pattern(
                                        "regex"
                                    ):
                                        regex_str: str = (
                                            props_transforms_stanza.get_option(
                                                "REGEX"
                                            ).value
                                        )
                                        matches = re.search(
                                            r"(?<!\\)\(.*(?<!\\)\)", regex_str
                                        )
                                        if matches is None:
                                            reporter_output = (
                                                f"Transforms.conf [{props_transforms_stanza_name.strip()}]"
                                                " specify a REGEX without any capturing group."
                                                " This is an incorrect usage."
                                                " Please include at least one capturing group."
                                            )
                                            reporter.fail(
                                                reporter_output,
                                                os.path.join(
                                                    directory, "transforms.conf"
                                                ),
                                                props_transforms_stanza.get_option(
                                                    "REGEX"
                                                ).lineno,
                                            )
                                        else:
                                            pass
                                    elif props_transforms_stanza.has_setting_with_pattern(
                                        "delims"
                                    ):
                                        pass
                                    else:
                                        reporter_output = (
                                            f"Transforms.conf [{props_transforms_stanza_name.strip()}]"
                                            " does not specify DELIMS or REGEX to match"
                                            f" props.conf [{props_section.name}], {setting.name}."
                                            f" File: {file_path}, Line: {props_section.lineno}."
                                        )
                                        reporter.fail(
                                            reporter_output,
                                            file_path,
                                            props_section.lineno,
                                        )
                                else:
                                    reporter_output = (
                                        "Transforms.conf does not contain"
                                        f" a [{props_transforms_stanza_name.strip()}] stanza to match"
                                        f" props.conf [{props_section.name}] {setting.name}={setting.value}."
                                        f" File: {file_path}, Line: {props_section.lineno}."
                                    )
                                    reporter.fail(
                                        reporter_output, file_path, props_section.lineno
                                    )
                else:
                    reporter_output = f"No transforms.conf exists. File: {file_path}"
                    reporter.fail(reporter_output, file_path)
            else:
                reporter_output = "No REPORT- properties were declared."
                reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.16")
def check_props_conf_regex_stanza_name_followed_by_double_colon(app, reporter):
    """Check that the props.conf stanzas (delayedrule, host, rule, or source)
        are followed by `::`.

    For example:

     * `[host::nyc*]`
     * `[rule::bar_some]`
    """
    config_file_paths = app.get_config_file_paths("props.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            props_conf = app.props_conf(directory)

            # if starts with host, source, rule or delayedrule then it is a
            # props.conf stanza name that uses regex
            regex_stanza_names = ["host", "delayedrule", "rule", "source"]

            regex_stanza_patterns = [
                f"^{regex_stanza_name}" for regex_stanza_name in regex_stanza_names
            ]
            regex_stanza_patterns_str = "|".join(regex_stanza_patterns)
            regex_stanza_patterns_regex_object = re.compile(
                regex_stanza_patterns_str, re.MULTILINE | re.IGNORECASE
            )

            valid_regex_stanza_patterns = [
                fr"^{regex_stanza_pattern}(?:::|\w+)"
                for regex_stanza_pattern in regex_stanza_names
            ]
            valid_regex_stanza_patterns_str = "|".join(valid_regex_stanza_patterns)
            valid_regex_stanza_patterns_regex_object = re.compile(
                valid_regex_stanza_patterns_str, re.MULTILINE | re.IGNORECASE
            )

            invalid_props_stanza_names = [
                (stanza.name, stanza.lineno)
                for stanza in props_conf.sections()
                if (
                    re.search(regex_stanza_patterns_regex_object, stanza.name)
                    and not re.search(
                        valid_regex_stanza_patterns_regex_object, stanza.name
                    )
                )
            ]
            if invalid_props_stanza_names:
                for invalid_props_stanza_name, lineno in invalid_props_stanza_names:
                    reporter_output = (
                        "Missing colon(s) detected for a props.conf"
                        " regex stanza name. Make sure it uses `::`."
                        f" Stanza Name: {invalid_props_stanza_name}."
                        f" File: {file_path}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, file_path, lineno)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="2.1.0")
def check_pretrained_sourcetypes_have_only_allowed_transforms(app, reporter):
    """
    Check that pretrained sourctypes in props.conf have only "TRANSFORM-" or "SEDCMD" settings,
    and that those transforms only modify the host, source, or sourcetype.
    """

    allowed_dest_keys = ["MetaData:Host", "MetaData:Source", "MetaData:Sourcetype"]

    props_file_path = os.path.join("default", "props.conf")
    transforms_file_path = os.path.join("default", "transforms.conf")
    if not app.file_exists(props_file_path):
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)
        return

    # collect all the sections for pretrained sourcetypes
    props_conf = app.props_conf()
    pretrained_sourcetype_sections = []
    for section in props_conf.sections():
        if section.name in SPLUNK_PRETRAINED_SOURCETYPES:
            pretrained_sourcetype_sections.append(section)

    # do the checking
    for section in pretrained_sourcetype_sections:
        for setting in section.settings():

            # these sections must have only "TRANSFORM-" or "SEDCMD-" settings
            if not setting.name.startswith(
                "TRANSFORMS-"
            ) and not setting.name.startswith("SEDCMD"):
                reporter_output = "Only TRANSFORMS- or SEDCMD options are allowed for pretrained sourcetypes."
                reporter.warn(reporter_output, props_file_path, setting.lineno)
                return

            if setting.name.startswith("TRANSFORMS-"):
                if not app.file_exists(transforms_file_path):
                    reporter_output = (
                        "No transforms.conf exists for setting in "
                        f"props.conf: {setting.name}={setting.value}"
                    )
                    reporter.warn(reporter_output, props_file_path, setting.lineno)
                    return

                transforms_conf = app.transforms_conf()

                for transform_stanza_name in setting.value.replace(" ", "").split(","):

                    if not transforms_conf.has_section(transform_stanza_name):
                        reporter_output = (
                            f"Transforms.conf does not contain a [{transform_stanza_name.strip()}] stanza"
                            f"to match props.conf [{section.name}] {setting.name}={setting.value}"
                        )
                        reporter.warn(reporter_output, props_file_path, setting.lineno)
                        return

                    # the transforms may only modify the allowed fields
                    transforms_section = transforms_conf.get_section(
                        transform_stanza_name
                    )
                    if transforms_section.has_option("DEST_KEY"):
                        dest = transforms_section.get_option("DEST_KEY")
                        if dest.value not in allowed_dest_keys:
                            reporter_output = (
                                f"Modifying the {dest.value} field for "
                                "a pretrained sourcetype is not allowed."
                            )
                            reporter.warn(
                                reporter_output, transforms_file_path, dest.lineno
                            )


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="2.2.0")
def check_props_conf_extract_option_has_named_capturing_group(app, reporter):
    """Check that each EXTRACT- in `props.conf` has regex with
    at least one named capturing group.
    """
    settings_key_regex_pattern = "EXTRACT-"

    config_file_paths = app.get_config_file_paths("props.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            props_config: ConfigurationFile = app.props_conf(directory)
            props_extract_sections = list(
                props_config.sections_with_setting_key_pattern(
                    settings_key_regex_pattern
                )
            )

            if props_extract_sections:
                for props_section in props_extract_sections:
                    for setting in props_section.settings_with_key_pattern(
                        settings_key_regex_pattern
                    ):
                        matches = re.search(
                            r"(?<!\\)\(\?P?\<\w+\>.*(?<!\\)\)", setting.value
                        )
                        if matches is not None:
                            pass
                        else:
                            reporter_output = (
                                f"[{setting.name}] setting in props.conf specified a regex"
                                " without any named capturing group."
                                " This is an incorrect usage."
                                " Please include at least one named capturing group."
                            )
                            reporter.fail(reporter_output, file_path, setting.lineno)
            elif directory == "default":
                reporter_output = "No EXTRACT- properties were declared."
                reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No props.conf file exists."
        reporter.not_applicable(reporter_output)
