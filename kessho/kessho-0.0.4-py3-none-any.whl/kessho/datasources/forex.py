from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


class AbstractForex(ABC):

    @abstractmethod
    def rates_for(self, cfrom: str, cto: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def rate_for(self, cfrom: str, cto: str, date: dt.date) -> float:
        pass


class Forex(AbstractForex):
    """
    Wrapper that scrapes from currency-converter.org.uk
    """

    def __init__(self, currency_pairs):

        self.forex = {}
        self.lookup = {}
        for cfrom, cto in currency_pairs:
            key = f'1{cfrom}={cto}'
            url = ('https://www.currency-converter.org.uk/currency-rates' +
                   '/historical/table/%s-%s.html' % (cfrom, cto))
            page = requests.get(url)
            soup = BeautifulSoup(page.content, features="html.parser")

            rows = soup.find(text='Friday').parent.parent.parent.findChildren('tr')[1:-1]

            rates = [[row.findChildren('td')[1].text,
                      float(row.findChildren('td')[3].text.split(" ")[0])] for row in rows]

            fx = pd.DataFrame(rates, columns=['Date', key])
            fx.Date = pd.to_datetime(fx.Date, format="%d/%m/%Y").map(lambda d: d.date())
            self.lookup[key] = dict(fx[['Date', key]].to_records(index=False))
            fx.set_index('Date', inplace=True)
            self.forex[key] = fx

    def rates_for(self, cfrom: str, cto: str) -> pd.DataFrame:
        return self.forex[f'1{cfrom}={cto}']

    def rate_for(self, cfrom: str, cto: str, date: dt.date) -> float:
        return self.lookup[f'1{cfrom}={cto}'].get(date, None)
