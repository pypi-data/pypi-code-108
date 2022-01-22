from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseCart
from .collections import get_collection
from .datastructures import CartConfig
from .product_items import ProductItems


class Cart(BaseCart):
    product_multi_item_cls = ProductItems
    config_cls = CartConfig

    def _init_cart_extra(self) -> Dict[str, Any]:
        return {}

    def _calc_fee(self) -> Tuple[int, List[Dict[str, Any]]]:
        fee_items: List[Dict[str, Any]] = [
            {
                "name": "運費",
                "amount": 0,
            }
        ]
        return (sum(i["amount"] for i in fee_items), fee_items)

    def _calc_coupon_discounts(
        self, subtotal: int, coupon_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if coupon_code:
            coupon = get_collection("coupon").find_one(
                {
                    "code": coupon_code,
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "usage": {"$gt": 0},
                }
            )

            if (
                coupon
                and subtotal > coupon["threshold"]
                and not coupon.get("is_void", None)
            ):
                user_id = coupon.get("user_id", None)
                if not user_id or user_id == self._cache_cart["owner"]:
                    items.append(
                        {
                            "type": "coupon",
                            "name": coupon["name"],
                            "sales_amount": round(
                                coupon["discount"] / self._tax_ratio, 7
                            ),
                            "amount": coupon["discount"],
                            "coupon": coupon,
                        }
                    )

        return items

    def _calc_threshold_discounts(self, subtotal: int) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if get_collection("discount") is not None:
            discounts = get_collection("discount").find(
                {
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "threshold": {"$lte": subtotal},
                }
            )

            if discounts:
                discounts.sort((("threshold", -1),))
                for discount in discounts:
                    items.append(
                        {
                            "type": "discount",
                            "name": discount["name"],
                            "sales_amount": round(
                                discount["discount"] / self._tax_ratio, 7
                            ),
                            "amount": discount["discount"],
                            "discount": discount,
                        }
                    )
                    break

        return items

    def _calc_extra_discount(self, subtotal: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        return items

    def _calc_points_discount(
        self, subtotal: int, discount_amount: int
    ) -> List[Dict[str, Any]]:
        items = []
        current_total = subtotal - discount_amount
        if current_total < 0:
            current_total = 0
        private_profile_conn = get_collection("private_profile")
        if self.use_full_points:
            private_profile = private_profile_conn.find_one(
                {"owner": str(self._user["_id"])}
            )
            # for migrate behavior to init private_profile
            if not private_profile:
                private_profile_conn.insert_one(
                    {
                        "owner": str(self._user["_id"]),
                        "email": self._user_profile["email"],
                        "points": 0,
                    }
                )
                user_points = 0
            else:
                user_points = private_profile.get("points", 0)
            points_amount = min(
                # 計算用戶點數比例金額後的數值
                user_points * self._points_ratio,
                # 與目前能夠折抵的訂單折扣後價格的金額
                round(self._user_points_ratio * current_total),
            )
        else:
            points_amount = min(
                # 計算帶入點數比例金額後的數值
                self.points * self._points_ratio,
                # 與目前能夠折抵的訂單折扣後價格的金額
                round(self._use_points_ratio * current_total),
            )
        points = (
            points_amount % self._points_ratio
            and int(points_amount / self._points_ratio) + 1
            or int(points_amount / self._points_ratio)
        )
        if points > 0:
            items.append(
                {
                    "type": "points",
                    "name": "點數折扣",
                    "sales_amount": round(points_amount / self._tax_ratio, 7),
                    "amount": points_amount,
                    "points": points,
                }
            )

        return items

    def _calc_discounts(
        self,
        subtotal: int,
        coupon_code: Optional[str] = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        items = []

        items += self._calc_coupon_discounts(subtotal, coupon_code)
        items += self._calc_threshold_discounts(subtotal)
        items += self._calc_extra_discount(subtotal)
        items += self._calc_points_discount(
            subtotal, sum([item["amount"] for item in items])
        )
        return sum([item["amount"] for item in items]), items
