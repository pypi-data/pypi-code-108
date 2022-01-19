import unittest
import datetime
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.services import date_service


class TestDates(unittest.TestCase):
    """
    Test the functions used by the PSU module
    """

    def test_date_strings(self):
        """
        Test the Date functions of psu_base
        """

        self.assertTrue(
            date_service.string_to_date("31-JAN-2018")
            == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #1",
        )
        self.assertTrue(
            date_service.string_to_date("2018-01-31")
            == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #2",
        )
        self.assertTrue(
            date_service.string_to_date("1/31/2018")
            == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #3",
        )
        self.assertTrue(
            date_service.string_to_date("1/31/18")
            == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #4",
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18")
            == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #5",
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30:45")
            == datetime.datetime(2018, 1, 31, 1, 30, 45, 0),
            "String-to_date #6",
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30")
            == datetime.datetime(2018, 1, 31, 1, 30, 0),
            "String-to_date #7",
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 PM")
            == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #8",
        )
        self.assertTrue(
            date_service.string_to_date("April 29, 2020, 8:24 a.m.")
            == datetime.datetime(2020, 4, 29, 8, 24, 0),
            "String-to_date #8b",
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 pm")
            == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #9",
        )
        self.assertTrue(
            date_service.string_to_date("2020-03-19 07:12:14.165927")
            == datetime.datetime(2020, 3, 19, 7, 12, 14, 165927),
            "String-to_date #10",
        )
        self.assertTrue(
            date_service.string_to_date("2020-08-13T10:15")
            == datetime.datetime(2020, 8, 13, 10, 15, 00),
            "String-to_date #11",
        )
        # An error message will be printed here. Suppress it.
        self.assertTrue(
            date_service.string_to_date("Today at 7:30") is None, "String-to_date #12"
        )

    def test_convenient_dates(self):
        """
        Test the ConvenientDate class
        """
        dd = ConvenientDate("01/31/2019")

        self.assertTrue(dd.datetime_instance, "ConvenientDate #1")
        self.assertTrue(dd.arrow_instance, "ConvenientDate #2")
        self.assertTrue(dd.banner_date() == "31-JAN-2019", "ConvenientDate #3")
        self.assertTrue(dd.date_field() == "2019-01-31", "ConvenientDate #4")
        self.assertTrue(dd.timestamp() == "2019-01-31 00:00:00", "ConvenientDate #5")
        self.assertTrue(str(dd) == "2019-01-31 00:00:00")

        dd = ConvenientDate("06/08/2019 15:37")

        self.assertTrue(dd.banner_date() == "08-JUN-2019", "ConvenientDate #6")
        self.assertTrue(dd.timestamp() == "2019-06-08 15:37:00", "ConvenientDate #7")
        self.assertTrue(
            dd.minus(2).timestamp() == "2019-06-06 15:37:00", "ConvenientDate #8"
        )
        self.assertTrue(
            dd.plus(2).timestamp() == "2019-06-08 15:37:00", "ConvenientDate #8"
        )

    def test_convenient_date_from_datetime(self):
        """
        Test creating ConvenientDate class from datetime instance
        """
        dt = datetime.datetime.now()
        dd = ConvenientDate(dt)

        self.assertTrue(dd.datetime_instance)
        self.assertTrue(dd.datetime_instance == dt)

    def test_convenient_date_from_none(self):
        """
        Test creating ConvenientDate class from None
        """

        # Create a null ConvenientDate
        dd = ConvenientDate(None)
        self.assertTrue(dd)
        self.assertTrue(dd.datetime_instance is None)
        self.assertTrue(dd.arrow_instance is None)

        # Create a ConvenientDate for right now
        dd = ConvenientDate("now")
        self.assertTrue(dd)
        self.assertTrue(dd.datetime_instance is not None)
        self.assertTrue(dd.arrow_instance is not None)

    def test_convenient_date_failure(self):
        """
        Test the ConvenientDate class
        """
        dd = ConvenientDate("1/2/3/4")

        print(f"DDDDDDDDD: {dd}")
        self.assertTrue(dd)
        self.assertTrue(dd.datetime_instance is None)
        self.assertTrue(dd.arrow_instance is None)
        self.assertTrue(dd.conversion_error is not None)
        self.assertTrue(dd.original_value == "1/2/3/4")


if __name__ == "__main__":
    unittest.main()
