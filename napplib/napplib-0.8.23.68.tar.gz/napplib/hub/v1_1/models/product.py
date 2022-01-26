from typing import List

class HubStoreProductMarketplace:
    def __init__(self, id: int,
                       statusProcessing: str = None,
                       marketplaceForeignId: str = None,
                       mktPartnerProductId: int = None) -> None:
        self.id = id
        if statusProcessing:
            self.statusProcessing = statusProcessing
        if marketplaceForeignId:
            self.marketplaceForeignId = marketplaceForeignId
        if mktPartnerProductId:
            self.mktPartnerProductId = mktPartnerProductId

class HubProductAttibute:
    def __init__(self,  name: str,
                        value: str):
        self.name = name
        self.value = value

class HubProduct:
    def __init__(self,  sku: str,
                        name: str,
                        description: str,
                        brandName: str,
                        warrantyTime: int,
                        salePrice: float,
                        stockQuantity: int,
                        active: bool,
                        ean: str = None,
                        parentSku: str = None,
                        categoryName: str = None,
                        listPrice: float = None,
                        weight: float = None,
                        width: float = None,
                        length: float = None,
                        height: float = None,
                        attributes: List[HubProductAttibute] = None,
                        images: List[str] = None):
        
        self.sku = sku
        self.name = name
        self.description = description
        self.brandName = brandName
        self.warrantyTime = warrantyTime
        self.salePrice = salePrice
        self.stockQuantity = stockQuantity
        self.active = active
        self.ean = ean
        self.parentSku = parentSku
        self.categoryName = categoryName
        self.listPrice = listPrice        
        self.weight = weight
        self.width = width
        self.length = length
        self.height = height
        self.attributes = attributes
        self.images = images

class HubStock:
    def __init__(self, sku: str,
                       stockQuantity: int):
        self.sku = sku
        self.stockQuantity = stockQuantity

class HubPrice:
    def __init__(self, sku: str,
                       salePrice: float,
                       listPrice: float = None):
        self.sku = sku
        self.salePrice = salePrice
        self.listPrice = listPrice

class HubStockPrice:
    def __init__(self, sku: str,
                       stockQuantity: int,
                       salePrice: float,
                       listPrice: float = None):
        self.sku = sku
        self.listPrice = listPrice
        self.salePrice = salePrice
        self.stockQuantity = stockQuantity

class HubUpdateInventory:
    def __init__(self, productCode: str,
                    stock: int,
                    price: float,
                    listPrice: float = None):
        self.productCode = productCode
        self.stock = stock 
        self.price = price
        self.listPrice = listPrice
