import unittest
import warnings
import datetime
from bwgds.berryworld.getdate import GetDate

warnings.filterwarnings('ignore')


class TestGetDate(unittest.TestCase):
    """ Testing the implemented classes """

    def test_getdate_get_now(self):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        self.assertEqual(GetDate().get_now(), datetime.datetime.utcnow().strftime(datetime_format))

    def test_getdate_get_today(self):
        date_format = '%Y-%m-%d'
        self.assertEqual(GetDate().get_today(), datetime.datetime.today().strftime(date_format))

    def test_getdate_get_year(self):
        self.assertEqual(GetDate().get_year(), datetime.datetime.utcnow().year)

    def test_getdate_strfdate(self):
        date_format = '%d/%m/%Y'
        self.assertEqual(GetDate().strfdate(GetDate().get_now(), date_format),
                         datetime.datetime.utcnow().strftime(date_format))

    def test_getdate_strftime(self):
        datetime_format = '%d/%m/%Y %H:%M:%S'
        self.assertEqual(GetDate().strftime(GetDate().get_now(), datetime_format),
                         datetime.datetime.utcnow().strftime(datetime_format))


if __name__ == '__main__':
    TestGetDate().test_getdate_get_now()
    TestGetDate().test_getdate_get_today()
    TestGetDate().test_getdate_get_year()
    TestGetDate().test_getdate_strfdate()
    TestGetDate().test_getdate_strftime()
