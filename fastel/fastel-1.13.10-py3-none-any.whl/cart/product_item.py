from typing import Any, Dict, Union

from bson.objectid import ObjectId

from .collections import get_collection
from .datastructures import BoolConfig, ItemConfig
from .datastructures import Product as ProductStructure
from .datastructures import SingleChoice, SingleConfig, VariantTypes
from .exceptions import CartException


class ProductItem:
    product_cls = ProductStructure
    config_cls = ItemConfig
    _tax_ratio = 1.05

    def __init__(self, product: ProductStructure, config: "ItemConfig") -> None:
        self.product = product
        self.config = config

    @property
    def name(self) -> str:
        return self.product.name

    @property
    def amount(self) -> int:
        return self._get_product_amount(self.config)

    @property
    def price(self) -> int:
        return self._get_product_price(self.config)

    # 因為 B2B 發票需要未稅的價格
    @property
    def sales_amount(self) -> float:
        return round(self.amount / self._tax_ratio, 7)

    # 因為 B2B 發票需要未稅的單價
    @property
    def unit_sales(self) -> float:
        return round(self.sales_amount / self.config.qty, 7)

    def _get_variant_price(self, config: Union[SingleConfig, BoolConfig]) -> int:
        try:
            variant = list(
                filter(
                    lambda product: product.name == config.name,
                    self.product.variants,
                )
            )[0]
        except IndexError:
            raise CartException("invalid_variant")

        if variant.type == VariantTypes.bool:
            return variant.price

        try:
            choice = list(
                filter(lambda _choice: _choice.name == config.choice, variant.choices)  # type: ignore
            )[0]
        except IndexError:
            raise CartException("invalid_variant")

        assert isinstance(choice, SingleChoice)
        return choice.price

    def _get_product_amount(self, config: ItemConfig) -> int:
        variant_price = sum(
            [self._get_variant_price(variant) for variant in config.variants]
        )
        price = self.product.price + variant_price
        return price * config.qty

    def _get_product_price(self, config: ItemConfig) -> int:
        variant_price = sum(
            [self._get_variant_price(variant) for variant in config.variants]
        )
        price = self.product.price + variant_price
        return price

    def to_dict(self) -> Dict[str, Any]:
        config = self.config.dict()
        product_dict = self.product.dict()
        return {
            "name": self.name,
            "unit_sales": self.unit_sales,
            "sales_amount": self.sales_amount,
            "price": self.price,
            "amount": self.amount,
            "config": config,
            "product": product_dict,
        }

    @classmethod
    def validate(
        cls,
        product_id: Union[str, ObjectId],
        config: Union[ItemConfig, Dict[str, Any]],
    ) -> "ProductItem":
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        product = get_collection("product").find_one({"_id": product_id})
        if not product:
            raise CartException("product_not_found")

        validated_product = cls.product_cls.validate(product)
        if isinstance(config, dict):
            config = cls.config_cls.validate(config)
        assert isinstance(config, ItemConfig)
        return cls(validated_product, config)
