from typing import List

class OpaBoxProductPhoto:
	def __init__(self, url: str, 
						order: int = 0):
		self.url = url
		self.order = order

class OpaBoxProductOptions:
	def __init__(self, id: str, 
						label: str):
		self.id = id
		self.label = label

class OpaBoxProductPresentation:
	def __init__(self, id: str,
						name: str,
						options: List[OpaBoxProductOptions]):
		self.id = id
		self.name = name
		self.options = options 

class OpaBoxProductViewPresentation:
	def __init__(self, option_id: str,
						presentation_id: str):
		self.option_id = option_id
		self.presentation_id = presentation_id

class OpaBoxProductView:
	def __init__(self, id: str,
						active: bool, 
						name: str, 
						price: float, 
						stock_quantity: float,					
						sku: str = None,
						ean: str = '',
						unit_label: str = '',
						unit_quantity: int = 0,
						promotional_price: float = 0,
						view: List[OpaBoxProductViewPresentation] = [],
						photos: List[OpaBoxProductPhoto] = None,
						order: int = 0):
		self.id = id       
		self.active = active
		self.name = name
		self.price = price
		self.stock_quantity = stock_quantity
		self.view = view
		self.sku = sku
		self.ean = ean
		self.unit_label = unit_label
		self.unit_quantity = unit_quantity
		self.promotional_price = promotional_price
		self.photos = photos
		self.order = order

class OpaBoxProduct:
	def __init__(self, active: bool, 
						external_id: str, 
						name: str, 
						price: float,
						stock_quantity: int,
						product_views: List[OpaBoxProductView],
						description: str = '', 
						category_id: str = '',
						category_label: str = '',
						price_cost: float = 0,
						presentations: List[OpaBoxProductPresentation] = [], 
						photos: List[str] = None, 
						updated_at: int = 0,
						order: int = 0):
		self.active = active
		self.external_id = external_id
		self.name = name
		self.price = price
		self.stock = stock_quantity
		self.description = description
		self.category_id = category_id
		self.category_label = category_label
		self.price_cost = price_cost
		self.presentations = presentations
		self.product_views = product_views        
		self.photos = photos
		self.updated_at = updated_at
		self.order = order

class OpaBoxInventory:
	def __init__(self, external_id: str,
						price: float,
						stock: int,
						product_view_id: str = None,
						promotional_price: float = 0,
						price_cost: float = 0):
		self.external_id= external_id
		self.price = price
		self.stock = stock
		self.product_view_id = product_view_id
		self.promotional_price = promotional_price
		self.price_cost = price_cost