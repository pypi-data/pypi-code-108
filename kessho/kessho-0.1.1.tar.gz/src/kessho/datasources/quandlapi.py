import json
import os
from itertools import accumulate

import pandas as pd
import quandl


class QuandlResource:
    def __init__(self):
        self.services = {
            'BULL': {
                'subject': 'American Association of Individual Investors sentiment data, bullish fraction',
                'frequency': 'weeky',
                'api_path': 'AAII/AAII_SENTIMENT',
                'date_column': 'Date',
                'column': 'Bullish'
            },
            'BEAR': {
                'subject': 'American Association of Individual Investors sentiment data, bearish fraction',
                'frequency': 'weeky',
                'api_path': 'AAII/AAII_SENTIMENT',
                'date_column': 'Date',
                'column': 'Bearish'
            },
            'UMCC': {
                'subject': 'University of Michigan Consumer Confidence',
                'frequency': 'monthly',
                'api_path': 'UMICH/SOC1',
                'date_column': 'Date',
                'column': 'Index'
            },
            'FRM1': {
                'subject': 'Federal Reserve Money Supply M1',
                'frequency': 'weekly',
                'api_path': 'FRED/M1',
                'date_column': 'Date',
                'column': 'Value'
            },
            'FRM1V': {
                'subject': 'Federal Reserve M1 Velocity',
                'frequency': 'weekly',
                'api_path': 'FRED/M1V',
                'date_column': 'Date',
                'column': 'Value'
            },
            'FRM2': {
                'subject': 'Federal Reserve Money Supply M2',
                'frequency': 'weekly',
                'api_path': 'FRED/M2',
                'date_column': 'Date',
                'column': 'Value'
            },
            'FRM2V': {
                'subject': 'Federal Reserve M2 Velocity',
                'frequency': 'weekly',
                'api_path': 'FRED/M2V',
                'date_column': 'Date',
                'column': 'Value'
            },
            'NUIS': {
                'subject': 'Nasdaq US Insider Sentiment Index',
                'frequency': 'daily',
                'api_path': 'NASDAQOMX/NQBUY',
                'date_column': 'Trade Date',
                'column': 'Index Value'
            },
            'NMIS': {
                'subject': 'Federal Reserve non-manufacturing invententory sentiment index',
                'frequency': 'monthly',
                'api_path': 'FRED/NMFINSI',
                'date_column': 'DATE',
                'column': 'VALUE'

            },
            # Yale opinion poll data
            'YVID': {
                'subject': "Yale's US market value confidence - Individual",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_VAL_INDIV',
                'date_column': 'Trade Date',
                'column': 'Index Value'
            },
            'YVIS': {
                'subject': "Yale's US market value confidence - Institutional",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_VAL_INST',
                'date_column': 'Trade Date',
                'column': 'Index Value'
            },
            'YCID': {
                'subject': "Yale's US stock crash confidence - Individual",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_CRASH_INDIV',
                'date_column': 'Trade Date',
                'column': 'Index Value'
            },
            'YCIS': {
                'subject': "Yale's US stock crash confidence - Institutional",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_CRASH_INST',
                'date_column': 'Trade Date',
                'column': 'Index Value'
            },
            'YDID': {
                'subject': "Yale's Buy-On-Dip confidence index - Individual",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_BUY_INDIV',
                'date_column': 'Date',
                'column': 'Index Value'
            },
            'YDIS': {
                'subject': "Yale's Buy-On-Dip confidence index - Institutional",
                'frequency': 'monthly',
                'api_path': 'YALE/US_CONF_INDEX_BUY_INST',
                'date_column': 'Date',
                'column': 'Index Value'
            }
        }

    def help(self, key=None):
        if not key:
            print("Available services are:")
            print(json.dumps(self.services, indent=2))
        elif key == 'list':
            print("Available services are:")
            for key, item in self.services.items():
                print(f"{key}: {item['subject']} - {item['frequency']}")
        else:
            if self.services.get(key):
                print(json.dumps(self.services[key], indent=2))
            else:
                print(f"No such service: {key}")
                print("Available services are:")
                self.help('list')

    def get_data(self, key: str, all_calendar_days=True):
        if not self.services.get(key):
            self.help('list')
        api_key = os.environ.get('QUANDL_KEY')
        quandl.ApiConfig.api_key = api_key
        column = self.services[key]['column']
        date_column = self.services[key]['date_column']
        df = quandl.get(self.services[key]['api_path'])
        df.reset_index(inplace=True)
        df.rename(columns={date_column: 'Date', column: 'Index'}, inplace=True)

        if all_calendar_days:
            df = fill_calendar(df)

        return df[['Date', 'Index']]


def fill_calendar(df: pd.DataFrame) -> pd.DataFrame:
    all_dates = pd.DataFrame(pd.date_range(min(df['Date']), max(df['Date'])))
    all_dates.columns = ['Date']
    all_dates['Date'] = all_dates['Date'].apply(lambda t: t.date())
    df['Date'] = df['Date'].apply(lambda t: t.date())
    df = all_dates.merge(df, on='Date', how='outer')
    df['Index'] = list(accumulate(df['Index'],
                                  lambda acc, new: acc if pd.isna(new) else new))
    return df
