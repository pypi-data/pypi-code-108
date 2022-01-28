from django.test import TestCase

from tests.models import ModelTest


class InitTest(TestCase):
    @classmethod
    def setup_class(self):
        """テストclass実行の前処理"""

        print("setup_class")

    def setUp(self):
        self.meiji = ["1905-1-2", "1905-1-1", "1905-2-1", "1905-2-2"]
        self.showa = ["1980-7-7", "1975-1-1"]
        self.heisei = ["2000-01-02", "2001-01-01", "2002-12-31"]

        self.birthdays = self.meiji + self.showa + self.heisei
        for birthday in self.birthdays:
            model_test = ModelTest(birthday=birthday)
            model_test.save()

    def test_order_by_birthday(self):
        pks1 = [obj.pk for obj in ModelTest.objects.order_by("birthday")]
        pks2 = [obj.pk for obj in ModelTest.objects.order_by_birthday(True)]

        self.assertNotEqual(pks1, pks2)

        # doys = [
        #     getattr(obj, "birthday_dayofyear_internal")
        #     for obj in ModelTest.objects.order_by_birthday()
        # ]
        # self.assertEqual(doys, [1, 2, 365])

        # doys = [
        #     getattr(obj, "birthday_dayofyear_internal")
        #     for obj in ModelTest.objects.order_by_birthday(True)
        # ]
        # self.assertEqual(doys, [365, 2, 1])

        years = [obj.birthday.year for obj in ModelTest.objects.order_by("birthday")]
        birthdays = sorted([int(b.split("-")[0]) for b in self.birthdays])

        self.assertEqual(years, birthdays)

    @classmethod
    def teardown_class(self):
        """テストclass実行の後処理"""

        print("teardown_class")
