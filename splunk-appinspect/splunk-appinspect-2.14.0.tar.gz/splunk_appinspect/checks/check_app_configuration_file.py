# Copyright 2019 Splunk Inc. All rights reserved.

"""
### App.conf standards

The **app.conf** file located at **default/app.conf** provides key application information and branding. For more, see [app.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Appconf).
"""

import logging
import os
import re

import splunk_appinspect
from splunk_appinspect.app_util import AppVersionNumberMatcher
from splunk_appinspect.splunk import normalizeBoolean
from splunk_appinspect.splunk_defined_conf_file_list import SPLUNK_DEFINED_CONFS

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect", "appapproval")
@splunk_appinspect.cert_version(min="1.0.0")
def check_app_version(app, reporter):
    """Check that the `app.conf` contains an application version number in the
    [launcher] stanza.
    """
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        config = app.get_config("app.conf")
        matcher = AppVersionNumberMatcher()

        try:
            config.has_option("launcher", "version")
            version = config.get("launcher", "version")
            if not matcher.match(version):
                lineno = config.get_section("launcher").get_option("version").lineno
                reporter_output = (
                    "Major, minor, build version numbering "
                    f"is required. File: {filename}, Line: {lineno}."
                )
                reporter.fail(reporter_output, filename, lineno)

        except splunk_appinspect.configuration_file.NoOptionError:
            lineno = config.get_section("launcher").lineno
            reporter_output = (
                "No version specified in launcher section "
                f"of app.conf. File: {filename}, Line: {lineno}."
            )
            reporter.fail(reporter_output, filename, lineno)

        except splunk_appinspect.configuration_file.NoSectionError:
            reporter_output = f"No launcher section found in app.conf. File: {filename}"
            reporter.fail(reporter_output, file_name=filename)
    else:
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.1.20")
def check_that_setup_has_not_been_performed(app, reporter):
    """Check that `default/app.conf` setting `is_configured` = False."""
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        app_conf = app.app_conf()
        if app_conf.has_section("install") and app_conf.has_option(
            "install", "is_configured"
        ):
            # Sets to either 1 or 0
            is_configured = normalizeBoolean(app_conf.get("install", "is_configured"))
            if is_configured:
                lineno = (
                    app_conf.get_section("install").get_option("is_configured").lineno
                )
                reporter_output = (
                    "The app.conf [install] stanza has the"
                    " `is_configured` property set to true."
                    " This property indicates that a setup was already"
                    f" performed. File: {filename}, Line: {lineno}."
                )
                reporter.fail(reporter_output, filename, lineno)
            else:
                pass  # Pass - The property is true
        else:
            pass  # Pass - The stanza or property does not exist.
    else:
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "self-service", "private_app")
@splunk_appinspect.cert_version(min="2.0.1")
def check_for_valid_package_id(app, reporter):
    """
    Check that the [package] stanza in app.conf has a valid `id` value.
    See https://docs.splunk.com/Documentation/Splunk/latest/Admin/Appconf for details.
    """
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        app_conf = app.app_conf()
        if app_conf.has_section("package"):
            package_configuration_section = app_conf.get_section("package")
            if package_configuration_section.has_option("id"):
                package_id = package_configuration_section.get_option("id")
                lineno = package_configuration_section.get_option("id").lineno
                if not _is_package_id_valid(package_id):  # with invalid package id
                    reporter_output = (
                        f"The app.conf [package] stanza's has an invalide 'id' property: {package_id.value}."
                        " For the `id` property, it must contain only letters, numbers, `.` (dot),"
                        " and `_` (underscore) characters, and can not endwith a dot character."
                        " Besides, some reserved names are prohibited."
                        " See https://docs.splunk.com/Documentation/Splunk/7.3.1/Admin/Appconf for details."
                        f" File: {filename}, Line: {lineno}."
                    )
                    reporter.fail(reporter_output, filename, lineno)

                elif _is_package_id_with_hyphen(package_id):  # with '-' in package id
                    reporter_output = (
                        f"The app.conf [package] stanza's has 'id' property: {package_id.value},"
                        " while '-' is not recommended. See https://docs.splunk.com/Documentation/Splunk/7.3.1/Admin/Appconf"
                        f" for more details. File: {filename}, Line: {lineno}."
                    )
                    reporter.warn(reporter_output, filename, lineno)
            else:
                reporter_output = "No `id` property under `package` section was detected in `default/app.conf`."
                reporter.not_applicable(reporter_output)
        else:
            reporter_output = "No `package` section was detected in `default/app.conf`."
            reporter.not_applicable(reporter_output)
    else:
        reporter_output = "No `default/app.conf` file was detected."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect")
@splunk_appinspect.cert_version(min="1.6.0")
def check_for_invalid_app_names(app, reporter):
    """Check that `default/app.conf` has `author = <some words are not about Splunk>` must not
    has attributes `label` or `description` with values of `Splunk App for XXXX`.
    """
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        app_conf = app.app_conf()
        is_author_splunk = _is_author_splunk(app_conf)
        if app_conf.has_option("ui", "label"):
            name = app_conf.get("ui", "label")
            if _is_with_value_of_splunk_app_for(name) and not is_author_splunk:
                lineno = app_conf.get_section("ui").get_option("label").lineno
                reporter_output = (
                    "For the app.conf [ui] stanza's 'label' attribute,"
                    " names of community-built apps must not start with 'Splunk'."
                    " For example 'Splunk app for Awesome' is inappropriate,"
                    f" but 'Awesome app for Splunk' is OK. File: {filename}, Line: {lineno}."
                )
                reporter.fail(reporter_output, filename, lineno)
        if app_conf.has_option("launcher", "description"):
            name = app_conf.get("launcher", "description")
            if _is_with_value_of_splunk_app_for(name) and not is_author_splunk:
                lineno = (
                    app_conf.get_section("launcher").get_option("description").lineno
                )
                reporter_output = (
                    "For the app.conf [launcher] stanza's 'description' attribute,"
                    " apps built by 3rd parties should not have names starting with Splunk."
                    " For example 'Splunk app for Awesome' is inappropriate,"
                    f" but 'Awesome app for Splunk' is OK. File: {filename}, Line: {lineno}."
                )
                reporter.fail(reporter_output, filename, lineno)
    else:
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)


def _is_with_value_of_splunk_app_for(name):
    # the regex expression is for searching:
    # "splunk (addon|add on|add-on|app)s for"
    return bool(
        re.search(r"splunk\s*(add(\s*|-*)on|app)(s*)\s*for", name, re.IGNORECASE)
    )


def _is_author_splunk(app_conf):
    if app_conf.has_option("launcher", "author"):
        if re.search(r"splunk", app_conf.get("launcher", "author"), re.IGNORECASE):
            return True
    for name in app_conf.section_names():
        if re.search(r"author=", name):
            if re.search(r"splunk", name, re.IGNORECASE):
                return True

            if app_conf.has_option(name, "company"):
                return bool(
                    re.search(r"splunk", app_conf.get(name, "company"), re.IGNORECASE)
                )
    return False


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.0")
def check_no_install_source_checksum(app, reporter):
    """Check in `default/app.conf`, install_source_checksum/install_source_local_checksum not be set explicitly."""
    stanz_black_list = ["install_source_checksum", "install_source_local_checksum"]
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        app_conf = app.app_conf()
        if app_conf.has_section("install"):
            for stanza in stanz_black_list:
                if app_conf.has_option("install", stanza):
                    if app_conf.get("install", stanza):
                        lineno = (
                            app_conf.get_section("install").get_option(stanza).lineno
                        )
                        reporter_output = (
                            f"For the app.conf [install] stanza's `{stanza}` attribute,"
                            " it records a checksum of the tarball from which a given app was installed"
                            " or a given app's local configuration was installed."
                            " Splunk Enterprise will automatically populate this value during installation."
                            " Developers should *not* set this value explicitly within their app!"
                            f" File: {filename}, Line: {lineno}."
                        )
                        reporter.warn(reporter_output, filename, lineno)
                    else:
                        pass  # Pass - The property is empty.
                else:
                    pass  # Pass - The property does not exist
        else:
            pass  # Pass - The stanza does not exist.
    else:
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.7.2")
def check_for_trigger_stanza(app, reporter):
    """Check that `default/app.conf` doesn't have a `reload.<CONF_FILE>`, where CONF_FILE is
    a non-custom conf. (https://docs.splunk.com/Documentation/Splunk/7.3.0/Admin/Appconf#.5Btriggers.5D)
    """
    if app.file_exists("default", "app.conf"):
        filename = os.path.join("default", "app.conf")
        app_conf = app.app_conf()

        if not app_conf.has_section("triggers"):
            return

        settings = app_conf.get_section("triggers").settings()
        default_meta_path = os.path.join("metadata", "default.meta")
        conf_permissions = (
            _get_conf_permissions(app.get_meta("default.meta"))
            if app.file_exists(default_meta_path)
            else {}
        )

        for conf_name, lineno in _get_reloaded_splunk_confs(settings):
            if _is_exported(conf_name, conf_permissions):
                reporter_output = (
                    f"{conf_name}.conf is a Splunk defined conf, which should not "
                    "be configured in [trigger] stanza. Per the documentation, "
                    "it should be configured only for custom config file. "
                    "Please remove this line."
                )
                reporter.fail(reporter_output, filename, lineno)
            else:
                reporter_output = (
                    f"{conf_name}.conf is a Splunk defined conf, which should not "
                    "be configured in [trigger] stanza. Per the documentation, "
                    "it should be configured only for custom config file. "
                    f"However, the {conf_name}.conf is not shared with other apps. "
                    "Suggest to remove this line."
                )
                reporter.warn(reporter_output, filename, lineno)
    else:
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="2.3.0")
def check_for_valid_ui_label(app, reporter):
    """Check that the `app.conf` contains a label key value pair in the
    [ui] stanza and the length is between 5 and 80 characters inclusive.
    """
    ## return not_applicable if app.conf does not exist
    if not app.file_exists("default", "app.conf"):
        reporter_output = "`default/app.conf` does not exist."
        reporter.not_applicable(reporter_output)
        return

    ## return not_applicable if ui stanza does not exist
    app_config = app.get_config("app.conf")
    if not app_config.has_section("ui"):
        reporter_output = "`default/app.conf` does not contain [ui] stanza."
        reporter.not_applicable(reporter_output)
        return

    ## return warning if label field does not exist in ui stanza
    ui_section = app_config.get_section("ui")
    filepath = os.path.join("default", "app.conf")
    if not ui_section.has_option("label"):
        reporter_output = f"`label` is required in [ui] stanza. File: {filepath}, Line: {ui_section.lineno}."
        reporter.warn(reporter_output, filepath, ui_section.lineno)
        return

    label_option = ui_section.get_option("label")
    if len(label_option.value) < 5 or len(label_option.value) > 80:
        reporter_output = (
            "The length of `label` field under [ui] stanza should between"
            f" 5 to 80 characters. File: {filepath}, Line: {label_option.lineno}."
        )
        reporter.warn(reporter_output, filepath, label_option.lineno)
        return


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
def check_reload_trigger_for_all_custom_confs(app, reporter):
    """Check that custom conf files have a corresponding reload trigger in app.conf

    Without a reload trigger the app will request a restart on any change to the conf file,
    which may be a negative experience for end-users.
    """

    # Get all custom confs
    custom_confs = []
    for directory, filename, _ in app.iterate_files(
        types=[".conf"], basedir=["default", "local"]
    ):
        if filename not in SPLUNK_DEFINED_CONFS:
            custom_confs.append(filename)

    # Pass the check if there are no custom confs
    if not custom_confs:
        return

    # Get the app config
    app_conf = app.app_conf()
    if not app_conf.has_section("triggers"):
        reporter.fail(
            f"App contains custom conf(s) {custom_confs} but does not have a [triggers] stanza in app.conf. "
            f"Without a reload trigger the app will request a restart on any change to the conf file, "
            f"which may be a negative experience for end-users."
        )
        return

    # Check that all the custom confs have a reload trigger
    # e.g. "banana.conf" -> "reload.banana" in app.conf
    for custom_conf in custom_confs:
        reload_option_name = f"reload.{os.path.splitext(custom_conf)[0]}"
        if not app_conf.has_option("triggers", reload_option_name):
            reporter.fail(
                f"Custom conf file {custom_conf} does not have a reload trigger in app.conf. "
                f"Without a reload trigger the app will request a restart on any change to the conf file, "
                f"which may be a negative experience for end-users."
            )


def _get_conf_permissions(default_meta):
    conf_permissions = {}
    meta_stanza_pattern = r"(?=\/).*"
    for section in default_meta.sections():
        name = re.sub(meta_stanza_pattern, "", section.name) or "default"
        is_exported = (
            section.has_option("export")
            and section.get_option("export").value == "system"
        )
        conf_permissions[name] = is_exported
    return conf_permissions


def _get_reloaded_splunk_confs(settings):
    splunk_conf_whitelist = ["passwords.conf"]
    reload_pattern = r"^reload\."
    for setting in settings:
        if re.match(reload_pattern, setting.name):
            conf_name = re.sub(reload_pattern, "", setting.name)
            conf_file_name = f"{conf_name}.conf"
            if (
                conf_file_name in SPLUNK_DEFINED_CONFS
                and conf_file_name not in splunk_conf_whitelist
            ):
                yield conf_name, setting.lineno


def _is_exported(conf_name, conf_permissions):
    if conf_name in conf_permissions:
        return conf_permissions[conf_name]

    default_stanza = "default"
    if default_stanza in conf_permissions:
        return conf_permissions[default_stanza]

    return False


def _is_package_id_with_hyphen(package_id):
    """Check that if package id contains '-'"""
    return "-" in package_id.value


def _is_package_id_valid(package_id):
    """
    Check rules for package id:
        1. must contain only letters, numbers, "." (dot), and "_" (underscore) characters.
           Besides, '-' should be add into the white list, see https://jira.splunk.com/browse/ACD-3636.
        2. must not end with a dot character
        3. must not be any of the following names: CON, PRN, AUX, NUL,
           COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9,
           LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9
    Best practice:
        1. do not endwith '.tar', '.tgz', '.tar.gz' and '.spl'
    """
    blcak_list = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]

    # check for rule 1
    pattern = re.compile(r"[^0-9a-zA-Z_.-]")
    results = re.findall(pattern, package_id.value)
    if results:
        return False
    # check for rule 2 and best practice
    if package_id.value.endswith((".", ".tar", ".tar.gz", ".tgz", ".spl")):
        return False
    # check for rule 3
    if package_id.value in blcak_list:
        return False

    return True
