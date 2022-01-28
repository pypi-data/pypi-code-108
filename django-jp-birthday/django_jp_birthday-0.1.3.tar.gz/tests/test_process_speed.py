import time
from faker import Faker

from django.test import TestCase
from datetime import date

from tests.models import ModelTest


class InitTest(TestCase):
    @classmethod
    def setup_class(self):
        """テストclass実行の前処理"""

        print("setup_class")

    def setUp(self):
        fakegen = Faker("ja_JP")

        self.meiji = ["1905-1-2", "1905-1-1", "1905-2-1", "1905-2-2"]
        self.showa = ["1980-7-7", "1975-1-1"]
        self.heisei = ["2000-01-02", "2001-01-01", "2002-12-31"]

        self.birthdays = self.meiji + self.showa + self.heisei

        count = 10000
        count = 2500
        self.birthdays = [str(fakegen.date_of_birth()) for _ in range(count)]
        for birthday in self.birthdays:
            model_test = ModelTest(birthday=birthday)
            model_test.save()

    def test_get_upcoming_birthdays(self):

        jan1 = date(year=2010, month=1, day=1)

        start = time.perf_counter()
        ModelTest.objects.get_upcoming_birthdays(30, jan1)
        end = time.perf_counter()
        run_time = end - start
        print("test_get_upcoming_birthdays", run_time)

        self.assertTrue(20 > run_time)

    def test_get_birthdays(self):
        start = time.perf_counter()
        ModelTest.objects.get_birthdays()
        end = time.perf_counter()
        run_time = end - start
        print("test_get_birthdays", run_time)

        self.assertTrue(20 > run_time)

    def test_order_by_birthday(self):

        start = time.perf_counter()

        years = [obj.birthday.year for obj in ModelTest.objects.order_by("birthday")]
        birthdays = sorted([int(b.split("-")[0]) for b in self.birthdays])

        end = time.perf_counter()
        run_time = end - start
        print("test_order_by_birthday", run_time)

        self.assertEqual(years, birthdays)
        self.assertTrue(20 > run_time)

        start = time.perf_counter()
        ModelTest.objects.order_by_birthday(True)
        end = time.perf_counter()
        run_time = end - start
        print("test_order_by_birthday", run_time)

        self.assertTrue(20 > run_time)

    @classmethod
    def teardown_class(self):
        """テストclass実行の後処理"""

        print("teardown_class")
