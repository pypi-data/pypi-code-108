from ..utils import Utils


class Product:
    def __init__(self, default_product_id = '', default_product_sku = '', default_product_name = '', default_sku_id = '',
            default_sku = '', default_ean = '', default_sku_name = '', default_description = '', default_brand = '',
            default_weight_net = '', default_weigh_m3 = '', default_width = '', default_height = '', default_depth = '',
            default_packing_width = '', default_packing_height = '', default_packing_depth = '', default_category = '',
            default_color = '', default_size = '', default_collection = '', default_origin = '', default_material = '',
            default_model = '', default_gender = '', default_manufacturer = '', default_composition = '',
            default_warranty = '', default_isbnm = '', default_line = '', default_hair_type = '', default_inches = '',
            default_voltage = '', default_plaid = '', default_btu = '', default_publishing_company = '',
            default_edition = '', default_language = '', default_author = '', default_age_range = '',
            default_quantity_of_pieces = '', default_breed_size = '', default_release_year = '', default_sport_club = '',
            default_stock_id = '', default_stock_quantity = '', default_price_id = '', default_list_price = '',
            default_price = '', default_ncm = ''):
        self.default_product_id = default_product_id
        self.default_product_sku = default_product_sku
        self.default_product_name = default_product_name
        self.default_sku_id = default_sku_id
        self.default_sku = default_sku
        self.default_ean = default_ean
        self.default_sku_name = default_sku_name
        self.default_description = default_description
        self.default_brand = default_brand
        self.default_weight_net = default_weight_net
        self.default_weigh_m3 = default_weigh_m3
        self.default_width = default_width
        self.default_height = default_height
        self.default_depth = default_depth
        self.default_packing_width = default_packing_width
        self.default_packing_height = default_packing_height
        self.default_packing_depth = default_packing_depth
        self.default_category = default_category
        self.default_color = default_color
        self.default_size = default_size
        self.default_collection = default_collection
        self.default_origin = default_origin
        self.default_material = default_material
        self.default_model = default_model
        self.default_gender = default_gender
        self.default_manufacturer = default_manufacturer
        self.default_composition = default_composition
        self.default_warranty = default_warranty
        self.default_isbnm = default_isbnm
        self.default_line = default_line
        self.default_hair_type = default_hair_type
        self.default_inches = default_inches
        self.default_voltage = default_voltage
        self.default_plaid = default_plaid
        self.default_btu = default_btu
        self.default_publishing_company = default_publishing_company
        self.default_edition = default_edition
        self.default_language = default_language
        self.default_author = default_author
        self.default_age_range = default_age_range
        self.default_quantity_of_pieces = default_quantity_of_pieces
        self.default_breed_size = default_breed_size
        self.default_release_year = default_release_year
        self.default_sport_club = default_sport_club
        self.default_stock_id = default_stock_id
        self.default_stock_quantity = default_stock_quantity
        self.default_price_id = default_price_id
        self.default_list_price = Utils.convert_to_currency(default_list_price)
        self.default_price = Utils.convert_to_currency(default_price)
        self.default_ncm = default_ncm