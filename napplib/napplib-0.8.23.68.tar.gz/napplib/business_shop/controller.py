import requests
from dataclasses import dataclass
from loguru 	import logger

from napplib.utils import AttemptRequests
from napplib.utils	import LoggerSettings

@logger.catch()
@dataclass
class BusinessShopController():

	business_shop_url: str
	business_shop_token: str
	business_shop_company: str

	limit = 100
	offset = 0
	debug: bool = False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)
	
	@AttemptRequests(success_codes=[200], waiting_time=5)
	def getStocksModified(self,
					start_update_date,
					end_update_date):

		headers = {
			'X-Access-Token': f'{self.business_shop_token}',
			'accept': 'application/json',
		}
				
		params = {
			'datainicial': start_update_date,
			'datafinal': end_update_date,
			'empresa': self.business_shop_company,
		}
		self.offset += self.limit
		return requests.get(f'{self.business_shop_url}/api/v1/estoque/modificados', headers=headers, params=params)
	
	@AttemptRequests(success_codes=[200], waiting_time=5)
	def getProduct(self, sku):
		headers = {
			'X-Access-Token': f'{self.business_shop_token}',
			'accept': 'application/json',
		}
		return requests.get(f'{self.business_shop_url}/api/v1/produtos/{sku}', headers=headers)

	@AttemptRequests(success_codes=[200], waiting_time=5)
	def getPrices(self, sku):
		headers = {
			'X-Access-Token': f'{self.business_shop_token}',
			'accept': 'application/json',
		}
		return requests.get(f'{self.business_shop_url}/api/v1/produtos/{sku}/precos', headers=headers)

