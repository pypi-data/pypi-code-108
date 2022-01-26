# ---- import external libs ---- #
import requests
from  dataclasses import dataclass
from loguru import logger
from typing import Union
from datetime import datetime

# ---- project imports ---- #
from napplib.utils import AttemptRequests
from napplib.utils import LoggerSettings

from .models.product import ShopifyProductStatus, ShopifyProductPublishedStatus

@logger.catch()
@dataclass
class ShopifyController:

	hostname: str
	apikey: str
	password: str
	debug: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		self.endpoint_base = f'https://{self.apikey}:{self.password}@{self.hostname}/admin/api'

	@AttemptRequests(success_codes=[200], attempts=3)
	def get_all_products(self, since_id:int, limit:int = 250, status: ShopifyProductStatus = None, published_status: ShopifyProductPublishedStatus = None, changed_after: Union[str, datetime] = None):
		params = dict()
		params['limit'] = limit
		
		params['since_id'] = since_id

		if changed_after:
			params['updated_at_min'] = changed_after
		
		if status:
			params['status'] = status.value

		if published_status:
			params['published_status'] = published_status.value
			
		return requests.get(self.endpoint_base + '/2021-10/products.json', params=params)
