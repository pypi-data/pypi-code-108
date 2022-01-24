# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Outputs.conf file standards

Ensure that the **outputs.conf** file located in the **/default** folder of the app is well formed and valid. For more, see [outputs.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Outputsconf).
"""
import os

import splunk_appinspect
from splunk_appinspect.splunk import normalizeBoolean


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.4")
def check_if_outputs_conf_exists(app, reporter):
    """Check that forwarding enabled in 'outputs.conf' is failed in cloud"""
    config_file_paths = app.get_config_file_paths("outputs.conf")
    option_name = "disabled"

    if not config_file_paths:
        reporter_output = "`outputs.conf` does not exist."
        reporter.not_applicable(reporter_output)
    else:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            outputs_conf = app.outputs_conf(directory)
            section_names = outputs_conf.section_names()
            if not section_names:
                # the situation that an outputs.conf has only global settings outside of any stanza is covered by check_no_default_stanzas
                pass
            else:
                for section in section_names:
                    if not outputs_conf.has_option(section, option_name):
                        reporter_output = (
                            f"From `{directory}/outputs.conf`, output is enabled by default."
                            f" This is prohibited in Splunk Cloud. File: {file_path}"
                        )
                        reporter.fail(reporter_output, file_path)
                    else:
                        is_disabled = normalizeBoolean(
                            outputs_conf.get(section, option_name)
                        )
                        if is_disabled:
                            pass
                        else:
                            lineno = (
                                outputs_conf.get_section(section)
                                .get_option(option_name)
                                .lineno
                            )
                            reporter_output = (
                                f"From `{directory}/outputs.conf`, output is enabled with 'disabled = False'."
                                " This is prohibited in Splunk Cloud. "
                                f" Stanza: [{section}]. File: {file_path}, Line: {lineno}."
                            )
                            reporter.fail(reporter_output, file_path, lineno)
