import datetime as dt
from unittest import TestCase

from kessho.datasources.forex import Forex


class ForexTest(TestCase):

    def test_forex(self):

        usd = 'USD'
        chf = 'CHF'

        forex = Forex([('USD', 'CHF'), ('CHF', 'USD')])
        self.assertIsNotNone(forex.forex)

        usd_chf = forex.rates_for(usd, chf)
        self.assertFalse(usd_chf.isna()['1USD=CHF'].all())
        self.assertGreater(len(usd_chf), 0)

        usd_chf_1 = forex.rate_for(usd, chf, dt.date(2021, 1, 1))
        usd_chf_2 = 1 / forex.rate_for(chf, usd, dt.date(2021, 1, 1))

        self.assertAlmostEqual(usd_chf_1, usd_chf_2, places=3)
