import json
from json.decoder import JSONDecodeError
from logging import exception
import time
from typing import Optional, Union
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass


@dataclass
class WooCommerceController:
	'''This is not a static class! 
	Instantiate an object passing the authentications through the constructor

	Documentation: https://woocommerce.github.io/woocommerce-rest-api-docs/'''

	url: str
	consumer_key: str
	consumer_secret: str
	version: Optional[str] = 'v3'


	def get_product(self, product_code: str = '', page: int = 1) -> Union[list, dict]:
		'''return all products when no product_code is informed'''
		endpoint= f'/wp-json/wc/{self.version}/products/' + product_code

		return self.__request('GET', endpoint, page)


	def __request(self, method: str, endpoint: str, page: int, aditional_headers: Optional[dict] = None, data: Optional[Union[str, dict]] = None):

		headers = {
			'User-Agent':'curl/7.68.0',
		}

		if aditional_headers:
			headers = { **headers, **aditional_headers }

		response = requests.request(method, f'{self.url}{endpoint}?page={page}', headers=headers, data=data, auth=HTTPBasicAuth(self.consumer_key,self.consumer_secret))

		if response is None:
			raise Exception('Response returned "None"')

		if response.status_code not in [ 200, 201 ]:
			raise Exception(f'[{response.status_code}] - {response.text}')

		try:
			return response.json()
		except JSONDecodeError:
			return json.loads(response.content.decode('utf-8-sig'))
