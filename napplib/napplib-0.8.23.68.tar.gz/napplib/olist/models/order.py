from typing import List, Any
from datetime import datetime
from uuid import UUID


class OlistAddress:
    address: str
    city: str
    complement: str
    country: str
    district: str
    full_address: str
    number: int
    reference: str
    state: str
    zip_code: int

    def __init__(self, address: str, city: str, complement: str, country: str, district: str, full_address: str, number: int, reference: str, state: str, zip_code: int) -> None:
        self.address = address
        self.city = city
        self.complement = complement
        self.country = country
        self.district = district
        self.full_address = full_address
        self.number = number
        self.reference = reference
        self.state = state
        self.zip_code = zip_code


class OlistPhone:
    phone: str
    phone_type: str

    def __init__(self, phone: str, phone_type: str) -> None:
        self.phone = phone
        self.phone_type = phone_type


class OlistCustomer:
    address: OlistAddress
    document_number: str
    email: str
    name: str
    phones: List[OlistPhone]
    birth_date: None

    def __init__(self, address: OlistAddress, document_number: str, email: str, name: str, phones: List[OlistPhone], birth_date: None) -> None:
        self.address = address
        self.document_number = document_number
        self.email = email
        self.name = name
        self.phones = phones
        self.birth_date = birth_date


class OlistPaymentMethod:
    installments: int
    payment_type: str
    sequential: int
    value: str

    def __init__(self, installments: int, payment_type: str, sequential: int, value: str) -> None:
        self.installments = installments
        self.payment_type = payment_type
        self.sequential = sequential
        self.value = value


class OlistSellerOrderHistory:
    cancelation_reason: str
    cancelation_status: str
    created_at: datetime
    status: str
    suspension_reason: str

    def __init__(self, cancelation_reason: str, cancelation_status: str, created_at: datetime, status: str, suspension_reason: str) -> None:
        self.cancelation_reason = cancelation_reason
        self.cancelation_status = cancelation_status
        self.created_at = created_at
        self.status = status
        self.suspension_reason = suspension_reason


class OlistHistory:
    id: UUID
    created_at: datetime
    status: str

    def __init__(self, id: UUID, created_at: datetime, status: str) -> None:
        self.id = id
        self.created_at = created_at
        self.status = status


class OlistProductAttribute:
    modelo: str

    def __init__(self, modelo: str) -> None:
        self.modelo = modelo


class OlistOrderSellerOrderItem:
    availability_days: int
    carrier: str
    channel_slug: str
    code: str
    commission_freight_olist: str
    commission_product_olist: str
    enable_subsidy: bool
    currency: str
    id: UUID
    item_commission: str
    freight_commission: str
    freight_mode: str
    freight_value: str
    full_name: str
    price: str
    price_freight_shift: str
    product_attributes: List[OlistProductAttribute]
    product_gtin: str
    product_photo: str
    product_sku: str
    seller_id: UUID
    seller_order: UUID
    seller_product_code: str
    status: str
    total_commission: str
    price_discount: None
    history: List[OlistHistory]

    def __init__(self, availability_days: int, carrier: str, channel_slug: str, code: str, commission_freight_olist: str, commission_product_olist: str, enable_subsidy: bool, currency: str, id: UUID, item_commission: str, freight_commission: str, freight_mode: str, freight_value: str, full_name: str, price: str, price_freight_shift: str, product_attributes: List[ProductAttribute], product_gtin: str, product_photo: str, product_sku: str, seller_id: UUID, seller_order: UUID, seller_product_code: str, status: str, total_commission: str, price_discount: None, history: List[History]) -> None:
        self.availability_days = availability_days
        self.carrier = carrier
        self.channel_slug = channel_slug
        self.code = code
        self.commission_freight_olist = commission_freight_olist
        self.commission_product_olist = commission_product_olist
        self.enable_subsidy = enable_subsidy
        self.currency = currency
        self.id = id
        self.item_commission = item_commission
        self.freight_commission = freight_commission
        self.freight_mode = freight_mode
        self.freight_value = freight_value
        self.full_name = full_name
        self.price = price
        self.price_freight_shift = price_freight_shift
        self.product_attributes = product_attributes
        self.product_gtin = product_gtin
        self.product_photo = product_photo
        self.product_sku = product_sku
        self.seller_id = seller_id
        self.seller_order = seller_order
        self.seller_product_code = seller_product_code
        self.status = status
        self.total_commission = total_commission
        self.price_discount = price_discount
        self.history = history


class OlistMeasures:
    height_unit: str
    height_value: str
    id: UUID
    length_unit: str
    length_value: str
    measures_id: UUID
    weight_unit: str
    weight_value: str
    width_unit: str
    width_value: str

    def __init__(self, height_unit: str, height_value: str, id: UUID, length_unit: str, length_value: str, measures_id: UUID, weight_unit: str, weight_value: str, width_unit: str, width_value: str) -> None:
        self.height_unit = height_unit
        self.height_value = height_value
        self.id = id
        self.length_unit = length_unit
        self.length_value = length_value
        self.measures_id = measures_id
        self.weight_unit = weight_unit
        self.weight_value = weight_value
        self.width_unit = width_unit
        self.width_value = width_value


class OlistRate:
    carrier_name: str
    carrier_slug: str
    cost: str
    currency: str
    rate_id: UUID
    carrier_address: str
    carrier_cnpj: str
    carrier_ie: str

    def __init__(self, carrier_name: str, carrier_slug: str, cost: str, currency: str, rate_id: UUID, carrier_address: str, carrier_cnpj: str, carrier_ie: str) -> None:
        self.carrier_name = carrier_name
        self.carrier_slug = carrier_slug
        self.cost = cost
        self.currency = currency
        self.rate_id = rate_id
        self.carrier_address = carrier_address
        self.carrier_cnpj = carrier_cnpj
        self.carrier_ie = carrier_ie


class OlistVolumeSellerOrderItem:
    id: UUID

    def __init__(self, id: UUID) -> None:
        self.id = id


class OlistVolume:
    code: str
    enabled: bool
    expected_financial_transfer: str
    id: UUID
    invoice: None
    limit_action_date: None
    measures: OlistMeasures
    parents: List[Any]
    rate: OlistRate
    seller_order_items: List[OlistVolumeSellerOrderItem]
    shipment: None
    status: str
    total_commission: str
    total_freight_value: str
    total_invoice: str
    total_price_freight_shift: str
    value: str

    def __init__(self, code: str, enabled: bool, expected_financial_transfer: str, id: UUID, invoice: None, limit_action_date: None, measures: Measures, parents: List[Any], rate: Rate, seller_order_items: List[VolumeSellerOrderItem], shipment: None, status: str, total_commission: str, total_freight_value: str, total_invoice: str, total_price_freight_shift: str, value: str) -> None:
        self.code = code
        self.enabled = enabled
        self.expected_financial_transfer = expected_financial_transfer
        self.id = id
        self.invoice = invoice
        self.limit_action_date = limit_action_date
        self.measures = measures
        self.parents = parents
        self.rate = rate
        self.seller_order_items = seller_order_items
        self.shipment = shipment
        self.status = status
        self.total_commission = total_commission
        self.total_freight_value = total_freight_value
        self.total_invoice = total_invoice
        self.total_price_freight_shift = total_price_freight_shift
        self.value = value


class OlistOrder:
    approved_at: datetime
    availability_days: int
    branded_store_slug: str
    cancelation_reason: str
    cancelation_status: str
    channel_slug: str
    channel_store: str
    code: str
    count_items: int
    created_at: datetime
    currency: str
    customer: OlistCustomer
    delivered_customer_date: None
    estimated_delivery_date: datetime
    invoice_danfe_url: str
    invoice_error_message: str
    invoice_id: None
    invoice_issue_date: None
    invoice_key: str
    invoice_number: int
    invoice_serial_number: int
    invoice_source: str
    invoice_status: str
    invoice_url: str
    payer: OlistCustomer
    payment_methods: List[OlistPaymentMethod]
    purchase_timestamp: datetime
    seller_brand: str
    seller_email: str
    seller_id: UUID
    seller_name: str
    seller_order_items: List[OlistOrderSellerOrderItem]
    shipment: None
    shipping_limit_date: datetime
    shipping_quote_group_id: UUID
    shipping_status: str
    status: str
    suspension_reason: str
    total_amount: str
    total_commission: str
    total_freight: str
    total_freight_commission: str
    total_freight_shift: str
    total_items: str
    total_items_commission: str
    updated_at: datetime
    volumes: List[OlistVolume]
    volumes_status: List[str]
    seller_order_history: List[OlistSellerOrderHistory]

    def __init__(self, approved_at: datetime, availability_days: int, branded_store_slug: str, cancelation_reason: str, cancelation_status: str, channel_slug: str, channel_store: str, code: str, count_items: int, created_at: datetime, currency: str, customer: Customer, delivered_customer_date: None, estimated_delivery_date: datetime, invoice_danfe_url: str, invoice_error_message: str, invoice_id: None, invoice_issue_date: None, invoice_key: str, invoice_number: int, invoice_serial_number: int, invoice_source: str, invoice_status: str, invoice_url: str, payer: Customer, payment_methods: List[PaymentMethod], purchase_timestamp: datetime, seller_brand: str, seller_email: str, seller_id: UUID, seller_name: str, seller_order_items: List[OrderSellerOrderItem], shipment: None, shipping_limit_date: datetime, shipping_quote_group_id: UUID, shipping_status: str, status: str, suspension_reason: str, total_amount: str, total_commission: str, total_freight: str, total_freight_commission: str, total_freight_shift: str, total_items: str, total_items_commission: str, updated_at: datetime, volumes: List[Volume], volumes_status: List[str], seller_order_history: List[SellerOrderHistory]) -> None:
        self.approved_at = approved_at
        self.availability_days = availability_days
        self.branded_store_slug = branded_store_slug
        self.cancelation_reason = cancelation_reason
        self.cancelation_status = cancelation_status
        self.channel_slug = channel_slug
        self.channel_store = channel_store
        self.code = code
        self.count_items = count_items
        self.created_at = created_at
        self.currency = currency
        self.customer = customer
        self.delivered_customer_date = delivered_customer_date
        self.estimated_delivery_date = estimated_delivery_date
        self.invoice_danfe_url = invoice_danfe_url
        self.invoice_error_message = invoice_error_message
        self.invoice_id = invoice_id
        self.invoice_issue_date = invoice_issue_date
        self.invoice_key = invoice_key
        self.invoice_number = invoice_number
        self.invoice_serial_number = invoice_serial_number
        self.invoice_source = invoice_source
        self.invoice_status = invoice_status
        self.invoice_url = invoice_url
        self.payer = payer
        self.payment_methods = payment_methods
        self.purchase_timestamp = purchase_timestamp
        self.seller_brand = seller_brand
        self.seller_email = seller_email
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.seller_order_items = seller_order_items
        self.shipment = shipment
        self.shipping_limit_date = shipping_limit_date
        self.shipping_quote_group_id = shipping_quote_group_id
        self.shipping_status = shipping_status
        self.status = status
        self.suspension_reason = suspension_reason
        self.total_amount = total_amount
        self.total_commission = total_commission
        self.total_freight = total_freight
        self.total_freight_commission = total_freight_commission
        self.total_freight_shift = total_freight_shift
        self.total_items = total_items
        self.total_items_commission = total_items_commission
        self.updated_at = updated_at
        self.volumes = volumes
        self.volumes_status = volumes_status
        self.seller_order_history = seller_order_history
