from typing import Dict, Union
import os


class ServerConfig:
    __slots__ = ["backend", "ip", "port"]

    def __init__(self, backend: str, ip: str, port: Union[str, int]):
        self.backend = backend
        self.ip = ip
        self.port = port


def parse_server_config(config: Union[Dict, str]) -> ServerConfig:
    if isinstance(config, dict):
        return ServerConfig(config["backend"], config["ip"], config["port"])
    if not (isinstance(config, str) and os.path.exists(config)):
        raise TypeError(f"SERVER_CONFIG must be dict or path string - {config}")

    d = {}
    with open(config) as f:
        for line in f.readlines():
            if not line:
                continue

            key, value = [i.strip() for i in line.split("=", 1)]
            d[key.lower()] = value

    return ServerConfig(d["backend"], d["ip"], d["port"])
