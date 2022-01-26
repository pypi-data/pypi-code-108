import re

from .openapi import V3Api

API_VERSIONS = {
    "v3": V3Api,
}

try:
    from .openapi import V3BetaApi as _V3BetaApi

    # Make any missing method on V3BetaApi dispatch to V3Api, so that
    # v3-beta is a superset of v3.
    class V3BetaApi(_V3BetaApi, V3Api):
        pass

    API_VERSIONS["v3-beta"] = V3BetaApi
except ImportError:
    API_VERSIONS["v3-beta"] = V3Api


try:
    from .openapi import V3AlphaApi as _V3AlphaApi

    # Make any missing method on V3AlphaApi dispatch to V3BetaApi, so that
    # v3-alpha is a superset of v3-beta (which is a superset of v3).
    class V3AlphaApi(_V3AlphaApi, API_VERSIONS["v3-beta"]):
        pass

    API_VERSIONS["v3-alpha"] = V3AlphaApi
except ImportError:
    API_VERSIONS["v3-alpha"] = API_VERSIONS["v3-beta"]


VERSION_REGEX = re.compile(r"(.*)\/v[0-9./]+$")


def host_has_version(host: str):
    return bool(VERSION_REGEX.findall(host))


def host_remove_version(host: str):
    matches = VERSION_REGEX.findall(host)
    if matches:
        return matches[0]
    else:
        return host
