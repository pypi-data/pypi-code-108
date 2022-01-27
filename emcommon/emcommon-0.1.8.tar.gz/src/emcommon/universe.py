#!/usr/bin/env python3

"""
Universe endpoints
"""

import json
from urllib.parse import urljoin
from emcommon.common import esi_request

class Universe:
    """
    Universe object to access esi endpoints
    """
    def __init__(self):
        self.base_url = "https://esi.evetech.net/latest/universe/"

    def systems(self):
        """ Return a list of all systems"""
        request_url = urljoin(self.base_url, 'systems')
        data = json.loads(esi_request(request_url, "GET"))
        return data

    def regions(self):
        """ Return a list of all regions """
        request_url = urljoin(self.base_url, 'regions')
        data = json.loads(esi_request(request_url, "GET"))
        return data

    def constellations(self):
        """ Return a list of all constellations """
        request_url = urljoin(self.base_url, 'constellations')
        data = json.loads(esi_request(request_url, "GET"))
        return data

    def structures(self):
        """ Return a list of all structures """
        request_url = urljoin(self.base_url, 'structures')
        data = json.loads(esi_request(request_url, "GET"))
        return data
