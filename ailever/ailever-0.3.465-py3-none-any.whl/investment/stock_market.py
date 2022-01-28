from ailever.investment import __fmlops_bs__ as fmlops_bs
from ._base_transfer import basket_wrapper

import os
from tqdm import tqdm
import pandas as pd
import FinanceDataReader as fdr


CORE_MS1 = fmlops_bs.core['MS1']

sources = pd.DataFrame(columns=['Name', 'Url'],
                       data=[['finviz', 'https://finviz.com/'],
                             ['investing','https://www.investing.com/'],
                             ['fred', 'https://fred.stlouisfed.org/']])

def market_monitoring(renewal=False):
    MM = MarketMonitoring()
    return MM.financial_indicator(renewal=renewal)

def market_information(baskets=None, only_symbol=False, inverse_mapping=False, source=False, market_cap=True):
    baskets = basket_wrapper(baskets, kind='symbols')

    r"""
    TARGET FRAME:
    Code	Name	Market	Dept	Close	ChangeCode	Changes	ChagesRatio	Open	High	Low	Volume	Amount	Marcap	Stocks
    """
    if source:
        return sources

    MI = MarketInformation()
    if baskets:
        market_info = MI.market_query(baskets=baskets, only_symbol=only_symbol, inverse_mapping=inverse_mapping)
    else:
        market_info = MI.market_info
    
    if market_cap:
        market_caps = fdr.StockListing('KRX-MARCAP')
        market_info = pd.merge(market_info, market_caps, how='left', left_on='Symbol', right_on='Code').drop(['Name_y', 'Market_y'], axis=1).rename(columns={'Market_x':'Market', 'Name_x':'Name'})

    return market_info


class MarketMonitoring:
    def __init__(self):
        self.renewal = False
        self.indicators = self.financial_indicator()

    def financial_indicator(self, renewal=True):
        fi_by_future = [
                'NG', 'GC', 'SI', 'HG', 'CL'
                ]
        fi_by_country = [
                'KS11', 'KQ11', 'KS50', 'KS100', 'KRX100', 'KS200',
                'DJI', 'IXIC', 'US500', 'RUTNU', 'VIX', 
                'JP225', 'STOXX50', 'HK50', 'CSI300', 'TWII', 'HNX30', 'SSEC', 'UK100', 'DE30', 'FCHI'
                ] 
        fi_by_exchange_rate = [
                'USD/KRW', 'USD/EUR', 'USD/JPY', 'CNY/KRW', 'EUR/USD', 'USD/JPY', 'JPY/KRW', 'AUD/USD', 'EUR/JPY', 'USD/RUB'
                ]
        fi_by_bond = [
                'KR1YT=RR', 'KR2YT=RR', 'KR3YT=RR', 'KR4YT=RR', 'KR5YT=RR', 'KR10YT=RR', 'KR20YT=RR', 'KR30YT=RR', 'KR50YT=RR',
                'US1MT=X', 'US3MT=X', 'US6MT=X', 'US1YT=X', 'US2YT=X', 'US3YT=X', 'US5YT=X', 'US7YT=X','US10YT=X', 'US30YT=X'
                ]
        fi_by_cryptocurrency = [
                'BTC/KRW','ETH/KRW','XRP/KRW','BCH/KRW','EOS/KRW','LTC/KRW','XLM/KRW',
                'BTC/USD','ETH/USD','XRP/USD','BCH/USD','EOS/USD','LTC/USD','XLM/USD'
                ]
        FIs = list()
        FIs.extend(fi_by_country)
        FIs.extend(fi_by_future)
        FIs.extend(fi_by_exchange_rate)
        FIs.extend(fi_by_bond)
        FIs.extend(fi_by_cryptocurrency)

        FI_dict = dict()
        for FI in tqdm(FIs):
            if renewal:
                try:
                    df = fdr.DataReader(FI)
                    df.to_csv(os.path.join(CORE_MS1.path, FI.replace('/', '').replace('=', '') + '.csv'))
                    FI_dict[FI] = df
                except:
                    continue
            else:
                try:
                    df = pd.read_csv(f'https://raw.githubusercontent.com/ailever/investment/main/{FI}.csv')
                    df.to_csv(os.path.join(CORE_MS1.path, FI.replace('/', '').replace('=', '') + '.csv'))
                    FI_dict[FI] = df
                except:
                    continue
        return FI_dict

class MarketInformation:
    def __init__(self):
        self.market_info = self.market_information()

    def market_query(self, baskets:list, only_symbol:bool=False, inverse_mapping=False):
        if not isinstance(baskets, list):
            baskets = [baskets]

        if not inverse_mapping:
            market_info = self.market_info.set_index('Name').loc[baskets].reset_index()
            if only_symbol:
                market_info = market_info.Symbol.to_list()
        else:
            market_info = self.market_info.set_index('Symbol').loc[baskets].reset_index()
            market_info = market_info.Name.to_list()

        return market_info

    def market_information(self):
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KRX.csv')):
            df = fdr.StockListing('KRX')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KRX.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KOSPI.csv')):
            df = fdr.StockListing('KOSPI')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KOSPI.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KOSDAQ.csv')):
            df = fdr.StockListing('KOSDAQ')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KOSDAQ.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KONEX.csv')):
            df = fdr.StockListing('KONEX')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KONEX.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'NYSE.csv')):
            df = fdr.StockListing('NYSE')
            df['Region'] = 'United States'
            df.to_csv(os.path.join(CORE_MS1.path, 'NYSE.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'NASDAQ.csv')):
            df = fdr.StockListing('NASDAQ')
            df['Region'] = 'United States'
            df.to_csv(os.path.join(CORE_MS1.path, 'NASDAQ.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'AMEX.csv')):
            df = fdr.StockListing('AMEX')
            df['Region'] = 'United States'
            df.to_csv(os.path.join(CORE_MS1.path, 'AMEX.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'S&P500.csv')):
            df = fdr.StockListing('S&P500')
            df['Region'] = 'United States'
            df.to_csv(os.path.join(CORE_MS1.path, 'S&P500.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'SSE.csv')):
            df = fdr.StockListing('SSE')
            df['Region'] = 'China'
            df.to_csv(os.path.join(CORE_MS1.path, 'SSE.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'SZSE.csv')):
            df = fdr.StockListing('SZSE')
            df['Region'] = 'China'
            df.to_csv(os.path.join(CORE_MS1.path, 'SZSE.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'HKEX.csv')):
            df = fdr.StockListing('HKEX')
            df['Region'] = 'Hong Kong'
            df.to_csv(os.path.join(CORE_MS1.path, 'HKEX.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'TSE.csv')):
            df = fdr.StockListing('TSE')
            df['Region'] = 'Japan'
            df.to_csv(os.path.join(CORE_MS1.path, 'TSE.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'HOSE.csv')):
            df = fdr.StockListing('HOSE')
            df['Region'] = 'Vietnam'
            df.to_csv(os.path.join(CORE_MS1.path, 'HOSE.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KRX-DELISTING.csv')):
            df = fdr.StockListing('KRX-DELISTING')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KRX-DELISTING.csv'))
        if not os.path.isfile(os.path.join(CORE_MS1.path, 'KRX-ADMINISTRATIVE.csv')):
            df = fdr.StockListing('KRX-ADMINISTRATIVE')
            df['Region'] = 'Korea'
            df.to_csv(os.path.join(CORE_MS1.path, 'KRX-ADMINISTRATIVE.csv'))

        stocks = pd.read_csv(os.path.join(CORE_MS1.path, 'KRX.csv')).drop('Unnamed: 0',axis=1)[['Market', 'Symbol', 'Name', 'Industry', 'Region']].sort_values(by='Market')
        for market in ['NYSE', 'NASDAQ', 'AMEX', 'HKEX', 'HOSE', 'S&P500', 'SSE', 'TSE']:
            df = pd.read_csv(os.path.join(CORE_MS1.path, f'{market}.csv')).drop('Unnamed: 0', axis=1)[['Symbol', 'Name', 'Industry', 'Region']]
            df['Market'] = market
            df = df[['Market', 'Symbol', 'Name', 'Industry', 'Region']]
            stocks = stocks.append(df).reset_index().drop('index', axis=1)
        stocks = stocks.drop_duplicates()
        stocks.to_csv(os.path.join(CORE_MS1.path, 'FINANCIAL_MARKET.csv'))
        return stocks


