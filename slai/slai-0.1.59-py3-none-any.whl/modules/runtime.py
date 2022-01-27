import os
import sys
import yaml

from pathlib import Path
from slai.exceptions import NoCredentialsFound

LOCAL_CREDENTIALS_PATHS = {"global": f"{Path.home()}/.slai/credentials.yml"}


def detect_credentials(*, profile_name="default"):
    credentials = getattr(sys.modules["slai"], "credentials", None)

    if credentials:
        return credentials

    if os.path.exists(LOCAL_CREDENTIALS_PATHS["global"]):
        credentials = _load_credentials(
            path=LOCAL_CREDENTIALS_PATHS["global"], credentials_type="global"
        )
        credentials = credentials.get(profile_name)

        if not credentials:
            raise NoCredentialsFound("no_credentials_found")

    else:
        raise NoCredentialsFound("no_credentials_found")

    return credentials


def _load_credentials(*, path, credentials_type="global"):
    credentials = {}

    with open(path, "r") as f_in:
        try:
            credentials = yaml.safe_load(f_in)
        except yaml.YAMLError:
            raise NoCredentialsFound("slai_invalid_config")

    if credentials_type == "global":
        return credentials

    return credentials
