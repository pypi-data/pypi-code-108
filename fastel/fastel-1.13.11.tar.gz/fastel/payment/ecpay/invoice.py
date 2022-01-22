from typing import Any, Dict, List

import requests

from fastel.payment.ecpay.models.invoice import IssueB2BModel, IssueB2CModel


class InvoiceSDK:
    PAYMENT_HOST = "https://payment-stg.revtel-api.com/v3"
    CLIENT_ID = ""
    CLIENT_SECRET = ""

    CARRIER_TYPE_TABLE = {
        "0": "",
        "1": "1",
        "2": "2",
        "3": "3",
    }

    def __init__(self, checkout: Dict[str, Any]):
        self.checkout = checkout

    def issue_invoice(self) -> Dict[str, Any]:
        if self.checkout.get("category", "B2C") == "B2C":
            url = f"{self.PAYMENT_HOST}/ecpay/B2C/invoice/issue?client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}"
            invoice_data = self.generate_B2C_invoice_data()
        else:
            url = f"{self.PAYMENT_HOST}/ecpay/B2B/invoice/issue?client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}"
            invoice_data = self.generate_B2B_invoice_data()
        resp = requests.post(url, json=invoice_data)
        print("issue invoice")
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        return resp_json

    @staticmethod
    def generate_B2C_invoice_item(
        items: List[Dict[str, Any]],
        extra_items: List[Dict[str, Any]],
        discount_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        result = []
        for item in items:
            item_result = {
                "ItemName": item.get("name", ""),
                "ItemCount": item["config"].get("qty", 1),
                "ItemWord": item["config"]["extra_data"]
                and item["config"]["extra_data"].get("word", "份")
                or "份",
                "ItemPrice": item.get("price", 0),
                "ItemAmount": item.get("amount", 0),
            }
            result.append(item_result)
        # 計算運費
        for extra_item in extra_items:
            item_result = {
                "ItemName": extra_item.get("name", ""),
                "ItemCount": 1,
                "ItemWord": "份",
                "ItemPrice": extra_item.get("amount", 0),
                "ItemAmount": extra_item.get("amount", 0),
            }
            result.append(item_result)
        # 計算折扣金額
        for discount_item in discount_items:
            item_result = {
                "ItemName": discount_item.get("name", ""),
                "ItemCount": 1,
                "ItemWord": "份",
                "ItemPrice": -discount_item.get("amount", 0),
                "ItemAmount": -discount_item.get("amount", 0),
            }
            result.append(item_result)
        return result

    def generate_B2C_invoice_data(self) -> Dict[str, Any]:
        items = self.checkout.get("items", [])
        extra_items = self.checkout.get("extra_items", [])
        discount_items = self.checkout.get("discount_items", [])
        carrier_type = self.CARRIER_TYPE_TABLE[
            self.checkout.get("invoice_carrier_type", "1")
        ]
        love_code = (
            self.checkout.get("invoice_donation", "0") == "1"
            and self.checkout.get("invoice_love_code", None)
            or None
        )
        carrier_num = (
            carrier_type in ["2", "3"]
            and self.checkout.get("invoice_carrier_num", "")
            or ""
        )
        invoice_data = {
            "RelateNumber": self.checkout.get("order_number", ""),
            "CustomerEmail": self.checkout.get("buyer_email", ""),
            "Print": "0",
            "Donation": self.checkout.get("invoice_donation", "0"),
            "LoveCode": love_code,
            "CarrierType": carrier_type,
            "CarrierNum": carrier_num,
            "TaxType": self.checkout.get("invoice_tax_type", "1"),
            "SalesAmount": self.checkout.get("total", 0),
            "Items": self.generate_B2C_invoice_item(items, extra_items, discount_items),
            "InvType": self.checkout.get("invoice_tax_type", "") == "4"
            and "08"
            or "07",
        }
        return IssueB2CModel.validate(invoice_data).dict(exclude_none=True)

    @staticmethod
    def generate_B2B_invoice_item(
        items: List[Dict[str, Any]],
        extra_items: List[Dict[str, Any]],
        discount_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        result = []
        seq = 1
        for item in items:
            item_result = {
                "ItemSeq": seq,
                "ItemName": item.get("name", ""),
                "ItemCount": item["config"].get("qty", 1),
                "ItemWord": item["config"]["extra_data"]
                and item["config"]["extra_data"].get("word", "份")
                or "份",
                "ItemPrice": item.get("unit_sales", 0),
                "ItemAmount": item.get("sales_amount", 0),
            }
            result.append(item_result)
            seq += 1
        # 計算運費
        for extra_item in extra_items:
            item_result = {
                "ItemSeq": seq,
                "ItemName": extra_item.get("name", ""),
                "ItemCount": 1,
                "ItemWord": "份",
                "ItemPrice": extra_item.get("sales_amount", 0),
                "ItemAmount": extra_item.get("sales_amount", 0),
            }
            result.append(item_result)
            seq += 1
        # 計算折扣金額
        for discount_item in discount_items:
            item_result = {
                "ItemSeq": seq,
                "ItemName": discount_item.get("name", ""),
                "ItemCount": 1,
                "ItemWord": "份",
                "ItemPrice": -discount_item.get("sales_amount", 0),
                "ItemAmount": -discount_item.get("sales_amount", 0),
            }
            result.append(item_result)
            seq += 1
        return result

    def generate_B2B_invoice_data(self) -> Dict[str, Any]:
        items = self.checkout.get("items", [])
        extra_items = self.checkout.get("extra_items", [])
        discount_items = self.checkout.get("discount_items", [])
        invoice_data = {
            "RelateNumber": self.checkout.get("order_number", ""),
            "CustomerIdentifier": self.checkout.get("invoice_uni_no", ""),
            "CustomerEmail": self.checkout.get("buyer_email", ""),
            "TaxType": self.checkout.get("invoice_tax_type", "1"),
            "SalesAmount": self.checkout.get("sales", 0),
            "TaxAmount": self.checkout.get("tax", 0),
            "TotalAmount": self.checkout.get("total", 0),
            "Items": self.generate_B2B_invoice_item(items, extra_items, discount_items),
            "InvType": self.checkout.get("invoice_tax_type", "") == "4"
            and "08"
            or "07",
        }
        return IssueB2BModel.validate(invoice_data).dict(exclude_none=True)
