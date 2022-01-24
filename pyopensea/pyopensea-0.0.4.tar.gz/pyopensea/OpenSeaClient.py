import os
from typing import Tuple, Union

import requests

class OpenSeaClient():

    def __init__(self):
        self.base_url = 'https://api.opensea.io/api/v1/'
        self.session = requests.Session()
    
    def build_params(self, params: dict, module: str):
        query_params = ''
        order_by = params.get("order_by", "sale_date")
        order_direction = params.get("order_direction", "desc")
        offset = params.get("offset", 0)
        limit = abs(params.get("limit", 50))
        if module == "collections":
            query_params = f'asset_owner={params.get("owner", "")}&offset={str(offset)}&limit={str(limit)}'
            return query_params
        if limit > 50 or limit == 0:
            limit = 50
        return f'owner={params.get("owner", "")}&order_direction={order_direction}&offset={str(offset)}&limit={str(limit)}'

    def build_url(self, params: dict, module: str) -> Tuple[bool, str]:
        owner = params.get("owner", None)
        if owner is None:
            return False, "Owner Cannot Be None"
        if module is None:
            return False, "Module Cannot Be None"
        query_params = self.build_params(params=params, module=module)    
        url = f'{self.base_url}{module}/?{query_params}'
        return True, url
    
    def get(self, url: str) -> Tuple[bool, Union[dict, list]]:
        response = self.session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        })
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    
    def get_address_assets(self, params: dict) -> Tuple[bool, str, list]:
        did_pass, url = self.build_url(params, "assets")
        if did_pass is False:
            return did_pass, '', []
        request_did_succeed, response = self.get(url)
        if request_did_succeed is False:
            return request_did_succeed, "request failed",response
        response_parsed = response.get("assets")
        return request_did_succeed, "success", response_parsed
    
    def get_owned_collections(self, params: dict) -> Tuple[bool, str, list]:
        params["offset"] = 0
        params["limit"] = 300
        agg_response = []
        should_continue = True
        while should_continue:
            did_pass, url = self.build_url(params, "collections")
            if did_pass is False:
                return did_pass, url, []
            request_did_succeed, response = self.get(url)
            if request_did_succeed is False:
                return request_did_succeed, "request failed", response
            new_offset = len(response)
            for collection in response:
                agg_response.append(collection)
            params["offset"] = new_offset
            if new_offset == 0 or new_offset < 300:
                return request_did_succeed, "success", agg_response
