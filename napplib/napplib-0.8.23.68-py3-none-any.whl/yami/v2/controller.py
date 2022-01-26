# build-in imports
from dataclasses 	import dataclass
from typing 		import List

# external imports
import requests
from loguru import logger

# project imports
from .models.product	import YamiBrand
from .models.product	import YamiCategory
from .models.product	import YamiImage
from .models.product	import YamiInventory
from .models.product	import YamiPrice
from .models.product	import YamiProduct
from .models.product	import YamiProductSpecification
from .models.product	import YamiSKUProduct
from .models.product	import YamiSpecificationGroup
from .models.product	import YamiSpecificationField
from napplib.utils		import AttemptRequests
from napplib.utils		import unpack_payload_dict
from napplib.utils		import LoggerSettings


@logger.catch()
@dataclass
class YamiController:
	"""[This controller has the function to execute the calls inside the Yami.
		All functions will return a requests.Response.]

	Args:
		account		(str): [Account for identification.].
		token 		(str): [The Authorization Token.].
		timeout		(int, optional): [Time in seconds for timeout.]. Defaults to 1800.
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.
	"""
	account		: str
	token		: str
	timeout		: int	= 1800
	debug		: bool	= False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		self.url = 'https://api.ymi.io/'

		self.headers = {
			'Content-Type'	: 'application/json',
			'Authorization'	: f'Bearer {self.token}',
		}

	def _make_endpoint(self, rote: str, page: int=None):
		endpoint = f'{self.url}{rote}?an={self.account}'
		return endpoint if not page else f'{endpoint}&page={page}'

	def _requests(self, method: str, endpoint: str, data: object=None, remove_null: bool=False, page: int=None):
		endpoint = self._make_endpoint(endpoint, page=page)
		data = unpack_payload_dict(data, remove_null=remove_null) if data else None
		return requests.request(method, endpoint, headers=self.headers, data=data, timeout=self.timeout)

	@AttemptRequests(success_codes=[200,201])
	def post_brand(self, brand: YamiBrand):
		return self._requests('POST', 'catalog/brand', data=brand, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def post_category(self, category: YamiCategory):
		return self._requests('POST', 'catalog/category', data=category, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def post_product(self, product: YamiProduct):
		return self._requests('POST', 'catalog/product/', data=product, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def post_sku(self, sku: YamiSKUProduct):
		return self._requests('POST', 'catalog/sku', data=sku, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def post_specification_group(self, group: YamiSpecificationGroup):
		return self._requests('POST', 'catalog/specification_group', data=group, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def post_specification_field(self, field: YamiSpecificationField):
		return self._requests('POST', 'catalog/specification_field', data=field, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_product_by_id(self, product_id: str, product: YamiProduct):
		return self._requests('PUT', f'catalog/product/{product_id}', data=product, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_sku_by_id(self, sku_id: str, sku: YamiSKUProduct):
		return self._requests('PUT', f'catalog/sku/{sku_id}', data=sku, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_sku_specification_by_id(self, sku_id: str, specification: YamiProductSpecification):
		return self._requests('PUT', f'catalog/sku_specification/{sku_id}', data=specification, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_sku_image_by_id(self, sku_id, images: List[YamiImage]):
		return self._requests('PUT', f'catalog/sku_images/{sku_id}', data=images, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_sku_inventory_by_id(self, warehouse_id, sku_id, inventory: YamiInventory):
		return self._requests('PUT', f'catalog/inventory/{sku_id}/{warehouse_id}', data=inventory, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def put_sku_price_by_id(self, sku_id, price: YamiPrice):
		return self._requests('PUT', f'catalog/price/{sku_id}', data=price, remove_null=True)

	@AttemptRequests(success_codes=[200,201])
	def get_skus_by_page(self, page: int=1):
		return self._requests('GET', f'catalog/skus')
