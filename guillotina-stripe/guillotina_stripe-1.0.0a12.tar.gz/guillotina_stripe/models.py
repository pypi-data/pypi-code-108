from typing import Any, List, Optional
from pydantic import BaseModel


class Card(BaseModel):
    token: Optional[str]
    exp_month: Optional[str]
    exp_year: Optional[str]
    number: Optional[str]
    cvc: Optional[str]


class BillingDetails(BaseModel):
    city: str
    country: str
    postal_code: str
    line1: str
    line2: Optional[str]
    state: str
    email: str
    name: str
    phone: str


class Subscription(BaseModel):
    id: str
    default_payment_method: Optional[str]
    current_period_end: int
    current_period_start: int
    status: str
    cancel_at_period_end: bool
    items: Any
    latest_invoice: Any

    def products(self) -> List[Any]:
        result = []
        if self.items is not None:
            for item in self.items['data']:
                result.append({
                    'price': item['price']['id'],
                    'product': item['price']['product']
                })
        return result

    def isactive(self) -> bool:
        return self.status == 'active'

    def last_intent(self) -> bool:
        payment_intent = self.latest_invoice['payment_intent']
        if payment_intent['status'] == 'requires_action':
            return {
                'status': 'requires_action',
                'client_secret': payment_intent['client_secret']
            }
        else:
            return {
                'status': payment_intent['status']
            }
