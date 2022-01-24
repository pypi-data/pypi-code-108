# Copyright 2019 Splunk Inc. All rights reserved.

import logging
import os
import re

from . import inspected_file

logger = logging.getLogger(__name__)


class RegexMatcher(object):

    MESSAGE_LIMIT = 80

    def __init__(self, regex_bundle_list):
        self.__regex_bundle_list = regex_bundle_list
        for regex_bundle in self.__regex_bundle_list:
            assert isinstance(regex_bundle, RegexBundle), regex_bundle
        self.has_valid_files = False

    def match(self, string, regex_option=0):
        """return all match results in sorted order"""
        ans = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = re.compile(regex_bundle.general_regex_string, regex_option)
            result = re.finditer(pattern, string)
            for match_result in result:
                ans.append(self._get_match_result(regex_bundle, match_result))
        ans.sort()
        return ans

    def match_string_array(self, string_array, regex_option=0):
        """return all match results in (lineno, result) tuple and in sorted order"""
        ans = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = re.compile(regex_bundle.general_regex_string, regex_option)
            for index, string in enumerate(string_array):
                result = re.finditer(pattern, string)
                for match_result in result:
                    ans.append(
                        (index + 1, self._get_match_result(regex_bundle, match_result))
                    )
        ans.sort()
        return ans

    def match_file(self, filepath, regex_option=0, excluded_comments=True):
        """return all match results in (lineno, result) tuple and in sorted order"""
        if not os.path.exists(filepath):
            return []

        file_to_inspect = inspected_file.InspectedFile.factory(filepath)
        ans = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = regex_bundle.regex_string(filepath)
            matches = file_to_inspect.search_for_pattern(
                pattern, excluded_comments=excluded_comments, regex_option=regex_option
            )

            for fileref_output, file_match in matches:
                lineno = fileref_output.rsplit(":", 1)[1]
                ans.append(
                    (
                        int(lineno),
                        self._get_match_result(regex_bundle, file_match, filepath),
                    )
                )

        ans.sort()
        return ans

    def match_results_iterator(
        self, app_dir, file_iterator, regex_option=0, excluded_comments=True
    ):
        directory = _empty = object()
        for directory, filename, _ in file_iterator:
            absolute_path = os.path.join(app_dir, directory, filename)
            file_path = os.path.join(directory, filename)
            match_result = self.match_file(
                filepath=absolute_path,
                regex_option=regex_option,
                excluded_comments=excluded_comments,
            )
            result_dict = {}
            # dedup result in one line
            for lineno, result in match_result:
                if lineno not in result_dict:
                    result_dict[lineno] = set()
                result_dict[lineno].add(result)
            for lineno, result_set in result_dict.items():
                for result in result_set:
                    yield result, file_path, lineno

        if directory != _empty:
            self.has_valid_files = True

    def _get_match_result(self, regex_bundle, match_result, filepath=None):
        raw_result = match_result.group(0)
        if filepath is not None and not regex_bundle.check_if_result_truncated(
            filepath
        ):
            return raw_result
        if len(raw_result) <= self.MESSAGE_LIMIT:
            return raw_result

        # concatenate sub-groups together
        result = "...".join(
            filter(
                lambda group: len(group) <= self.MESSAGE_LIMIT, match_result.groups()
            )
        )
        # sub-groups are defined in regex
        if result != "":
            result = "..." + result + "..."
        else:
            result = raw_result[0 : self.MESSAGE_LIMIT] + "..."
        return result


class JSInsecureHttpRequestMatcher(RegexMatcher):
    def __init__(self):

        possible_insecure_http_request_regex_patterns = [
            RegexBundle(
                r"\w{1,10}\.open\s*\(\s*[\"\'](GET|POST)[\"\']\s*,\s*((?![\"\']https://)[\w.:/\-\"\']+).*?\)"
            ),
            RegexBundle(
                r"(\$|jQuery)\.(get|post|getJSON|getScript)\s*\(\s*((?![\"\']https://)[\w.:/\-\"\']+).*?\)"
            ),
            RegexBundle(
                r"(http|request|axios|superagent|fly|got)\.(get|post)\s*\(\s*((?![\"\']https://)[\w.:/\-\"\']+).*?\)"
            ),
            RegexBundle(r"(\$|jQuery)\.ajax(?![\w.])\s*[(]?"),
        ]
        super(JSInsecureHttpRequestMatcher, self).__init__(
            possible_insecure_http_request_regex_patterns
        )


class JSIFrameMatcher(RegexMatcher):
    def __init__(self):

        possible_iframe_regex_patterns = [
            RegexBundle(r'(<iframe[^>]*src=[\'"]([^\'">]*)[\'"][^>]*>)')
        ]
        super(JSIFrameMatcher, self).__init__(possible_iframe_regex_patterns)


class JSConsoleLogMatcher(RegexMatcher):
    def __init__(self):
        possible_console_log_regex_patterns = [
            RegexBundle(
                r"console.log\([^)]*(pass|passwd|password|token|auth|priv|access|secret|login|community|key|privpass)[^)]*\)"
            )
        ]
        super(JSConsoleLogMatcher, self).__init__(possible_console_log_regex_patterns)


class JSRemoteCodeExecutionMatcher(RegexMatcher):
    def __init__(self):

        # use {0,50} to avoid matching a very long eval string
        possible_remote_code_execution_regex_patterns = [
            RegexBundle(r"(\$|\w{1,10})\.globalEval\s*\([^)]{0,50}"),
            RegexBundle(r"eval\s*\([^)]{0,50}"),
        ]
        super(JSRemoteCodeExecutionMatcher, self).__init__(
            possible_remote_code_execution_regex_patterns
        )


class JSWeakEncryptionMatcher(RegexMatcher):
    def __init__(self):
        weak_encryption_regex_patterns = [
            RegexBundle(r"CryptoJS\s*\.\s*(DES\s*\.\s*encrypt|MD5|SHA1)")
        ]
        super(JSWeakEncryptionMatcher, self).__init__(weak_encryption_regex_patterns)


class JSUDPCommunicationMatcher(RegexMatcher):
    def __init__(self):
        udp_communication_regex_patterns = [
            RegexBundle(r"getUserMedia"),
            RegexBundle(r"RTCPeerConnection"),
            RegexBundle(r"UDPSocket"),
            RegexBundle(r"chrome.sockets.udp"),
        ]
        super(JSUDPCommunicationMatcher, self).__init__(
            udp_communication_regex_patterns
        )


class JSReflectedXSSMatcher(RegexMatcher):
    def __init__(self):
        reflected_xss_regex_patterns = [
            RegexBundle(
                r"<img[ ]+(dynsrc|lowsrc|src)\s*=\s*[\"\' ]javascript:(?!false)[^0].*?>"
            ),
            RegexBundle(
                r"<(bgsound|iframe|frame)[ ]+src\s*=\s*[\"\' ]javascript:(?!false)[^0].*?>"
            ),
            RegexBundle(r"<a\s*(on.*)\s*=.*?>"),
            RegexBundle(r'<img """><script>.*?</script>">'),
            RegexBundle(r"<img[ ]+(on.*?)\s*=.*?>"),
            RegexBundle(r"<(img|iframe)[ ]+src\s*=\s*#\s*(on.*)\s*=.*?>"),
            RegexBundle(r"<img[ ]+src\s*=\s*(on.*)\s*=.*?>"),
            RegexBundle(r"<img[ ]+src\s*=\s*/\s*onerror\s*=.*?>"),
            RegexBundle(
                r"<input[ ]+type\s*=\s*[\"\']image[\"\']\s*src\s*=\s*[\"\']javascript:(?!false)[^0].*?>"
            ),
            RegexBundle(
                r"<(body|table|td)[ ]+background\s*=\s*[\"\']javascript:(?!false)[^0].*?>"
            ),
            RegexBundle(r"<svg[ ]+onload\s*=.*?>"),
            RegexBundle(r"<body\s*ONLOAD\s*=.*?>"),
            RegexBundle(r"<br[ ]+size\s*=\s*[\"\']&\{.*?\}[\"\']>"),
            RegexBundle(r"<link[ ]+href\s*=\s*[\"\']javascript:(?!false)[^0].*?>"),
            RegexBundle(
                r"<div\s*style\s*=\s*[\"\']background-image:\s*url\(javascript:(?!false)[^0].*?>"
            ),
        ]
        super(JSReflectedXSSMatcher, self).__init__(reflected_xss_regex_patterns)


class ConfEndpointMatcher(RegexMatcher):
    def __init__(self):
        conf_endpoint_regex_patterns = [
            RegexBundle(r"servicesNS/\S*configs/\S*conf-\S*/\S*"),
            RegexBundle(r"services/configs/conf-\S*/\S*"),
            RegexBundle(r"services/properties/\S*/\S*"),
        ]
        super(ConfEndpointMatcher, self).__init__(conf_endpoint_regex_patterns)


class SecretDisclosureInAllFilesMatcher(RegexMatcher):
    def __init__(self):
        secret_patterns = [
            RegexBundle(
                r"(?i)https?://[^\"\'\s]*?(key|pass|pwd|token)[0-9a-z]*\=[^&\"\'\s]+"
            ),  # Secrets in the url
            RegexBundle(
                r"(?i)xox[pboa]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}"
            ),  # Slack Token
            RegexBundle(r"(?i)-----BEGIN RSA PRIVATE KEY-----"),  # RSA private key
            RegexBundle(
                r"(?i)-----BEGIN OPENSSH PRIVATE KEY-----"
            ),  # SSH (OPENSSH) private key
            RegexBundle(
                r"(?i)-----BEGIN DSA PRIVATE KEY-----"
            ),  # SSH (DSA) private key
            RegexBundle(r"(?i)-----BEGIN EC PRIVATE KEY-----"),  # SSH (EC) private key
            RegexBundle(
                r"(?i)-----BEGIN PGP PRIVATE KEY BLOCK-----"
            ),  # PGP private key block
            RegexBundle(
                r"(?i)f(ace)?b(ook)?.{0,10}=\s*[\'\"]EAA[0-9a-z]{180,}[\'\"]"
            ),  # Facebook user token
            RegexBundle(
                r"(?i)f(ace)?b(ook)?.{0,10}=\s*[\'\"]\d+\|[0-9a-z]+[\'\"]"
            ),  # Facebook app token
            RegexBundle(
                r"(?i)github.{0,10}=\s*[\'\"][0-9a-f]{40}[\'\"]"
            ),  # GitHub personal access token
            RegexBundle(
                r"(?i)\"client_secret\":\s*\"[a-zA-Z0-9-_]{24}\""
            ),  # Google Oauth
            RegexBundle(r"(?i)AKIA[0-9A-Z]{16}"),  # AWS API Key
            RegexBundle(
                r"(?i)heroku.*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
            ),
        ]  # Heroku API Key
        super(SecretDisclosureInAllFilesMatcher, self).__init__(secret_patterns)


class SecretDisclosureInNonPythonFilesMatcher(RegexMatcher):
    def __init__(self):
        bundle = RegexBundle(
            r"(?i).{0,22}(login|passwd|password|community|privpass|apikey)\s*=\s*[^\s]+"
        )
        bundle.exception(
            os.path.join("default", "props.conf"),
            r"(?i).*(login|passwd|password|community|privpass|apikey)\s*=\s*[^\s]+",
            False,
        )
        bundle.exception(
            os.path.join("default", "transforms.conf"),
            r"(?i).*(login|passwd|password|community|privpass|apikey)\s*=\s*[^\s]+",
            False,
        )
        secret_patterns = [bundle]  # General secret
        super(SecretDisclosureInNonPythonFilesMatcher, self).__init__(secret_patterns)


class JSTelemetryEndpointMatcher(RegexMatcher):
    def __init__(self):

        possible_telemetry_endpoint_regex_patterns = [
            # https://<host>:<management_port>/servicesNS/<user_context>/<app_context>/telemetry-metric
            RegexBundle(r"(?:https|http)://\S*/servicesNS/\S*/telemetry-metric"),
            # http://<host>:<splunkweb_port>/<locale>/splunkd/__raw/servicesNS/<user_context>/<app_context>/telemetry-metric
            RegexBundle(
                r"(?:https|http)://\S*/splunkd/__raw/servicesNS/\S*/telemetry-metric"
            ),
        ]
        super(JSTelemetryEndpointMatcher, self).__init__(
            possible_telemetry_endpoint_regex_patterns
        )


class JSTelemetryMetricsMatcher(RegexMatcher):
    def __init__(self):
        telemetry_regex_patterns = [
            RegexBundle(r"window\._splunk_metrics_events\.push\s*"),
            RegexBundle(r"(splunk_metrics|\w+)\.trackEvent\s*"),
            RegexBundle(r"(splunk_metrics|\w+)\.init\([^}]*logging.*true\)"),
            RegexBundle(r"(splunk_metrics|\w+)\.init\([^}]*log.*\)"),
        ]
        super(JSTelemetryMetricsMatcher, self).__init__(telemetry_regex_patterns)


class RegexBundle(object):
    def __init__(self, regex_string):
        self._regex_string = regex_string
        self._exception_dict = {}

    @property
    def general_regex_string(self):
        return self._regex_string

    def exception(self, filepath, regex_string, is_truncated=True):
        self._exception_dict[filepath] = (regex_string, is_truncated)

    def regex_string(self, filepath):
        for suffix, (regex_string, _) in self._exception_dict.items():
            if filepath.endswith(suffix):
                return regex_string
        return self._regex_string

    def check_if_result_truncated(self, filepath):
        for suffix, (_, is_truncated) in self._exception_dict.items():
            if filepath.endswith(suffix):
                return is_truncated
        return True
