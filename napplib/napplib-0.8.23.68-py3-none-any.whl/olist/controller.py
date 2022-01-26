import json
import requests

class OlistController:

	def get_access_token(url, code, client_id, client_secret, redirect_uri):
		headers = {}
		headers['Content-Type'] = 'application/x-www-form-urlencoded'

		payload = f"code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code"

		return requests.post(f"{url}/openid/token", data=payload, headers=headers)


	def refresh_access_token(url, client_id, client_secret, refresh_token):
		headers = {}
		headers['Content-Type'] = 'application/x-www-form-urlencoded'

		payload = f"client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token"

		r = requests.post(f"{url}/openid/token", data=payload, headers=headers)
		return r


	def create_product(url, access_token, products):
		headers = {
			"Authorization": f"JWT {access_token}",
			"Accept": "application/json",
			"Content-Type": "application/json"
		}

		payload = json.dumps(products, default = lambda o: o.__dict__)

		r = requests.post(f"{url}/v1/seller-products/", headers=headers, data=payload)
		return r


	def update_product(url, access_token, product, product_sku):
		headers = {
			"Authorization": f"JWT {access_token}",
			"Accept": "application/json",
			"Content-Type": "application/json"
		}

		payload = json.dumps(product, default = lambda o: o.__dict__)

		r = requests.patch(f"{url}/v1/seller-products/{product_sku}/", headers=headers, data=payload)
		return r
