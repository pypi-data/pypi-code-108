from os import utime


from ..utils import Utils


class OrderItem:
    def __init__(self, default_order_id = '', default_order_number = '', default_item_id = '', default_item_sku = '',
                default_item_ean = '', default_item_name = '', default_item_quantity = '', default_item_weight = '',
                default_item_list_price_amount = '', default_item_price_amount = '', default_item_discount_amount = ''):
        self.default_order_id = default_order_id
        self.default_order_number = default_order_number
        self.default_item_id = default_item_id
        self.default_item_sku = default_item_sku
        self.default_item_ean = default_item_ean
        self.default_item_name = default_item_name
        self.default_item_quantity = default_item_quantity
        self.default_item_weight = default_item_weight
        self.default_item_list_price_amount = Utils.convert_to_currency(default_item_list_price_amount)
        self.default_item_price_amount = Utils.convert_to_currency(default_item_price_amount)
        self.default_item_discount_amount = Utils.convert_to_currency(default_item_discount_amount)