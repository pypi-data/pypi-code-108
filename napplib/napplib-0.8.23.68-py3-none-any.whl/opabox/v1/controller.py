import requests
import json
from typing import List

from .models.product import OpaBoxProduct
from .models.product import OpaBoxInventory

class OpaboxController:

    @staticmethod
    def post_products(server_url: str, company_id: str, token: str, products: List[OpaBoxProduct]):
        headers = dict()
        headers['Content-type'] = 'application/json'

        params = dict()
        params['api_token'] = token

        payload = json.dumps(products, default = lambda o: o.__dict__)
        
        return requests.put(f'{server_url}/prod/v2/company/{company_id}/products', headers=headers, data=payload, params=params)

    @staticmethod
    def put_inventory(server_url: str, company_id: str, token: str, inventory: List[OpaBoxInventory]):
        headers = dict()
        headers['Content-type'] = 'application/json'

        params = dict()
        params['api_token'] = token

        payload = json.dumps(inventory, default = lambda o: o.__dict__)
        
        return requests.post(f'{server_url}/prod/v2/company/{company_id}/products_price_stock', headers=headers, data=payload, params=params) 

    