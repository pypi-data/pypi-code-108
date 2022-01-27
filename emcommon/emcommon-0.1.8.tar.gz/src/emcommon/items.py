# -*- coding: future_fstrings -*-
"""
inventory type class
"""


import json
import requests
from emcommon.common import esi_request


class Item:
    """ An eve online inventory type"""
    def __init__(self, type_id):
        self.type_id = type_id

    def type_id(self):
        """ Just return the type_id """
        return self.type_id

    def info(self, field):
        """ Return the typeName for a given type_id"""
        request_url = f"https://esi.evetech.net/latest/universe/types/{self.type_id}/?datasource=tranquility&language=en"
        data = json.loads(esi_request(request_url, "GET"))
        return data[field]

    def orders(self, system_id=None):
        """ Return a list of orders for this type_id"""
        if system_id is None:
            request_url = f"https://api.eve-market.net/orders?item_id={self.type_id}"
        else:
            request_url = f"https://api.eve-market.net/orders?item_id={self.type_id}&system_id={system_id}"
        data = json.loads(requests.get(request_url).text)
        return data

    def price(self, system_id=30000142):
        """ Return the price for this type_id. Defaults to Jita """
        request_url = f"https://api.eve-market.net/get_adjusted_market_price?type_id={self.type_id}&market={system_id}"
        data = json.loads(requests.get(request_url).text)
        return data
