# build-in imports
from dataclasses import dataclass
from typing import List
from enum import Enum

@dataclass
class HubProduct:
	code:			str
	external_id:	str
	name:			str
	is_enabled:		bool
	
@dataclass
class HubSkuAttribute:
	name	: str
	value	: str

@dataclass
class HubSku:
	external_id: 	str
	sku: 		 	str
	name:	 		str
	ean: 			str = None
	description: 	str = None
	weight_net: 	float = None
	weight_m3: 		float = None
	height: 		float = None
	width: 			float = None
	length: 		float = None
	packing_height: float = None
	packing_width: 	float = None
	packing_length: float = None
	cross_docking: 	int = None
	is_enabled: 	bool = None
	category_name: 	str = None
	brand_name: 	str = None
	product: 		HubProduct = None
	attributes: 	List[HubSkuAttribute] = None
	images: 		List[str] = None


@dataclass
class HubSkuPrice:
	price					: float
	list_price				: float
	sku						: str = None
	external_id				: str = None

@dataclass
class HubSkuStock:
	quantity				: int
	sku						: str = None
	external_id				: str = None
	
@dataclass
class HubSkuStatus:
	id				: int
	is_enabled		: bool

class HubParamStatus(Enum):
	ENABLED	= 'ENABLED'
	DISABLED = 'DISABLED'
	ALL = 'ALL'
