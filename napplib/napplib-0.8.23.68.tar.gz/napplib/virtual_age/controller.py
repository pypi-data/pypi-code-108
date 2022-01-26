import re
from typing import Union
from .models.authentication import VirtualAgeAuthentication
from .utils import VirtualAgeRequestWrapper, xmlsoap_to_dict, normalize_datetime
from datetime import datetime

import requests

class VirtualAgeController:
	'''
	Documentação: https://trello-attachments.s3.amazonaws.com/5fecd1d98602685ce3a6554c/6089a08d29b2021bb0bd1723/10964a2aa300353b78bbad23926c1d10/VirtualWebService_Manual_(NOVO).pdf
	'''

	url = 'https://www.bhan.com.br/wbsStoreage/VirtualWsServer.exe/soap/IdmDados'

	offset = 100

	@classmethod
	def _post(cls, authentication: VirtualAgeAuthentication, **kwargs) -> Union[dict, None]:

		payload = VirtualAgeRequestWrapper()
		payload['loginws'] = {
			'cd_loginws': authentication.username,
			'cd_senhaws': authentication.password
		}

		for key, item in kwargs.items():
			if 'acao' not in item:
				item['acao'] = 'con' 

			payload[key] = item

		response = requests.post(cls.url, payload.envelope())

		response = xmlsoap_to_dict(response.content)

		if response and 'erro' in response:
			raise Exception(response['erro'])

		return response


	@classmethod
	def getProduct(cls, authentication: VirtualAgeAuthentication, product_code: Union[int, str]) -> Union[dict, None]:
		params = dict()
		params['cd_produto'] = product_code
		return cls._post(authentication, produto=params)


	@classmethod
	def getChangedProducts(
		cls,
		authentication: VirtualAgeAuthentication,
		start_alteration_date: Union[datetime, str],
		end_alteration_date: Union[datetime, str]
	) -> Union[dict, None]:
		params = dict()
		params['dt_alteracaoini'] = normalize_datetime(start_alteration_date)
		params['dt_alteracaofin'] = normalize_datetime(end_alteration_date)

		return cls._post(authentication, produtoAlteracao=params)


	@classmethod
	def getProductsInfo(
		cls,
		authentication: VirtualAgeAuthentication,
		page: int
	) -> Union[dict, None]:
		if page < 0:
			raise ValueError('"page" must be greater than 0')

		params = dict()
		params['cd_produtoini'] = page * cls.offset - cls.offset
		params['cd_produtofin'] = page * cls.offset

		return cls._post(authentication, produtoInfo=params)


	@classmethod
	def getProductStockChange(
		cls,
		authentication: VirtualAgeAuthentication,
		start_alteration_date: Union[datetime, str],
		end_alteration_date: Union[datetime, str],
	) -> Union[dict, None]:
		params = dict()
		params['dt_alteracaoini'] = normalize_datetime(start_alteration_date)
		params['dt_alteracaofin'] = normalize_datetime(end_alteration_date)

		return cls._post(authentication, produtoSaldoAlteracao=params)


	@classmethod
	def getProductValue(
		cls,
		authentication: VirtualAgeAuthentication,
		product_code: Union[int, str],
		value_code: Union[int, str],
		value_type: str,
	) -> Union[dict, None]:
		if not re.search('^[PC]$', value_type):
			raise ValueError('"value_type" must be either "P" (PREÇO) or "C" (CUSTO)')

		params = dict()
		params['cd_produto'] = product_code
		params['cd_valor'] = value_code
		params['tp_valor'] = value_type.capitalize()

		return cls._post(authentication, produtoValorTipo=params)


	@classmethod
	def getSynthProduct(
		cls,
		authentication: VirtualAgeAuthentication,
		product_code: Union[str, int]
	) -> Union[dict, None]:
		params = dict()
		params['cd_produto'] = product_code

		return cls._post(authentication, produtoCon=params)
