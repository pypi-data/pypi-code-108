from typing import List, overload


class MpmsValue:
	value: str

	def __init__(self, value: str):
		self.value = value


class MpmsAttribute:
	id: int
	name: str
	values: List[MpmsValue]

	def __init__(self, id: int, name: str, values: List[MpmsValue]):
		self.id = id
		self.name = name
		self.values = values


class MpmsCategory:
	id: int
	name: str
	parentCategoryId: int
	parentCategory: str

	def __init__(self, id: int, name: str, parentCategoryId: int, parentCategory: str):
		self.id = id
		self.name = name
		self.parentCategoryId = parentCategoryId
		self.parentCategory = parentCategory


class MpmsSellerIntegratorData:
	id: int
	parentId: int
	productBrandName: str
	name: str
	description: str
	cest: str
	active: bool
	codeEAN: str
	codeNCM: int
	mainImageURL: str
	urlImages: List[str]
	productCode: str
	storeId: int
	attributes: List[MpmsAttribute]
	categories: List[MpmsCategory]

	def __init__(self, id: int,
						parentId: int,
						productBrandName: str,
						name: str,
						description: str,
						cest: str,
						active: bool,
						codeEAN: str,
						codeNCM: int,
						mainImageURL: str,
						urlImages: List[str],
						productCode: str,
						storeId: int,
						attributes = [],
						categories = []):
		self.id = id
		self.parentId = parentId
		self.productBrandName = productBrandName
		self.name = name
		self.description = description
		self.cest = cest
		self.active = active
		self.codeEAN = codeEAN
		self.codeNCM = codeNCM
		self.mainImageURL = mainImageURL
		self.urlImages = urlImages
		self.productCode = productCode
		self.storeId = storeId
		self.attributes = attributes
		self.categories = categories


class MpmsShippingDimensions:
	length: str
	width: str
	height: str
	weight: str

	def __init__(self, length: str, width: str, height: str, weight: str):
		self.length = length
		self.width = width
		self.height = height
		self.weight = weight


class MpmsProduct:
	itemid: str
	name: str
	gtins: List[int]
	shippingdimensions: MpmsShippingDimensions
	sellerintegratordataformat: str
	sellerintegratordata: MpmsSellerIntegratorData

	def __init__(self, itemid: str,
						name: str,
						gtins: List[int],
						sellerintegratordataformat: str,
						shippingdimensions: MpmsShippingDimensions,
						sellerintegratordata: MpmsSellerIntegratorData):
		self.itemid = itemid
		self.name = name
		self.gtins = gtins
		self.sellerintegratordataformat = sellerintegratordataformat
		self.shippingdimensions = shippingdimensions
		self.sellerintegratordata = sellerintegratordata

	def json(self):
		return {
			"item-id": self.itemid,
			"name": self.name,
			"gtins": self.gtins,
			"seller-integrator-data-format": self.sellerintegratordataformat,
			"seller-integrator-data": self.sellerintegratordata.__dict__,
			"shipping-dimensions": self.shippingdimensions.__dict__
		}

class MpmsInventory:
	itemid: str
	stockid: str
	physicalquantity: int

	def __init__(self, itemid: str, stockid: str, physicalquantity: int):
		self.itemid = itemid
		self.stockid = stockid
		self.physicalquantity = physicalquantity

	def json(self):
		return {
			"item-id": self.itemid,
			"stock-id": self.stockid,
			"physical-quantity": self.physicalquantity
		}

class MpmsPrice:
	itemid: str
	pricemsrp: str
	price: str

	def __init__(self, itemid: str, pricemsrp: str, price: str):
		self.itemid = itemid
		self.pricemsrp = pricemsrp
		self.price = price

	def json(self):
		return {
			"item-id": self.itemid,
			"price-msrp": self.pricemsrp,
			"price": self.price
		}