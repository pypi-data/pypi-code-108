from typing import List, overload


class DeliveryCenterProductVariant:
    available_quantity: int
    price: int

    def __init__(self, available_quantity: int, price: int):
        self.available_quantity = available_quantity
        self.price = price

class ProductVariant:
    product_variant: DeliveryCenterProductVariant

    def __init__(self, product_variant: DeliveryCenterProductVariant):
        self.product_variant = product_variant
