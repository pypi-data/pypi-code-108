from ailever.investment import __fmlops_bs__ as fmlops_bs
from pandas.core.indexes.base import Index
from ...path import refine
from .._base_transfer import DataTransferCore
from ..logger import update_log
from ..logger import Logger
from .korea_exchange import download, korea_ex, kospi, kosdaq, konex
from .global_exchange import all_exchanges
all_exchanges = all_exchanges(['KOSPI', 'KOSDAQ', 'KONEX', 'NYSE', 'NASDAQ', 'AMEX', 'S&P500', 'HKEX', 'HOSE', 'SSE', 'TSE'])

from typing import Optional, Any, Union, Callable, Iterable
from pytz import timezone
from tqdm import tqdm
from yahooquery import Ticker

import pandas as pd
import FinanceDataReader as fdr
import json

import os
import datetime
import pandas as pd

"""DataVendor Crawling Class - Return cls.dict and cls.log will be passed onto Loader.datacore frame"""       

logger = Logger()
dataset_dirname = fmlops_bs.core['FS'].path

class DataVendor(DataTransferCore):
        
    fundamentals_modules_fromyahooquery_dict = {'DividendYield': ['summaryDetail','dividendYield','DivY'],
                                                'FiveYrsDividendYield': ['summaryDetail','fiveYearAvgDividendYield','5yDivY'],
                                                 'DividendRate': ['summaryDetail','dividendRate','DivR'],
                                                 'trailingDivRate' : ['summaryDetail', 'trailingAnnualDividendRate', 'tDivR'],
                                                 'trailingDivY' : ['summaryDetail', 'trailingAnnualDividendYield', 'tDivY'],
                                                 'Beta': ['summaryDetail','beta','Beta'],
                                                 'Marketcap' : ['summaryDetail', 'marketCap', 'MC'],
                                                 'trailingPE' : ['summaryDetail', 'trailingPE', 'trailingPE'],
                                                 'forwardPE' : ['summaryDetail', 'forwardPE', 'forwardPE'],                                                 
                                                  'EVtoEBITDA': ['defaultKeyStatistics', "enterpriseToEbitda",'EvEbitda'],
                                                  'EnterpriseValue' : ['defaultKeyStatistics', 'enterpriseValue', 'EV'],
                                                  'Shortfloat' : ['defaultKeyStatistics', 'shortPercentSharesOut', 'shortfloat'],
                                                  'Shortratio' : ['defaultKeyStatistics', 'shortRatio', 'shortratio'],
                                                  'SharesOutstanding': ['defaultKeyStatistics', 'sharesOutstanding', 'shares'],
                                                  'Industry' : ['summaryProfile', 'industry', 'industry'],
                                                  'Sector' : ['summaryProfile', 'sector', 'sector'],
                                                  'Summary' : ['summaryProfile', 'longBusinessSummary', 'summary'],
                                                   'website' : ['summaryProfile', 'website', 'web']
                                                      }
    fundamentals_modules_fromyahooquery = fundamentals_modules_fromyahooquery_dict.keys()
    r"""dict structure = {internal module_name : [outer_module, inner_key, abbr for colums]"""


    def __init__(self, baskets=None, country=None):
        
        self.dict = dict()
        self.successes = dict()
        self.failures = list()
        self.baskets = baskets
        self.country = country
        
        r"""OHLCV raw data download process
        
        |--- Directly downloaded from yahooquery or fdr qudry or any other data vendor(TBD)
        |--- Load from LOCAL Directories (from_dir) through ohlcv_from_local() 
    
        """

    def ohlcv_from_local(self, baskets=None, from_dir=None, update_log_dir=None, update_log_file=None):
          
        from_dir = from_dir
        update_log_dir = update_log_dir
        update_log_file = update_log_file
        
        r"""Load from LOCAL directories"""
        dataset = dict()
        num_baskets = len(baskets)
        logger.normal_logger.info(f'[DATAVENDOR] LOAD {num_baskets} BASKETS FROM LOCAL {from_dir}')
        for security in baskets:
            dataset[security] = pd.read_csv(os.path.join(from_dir, f'{security}.csv'), index_col='date')
        self.dict = dataset
       
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))
        self.log = update_log 

        return self

    def ohlcv_from_yahooquery(self, baskets=None, from_dir=None, to_dir=None, update_log_dir=None, update_log_file=None, interval=None, country=None, progress=True,
                        asynchronouse=False, backoff_factor=0.3, formatted=False, max_workers=12, proxies=None, retry=5, 
                        status_forcelist=[404, 429, 500, 502, 503, 504], timeout=5, validate=False,verify=True):
        
        r"""Initializing Args"""
        if not baskets:
            baskets = self.baskets
        if not country:
            coutry = self.country
        
        baskets = list(baskets)
        to_dir = to_dir
        update_log_dir = update_log_dir
        update_log_file = update_log_file
        
        successes = dict()
        _successes = list()
        failures = list()
        
        r"""Request from [Data Vendor]"""
        try:
            ticker = Ticker(symbols=baskets, asynchronouse=asynchronouse, backoff_factor=backoff_factor, country=country,
                            formatted=formatted, max_workers=max_workers, proxies=proxies, retry=retry, status_forcelist=status_forcelist, timeout=timeout,
                            validate=validate, verify=verify, progress=progress)
            securities = ticker.history(period="max", interval=interval, start=None, end=None, adj_timezone=True, adj_ohlc=True)
    
        except:
            failures.extend(baskets)
            self.failures.extend(failures)
            logger.normal_logger.info(f'[DATAVENDOR] DATAVENDOR LOADING FAILED - Please Retry')    
            return
        

        if isinstance(securities, pd.core.frame.DataFrame):
            
            r"""ohlcv pre-processing"""
            securities.columns = list(map(lambda x: x.lower(), securities.columns))
            securities.index.names = list(map(lambda x: x.lower(), securities.index.names))
            securities = securities[['open', 'high', 'low', 'close', 'volume']]
            
            be_in_memory = set(map(lambda x:x[0], securities.index))
            _successes.extend(be_in_memory)
            failures.extend(filter(lambda x: not x in be_in_memory, baskets))
            
            for security in be_in_memory:
                security_frame = securities.loc[security]
                
                
                security_frame.to_csv(os.path.join(to_dir, f'{security}.csv'))
                self.dict[security] = security_frame
                successes[security] = {'Table_NumRows':security_frame.shape[0],
                                       'Table_NumColumns':security_frame.shape[1],
                                       'Table_Start':security_frame.index[0].strftime('%Y-%m-%d'),
                                       'Table_End':security_frame.index[-1].strftime('%Y-%m-%d'),
                                       }
            
        elif isinstance(securities, dict):
            be_in_memory = map(lambda x:x[0], filter(lambda x:not isinstance(x[1], str), zip(securities.keys(), securities.values())))
            not_in_memory = map(lambda x:x[0], filter(lambda x:isinstance(x[1], str), zip(securities.keys(), securities.values())))
            
            _successes.extend(be_in_memory)
            failures.extend(not_in_memory)

            for security in be_in_memory:
                security_frame = securities.loc[security]
                
                r"""ohlcv pre-processing"""
                security_frame.columns = list(map(lambda x: x.lower(), security_frame.columns))
                security_frame.index.names = ['date']
                security_frame = security_frame[['open', 'high', 'low', 'close', 'volume']]
                
                self.dict[security] = security_frame
                security_frame.to_csv(os.path.join(to_dir, f'{security}.csv'))
                successes[security] = {'Table_NumRows':security_frame.shape[0],
                                       'Table_NumColumns':security_frame.shape[1],
                                       'Table_Start':security_frame.index[0].strftime('%Y-%m-%d'),
                                       'Table_End':security_frame.index[-1].strftime('%Y-%m-%d'),
                                       }
                

        self.successes.update(successes)
        self.failures.extend(failures)
        logger.normal_logger.info('[DATAVENDOR] OHLVC FOR {tickers} TICKERS - Failures list: {failures}'.format(tickers=len(list(self.successes.keys())), failures=self.failures))    
        self.ohlcv_logger_for_successes(message='from_yahooquery', updated_basket_info=self.successes, 
                                    update_log_dir=update_log_dir, update_log_file=update_log_file, country=country)
        return self

    def ohlcv_from_fdr(self, baskets=None, from_dir=None, to_dir=None, update_log_dir=None, update_log_file=None, interval=None, country=None, progress=True):
        if not baskets:
            baskets = self.baskets
        if not country:
            country = self.country
        
        baskets = list(baskets)
        to_dir = to_dir
        update_log_dir = update_log_dir
        update_log_file = update_log_file
        
        successes = dict()
        failures = list()
        for security in tqdm(baskets):
            try:
                security_frame = fdr.DataReader(security)
                
                r"""ohlcv pre-processing"""
                security_frame.columns = list(map(lambda x: x.lower(), security_frame.columns)) 
                security_frame.index.names = list(map(lambda x: x.lower(), security_frame.index.names))
                security_frame = security_frame[['open', 'high', 'low', 'close', 'volume']]
                
                self.dict[security] = security_frame
                security_frame.to_csv(os.path.join(to_dir, f'{security}.csv'))
                successes[security] = {'Table_NumRows':security_frame.shape[0],
                                       'Table_NumColumns':security_frame.shape[1],
                                       'Table_Start':security_frame['Date'].iloc[0],
                                       'Table_End':security_frame['Date'].iloc[-1],
                                       }
        
            except:
                failures.append(security)
                continue
        
        self.successes.update(successes)
        for success in list(filter(lambda x: x in self.successes, self.failures)):
            self.failures.remove(success)
        self.failures.extend(failures)
        logger.normal_logger.info('[DATAVENDOR] OHLVC FOR {tickers} TICKERS - Failures list: {failures}'.format(tickers=len(list(self.successes.keys())), failures=self.failures))    
        self.ohlcv_logger_for_successes(message='from_fdr', updated_basket_info=self.successes, 
                                    update_log_dir=update_log_dir, update_log_file=update_log_file, country=country)
        return self 


    def fundamentals_from_yahooquery(self, baskets=None, from_dir=None, to_dir=None, update_log_dir=None, update_log_file=None, country=None, modules=None, process=True,        
                                    asynchronouse=False, backoff_factor=0.3, formatted=False, max_workers=12, proxies=None, retry=5, 
                                    status_forcelist=[404, 429, 500, 502, 503, 504], timeout=5, validate=False,verify=True):

        r""" No Update log formatted in json is currently available"""
        if not baskets:
            baskets = self.baskets
        if not country:
            country = self.country
        try:
            ticker = Ticker(symbols=baskets, asynchronouse=asynchronouse, backoff_factor=backoff_factor, country=country,
                        formatted=formatted, max_workers=max_workers, proxies=proxies, retry=retry, status_forcelist=status_forcelist, timeout=timeout,
                        validate=validate, verify=verify, progress=True)
        except Exception as e:
            logger.normal_logger.error(e)  
            return
        
                
        if type(modules) == str:
            logger.normal_logger.info('[DATAVENDOR] SINGLE MODULE INPUT -> {Ticker1:Value1, Ticker2:Value2}')
            module_temp_outer = getattr(ticker,"get_modules")(self.fundamentals_modules_fromyahooquery_dict[modules][0])
            fundamentals = dict()
            for tck in baskets:
                fundamentals[tck] = module_temp_outer[tck].get(self.fundamentals_modules_fromyahooquery_dict[modules][1])
            self.dict = fundamentals
            self.pdframe = pd.DataFrame(fundamentals.items(), columns=['ticker', modules])
            self.pdframe.to_csv(os.path.join(to_dir, "fundamentals.csv"), index=False)

        if type(modules) == list:
            logger.normal_logger.info('[DATAVENDOR] MULTIPLE MODULE INPUT -> {Ticker1:{MODULE1: VALUE1, MODULE2: VALUE2}, Ticker2:{MODULE1: VALUE3, MODULE2, VAULE4}}')
            modules_input = list(set(list(map(lambda x: self.fundamentals_modules_fromyahooquery_dict[x][0], modules))))
            module_temp_outer = getattr(ticker,"get_modules")(modules_input)
            fundamentals = dict()
            for tck in baskets:
                fundamentals[tck] =dict()
                for module in modules:
                    module_temp_inner = module_temp_outer[tck].get(self.fundamentals_modules_fromyahooquery_dict[module][0])
                    module_temp_second_inner = module_temp_inner.get(self.fundamentals_modules_fromyahooquery_dict[module][1])
                    fundamentals[tck].update({self.fundamentals_modules_fromyahooquery_dict[module][2]:module_temp_second_inner})
                  
            self.dict = fundamentals
            pdframe = pd.DataFrame(fundamentals).T
            pdframe.index.name = 'ticker'
            self.pdframe = pdframe
            self.pdframe.to_csv(os.path.join(to_dir, "fundamentals.csv"), index=True)
            

        _success = list(self.dict.keys())
        self.successes = fundamentals
        failure = list(filter(lambda x: not x in _success, baskets))
        self.failures.extend(failure)
        logger.normal_logger.info('[DATAVENDOR] FUNDAMENTALS {modules} FOR {tickers} TICKERS - Failures list: {failures}'.format(modules=modules, tickers=len(list(self.successes.keys())), failures=self.failures))
        self.fundamentals_logger_for_success(modules=modules, updated_basket=_success, update_log_dir=update_log_dir, update_log_file=update_log_file, country=country) 
        return self

    def fundamentals_from_local(self, baskets=None, from_dir=None, update_log_dir=None, update_log_file=None):
          
        from_dir = from_dir
        update_log_dir = update_log_dir
        update_log_file = update_log_file
        
        r"""Load from LOCAL directories"""
        num_baskets = len(baskets)
        logger.normal_logger.info(f'[DATAVENDOR] LOAD {num_baskets} BASKETS FROM LOCAL {from_dir}')
        main_frame = pd.read_csv(os.path.join(from_dir, 'fundamentals.csv'),index_col='ticker')
        self.pdframe = main_frame.loc[baskets]
        self.dict = main_frame.to_dict('index')

        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))
        self.log = update_log 

        return self


    def ohlcv_logger_for_successes(self, message=False, updated_basket_info=False, 
                                update_log_dir=None, update_log_file=None, country=False):
        
        if country == 'united states':
            today = datetime.datetime.now(timezone('US/Eastern'))
            tz = timezone('US/Eastern')
        if country == 'korea':
            today = datetime.datetime.now(timezone('Asia/Seoul'))
            tz = timezone('Asia/Seoul')
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))     
        updated_basket = list(updated_basket_info.keys())
        for security in updated_basket:
            update_log[security] = {'WhenDownload':today.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                     'WhenDownload_TZ':today.tzname(),
                                      'HowDownload':message,
                                      'Table_NumRows':updated_basket_info[security]['Table_NumRows'],
                                      'Table_NumColumns':updated_basket_info[security]['Table_NumColumns'],
                                      'Table_Start':updated_basket_info[security]['Table_Start'],
                                      'Table_End':updated_basket_info[security]['Table_End'],
                                      }

        with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
            json.dump(json.dumps(update_log, indent=4), log)
        logger.normal_logger.info(f'[DATAVENDOR] OHLCV JSON LOG SUCCESS - {updated_basket} Logged in {update_log_file}')    
        self.log = update_log

    def fundamentals_logger_for_success(self, modules=False ,updated_basket=False,
                                        update_log_dir=None, update_log_file=None, country=False):

        if country == 'united states':
            today = datetime.datetime.now(timezone('US/Eastern'))
            tz = timezone('US/Eastern')
        if country == 'korea':
            today = datetime.datetime.now(timezone('Asia/Seoul'))
            tz = timezone('Asia/Seoul')
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))
        update_log['Modules'] = modules
        update_log['WhenDownload'] = today.strftime('%Y-%m-%d %H:%M:%S.%f')
        update_log['WhenDownload_TZ'] = today.tzname()
        update_log['Baskets'] = updated_basket

        with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
            json.dump(json.dumps(update_log, indent=4), log)
        logger.normal_logger.info(f'[DATAVENDOR] FUNDAMENTALS JSON LOG SUCCESS - {modules} of {updated_basket} Logged in {update_log_file}')    
        self.log = update_log
     
    def MBM_into_local(self, market='kospi'):
        download(n=30)
        
    def MBM_from_local(self, market='GLOBAL', date='2010-01-01', mode='Close', cut=None, baskets=None, usage=None):
        if market.upper() == 'KOSPI':
            DF = kospi(date=date, mode=mode, cut=cut, baskets=baskets)
        elif market.upper() == 'KOSDAQ':
            DF = kosdaq(date=date, mode=mode, cut=cut, baskets=baskets)
        elif market.upper() == 'KONEX':
            DF = konex(date=date, mode=mode, cut=cut, baskets=baskets)
        elif market.upper() == 'NYSE':
            DF = None
        elif market.upper() == 'NASDAQ':
            DF = None
        elif market.upper() == 'AMEX':
            DF = None
        elif market.upper() == 'S&P500':
            DF = None
        elif market.upper() == 'HKEX':
            DF = None
        elif market.upper() == 'HOSE':
            DF = None
        elif market.upper() == 'SSE':
            DF = None
        elif market.upper() == 'TSE':
            DF = None
        else:
            DF = all_exchanges(date=date, mode=mode, cut=cut, baskets=baskets, usage=usage)
        return DF



r"""
log form

ohlcv_{interval}.json: {ticekr1: {'WhenDownload':today.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'WhenDownload_TZ':today.tzname(),
                    'HowDownload':message,
                    'Table_NumRows':updated_basket_info[security]['Table_NumRows'],
                    'Table_NumColumns':updated_basket_info[security]['Table_NumColumns'],
                    'Table_Start':updated_basket_info[security]['Table_Start'],
                    'Table_End':updated_basket_info[security]['Table_End'],
                                      }
                        ticker2 ~ }              

fundamentals.json:{'Modules':list(modules), 'WhenDownload':today.strfimte('%Y-%m-%d %H:%M:%S.%f'), 'WhenDownload_TZ':today.tzname(), 'Baskets':list(tickers)}
"""
