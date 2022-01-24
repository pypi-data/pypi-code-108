# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Meta file standards

Ensure that all meta files located in the **/metadata** folder are well formed and valid.
"""
import collections
import logging
import os

import splunk_appinspect

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.cert_version(min="1.6.1")
@splunk_appinspect.tags("splunk_appinspect")
def check_validate_no_duplicate_stanzas_in_meta_files(app, reporter):
    """Check that `.meta` files do not have duplicate
    [stanzas](https://docs.splunk.com/Splexicon:Stanza).
    """
    stanzas_regex = r"^\[(.*)\]"
    stanzas = app.search_for_pattern(stanzas_regex, types=[".meta"])
    stanzas_found = collections.defaultdict(list)

    for fileref_output, match in stanzas:
        filepath, line_number = fileref_output.rsplit(":", 1)
        file_stanza = (filepath, match.group())
        stanzas_found[file_stanza].append(line_number)

    for key, linenos in iter(stanzas_found.items()):
        if len(linenos) > 1:
            for lineno in linenos:
                reporter_output = f"Duplicate {key[1]} stanzas were found. File: {key[0]}, Line: {lineno}."
                reporter.fail(reporter_output, key[0], lineno)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.12")
def check_meta_file_parsing(app, reporter):
    """Check that all `.meta` files parse with no trailing whitespace after
    continuations with no duplicate stanzas or options.
    """
    for directory, file, _ in app.iterate_files(types=[".meta"]):
        file_path = os.path.join(directory, file)
        meta = app.get_meta(file, directory=directory)
        for err, line, section in meta.errors:
            reporter_output = (
                f"{err} at line {line} in [{section}] of {file}."
                " File: {file_path}, Line: {line}."
            )
            reporter.fail(reporter_output, file_path, line)
