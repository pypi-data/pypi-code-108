# build-in imports
from dataclasses 	import dataclass
from typing 		import List


@dataclass
class YamiBrand:
	name 		: str
	isActive 	: bool	= True
	description : str	= None
	brandId 	: int	= None


@dataclass
class YamiCategory:
	name		: str
	idParent	: int
	active		: bool	= True
	idCategory	: int	= None


@dataclass
class YamiProduct:
	description			: str
	metaTagDescription	: str
	linkId				: str
	name				: str
	title				: str
	toActive			: bool	= True
	isVisible			: bool	= True
	showWithoutStock	: int   = None
	productId			: int   = None
	brandId				: int   = None
	categoryId			: int   = None


@dataclass
class YamiProductSpecification:
	fieldId	: int
	value	: str


@dataclass
class YamiSpecificationGroup:
	id			: int
	name		: str
	categoryId	: str


@dataclass
class YamiSpecificationField:
	name				: str
	categoryId			: int
	fieldType			: str
	groupId				: int
	fieldId				: int
	desciption			: str   = None
	isActive			: bool  = None
	isRequired			: bool  = None
	isStockKeepingUnit	: bool  = None


@dataclass
class YamiProductDimension:
	cubic_weight	: float = None
	height			: float = None
	width			: float = None
	length			: float = None
	weight_kg		: float = None


@dataclass
class YamiProductRealDimension:
	height_real		: float = None
	width_real		: float = None
	length_real		: float = None
	weight_kg_real	: float = None


@dataclass
class YamiSKUProduct:
	name				: str
	detailUrl			: str								= None
	ean					: str 								= None
	refId				: str 								= None
	isKit				: bool								= False
	isActive			: bool								= True
	toActive			: bool								= True
	productId			: int 								= None
	skuId				: int 								= None
	modalId				: int 								= None
	availability		: int 								= None
	skuUnitMultiplier	: int 								= None
	dimension			: YamiProductDimension 				= None
	realDimension		: YamiProductRealDimension 			= None
	specifications		: List[YamiProductSpecification]	= None


@dataclass
class YamiImage:
	urlImage	: str
	mainImage	: str
	label		: str = None
	text		: str = None


@dataclass
class YamiInventory:
	totalQuantity			: int
	hasUnlimitedQuantity	: bool	= False
	reservedQuantity		: int	= None


@dataclass
class YamiPrice:
	price			: float
	listPrice		: float
	salesChannel	: int = None
