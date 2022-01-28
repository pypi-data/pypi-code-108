from __future__ import annotations
import re
import typing as t


def extract_groups(
    matches: re.Match,
    names: t.Iterable[str],
    none_str: str = "ignore",
    combine: t.Optional[t.Mapping[str, t.List[str]]] = None
) -> t.Dict[str, t.Optional[str]]:
    """
    Extract named groups from a `re.Match` object to a dictionary.
    These named groups are delimited by `(?P<name>)`.
    
    Parameters
    ----------
    matches: re.Match
        The matches created by `re.search`.
    
    names: Iterable[str]
        A list of named groups found in the regex string.
    
    none_str: str = "ignore"
        If "ignore", strings will be left as they are.
        If "to_none", empty strings will be converted to `None`.
        If "to_str", `None` will be converted to empty strings.
    
    combine: Optional[Mapping[str, List[str]]] = None
        An optional list of named groups that are supposed to be treated as the
        same named group.
        For example: there may be 2 named groups called "path_type1" and
        "path_type2". Each named group represents one type of "path" and only
        1 of each type can occur in any given string. However, they are
        intrisically still considered the same thing: a path. This parameter
        allows you to specify that "path_type1" and "path_type2" should
        be converted to "path" by passing
        `extract_group(..., combine={"path": ["path_type1", "path_type2"], ...})`
        in the final dictionary. However, if more than 1 of any of the 2
        possible groups appear, a ValueError will be raised.
        
    Raises
    ------
    ValueError
        If more than 1 named group in a group of related named groups are found,
        this error is raised.
        OR If an invalid value is given to none_str.
    
    Returns
    -------
    Dict[str, Optional[str]]
        A dictionary of named groups and their associated values.
    """
    if none_str not in {"ignore", "to_none", "to_str"}:
        raise ValueError(f"Invalid none_str: {none_str}")
    
    def null_convert(input: t.Optional[str]) -> t.Optional[str]:
        if (input is not None and input != "") or none_str == "ignore":
            return input
        elif none_str == "to_none":
            return None
        else:
            return ""
    
    combine: t.Mapping[str, t.List[str]] = {} if combine is None else combine
    result = {}
    for name in names:
        related_name_groups = combine.get(name)
        related_name_groups = (
            [name]
            if related_name_groups is None
            else related_name_groups
        )
        for related in related_name_groups:
            try:
                group_value = matches.group(related)
            except IndexError:
                group_value = None
            group_value = null_convert(group_value)
            current_value = result.get(name)
            if current_value is not None and group_value is not None:
                raise ValueError(
                    f"'{name}' has already been filled by '{result.get(name)}' "
                    f"but a new value ('{group_value}') was found."
                )
            elif current_value is None:
                result[name] = group_value
        if name not in result:
            result[name] = None if none_str == "to_str" else ""
    return result


def make_parser(
    regex: re.Pattern[str],
    names: t.Iterable[str]
) -> t.Callable[[str, t.Mapping[t.str, t.Any]], t.Dict[str, t.Optional[str]]]:
    """
    Create a function that can parse locators.
    
    Parameters
    ----------
    regex: re.Pattern[str]
        A compiled regex pattern. You can create such an object by calling
        `re.compile` on a regex string.
    
    names: Iterable[str]
        A list of named groups that the parser should encounter in the regex
        matches.
    
    Returns
    -------
    Callable[[str, Mapping[t.Str, Any]], Dict[str, Optional[str]]]
        The parser function.
    """
    
    def parser(input: str, **kwargs: t.Any) -> t.Dict[str, t.Optional[str]]:
        matches = regex.search(input)
        if matches is None:
            return {}
        else:
            return extract_groups(matches, names, **kwargs)
    
    return parser


UNRESERVED: str = r"[0-9a-zA-Z._~\-]"
PERCENT_ENCODED: str = r"%[0-9a-fA-F]{2}"
SUB_DELIMS: str = r"[!\$&'\(\)\*\+\,\;\=]"
CHAR: str = f"{UNRESERVED}|{PERCENT_ENCODED}|{SUB_DELIMS}"


# Taken from validators.domain.pattern
DOMAIN_REGEX_RAW: str = (
    r"(?P<domain>"
    r"(?:[a-zA-Z0-9]"  # First character of the domain
    r"(?:[a-zA-Z0-9-_]{0,61}[A-Za-z0-9])?\.)+"  # Sub domain + hostname
    r"[A-Za-z0-9][A-Za-z0-9-_]{0,61}"  # First 61 characters of the gTLD
    r"[A-Za-z]"  # Last character of the gTLD
    r")"
)

# Taken from https://ihateregex.io/expr/ip/
IPV4_REGEX_RAW: str = (
    r"(?P<ipv4>"
    r"(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}"
    r")"
)

# Taken from https://stackoverflow.com/a/17871737
IPV6_REGEX_RAW: str = (
    r"(?P<ipv6>"
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"          # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){1,7}:|"                         # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"         # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"  # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"  # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"  # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"  # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"       # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8  
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"                     # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::     
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"     # fe80::7:8%eth0   fe80::7:8%1     (link-local IPv6 addresses with zone index)
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"          # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255  (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"           # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
    r")"
)


HOST_REGEX_RAW: str = f"(?P<host>{DOMAIN_REGEX_RAW}|{IPV4_REGEX_RAW}|{IPV6_REGEX_RAW})"


USERNAME_REGEX_RAW: str = f"(?P<username>({CHAR})+)"
PASSWORD_REGEX_RAW: str = f"(?P<password>({CHAR}|[:])+)"


USERINFO_REGEX_RAW: str = f"{USERNAME_REGEX_RAW}(:{PASSWORD_REGEX_RAW})?"


# 0 to 65535
PORT_REGEX_RAW: str = (
    r"(?P<port>"
    r"(6553[0-5]|655[0-2]\d|65[0-4]\d\d|6[0-4]\d\d\d|[1-5]?\d\d\d\d|[1-9]\d{0,3}|[0-9])"
    r")"
)


AUTHORITY_REGEX_RAW: str = (
    r"(?P<authority>"
    f"({USERINFO_REGEX_RAW}@)?({HOST_REGEX_RAW})(:{PORT_REGEX_RAW})?"
    r")"
)
AUTHORITY_REGEX: re.Pattern[str] = re.compile(f"^{AUTHORITY_REGEX_RAW}$")


SCHEME_REGEX_RAW: str = r"(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*)"
PATH_INTERNAL_REGEX_RAW: str = f"(({CHAR}|[@])+(/({CHAR}|[@])+)*)/?|/?"
PATH_REGEX_RAW: str = r"(?P<path>" + PATH_INTERNAL_REGEX_RAW + r")"
SCP_PATH_REGEX_RAW: str = r"(?P<path>/?" + PATH_INTERNAL_REGEX_RAW + r")"
QUERY_REGEX_RAW: str = f"(?P<query>({CHAR}|[/\?])*)"
FRAGMENT_REGEX_RAW: str = f"(?P<fragment>({CHAR}|[/\?])*)"


FULL_URL_REGEX_RAW: str = (
    r"(?P<full_url>"
    f"{SCHEME_REGEX_RAW}://{AUTHORITY_REGEX_RAW}(/{PATH_REGEX_RAW})?(\?{QUERY_REGEX_RAW})?(#{FRAGMENT_REGEX_RAW})?"
    r")"
)
FULL_URL_REGEX: re.Pattern[str] = re.compile(f"^{FULL_URL_REGEX_RAW}$")


DIRTY_URL_REGEX_RAW: str = (
    r"(?P<dirty_url>"
    f"({SCHEME_REGEX_RAW}://)?"
    f"({AUTHORITY_REGEX_RAW})?"
    f"(/?{PATH_REGEX_RAW}?)?"
    f"(\?{QUERY_REGEX_RAW})?"
    f"(#{FRAGMENT_REGEX_RAW})?"
    r")"
)
DIRTY_URL_REGEX: re.Pattern[str] = re.compile(f"^{DIRTY_URL_REGEX_RAW}$")


SCP_FULL_LOC_REGEX_RAW: str = (
    r"(?P<scp_full>"
    f"{AUTHORITY_REGEX_RAW}(:{SCP_PATH_REGEX_RAW})?"
    r")"
)
SCP_FULL_LOC_REGEX: re.Pattern[str] = re.compile(f"^{SCP_FULL_LOC_REGEX_RAW}$")

SCP_DIRTY_LOC_REGEX_RAW: str = (
    r"(?P<scp_dirty>"
    f"({AUTHORITY_REGEX_RAW})?(:{SCP_PATH_REGEX_RAW})?"
    r")"
)
SCP_DIRTY_LOC_REGEX: re.Pattern[str] = re.compile(f"^{SCP_DIRTY_LOC_REGEX_RAW}$")


parse_authority = make_parser(
    AUTHORITY_REGEX,
    ["authority", "host", "domain", "ipv4", "ipv6", "username", "password", "port"]
)
"""
Parse the authority segment in a URL and split it into its consituent parts.

Parameters
----------
authority: str
    The authority segment in a URL.

**kwargs: Any
    Keyword arguments to be passed to `extract_groups`.

Returns
-------
Dict[str, Optional[str]]
    The parts of the authority segment.
"""


parse_full_url = make_parser(
    FULL_URL_REGEX, [
        "full_url",
        "scheme",
        "authority",
        "host",
        "domain",
        "ipv4",
        "ipv6",
        "username",
        "password",
        "port",
        "path",
        "query",
        "fragment"
    ]
)
"""
Parse a full URL and split it into its constituent parts.

Parameters
----------
url: str
    The full URL.

**kwargs: Any
    Keyword arguments to be passed to `extract_groups`.

Returns
-------
Dict[str, Optional[str]]
    The parts of the URL.
"""


parse_dirty_url = make_parser(
    DIRTY_URL_REGEX,
    [
        "dirty_url",
        "scheme",
        "authority",
        "host",
        "domain",
        "ipv4",
        "ipv6",
        "username",
        "password",
        "port",
        "path",
        "query",
        "fragment"
    ]
)
"""
Parse a URL (assuming that it was inputted by a lazy human) and split it
into its constituent parts.

Parameters
----------
url: str
    The user-inputted URL.

**kwargs: Any
    Keyword arguments to be passed to `extract_groups`.

Returns
-------
Dict[str, Optional[str]]
    The parts of the URL.
"""


parse_scp_full_loc = make_parser(
    SCP_FULL_LOC_REGEX,
    [
        "scp_full",
        "authority",
        "host",
        "domain",
        "ipv4",
        "ipv6",
        "username",
        "password",
        "path"
    ]
)
"""
Parse a full SCP (secure copy) locator and split it into its constituent parts.

Parameters
----------
url: str
    The full URL.

**kwargs: Any
    Keyword arguments to be passed to `extract_groups`.

Returns
-------
Dict[str, Optional[str]]
    The parts of the locator.
"""


parse_scp_dirty_loc = make_parser(
    SCP_DIRTY_LOC_REGEX,
    [
        "scp_dirty",
        "authority",
        "host",
        "domain",
        "ipv4",
        "ipv6",
        "username",
        "password",
        "path"
    ]
)
"""
Parse a SCP locator (assuming that it was inputted by a lazy human) and split it
into its constituent parts.

Parameters
----------
url: str
    The user-inputted URL.

**kwargs: Any
    Keyword arguments to be passed to `extract_groups`.

Returns
-------
Dict[str, Optional[str]]
    The parts of the locator.
"""
