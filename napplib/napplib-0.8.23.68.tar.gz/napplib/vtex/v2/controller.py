# build-in imports
import sys
from dataclasses import dataclass
from typing import List

# external imports
import requests
from loguru import logger

# project imports
from napplib.vtex.v2.models.order import VtexOrderInvoice
from napplib.vtex.v2.models.suggestion import VtexSuggestion
from napplib.utils import AttemptRequests
from napplib.utils import LoggerSettings
from napplib.utils import unpack_payload_dict


@logger.catch()
@dataclass
class VtexController:
    """[This controller has the function of executing the calls inside the vtex.
        All functions will return a "request.Response".]

    API Documentation:
        https://developers.vtex.com/vtex-rest-api/reference/manage-suggestions-1#send-sku-suggestion

    Args:
		account_name(str): [Account name for identification.].
		app_key 	(str): [The Authorization Key.].
		app_token 	(str): [The Authorization Token.].
		environment	(Environment): [The environment for making requests.].
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

    Raises:
        TypeError: [If account_name is not informed, it will raise a TypeError.]
        TypeError: [If app_key is not informed, it will raise a TypeError.]
        TypeError: [If app_token is not informed, it will raise a TypeError.]
    """
    account_name: str
    app_key     : str
    app_token   : str
    environment : str
    debug       : bool = False

    def __post_init__(self):
        level = "DEBUG" if self.debug else "INFO"
        LoggerSettings(level=level)

        if not self.account_name:
            raise TypeError("Account name need to be defined")

        if not self.app_key:
            raise TypeError("App key need to be defined")

        if not self.app_token:
            raise TypeError("App token need to be defined")

        if not self.environment:
            self.environment = "vtexcommercestable"

        self.headers = {
            "X-VTEX-API-AppKey": self.app_key,
            "X-VTEX-API-AppToken": self.app_token,
        }

    @AttemptRequests(success_codes=[200, 404])
    def get_order_by_id(self, order_id: str):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/oms/pvt/orders/{order_id}"
        return requests.get(endpoint, headers=headers)

    @AttemptRequests(success_codes=[200])
    def post_invoice(self, order_id: str, invoice: VtexOrderInvoice):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/oms/pvt/orders/{order_id}/invoice"
        return requests.post(endpoint, headers=headers, data=unpack_payload_dict(invoice,remove_null=True))

    @AttemptRequests(success_codes=[200])
    def put_suggestion(self, seller: str, sku: str, suggestion: VtexSuggestion):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        endpoint = f"https://api.vtex.com/{self.account_name}/suggestions/{seller}/{sku}"

        return requests.put(endpoint, headers=headers, data=unpack_payload_dict(suggestion,remove_null=True))

    @AttemptRequests(success_codes=[202])
    def post_notificator_change_stock(self, seller: str, sku: str):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        
        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/notificator/{seller}/changenotification/{sku}/inventory"

        return requests.post(endpoint, headers=headers)

    @AttemptRequests(success_codes=[202])
    def post_notificator_change_price(self, seller: str, sku: str):
        headers = dict(self.headers)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        
        endpoint = f"https://{self.account_name}.{self.environment}.com.br/api/notificator/{seller}/changenotification/{sku}/price"

        return requests.post(endpoint, headers=headers)        
