import requests
import logging
import json

from typing import List

from .models.product import Product
from .models.inventory import ProductPrice
from .models.inventory import ProductStock


# logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")


class LoriController:
	@staticmethod
	def post_autorization_credentials(environment: str, client_id: str, client_secret: str, username: str, password: str, scope: str):
		data = {
			"clientId": client_id,
			"clientSecret": client_secret,
			"username": username,
			"password": password,
			"scope": scope
		}

		route = '/auth/token/anonymous'
		
		response = requests.post(f'https://{environment}.neomode.com.br{route}', data=json.dumps(data))
		if response.status_code == 200:
				logging.info(f'[{response.status_code}]Authorization - Success')
		else:
				logging.warning(f'[{response.status_code}]Authorization - Failed - {response.text}')
		return response

	@staticmethod
	def put_products(environment: str, token: str, products: List[Product]):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		data = json.dumps(products, default=lambda o: o.__dict__)

		route = '/cp/management/catalog/products'
		
		response = requests.put(f'https://{environment}.neomode.com.br{route}', data=data, headers=headers)
		if response.status_code == 204:
			logging.info(f'[{response.status_code}]Product was sent - Success')
		else:
			logging.warning(f'[{response.status_code}]Product has not sent - Failed - {response.text}')
		return response
	
	@staticmethod
	def put_products_prices(environment: str, token: str, prices: List[ProductPrice]):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		data = json.dumps(prices, default=lambda o: o.__dict__)

		route = '/cp/management/catalog/prices'
		
		response = requests.put(f'https://{environment}.neomode.com.br{route}', data=data, headers=headers)
		if response.status_code == 204:
			logging.info(f'[{response.status_code}]Product price was updated - Success')
		elif response.status_code == 401:
			raise Exception(response.text)
		else:
			logging.warning(f'[{response.status_code}]Product price has not updated - Failed - {response.text}')
		return response
	
	@staticmethod
	def put_products_stocks(environment: str, token: str, stocks: List[ProductStock]):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		data = json.dumps(stocks, default=lambda o: o.__dict__)

		route = '/cp/management/catalog/skus/stocks/batch'
		
		response = requests.put(f'https://{environment}.neomode.com.br{route}', data=data, headers=headers)
		if response.status_code == 204:
			logging.info(f'[{response.status_code}]Product stock was updated - Success')
		elif response.status_code == 401:
			raise Exception(response.text)
		else:
			logging.warning(f'[{response.status_code}]Product stock has not updated - Failed - {response.text}')
		return response
