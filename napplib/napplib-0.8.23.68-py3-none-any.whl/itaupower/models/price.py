from typing import List


class Price:
	price: int
	store_id: int
	sku: str
	price_from: str
	price_to: str

	def __init__(self, price: int,
						store_id: int,
						sku: str,
						price_from: str = None,
						price_to: str = None) -> None:
		self.price = price
		self.store_id = store_id
		self.sku = sku
		if price_from:
			self.price_from = price_from
		if price_to:
			self.price_to = price_to


class ItauPowerPrice:
	prices: List[Price]

	def __init__(self, prices: List[Price]) -> None:
		self.prices = prices
