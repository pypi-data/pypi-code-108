import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Process, Queue
import FinanceDataReader as fdr


def _download(exchange, bound, queue):
    symbols = pd.read_csv(f'stockset/{exchange}.csv').Symbol.values

    exception_list = queue
    for i, symbol in enumerate(tqdm(symbols)):
        if i >= bound[0] and i < bound[1]:
            try:
                if not os.path.isfile(f'stockset/{symbol}.csv'):
                    fdr.DataReader(symbol).to_csv(f'stockset/{symbol}.csv')
            except:
                exception_list.put(symbol)

queue = Queue()
def download(n=30, exchange='NYSE', queue=queue):
    r"""
    Args:
        n:
        queue:

    Examples:
        >>> from ailever.forecast.STOCK import usx
        >>> usx.download(n=30, exchange='NYSE')
    """

    assert exchange in ['NYSE', 'NASDAQ', 'AMEX', 'SP500'], 'exchange must be in "NYSE","NASDAQ","AMEX","SP500"'

    if not os.path.isdir('stockset'):
        os.mkdir('stockset')

    USIs = ['DJI', 'IXIC', 'US500', 'VIX']
    print('* United States Composite Stock Price Index Lodaer')
    for USI in tqdm(USIs):
        usa_index = fdr.DataReader(f'{USI}')
        usa_index.to_csv(f'stockset/{USI}.csv')

    usx = fdr.StockListing(f'{exchange}')
    if not os.path.isfile(f'stockset/{exchange}.csv'):
        usx.to_csv(f'stockset/{exchange}.csv')

    common_diff = int(len(usx)/int(n))

    print('* United States Stock Lodaer')
    procs = []
    for _n in range(int(n)):
        lower = int(common_diff * (_n))
        upper = int(common_diff * (_n+1))
        bound = (lower, upper)
        proc = Process(target=_download, args=(exchange, bound, queue, ))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    exception_list = []
    for _ in range(queue.qsize()):
        exception_list.append(queue.get())
    
    print('Complete!')
    return exception_list


def all(date='2010-01-01', mode='Close', cut=None):
    pass

def _all(date='2010-01-01', mode='Close', cut=None):
    pass


def nyse(date='2010-01-01', mode='Close', cut=None):
    r"""
    Args:
        date:
        mode:
        cut:

    Examples:
        >>> from ailever.forecast.STOCK import usx
        >>> Df = usx.nyse(date='2010-01-01', mode='Close')
        >>> ...
        >>> stock = Df[0]
        >>> info = Df[1]
        >>> exception_list = Df[2]
        >>> USI_dict = Df[3]
        >>> mode = Df[4]

    Examples:
        >>> from ailever.forecast.STOCK import usx, Ailf_US
        >>> ...
        >>> Df = usx.nyse('2018-01-01', mode='Close')
        >>> ailf = Ailf_US(Df=Df, filter_period=100, criterion=1.5, GC=False, V=None)

    Examples:
        >>> from ailever.forecast.STOCK import usx, Ailf_US
        >>> ...
        >>> date = '2018-01-01'
        >>> Df1 = usx.nyse(date, mode='Close')
        >>> Df2 = usx.nyse(date, mode='Open')
        >>> Df3 = usx.nyse(date, mode='Low')
        >>> Df4 = usx.nyse(date, mode='High')
        >>> ADf = dict(Close=Df1, Open=Df2, Low=Df3, High=Df4)
        >>> ailf = Ailf_US(ADf=ADf, filter_period=100, criterion=1.5, GC=False, V=None)

    """

    stock_list = pd.read_csv(f'stockset/NYSE.csv').drop('Unnamed: 0', axis=1)
    symbols = stock_list.Symbol.values
    stocks = pd.read_csv('stockset/JPM.csv')
    stocks = stocks[stocks.Date >= date][f'{mode}'].values

    # Df[0] & Df[2] : United States Stock / Exception List
    exception_list = list()
    for i, symbol in enumerate(tqdm(symbols)):
        if i == cut: break
        try:
            stock = pd.read_csv(f'stockset/{symbol}.csv')
            stock = stock[stock.Date >= date][f'{mode}'].values
            if len(stocks) == len(stock):
                stocks = np.c_[stocks, stock]
            else:
                exception_list.append(symbol)
        except:
            exception_list.append(symbol)
    
    # Df[1] : United States Stock List
    stock_list = stock_list.query(f'Symbol != {exception_list}')

    # Df[3] : United States Composite Stock Price Index Lodaer
    USIs = ['DJI', 'IXIC', 'US500', 'VIX']
    USI_dict = {}
    for USI in USIs:
        df = pd.read_csv(f'stockset/{USI}.csv')
        USI_dict[USI] = df

    return stocks[:, 1:], stock_list, exception_list, USI_dict, mode


def _nyse(date='2010-01-01', mode='Close', cut=None):
    date = np.datetime64(date)
    stock_list = fdr.StockListing('NYSE')
    symbols = stock_list.Symbol.values
    stocks = fdr.DataReader('JPM', date)
    stocks = stocks[f'{mode}'].values

    # Df[0] & Df[2] : United States Stock / Exception List
    exception_list = list()
    for i, symbol in enumerate(tqdm(symbols)):
        if i == cut: break
        try:
            stock = fdr.DataReader(symbol, date)
            stock = stock[f'{mode}'].values
            stocks = np.c_[stocks, stock]
        except:
            exception_list.append(symbol)
        
    # Df[1] : United States Stock List
    stock_list = stock_list.query(f'Symbol != {exception_list}')

    # Df[3] : United States Composite Stock Price Index Lodaer
    USIs = ['DJI', 'IXIC', 'US500', 'VIX']
    USI_dict = {}
    for USI in tqdm(USIs):
        usa_index = fdr.DataReader(f'{USI}')
        USI_dict[USI] = usa_index

    return stocks[:, 1:], stock_list, exception_list, USI_dict, mode



def nasdaq(date='2010-01-01', mode='Close', cut=None):
    pass

def _nasdaq(date='2010-01-01', mode='Close', cut=None):
    pass


def amex(date='2010-01-01', mode='Close', cut=None):
    pass

def _amex(date='2010-01-01', mode='Close', cut=None):
    pass


def sp500(date='2010-01-01', mode='Close', cut=None):
    pass

def _sp500(date='2010-01-01', mode='Close', cut=None):
    pass
