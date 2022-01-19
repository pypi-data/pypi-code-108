# REST API MixIn
# Author: Spencer Hanson, for Swimlane

from urllib.parse import urljoin
from requests.auth import AuthBase
import requests
import pprint
from swimlane_connector_exceptions import exceptions
from pyflattener import extend_nested_lists, do_flatten
import polling


def asset_parser(context_asset, host_name="host",
                 username="username", password="password", auth=None, **kwargs):
    """Take in a context asset and break it into params for an ``__init__`` call on BasicRestEndpoint

    Args:
        context_asset: Context asset object
        host_name: host key name to grab from asset, defaults to ``host``
        username: username key name to grab from asset, defaults to ``username``
        password: password key name to grab from asset, defaults to ``password``
        auth: optional auth argument to override username/password. Set to None to disable auth
        kwargs: optional keyword args to overwrite the parameters with

    Returns:
        Dictionary of key args to use with \*\*{} in the ``super().__init__()`` of a BasicRestEndpoint

    """
    host = context_asset.get(host_name)
    if host is not None:
        host = host.strip(" /")
        if 'port' in context_asset:
            host = "{}:{}".format(host, context_asset['port'])

    params = {
        "host": host,
        "verify": context_asset.get("verify_ssl", True),
        "proxy": context_asset.get("http_proxy"),
        "verbose_errors": context_asset.get("verbose_errors", False)
    }

    if auth == "basic":  # nondefault auth
        params["auth"] = (context_asset[username], context_asset[password])
    elif auth:  # No auth, but not none (else is inferred to be no auth)
        params["auth"] = auth

    params.update(kwargs)

    return params


class HeaderAuth(AuthBase):
    """Auth for basic

    """

    def __init__(self, headers):
        self.headers = headers

    def __call__(self, r):
        r.headers.update(self.headers)
        return r


class ParamAuth(AuthBase):
    def __init__(self, params):
        self.params = params

    def __call__(self, r):
        r.prepare_url(r.url, self.params)
        return r


class WrappedSession(requests.Session):
    """A wrapper for requests.Session to override 'verify' property, ignoring REQUESTS_CA_BUNDLE environment variable.

    This is a workaround for https://github.com/kennethreitz/requests/issues/3829 (will be fixed in requests 3.0.0)
    Code sourced from user intgr https://github.com/kennethreitz/requests/issues/3829
    """

    def merge_environment_settings(self, url, proxies, stream, verify, *args, **kwargs):
        if self.verify is False:
            verify = False

        return super(WrappedSession, self).merge_environment_settings(url, proxies, stream, verify, *args, **kwargs)


class RestAPIMixin(object):
    """
    Superclass Mix In, for custom APIs
    """

    def __init__(self, host, verify=True, proxy=None, auth=None, raise_for_status=True,
                 verbose_errors=False, default_status_actions=True):
        """Create an API adapter class

        Args:
            host: Full URL, including schema for the base of the API. Ex: http://google.com/v1/api
            verify: Optional boolean to verify SSL certificates in the requests, defaults to True
            proxy: Optional proxy for the requests session. A given string value will be used for both HTTP/HTTPS
            auth: Optional requests session authentication
            raise_for_status: Optional to raise for status errors after each request, defaults to True

        """

        self.host = host
        self.session = WrappedSession()
        self.session.verify = verify
        self.session.proxies = {
            "http": proxy,
            "https": proxy
        }

        self.session.auth = auth
        self.raise_for_status = raise_for_status
        self.custom_status_actions = {}
        self.verbose_errors = verbose_errors

        self.configure_status_actions(default_status_actions=default_status_actions)

    def configure_status_actions(self, default_status_actions=True, status_mapping_update=None,
                                 remove_status_from_mapping=None, verbose_errors=None,
                                 status_range_mapping_update=None):
        """
        Args:
            default_status_actions: use swimlane default errors for 404 and 401
            status_mapping_update: A dictionary to update the mapping of error codes to functions.  This must
                                      be the same format as the default_actions dictionary.  This will overwrite
                                      mappings defined in status_range_mapping_update.
            remove_status_from_mapping: A list of status codes to remove from the custom_status_actions mapping
            verbose_errors: If true, errors will return more information from the failed request. Defaults to None for no change
            status_range_mapping_update: a dictionary with status ranges as keys and functions as values
                                    a range is a string formatted as "{min status code}-{max status code}"
                                    e.g. "400-499" represents all 4xx status codes
        Returns:
            None
        """
        if verbose_errors is not None:
            self.verbose_errors = verbose_errors

        default_actions = {404: self.get_404_exception,
                           401: self.get_401_exception}

        range_mappings = self._convert_range_mappings_to_dict(status_range_mapping_update)
        self.custom_status_actions.update(range_mappings)
        if default_status_actions:
            self.custom_status_actions.update(default_actions)
        if status_mapping_update:
            self.custom_status_actions.update(status_mapping_update)
        if remove_status_from_mapping:
            for status in remove_status_from_mapping:
                self.custom_status_actions.pop(status)

    def _convert_range_mappings_to_dict(self, range_mappings):
        if not range_mappings:
            return {}
        mappings = {}
        for key, value in range_mappings.items():
            try:
                status_range = key.split('-')
                minimum = int(status_range[0])
                maximum = int(status_range[1])
            except Exception as e:
                raise ValueError("Invalid key format in status_range_mapping_update: {}".format(key))
            for status in range(minimum, maximum+1):
                mappings[status] = value
        return mappings

    def default_error_message(self, response):
        return "{} response from {}\n{}".format(response.status_code, response.url, response.content)

    def get_404_exception(self, response):
        raise exceptions.ResourceNotFound(self.default_error_message(response), resource_name=response.url.split('/')[-1])

    def get_401_exception(self, response):
        raise exceptions.InvalidCredentials(self.default_error_message(response))

    def request(self, method, endpoint, **kwargs):
        """Make a request using the requests library, given a method, endpoint and keyword arguments

        Args:
            method: HTTP Method to use to make the request
            endpoint: Endpoint to hit on the host, Ex: '/update'
            kwargs: Extra keyword arguments to add to the request func call

        Returns:
            Requests response object

        """
        try:
            response = self.session.request(method, urljoin(self.host, endpoint), **kwargs)
        except requests.exceptions.ConnectionError as e:
            split_host = self.host.split(":")
            protocol = split_host[0]
            host = split_host[1].strip(r'/')
            port = '80'
            if len(split_host) > 2:
                port = split_host[2]
            raise exceptions.ConnectionError(e,
                                             host=host,
                                             port=port,
                                             protocol=protocol)
        if self.verbose_errors and response.status_code >= 400:
            headers_text = pprint.pformat(dict(response.headers))
            message = "\nStatus Code: {}\nURL: {}\nContent:\n{}\nHeaders:\n{}".format(response.status_code,
                                                                                      response.url,
                                                                                      response.content,
                                                                                      headers_text)
            raise exceptions.SwimlaneIntegrationException(message)
        if response.status_code in self.custom_status_actions:
            return self.custom_status_actions[response.status_code](response)
        if self.raise_for_status:
            try:
                response.raise_for_status()
            except Exception as e:
                raise  # For debugging, put a breakpoint here
        return response

    def set_user_agent(self, bundle_name=None, bundle_version=None, swimlane_version=None, **kwargs):
        """Set the user agent to be Swimlane-specific

        Args:
            bundle_name: name of the bundle making the request
            bundle_version: version of the bundle
            swimlane_version: version of Swimlane being used
            kwargs: additional arguments to include in the user agent

        Returns:
            user_agent string

        """
        user_agent = ''
        if bundle_name and bundle_version:
            user_agent = '{}/{} '.format(bundle_name, bundle_version)
        if swimlane_version:
            user_agent += 'Swimlane/{} '.format(swimlane_version)
        if kwargs:
            for key, val in kwargs.items():
                user_agent += '{}/{} '.format(key, val)
        if user_agent:
            user_agent = user_agent.rstrip()
            self.session.headers.update({'User-Agent': user_agent})

    def poll_request(self, method, endpoint, step=5, timeout=60, poll_func=None, **kwargs):
        """Make a request using polling, for endpoint that need to be poked over and over until they respond correctly

        Args:
            method: HTTP Method to use in the polling requests
            endpoint: Endpoint to hit when polling
            step: Seconds between polled requests
            timeout: Total time of polling before the request fails
            poll_func: Polling function with form f(method, endpoint, kwargs) -> Truth value of the returned determines whether the polling request succeeds

        Returns:
            result of poll_func when result is true

        """
        if not poll_func:
            def poll_func(m, e, kwa):
                result = self.request(m, e, **kwa)
                if result.status_code in (200, 201):
                    return result
                else:
                    return False

        return polling.poll(
            poll_func,
            args=[method, endpoint, kwargs],
            step=step,
            timeout=timeout
        )


class BasicRestEndpoint(RestAPIMixin):
    """Basic rest endpoint mix in, should be sufficient for most APIs"""
    endpoint = ""
    kwargs = {}
    method = "GET"

    def get_endpoint(self):
        """Endpoint relative to the host, ie '/v2/update'"""
        return self.endpoint

    def parse_response(self, response):
        """Given a requests response, process it


        Args:
            response: Requests response object

        Returns:
            response.json()

        """
        response = response.json()
        if isinstance(response, list):
            return do_flatten(response, shallow_flatten=True, add_raw_json=True)
        return do_flatten(response, add_raw_json=True)

    def get_req_method(self):
        """Request method to use, valid: GET, POST, PUT, PATCH, DELETE

        Returns:
            String for request method to use

        """
        return self.method

    def get_kwargs(self):
        """Optional keyword arguments to pass to the request

            Examples:
                kwargs = {
                    "data": "stringifiedata",
                    "json": {...JSONOBJ...},
                    "files": {
                        "file1":open('/path/to/file1', 'rb')
                    }
                }

        Returns:
            Dict to be used for parameters in the requests.request() call

        """
        return self.kwargs

    def execute(self):
        """Run the request, and return the processed response

        Returns:
            Parsed response from the request

        """
        response = self.request(self.get_req_method(), self.get_endpoint(), **self.get_kwargs())
        return self.parse_response(response)


class BasicRestPaginationEndpoint(BasicRestEndpoint):
    def __init__(self, result_limit=None, *args, **kwargs):
        """
        If the API has pagination support, this class makes it easy to query them all
        Just define next_page which is run until it returns None, marking the end of the pages
        each request is run through parse_response, which, by default, doesn't touch the response object
        Then combine_pages is given the list of response objects, to finalize the execution

        If result_limit is not None, then the execution will continue until the count_result function returns sums up to
        greater or equal to result_limit


        Args:
            result_limit:  Limit on the number of results to return
            *args:  BasicRestEndpoint args
            **kwargs: BasicRestEndpoint args
        """
        super(BasicRestPaginationEndpoint, self).__init__(*args, **kwargs)
        if result_limit:
            self.result_limit = result_limit  # Limit the results
        else:
            self.result_limit = InfinityVal()  # No limit, results limit is infinity

        self.result_count = 0  # Number of results, as defined by count_result()
        self.request_count = 0  # Count the number of times requests have been made (could be useful for page #'s)

    def count_result(self, parsed_response):
        """
        Function to return a number to be added to the 'result_count'
        If that number + the current result_count > result_limit, requests will stop

        Args:
            parsed_response: response resulting from self.parse_response

        Returns: Defaults to 1, for 1 response per request.

        """
        if isinstance(parsed_response, list):
            return len(parsed_response)
        return 1

    def get_next_page(self, response):
        """Function to return the next endpoint to hit, given the previous response
        If it returns None, it's finished

        Args:
            response: The previous requests response
            all_responses: A list of the previous responses, for keeping count

        Returns:
            URL to use for the next request call

        """
        raise NotImplementedError

    def combine_responses(self, results):
        """Take all the response objects from the pages and combine them into the final result
        Defaults to extending the list of results into a single list
        Args:
            results: List of responses

        Returns:
            Combined responses for final output

        """
        results = extend_nested_lists(results)
        if len(results) > self.result_limit:
            return results[:self.result_limit]
        else:
            return results

    def execute(self):
        """Continually run the request, making sure to check if there are more pages, returns output from combine_responses

        Returns:
            result of the processed request

        """
        results = []

        response = self.request(self.get_req_method(), self.get_endpoint(), **self.get_kwargs())
        parsed_response = self.parse_response(response)
        self.result_count += self.count_result(parsed_response)
        results.append(parsed_response)
        self.request_count += 1

        if self.result_count >= self.result_limit:
            pass  # Already reached limit on first call
        else:
            next_page = self.get_next_page(response)
            while next_page:
                response = self.request(self.get_req_method(), next_page, **self.get_kwargs())
                parsed_response = self.parse_response(response)
                self.result_count += self.count_result(parsed_response)
                results.append(parsed_response)
                self.request_count += 1

                if self.result_count >= self.result_limit:
                    break

                next_page = self.get_next_page(response)

        return self.combine_responses(results)


class LinkHeadersPaginationEndpoint(BasicRestPaginationEndpoint):
    """Basic Pagination endpoint implementation that uses the 'Link Headers' specification
    """

    def get_next_page(self, response):
        return self.parse_link(response.links)

    def parse_link(self, links):
        if 'next' in links and 'url' in links['next']:
            return links["next"]["url"]
        return None


class GETMixin(BasicRestEndpoint):
    """Mixin for GET requests
    """

    method = "GET"


class POSTMixin(BasicRestEndpoint):
    """Mixin for POST requests
    """

    method = "POST"


class PUTMixin(BasicRestEndpoint):
    """Mixin for PUT requests
    """

    method = "PUT"


class DELETEMixin(BasicRestEndpoint):
    """Mixin for DELETE requests
    """

    endpoint = "DELETE"


class PATCHMixin(BasicRestEndpoint):
    """Mixin for PATCH requests
    """

    endpoint = "PATCH"

class InfinityVal(object):
    """Infinity exists for float but not int, so this class represents infinity for all numerical types
    """
    def __init__(self, pos=True):
        """
        Args:
            pos: If this infinity is positive or negative

        """
        self.pos = pos

    def __sub__(self, other):
        return self

    def __add__(self, other):
        return self

    def __ge__(self, other):
        return self.pos

    def __le__(self, other):
        return not self.pos

    def __gt__(self, other):
        return self.pos

    def __lt__(self, other):
        return not self.pos

    def __str__(self):
        return ("+" if self.pos else "-") + "inf"
