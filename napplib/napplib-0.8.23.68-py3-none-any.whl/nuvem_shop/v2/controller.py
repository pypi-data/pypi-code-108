import requests

from dataclasses import dataclass
from typing import  Union
from datetime import datetime
from loguru 	import logger
from napplib.utils	import LoggerSettings

from napplib.utils import AttemptRequests
from .models.product import NuvemshopProductPublished

@logger.catch()
@dataclass
class NuvemShopController():

	store_id : str = None
	token : str = None
	debug : bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		self.endpoint_base = f'https://api.nuvemshop.com.br/v1/{self.store_id}'
		self.headers = {}
		self.headers['Authentication'] = f'bearer {self.token}'

	@AttemptRequests(success_codes=[200])
	def get_all_products(self, page: int, limit: int = 100, updated_at_min: Union[str, datetime] = None, published: NuvemshopProductPublished = None):
		if not page or page <= 0:
			raise ValueError('"page" must be greater than 0')

		params = dict()
		params['page'] = page
		params['per_page'] = limit

		if published:
			params['published'] = published.value

		if updated_at_min:
			params['updated_at_min'] = updated_at_min

		request_headers = self.headers.copy()
		request_headers['Content-Type'] = 'application/json'

		return requests.get(f'{self.endpoint_base}/products', headers=request_headers, params=params)

