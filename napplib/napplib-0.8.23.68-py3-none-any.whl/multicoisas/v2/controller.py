import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass

from loguru import logger

from napplib.utils import AttemptRequests
from napplib.utils	import LoggerSettings

@logger.catch()
@dataclass
class MulticoisasController():
	username: str
	password: str
	debug: bool = False
	
	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.username, str) or not self.username:
			raise TypeError(f'please enter a valid username. username: {self.username}')
		
		if not isinstance(self.password, str) or not self.password:
			raise TypeError(f'please enter a valid password. password: {self.password}')

		self.endpoint_base = 'https://multicoisasnapp.gateway.linkapi.com.br/v1'

		self.authentication = HTTPBasicAuth(self.username,self.password)

		self.headers = {
			'Content-Type'   : 'application/json',
			'Accept-Charset' : 'utf-8',
		}

		self.limit = 256

	@AttemptRequests(success_codes=[200,204], waiting_time=15)
	def get_products(self, page: int) -> requests.Response:

		offset = page * self.limit - self.limit

		return requests.get(f'{self.endpoint_base}/produtosComercial/{offset}/{self.limit}', headers=self.headers,auth=self.authentication)

	@AttemptRequests(success_codes=[200,204], waiting_time=15)
	def get_inventories(self, store_code: int,
							page: int) -> requests.Response:

		offset = page * self.limit - self.limit

		return requests.get(f'{self.endpoint_base}/estoqueDigital/{store_code}/{offset}/{self.limit}', headers=self.headers, auth=self.authentication)