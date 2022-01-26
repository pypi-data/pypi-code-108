from typing import Optional
import requests
import logging
from dataclasses import dataclass
from time import sleep

from .utils import return_response


@dataclass
class LojaIntegradaController:
	# doc: https://lojaintegrada.docs.apiary.io
	api_key: str
	application_key: str

	def __post_init__(self):
		self._root = 'https://api.awsli.com.br'
		self._params = {
			'format': 'json',
			'chave_api': self.api_key,
			'chave_aplicacao': self.application_key
		}
		self._limit = 20

	@return_response()
	def get_products(self, page: int = 0):
		params = {'limit': self._limit, 'offset': page * self._limit}
		return self._get(f'/api/v1/produto/', params)

	@return_response()
	def get_stocks(self, page: int = 0):
		params = {'limit': self._limit, 'offset': page * self._limit}
		return self._get(f'/api/v1/produto_estoque', params)

	@return_response()
	def get_prices(self, page: int = 0):
		params = {'limit': self._limit, 'offset': page * self._limit}
		return self._get(f'/api/v1/produto_preco', params)

	@return_response()
	def get_product_detail(self, product_id: int):
		return self._get(f'/api/v1/produto/{product_id}')

	@return_response()
	def get_category_detail(self, category_id: int):
		return self._get(f'/api/v1/categoria/{category_id}')

	@return_response()
	def get_brand_detail(self, brand_id: int):
		return self._get(f'/api/v1/marca/{brand_id}')

	@return_response()
	def get_attribute_detail(self, attribute_id: int):
		return self._get(f'/api/v1/grades/{attribute_id}')

	@return_response()
	def get_attribute_value_detail(self, attribute_id: int, value_id: int):
		return self._get(f'/api/v1/grade/{attribute_id}/variacao/{value_id}')


	def _get(self, endpoint, aditional_params: Optional[dict] = None, attempts: int = 10):

		params = self._params.copy()
		if aditional_params:
			for key, value in aditional_params.items():
				params[key] = value

		action = lambda:\
			requests.get(f'{self._root}{endpoint}', params=params) 

		response = None
		for _ in range(attempts):
			response = action()
			if not response or response.status_code == 429: # 429 is throttling status
				logging.error('Waiting for throttling...')
				sleep(10)
				continue
			return response
