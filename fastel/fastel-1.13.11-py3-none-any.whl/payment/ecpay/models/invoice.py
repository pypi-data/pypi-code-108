from typing import List, Literal, Optional

from pydantic import BaseModel


class B2BItem(BaseModel):
    ItemSeq: int
    ItemName: str
    ItemCount: int
    ItemWord: Optional[str]
    ItemPrice: int
    ItemAmount: int
    ItemTax: Optional[Literal["1", "2"]]
    ItemRemark: Optional[str]


class IssueB2BModel(BaseModel):
    RelateNumber: str
    InvoiceTime: Optional[str]
    CustomerIdentifier: str
    CustomerEmail: Optional[str]
    ClearanceMark: Optional[str]
    InvType: Literal["07", "08"] = "07"
    TaxType: Literal["1", "2", "3", "4"] = "1"
    TaxRate: Optional[float]
    Items: List[B2BItem]
    SalesAmount: int
    TaxAmount: int
    TotalAmount: int
    InvoiceRemark: Optional[str]


class B2CItem(BaseModel):
    ItemSeq: Optional[int]
    ItemName: str
    ItemCount: int
    ItemWord: str
    ItemPrice: int
    ItemTaxType: Optional[Literal["1", "2", "3"]]
    ItemAmount: int
    ItemRemark: Optional[str]


class IssueB2CModel(BaseModel):
    RelateNumber: str
    CustomerID: Optional[str]
    CustomerIdentifier: Optional[str]
    CustomerName: Optional[str]
    CustomerAddr: Optional[str]
    CustomerPhone: Optional[str]
    CustomerEmail: Optional[str]
    ClearanceMark: Optional[str]
    Print: Literal["0", "1"] = "0"
    Donation: Literal["0", "1"] = "0"
    LoveCode: Optional[str]
    CarrierType: Optional[Literal["1", "2", "3", ""]]
    CarrierNum: Optional[str]
    TaxType: Literal["1", "2", "3", "4", "9"] = "1"
    SpecialTaxType: Optional[Literal["1", "2", "3", "4", "5", "6", "7", "8"]]
    SalesAmount: int
    InvoiceRemark: Optional[str]
    Items: List[B2CItem]
    InvType: Literal["07", "08"]
    vat: Optional[Literal["0", "1"]]


class QueryB2BModel(BaseModel):
    InvoiceCategory: Literal[0, 1] = 0
    InvoiceNumber: str
    InvoiceDate: str
    RelateNumber: Optional[str]


class QueryB2CModel(BaseModel):
    RelateNumber: Optional[str]
    InvoiceNo: Optional[str]
    InvoiceDate: Optional[str]


class VoidB2BModel(BaseModel):
    InvoiceNumber: str
    InvoiceDate: str
    Reason: str
    Remark: Optional[str]


class VoidB2CModel(BaseModel):
    InvoiceNo: str
    InvoiceDate: str
    Reason: str
