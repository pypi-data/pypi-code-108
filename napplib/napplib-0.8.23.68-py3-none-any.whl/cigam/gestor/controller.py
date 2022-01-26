import requests
import json
import logging

from datetime import datetime
from typing import Union, Tuple

from requests.api import head

# ---- documentantion ---- #
# https://documenter.getpostman.com/view/1261739/TzCV45Kw#00658c24-e9c1-4b99-aad8-329b64c2d030

class CigamGestorController:

	@classmethod
	def get_products(cls, url: str, token: str, store: str,access: str, reference: str = None):
		headers = cls.__make_headers(token,access)
		
		params = cls.__make_params(store, reference)

		response = requests.get(f'http://{url}/Gestor.Api.IntegracaoHub/IntegracaoHub/product', headers=headers, params=params)

		if access == '' and response.status_code != 200:
			print('Required Access Key')

		if response.status_code != 200:
			logging.info(f"Error: {response.status_code} - {response.text}")

		try:
			response = response.json()
		except:
			raise Exception('Response returned is not a valid json\n' + response.content.decode('utf-8'))

		return response

	@classmethod
	def get_stocks(cls, url: str, token: str, store: str,access: str, reference: str = None):
		headers = cls.__make_headers(token,access)

		params = cls.__make_params(store, reference)

		response = requests.get(f'http://{url}/Gestor.Api.IntegracaoHub/IntegracaoHub/stock', headers=headers, params=params)

		if access == '' and response.status_code != 200:
			print('Required Access Key')

		if response.status_code != 200:
			logging.info(f"Error: {response.status_code} - {response.text}")

		try:
			response = response.json()
		except:
			raise Exception('Response returned is not a valid json\n' + response.content.decode('utf-8'))

		return response
		
	@classmethod
	def get_prices(cls, url: str, token: str, store: str,access: str, reference: str = None):
		headers = cls.__make_headers(token,access)

		params = cls.__make_params(store, reference)

		response = requests.get(f'http://{url}/Gestor.Api.IntegracaoHub/IntegracaoHub/price', headers=headers, params=params)

		if access == '' and response.status_code != 200:
			print('Required Access Key')
			
		if response.status_code != 200:
			logging.info(f"Error: {response.status_code} - {response.text}")

		try:
			response = response.json()
		except:
			raise Exception('Response returned is not a valid json\n' + response.content.decode('utf-8'))

		return response

	def __make_headers(token: str, access: str):
		headers = dict()
		headers['Content-Type'] = 'application/json'
		headers['Authorization'] = f'Bearer {token}'

		if access != '':
			headers['acesso'] = f'{access}'

		return headers

	def __make_params(store: str, reference: str):
		params = dict()
		params['loja'] = store
		if reference:
			params['referencia'] = reference

		return params
