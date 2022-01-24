# Copyright 2019 Splunk Inc. All rights reserved.

"""
### REST endpoints and handler standards

REST endpoints are defined in a **restmap.conf** file in the **/default** directory of the app. For more, see [restmap.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Restmapconf).
"""
import logging
import os

import splunk_appinspect

logger = logging.getLogger(__name__)

report_display_order = 23


@splunk_appinspect.tags("splunk_appinspect", "restmap_config", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.0")
@splunk_appinspect.display(report_display_order=1)
def check_restmap_conf_exists(app, reporter):
    """Check that `restmap.conf` file exists at `default/restmap.conf` when
    using REST endpoints.
    """
    rest_map = app.get_rest_map()
    if rest_map.configuration_file_exists():
        pass
    else:
        reporter_output = "No restmap.conf file exists."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "restmap_config")
@splunk_appinspect.cert_version(min="1.1.0")
def check_rest_handler_scripts_exist(app, reporter):
    """Check that each stanza in restmap.conf has a matching handler script.
    if not, fail this app.
    """
    do_rest_handler_scripts_check(app, reporter.fail)


@splunk_appinspect.tags("cloud", "restmap_config", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_rest_handler_scripts_exist_for_cloud(app, reporter):
    """Check that each stanza in restmap.conf has a matching handler script.
    if not, throw a warning.
    """
    do_rest_handler_scripts_check(app, reporter.fail)


def do_rest_handler_scripts_check(app, reporter_result):
    """Check that each stanza in restmap.conf has a matching handler script."""
    rest_map = app.get_rest_map()
    if rest_map.configuration_file_exists():
        # From ACD-300, ACD-271,ACD-367
        # A rest config can have both, handler and handler_file. Or use the global handler
        # See
        # http://docs.splunk.com/Documentation/Splunk/latest/Admin/restmapconf
        file_path = os.path.join("default", "restmap.conf")
        global_handler = rest_map.global_handler_file()

        if global_handler.exists():
            message = f"A global rest handler was found at {global_handler.file_path}"
            logger.info(message)

        else:
            logger.info(
                "A global rest handler was not found at %s", global_handler.file_path
            )

            handler_list = rest_map.handlers()
            for handler in handler_list:
                if (
                    handler.handler_file().exists()
                    or handler.handler().exists()
                    or handler.executable_script_file().exists()
                ):
                    pass
                else:
                    reporter_output = (
                        f"Neither the handler or handlerfile specified in the stanza {handler.name} was found"
                        f" in app/bin for {handler.handler_file().file_path}, {handler.handler().file_path} or"
                        f" {handler.executable_script_file().file_path}. File: {file_path}, Line: {handler.lineno}."
                    )
                    reporter_result(reporter_output, file_path, handler.lineno)
    else:
        pass


@splunk_appinspect.tags(
    "splunk_appinspect", "restmap_config", "cloud", "python3_version", "private_app"
)
@splunk_appinspect.cert_version(min="2.1.0")
def check_rest_handler_python_executable_exists(app, reporter):
    """Check that python version is python3 for executables in restmap.conf."""
    rest_map = app.get_rest_map()
    file_path = os.path.join("default", "restmap.conf")
    if rest_map.configuration_file_exists():
        handler_list = rest_map.handlers()
        for handler in handler_list:
            # Skip non-python rest handler. It is reasonable to assume that Python files will have .py extension.
            if (
                handler.scripttype == "persist"
                and not handler.handler_module_file_name.endswith(".py")
            ):
                continue

            # Verify python rest handler.
            if not handler.python_version or handler.python_version != "python3":
                reporter_message = (
                    f"The handler of stanza [{handler.name}] should be `python3` executable. "
                    f"File: {file_path}, Line: {handler.lineno}."
                )
                reporter.fail(reporter_message, file_path, handler.lineno)
    else:
        reporter_output = "No restmap.conf file exists."
        reporter.not_applicable(reporter_output)
