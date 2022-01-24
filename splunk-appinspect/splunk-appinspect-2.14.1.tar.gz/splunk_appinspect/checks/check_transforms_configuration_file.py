# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Transforms.conf file standards

Ensure that the **transforms.conf** file located in the **/default** folder is well formed and valid. For more, see [transforms.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Transformsconf).
"""
import logging
import os

import regex as re

import splunk_appinspect

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.12")
def check_all_lookups_are_used(app, reporter):
    """Check that all files in the /lookups directory are referenced in
    `transforms.conf`.
    """
    lookup_file_names = set()
    transforms_reference_file_names = set()
    for _, file_name, _ in app.iterate_files(basedir="lookups"):
        if file_name.endswith(".default"):
            loookup_file_no_default_suffix = file_name[
                : len(file_name) - len(".default")
            ]
            lookup_file_names.add(loookup_file_no_default_suffix)
        else:
            lookup_file_names.add(file_name)

    if app.file_exists("default", "transforms.conf"):
        file_path = os.path.join("default", "transforms.conf")
        transforms = app.transforms_conf()
        for section in transforms.sections():
            if section.has_option("filename"):
                lookup_file_name = section.get_option("filename").value
                transforms_reference_file_names.add(lookup_file_name)
        for file_name in lookup_file_names - transforms_reference_file_names:
            reporter_output = (
                f"Lookup file {file_name} is not referenced in"
                f" transforms.conf. File: {file_path}"
            )
            reporter.fail(reporter_output, file_path)
    else:
        reporter.not_applicable("No transforms.conf in app.")


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.12")
def check_capture_groups_in_transforms(app, reporter):
    """Check that all capture groups are used in transforms.conf.
    Groups not used for capturing should use the
    [non-capture group syntax](http://docs.splunk.com/Documentation/Splunk/latest/Knowledge/AboutSplunkregularexpressions#Non-capturing_group_matching)
    """
    if app.file_exists("default", "transforms.conf"):
        transforms = app.transforms_conf()
        file_path = os.path.join("default", "transforms.conf")
        for section in transforms.sections():
            if section.has_option("REGEX") and section.has_option("FORMAT"):
                regex = section.get_option("REGEX")
                fmt = section.get_option("FORMAT")

                if fmt.value and (not re.search(r"\$[\d]+", fmt.value)):
                    # Do not continue to check if there is no $\d in FORMAT.
                    continue

                try:
                    # Splunk regular expressions are PCRE (Perl Compatible Regular Expressions)
                    # re does not support PCRE, so use regex as re, see import part
                    pattern = re.compile(regex.value)
                except re.error:
                    reporter_output = (
                        "The following stanza contains invalid `REGEX` property."
                        f" Stanza: [{section.name}]"
                        f" REGEX: {regex.value}."
                        f" File: {file_path},"
                        f" Line: {regex.lineno}"
                    )
                    reporter.fail(reporter_output, file_path, regex.lineno)
                    return

                unused_groups = []
                for i in range(pattern.groups):
                    if fmt.value.find("$" + str(i + 1)) < 0:
                        unused_groups.append("$" + str(i + 1))

                if unused_groups:
                    url = "http://docs.splunk.com/Documentation/Splunk/latest/Knowledge/AboutSplunkregularexpressions#Non-capturing_group_matching"
                    reporter_output = (
                        "The following stanza contains `FORMAT`"
                        f" property that does not match its `REGEX` property, missing: {unused_groups}."
                        f" Stanza: [{section.name}]"
                        f" REGEX: {regex}"
                        f" FORMAT: {fmt.value}."
                        " If you don't want to capture any group in your regexp,"
                        " please use a non-capturing expression."
                        f" See {url} for details. File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)
    else:
        reporter.not_applicable("No transforms.conf in app.")
