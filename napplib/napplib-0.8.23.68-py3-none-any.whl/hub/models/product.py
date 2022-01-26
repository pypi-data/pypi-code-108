import sys, datetime
sys.path.append("..")
from ..utils import Utils

class PackageDimensions:
    def __init__(self, height='',
                        width='',
                        length='',
                        weigth=''):
        self.height = height
        self.width = width
        self.length = length
        self.weight = weigth

class ProductCategorie:
    def __init__(self, id='',
                        categoryName='',
                        eanProduct='',
                        productCode='',
                        storeId=''):
        self.categoryId = id if id else None
        self.categoryName = Utils.create_values(categoryName, 'String')
        self.eanProduct = Utils.create_values(eanProduct, 'String')
        self.productCode = Utils.create_values(productCode, 'String')
        self.storeId = Utils.create_values(storeId, 'Int64') if storeId else None

class Categorie:
    def __init__(self, id='',
                        name=''):
        self.id = id if id else None
        self.name = name

class CategorieChild:
    def __init__(self, id='',
                        name='',
                        parentCategoryId=''):
        self.id = id if id else None
        self.name = name
        self.parentCategoryId = Utils.create_values(parentCategoryId, 'Int64') if parentCategoryId else None

class ProductBrand:
    def __init__(self, id='',
                        description=''):
        self.id = id if id else None
        self.description = description

class Attribute:
    def __init__(self, id='',
                       name=''):
        self.id = id if id else None
        self.name = name

class AttributeValue:
    def __init__(self, id='',
                        name='',
                        value=''):
        self.id = id if id else None
        self.attributeName = Utils.create_values(name, 'String')
        self.value = value

class ProductAttribute:
    def __init__(self, id='',
                        name='',
                        value='',
                        eanProduct='',
                        productCode='',
                        storeId=''):
        self.id = id if id else None
        self.name = name
        self.value = value
        self.eanProduct = Utils.create_values(eanProduct, 'String')
        self.productCode = Utils.create_values(productCode, 'String')
        self.storeId = Utils.create_values(storeId, 'Int64')

class Image:
    def __init__(self, id=0,
                        productId=0,
                        path="") -> None:
        self.id = id
        self.productId = productId
        self.path = path

class Product:
    def __init__(self,  id='',
                        parentId='',
                        productBrandId='',
                        productBrandName='',
                        skuErp='',
                        name='',
                        description='',
                        NBMOrigin='',
                        cest='',
                        warrantyTime='',
                        active='',
                        codeNCM='',
                        codeISBN='',
                        variation='',
                        mainImageURL='',
                        urlImages='',
                        createdAt='',
                        updatedAt='',
                        productCode='',
                        codeEan='',
                        storeId='',
                        storeProduct='',
                        attributes=[],
                        categories=[],
                        images=[]):
        self.id = id if id else None
        self.parentId = Utils.create_values(parentId, 'Int64') if parentId else None
        self.productBrandId = Utils.create_values(productBrandId, 'Int64') if productBrandId else None
        self.productBrandName = Utils.create_values(productBrandName, 'String')
        self.skuErp = skuErp
        self.name = name
        self.description = description
        self.NBMOrigin = Utils.create_values(NBMOrigin, 'Int64') if NBMOrigin else None
        self.cest = Utils.create_values(cest, 'String')
        self.warrantyTime = Utils.create_values(warrantyTime, 'Int64') if warrantyTime else None
        self.active = active
        self.codeNCM = Utils.create_values(codeNCM, 'String') if codeNCM else None
        self.codeISBN = Utils.create_values(codeISBN, 'String') if codeISBN else None
        self.variation = Utils.create_values(variation, 'String') if variation else None
        self.mainImageURL = Utils.create_values(mainImageURL, 'String') if mainImageURL else None
        self.urlImages = Utils.create_values(urlImages, 'String') if urlImages else None
        self.createdAt = Utils.create_values(createdAt, 'String') if createdAt else None
        self.updatedAt = Utils.create_values(updatedAt, 'String') if updatedAt else None
        self.productCode = Utils.create_values(productCode, 'String')
        self.codeEan = Utils.create_values(codeEan, 'String')
        self.storeId = Utils.create_values(storeId, 'Int64')
        self.storeProduct = storeProduct
        self.attributes = attributes
        self.categories = categories
        self.images = images

class StoreProduct:
    def __init__(self, id='',
                        storeId='',
                        productId='',
                        productCode='',
                        eanProduct='',
                        erpCode='',
                        stockQuantity='',
                        listPrice='',
                        salePrice='',
                        active='',
                        measurementUnit='',
                        createdAt='',
                        updatedAt='',
                        height='',
                        width='',
                        length='',
                        weight='',
                        packageDimensions=''):
        self.id = id if id else None
        self.storeId = storeId
        self.productId = Utils.create_values(productId, 'Int64')
        self.productCode = Utils.create_values(productCode, 'String')
        self.eanProduct = Utils.create_values(eanProduct, 'String')
        self.erpCode = erpCode if erpCode else None
        self.stockQuantity = stockQuantity if stockQuantity else 0.0
        self.listPrice = listPrice if listPrice else 0
        self.salePrice = salePrice if salePrice else 0
        self.active = active if active else False
        self.measurementUnit = Utils.create_values(measurementUnit, 'String')
        self.createdAt = Utils.create_values(createdAt, 'String')
        self.updatedAt = Utils.create_values(updatedAt, 'String')
        self.height = Utils.create_values(height, 'Float64')
        self.width = Utils.create_values(width, 'Float64')
        self.length = Utils.create_values(length, 'Float64')
        self.weight = Utils.create_values(weight, 'Float64')
        self.packageDimensions = Utils.create_values(packageDimensions, 'String')

class StoreProductMarketplace:
    def __init__(self, id='',
                        marketplaceId='',
                        storeProductId='',
                        marketplaceForeignId='',
                        mktPartnerProductId='',
                        active='',
                        listPrice='',
                        salePrice='',
                        stockQuantity='',
                        updatedAt='',
                        marketplaceCategory='',
                        statusProcessing=''):
        self.id = id if id else None
        self.marketplaceId = marketplaceId
        self.storeProductId = storeProductId
        self.marketplaceForeignId = Utils.create_values(marketplaceForeignId, 'String')
        self.mktPartnerProductId = Utils.create_values(mktPartnerProductId, 'Int64')
        self.active = active if active else False
        self.listPrice = Utils.create_values(listPrice, 'Float64')
        self.salePrice = Utils.create_values(salePrice, 'Float64')
        self.stockQuantity = Utils.create_values(stockQuantity, 'Float64')
        self.updatedAt = Utils.create_values(updatedAt, 'String')
        self.marketplaceCategory = Utils.create_values(marketplaceCategory, 'String')
        self.statusProcessing = Utils.create_values(statusProcessing, 'String')

class MarketplaceCategory:
    def __init__(self, id='',
                        categoryDescription='',
                        marketplaceId=''):
        self.id = id if id else None
        self.categoryDescription = categoryDescription
        self.marketplaceId = marketplaceId