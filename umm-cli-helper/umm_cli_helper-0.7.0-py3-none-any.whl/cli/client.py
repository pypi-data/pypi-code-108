from typing import Dict, List

import requests

from umm.utils.config import parse_config


def add_request(command: str, tags: List[str]) -> Dict:
    """
    Args:
        command:
        tags:
    Returns:
        response json
    """
    config = parse_config()
    params = {"command": command, "tags": tags}
    resp = requests.get(f"http://0.0.0.0:{config.port}/add", params=params)
    return resp.json()


def umm_request(tags: List[str]) -> Dict:
    """
    Args:
        tags:
    Returns:
        response json
    """
    config = parse_config()
    params = {t: "" for t in tags}
    resp = requests.get(f"http://0.0.0.0:{config.port}/umm", params=params)
    return resp.json()


def confirm_request(id: str) -> Dict:
    """
    Args:
        id:
    Returns:
        response json
    """
    config = parse_config()
    params = dict(id=id)
    resp = requests.get(f"http://0.0.0.0:{config.port}/confirm", params=params)
    return resp.json()
