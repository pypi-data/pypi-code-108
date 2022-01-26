# build-in
import time
import functools
from dataclasses import dataclass

# external imports
from zeep import Client



def try_request(func):
	attempts = 3

	@functools.wraps(func)
	def wrapper(*args, attempt=1, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as err:
			if attempt == attempts:
				raise Exception(err)
			else:
				time.sleep(1)
				wrapper(*args, **kwargs, attempt=attempt+1)
	return wrapper


@dataclass
class MagentoV1Controller:
	wsdl_url: str
	api_user: str
	api_key	: str

	def __post_init__(self):
		self.client = Client(self.wsdl_url)
		self.sessionId = self.client.service.login(username=self.api_user, apiKey=self.api_key)
		self.session = self.client.service.startSession()

	@try_request
	def get_product_ids(self):
		filter_status = {'type': ''}
		store_view = ''
		products_id = self.client.service.catalogProductList(self.sessionId, filter_status, store_view)
		ids = []
		for product in products_id:
			productId = product['product_id']
			ids.append(productId)
		return ids
	@try_request
	def get_product_skus(self):
		filter_status = {'type': ''}
		store_view = ''
		products_sku = self.client.service.catalogProductList(self.sessionId, filter_status, store_view)
		skus = []
		for product in products_sku:
			productSKU = product['sku']
			skus.append(productSKU)
		return skus

	@try_request
	def get_products(self):
		filter_status = {'type': ''}
		store_view = ''
		return self.client.service.catalogProductList(self.sessionId, filter_status, store_view)

	@try_request
	def get_stock(self, product_sku):
		return self.client.service.catalogInventoryStockItemList(self.sessionId, products=[product_sku])
			
	@try_request
	def get_product_info(self, product_sku):
		return self.client.service.catalogProductInfo(self.sessionId, product_sku, '', '', 'SKU')

	@try_request
	def get_images(self, product_id):
		return self.client.service.catalogProductAttributeMediaList(self.sessionId, product_id, '', '')

	@try_request
	def get_categorie(self, category_id):
		return self.client.service.catalogCategoryTree(self.sessionId, int(category_id), '')

	@try_request
	def get_brands(self, brand_id):
		return self.get_categorie(brand_id)
