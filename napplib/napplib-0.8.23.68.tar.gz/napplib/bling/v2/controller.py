import requests
from datetime import datetime
from typing import Union, Tuple
from dataclasses import dataclass
from .utils import parse_date_filter

from loguru 	import logger

from napplib.utils import AttemptRequests
from napplib.utils	import LoggerSettings

from .models.product import Situation

@logger.catch()
@dataclass
class BlingController():
	apikey: str
	debug: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.apikey, str) or not self.apikey:
			raise TypeError(f'please enter a valid apikey. apikey: {self.apikey}')

		self.endpoint_base = 'https://bling.com.br/Api/v2/'

		self.params = {}
		self.params['apikey'] = self.apikey


	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_products(self, page: str, 
						   situation: Situation = None,
						   with_stock: bool = False,
						   with_image: bool = False,
						   store_code: str = None,
						   change_date: Union[str, datetime, Tuple[str, str], Tuple[datetime, datetime]] = None)  -> requests.Response:

		if not page or page <= 0:
			raise ValueError('"page" must be greater than 0')
		
		headers = {
			'Content-Type'   : 'application/json',
			'Accept-Charset' : 'utf-8',
		}

		request_params = self.params.copy()

		if with_stock:
			request_params['estoque'] = 'S'

		if with_image:
			request_params['imagem'] = 'S'

		if store_code:
			request_params['loja'] = store_code

		if situation:
			request_params['situacao'] = situation.value

		filters = []

		if change_date:
			filters.append(parse_date_filter('dataAlteracao', change_date))

		if filters:
			request_params['filters'] = ';'.join(filters)


		return requests.get(f'{self.endpoint_base}/produtos/page={page}/json/', headers=headers, params=request_params)

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_product_by_code(self, code: str) -> requests.Response:
		headers = {
			'Content-Type'   : 'application/json',
			'Accept-Charset' : 'utf-8',
		}					

		request_params = self.params.copy()

		return requests.get(f'{self.endpoint_base}/produto/{code}/json/', headers=headers, params=request_params)