#build-in
import requests
from dataclasses import dataclass


@dataclass
class HiperEcommerceController:
	# https://produto.hiper.com.br/documentacao/
	seller_url		: str
	security_key	: str

	def __post_init__(self):
		response = requests.get(f"{self.seller_url}/api/v1/auth/gerar-token/{self.security_key}")

		if response.status_code != 200:
			raise Exception('Login Failed!!')

		self.headers = {'Authorization': f"Bearer {response.json()['token']}"}

	def get_products(self):
		# https://produto.hiper.com.br/documentacao/#1412
		# get all products /produtos/0
		# get updated products /produtos/{pontoDeSincronizacao}
		response = requests.get(f"{self.seller_url}/api/v1/produtos/0", headers=self.headers)

		if response.status_code != 200:
			try:
				response_json = response.json()
				err = response_json['errors']
				msg = response_json['message']
			except:
				err = response.content 
				msg = 'Error to get products'
			raise Exception(f"[{response.status_code}]{msg} - {err}")
		return response

	def get_stock(self, product_id):
		# https://produto.hiper.com.br/documentacao/#1588
		# get current stock products /estoques/0
		# get updated stock products /estoques/{pontoDeSincronizacao}

		params = {"ProdutoId":product_id}
		response = requests.get(f"{self.seller_url}/api/v1/estoques/0", params=params, headers=self.headers)

		if response.status_code != 200:
			try:
				response_json = response.json()
				err = response_json['errors']
				msg = response_json['message']
			except:
				err = response.content 
				msg = 'Error to get stock products'
			raise Exception(f"[{response.status_code}]{msg} - {err}")
		return response
