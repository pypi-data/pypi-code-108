# -*- coding: future_fstrings -*-
"""
systems type class
"""

import json
import requests
from emcommon.common import esi_request


class System:
    """ An eve online system type"""
    def __init__(self, system_id):
        self.system_id = system_id

    def info(self, field):
        """ Return the typeName for a given type_id"""
        request_url = f"https://esi.evetech.net/latest/universe/systems/{self.system_id}/?datasource=tranquility&language=en"
        data = json.loads(esi_request(request_url, "GET"))
        return data[field]


    def route(self, dest, flag="shortest"):
        """ Return the route info for the two given systems """
        request_url = f"https://esi.evetech.net/latest/route/{self.system_id}/{dest}/?datasource=tranquility&language=en&flag={flag}"
        data = json.loads(esi_request(request_url, "GET"))
        return data