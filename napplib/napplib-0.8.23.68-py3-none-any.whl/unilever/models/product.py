from dataclasses 	import dataclass
from typing 		import List


@dataclass
class UnileverProduct:
	productTitle	: str
	ean				: str
	price			: str
	stockQty		: int
	sku				: str = None
	weight			: str = None


@dataclass
class UnileverProductStock:
	sku			: str
	stockQty	: int


@dataclass
class UnileverProductPrice:
	sku				: str
	price			: str
	originalPrice	: str = None

@dataclass
class UnileverProductList:
	products : List[UnileverProduct]

@dataclass
class UnileverProductStockList:
	products : List[UnileverProductStock]

@dataclass
class UnileverProductPriceList:
	products : List[UnileverProductPrice]
