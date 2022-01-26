"""
All endpoints return either a JSON object or array.
Data is returned in ascending order. Oldest first, newest last.
All time and timestamp related fields are in milliseconds.

------------
TODO: ERROR CODES to look out for
------------
HTTP 4XX return codes are used for malformed requests; the issue is on the sender's side.
HTTP 403 return code is used when the WAF Limit (Web Application Firewall) has been violated.
HTTP 429 return code is used when breaking a request rate limit.
HTTP 418 return code is used when an IP has been auto-banned for continuing to send requests after receiving 429 codes.
HTTP 5XX return codes are used for internal errors; the issue is on Binance's side. It is important to NOT treat this as a failure operation; the execution status is UNKNOWN and could have been a success

------------
PARAMETERS
------------
SOme considerations (from binance API)
For GET endpoints, parameters must be sent as a query string.
For POST, PUT, and DELETE endpoints, the parameters may be sent as a query string or in the request body with content type application/x-www-form-urlencoded. You may mix parameters between both the query string and request body if you wish to do so.
Parameters may be sent in any order.
If a parameter sent in both the query string and request body, the query string parameter will be used.

------------
TODO: RATE LIMITS
------------
The following `intervalLetter` values for headers:
SECOND => S
MINUTE => M
HOUR => H
DAY => D

`intervalNum` describes the amount of the interval.
- For example, intervalNum 5 with intervalLetter M means "Every 5 minutes".

The /api/v3/exchangeInfo `rateLimits` array contains objects related to the
exchange's RAW_REQUESTS, REQUEST_WEIGHT, and ORDERS rate limits. These are
further defined in the ENUM definitions section under Rate limiters (rateLimitType).
A 429 will be returned when either rate limit is violated.


A `Retry-After` header is sent with a `418` or `429` responses and will give the
number of seconds required to wait, in the case of a 429, to prevent a ban, or,
in the case of a 418, until the ban is over.

The limits on the API are based on the IPs, not the API keys.

We recommend using the websocket for getting data as much as possible, as this
will not count to the request rate limit.

ORDER RATE LIMIT
Every successful order response will contain a X-MBX-ORDER-COUNT-(intervalNum)(intervalLetter) header which has the current order count for the account for all order rate limiters defined.
When the order count exceeds the limit, you will receive a 429 error without the Retry-After header. Please check the Order Rate Limit rules using GET api/v3/exchangeInfo and wait for reactivation accordingly.
Rejected/unsuccessful orders are not guaranteed to have X-MBX-ORDER-COUNT-** headers in the response.
The order rate limit is counted against each account.
"""
import copy
# import datetime
# import time

# import decouple
import requests

# from .utils.dt import DATETIME_FORMAT, convert_timearg_as_datetime
from .utils.status_handlers import handle_too_many_requests, DEFAULT_STATUS_HANDLERS

# env = decouple.AutoConfig(search_path="./.env")
# from .utils.signatures import sign_params, sign_message


class BaseClient:
    def __init__(self, base_url=None, headers=None, max_requests_per_min=60, response_kind="json", status_handlers=None):
        """
        Args:
            base_url (str): The base url of the API.
            headers (dict): The headers to be sent with each request.
            max_requests_per_min (int): The maximum number of requests per minute.
            response_kind (str): The kind of response to return. eg "json" or "text"
            status_handlers (dict): 
                A dictionary of response status codes and functions to handle them.
                Each function must have the following argument structure:
                    func(response, msg=None, **kwargs)
                NOTE: if you have status handlers that depend on the state of the 
                client, or are defined as instance methods of the client, then 
                you should leave this field blank, and use the 
                `client.add_status_handlers()` method once the client is 
                instantiated.
        """
        self.base_url = "" if base_url is None else base_url
        self.request_interval = 1.0 / (max_requests_per_min / 60.0) # time to wait between requests
        if headers is None:
            self.headers = {}
        else:
            self.headers = copy.deepcopy(headers)
        self.response_kind = response_kind

        self._status_handlers = DEFAULT_STATUS_HANDLERS
        if status_handlers is not None:
            self.add_status_handlers(status_handlers)

    def add_status_handlers(self, status_handlers):
        """Add aditional response status handler functions to handle different
        kinds of response errors.
        
        Args:
            status_handlers (dict):
                A dictionary of response status codes and functions to handle
                them. 
                - Each key must be an integer status code (eg `404`)
                - Each value must be one of the following:
                    - A function with the following argument structure:

                          func(response, msg=None, **kwargs)

                          where `msg` is the extracted response message
                          (eg from calling response.json() or response.text())

                    - A `None` value. Which will remove a handler.
                    - A "pass" string. Which will ignore the status, and return
                      the response message as if nothing bad happened.

        Note:
            Note, if you provide keys that already exist, they will override the
            existing handlers. New keys will be appended. And all other keys
            will remain as they were.

        Example:
            # Create a client with some status handlers
            original_status_handlers = {429:func1, 430:func2}
            >>> client = BaseClient("http://example.com", status_handlers=original_status_handlers)
            
            # Overwrite the existing handler for 430, and add a new handler for 431
            >>> client.add_status_handlers({430:func3, 431:func4})

            # Remove status handler for 429
            >>> client.add_status_handlers({429:None})

            # Make it ignore status 432
            >>> client.add_status_handlers({432:"pass"})
        """
        self._status_handlers = {**self._status_handlers, **status_handlers}

    def request(self, url=None, endpoint=None, params=None, headers=None, kind="get", response_kind=None):
        return self._request(url=url, endpoint=endpoint, params=params, headers=headers, kind=kind, response_kind=response_kind)

    def _request(self, url=None, endpoint=None, params=None, headers=None, kind="get", response_kind=None):
        if (url is None) and (endpoint is None):
            raise ValueError("Either `url` or `endpoint` must be provided")
        if url is None:
            url = self.base_url + str(endpoint)

        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)

        if headers is None:
            headers = {}
        headers = {**self.headers, **headers}

        if kind.lower() == "get":
            response = requests.get(url, params, headers=headers)
        elif kind.lower() == "post":
            response =  requests.post(url, params, headers=headers)
        return self._process_response(response)

    def _process_response(self, response, response_kind=None):
        """Attempt to extract the response message from the response object if
        it was a succesful response, otherwise handle using one of the response
        status handlers.
        """
        response_kind = self.response_kind if response_kind is None else response_kind
        if response.ok:
            if response_kind.lower() == "json":
                return response.json()
            else:
                return response.text()
        else:
            # TRY EXTRACT A RESPONSE MESSAGE
            try:
                if response_kind.lower() == "json":
                    msg = response.json()
            except:
                try:
                    msg = response.text()
                except:
                    msg = None

            # CATCH EXCEPTIONS - using one of the status handlers
            status_code = response.status_code
            response_function = self._status_handlers.get(int(status_code))
            if response_function is not None:
                response_function(response=response, msg=msg)
            elif response_function == "pass":
                # Return as if nothing bad happened
                return msg
            else:
                print(f"ERROR: with this response message {msg}")
                response.raise_for_status()

    def _time_range_batched_request(self, url, params=None, kind="get", t1=None, t2=None, window_delta=None, limit=1000):
        raise NotImplementedError("This method is not implemented yet")
        # """Process a query in batches"""
        # no_timerange = False
        # if params is None:
        #     params = {}

        # # PROCESS THE TIME RANGE
        # if window_delta is None:
        #     window_delta = datetime.timedelta(days=90)
        # assert isinstance(window_delta, datetime.timedelta), f"`window_delta` should be a `datetime.timedelta`, received a {type(window_delta)}"
        # if (t1 is None) and (t2 is None):
        #     no_timerange = True
        # elif t1 is None:
        #     t2 = convert_timearg_as_datetime(t2)
        #     t1 = t2 - window_delta
        # elif t2 is None:
        #     t1 = convert_timearg_as_datetime(t1)
        #     t2 = t1 + window_delta
        # else:
        #     t1 = convert_timearg_as_datetime(t1)
        #     t2 = convert_timearg_as_datetime(t2)

        # responses = []
        # def extend_responses(response):
        #     if isinstance(response, list):
        #         responses.extend(response)
        #     else:
        #         responses.append(response)

        # _params = copy.deepcopy(params)
        # if no_timerange:
        #     response = self.request(url=url, params=_params, kind=kind, limit=limit)
        #     extend_responses(response)
        # else:
        #     # BREAK TIME RANGE UP INTO 90 DAY BATCHES
        #     t1s = []
        #     t2s = []
        #     _t1  = t1
        #     while _t1 < t2:
        #         _t2 = min(_t1 + window_delta, t2)
        #         t1s.append(_t1)
        #         t2s.append(_t2)
        #         _t1 = _t2

        #     # RUN QUERY IN BATCHES
        #     for _t1, _t2 in zip(t1s, t2s):
        #         print(f"BATCH: {_t1} to {_t2}")
        #         _params["startTime"] = int(_t1.timestamp() * 1000)
        #         _params["endTime"] = int(_t2.timestamp() * 1000)
        #         response = self.request(url=url, params=_params, kind=kind, limit=limit)
        #         extend_responses(response)
        #         sleep_period = self.request_interval
        #         time.sleep(sleep_period)

        # return responses

