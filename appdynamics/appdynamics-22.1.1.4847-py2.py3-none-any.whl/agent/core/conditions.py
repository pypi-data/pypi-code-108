# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Utilities for dealing with match rules.

"""

from __future__ import unicode_literals
import re

from appdynamics.lang import items, str, str_t
from appdynamics.lib import get_request_host_and_port
from appdynamics.agent.core import pb


def flip(binary_func):
    """Return a function which, when called, will reverse the input arguments.

    """
    return lambda x, y: binary_func(y, x)


MATCH_METHODS = {
    pb.StringMatchCondition.CONTAINS: lambda x, y: x in y,
    pb.StringMatchCondition.EQUALS: lambda x, y: x == y,
    pb.StringMatchCondition.STARTS_WITH: flip(str_t.startswith),
    pb.StringMatchCondition.ENDS_WITH: flip(str_t.endswith),
    pb.StringMatchCondition.MATCHES_REGEX: re.search,
}


def match(instr, cond):
    """Match a string according to a condition.

    Parameters
    ----------
    instr : str
    cond : pb.StringMatchCondition

    Returns
    -------
    bool
        True if `instr` matches `cond`, else false.

    """
    is_match = None

    instr = str(instr)  # i shouldn't have to do this.
    if cond.type == pb.StringMatchCondition.IS_NOT_EMPTY:
        assert len(cond.matchStrings) == 0
        is_match = bool(instr)
    elif cond.type == pb.StringMatchCondition.IS_IN_LIST:
        assert len(cond.matchStrings) > 0
        is_match = instr in cond.matchStrings
    else:
        assert len(cond.matchStrings) == 1
        match_str = cond.matchStrings[0]
        is_match = bool(MATCH_METHODS[cond.type](match_str, instr))

    return is_match != cond.isNot


def match_kv(d, kv_matches):
    """Match a dictionary against a KeyValueMatch rule.

    A dictionary, `d`, is said to match the rules `kv_matches` if each
    rule in `kv_matches` matches at least one item in `d`. A dictionary
    may have items that do not match any rules in `kv_matches`; the presence
    of these "extra" items does not prevent a match.

    If `kv_matches` is empty, this function returns `True` (because any
    dictionary matches the set of empty rules).

    Parameters
    ----------
    d : dict
        A key-value mapping where the keys and values are strings.
    kv_matches : iterable[pb.KeyValueMatch]
        A list of :py:class:`pb.KeyValueMatch` instances.

    Returns
    -------
    bool
        True if all of the key-value matches in `kv_matches` are matched in
        the given dictionary, `items`, else false.

    """
    for kv_match in kv_matches:
        for key, value in items(d):
            if (match(key, kv_match.key) and
                    (kv_match.type == pb.KeyValueMatch.CHECK_FOR_EXISTENCE or match(value, kv_match.value))):
                break  # Found a match for this rule.
        else:
            # We looked at all items and didn't find a match for this rule.
            return False

    return True


def match_http(request, http_rule):
    """Match an HTTP request against an HTTPMatchRule.

    Parameters
    ----------
    request : request-like object
        An object representing an incoming HTTP request with fields `method`,
        `path`, `args` (the HTTP query parameters), `headers`, `cookies`,
        `host`, and `environ` (the WSGI environment).
    http_rule : pb.EntryPointMatchCondition.HTTPMatchRule

    Returns
    -------
    bool
        True if the given HTTP request matches the `http_rule`.

    """
    # http_rule.method returns 0 by default which corresponds to 'GET' method when 'method' field is absent
    if http_rule.HasField('method') and pb.HTTPMethod.Name(http_rule.method) != request.method:
        return False

    if http_rule.uri.IsInitialized() and not match(request.path, http_rule.uri):
        return False

    if http_rule.host.IsInitialized() or http_rule.port.IsInitialized():
        host, port = get_request_host_and_port(request)
    else:
        host, port = None, None

    if http_rule.host.IsInitialized() and not match(host, http_rule.host):
        return False

    if http_rule.port.IsInitialized() and not match(str(port), http_rule.port):
        return False

    if http_rule.params and not match_kv(request.args, http_rule.params):
        return False

    if http_rule.cookies and not match_kv(request.cookies, http_rule.cookies):
        return False

    if http_rule.headers and not match_kv(request.headers, http_rule.headers):
        return False

    return True
