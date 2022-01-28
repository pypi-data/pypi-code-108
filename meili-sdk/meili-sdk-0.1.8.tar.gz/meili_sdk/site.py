from os import getenv

from meili_sdk.config.utils import safe_load_config


def get_host():
    """
    Get host that the SDK should connect to

    It will look for host in the following order:
    - environment variables
    - ~/.meili/cfg.yaml
    - will default to app.meilirobots.com
    """
    config = safe_load_config()
    site = config.get("site", None) if config else None
    host = getenv("MEILI_HOST") or site or "https://app.meilirobots.com"
    if not host.startswith("http"):
        host = "https://" + host
    return host
