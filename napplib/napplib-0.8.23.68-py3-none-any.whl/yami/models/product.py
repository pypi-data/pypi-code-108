from typing import List

class YamiBrand:
    """
    Marca dos produtos para Yami
    - Parametros:
    ----------
        - brandId : int
        - name : str
        - description : str
        - isActive : bool, optional - Default: False"""
    brandId : int
    name : str
    description : str
    isActive : bool

    def __init__(self, brandId=None,
                        name='',
                        description=None,
                        isActive=True):
        self.name = name
        self.isActive = isActive

        if brandId:
            self.brandId = brandId
        if description:
            self.description = description

class YamiCategory:
    """
    Categoria dos produtos para Yami
    - Parametros:
    ----------
        - idCategory : int
        - name : str
        - idParent : int
        - active : bool - Default: False"""
    idCategory : int
    name : str
    idParent : int
    active : bool

    def __init__(self, idCategory=None,
                        name='',
                        idParent=0,
                        active=True):
        self.name = name
        self.active = active
        self.idParent = idParent

        if idCategory:
            self.idCategory = idCategory

class YamiProduct:
    """
    Produto Pai para Yami
    - Parametros:
    ----------
        - productId : int
        - brandId : int
        - categoryId : int
        - description : str
        - isActive: bool
        - metaTagDescription : str
        - linkId : str
        - name : str
        - title : str"""
    productId: int
    brandId: int
    categoryId: int
    description: str
    isActive: bool
    metaTagDescription: str
    linkId: str
    name: str
    title: str
    showWithoutStock: bool

    def __init__(self, productId=None,
                        brandId=None,
                        categoryId=None,
                        description='',
                        toActive=True,
                        isVisible=True,
                        metaTagDescription='',
                        linkId='',
                        name='',
                        title='',
                        showWithoutStock=None):
        self.description = description
        self.toActive = toActive
        self.isVisible = isVisible
        self.metaTagDescription = metaTagDescription
        self.linkId = linkId
        self.name = name
        self.title = title

        if productId:
            self.productId = productId
        if categoryId:
            self.categoryId = categoryId
        if brandId:
            self.brandId = brandId
        if showWithoutStock:
            self.showWithoutStock = showWithoutStock

class YamiProductSpecification:
    """
    Especificação do Produto
    - Parametros:
    ---
        - fieldId : int
        - value : str"""
    fieldId: int
    value: str

    def __init__(self, fieldId=0,
                        value='') -> None:
        self.value = value
        self.fieldId = fieldId

class YamiSpecificationGroup:
    """
    Campo da Especificação do Produto
    - Parametros:
    ---
        - id: int
        - name: str
        - categoryId: str"""
    id: int
    name: str
    categoryId: str

    def __init__(self, id=0,
                        name='',
                        categoryId='') -> None:
        self.id = id
        self.name = name
        self.categoryId = categoryId

class YamiSpecificationField:
    """
    Campo da Especificação do Produto
    - Parametros:
    ---
        - name: str
        - fieldId: int
        - desciption: str
        - categoryId: int
        - isActive: bool
        - isRequired: bool
        - fieldType: str
        - isStockKeepingUnit: bool
        - groupId: int"""
    name: str
    fieldId: int
    desciption: str
    categoryId: int
    isActive: bool
    isRequired: bool
    fieldType: str
    isStockKeepingUnit: bool
    groupId: int

    def __init__(self, name='',
                        fieldId=None,
                        desciption=None,
                        categoryId=0,
                        isActive=None,
                        isRequired=None,
                        fieldType='',
                        isStockKeepingUnit=None,
                        groupId=0) -> None:
        self.name=name
        self.categoryId=categoryId
        self.fieldType=fieldType
        self.groupId=groupId

        if fieldId:
            self.fieldId=fieldId
        if desciption:
            self.desciption=desciption
        if isActive:
            self.isActive=isActive
        if isRequired:
            self.isRequired=isRequired
        if isStockKeepingUnit:
            self.isStockKeepingUnit=isStockKeepingUnit

class YamiProductDimension:
    """
    Dimensões do Produto
    - Parametros:
    ---
        - cubic_weight: float
        - height: float
        - width: float
        - length: float
        - weight_kg: float"""
    cubic_weight: float
    height: float
    width: float
    length: float
    weight_kg: float

    def __init__(self, cubic_weight=None,
                        height=None,
                        width=None,
                        length=None,
                        weight_kg=None) -> None:
        if cubic_weight:
            self.cubic_weight = cubic_weight
        if height:
            self.height = height
        if width:
            self.width = width
        if length:
            self.length = length
        if weight_kg:
            self.weight_kg = weight_kg


class YamiProductRealDimension:
    """
    Dimensões Reais do Produto
    - Parametros:
    ---
        - height_real: float
        - width_real: float
        - length_real: float
        - weight_kg_real: float"""
    height_real: float
    width_real: float
    length_real: float
    weight_kg_real: float

    def __init__(self, height_real=None,
                        width_real=None,
                        length_real=None,
                        weight_kg_real=None) -> None:
        if height_real:
            self.height_real = height_real
        if width_real:
            self.width_real = width_real
        if length_real:
            self.length_real = length_real
        if weight_kg_real:
            self.weight_kg_real = weight_kg_real

class YamiSKUProduct:
    """
    Variações do Produto
    - Parametros:
    ---
        - productId: int
        - skuId: int
        - name: str
        - ean: str
        - refId: str
        - detail_url: str
        - modalId: int
        - isKit: bool
        - isActive: bool
        - toActive: bool
        - availability: int
        - skuUnitMultiplier: int
        - dimension: YamiProductDimension
        - realDimension: YamiProductRealDimension
        - specifications: List[YamiProductSpecification]"""
    productId: int
    skuId: int
    name: str
    ean: str
    refId: str
    detailUrl: str
    modalId: int
    isKit: bool
    isActive: bool
    toActive: bool
    availability: int
    skuUnitMultiplier: int
    dimension: YamiProductDimension
    realDimension: YamiProductRealDimension
    specifications: List[YamiProductSpecification]

    def __init__(self, productId=None,
                        skuId=None,
                        name='',
                        ean=None,
                        refId=None,
                        detailUrl='',
                        modalId=None,
                        isKit=False,
                        isActive=True,
                        toActive=True,
                        availability=None,
                        skuUnitMultiplier=None,
                        dimension: YamiProductDimension =None,
                        realDimension: YamiProductRealDimension=None,
                        specifications = None) -> None:
        self.name = name
        self.detailUrl = detailUrl
        self.isKit = isKit
        self.isActive = isActive
        self.toActive = toActive

        if ean:
            self.ean = ean
        if productId:
            self.productId = productId
        if skuId:
            self.skuId = skuId
        if refId:
            self.refId = refId
        if modalId:
            self.modalId = modalId
        if availability:
            self.availability = availability
        if skuUnitMultiplier:
            self.skuUnitMultiplier = skuUnitMultiplier
        if dimension:
            self.dimension = dimension
        if realDimension:
            self.realDimension = realDimension
        if specifications:
            self.specifications = specifications

class YamiImage:
    """
    Imagem do Produto
    - Parametros:
    ---
        - urlImage: str
        - label: str
        - text: str
        - mainImage: str"""
    urlImage: str
    label: str
    text: str
    mainImage: str

    def __init__(self, urlImage='',
                        label='',
                        text='',
                        mainImage='') -> None:
        self.urlImage = urlImage
        self.label = label
        self.text = text
        self.mainImage = mainImage

class YamiInventory:
    """
    Estoque do Produto
    - Parametros:
    ---
        - totalQuantity: int
        - reservedQuantity: int
        - hasUnlimitedQuantity: bool"""
    totalQuantity: int
    reservedQuantity: int
    hasUnlimitedQuantity: bool

    def __init__(self, totalQuantity=0,
                        reservedQuantity=None,
                        hasUnlimitedQuantity=False) -> None:
        self.totalQuantity = totalQuantity
        self.hasUnlimitedQuantity = hasUnlimitedQuantity

        if reservedQuantity:
            self.reservedQuantity = reservedQuantity

class YamiPrice:
    """
    Preço do Produto
    - Parametros:
    ---
        - salesChannel: int, oprional
        - price: float
        - listPrice: float"""
    salesChannel: int
    price: float
    listPrice: float

    def __init__(self, salesChannel=None,
                        price=0,
                        listPrice=0) -> None:
        self.price = price
        self.listPrice = listPrice
        if salesChannel:
            self.salesChannel = salesChannel