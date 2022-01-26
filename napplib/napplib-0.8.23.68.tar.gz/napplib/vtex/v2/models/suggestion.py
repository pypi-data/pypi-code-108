from dataclasses 	import dataclass
from typing 		import List


@dataclass
class VtexSuggestionImage:
	imageName	: str
	imageUrl	: str


@dataclass
class VtexSuggestionPricing:
	Currency		: str
	SalePrice		: int
	CurrencySymbol	: str


@dataclass
class VtexSuggestionSpecification:
	FieldName	: str
	FieldValues	: List[str]


@dataclass
class VtexSuggestion:
	SkuName							: str
	RefId							: str
	SellerStockKeepingUnitId		: str
	ProductName						: str								= None
	ProductId						: str								= None
	ProductDescription				: str								= None
	BrandName						: str								= None
	SellerId						: str								= None
	Height							: float								= None
	Width							: float								= None
	Length							: float								= None
	WeightKg						: float								= None
	EAN								: str								= None
	CategoryFullPath				: str								= None
	AvailableQuantity				: int								= None
	Images							: List[VtexSuggestionImage]			= None
	Pricing							: VtexSuggestionPricing				= None
	SkuSpecifications				: List[VtexSuggestionSpecification]	= None
	MeasurementUnit					: str								= 'un'
	UnitMultiplier					: int								= 1
