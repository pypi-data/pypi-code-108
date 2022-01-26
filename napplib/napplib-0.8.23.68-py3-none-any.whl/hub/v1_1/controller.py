import json
import logging
import requests
from enum import Enum

from typing import Any, List, Union
from .models.product import HubPrice, HubProduct, HubStock, HubStockPrice, HubStoreProductMarketplace, HubStock, HubPrice

class Status(Enum):
    PENDING_REGISTER_PRODUCT = 'pending_register_product'
    DONE                     = 'done'
    PENDING_RECORD_REVIEW    = 'pending_record_review'
    NOT_FOUND_IN_MARKETPLACE = 'not_found_in_marketplace'
    PENDING_STOCK            = 'pending_stock'
    PENDING_CURATORSHIP_NAPP = 'pending_curatorship_napp'

class HubController:

    timeout = (30 * 60) # timeout de 30 minutos 


    @classmethod
    def get_store_product_marketplace_limit(cls, server_url, token, marketplace_id, store_id, page=0, status: Union[Status, str] =None, updated_after=None, limit=20):

        url = '/storeProductsMarketplace/'
        offset = page * limit
        params = {
            "marketplaceId": marketplace_id,
            "storeId": store_id,
            "offset": offset,
            "limit": limit
        }

        if status:
            status = Status(status) if isinstance(status, str) else status
            params["statusProcessing"] = status.value

        if updated_after:
            params["updatedAfter"] = updated_after

        response = cls._request('GET', f"{server_url}{url}", token=token, params=params)

        if response.status_code != 200:
            logging.error(f"/storeProductsMarketplace/ ERROR - {response.status_code} - {response.content if not 'html' in str(response.content) else 'Error'} - {status.value if status else ''}")
            return {
                "total": 0,
                "data": None
            }

        if json.loads(response.content)['total'] == 0:
            logging.info(f"/storeProductsMarketplace/ is empty - {status.value if status else ''}")
            return {
                "total": 0,
                "data": None
            }

        return json.loads(response.content)


    @classmethod
    def patch_store_product_marketplace(cls, server_url, token, storeProducts: List[HubStoreProductMarketplace]):
        return cls._request('PATCH', f'{server_url}/storeProductsMarketplace/?list=true&type=2', token=token, data=storeProducts)


    @classmethod
    def post_products(cls, server_url, token, store_id, products: List[HubProduct]):
        return cls.__post_integrate_products(server_url, token, products, store_id, fillInventory=False)


    @classmethod
    def post_store_products(cls, server_url, token, store_id, products: List[HubProduct]):
        return cls.__post_integrate_products(server_url, token, products, store_id, fillInventory=True)


    @classmethod
    def post_store_products_marketplace(cls, server_url, token, store_id, marketplace_id, products: List[HubProduct]):
        return cls.__post_integrate_products(server_url, token, products, store_id, marketplace_id, fillInventory=True)


    @classmethod
    def __post_integrate_products(cls, server_url, token, products: List[HubProduct], store_id=None, marketplace_id=None, fillInventory=True):

        url = '/integrateProducts/'
        params = {'fillInventory': fillInventory}

        if store_id:
            url += f'{store_id}'

            if marketplace_id:
                url += f'/{marketplace_id}'

        return cls._request('POST', f'{server_url}{url}', token=token, data=products, params=params)


    @classmethod
    def patch_stocks_prices(cls, server_url, token, store_id, marketplace_id, stocksPrices: List[HubStockPrice]):
        return cls.__patch_inventories(server_url, token, store_id, marketplace_id, stocksPrices, 'stockAndPrice')


    @classmethod
    def patch_prices(cls, server_url, token, store_id, marketplace_id, prices: List[HubPrice]):
        return cls.__patch_inventories(server_url, token, store_id, marketplace_id, prices, 'price')


    @classmethod
    def patch_stocks(cls, server_url, token, store_id, marketplace_id, stocks: List[HubStock]):
        return cls.__patch_inventories(server_url, token, store_id, marketplace_id, stocks, 'stock')


    @classmethod
    def __patch_inventories(cls, server_url, token, store_id, marketplace_id, payload, _type):
        return cls._request('PATCH', f'{server_url}/updateInventory/{store_id}/{marketplace_id}/{_type}', token=token, data=payload)


    @classmethod
    def get_total_products_by_store(cls, server_url, token, store_id):

        url = f'/totalProductsByStore/{store_id}'
        return cls._request('GET', f'{server_url}{url}', token=token)


    @classmethod
    def get_products_not_exists(cls, server_url, token, store_id, products=[]):

        url = f'/checkProductsNotExists/{store_id}'
        
        return  cls._request('GET', f'{server_url}{url}', token=token, data=products)


    @classmethod
    def post_update_inventory(cls, server_url, token, store_id, marketplace_id, products=[]):
        url = f'/updateInventory/{store_id}/{marketplace_id}'
        
        return cls._request('POST', f'{server_url}{url}', token=token, data=products)


    @classmethod
    def _request(
        cls,
        method: str,
        url: str,
        token: str,
        additional_headers: Union[dict, None] = None,
        data: Any = None,
        params: dict = None
    ):
        headers = dict()
        headers['Authorization'] = f'Bearer {token}'

        if additional_headers:
            headers = { **headers, **additional_headers }

        try: 
            data = json.dumps(data, default = lambda o: o.__dict__) if not isinstance(data, str) else data
        except json.JSONDecodeError as ex:
            raise ValueError(f'{type(data)} cannot be turned into a json')

        return requests.request(
            method,
            url,
            headers=headers,
            data=data,
            params=params,
            timeout=cls.timeout
        )
