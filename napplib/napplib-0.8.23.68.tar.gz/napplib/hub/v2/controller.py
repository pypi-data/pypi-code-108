# build-in imports
from dataclasses 	import dataclass
from typing 		import List
from typing 		import Optional

# external imports
import requests
from loguru import logger

# project imports
from .models.catalog	import HubSku, HubParamStatus, HubSkuPrice, HubSkuStock, HubSkuStatus
from .models.channel	import HubChannelType, HubChannelStatus, HubSellerChannelSyncProduct, HubSellerChannelSyncPriceAndStock
from .models.order	    import HubOrder
from .models.message	import HubMessage
from .models.plataform	import HubPlataform
from .utils				import Environment
from napplib.utils		import AttemptRequests
from napplib.utils		import unpack_payload_dict
from napplib.utils		import LoggerSettings


@logger.catch()
@dataclass
class HubController:
	"""[This controller has the function to execute the calls inside the Napp HUB V2.
		All functions will return a requests.Response.]

	Args:
		environment	(Environment): [The environment for making requests.].
		token 		(str): [The Authorization Token.].
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the environment is not valid, it will raise a TypeError.]
		TypeError: [If the token is not valid, it will raise a TypeError.]
		ValueError: [If the token is empty or None, it will raise a ValueError.]
	"""

	environment				: Environment
	token					: str = None
	debug					: bool = False
	endpoint_development	: Optional[str] = None
	
	def __post_init__(self):		
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')

		if not isinstance(self.token, str):
			raise TypeError(f'please enter a valid token. token: {self.token}')

		if not self.token:
			raise ValueError(f'Please provide a token.')

		self.headers = {
			'Authorization': f'Bearer {self.token}'
		}

	@AttemptRequests(success_codes=[200])
	def get_sku_by_id(self, sku_id: str) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/skus/{sku_id}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_price_and_stock_by_external_ids(self, external_seller_id: str, external_channel_id: str, external_sku: str) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/skus/external/{external_sku}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def put_order(self, external_seller_id: str, external_channel_id: str, order: HubOrder) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/orders', headers=self.headers, data=unpack_payload_dict(order,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def get_order_by_id(self, order_id: str) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/orders/{order_id}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_logistics_shipping_fee(self, external_seller_id: str, zip_code: str) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/logistics/zipcode/{zip_code}/shipping/fee', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_seller_channel_type(self, external_seller_id: str, external_channel_id: str, channel_type: HubChannelType) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/type/{channel_type.value}', headers=self.headers)

	@AttemptRequests(success_codes=[204])
	def put_channel_sku_status(self, channel_sku_id: str, channel_status: HubChannelStatus) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/channels/skus/{channel_sku_id}/status', headers=self.headers, data=unpack_payload_dict(channel_status,remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_channel_sku_log(self, channel_sku_id: str, message: HubMessage) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/channels/skus/{channel_sku_id}/logs', headers=self.headers, data=unpack_payload_dict(message,remove_null=True))
	
	@AttemptRequests(success_codes=[204])
	def put_channel_product_status(self, channel_product_id: str, channel_status: HubChannelStatus) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/channels/products/{channel_product_id}/status', headers=self.headers, data=unpack_payload_dict(channel_status,remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_channel_product_log(self, channel_sku_id: str, message: HubMessage) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/channels/products/{channel_sku_id}/logs', headers=self.headers, data=unpack_payload_dict(message,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def get_skus_ids(self, seller_id: int, offset: int, limit: int, status: HubParamStatus) -> requests.Response:
		params = {}
		params['offset'] = offset
		params['limit'] = limit

		if status == HubParamStatus.ENABLED:
			params['filter_sku.is_enabled'] = 'true'

		if status == HubParamStatus.DISABLED:
			params['filter_sku.is_enabled'] = 'false'

		return requests.get(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus/ids', headers=self.headers, params=params)

	@AttemptRequests(success_codes=[200])
	def put_skus_status(self, seller_id: int, sku_status: List[HubSkuStatus]) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus/status', headers=self.headers, data=unpack_payload_dict(sku_status,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def put_skus(self, seller_id: int, skus: List[HubSku]) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus', headers=self.headers, data=unpack_payload_dict(skus,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def put_skus_prices(self, seller_id: str, sku_prices: List[HubSkuPrice]) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus/prices', headers=self.headers, data=unpack_payload_dict(sku_prices,remove_null=True))
	
	@AttemptRequests(success_codes=[200])
	def put_skus_stocks(self, seller_id: str, sku_stocks: List[HubSkuStock]) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/{seller_id}/skus/stocks', headers=self.headers, data=unpack_payload_dict(sku_stocks,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def get_sellers_by_channel_type_and_plataform(self, channel_type: HubChannelType, plataform: HubPlataform) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/sellers/channels/{channel_type.value}/plataforms/{plataform.value}', headers=self.headers)

	@AttemptRequests(success_codes=[200])
	def get_seller_by_external_ids_and_channel_type(self, channel_type: HubChannelType, external_seller_id: str, external_channel_id: str) -> requests.Response:
		return requests.get(f'{self.__get_endpoint_base()}/sellers/{external_seller_id}/channels/{external_channel_id}/type/{channel_type.value}', headers=self.headers)

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_last_product(self, seller_channel_id: str, entity: HubSellerChannelSyncProduct) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/last/products', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_full_product(self, seller_channel_id: str, entity: HubSellerChannelSyncProduct) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/full/products', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_last_price(self, seller_channel_id: str, entity: HubSellerChannelSyncPriceAndStock) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/last/prices', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_full_price(self, seller_channel_id: str, entity: HubSellerChannelSyncPriceAndStock) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/full/prices', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_last_stock(self, seller_channel_id: str, entity: HubSellerChannelSyncPriceAndStock) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/last/stocks', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))

	@AttemptRequests(success_codes=[204])
	def put_seller_by_channel_sync_full_stock(self, seller_channel_id: str, entity: HubSellerChannelSyncPriceAndStock) -> requests.Response:
		return requests.put(f'{self.__get_endpoint_base()}/sellers/channels/{seller_channel_id}/sync/full/stocks', headers=self.headers, data=unpack_payload_dict(entity, remove_null=True))


	def __get_endpoint_base(self): 
		if self.environment == Environment.DEVELOPMENT and self.endpoint_development:
			return self.endpoint_development

		return self.environment.value