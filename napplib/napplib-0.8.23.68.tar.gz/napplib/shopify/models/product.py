class ShopifyOptions:
    def __init__(self, name='', values=[]):
        self.name = name
        self.values = values

class ShopifyVariants:
    def __init__(self, option1='', option2='', price='', compare_at_price='', inventory_quantity=None, inventory_management=None, sku='', weight=0):
        self.option1 = option1
        self.option2  = option2
        self.price = price
        self.compare_at_price = compare_at_price
        if inventory_quantity:
            self.inventory_quantity = inventory_quantity
        if inventory_management:
            self.inventory_management = inventory_management
        self.sku = sku
        self.weight = weight

class ShopifyInventory:
    def __init__(self, inventory_item_id='', location_id='', available='', updated_at=''):
        self.inventory_item_id = inventory_item_id
        self.location_id = location_id
        self.available = available
        self.updated_at = updated_at

class ShopifyVariantsPrice:
    def __init__(self, id='', price=''):
        self.id = id
        self.price = price

class ShopifyVariantsPriceData:
    def __init__(self, variant=''):
        self.variant = variant

class ShopifyProductData:
    def __init__(self, title='', body_html='', vendor='', product_type='', variants=[], options=[]):
        self.title = title
        self.body_html = body_html
        self.vendor = vendor
        self.product_type = product_type
        self.variants = variants
        self.options = options

class ShopifyProduct:
    def __init__(self, product_data=''):
        self.product = product_data