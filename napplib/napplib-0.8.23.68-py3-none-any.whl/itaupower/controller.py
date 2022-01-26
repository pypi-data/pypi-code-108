import requests
import json

from .models.product import ItauPowerProduct
from .models.price import ItauPowerPrice
from .models.inventory import ItauPowerInventory


class ItauPowerController:

	@classmethod
	def authentication(cls, url:str, username:str, password:str):
		payload = json.dumps({
			"username": username,
			"password": password
		})
		headers = { 'Content-Type': 'application/json' }

		response = requests.post(f"{url}/integration/admin/token", headers=headers, data=payload)

		print(f"Authentication status: {response.status_code}")
		return response

	@classmethod
	def get_products(cls, url:str, token:str, currentPage:int=0):
		headers = { 'Authorization': f'Bearer {token}' }
		params = {
			"searchCriteria[currentPage]": currentPage,
			"searchCriteria[pageSize]": 100
		}
		response = requests.get(f"{url}/products", headers=headers, params=params)

		if response.status_code == 200 or response.status_code == 201:
			print(f"Get Products: {response.status_code}")
		else:
			print(f"Failed to Get Products: {response.status_code} - {response.text}")

		return response

	@classmethod
	def post_products(cls, url:str, token:str, product:ItauPowerProduct):
		headers = {
			'Authorization': f'Bearer {token}',
  			'Content-Type': 'application/json'
		}
		payload = json.dumps(product, default= lambda a: a.__dict__)
		response = requests.post(f"{url}/products", headers=headers, data=payload)

		if response.status_code == 200 or response.status_code == 201:
			print(f"Post Product: {response.status_code}")
		else:
			print(f"Failed to Post Product: {response.status_code} - {response.text}")

		return response

	@classmethod
	def post_price(cls, url:str, token:str, price:ItauPowerPrice):
		headers = {
			'Authorization': f'Bearer {token}',
  			'Content-Type': 'application/json'
		}
		payload = json.dumps(price, default= lambda a: a.__dict__)
		response = requests.post(f"{url}/products/base-prices/", headers=headers, data=payload)

		if response.status_code == 200 or response.status_code == 201:
			print(f"Post Price: {response.status_code}")
		else:
			print(f"Failed to Post Price: {response.status_code} - {response.text}")

		return response

	@classmethod
	def post_special_price(cls, url:str, token:str, price:ItauPowerPrice):
		headers = {
			'Authorization': f'Bearer {token}',
  			'Content-Type': 'application/json'
		}
		payload = json.dumps(price, default= lambda a: a.__dict__)
		response = requests.post(f"{url}/products/special-prices/", headers=headers, data=payload)

		if response.status_code == 200 or response.status_code == 201:
			print(f"Post Special Price: {response.status_code}")
		else:
			print(f"Failed to Post Special Price: {response.status_code} - {response.text}")

		return response

	@classmethod
	def put_inventory(cls, url:str, token:str, sku_id:str, item_id:str, stock:ItauPowerInventory):
		headers = {
			'Authorization': f'Bearer {token}',
  			'Content-Type': 'application/json'
		}
		payload = json.dumps(stock, default= lambda a: a.__dict__)
		response = requests.put(f"{url}/products/{sku_id}/stockItems/{item_id}", headers=headers, data=payload)

		if response.status_code == 200 or response.status_code == 201:
			print(f"Put Inventory: {response.status_code}")
		else:
			print(f"Failed to Put Inventory: {response.status_code} - {response.text}")

		return response
