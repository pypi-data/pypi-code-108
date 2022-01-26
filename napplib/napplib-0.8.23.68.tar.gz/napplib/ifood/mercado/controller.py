import json
import requests

class IfoodMercadoController:

	@classmethod
	def authenticate(self, url, auth):
		headers = {"Content-Type": "application/json"}
		payload = auth.__dict__

		response = requests.post(f"{url}/api/v1/oauth/token", json=payload, headers=headers)

		return response

	@classmethod
	def create_product(self, url, token, products=[]):
		headers = {
			"Authorization": f"Bearer {token}",
			"Content-Type": "application/json"
		}

		dict_prods = []
		for prod in products:
			if not isinstance(prod, dict):
				dict_prods.append(prod.__dict__)
			else:
				dict_prods.append(prod)

		response = requests.post(f"{url}/api/v1/produtointegracao", json=dict_prods, headers=headers)

		return response