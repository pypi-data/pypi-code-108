from typing import List


class ProductPrice:
    def __init__(self, price: float,
                        productCode: str,
                        oldPrice: float = None,
                        sellerCode: str = None):
        self.price = price
        self.productCode = productCode
        if oldPrice:
            self.oldPrice = oldPrice
        if sellerCode:
            self.sellerCode = sellerCode


class ProductStock:
    def __init__(self, quantity: int,
                        sellerCode: str,
                        skuCode: str):
        self.quantity = quantity
        self.sellerCode = sellerCode
        self.skuCode = skuCode
