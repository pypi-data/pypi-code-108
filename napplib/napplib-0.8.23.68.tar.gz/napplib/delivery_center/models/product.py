from typing import List, overload


class DeliveryCenterImage:
    cover: bool
    url: str
    
    def __init__(self, cover: bool, url: str):
        self.cover = cover
        self.url = url
        

class DeliveryCenterVariantAttribute:
    attribute_code: str
    attribute_value_id: int

    def __init__(self, attribute_code: str, attribute_value_id: int):
        self.attribute_code = attribute_code
        self.attribute_value_id = attribute_value_id


class DeliveryCenterVariant:
    available_quantity: int
    gtin: None
    images: List[DeliveryCenterImage]
    price: int
    sku: int
    variant_attributes: List[DeliveryCenterVariantAttribute]

    def __init__(self, available_quantity: int, gtin: None, images: List[DeliveryCenterImage], price: int, sku: int, variant_attributes: List[DeliveryCenterVariantAttribute]):
        self.available_quantity = available_quantity
        self.gtin = gtin
        self.images = images
        self.price = price
        self.sku = sku
        self.variant_attributes = variant_attributes


class DeliveryCenterProduct:
    brand: str
    category_id: int
    composition: str
    description: str
    external_code: str
    height: int
    length: int
    model: str
    provider_code: str
    store_id: int
    title: str
    variants: List[DeliveryCenterVariant]
    weight: int
    width: int

    def __init__(self, brand: str, category_id: int, composition: str, description: str, external_code: str, height: int, length: int, model: str, provider_code: str, store_id: int, title: str, variants: List[DeliveryCenterVariant], weight: int, width: int):
        self.brand = brand
        self.category_id = category_id
        self.composition = composition
        self.description = description
        self.external_code = external_code
        self.height = height
        self.length = length
        self.model = model
        self.provider_code = provider_code
        self.store_id = store_id
        self.title = title
        self.variants = variants
        self.weight = weight
        self.width = width

class Product:
    product: DeliveryCenterProduct

    def __init__(self, product: DeliveryCenterProduct):
        self.product = product


