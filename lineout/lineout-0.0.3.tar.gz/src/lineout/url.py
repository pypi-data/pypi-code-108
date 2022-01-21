__all__ = ['get_detail_url', 'url_add_params']

from urllib.parse import urljoin, urlencode, urlsplit, urlunsplit, parse_qs


def get_detail_url(base_url, id):
    return urljoin(base_url, str(id)) + '/'


def url_add_params(url, params):
    if not params:
        return url
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params.update(params)
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

