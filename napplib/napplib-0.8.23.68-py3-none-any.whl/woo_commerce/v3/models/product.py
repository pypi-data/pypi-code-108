from enum import Enum

class WoocommerceProductType(Enum):
	SIMPLE = 'simple'
	GROUPED = 'grouped'
	EXTERNAL = 'external'
	VARIABLE = 'variable'


class WoocommerceProductStatus(Enum):
	PUBLISH	= 'publish'
	PRIVATE = 'private'
	PENDING = 'pending'
	DRAFT = 'draft'
	ANY	= 'any'
