import json
from dataclasses 	import dataclass

import requests
from loguru import logger

from .utils				import Environment
from .models.auth		import UnileverAuth
from .models.product	import UnileverProductList, UnileverProductPriceList, UnileverProductStockList
from napplib.utils		import AttemptRequests, unpack_payload_dict, LoggerSettings


@logger.catch()
@dataclass
class UnileverController:
	"""[This function will handle unilever calls..
		All functions will return a requests.Response.
		#* for more information about unilever APIs: http://prod-mmchub-v1.ir-e1.cloudhub.io/erpconsole/
		]

	Args:
		environment		(Environment): [The environment for making requests.].
		debug 		 	(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the environment is not valid, it will raise a TypeError.]
	"""
	environment	: Environment
	debug		: bool	= False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')

		self.headers = {}
		self.headers['Content-Type'] = 'application/json'
		
	def __set_header_authorization(self, token: str):
		self.headers['Authorization'] = f'Basic {token}'

	@AttemptRequests(success_codes=[200])
	def post_auth(self, integrator_token: str, client_token: str):
		auth = UnileverAuth(integratorToken=integrator_token, clientToken=client_token)
		return requests.post(f'{self.environment.value}/auth', headers=self.headers, data=unpack_payload_dict(auth,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product(self, token: str, product_list:UnileverProductList):
		self.__set_header_authorization(token)
		return requests.post(f'{self.environment.value}/products', headers=self.headers, data=unpack_payload_dict(product_list,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_stock(self, token: str, product_stock_list:UnileverProductStockList):
		self.__set_header_authorization(token)
		return requests.post(f'{self.environment.value}/productstock', headers=self.headers, data=unpack_payload_dict(product_stock_list,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_price(self, token: str, product_price_list:UnileverProductPriceList):
		self.__set_header_authorization(token)
		return requests.post(f'{self.environment.value}/productprice', headers=self.headers, data=unpack_payload_dict(product_price_list,remove_null=True))
