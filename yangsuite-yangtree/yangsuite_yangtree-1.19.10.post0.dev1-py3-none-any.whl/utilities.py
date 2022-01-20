# Copyright 2016 Cisco Systems, Inc
"""General utility functions for working with yangtrees and XPaths."""

import re
from collections import OrderedDict
from yangsuite.logs import get_logger

log = get_logger(__name__)

# TODO similar REs in ysnetconf.rpcbuilder and ysgnmi.jsonbuilder

XPATH_PREFIX_IDENTIFIER_RE = re.compile(
    '''(?:([a-zA-Z_][-a-zA-Z0-9_.]*):)?([a-zA-Z_][-a-zA-Z0-9_.]*)''')
"""Regex matching an identifier token and its possible prefix in an XPath.

Matches strings like ``openconfig-interfaces:interfaces`` and
``interface``.

- match.group(0) is the entire token (identifier, with or without prefix)
- match.group(1) is the prefix, if any
- match.group(2) is the un-prefixed identifier
"""


XPATH_KEY_PREDICATE_RE = re.compile(
    r"\[([^=\[\]]+)="    # [key=
    r"(?:"               # one of
    r'"([^"]+)"'         # "double-quoted value"
    r"|"                 # or
    r"'([^']+)'"         # 'single-quoted value'
    r"|"                 # or
    r"concat\((.*)\)"    # concat(...)
    r"|"                 # or
    r"([^\]]+)"          # unquoted value
    r")\]"
)
"""Regex for an XPath predicate representing a list key and value.

Matches strings like ``[name="foobar"]`` and returns the key and value
(here, ``name`` and ``foobar``) as match subgroups. Note that the key is
always subgroup 1, whereas the value will be subgroup 2 (if double-quoted),
3 (if single-quoted), 4 (if based on concat()), or 5 (if unquoted),
depending on the input.
"""


CONCAT_TOKEN_RE = re.compile(
    r"(?:"               # one of
    r'"([^"]*)"'         # double-quoted string
    r"|"                 # or
    r"'([^']*)'"         # single-quoted string
    r")"
)
"""Regex for a single-quoted or double-quoted string.

Double-quoted strings are returned as match group 1, single-quoted as
match group 2.
"""


class XPathInvalidError(ValueError):
    """Exception raised when an XPath is malformed."""

    def __init__(self, xpath, reason):
        self.xpath = xpath
        self.reason = reason
        super(XPathInvalidError, self).__init__(str(self))

    def __str__(self):
        return "ERROR: Invalid XPath:\n{0}\n  {1}".format(
            self.xpath, self.reason)


def xpath_iterator(xpath):
    """Iterator over an XPath.

    Yields:
      tuple: (token, keys_values, kv_tokens, remaining), such as::

        "oc-if:interfaces", {}, [], "/oc-if:interface[oc-if:name="Eth1"]"
        "oc-if:interface", {'oc-if:name':'Eth1'}, ['[oc-if:name="Eth1"]'], ''

    Raises:
      XPathInvalidError: if the path is invalid in various ways.

    Examples::

      >>> for tok, k_v, kv_tokens, remaining in xpath_iterator(
      ... '/oc-if:interfaces/oc-if:interface[oc-if:name="Et1"]/oc-if:state'):
      ...     print("%s %s %s '%s'" % (tok, dict(k_v), kv_tokens, remaining))
      oc-if:interfaces {} [] '/oc-if:interface[oc-if:name="Et1"]/oc-if:state'
      oc-if:interface {'oc-if:name': 'Et1'} ['[oc-if:name="Et1"]'] \
'/oc-if:state'
      oc-if:state {} [] ''
    """
    path = xpath
    while path:
        if not path.startswith('/'):
            raise XPathInvalidError(xpath, "expected /... but found {0}"
                                    .format(path))
        # Strip leading /
        path = path[1:]

        if not path:
            raise XPathInvalidError(xpath, "trailing slash")

        # A valid component could be:
        # pfx:localname
        # pfx:localname[key1="value1"]
        # localname[key1="value1:value2"][foo:keyA="valueA"]
        # pfx:localname[key1='"foo/bar"'][foo:keyB=concat("hello","world")]
        #
        # TODO: we do not yet support:
        # pfx:localname[key1="value1" and key2="value2"]
        identifier = XPATH_PREFIX_IDENTIFIER_RE.match(path)
        if not identifier:
            raise XPathInvalidError(xpath,
                                    'expected an identifier, but got "{0}"'
                                    .format(path))
        token = identifier.group(0)
        path = path[identifier.end():]
        log.debug("  ...minus pfx/localname: %s", path)

        keys_values = OrderedDict()
        kv_tokens = []
        while XPATH_KEY_PREDICATE_RE.match(path):
            # XPATH_KEY_PREDICATE_RE may match as:
            # key, value, '', '', '', ''
            # key, '', value, '', '', ''
            # key, '', '', value, '', ''
            # key, '', '', '', value, ''
            # key, '', '', '', '', value
            predicate_key_value = XPATH_KEY_PREDICATE_RE.match(path)
            kv_tokens.append(predicate_key_value.group(0))
            predicate_key = predicate_key_value.group(1)
            predicate_value = (predicate_key_value.group(2) or
                               predicate_key_value.group(3) or
                               predicate_key_value.group(5))
            if predicate_key_value.group(4) is not None:
                predicate_value = ''.join(
                    ''.join(item) for item in CONCAT_TOKEN_RE.findall(
                        predicate_key_value.group(4)
                    )
                )
            keys_values[predicate_key] = predicate_value
            path = path[predicate_key_value.end():]
            log.debug("  ...minus keys / values: %s", path)

        if path and not path.startswith('/'):
            raise XPathInvalidError(xpath, "expected /... but found {0}"
                                    .format(path))

        log.debug("%s, %s, %s, %s", token, keys_values, kv_tokens, path)
        yield (token, keys_values, kv_tokens, path)


def xpath_to_xpath_pfx(xpath, implied_prefix):
    """Add explicit prefix to all un-prefixed tokens in the given XPath.

    Args:
      xpath (str): XPath, possibly with un-prefixed tokens
      implied_prefix (str): Prefix to apply to un-prefixed tokens

    Returns:
      str: Fully prefixed XPath

    Examples::

      >>> xpath_to_xpath_pfx('/interfaces/interface/oc-eth:ethernet', 'oc-if')
      '/oc-if:interfaces/oc-if:interface/oc-eth:ethernet'
      >>> xpath_to_xpath_pfx('/interfaces/interface[name="hello"]', 'oc-if')
      '/oc-if:interfaces/oc-if:interface[oc-if:name="hello"]'

    """
    xpath_pfx = ""
    for token, keys_values, _, _ in xpath_iterator(xpath):
        if ':' not in token:
            token = implied_prefix + ':' + token
        new_keys_values = OrderedDict()
        for key in keys_values.keys():
            if ':' not in key:
                new_keys_values[implied_prefix + ':' + key] = keys_values[key]
            else:
                new_keys_values[key] = keys_values[key]
        xpath_pfx += '/' + token + ''.join('[{0}="{1}"]'.format(k, v)
                                           for k, v in new_keys_values.items())
    return xpath_pfx


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
