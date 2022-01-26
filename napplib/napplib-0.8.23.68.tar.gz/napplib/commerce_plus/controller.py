import requests


'''	
Documentação

https://app.swaggerhub.com/apis-docs/commerceplus6/commerceplus/1.0.0#/

'''

class CommercePlusController: 

	@staticmethod
	def get_products(user: str, password: str, page: int):

		if not page or page <= 0:
			raise ValueError('"page" must be greater than 0')

		endpoint = f'https://commerceplus.com.br/api/v1/produtos'

		headers = {
		'user'   : user,
		'password' : password,
		}

		params = {
			'pagina' : page
		}
		
		return requests.get(f'{endpoint}', headers=headers, params=params)