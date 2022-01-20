# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Custom workflow actions structure and standards

Custom workflow actions are defined in a **workflow_actions.conf** file in the **/default** directory of the app. For more, see [About lookups](http://docs.splunk.com/Documentation/Splunk/latest/Knowledge/Aboutlookupsandfieldactions) and [workflow_actions.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Workflow_actionsconf).
"""
import logging
import os

import splunk_appinspect

logger = logging.getLogger(__name__)

report_display_order = 20


@splunk_appinspect.tags("splunk_appinspect", "custom_workflow_actions")
@splunk_appinspect.cert_version(min="1.1.7")
def check_workflow_actions_conf_exists(app, reporter):
    """Check that a valid `workflow_actions.conf` file exists at
    `default/workflow_actions.conf`.
    """
    workflow_actions = app.get_workflow_actions()
    if workflow_actions.configuration_file_exists():
        pass
    else:
        reporter_output = "The 'workflow_actions.conf' does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "custom_workflow_actions")
@splunk_appinspect.cert_version(min="1.1.7")
def check_required_stanza_fields_are_specified(app, reporter):
    """Check that stanzas in `workflow_actions.conf.spec` have the required
    fields, type, and label.
    """
    workflow_actions = app.get_workflow_actions()
    if workflow_actions.configuration_file_exists():
        file_path = os.path.join("default", "workflow_actions.conf")
        for action in workflow_actions.get_workflow_actions():

            if "type" not in action.args:
                reporter_output = (
                    f"The stanza [{action.name}] does not specify 'type'. "
                    f"File: {file_path}, Line: {action.lineno}."
                )
                reporter.fail(reporter_output, file_path, action.lineno)

            if "label" not in action.args:
                reporter_output = (
                    f"The stanza [{action.name}] does not specify 'label'. "
                    f"File: {file_path}, Line: {action.lineno}."
                )
                reporter.fail(reporter_output, file_path, action.lineno)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.1.20")
def check_workflow_actions_link_uri_does_not_use_http_protocol(app, reporter):
    """Check that for each workflow action in `workflow_actions.conf` the
    link.uri property uses the https protocol for external links. Unencrypted
    http is permitted for internal links.
    """
    if app.file_exists("default", "workflow_actions.conf"):
        file_path = os.path.join("default", "workflow_actions.conf")
        workflow_actions = app.get_workflow_actions()

        workflow_actions_with_link_uri = [
            workflow_action
            for workflow_action in workflow_actions.get_workflow_actions()
            if "link.uri" in workflow_action.args
        ]
        for workflow_action in workflow_actions_with_link_uri:
            links = workflow_action.args["link.uri"]
            link_uri = links[0].strip()
            # Internal links (to the local server) are permitted to be HTTP,
            # external links must use HTTPS
            if link_uri.startswith(
                (
                    "/",
                    "http://localhost",
                    "http://127.0.0.1",
                    "localhost",
                    "127.0.0.1",
                    "https://",
                )
            ):
                pass
            else:
                reporter_output = (
                    f"The workflow action [{workflow_action.name}] link.uri"
                    " property appears to be an external"
                    " link that is unencrypted. Please"
                    f" change `{link_uri}` to use https://."
                    f" File: {file_path}, Line: {links[1]}."
                )
                reporter.fail(reporter_output, file_path, links[1])
    else:
        reporter_output = "`workflow_actions.conf` does not exist."
        reporter.not_applicable(reporter_output)
