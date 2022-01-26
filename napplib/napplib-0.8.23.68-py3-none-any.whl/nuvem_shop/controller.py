import requests
class NuvemShopController: 

	url = 'https://api.nuvemshop.com.br/v1'
	limit = 100

	@classmethod
	def get_products(
		self,
		store_id, 
		email, 
		token, 
		page, 
		created_at_min = None, # Show Products created after date (yyyy-mm-dd)
		created_at_max = None, # Show Products created before date (yyyy-mm-dd)
		updated_at_min = None, # Show Products last updated after date (yyyy-mm-dd)
		updated_at_max = None # Show Products last updated before date (yyyy-mm-dd)
		):

		headers = {
			'Authentication' : f'bearer {token}',
			'Content-Type'   : 'application/json',
			'User-Agent' : f'MyApp {email}',
			}

		params = dict()
		if created_at_min:
			params['created_at_min'] = created_at_min
		if created_at_max:
			params['created_at_max'] = created_at_max
		if updated_at_min:
			params['updated_at_min'] = updated_at_min
		if updated_at_max:
			params['updated_at_max'] = updated_at_max

		if not page or page < 0:
			raise ValueError('"page" must be greater than 0')

		url_products = f'{self.url}/{store_id}/products?page={page}&per_page={self.limit}'
		
		response = requests.get(url_products, headers=headers, params=params)

		products = response.json()
		
		return products

	@classmethod
	def get_category(
		self,
		store_id, 
		email, 
		token, 
		categ_ig
		):

		headers = {
			'Authentication' : f'bearer {token}',
			'Content-Type'   : 'application/json',
			'User-Agent' : f'MyApp {email}',
			}

		url_categories = f'{self.url}/{store_id}/categories/{categ_ig}'

		response = requests.get(url_categories, headers=headers)

		categories = response.json()

		return categories