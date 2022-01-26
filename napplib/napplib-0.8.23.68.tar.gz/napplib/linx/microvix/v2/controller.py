import requests
from .models.payload import MicrovixPayload
from datetime import datetime
from torrequest import TorRequest
from dataclasses import dataclass

from loguru 	import logger

from napplib.utils import AttemptRequests
from napplib.utils	import LoggerSettings

@logger.catch()
@dataclass
class MicrovixController():
	user     	: str
	password 	: str
	key      	: str
	cnpj     	: str
	use_tor     : bool = False
	debug	 	: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.user, str):
			raise TypeError(f'Please enter a valid user. User: {self.user}')

		if not isinstance(self.password, str):
			raise TypeError(f'Please enter a valid password. Password: {self.password}')

		if not isinstance(self.key, str):
			raise TypeError(f'Please enter a valid key. Key: {self.key}')

		if not isinstance(self.cnpj, str):
			raise TypeError(f'Please enter a valid cnpj. CNPJ: {self.cnpj}')

		self.payload = MicrovixPayload(
			user=self.user, 
			password=self.password, 
			key=self.key, 
			cnpj=self.cnpj
		)

		self.endpoint_base = 'http://webapi.microvix.com.br/1.0/api/integracao'
		self.headers = { 'Content-Type': 'application/xml' }

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_stocks(self, start_mov_date: datetime = None, end_mov_date: datetime = None):
		if start_mov_date:
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		if end_mov_date:
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		payload = self.payload.copy()
		payload.setCommandName('LinxProdutosDetalhes')

		payload['data_mov_ini'] = start_mov_date
		payload['data_mov_fim'] = end_mov_date

		return self.__make_session().post(self.endpoint_base, headers=self.headers, data=str(payload))

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_price(self, product_id: str):
		payload = self.payload.copy()
		payload.setCommandName('LinxProdutosTabelasPrecos')

		payload['cod_produto'] = product_id
		payload['timestamp'] = None
		
		return self.__make_session().post(self.endpoint_base, headers=self.headers, data=str(payload))

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_stock(self, product_id: str):
		current_date  = str(datetime.now().date())

		payload = self.payload.copy()
		payload.setCommandName('LinxProdutosInventario')
		payload['cod_produto'] = product_id
		payload['data_inventario'] = current_date

		return self.__make_session().post(self.endpoint_base, headers=self.headers, data=str(payload))

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def get_product_attributes(self, product_code: str, start_mov_date: datetime = None, end_mov_date: datetime = None):
		if start_mov_date :
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		if end_mov_date:
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		payload = self.payload.copy()
		payload.setCommandName('LinxProdutosCamposAdicionais')

		payload['data_mov_ini'] = start_mov_date
		payload['data_mov_fim'] = end_mov_date
		payload['cod_produto'] = product_code

		return self.__make_session().post(self.endpoint_base, headers=self.headers, data=str(payload))

	@AttemptRequests(success_codes=[200], attempts=3, waiting_time=3000)
	def get_products(self, product_code: str, start_update_date: datetime = None, end_update_date: datetime = None):

		if start_update_date and isinstance(start_update_date, datetime):
			start_update_date = start_update_date.strftime('%Y-%m-%d')

		if end_update_date and isinstance(end_update_date, datetime):
			end_update_date = end_update_date.strftime('%Y-%m-%d')

		payload = self.payload.copy()
		payload.setCommandName('LinxProdutos')

		payload['dt_update_inicio'] = start_update_date
		payload['dt_update_fim'] = end_update_date
		payload['cod_produto'] = product_code

		return self.__make_session().post(self.endpoint_base, headers=self.headers, data=str(payload))
		
	def __make_session(self):
		if self.use_tor:
			session = TorRequest()
			session.reset_identity()

			return session

		return requests.Session()

