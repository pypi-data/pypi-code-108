import requests, json

class FarmaciasAppController:
	@classmethod
	def authenticate(self, server_url, grant_type, client_id, client_secret, scope):
		# def headers
		headers = dict()
		headers['Content-Type'] = 'application/x-www-form-urlencoded'

		# def payload informations
		payload = dict()
		payload['grant-type'] = grant_type
		payload['client_id'] = client_id
		payload['client_secret'] = client_secret
		payload['scope'] = scope
		
		# get token
		r = requests.post(f'{server_url}/oauth2/token',data=payload,headers=headers)

		# catch error
		if r.status_code != 200:
			raise Exception(f'Failed to get TOKEN from Farmacias App. Check the oauth informations. {r.content.decode("utf-8")}')
		
		# parse and return token
		token = json.loads(r.content.decode('utf8'))['access_token']        
		return token

	@classmethod
	def put_offer(self, server_url, token, offer):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'
		headers['Content-Type'] = 'application/json'

		payload = json.dumps(offer, default = lambda o: o.__dict__)

		r = requests.put(f'{server_url}/partner/v1/offer/ean', headers=headers, data=payload)

		return r