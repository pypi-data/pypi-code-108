# build-in imports
from dataclasses 	import dataclass

# external imports
import requests
from loguru 	import logger

# project imports
from napplib.utils		import AttemptRequests
from napplib.utils		import LoggerSettings
from .models.product	import Situation


@logger.catch()
def extra_exception_tiny(response: requests.Response):
	resp_json = response.json()['retorno']
	if str(resp_json['status']).lower() == 'erro':
		return True
	return False


@logger.catch()
@dataclass
class TinyController:
	"""[This function will handle tiny calls V2.0.
		All functions will return a requests.Response.
		for more information
			DOC: https://www.tiny.com.br/ajuda/hall-integracoes]

	Args:
		token 		(str): [The Authorization Token.].
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the environment is not valid, it will raise a TypeError.]
	"""
	token					: str
	debug					: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.token, str) or not self.token:
			raise TypeError(f'please enter a valid token. token: {self.token}')

		self.url = 'https://api.tiny.com.br/api2'

		self.params = {}
		self.params['token'] = self.token
		self.params['formato'] = 'json'


	@AttemptRequests(success_codes=[200], waiting_time=65, extra_exception=extra_exception_tiny)
	def get_product_search(self, page: int, situation: Situation = None):
		if not isinstance(page, int):
			raise TypeError(f'Please enter a valid page, page: {page}')

		request_params = self.params.copy()
		request_params['pagina'] = page

		if situation:
			request_params['situacao'] = situation.value

		return requests.get(f'{self.url}/produtos.pesquisa.php', params=request_params)

	@AttemptRequests(success_codes=[200], waiting_time=65, extra_exception=extra_exception_tiny)
	def get_product(self, id: int):
		request_params = self.params.copy()
		request_params['id'] = id

		return requests.get(f'{self.url}/produto.obter.php', params=request_params)

	@AttemptRequests(success_codes=[200], waiting_time=65, extra_exception=extra_exception_tiny)
	def get_product_stock(self, id: int):
		request_params = self.params.copy()
		request_params['id'] = id

		return requests.get(f'{self.url}/produto.obter.estoque.php', params=request_params)
