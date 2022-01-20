# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Security vulnerabilities
"""
import logging
import os
import platform
import re

import splunk_appinspect
from splunk_appinspect.check_routine.python_ast_searcher.ast_searcher import AstSearcher
from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common import metadata_consts
from splunk_appinspect.python_modules_metadata.python_modules_metadata_store import (
    metadata_store,
)
from splunk_appinspect.regex_matcher import (
    SecretDisclosureInAllFilesMatcher,
    SecretDisclosureInNonPythonFilesMatcher,
)

logger = logging.getLogger(__name__)
report_display_order = 5

potentially_dangerous_windows_filetypes = [
    ".cmd",
    ".ps1",
    ".bat",
    ".ps2",
    ".ws",
    ".wsf",
    ".psc1",
    ".psc2",
]


@splunk_appinspect.tags("splunk_appinspect", "security", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_pexpect(app, reporter):
    """Check for use of `pexpect` to ensure it is only controlling app
    processes.
    """
    for match in app.search_for_pattern("pexpect.run", types=[".py"]):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Possible use of pexpect- detected in {match[0]}. "
            f"File: {filename}, Line: {line}."
        )
        reporter.manual_check(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_secret_disclosure(app, reporter):
    """Check for passwords and secrets."""
    # the messages in props.conf or transforms.conf need to filter by _secret_disclosure_commands_whitelist
    # extract the messages with the structure: {file_path: {lineno: [result1, result2]}}
    messages_in_special_files = {}
    special_files = [
        os.path.join("default", "props.conf"),
        os.path.join("default", "transforms.conf"),
    ]

    # general regex patterns
    matcher = SecretDisclosureInAllFilesMatcher()
    for result, file_path, lineno in matcher.match_results_iterator(
        app.app_dir, app.iterate_files()
    ):
        # extract the messages in props.conf or transforms.conf and combine them
        if file_path in special_files:
            _combine_messages_in_special_files(
                file_path, lineno, result, messages_in_special_files
            )
            continue
        if _secret_disclosure_values_whitelist(result):
            continue
        reporter_output = (
            "The following line will be inspected during code review. "
            "Possible secret disclosure found."
            f" Match: {result}"
            f" File: {file_path}"
            f" Line: {lineno}"
        )
        reporter.manual_check(reporter_output, file_path, lineno)

    # regex patterns target non-python files, python files would be covered in check_python_files
    matcher = SecretDisclosureInNonPythonFilesMatcher()
    for result, file_path, lineno in matcher.match_results_iterator(
        app.app_dir, app.iterate_files(excluded_types=[".py"])
    ):
        # extract the messages in props.conf or transforms.conf and combine them
        if file_path in special_files:
            _combine_messages_in_special_files(
                file_path, lineno, result, messages_in_special_files
            )
            continue
        if _secret_disclosure_values_whitelist(result):
            continue
        reporter_output = (
            "The following line will be inspected during code review."
            "Possible secret disclosure found."
            f" Match: {result}"
            f" File: {file_path}"
            f" Line: {lineno}"
        )
        reporter.manual_check(reporter_output, file_path, lineno)

    # process the messages_in_props_or_transforms_file: {file_path: {lineno: [result1, result2]}}
    for file_path, messages in messages_in_special_files.items():
        for lineno, results in messages.items():
            if _secret_disclosure_commands_whitelist(file_path, results):
                continue
            for result in results:
                if _secret_disclosure_values_whitelist(result):
                    continue
                reporter_output = (
                    "The following line will be inspected during code review."
                    "Possible secret disclosure found."
                    f" Match: {result}"
                    f" File: {file_path}"
                    f" Line: {lineno}"
                )
                reporter.manual_check(reporter_output, file_path, lineno)


def _secret_disclosure_values_whitelist(line_message):
    """
    :param line_message: the line message matched by secret_patterns regex in check_for_secret_disclosure
    :return: True or False
    """
    # if the secret credential is equal to following values, then pass
    values_whitelist = [
        "value",
        "string",
        "not_set",
        "str",
        "password",
        "enabled",
        "true",
        "false",
        "Enter",
        "YourSecretPassword",
        "YOUR_ADMIN_PASSWORD",
        "undefined",
        "received",
        "self",
        "changeme",
        "Heavy",
        "null",
        "0+",
        "x+",
        "X+",
        r"\*+",
        r"\^+",
    ]
    # (?i) case insensitive
    values_patterns = (
        r"((?i)((?:(key|pass|pwd|token|login|passwd|password|community|privpass))[ ]{0,10}=[ ]{0,10}((<|\"|\'|\\\"|\\\')?(%s)(>|\"|\'|\\\"|\\\')?)$))"
        % ("|".join(values_whitelist))
    )

    if re.search(values_patterns, line_message):
        return True

    return False


def _secret_disclosure_commands_whitelist(file_path, messages):
    """
    :param file_path: the file path of this matched line
    :param messages: the message list in one line matched by secret_patterns regex in check_for_secret_disclosure
                     the structure is [message1, message2]
    :return: True or False
    """

    # if the line begins with following commands in props.conf and transforms.conf, then pass
    # In props.conf e.g. SEDCMD-<class>, EXTRACT-<classs>, REPORT-<class>, TRANSFORMS-<class>, LOOKUP-<class>,
    # EVAL-<class>, FIELDALIAS-<class>
    # In transforms.conf, e.g. REGEX=, FORMAT=

    commands_whitelist_in_props_file = [
        "SEDCMD-",
        "EXTRACT-",
        "REPORT-",
        "TRANSFORMS-",
        "LOOKUP[-|_]?",
        "lookup[-|_]?",
        "EVAL-",
        "FIELDALIAS-",
    ]
    commands_whitelist_in_transforms_file = ["REGEX[ ]*=", "FORMAT[ ]*="]

    if file_path == os.path.join("default", "props.conf"):
        commands_patterns = r"(^(?=%s))" % ("|".join(commands_whitelist_in_props_file))
    elif file_path == os.path.join("default", "transforms.conf"):
        commands_patterns = r"(^(?=%s))" % (
            "|".join(commands_whitelist_in_transforms_file)
        )
    else:
        # the filename is not valid
        return False

    for message in messages:
        if re.search(commands_patterns, message):
            return True

    return False


def _combine_messages_in_special_files(
    file_path, lineno, result, messages_in_special_files
):
    """Combine the messages and update the messages_in_special_files
    :param file_path:
    :param lineno:
    :param result:
    :param messages_in_special_files: the structure is {file_path: {lineno: [result1, result2]}}
    :return: Update the messages_in_special_files
    """
    if file_path in messages_in_special_files.keys():
        if lineno in messages_in_special_files[file_path].keys():
            messages_in_special_files[file_path][lineno].append(result)
        else:
            messages_in_special_files[file_path][lineno] = [result]
    else:
        message = {lineno: [result]}
        messages_in_special_files[file_path] = message


@splunk_appinspect.tags("splunk_appinspect", "security", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_for_sensitive_info_in_url(app, reporter):
    """Check for sensitive information being exposed in transit via URL query string parameters"""
    sensitive_info_patterns = (
        r"((?i)[ \f\r\t\v]*[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*[\"\']?https?://[^\"\'\s]*?(key|pass|pwd|token)[0-9a-z]*=[^&\"\'\s]+[\"\']?|"  # Single line url
        r"[ \f\r\t\v]*[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*([\"\']\{\}://\{\}:\{\}@\{\}:\{\}[\"\'])\.format\([^\)]*(key|password|pass|pwd|token|cridential|secret|login|auth)[^\)]*\))"
    )  # Multi line url

    sensitive_info_patterns_for_report = (
        r"((?i)[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*[\"\']?https?://[^\"\'\s]*?(key|pass|pwd|token)[0-9a-z]*=[^&\"\'\s]+[\"\']?|"  # Single line url
        r"[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*([\"\']\{\}://\{\}:\{\}@\{\}:\{\}[\"\'])\.format\([^\)]*(key|password|pass|pwd|token|cridential|secret|login|auth)[^\)]*\))"
    )  # Multi line url

    for match in app.search_for_crossline_pattern(
        pattern=sensitive_info_patterns, cross_line=5
    ):
        filename, line = match[0].rsplit(":", 1)
        # handle massage
        for rx in [re.compile(p) for p in [sensitive_info_patterns_for_report]]:
            for p_match in rx.finditer(match[1].group()):
                description = p_match.group()
                reporter_output = (
                    f"Possible sensitive information being exposed via URL in {match[0]}: {description}."
                    f" File: {filename}, Line: {line}."
                )
                reporter.warn(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_vbs_command_injection(app, reporter):
    """Check for command injection in VBS files."""
    for match in app.search_for_pattern("Shell.*Exec", types=[".vbs"]):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Possible command injection in {match[0]}: {match[1].group()}. "
            f"File: {filename}, Line: {line}."
        )
        reporter.manual_check(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_command_injection_through_env_vars(app, reporter):
    """Check for command injection through environment variables."""
    for match in app.search_for_pattern(
        "start.*%", types=potentially_dangerous_windows_filetypes
    ):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Possible command injection in {match[0]}: {match[1].group()}. "
            f"File: {filename}, Line: {line}."
        )
        reporter.manual_check(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "cloud", "manual", "ast")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_insecure_http_calls_in_python(app, reporter):
    """Check for insecure HTTP calls in Python."""
    report_template = (
        "Possible insecure HTTP Connection."
        " Match: {}"
        " Positional arguments, {}; Keyword arguments, {}"
    )

    query = (
        metadata_store.query()
        .tag(metadata_consts.TagConsts.HTTP_CONNECTION)
        .python_compatible()
    )

    def is_secure_var(var, ast_info):
        variable = ast_info.get_variable_details(var)
        return AstVariable.is_string(variable) and variable.variable_value.startswith(
            "https"
        )

    def is_arg_secure(call_node, ast_info):
        # check if https prefix is found
        is_secure = False
        # only pay attention to first two arguments, url will always be included
        for arg in call_node.args[:2]:
            is_secure = is_secure_var(arg, ast_info)
            if is_secure:
                break
        return is_secure

    def is_keyword_secure(call_node, ast_info):
        is_secure = False
        possible_argument_keys = {"url", "fullurl", "host"}
        for keyword in call_node.keywords:
            if keyword.arg in possible_argument_keys:
                is_secure = is_secure_var(keyword.value, ast_info)
                if is_secure:
                    break
        return is_secure

    def is_arg_secure_or_keyword_secure(call_node, ast_info):
        return not is_arg_secure(call_node, ast_info) and not is_keyword_secure(
            call_node, ast_info
        )

    components = query.functions() + query.classes()
    files_with_results = AstSearcher(app.python_analyzer_client).search(
        components, node_filter=is_arg_secure_or_keyword_secure, get_func_params=True
    )
    reporter.ast_manual_check(report_template, files_with_results)


@splunk_appinspect.tags("splunk_appinspect", "security", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_stacktrace_returned_to_user(app, reporter):
    """Check that stack traces are not being returned to an end user."""
    for match in app.search_for_pattern("format_exc", types=[".py"]):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Stacktrace being formatted in {match[0]}: {match[1].group()}. "
            f"File: {filename}, Line: {line}."
        )
        reporter.manual_check(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_environment_variable_use_in_python(app, reporter):
    """Check for environment variable manipulation and attempts to monitor
    sensitive environment variables."""
    # Catch `os.environ.get(` or `os.getenv(` but allow for `"SPLUNK_HOME` or
    # `'SPLUNK_HOME`
    # Catch `os.environ` other than `os.environ.get` (which is covered above)
    env_manual_regex = (
        r"((os[\s]*\.[\s]*environ[\s]*\.[\s]*get)"
        r"|(os[\s]*\.[\s]*getenv))"
        r"(?![\s]*\([\s]*[\'\"]SPLUNK\_HOME)"
        r"|(os[\s]*\.[\s]*environ(?![\s]*\.[\s]*get))"
    )
    for match in app.search_for_pattern(env_manual_regex, types=[".py"]):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Environment variable being used in {match[0]}: {match[1].group()}. "
            f"File: {filename}, Line: {line}."
        )
        reporter.manual_check(reporter_output, filename, line)
    # Fail for use of `os.putenv` / `os.unsetenv` in any scenario
    env_set_regex = r"(os[\s]*\.[\s]*putenv|os[\s]*\.[\s]*unsetenv)"
    for match in app.search_for_pattern(env_set_regex, types=[".py"]):
        filename, line = match[0].rsplit(":", 1)
        reporter_output = (
            f"Environment variable manipulation detected in {match[0]}: {match[1].group()}."
            f"File: {filename}, Line: {line}."
        )
        reporter.fail(reporter_output, filename, line)


@splunk_appinspect.tags("splunk_appinspect", "security", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.5.2")
def check_symlink_outside_app(app, reporter):
    """Check no symlink points to the file outside this app"""
    if platform.system() == "Windows":
        reporter_output = "Please run AppInspect using another OS to enable this check. Or use AppInspect API."
        reporter.warn(reporter_output)
    else:
        for basedir, file, _ in app.iterate_files():
            app_file_path = os.path.join(basedir, file)
            full_file_path = app.get_filename(app_file_path)
            # it is a symbolic link file
            if os.path.islink(full_file_path):
                # For python 2.x, os.path.islink will always return False in windows
                # both of them are absolute paths
                link_to_absolute_path = os.path.abspath(
                    os.path.realpath(full_file_path)
                )
                app_root_dir = app.app_dir
                # link to outer path
                if not link_to_absolute_path.startswith(app_root_dir):
                    reporter_output = (
                        f"Link file found in path: {full_file_path}. The file links to a path "
                        f"outside of this app, the link path is: {link_to_absolute_path}. "
                        f"File: {app_file_path}"
                    )
                    reporter.fail(reporter_output, app_file_path)
