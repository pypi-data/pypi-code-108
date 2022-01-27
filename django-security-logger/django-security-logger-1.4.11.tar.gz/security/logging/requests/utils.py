import re
import json

from urllib.parse import parse_qs, urlparse

from json import JSONDecodeError

from django.template.defaultfilters import truncatechars
from django.utils.encoding import force_text

from security.config import settings
from security.utils import remove_nul_from_string


def is_base_collection(v):
    return isinstance(v, (list, tuple, set))


def get_headers(request):
    regex = re.compile('^HTTP_')
    return dict((regex.sub('', header), value) for (header, value)
                in request.META.items() if header.startswith('HTTP_'))


def regex_sub_groups_global(pattern, repl, string):
    """
    Globally replace all groups inside pattern with `repl`.
    If `pattern` doesn't have groups the whole match is replaced.
    """
    for search in reversed(list(re.finditer(pattern, string))):
        for i in range(len(search.groups()), 0 if search.groups() else -1, -1):
            start, end = search.span(i)
            string = string[:start] + repl + string[end:]
    return string


def flat_params(params):
    return {
        k: v[0] if is_base_collection(v) and len(v) == 1 else v
        for k, v in params.items()
    }


def list_params(params):
    return {
        k: list(v) if is_base_collection(v) else [v]
        for k, v in params.items()
    }


def get_logged_params(url):
    return flat_params(parse_qs(urlparse(url).query))


def hide_sensitive_data_body(content):
    if settings.HIDE_SENSITIVE_DATA:
        for pattern in settings.HIDE_SENSITIVE_DATA_PATTERNS.get('BODY', ()):
            content = regex_sub_groups_global(pattern, settings.SENSITIVE_DATA_REPLACEMENT, content)
    return content


def hide_sensitive_data_headers(headers):
    if settings.HIDE_SENSITIVE_DATA:
        headers = dict(headers)
        for pattern in settings.HIDE_SENSITIVE_DATA_PATTERNS.get('HEADERS', ()):
            for header_name, header in headers.items():
                if re.match(pattern, header_name, re.IGNORECASE):
                    headers[header_name] = settings.SENSITIVE_DATA_REPLACEMENT
    return headers


def hide_sensitive_data_queries(queries):
    if settings.HIDE_SENSITIVE_DATA:
        queries = dict(queries)
        for pattern in settings.HIDE_SENSITIVE_DATA_PATTERNS.get('QUERIES', ()):
            for query_name, query in queries.items():
                if re.match(pattern, query_name, re.IGNORECASE):
                    queries[query_name] = (
                        len(query) * [settings.SENSITIVE_DATA_REPLACEMENT] if is_base_collection(query)
                        else settings.SENSITIVE_DATA_REPLACEMENT
                    )
    return queries


def truncate_json_data(data):
    if isinstance(data, dict):
        return {key: truncate_json_data(val) for key, val in data.items()}
    elif isinstance(data, list):
        return [truncate_json_data(val) for val in data]
    elif isinstance(data, str):
        return truncatechars(data, settings.LOG_JSON_STRING_LENGTH)
    else:
        return data


def truncate_body(content, max_length):
    content = force_text(content, errors='replace')
    if len(content) > max_length:
        try:
            json_content = json.loads(content)
            return (
                json.dumps(truncate_json_data(json_content))
                if isinstance(json_content, (dict, list)) and settings.LOG_JSON_STRING_LENGTH is not None
                else content[:max_length + 1]
            )
        except JSONDecodeError:
            return content[:max_length + 1]
    else:
        return content


def clean_body(body, max_length):
    if body is None:
        return body
    body = force_text(body, errors='replace')
    cleaned_body = truncatechars(
        truncate_body(body, max_length), max_length + len(settings.SENSITIVE_DATA_REPLACEMENT)
    ) if max_length is not None else str(body)
    cleaned_body = hide_sensitive_data_body(remove_nul_from_string(cleaned_body)) if cleaned_body else cleaned_body
    cleaned_body = truncatechars(cleaned_body, max_length) if max_length else cleaned_body
    return cleaned_body


def clean_json(data):
    return {remove_nul_from_string(k): remove_nul_from_string(v) if isinstance(v, str) else v for k, v in data.items()}


def clean_headers(headers):
    return hide_sensitive_data_headers(clean_json(headers)) if headers else headers


def clean_queries(queries):
    return hide_sensitive_data_queries(clean_json(queries)) if queries else queries


def log_input_request_with_data(request, related_objects=None, slug=None, extra_data=None):
    input_request_logger = getattr(request, 'input_request_logger', None)
    if not input_request_logger:
        return False
    if related_objects:
        input_request_logger.add_related_objects(*related_objects)
    if slug:
        input_request_logger.set_slug(slug)
    if extra_data:
        input_request_logger.update_extra_data(extra_data)
    return True
