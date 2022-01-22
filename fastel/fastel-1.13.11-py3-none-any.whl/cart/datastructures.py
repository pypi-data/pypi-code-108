from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Type, Union

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator

from fastel.exceptions import APIException


class BaseCartConfig(BaseModel):
    @classmethod
    def model_with_optional_fields(cls: Type[BaseModel]) -> Type[BaseModel]:
        """Generate a `BaseModel` class with all the same fields as `model` but as optional"""

        class OptionalModel(cls):  # type: ignore
            ...

        for field in OptionalModel.__fields__.values():
            field.required = False

        # for generated schema for example (can be removed)
        OptionalModel.__name__ = f"Optional{cls.__name__}"

        return OptionalModel

    @classmethod
    def validate_optional(cls, value: Any) -> BaseModel:
        return cls.model_with_optional_fields().validate(value)


class PaymentSubTypes(str, Enum):
    atm = "atm"
    credit = "credit"
    cod = "cod"
    offline = "offline"


class LogisticTypes(str, Enum):
    HOME = "HOME"
    CVS = "CVS"


class HomeSubtypes(str, Enum):
    ECAN = "ECAN"
    TCAT = "TCAT"


class CVSLogisticSubTypes(str, Enum):
    FAMI = "FAMI"
    UNIMART = "UNIMART"
    HILIFE = "HILIFE"
    FAMIC2C = "FAMIC2C"
    UNIMARTC2C = "UNIMARTC2C"
    HILIFEC2C = "HILIFEC2C"
    OKMARTC2C = "OKMARTC2C"


class CartConfig(BaseCartConfig):
    buyer_name: str = ""
    buyer_phone: Optional[str] = ""
    buyer_email: EmailStr
    buyer_zip: Optional[str] = ""
    buyer_city: Optional[str] = ""
    buyer_district: Optional[str] = ""
    buyer_address: Optional[str] = ""
    buyer_tel: Optional[str] = ""
    buyer_tel_ext: Optional[str] = ""
    receiver_name: Optional[str] = ""
    receiver_phone: Optional[str] = ""
    receiver_email: Optional[str] = ""
    receiver_zip: Optional[str] = ""
    receiver_city: Optional[str] = ""
    receiver_district: Optional[str] = ""
    receiver_address: Optional[str] = ""
    receiver_tel: Optional[str] = ""
    receiver_tel_ext: Optional[str] = ""
    payment_subtype: PaymentSubTypes = PaymentSubTypes.credit
    logistics_type: LogisticTypes = LogisticTypes.CVS
    logistics_subtype: str = CVSLogisticSubTypes.FAMIC2C
    logistics_cvs_store_id: Optional[str]
    # 1: 應稅 2: 零稅率 3: 免稅 4: 特種應稅 9: 混合稅（限B2C）
    invoice_tax_type: Literal["1", "2", "3", "4", "9"] = "1"
    invoice_tax_rate: float = 0.05
    # B2B 統編
    invoice_uni_no: Optional[str]
    invoice_category: Literal["B2B", "B2C"] = "B2C"
    # B2C 是否捐贈
    invoice_donation: Literal["0", "1"] = "0"
    # B2C 捐贈碼
    invoice_love_code: Optional[str]
    # B2C 載具類型 0: 無載具 1: 綠界電子發票（使用者email-優先 or phone） 2: 自然人憑證 3: 手機條碼
    invoice_carrier_type: Literal["0", "1", "2", "3"] = "1"
    # B2C 載具編號 如果 carrier_type = "1" 載具編號放空字串即可， ecpay 會拿 customer email or phone
    invoice_carrier_num: str = ""
    order_note: str = ""
    points: int = 0
    use_full_points: bool = False
    extra_data: Optional[Any]

    @validator("logistics_subtype")
    def validate_logistic_subtype(cls, value: str, values: Dict[str, Any]) -> str:
        if value is None:
            return ""

        try:
            if values["logistics_type"] == LogisticTypes.HOME:
                return HomeSubtypes[value]
            return CVSLogisticSubTypes[value]
        except KeyError:
            raise ValueError("subtype_not_valid")


OptionalCartConfig = CartConfig.model_with_optional_fields()


class SingleConfig(BaseModel):
    name: str
    choice: str


class BoolConfig(BaseModel):
    name: str


class ItemConfig(BaseModel):
    qty: int
    variants: List[Union[SingleConfig, BoolConfig]] = []
    extra_data: Optional[Any]

    @validator("qty")
    def positive_qty(cls, qty: int) -> int:
        if qty < 1:
            raise APIException(
                status_code=400, error="invalid_qty_error", detail="quantity must > 0"
            )
        return qty

    @validator("variants")
    def validate_variants(
        cls, value: List[Union[SingleConfig, BoolConfig]]
    ) -> List[Union[SingleConfig, BoolConfig]]:
        names = []
        for variant in value:
            if variant.name in names:
                raise APIException(status_code=400, error="invalid_variant", detail="")
            names.append(variant.name)

        return value


class VariantTypes(str, Enum):
    bool = "bool"
    single = "single"


class SingleChoice(BaseModel):
    name: str
    label: str
    price: int


class SingleVariant(BaseModel):
    type: Literal["single"]
    name: str
    label: str
    choices: List[SingleChoice]


class BooleanVariant(BaseModel):
    type: Literal["bool"]
    name: str
    label: str
    price: int


class ValidatedObjectId(ObjectId):  # type: ignore
    @classmethod
    def __get_validators__(cls) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        return ObjectId(value)


class Product(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    price: int
    variants: List[Union[SingleVariant, BooleanVariant]] = []
    on_shelf: Optional[bool]
    public: Optional[bool]
    labels: Optional[List[str]]
    images: Optional[Union[List[str], List[Dict[str, Any]]]]
    extra_data: Optional[Any]


class Coupon(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    code: str
    discount: int
    threshold: int
    start_time: int
    end_time: int
    usage: int = 0


class Discount(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    discount: int
    threshold: int
    start_time: int
    end_time: int
