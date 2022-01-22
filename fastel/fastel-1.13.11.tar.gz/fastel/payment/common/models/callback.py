import time
from typing import Any, Dict, Optional

from pydantic import BaseModel


class CallbackModel(BaseModel):
    client_id: str
    payment_subtype: str
    payment_status: str
    payment_transaction_detail: Optional[Dict[str, Any]]
    payment_redirect_detail: Optional[Dict[str, Any]]
    payment_transaction_time: Optional[str]

    total: int
    order_id: str
    pay_deadline: Optional[str]

    code_no: Optional[str]

    bank_code: Optional[str]
    bank_account: Optional[str]

    barcode_1: Optional[str]
    barcode_2: Optional[str]
    barcode_3: Optional[str]

    @property
    def stepfn_name(self) -> str:
        return f"{self.order_id}_{self.payment_status}_{int(time.time())}"


class LogisticCallbackModel(BaseModel):
    logistic_status: str
    logistic_type: str
    logistic_subtype: str
    logistic_id: str
    detail: Dict[str, Any]
