from typing import List, Literal, Optional

from pydantic import BaseModel


class EZItem(BaseModel):
    name: str
    quantity: float
    price: float
    amount: float


class IssueModel(BaseModel):
    TransNum: Optional[str]
    MerchantOrderNo: str
    Status: Literal["0", "1", "3"] = "1"
    CreateStatusTime: Optional[str]
    Category: Literal["B2B", "B2C"] = "B2C"
    BuyerName: str
    BuyerUBN: Optional[str]
    BuyerAddress: Optional[str]
    BuyerEmail: Optional[str]
    CarrierType: Optional[Literal["0", "1", "2"]]
    CarrierNum: Optional[str]
    LoveCode: Optional[int]
    PrintFlag: Literal["Y", "N"] = "Y"
    TaxType: Literal["1", "2", "3", "9"] = "1"
    TaxRate: int = 5  # 5%
    CustomsClearance: Optional[Literal["1", "2"]]
    Amt: float
    AmtSales: Optional[int]
    AmtZero: Optional[int]
    AmtFree: Optional[int]
    TaxAmt: float
    TotalAmt: float
    items: List[EZItem]


class QueryModel(BaseModel):
    SearchType: Optional[Literal["0", "1"]]
    MerchantOrderNo: str
    TotalAmt: str
    InvoiceNumber: str
    RandomNum: str
    DisplayFlag: Optional[Literal["1"]]


class VoidModel(BaseModel):
    InvoiceNumber: str
    InvalidReason: str
