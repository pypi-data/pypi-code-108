class OpaBoxProductOptions:
    def __init__(self, id='', label=''):
        self.id = id
        self.label = label

class OpaBoxProductPresentation:
    def __init__(self, presentation_name='', id='', name='', options=[]):
        self.id = id
        self.name = name
        self.options = options 

class OpaBoxProductPhoto:
    def __init__(self, url='', order=0):
        self.url = url
        self.order = order

class OpaBoxProductView:
    def __init__(self, option_id='', presentation_id=''):
        self.option_id = option_id
        self.presentation_id = presentation_id

class OpaBoxProductViewData:
    def __init__(self, id='', 
                        active=False, 
                        name='', 
                        order=0,
                        photos=[],
                        price=0, 
                        stock_quantity=0, 
                        unit_label='', 
                        unit_quantity=0,
                        view=[],
                        sku='',
                        ean=''):
        self.id = id       
        self.active = active
        self.name = name
        self.order = order
        self.photos = photos
        self.price = price
        self.stock_quantity = stock_quantity
        self.unit_label = unit_label
        self.unit_quantity = unit_quantity
        self.view = view
        self.sku = sku
        self.ean = ean

class OpaBoxProduct:
    def __init__(self, active=False, 
                        external_id='', 
                        name='', 
                        description='', 
                        order=0, 
                        updated_at='', 
                        photos=[], 
                        presentations=[], 
                        product_views=[],
                        price=None,
                        price_cost=None,
                        stock=None,
                        product_view_id=None,
                        category_id='',
                        category_label=''):
        self.active = active
        self.external_id = external_id
        self.name = name
        self.description = description
        self.order = order
        self.updated_at = updated_at
        self.photos = photos
        self.presentations = presentations
        self.product_views = product_views
        self.category_id = category_id
        self.category_label = category_label
        
        if price:
            self.price = price
        if price_cost:
            self.price_cost = price_cost
        if stock:
            self.stock = stock
        if product_view_id:
            self.product_view_id = product_view_id