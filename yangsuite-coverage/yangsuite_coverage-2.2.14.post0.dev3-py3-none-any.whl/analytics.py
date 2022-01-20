# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# ! /usr/bin/env python
"""Manage queries to servers that contain interesting data."""

import socket
import requests
import docker


def get_docker_container_list(uri=None):
    """Return list of currently running containers.

    Args:
      uri (str): URL to retrieve list from remote server.

    Return:
      (list): Raw list of docker container
    """
    if uri:
        if socket.gethostname().lower() not in uri:
            resp = requests.get(uri)
            resp.raise_for_status()
            return resp.json()
    else:
        client = docker.APIClient()
        return client.containers()
