import base64
import re

from collections import Counter
from copy import deepcopy
from re import sub
from datetime import timedelta, date, datetime
from types import GeneratorType
from urllib.parse import urlparse
from requests import Response


def remove_dupes_but_take_higher_access(my_list):
    """
        Deduping function for keeping members with higher access
    """
    already_found = {}
    new_list = []
    for d in my_list:
        obj_id = d["id"]
        if already_found.get(obj_id):
            if already_found[obj_id]["access_level"] < d["access_level"]:
                c = deepcopy(d)
                c["index"] = already_found[obj_id]["index"]
                new_list[already_found[obj_id]["index"]] = c
                already_found[obj_id] = c
        else:
            already_found[obj_id] = deepcopy(d)
            new_list.append(d)
            already_found[obj_id]["index"] = len(new_list) - 1
    return new_list


def expiration_date():
    return (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')


def parse_query_params(params):
    query_params_string = ""
    query_params_list = []
    for p in params:
        if params.get(p, None) is not None:
            query_params_list.append("%s=%s" % (p, str(params[p])))

    if len(query_params_list) > 0:
        query_params_string = "?%s" % "&".join(query_params_list)

    return query_params_string


def input_generator(params):
    for param in params:
        yield param


def get_dry_log(dry_run=True):
    return "DRY-RUN: " if dry_run else ""


def get_rollback_log(rollback=False):
    return "Rollback: " if rollback else ""


def pretty_print_key(s):
    return " ".join(w.capitalize() for w in s.split("_"))


def is_error_message_present(response):
    errors = ["message", "errors", "error"]
    if isinstance(response, Response):
        response = safe_json_response(response)
    if isinstance(response, (GeneratorType, map, filter)):
        response = list(response)
    if isinstance(response, list) and response and response[0] in errors:
        return True, response
    if isinstance(response, dict) and any(r in response for r in errors):
        return True, response
    if isinstance(response, str) and response in errors:
        return True, response
    return False, response


def get_timedelta(timestamp):
    """
    Get timedelta between provided timestamp and current time

        :param timestamp: A timestamp string
        :return: timedelta between provided timestamp and datetime.now() in hours
    """
    try:
        created_at = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        created_at = datetime.strptime(
            timestamp.split(".")[0], '%Y-%m-%dT%H:%M:%S')
    now = datetime.now()
    return (now - created_at).days * 24


def validate_name(name, log=None):
    """
    Validate group and project names to satisfy the following criteria:
    Name can only contain letters, digits, emojis, '_', '.', dash, space.
    It must start with letter, digit, emoji or '_'.
    """
    valid = " ".join(sub(r"[^\U00010000-\U0010ffff\w\_\-\. ]",
                         " ", name.lstrip("-").lstrip(".")).split())
    if name != valid:
        output = f"Renaming invalid name '{name}' -> '{valid}'"
        log.warning(output) if log else print(output)
    return valid


def generate_audit_log_message(req_type, message, url, data=None):
    try:
        return "{0}enerating {1} request to {2}{3}".format(
            "{} by g".format(message) if message else "G",
            req_type,
            url,
            " with data: {}".format(data) if data else "")
    except TypeError as te:
        return f"Message formatting ERROR ({te}). No specific message generated. Generating {req_type} request to {url}"


def safe_json_response(response):
    """
        Helper method to handle getting valid JSON safely. If valid JSON cannot be returned, it returns none.
    """
    if response is not None:
        try:
            if isinstance(response, GeneratorType):
                return list(response)
            return response.json()
        except ValueError:
            return None
    return None


def get_duplicate_paths(data, are_projects=True):
    """
        Legacy GL versions had case insensitive paths, which on newer GL versions are seen as duplicates
    """
    paths = [x.get("path_with_namespace", "").lower() if are_projects else x.get(
        "full_path", "").lower() for x in data]
    return [i for i, c in Counter(paths).items() if c > 1]


def strip_netloc(s):
    return urlparse(s).netloc


def strip_scheme(s):
    return urlparse(s).scheme


def get_decoded_string_from_b64_response_content(response):
    """
        Takes a web response, returns the decoded *string* of the content, not byte object
    """
    if j := safe_json_response(response):
        content = j.get("content", "")
        if content is not None and str("content").strip() != "":
            return base64.b64decode(content).decode()
    return None


def do_yml_sub(yml_file, pattern, replace_with):
    """
        Does a regex subn and returns the entity
    """
    return re.subn(pattern, replace_with, yml_file)
