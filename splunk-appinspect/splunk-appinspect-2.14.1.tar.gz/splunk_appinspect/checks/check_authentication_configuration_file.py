# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Authentication.conf file standards

Ensure that `bindDNpassword` is not specified. For more, see [authentication.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Authenticationconf).
"""

import logging
import os

import splunk_appinspect
from splunk_appinspect.splunk import normalizeBoolean

logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.5.0")
def check_authentication_conf_does_not_have_binddnpassword_property(app, reporter):
    """Check that stanzas in `authentication.conf` do not use the the
    bindDNpassword property.
    """
    config_file_paths = app.get_config_file_paths("authentication.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            authentication_conf_file = app.authentication_conf(dir=directory)
            stanzas_with_bind_dn_password = [
                stanza_name
                for stanza_name in authentication_conf_file.section_names()
                if authentication_conf_file.has_option(stanza_name, "bindDNpassword")
            ]
            if stanzas_with_bind_dn_password:
                for stanza_name in stanzas_with_bind_dn_password:
                    lineno = (
                        authentication_conf_file.get_section(stanza_name)
                        .get_option("bindDNpassword")
                        .lineno
                    )
                    reporter_output = (
                        "authentication.conf contains the"
                        " property bindDNpassword. Plain text"
                        " credentials should not be included in an"
                        " app. Please remove the bindDNpassword= property."
                        f" Stanza: [{stanza_name}]. File: {file_path}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, file_path, lineno)
    else:
        reporter_output = "authentication.conf does not exist."
        reporter.not_applicable(reporter_output)


# ACD-2339
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.0")
def check_saml_auth_should_not_turn_off_signed_assertion(app, reporter):
    """Check that saml-* stanzas in `authentication.conf` do not turn off signedAssertion property"""
    config_file_paths = app.get_config_file_paths("authentication.conf")
    if config_file_paths:
        for directory, _ in iter(config_file_paths.items()):
            authentication_conf_file = app.authentication_conf(dir=directory)
            has_auth_type = authentication_conf_file.has_option(
                "authentication", "authType"
            )
            if (
                has_auth_type
                and authentication_conf_file.get("authentication", "authType") == "SAML"
            ):
                _report_failure_for_saml_stanza_with_signed_assertion_off(
                    directory, authentication_conf_file, reporter
                )

    else:
        reporter_output = "authentication.conf does not exist."
        reporter.not_applicable(reporter_output)


def _report_failure_for_saml_stanza_with_signed_assertion_off(
    directory, auth_conf, reporter
):
    stanzas_with_signed_assertion = [
        (section.name, section.lineno)
        for section in auth_conf.sections_with_setting_key_pattern("signedAssertion")
        if section.name.startswith("saml-") and _is_signed_assertion_off(section)
    ]
    file_path = os.path.join(directory, "authentication.conf")
    for stanza_name, stanza_lineno in stanzas_with_signed_assertion:
        reporter_output = (
            "SAML signedAssertion property is turned off, which will introduce vulnerabilities. "
            "Please turn the signedAssertion property on. "
            f"Stanza: [{stanza_name}] "
            f"File: {file_path}, "
            f"Line: {stanza_lineno}."
        )
        reporter.fail(reporter_output, file_path, stanza_lineno)


def _is_signed_assertion_off(section):
    return not normalizeBoolean(section.get_option("signedAssertion").value.strip())


@splunk_appinspect.tags("splunk_appinspect", "cloud", "python3_version", "private_app")
@splunk_appinspect.cert_version(min="2.1.0")
def check_scripted_authentication_has_valid_python_version_property(
    app, reporter, target_splunk_version
):
    """Check that all the scripted authentications defined in `authentication.conf` are explicitly
    set the python.version to python3.
    """
    if target_splunk_version < "splunk_8_0":
        return

    config_file_paths = app.get_config_file_paths("authentication.conf")
    if config_file_paths:
        for directory, filename in iter(config_file_paths.items()):
            file_path = os.path.join(directory, filename)
            authentication_conf_file = app.authentication_conf(dir=directory)
            if (
                authentication_conf_file.has_option("authentication", "authType")
                and authentication_conf_file.get("authentication", "authType")
                == "Scripted"
                and authentication_conf_file.has_option(
                    "authentication", "authSettings"
                )
            ):
                auth_settings_stanza_name = authentication_conf_file.get(
                    "authentication", "authSettings"
                )
                if authentication_conf_file.has_section(auth_settings_stanza_name):
                    if (
                        not authentication_conf_file.has_option(
                            auth_settings_stanza_name, "python.version"
                        )
                        or authentication_conf_file.get(
                            auth_settings_stanza_name, "python.version"
                        )
                        != "python3"
                    ):

                        reporter_output = (
                            f"Scripted authentication [{auth_settings_stanza_name}] is defined, "
                            "and python.version should be explicitly set to python3."
                        )
                        section = authentication_conf_file.get_section(
                            auth_settings_stanza_name
                        )
                        reporter.fail(reporter_output, file_path, section.lineno)
                        # TODO: further verify the script's compatibility of python3 interpreter if applicable
                else:
                    reporter.warn(
                        f" Script authentication configuration for [{auth_settings_stanza_name}] is missing"
                    )

    else:
        reporter_output = "authentication.conf does not exist."
        reporter.not_applicable(reporter_output)
