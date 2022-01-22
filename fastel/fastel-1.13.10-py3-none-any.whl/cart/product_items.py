from typing import Any, Dict, Iterator, List, Sequence, Type

from .datastructures import ItemConfig
from .exceptions import CartException
from .product_item import ProductItem


class ProductItems:
    default_item_length: int = 10
    item_cls: Type[ProductItem]

    items: List[ProductItem]

    def __init__(self, products: Sequence[Dict[str, Any]]) -> None:
        self.items = [
            self.item_cls.validate(product["id"], product["config"])
            for product in products
        ]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ProductItem]:
        return iter(self.items)

    @property
    def total(self) -> int:
        return sum([item.amount for item in self.items])

    @property
    def sales(self) -> int:
        return round(self.total / 1.05)

    @property
    def tax(self) -> int:
        return self.total - self.sales

    def to_dict(self) -> Sequence[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    def clean_items(self) -> None:
        self.items = []

    def add_item(self, product_id: str, config: ItemConfig) -> None:
        if len(self) >= self.default_item_length:
            raise CartException("item_length_limit")

        item = self.item_cls.validate(product_id, config)
        self.items.append(item)

    def delete_item(self, index: int) -> None:
        try:
            self.items.pop(index)
        except IndexError:
            raise CartException(
                "index_does_exist",
            )

    def edit_item(self, index: int, config: ItemConfig) -> None:
        try:
            item = self.items[index]
            self.items[index] = self.item_cls.validate(
                item.product.id,
                config,
            )
        except IndexError:
            raise CartException(
                "index_does_exist",
            )

    def validate(self) -> None:
        return
