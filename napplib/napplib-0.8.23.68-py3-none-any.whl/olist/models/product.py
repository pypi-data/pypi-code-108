from typing import Optional, List, Any


class OlistAttribute:
    attribute_name: str
    attribute_value: str
    category_attribute_id: None

    def __init__(self, attribute_name: str, attribute_value: str, category_attribute_id: None) -> None:
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.category_attribute_id = category_attribute_id


class OlistMeasure:
    height_unit: str
    height_value: str
    length_unit: str
    length_value: str
    weight_unit: str
    weight_value: str
    width_unit: str
    width_value: str
    capacity: Optional[int]

    def __init__(self, height_unit: str, height_value: str, length_unit: str, length_value: str, weight_unit: str, weight_value: str, width_unit: str, width_value: str, capacity: Optional[int]) -> None:
        self.height_unit = height_unit
        self.height_value = height_value
        self.length_unit = length_unit
        self.length_value = length_value
        self.weight_unit = weight_unit
        self.weight_value = weight_value
        self.width_unit = width_unit
        self.width_value = width_value
        self.capacity = capacity


class OlistPhoto:
    order: int
    url: str

    def __init__(self, order: int, url: str) -> None:
        self.order = order
        self.url = url


class OlistPrice:
    channel_slug: str
    currency: str
    minimum_quantity: int
    offer: str
    value: str
    price_freight_shift: str

    def __init__(self, channel_slug: str, currency: str, minimum_quantity: int, offer: str, value: str, price_freight_shift: str) -> None:
        self.channel_slug = channel_slug
        self.currency = currency
        self.minimum_quantity = minimum_quantity
        self.offer = offer
        self.value = value
        self.price_freight_shift = price_freight_shift


class OlistStock:
    availability_days: int
    quantity: int

    def __init__(self, availability_days: int, quantity: int) -> None:
        self.availability_days = availability_days
        self.quantity = quantity


class OlistProduct:
    attributes: List[OlistAttribute]
    availability_days: int
    brand: str
    categories: List[Any]
    description: str
    free_shipping: bool
    gtin: str
    name: str
    origin: str
    package_measures: List[OlistMeasure]
    photos: List[OlistPhoto]
    prices: List[OlistPrice]
    in_campaign: bool
    product_code: int
    product_measures: List[OlistMeasure]
    seller_id: str
    stock: List[OlistStock]
    tags: List[Any]

    def __init__(self, attributes: List[OlistAttribute] = None,
                        availability_days: int = None,
                        brand: str = None,
                        categories: List[Any] = None,
                        description: str = None,
                        free_shipping: bool = None,
                        gtin = None,
                        name: str = None,
                        origin: str = None,
                        package_measures: List[OlistMeasure] = None,
                        photos: List[OlistPhoto] = None,
                        prices: List[OlistPrice] = None,
                        in_campaign: bool = None,
                        product_code: int = None,
                        product_measures: List[OlistMeasure] = None,
                        seller_id: str = None,
                        stock: List[OlistStock] = None,
                        tags: List[Any] = None) -> None:
        self.attributes = attributes
        self.availability_days = availability_days
        self.brand = brand
        self.categories = categories
        self.description = description
        self.free_shipping = free_shipping
        self.gtin = gtin
        self.name = name
        self.origin = origin
        self.package_measures = package_measures
        self.photos = photos
        self.prices = prices
        self.in_campaign = in_campaign
        self.product_code = product_code
        self.product_measures = product_measures
        self.seller_id = seller_id
        self.stock = stock
        self.tags = tags
