# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Lookup file standards

Lookups add fields from an external source to events based on the values of fields that are already present in those events.
"""

import glob
import logging
import os

import splunk_appinspect
from splunk_appinspect import lookup

logger = logging.getLogger(__name__)
report_display_order = 13


@splunk_appinspect.tags("splunk_appinspect", "csv")
@splunk_appinspect.cert_version(min="1.5.0")
def check_lookup_csv_is_valid(app, reporter):
    """Check that `.csv` files are not empty, have at least two columns, have
    headers with no more than 4096 characters, do not use Macintosh-style (`\\r`)
    line endings, have the same number of columns in every row, and contain
    only UTF-8 characters."""

    for basedir, file, _ in app.iterate_files(basedir="lookups", types=[".csv"]):
        app_file_path = os.path.join(basedir, file)
        full_file_path = app.get_filename(app_file_path)
        try:
            is_valid, rationale = lookup.LookupHelper.is_valid_csv(full_file_path)
            if not is_valid:
                reporter.fail(
                    "This .csv lookup is not formatted as valid csv."
                    f" Details: {rationale}",
                    app_file_path,
                )
            elif rationale != lookup.VALID_MESSAGE:
                reporter.warn(rationale, app_file_path)
        except Exception as err:
            logger.warning(
                "Error validating lookup. File: %s. Error: %s", full_file_path, err
            )
            reporter.fail(
                "Error opening and validating lookup. Please"
                " investigate this lookup and remove it if it is not"
                " formatted as valid CSV.",
                app_file_path,
            )


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="2.0.0")
def check_for_lookups_file_name(app, reporter):
    """Check that no two files/directories under the lookups directory have this naming pattern respectively:
    `xxx` and `xxx.default` - with the only difference in the `.default` extension.
    During the installation of an app in Splunk Cloud, a lookup file will be temporarily renamed to append an additional
    `.default` extension to it, which will cause error if a namesake file already exists.
    """

    def is_preserve_lookups_mode(app):
        if app.file_exists("default", "app.conf"):
            app_conf = app.app_conf()
            if app_conf.has_section("shclustering"):
                shclustering_stanza = app_conf.get_section("shclustering")
                if shclustering_stanza.has_option("deployer_lookups_push_mode"):
                    push_mode = shclustering_stanza.get_option(
                        "deployer_lookups_push_mode"
                    ).value
                    if push_mode == "always_overwrite":
                        return False
        return True

    if app.directory_exists("lookups"):
        base_dir = os.path.join(app.app_dir, "lookups")

        if not is_preserve_lookups_mode(app):
            return
        for path in glob.glob(base_dir + os.sep + "*.default"):
            csv_path = path[:-8]
            if os.path.exists(csv_path):
                default_file = os.path.basename(path)
                csv_file = os.path.basename(csv_path)
                default_path = os.path.join("lookups", default_file)
                reporter.fail(
                    f" When installing an app in Splunk Cloud, the lookup file '{csv_file}'"
                    " will be temporarily renamed with an extra '.default' extension."
                    f" It will run into errors if '{default_file}' file already exists. "
                    " Please remove one of them or change one of their name.",
                    default_path,
                )
    else:
        reporter.not_applicable("lookups folder does not exist")
