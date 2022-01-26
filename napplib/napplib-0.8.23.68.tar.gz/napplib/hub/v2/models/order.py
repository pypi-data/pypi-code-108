from dataclasses import dataclass
from typing import List
from enum import Enum
from typing import Optional

@dataclass
class HubOrderPayment:
    external_id: str
    value: float
    acquirer_transaction_id: Optional[str] = None
    method: Optional[str] = None
    credit_installments: Optional[int] = None
    credit_card_brand: Optional[str] = None
    credit_card_last_digits: Optional[str] = None
    coupon_code: Optional[str] = None

@dataclass
class HubOrderItem:
    external_id: str
    name: str
    quantity: int
    unit_amount: float
    total_amount: float
    sku_code: Optional[str] = None
    product_code: Optional[str] = None
    shipping_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    image_url: Optional[str] = None
    position: Optional[int] = None

@dataclass
class HubOrderInvoice:
    external_id: Optional[str] = None
    number: Optional[str] = None
    serie: Optional[str] = None
    key: Optional[str] = None
    date: Optional[str] = None
    pdf: Optional[str] = None
    xml: Optional[str] = None

@dataclass
class HubOrderShipping:
    external_id: Optional[str] = None
    method: Optional[str] = None
    tracking_url: Optional[str] = None
    tracking_code: Optional[str] = None
    delivery_estimate_date: Optional[str] = None

@dataclass
class HubOrderAddress:
    zip_code: str
    external_id: Optional[str] = None
    receiver_name: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    neighborhood: Optional[str] = None
    complement: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    reference: Optional[str] = None

@dataclass
class HubOrderCustomer:
    external_id: str
    name: str
    email: str
    corporate_trade_name: Optional[str] = None
    corporate_ie: Optional[str] = None
    type: Optional[str] = None
    document: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class HubOrderDelivery:
    external_id: Optional[str] = None
    date: Optional[str] = None

class HubOrderStatus(Enum):
    CREATING = "CREATING"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_APPROVED = "PAYMENT_APPROVED"
    INVOICED = "INVOICED"
    SHIPMENT = "SHIPMENT"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


@dataclass
class HubOrder:
    external_id: str = None
    status: HubOrderStatus = None
    total_amount: float = None 
    date: Optional[str] = None
    items_amount: Optional[int] = None
    shipping_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    invoice: Optional[HubOrderInvoice] = None
    shipping: Optional[HubOrderShipping] = None
    delivery: Optional[HubOrderDelivery] = None
    address: Optional[HubOrderAddress] = None
    customer: Optional[HubOrderCustomer] = None
    items: Optional[List[HubOrderItem]] = None
    payments: Optional[List[HubOrderPayment]] = None
    json: Optional[str] = None

