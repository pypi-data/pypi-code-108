import requests
from requests import Response
from typing import Union, List
from datetime import datetime

from .models.authentication import VarejoOnlineAuthentication
from .utils import parse_datetime
class VarejoOnlineController:

	url='https://erp.varejonline.com.br/apps'
	headers = { 'Content-Type': "application/json" }
	page_offset = 100


	@classmethod
	def authenticate(cls, authentication: VarejoOnlineAuthentication) -> str:
		response = cls.__post(f'{cls.url}/oauth/token',cls.headers, str(authentication))
		return response.json()


	@classmethod
	def get_products(cls, token: str, page: int, changed_after: Union[str, datetime] = None) -> List[dict]:

		if not isinstance(page, int):
			raise ValueError('page must be a int')

		params = dict()
		params['token'] = token
		if changed_after:
			params['alteradoApos'] = parse_datetime(changed_after)

		cls.__setPage(params, page, cls.page_offset)

		response = cls.__get(f'{cls.url}/api/produtos', cls.headers, params)

		return response.json()


	@classmethod
	def get_stock(cls, token: str, page: int, entity_id: int = None, changed_after: Union[str, datetime] = None) -> List[dict]:

		if not isinstance(page, int):
			raise ValueError('page must be a int')

		params = dict()
		params['token'] = token
		if changed_after:
			params['alteradoApos'] = parse_datetime(changed_after)
		if entity_id:
			params['entidades'] = entity_id

		cls.__setPage(params, page, cls.page_offset)

		response = cls.__get(f'{cls.url}/api/saldos-mercadorias', cls.headers, params)

		return response.json()


	@classmethod
	def get_price_by_table(cls, token: str, table_id: int, page: int, changed_after: Union[str, datetime] = None):
		url = f'{cls.url}/api/tabelas-preco/{table_id}/produtos'

		params = dict()
		params['token'] = token

		if changed_after:
			params['alteradoApos'] = parse_datetime(changed_after)

		cls.__setPage(params, page, cls.page_offset)

		try:

			response = cls.__get(url, cls.headers, params)

		except VarejoOnlineException as ex:

			if ex.error == 'Nenhum registro encontrado':
				return None

			raise ex

		return response.json()


	@classmethod
	def get_price_by_table_by_product_id(cls, token: str, table_id: int, product_id: int):
		url = f'{cls.url}/api/tabelas-preco/{table_id}/produtos/{product_id}'

		params = dict()
		params['token'] = token
		try:

			response = cls.__get(url, cls.headers, params)

		except VarejoOnlineException as ex:

			if ex.error == 'Nenhum registro encontrado':
				return None

			raise ex

		return response.json()


	@classmethod
	def __setPage(cls, params: dict, page: int, offset: int):
		params['quantidade'] = offset
		params['inicio'] = page * offset - offset


	@classmethod
	def __post(cls, url, headers, payload):
		return cls.__request('POST', url, headers, payload)


	@classmethod
	def __get(cls, url, headers, params):
		return cls.__request('GET', url, headers, None, params)


	@staticmethod
	def __request(method, url, headers, payload, params=None):

		response = requests.request(method, url, headers=headers, data=payload, params=params)

		if response.status_code != 200:
			raise VarejoOnlineException(response)

		return response


class VarejoOnlineException(Exception):

	def __init__(self, response):

		self.error = None
		if not isinstance(response, Response):
			super().__init__(response)
			return

		try:
			msg = response.json()
			if 'message' in msg:
				self.error=msg['message']
				super().__init__(msg['message'])
				return

			if 'mensagem' in msg:
				self.error=msg['mensagem']
				super().__init__(msg['mensagem'])
				return
		except:
			super().__init__(response.content.decode('utf-8'))
