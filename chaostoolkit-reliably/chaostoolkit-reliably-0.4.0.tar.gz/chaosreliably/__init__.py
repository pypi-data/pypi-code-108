import os
from contextlib import contextmanager
from typing import Dict, Generator, List

import httpx
import yaml
from chaoslib.discovery.discover import discover_probes, initialize_discovery_result
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, DiscoveredActivities, Discovery, Secrets
from logzero import logger

__version__ = "0.4.0"
__all__ = ["get_session", "discover"]
RELIABLY_CONFIG_PATH = "~/.config/reliably/config.yaml"
RELIABLY_HOST = "reliably.com"


@contextmanager
def get_session(
    configuration: Configuration = None, secrets: Secrets = None
) -> Generator[httpx.Client, None, None]:
    auth_info = get_auth_info(configuration, secrets)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(auth_info["token"]),
    }
    with httpx.Client() as client:
        client.headers = httpx.Headers(headers)
        client.base_url = httpx.URL(
            f"https://{auth_info['host']}/api/entities/"
            f"{auth_info['org']}/reliably.com/v1"
        )
        yield client


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Reliably capabilities from this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-reliably")

    discovery = initialize_discovery_result(
        "chaostoolkit-reliably", __version__, "reliably"
    )
    discovery["activities"].extend(load_exported_activities())

    return discovery


###############################################################################
# Private functions
###############################################################################
def get_auth_info(
    configuration: Configuration = None, secrets: Secrets = None
) -> Dict[str, str]:
    reliably_config_path = None
    reliably_host = None
    reliably_token = None
    reliably_org = None

    configuration = configuration or {}
    reliably_config_path = os.path.expanduser(
        configuration.get("reliably_config_path", RELIABLY_CONFIG_PATH)
    )
    if reliably_config_path and not os.path.isfile(reliably_config_path):
        reliably_config_path = None

    secrets = secrets or {}
    reliably_token = secrets.get("token")
    reliably_host = secrets.get("host")
    reliably_org = secrets.get("org")

    if not reliably_token and reliably_config_path:
        logger.debug(f"Loading Reliably config from: {reliably_config_path}")
        with open(reliably_config_path) as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as ye:
                raise ActivityFailed(
                    "Failed parsing Reliably configuration at "
                    "'{}': {}".format(reliably_config_path, str(ye))
                )
        reliably_host = reliably_host or RELIABLY_HOST
        logger.debug(f"Connecting to Reliably: {reliably_host}")
        auth_hosts = config.get("auths", {})
        for auth_host, values in auth_hosts.items():
            if auth_host == reliably_host:
                reliably_token = values.get("token")
                break
        current_org = config.get("currentOrg")
        if current_org:
            reliably_org = current_org.get("name")

    if (
        not reliably_config_path
        and not reliably_token
        and not reliably_host
        and not reliably_org
    ):
        raise ActivityFailed(
            "Make sure to login against Reliably's services and/or provide "
            "the correct authentication information to the experiment."
        )

    if not reliably_token:
        raise ActivityFailed(
            "Make sure to provide the Reliably token as a secret or via "
            "the Reliably's configuration's file."
        )

    if not reliably_host:
        raise ActivityFailed(
            "Make sure to provide the Reliably host as a secret or via "
            "the Reliably's configuration's file."
        )

    if not reliably_org:
        raise ActivityFailed(
            "Make sure to provide the current Reliably org as a secret or via "
            "the Reliably's configuration's file."
        )

    return {"host": reliably_host, "token": reliably_token, "org": reliably_org}


def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions, probes and tolerances
    exposed by this extension.
    """
    activities = []
    activities.extend(discover_probes("chaosreliably.slo.probes"))
    activities.extend(discover_probes("chaosreliably.slo.tolerances"))

    return activities
