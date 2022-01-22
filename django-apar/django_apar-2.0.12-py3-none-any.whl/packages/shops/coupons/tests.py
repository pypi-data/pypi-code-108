# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase
from aparnik.packages.shops.coupons.models import CouponForAllUser
from aparnik.contrib.users.models import User
from aparnik.packages.shops.orders.models import Order
from django.utils.timezone import now


class CouponTestCase(TestCase):
    def setUp(self):
        """"""
        self.user = User.objects.create_user(username='009800000000')
        self.order = Order.objects.create(user=self.user)
        self.coupon = CouponForAllUser.objects.create(code='unittest', type='p', value=60)
        self.coupon1 = CouponForAllUser.objects.create(code='unittest1', type='v', value=500)
        self.coupon2 = CouponForAllUser(code='unittest2', type='p', value=120)
        self.coupon3 = CouponForAllUser.objects.create(code='unittest3', type='p', value=60, expire_at=now())

    def test_status(self):
        with self.assertRaises(ValidationError):
            CouponForAllUser.objects.status('notExists', self.user, self.order)

        with self.assertRaises(ValidationError):
            CouponForAllUser.objects.status(self.coupon3, self.user, self.order)

        self.assertEqual(CouponForAllUser.objects.status(self.coupon, self.user, self.order), self.coupon.COUPON_STATUS_OK)

    def test_clean(self):
        """"""
        self.assertRaises(ValidationError, self.coupon2.full_clean)

    def test_save(self):
        self.assertRaises(ValidationError, self.coupon2.save)
        # self.assertIsNone(self.coupon.save)

    def test_get_status_description(self):
        for status in self.coupon.COUPON_STATUS_CHOICES:
            self.assertEqual(self.coupon.get_status_description(status[0]), status[1])
        self.assertIsNone(self.coupon.get_status_description('test'))

    def test_calculate_discount(self):
        """"""
        self.assertEqual(self.coupon.calculate_discount(1000), 600)
        self.assertEqual(self.coupon1.calculate_discount(1000), self.coupon1.value)
