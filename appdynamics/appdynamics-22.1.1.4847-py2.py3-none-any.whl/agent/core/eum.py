# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import re
from uuid import uuid4

from appdynamics import config
from appdynamics.lang import items, map, native_str, SimpleCookie, str
from appdynamics.agent.core.snapshot import is_partial_snapshot
from appdynamics.agent.core.logs import setup_logger

logger = setup_logger('appdynamics.agent')

EUM_HEADER_NAME = 'ADRUM_{0}'
EUM_HEADER_SEPERATOR = ':'

EUM_COOKIE_NAME = 'ADRUM_BT'
EUM_COOKIE_REGEX = re.compile(r'(?:ADRUM_BT\w*)|(?:ADRUM_[0-9]+_[0-9]+_[0-9]+)')
EUM_COOKIE_MAX_AGE = 30
EUM_COOKIE_SEPERATOR = '|'

# CORE-19525: RUM: server agent fails to stale delete cookies written for
# another path. You delete a cookie by setting it again with an expiration date
# in the past. However, cookies are scoped to a path. In this bug, we would
# write a cookie at /. The next request would be for /foo/, so we would see the
# cookie and try to delete it, but you're not allowed to do that, so it
# wouldn't delete. Fix is to always use / so we'll always be able to find our
# own cookies.
EUM_COOKIE_PATH = '/'

PARTIAL_SNAPSHOT_VALUE = 'p'
FULL_SNAPSHOT_VALUE = 'f'
ENTRY_POINT_ERROR_VALUE = 'e'


class EUMCookie(SimpleCookie):
    def __init__(self, name, value, is_secure, max_age=EUM_COOKIE_MAX_AGE):
        super(EUMCookie, self).__init__()
        name = native_str(name)
        self[name] = value
        self[name]['path'] = EUM_COOKIE_PATH
        self[name]['max-age'] = max_age

        # We do this check because setting 'secure' to *anything*, even False,
        # marks the cookie as secure.
        if is_secure:
            self[name]['secure'] = True

    def __str__(self):
        return self.output()[1]

    def output(self):
        return tuple(map(native_str, super(EUMCookie, self).output().split(': ', 1)))


def guid_key(use_long_form):
    return 'clientRequestGUID' if use_long_form else 'g'


def bt_id_key(use_long_form):
    return 'btId' if use_long_form else 'i'


def bt_art_key(use_long_form):
    return 'btERT' if use_long_form else 'e'


def bt_duration_key(use_long_form):
    return 'btDuration' if use_long_form else 'd'


def snapshot_type_key(use_long_form):
    return 'serverSnapshotType' if use_long_form else 's'


def has_entry_point_errors_key(use_long_form):
    return 'hasEntryPointErrors' if use_long_form else 'h'


def global_account_name_key(use_long_form):
    return 'globalAccountName' if use_long_form else 'n'


def add_cookie(cookie, response_headers):
    """Add a cookie to the current response.

    Parameters
    ----------
    cookie : EUMCookie
        The cookie to add.
    response_headers : list
        A list of (header_name, header_value) tuples as described in PEP 0333.

    """
    response_headers.append(cookie.output())


def referrer_hash(referrer):
    """Return a hash of the HTTP referrer string.

    Note: The Python team resents the use of the word 'hash' to describe this
    operation.

    """
    return len(referrer) if referrer else 0


def make_eum_cookie(referrer, metadata, is_secure):
    """Return a cookie containing the EUM metadata.

    Parameters
    ----------
    referrer : str
        The HTTP referer header for the incoming request.
    metadata : dict
        EUM metadata to include in the cookie value.
    is_secure : bool
        True if the current request is HTTPS.

    """
    cookie_value = 'R:%s' % referrer_hash(referrer)

    for key, val in items(metadata):
        cookie_value += '%s%s:%s' % (EUM_COOKIE_SEPERATOR, key, val)

    cookie = EUMCookie(EUM_COOKIE_NAME, cookie_value, is_secure)
    return cookie


def eum_metadata_injection_enabled(eum_config, bt):
    """Return True if we should inject EUM metadata.

    Parameters
    ----------
    eum_config : appdynamics.agent.pb.EUMConfig
        The external EUM configuration.
    bt : appdynamics.agent.models.Transaction
        The BT associated with the current request.

    """

    if bt.eum_guid:
        # We have already injected the metadata.
        return False

    if not bt.registered_id:
        # The BT must be registered to generate the metadata.
        return False

    if bt.incoming_correlation:
        # EUM has no interest in continuing transactions, because the metadata
        # has no way to make it back to the web tier.
        return False

    if not eum_config.enabled:
        return False

    if config.EUM_DISABLE_COOKIE:
        return False

    user_agent_whitelist = config.EUM_USER_AGENT_WHITELIST

    if '*' in user_agent_whitelist:
        return True

    user_agent = bt.request.user_agent
    if user_agent:
        for pattern in user_agent_whitelist:
            if pattern in user_agent:
                return True

    logger.debug('EUM metadata injection disabled due to unknown user-agent: %r' % user_agent)
    return False


def make_eum_guid():
    return str(uuid4())


def _generate_eum_metadata(eum_config, bt):
    """Return a dict of metadata to inject into the current response.

    Metadata includes: request GUID; BT ID; BT average response time;
    snapshot type; BT has errors; BT duration (not currently used).

    Parameters
    ----------
    eum_config : appdynamics.agent.pb.EUMConfig
        The external EUM configuration.
    bt : appdynamics.agent.models.Transaction
        The BT associated with the current request.

    """
    metadata = {}

    # backward compatibility concerns
    # - to address set-cookie headers being too long (CORE-32353), we plan to
    #   use short-formed meta keys (3.9.2+)
    # - this means old JS agent (before 3.9.2) won't be able to read the bt
    #   info sent by the new server agent. we consider this a price to pay, and
    #   for customers, upgrading JS agent won't be too difficult
    # - mobile agents, on the other hand, are much difficult to upgrade since
    #   they are deployed within customers' apps. At the same time, meta data
    #   for mobile requests are injected as response headers and no one has
    #   complained about them being too long, so we decide to still use the old
    #   meta keys.
    use_long_form = bt.request.is_mobile

    global_account_name = eum_config.globalAccountName
    if global_account_name:
        metadata[global_account_name_key(use_long_form)] = global_account_name

    metadata[guid_key(use_long_form)] = bt.eum_guid
    metadata[bt_id_key(use_long_form)] = bt.registered_id

    response_received = bt.wait_for_bt_info_response()
    if response_received and bt.bt_info_response.HasField('averageResponseTimeForLastMinute'):
        metadata[bt_art_key(use_long_form)] = bt.bt_info_response.averageResponseTimeForLastMinute

    if bt.snapshot_guid or (response_received and bt.bt_info_response.isSnapshotRequired):
        partial_snapshot = is_partial_snapshot(bt.snapshot_trigger, bt.started_on_time)
        metadata[snapshot_type_key(use_long_form)] = (PARTIAL_SNAPSHOT_VALUE if partial_snapshot else
                                                      FULL_SNAPSHOT_VALUE)

        # There is also a field in the cookie for bt duration, but we should
        # only set this if the bt has ended. Currently, there is no way for the
        # bt to have ended at this point so we don't do it.

    if bt.has_errors:
        metadata[has_entry_point_errors_key(use_long_form)] = ENTRY_POINT_ERROR_VALUE

    return metadata


def match_eum_cookie_name(name):
    """Return True if this is an EUM cookie name.

    """
    return EUM_COOKIE_REGEX.match(name) is not None


def delete_stale_eum_cookies(cookies, response_headers, is_secure):
    """Delete stale EUM cookies (see CORE-18055).

    Parameters
    ----------
    cookies : dict
        Cookies associated with the current request.
    response_headers : list
        A list of (header_name, header_value) tuples as described in PEP 0333.
    is_secure : bool
        True if the current request is HTTPS.

    """

    # CORE-18055: RUM: Navigating from non-instrumented page to
    # instrumented page with same referrer causes problems
    #
    # Recall that EUMContext tells JSAgent which cookies are designated for
    # the current response by hashing the referrer. We can't use the page
    # URL because because EUMContext and JSAgent may see different request
    # URLs in the case of server-side URL rewriting, which is transparent
    # to the client.
    #
    # In the case of this bug, the non-instrumented page leaves uneaten
    # cookies behind, which are eaten by the next instrumented page
    # with the same referrer.
    #
    # The fix is to make cookies behave more like one-time response
    # metadata, which is what we really want anyway. On each request,
    # we tell the browser to delete any cookies left over from previous
    # requests.
    #
    # Note this may introduce the opposite bug: we may delete a cookie
    # before JSAgent has a chance to read this. How could it happen?
    # From the browser's point of view:
    #  - Send page1 request
    #  - Receive page1 response with cookies1
    #  - Send page2 request (in another tab, in an iframe, etc) with cookies1
    #  - Receive page2 response which deletes cookies1
    #  - Start executing scripts for page1, but find that cookies1 are deleted
    #
    # But I would argue that it's preferable to have false negatives
    # (missing BT correlation) than false positives (incorrect BT correlation),
    # especially since we already know that cookie metadata may be truncated.

    for name, value in items(cookies):
        if match_eum_cookie_name(name):
            # Add the cookie to the current response, but expire it immediately.
            cookie = EUMCookie(name, value, is_secure, max_age=0)
            add_cookie(cookie, response_headers)
            logger.debug('Deleting stale EUM cookie: %s' % cookie)


def inject_eum_metadata(eum_config, bt, response_headers):
    """Inject EUM metadata into the response headers.

    Either write a cookie containing the metadata, or add individual headers
    for mobile/ajax requests.

    Parameters
    ----------
    eum_config : appdynamics.agent.pb.EUMConfig
        The external EUM configuration.
    bt : appdynamics.agent.models.Transaction
        The BT associated with the current request.
    response_headers : list
        A list of (header_name, header_value) tuples as described in PEP 0333.

    """
    delete_stale_eum_cookies(bt.request.cookies, response_headers, bt.request.is_secure)

    # refactor this so that we don't pass the whole BT to this function for better testing????
    if eum_metadata_injection_enabled(eum_config, bt):
        bt.eum_guid = make_eum_guid()
        metadata = _generate_eum_metadata(eum_config, bt)

        if bt.request.is_ajax:
            logger_string = 'Injecting EUM headers into response:'
            for i, data in enumerate(items(metadata)):
                header = (native_str(EUM_HEADER_NAME.format(i)), native_str(EUM_HEADER_SEPERATOR.join(map(str, data))))
                response_headers.append(header)
                logger_string += ' %s' % (header,)
            logger.debug(logger_string)
        else:
            cookie = make_eum_cookie(bt.request.referer, metadata, bt.request.is_secure)
            logger.debug('Injecting EUM cookie into response headers: %s' % cookie)
            add_cookie(cookie, response_headers)
