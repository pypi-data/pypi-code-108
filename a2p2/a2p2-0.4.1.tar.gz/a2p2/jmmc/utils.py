#!/usr/bin/env python

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
import requests
__all__ = []

import logging

logger = logging.getLogger(__name__)

# Do not use next code directly - this is dev related code.
# Please have a look on the other jmmc modules for client code.


#  Retry Handling for requests
# See https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Or https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/


# TODO check that we return more infiormation for 500 error case because some server side code part do return 500
# and here we may

def requests_retry_session(
        retries=3,
        backoff_factor=1.0,
        status_forcelist=(500, 502, 504)):

    adapter = HTTPAdapter()
    adapter.max_retries = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        respect_retry_after_header=False
    )
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

#            r = requests.request(method, url, headers=headers, data=json.dumps(data))
# -> r = requests_session.request(method, url, headers=headers, data=json.dumps(data))


class JmmcAPI():
    def __init__(self, rootURL, username=None, password=None):
        self.rootURL = rootURL

        # credentials can be given by hand but .netrc files automatically are used on 401

        if username and password:
            self.auth = HTTPBasicAuth(username, password)
        else:
            self.auth = None

        self.requests_session = requests_retry_session()

        logger.debug("Instanciating JmmcAPI on '%s'" % self.rootURL)

    def _get(self, url):
        return self._request('GET', url)

    def _put(self, url, json):
        return self._request('PUT', url, json)

    def _post(self, url, json):
        return self._request('POST', url, json)

    def _post(self, url, **kwargs):
        return self._request2('POST', url, **kwargs)

    def _request2(self, method, url, **kwargs):
        logger.info("performing %s request on %s" % (method, self.rootURL+url))
        r = self.requests_session.request(
            method, self.rootURL+url, **kwargs)
        # handle response if any or throw an exception
        if (r.status_code == 204):  # No Content : everything is fine
            return
        elif 200 <= r.status_code < 300:
            if 'Content-Type' in r.headers.keys() and 'application/json' in r.headers['Content-Type']:
                return r.json()
            else:
                return r.content
        # TODO enhance error handling ? Throw an exception ....
        error = []
        error.append("status_code is %s"%r.status_code)
        if r.reason :
            error.append(r.reason)
        if "X-Http-Error-Description" in r.headers.keys():
            error.append(r.headers["X-Http-Error-Description"])

        raise Exception(error)

    def _request(self, method, url, json=None, data=None, files=None):
        logger.info("performing %s request on %s" % (method, self.rootURL+url))
        r = self.requests_session.request(
            method, self.rootURL+url, auth=self.auth, json=json, data=data, files=files)
        # handle response if any or throw an exception
        if (r.status_code == 204):  # No Content : everything is fine
            return
        elif 200 <= r.status_code < 300:
            if 'Content-Type' in r.headers.keys() and 'application/json' in r.headers['Content-Type']:
                return r.json()
            else:
                return r.content
        # TODO enhance error handling ? Throw an exception ....
        error = []
        error.append("status_code is %s"%r.status_code)
        if r.reason :
            error.append(r.reason)
        if "X-Http-Error-Description" in r.headers.keys():
            error.append(r.headers["X-Http-Error-Description"])

        raise Exception(error)
