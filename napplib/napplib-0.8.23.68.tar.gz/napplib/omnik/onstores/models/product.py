from dataclasses import dataclass
from typing import List

@dataclass
class OmnikONStoresProductCode:
    code            : str

@dataclass
class OmnikONStoresSkuCode:
    code            : str

@dataclass
class OmnikONStoresDimension:
    width           : int
    height          : int
    depth           : int
    grossWeight     : int

@dataclass
class OmnikONStoresCategory:
    id              : str
    code            : str

@dataclass
class OmnikONStoresImage:
    link            : str

@dataclass
class OmnikONStoresAttribute:
    name            : str
    value           : str

@dataclass
class OmnikONStoresPrice:
    fromPrice       : float
    price           : float

@dataclass
class OmnikONStoresStock:
    stock           : int
    minStock        : int = 0

@dataclass
class OmnikONStoresSkuData:
    active                  : bool
    sku                     : str
    skuName                 : str
    gtin                    : str = None

@dataclass
class OmnikONStoresSku:
    active                  : bool
    skuData                 : OmnikONStoresSkuData
    codes                   : List[OmnikONStoresSkuCode]
    priceData               : OmnikONStoresPrice
    stockData               : OmnikONStoresStock
    packageDimensionData    : OmnikONStoresDimension
    images                  : List[OmnikONStoresImage]
    attributes              : List[OmnikONStoresAttribute]
    
@dataclass
class OmnikONStoresProductData:
    active                  : bool
    variant                 : bool
    productName             : str
    description             : str
    brand                   : str
    warranty                : int = None

@dataclass
class OmnikONStoresProduct:
    active                 : bool
    productData            : OmnikONStoresProductData
    codes                  : List[OmnikONStoresProductCode]
    productDimensionData   : OmnikONStoresDimension
    packageDimensionData   : OmnikONStoresDimension
    categoryData           : OmnikONStoresCategory
    skus                   : List[OmnikONStoresSku]
    