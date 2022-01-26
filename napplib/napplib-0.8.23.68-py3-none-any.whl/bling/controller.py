import requests
from datetime import datetime
from typing import Union, Tuple
from .utils import parse_date_filter
class BlingController: 

	url = 'https://bling.com.br/Api/v2/'
	headers = {
	'Content-Type'   : 'application/json',
	'Accept-Charset' : 'utf-8',
	}

	@staticmethod
	def get_products(
		key,
		page,
		storeCode = None,
		inclusion_date: Union[str, datetime, Tuple[str, str], Tuple[datetime, datetime]] = None,
		change_date: Union[str, datetime, Tuple[str, str], Tuple[datetime, datetime]] = None,
	):

		if not page or page < 0:
			raise ValueError('"page" must be greater than 0')

		url = f'{BlingController.url}produtos/page={page}/json/'

		params = dict()
		params['apikey'] = key
		params['estoque'] = 'S'
		params['imagem'] = 'S'

		if storeCode:
			params['loja'] = storeCode

		filters = []

		if inclusion_date:
			filters.append(parse_date_filter('dataInclusao', inclusion_date))

		if change_date:
			filters.append(parse_date_filter('dataAlteracao', change_date))

		if filters:
			params['filters'] = ';'.join(filters)

		response = requests.get(url, headers=BlingController.headers, params=params)

		if response.status_code != 200:
			try:
				error = response.json()
			except:
				raise Exception(response.content)

			raise BlingException(error)

		try:
			response = response.json()
		except:
			raise Exception('Response returned is not a valid json\n' + response.content.decode('utf-8'))

		response = response['retorno']

		products = response['produtos'] if 'produtos' in response else None

		if products:
			products = [ item['produto'] for item in products ]

		return products

class BlingException(Exception):

	def __init__(self, apiResponse: dict):

		erro = apiResponse
		keys = [
			'retorno',
			'erros',
			'erro',
			'msg',
		]
		for key in keys:
			erro = erro[key] if key in erro else erro


		super().__init__(erro)
