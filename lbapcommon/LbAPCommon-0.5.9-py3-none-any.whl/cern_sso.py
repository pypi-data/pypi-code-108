###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import logging
import xml.etree.ElementTree as ET
from logging import NullHandler
from urllib.parse import urljoin, urlparse

import requests
from requests_kerberos import OPTIONAL, HTTPKerberosAuth

log = logging.getLogger(__name__)
log.addHandler(NullHandler())

DEFAULT_TIMEOUT_SECONDS = 60
ANA_PROD_HOST = "https://lhcb-analysis-productions.web.cern.ch/"


class SSOException(Exception):
    pass


class SSOAuthException(SSOException):
    def __str__(self):
        return (
            "Failed to login to analysis productions website\n\n"
            'Try running "kinit username@CERN.CH"'
        )


def _init_session(s, url, cookiejar, auth_url_fragment):
    """
    Internal helper function: initialise the session by trying to access
    a given URL, setting up cookies etc.


    :param: auth_url_fragment: a URL fragment which will be joined to
    the base URL after the redirect, before the parameters. Examples are
    auth/integrated/ (kerberos) and auth/sslclient/ (SSL)
    """
    if cookiejar is not None:
        log.debug("Using provided cookiejar")
        s.cookies = cookiejar

    # Try getting the URL we really want, and get redirected to SSO
    log.info("Fetching URL: %s" % url)
    r1 = s.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)

    # Parse out the session keys from the GET arguments:
    redirect_url = urlparse(r1.url)
    log.debug("Was redirected to SSO URL: %s" % str(redirect_url))

    # ...and inject them into the Kerberos authentication URL
    return "{auth_url}?{parameters}".format(
        auth_url=urljoin(r1.url, auth_url_fragment), parameters=redirect_url.query
    )


def _finalise_login(s, auth_results):
    """
    Perform the final POST authentication steps to fully authenticate
    the session, saving any cookies in s' cookie jar.
    """

    r2 = auth_results

    # Did it work? Raise Exception otherwise.
    r2.raise_for_status()

    # Get the contents
    try:
        tree = ET.fromstring(r2.content)
    except ET.ParseError as e:
        log.error("Could not parse response from server!")
        log.error("The contents returned was:\n{}".format(r2.content))
        raise e

    action = tree.findall("body/form")[0].get("action")

    # Unpack the hidden form data fields
    form_data = {
        elm.get("name"): elm.get("value") for elm in tree.findall("body/form/input")
    }

    # ...and submit the form (WHY IS THIS STEP EVEN HERE!?)
    log.debug("Performing final authentication POST to %s" % action)
    r3 = s.post(url=action, data=form_data, timeout=DEFAULT_TIMEOUT_SECONDS)

    # Did _that_ work?
    r3.raise_for_status()

    # The session cookie jar should now contain the necessary cookies.
    log.debug("Cookie jar now contains: %s" % str(s.cookies))

    return s.cookies


def krb_sign_on(url, cookiejar=None):
    """
    Perform Kerberos-backed single-sign on against a provided
    (protected) URL.

    It is assumed that the current session has a working Kerberos
    ticket.

    Returns a Requests `CookieJar`, which can be accessed as a
    dictionary, but most importantly passed directly into a request or
    session via the `cookies` keyword argument.

    If a cookiejar-like object (such as a dictionary) is passed as the
    cookiejar keword argument, this is passed on to the Session.
    """

    kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)

    with requests.Session() as s:

        krb_auth_url = _init_session(
            s=s, url=url, cookiejar=cookiejar, auth_url_fragment="auth/integrated/"
        )

        # Perform actual Kerberos authentication
        log.info("Performing Kerberos authentication against %s" % krb_auth_url)

        r2 = s.get(krb_auth_url, auth=kerberos_auth, timeout=DEFAULT_TIMEOUT_SECONDS)

        return _finalise_login(s, auth_results=r2)


def sign_in(url):
    try:
        cookies = krb_sign_on(url)
    except requests.exceptions.HTTPError as r:
        raise SSOAuthException(r) from None
    else:
        return cookies


def get_with_cookies(url):
    resp = requests.get(url, cookies=sign_in(ANA_PROD_HOST))
    if not resp.ok:
        raise SSOException(f"Request to {url} failed with {resp.text}")
    return resp.json()
