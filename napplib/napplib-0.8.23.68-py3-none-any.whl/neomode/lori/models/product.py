from typing import List


class CategoryItem:
    def __init__(self, code: str = "",
                        name: str = "",
                        isActive: bool = True):
        self.code = code
        self.name = name
        self.isActive = isActive


class Category:
    def __init__(self, code: str = "",
                        name: str = "",
                        isActive: bool = True,
                        children: List[CategoryItem] = []):
        self.code = code
        self.name = name
        self.isActive = isActive
        self.children = children


class Image:
    def __init__(self, order: int,
                        imageUrl: str):
        self.order = order
        self.imageUrl = imageUrl


class Attribute:
    def __init__(self,  title: str,
                        value: str
                        ):
        self.title = title
        self.value = value


class Sku:
    def __init__(self, code: str,
                        name: str,
                        isActive: bool,
                        barcode: str = "",
                        images: List[Image] = [],
                        Attributes: List[Attribute] = []):
        self.code = code
        self.name = name
        self.isActive = isActive
        self.barcode = barcode
        self.images = images
        self.Attributes = Attributes


class Product:
    def __init__(self, name: str,
                        code: str,
                        isActive: bool,
                        auxCode: str = "",
                        referenceCode: str = "",
                        description: str = "",
                        keywords: str = "",
                        weight: float = 0.0,
                        height: float = 0.0,
                        lenght: float = 0.0,
                        width: float = 0.0,
                        releaseDate: str = "",
                        categories: List[Category] = [],
                        images: List[Image] = [],
                        skus: List[Sku] = []):
        self.name = name
        self.code = code
        self.isActive = isActive
        self.auxCode = auxCode
        self.referenceCode = referenceCode
        self.description = description
        self.keywords = keywords
        self.weight = weight
        self.height = height
        self.lenght = lenght
        self.width = width
        self.releaseDate = releaseDate
        self.categories = categories
        self.images = images
        self.skus = skus