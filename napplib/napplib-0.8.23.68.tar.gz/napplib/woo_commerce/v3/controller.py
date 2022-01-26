from typing import Optional, Union
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass

from loguru 	import logger

from napplib.utils import AttemptRequests
from napplib.utils	import LoggerSettings

from .models.product import WoocommerceProductStatus, WoocommerceProductType


@logger.catch()
@dataclass
class WooCommerceController:
	'''This is not a static class! 
	Instantiate an object passing the authentications through the constructor

	Documentation: https://woocommerce.github.io/woocommerce-rest-api-docs/'''

	url: str
	consumer_key: str
	consumer_secret: str
	debug: bool = False
	
	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		self.authentication = HTTPBasicAuth(self.consumer_key,self.consumer_secret)

		self.headers = {}
		self.headers['User-Agent'] = 'curl/7.68.0'

		self.api_version = 'v3'

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_products(self, page: int, type: WoocommerceProductType = None,  status: WoocommerceProductStatus = None) -> requests.Response:
		if not page or page <= 0:
			raise ValueError('"page" must be greater than 0')

		params = dict()
		params['page'] = page
		
		if type:
			params['type'] = type.value

		if status:
			params['status'] = status.value

		return requests.get(f'{self.url}/wp-json/wc/{self.api_version}/products/', headers=self.headers, params=params, auth=self.authentication)

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_product_by_id(self, id: str = None) -> requests.Response:
		return requests.get(f'{self.url}/wp-json/wc/{self.api_version}/products/{id}', headers=self.headers, auth=self.authentication)

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_variants_by_id(self, id: str) -> requests.Response:
		return requests.get(f'{self.url}/wp-json/wc/{self.api_version}/products/{id}/variations', headers=self.headers, auth=self.authentication)
