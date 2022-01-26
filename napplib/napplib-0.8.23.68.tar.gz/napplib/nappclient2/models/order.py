from ..utils import Utils


class Order:
    def __init__(self, default_order_id = '', default_order_number = '', default_date = '', default_total_amount = '',
            default_subtotal_amount = '', default_shipping_amount = '', default_discount_amount = '', default_status = '',
            default_customer_id = '', default_customer_name = '', default_customer_trade_name = '', default_customer_email = '',
            default_customer_cpf = '', default_customer_cnpj = '', default_customer_ie = '', default_customer_phone_1 = '',
            default_customer_phone_2 = '', default_salesperson_id = '', default_salesperson_code = '', default_salesperson_name = '',
            default_salesperson_document = '', default_salesperson_email = '', default_shipping_type = '', default_shipping_address_id = '',
            default_shipping_address_name = '', default_shipping_address_zipcode = '', default_shipping_address_street = '',
            default_shipping_address_number = '', default_shipping_address_complement = '', default_shipping_address_additional_info = '',
            default_shipping_address_neighborhood = '', default_shipping_address_city = '', default_shipping_address_state = '',
            default_shipping_address_country = '', default_payment_id = '', default_payment_type = '', default_payment_name = '',
            default_payment_transaction_id = '', default_payment_installments = '', default_invoice_id = '', default_invoice_number = '',
            default_invoice_serie = '', default_invoice_date = '', default_invoice_amount = '', default_invoice_key = '',
            default_invoice_url_xml = '', default_invoice_url_danfe = '', default_invoice_status = '', default_invoice_cfop = '',
            default_shipping_id = '', default_shipping_tracking_url = '', default_shipping_tracking_number = '',
            default_shipping_method = '', default_shipping_company = '', default_shipping_date_shipped = '', default_shipping_date_delivered = '', default_channel = '', custom_service_amount=''):
        self.default_order_id = default_order_id
        self.default_order_number = default_order_number
        self.default_date = Utils.convert_to_datetime(default_date)
        self.default_total_amount = Utils.convert_to_currency(default_total_amount)
        self.default_subtotal_amount = Utils.convert_to_currency(default_subtotal_amount)
        self.default_shipping_amount = Utils.convert_to_currency(default_shipping_amount)
        self.default_discount_amount = Utils.convert_to_currency(default_discount_amount)
        self.default_status = default_status
        self.default_customer_id = default_customer_id
        self.default_customer_name = default_customer_name
        self.default_customer_trade_name = default_customer_trade_name
        self.default_customer_email = default_customer_email
        self.default_customer_cpf = default_customer_cpf
        self.default_customer_cnpj = default_customer_cnpj
        self.default_customer_ie = default_customer_ie
        self.default_customer_phone_1 = default_customer_phone_1
        self.default_customer_phone_2 = default_customer_phone_2
        self.default_salesperson_id = default_salesperson_id
        self.default_salesperson_code = default_salesperson_code
        self.default_salesperson_name = default_salesperson_name
        self.default_salesperson_document = default_salesperson_document
        self.default_salesperson_email = default_salesperson_email
        self.default_shipping_type = default_shipping_type
        self.default_shipping_address_id = default_shipping_address_id
        self.default_shipping_address_name = default_shipping_address_name
        self.default_shipping_address_zipcode = default_shipping_address_zipcode
        self.default_shipping_address_street = default_shipping_address_street
        self.default_shipping_address_number = default_shipping_address_number
        self.default_shipping_address_complement = default_shipping_address_complement
        self.default_shipping_address_additional_info = default_shipping_address_additional_info
        self.default_shipping_address_neighborhood = default_shipping_address_neighborhood
        self.default_shipping_address_city = default_shipping_address_city
        self.default_shipping_address_state = default_shipping_address_state
        self.default_shipping_address_country = default_shipping_address_country
        self.default_payment_id = default_payment_id
        self.default_payment_type = default_payment_type
        self.default_payment_name = default_payment_name
        self.default_payment_transaction_id = default_payment_transaction_id
        self.default_payment_installments = default_payment_installments
        self.default_invoice_id = default_invoice_id
        self.default_invoice_number = default_invoice_number
        self.default_invoice_serie = default_invoice_serie
        self.default_invoice_date = Utils.convert_to_datetime(default_invoice_date)
        self.default_invoice_amount = Utils.convert_to_currency(default_invoice_amount)
        self.default_invoice_key = default_invoice_key
        self.default_invoice_url_xml = default_invoice_url_xml
        self.default_invoice_url_danfe = default_invoice_url_danfe
        self.default_invoice_status = default_invoice_status
        self.default_invoice_cfop = default_invoice_cfop
        self.default_shipping_id = default_shipping_id
        self.default_shipping_tracking_url = default_shipping_tracking_url
        self.default_shipping_tracking_number = default_shipping_tracking_number
        self.default_shipping_method = default_shipping_method
        self.default_shipping_company = default_shipping_company
        self.default_shipping_date_shipped = Utils.convert_to_datetime(default_shipping_date_shipped)
        self.default_shipping_date_delivered = Utils.convert_to_datetime(default_shipping_date_delivered)
        self.default_channel = default_channel
        self.custom_service_amount = custom_service_amount