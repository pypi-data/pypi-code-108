#!/usr/bin/env python3

# Just testing out how to access github from python

import urllib.request
import urllib
from vpv import __version__
import socket

def get_latest_github_version():

    socket.setdefaulttimeout(4)
    try:
        response = urllib.request.urlopen('https://github.com/mpi2/vpv/releases/latest', timeout=4)
    except (urllib.request.URLError, IOError):
        print('timed out')
        return False

    resolves_to = response.url
    latest_version = resolves_to.split('/')[-1].strip('v')

    current_version = __version__

    if current_version < latest_version:
        return resolves_to
    else:
        return False
