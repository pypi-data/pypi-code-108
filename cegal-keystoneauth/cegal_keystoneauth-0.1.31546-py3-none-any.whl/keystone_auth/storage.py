# Copyright 2021 Cegal AS
# All rights reserved

import json
from os import makedirs, path

from cegal.keystone_auth import logger as logger


def load_auth_from_file(storage_path):
    try:
        with open(storage_path, "r") as auth:
            token = json.loads(auth.read())
            auth.close()
            return token

    except FileNotFoundError:
        logger.debug("Auth file not found locally")

    return None


def write_auth_to_file(storage_path, id_token, access_token, refresh_token):
    makedirs(path.dirname(storage_path), exist_ok=True)
    token_dict = {
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    with open(storage_path, "wt") as auth:
        tokens = json.dumps(token_dict)
        auth.write(tokens)
