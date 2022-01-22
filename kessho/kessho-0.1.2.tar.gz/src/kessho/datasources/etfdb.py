import json
from bs4 import BeautifulSoup
import requests
import datetime as dt
import pandas as pd
    

class EtfDbResource:

    @staticmethod
    def fund_flows(etf_ticker: str) -> pd.DataFrame:
        
        url = f"https://etfdb.com/etf/{etf_ticker}/#fund-flows"

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # The data for all the in and outflows is encoded in a <div>
        div = soup.find_all(lambda tag: tag.name == 'div' and "data-series" in tag.attrs)

        data = json.loads(div[0]['data-series'])

        data = [[dt.datetime.fromtimestamp(int(r[0]/1000)).date(), r[1]] for r in data]

        df = pd.DataFrame.from_records(data, columns=['Date', 'Flow'])
        return df
