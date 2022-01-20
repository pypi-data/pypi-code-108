from ailever.investment import __fmlops_bs__ as fmlops_bs
from numpy import exp
from pandas.core import indexing

from ...path import refine
from .._base_transfer import DataTransferCore
from ..logger import update_log
from ..logger import Logger
from ..fmlops_management import FS1d_Manager
from .datavendor import DataVendor

from typing import Optional, Any, Union, Callable, Iterable
from pytz import timezone

import datetime
import pandas as pd
import numpy as np
import os
import json

r"""
Integrated Loader for all types of financial datasets
DataVendor Source: yahooquery, financial datareader

Unites States Stock market Timezone : EST 09:30 ~ 16:00
"""

# for logger
logger = Logger()
log_dirname = fmlops_bs.core['MS'].path
update_log_dict = update_log

# dataset paths
dataset_dirname = fmlops_bs.core['FS'].path

class IntegratedLoader:
    def __init__(self):
        self._fs1d_manager = FS1d_Manager() # feature_store.1d

    def __call__(self, baskets:list):
        return None
    
    def feature_store_1d(self, command:str):
        pass

    def _listdir(self, fmlops_symbol=None):
        return getattr(self, f'_{fmlops_symbol}_manager').listdir()

    def _listfiles(self, fmlops_symbol=None):
        return getattr(self, f'_{fmlops_symbol}_manager').listfiles()

    def _remove(self, fmlops_symbol=None):
        pprint(getattr(self, f'_{fmlops_symbol}_manager').listfiles())
        if fmlops_sysbol == 'fmr':
            id = int(input('ID : '))
            answer = input(f"Type 'Yes' if you really want to delete the model{id} in forecasting model registry.")
            if answer == 'Yes':
                model_saving_infomation = self._fmr_manager.local_finder(entity='id', target=id)
                self._fmr_manager.remove(name=model_saving_infomation['model_saving_name'])
        else:
            answer = input(f"Which file do you like to remove? : ")
            getattr(self, f'_{fmlops_symbol}_manager').remove(name=answer)

    def _clearall(self, fmlops_symbol=None):
        answer = input(f"Type 'YES' if you really want to delete all models in forecasting model registry.")
        if answer == 'YES':
            getattr(self, f'_{fmlops_symbol}_manager').clearall()
    
    def _copyall(self, fmlops_symbol=None):
        getattr(self, f'_{fmlops_symbol}_manager').copyall()

class Loader:
    baskets = None
    from_dir = None
    to_dir = None
    fundamentals_modules_fromyahooquery = DataVendor.fundamentals_modules_fromyahooquery
    fmf = DataVendor.fundamentals_modules_fromyahooquery

    def __init__(self, baskets=None, from_dir=dataset_dirname, to_dir=dataset_dirname, update_log_dir=log_dirname, update_log_file=None):
        self.baskets = baskets
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.update_log_dict = update_log_dict
        self.update_log_dir = update_log_dir
        self.update_log_file = update_log_file
        

    def ohlcv_loader(self, baskets:Iterable[str]=None, from_dir=None, to_dir=None, 
                    update_log_dir=None, update_log_file=None, country='united states', interval='1d', source='yahooquery'):

        r"""---------- Initialzing dataset directories ----------"""
        if not from_dir:
            from_dir = self.from_dir    
            logger.normal_logger.info(f'[LOADER] FROM_DIR INPUT REQUIRED - Default Path:{from_dir}')
        if not to_dir:
            to_dir = self.to_dir                
            logger.normal_logger.info(f'[LOADER] TO_DIR INPUT REQUIRED - Default Path:{to_dir}')

        r"""---------- Initialzing Timezone ----------""" 
        format_time_full = '%Y-%m-%d %H:%M:%S.%f'
        format_time_date = '%Y-%m-%d'
        if country == 'united states':
            today = datetime.datetime.now(timezone('US/Eastern'))
            tz = timezone('US/Eastern')
            now = datetime.datetime.now(tz)
            now_open = tz.localize(datetime.datetime(now.year, now.month, now.day, 9, 30, 0, 0))
            now_close = tz.localize(datetime.datetime(now.year, now.month, now.day, 16, 0, 0, 0))
        if country == 'korea':
            today = datetime.datetime.now(timezone('Asia/Seoul'))
            tz = timezone('Asia/Seoul')
            now = datetime.datetime.now(tz)
            now_open = tz.localize(datetime.datetime(now.year, now.month, now.day, 9, 0, 0, 0))
            now_close = tz.localize(datetime.datetime(now.year, now.month, now.day, 16, 0, 0, 0))
 
        r"""--------- Initializing UPDATE log directoreis ----------"""
        if update_log_dir:
            if not os.path.isdir(update_log_dir):
                os.mkdir(update_log_dir)

        if not update_log_dir:
            update_log_dir = self.update_log_dir
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_DIR INPUT REQUIRED - Default Path:{update_log_dir}')
            if not os.path.isdir(update_log_dir):
                os.mkdir(update_log_dir)
        
        r"""---------- Initializing UPDATE log file name -----------"""
        if not update_log_file:
            update_log_key = f'ohlcv_{interval}'
            update_log_file = self.update_log_dict[update_log_key]
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_FILE INPUT REQUIRED - Default Path:{update_log_file}')

        r"""---------- Initializing UPDATE log file ----------"""
        
        if not os.path.isfile(os.path.join(update_log_dir, update_log_file)):
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_FILE DOES NOT EXIST - Make {update_log_file} in {update_log_dir}')
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(dict(), indent=4), log)
            update_log = dict()            
            for existed_security in map(lambda x: x[:-4], filter(lambda x: (x[-3:] == 'csv') and ("-" not in x) and ("+" not in x), os.listdir(from_dir))):
                update_log[existed_security] = {'WhenDownload':today.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                'WhenDownload_TZ':today.tzname(),
                                                'HowDownload':'origin',
                                                'Table_NumRows':None,
                                                'Table_NumColumns':None,
                                                'Table_Start':None,
                                                'Table_End':None,
                                                }         
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(update_log, indent=4), log)
        r"""---------- Double check for UPDATE log file ---------"""
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))
        if not update_log:
            logger.normal_logger.info('[LOADER] UPDATE_LOG_FILE IS EMPTY - Rewrite with exisiting directories')
            update_log = dict()            
            for existed_security in map(lambda x: x[:-4], filter(lambda x: (x[-3:] == 'csv') and ("_" not in x) and ("+" not in x), os.listdir(from_dir))):
                update_log[existed_security] = {'WhenDownload':today.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                'WhenDownload_TZ':today.tzname(),
                                                'HowDownload':'origin',
                                                'Table_NumRows':None,
                                                'Table_NumColumns':None,
                                                'Table_Start':None,
                                                'Table_End':None,
                                                }         
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(update_log, indent=4), log)    

        r"---------- Initializing SELECT baskets ----------"
        ## Update log file loading    
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))

        ### Case 1) -> No Baskets    
        if not baskets:
            up_to_date_from_local = None
            serialized_objects = os.listdir(from_dir)
            serialized_object =list(filter(lambda x: (x[-3:] == 'csv') and ('_' not in x) and ('+' not in x), serialized_objects))
            baskets_in_dir = list(map(lambda x: x[:-4], serialized_object))
            if not baskets_in_dir:
                logger.normal_logger.info("[LOADER] NO BASKETS INPUT & NO BASKETS IN DIR")
                return
            if not update_log:
                logger.normal_logger.info(f'[LOADER] EMPTY UPDATE LOG -> Baskets {baskets_in_dir} from {from_dir}')
                select_baskets = baskets_in_dir
            if update_log:
                format_time_full = format_time_full ; now = now ; now_open = now_open ; now_close = now_close
                if interval == '1d':
                    baskets_date_dict = dict()
                    logger.normal_logger.info('[LOADER] INTERVAL BASED ON 1D')
                    for ticker in (update_log.keys()):
                        try:
                            dates = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_full))
                            baskets_date_dict[ticker] = tz.localize(datetime.datetime(dates.year, dates.month, dates.day, now_close.hour, now_close.minute, now_close.second, now_close.microsecond))                    
                        except ValueError:
                            dates = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_date))
                            baskets_date_dict[ticker] = tz.localize(datetime.datetime(dates.year, dates.month, dates.day, now_close.hour, now_close.minute, now_close.second, now_close.microsecond))                    
                    logger.normal_logger.info(f'[LOADER] NO BASKETS INPUT -> Baskets {baskets_in_dir} from {from_dir}')
                    if None in list(baskets_date_dict.values()):
                        logger.normal_logger.info(f'[LOADER] ONE OF TICKERS IN THE BASETS HAS NO TIME RECORDS - Update All:{baskets_in_dir}')
                    if not None in list(baskets_date_dict.values()):
                            outdated_baskets = list(dict(filter(lambda x: np.busday_count(datetime.datetime.strftime(x[1],'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))>=2,baskets_date_dict.items())).keys())
                            semi_outdated_baskets = list(dict(filter(lambda x: np.busday_count(datetime.datetime.strftime(x[1],'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))==1,baskets_date_dict.items())).keys())
                            if now>now_close:
                                select_baskets = semi_outdated_baskets + outdated_baskets
                                up_to_date_baskets = list(filter(lambda x: x not in (outdated_baskets+semi_outdated_baskets), baskets_in_dir))
                                if not select_baskets:
                                    logger.normal_logger.info(f'[LOADER] BASKETS ALL UP-TO-DATE - Loading from Local {from_dir}')
                                    datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                    return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                                if select_baskets:
                                    if not up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                    if up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                        up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                            if now<=now_close:
                                select_baskets = outdated_baskets
                                up_to_date_baskets = list(filter(lambda x: x not in (outdated_baskets), baskets_in_dir))
                                if not select_baskets:
                                    logger.normal_logger.info(f'[LOADER] BASKETS ALL UP-TO-DATE - Loading  from Local {from_dir}')
                                    datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                    return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                                if select_baskets:
                                    if not up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                    if up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                        up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                if interval != '1d':
                    baskets_time_dict = dict()
                    logger.normal_logger.info(f'[LOADER] INTERVAL BASED ON <> 1D')
                    for ticker in (update_log.keys()):
                            try:
                                baskets_time_dict[ticker] = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_full))
                            except ValueError:
                                baskets_time_dict[ticker] = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_date))
                    logger.normal_logger.info(f'[LOADER] NO BASKETS INPUT -> Baskets {baskets_in_dir} from {from_dir}')
                    if None in list(baskets_time_dict.values()):
                        logger.normal_logger.info(f'[LOADER] ONE OF TICKERS IN THE BASETS HAS NO TIME RECORDS - Update All:{baskets_in_dir}')
                    if not None in list(baskets_time_dict.values()):
                            outdated_baskets = list(dict(filter(lambda x: now > x[1],baskets_time_dict.items())).keys())
                            select_baskets = outdated_baskets
                            up_to_date_baskets = list(filter(lambda x: x not in (outdated_baskets), baskets_in_dir))
                            if not select_baskets:
                                logger.normal_logger.info(f'[LOADER] BASKETS ALL UP-TO-DATE - Loading  from Local {from_dir}')
                                datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                            if select_baskets:
                                    if not up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                    if up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                        up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
           
        ### Case 2) -> Baskets
        else:
            up_to_date_from_local = None
            if not update_log:
                select_baskets = baskets   
                logger.normal_logger.info(f'[LOADER] EMPTY UPDATE LOG')
            else:
                baskets_in_log = update_log.keys()
                new_baskets = list(filter(lambda x: x not in baskets_in_log, baskets))
                old_baskets = list(filter(lambda x: x in baskets_in_log, baskets))
                if not old_baskets:
                    select_baskets = new_baskets
                    logger.normal_logger.info(f'[LOADER] ALL NEW BASKETS')
                if old_baskets:
                    format_time_full = format_time_full ; now = now ; now_open = now_open ; now_close = now_close
                    if interval == '1d':
                        baskets_date_dict = dict()
                        logger.normal_logger.info('[LOADER] INTERVAL BASED ON 1D')
                        for ticker in old_baskets:
                            try:
                                dates = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_full))
                                baskets_date_dict[ticker] = tz.localize(datetime.datetime(dates.year, dates.month, dates.day, now_close.hour, now_close.minute, now_close.second, now_close.microsecond))                    
                            except ValueError:
                                dates = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_date))
                                baskets_date_dict[ticker] = tz.localize(datetime.datetime(dates.year, dates.month, dates.day, now_close.hour, now_close.minute, now_close.second, now_close.microsecond))                    
                        if None in list(baskets_date_dict.values()):
                            logger.normal_logger.info(f'[LOADER] ONE OF TICKERS IN THE BASETS HAS NO TIME RECORDS - Update All:{baskets}')
                        if not None in list(baskets_date_dict.values()):
                                outdated_baskets = list(dict(filter(lambda x: np.busday_count(datetime.datetime.strftime(x[1],'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))>=2,baskets_date_dict.items())).keys())
                                semi_outdated_baskets = list(dict(filter(lambda x: np.busday_count(datetime.datetime.strftime(x[1],'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))==1,baskets_date_dict.items())).keys())
                                if now>now_close:
                                    select_baskets = semi_outdated_baskets + outdated_baskets + new_baskets
                                    up_to_date_baskets = list(filter(lambda x: x not in (outdated_baskets+semi_outdated_baskets), old_baskets))
                                    if not select_baskets:
                                        logger.normal_logger.info(f'[LOADER] NO NEW BASKETS & ALL OLD BASKETS UP-TO-DATE - Loading  from Local {from_dir}')
                                        datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                                    if select_baskets:
                                        if not up_to_date_baskets:
                                            logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                        if up_to_date_baskets:
                                            logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                            up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                            up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                                if now<=now_close:
                                    select_baskets = outdated_baskets + new_baskets
                                    up_to_date_baskets = list(filter(lambda x: x not in outdated_baskets, old_baskets))
                                    if not select_baskets:
                                        logger.normal_logger.info(f'[LOADER] BASKETS ALL UP-TO-DATE - Loading  from Local {from_dir}')
                                        datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                                    if select_baskets:
                                        if not up_to_date_baskets:
                                            logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                        if up_to_date_baskets:
                                            logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                            up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                            up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)

                    if interval != '1d':
                        baskets_time_dict = dict()
                        logger.normal_logger.info('[LOADER] INTERVAL BASED ON != 1D')
                        for ticker in old_baskets:
                            try:
                                baskets_time_dict = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_full))
                            except ValueError:
                                baskets_time_dict = tz.localize(datetime.datetime.strptime(update_log[ticker]["Table_End"],format_time_date))
                        if None in list(baskets_time_dict.values()):
                            logger.normal_logger.info(f'[LOADER] ONE OF TICKERS IN THE BASETS HAS NO TIME RECORDS - Update All:{baskets}')
                        if not None in list(baskets_time_dict.values()):    
                            outdated_baskets = list(dict(filter(lambda x: now > x[1],baskets_time_dict.items())).keys())
                            select_baskets = outdated_baskets + new_baskets
                            up_to_date_baskets = list(filter(lambda x: x not in (outdated_baskets), old_baskets))
                            if not select_baskets:
                                logger.normal_logger.info(f'[LOADER] NO NEW BASKETS ALL OLD BASKETS UP-TO-DATE - Loading  from Local {from_dir}')
                                datavendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                return datavendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
                            if select_baskets:
                                    if not up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] All BASKETS NEEDS UPDATE')
                                    if up_to_date_baskets:
                                        logger.normal_logger.info(f'[LOADER] UP-TO-DATE BASKETS - Loading from Local {from_dir}')
                                        up_to_date_vendor = DataVendor(baskets=up_to_date_baskets, country=country)
                                        up_to_date_from_local =  up_to_date_vendor.ohlcv_from_local(baskets=up_to_date_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
     
        r""" ---------- Executing DataVendor ----------"""   
        logger.normal_logger.info(f"[LOADER] EXECUTING DATAVENDOR")
        datavendor = DataVendor(baskets=select_baskets, country=country)
        
        if interval == '1d':
            logger.normal_logger.info('[LOADER] TBD * from yahooquery currently only supporting \'1d\' interval.')

        if source == 'yahooquery':
            r""" --------- ohlcv from yahooquery ----------"""
            logger.normal_logger.info('[LOADER] * from yahooquery')
            if up_to_date_from_local:
                new_baskets = datavendor.ohlcv_from_yahooquery(baskets=select_baskets, from_dir=from_dir, to_dir=to_dir, 
                                                    update_log_dir=update_log_dir, update_log_file=update_log_file, interval=interval, country=country, progress=True)
                new_baskets.dict.update(up_to_date_from_local.dict)
                return new_baskets
            else:
                return datavendor.ohlcv_from_yahooquery(baskets=select_baskets, from_dir=from_dir, to_dir=to_dir, 
                                                    update_log_dir=update_log_dir, update_log_file=update_log_file, interval=interval, country=country, progress=True)
            
        elif source == 'fdr':
            r""" ---------- ohlcv from fdr reader ----------"""
            logger.normal_logger.info('[LOADER] * from finance-datareader')
            if up_to_date_from_local:
                new_baskets = datavendor.ohlcv_from_fdr(baskets=select_baskets, from_dir=from_dir, to_dir=to_dir, 
                                                    update_log_dir=update_log_dir, update_log_file=update_log_file, interval=interval, country=country, progress=True)
                new_baskets.dict.update(up_to_date_from_local.dict)
                return new_baskets
            else:
                return datavendor.ohlcv_from_fdr(baskets=select_baskets, from_dir=from_dir, to_dir=to_dir, 
                                                    update_log_dir=update_log_dir, update_log_file=update_log_file, interval=interval, country=country, progress=True)
            


    def fundamentals_loader(self, baskets:Iterable[str], from_dir=dataset_dirname, to_dir=dataset_dirname, 
                    update_log_dir=None, update_log_file=None, interval=None, country='united states', modules=None, frequency = None, source='yahooquery'):
        r"""---------- Initializing modules ----------"""
        if not modules:
            modules = list(self.fmf)
            logger.normal_logger.info("[LOADER] MODULES INPUT[LIST, STR] REQUIRED - Default Modules: {modules}")
        r"""---------- Initialzing dataset directories ----------"""
        if not from_dir:
            from_dir = self.from_dir    
            logger.normal_logger.info(f'[LOADER] FROM_DIR INPUT REQUIRED - Default Path:{from_dir}')
        if not to_dir:
            to_dir = self.to_dir           
            logger.normal_logger.info(f'[LOADER] TO_DIR INPUT REQUIRED - Default Path:{to_dir}')                      
        r"""---------- Initialzing Timezone ----------"""
        format_time_full = '%Y-%m-%d %H:%M:%S.%f'
        format_time_date = '%Y-%m-%d'
        if country == 'united states':
            today = datetime.datetime.now(timezone('US/Eastern'))
            tz = timezone("US/Eastern")
            now = datetime.datetime.now(tz)
        if country == 'korea':
            today = datetime.datetime.now(timezone('Asia/Seoul'))
            tz = timezone("Asia/Seoul")
            now = datetime.datetime.now(tz)
        r"""--------- Initializing UPDATE log directoreis ----------"""
        if update_log_dir:
            if not os.path.isdir(update_log_dir):
                os.mkdir(update_log_dir)
        if not update_log_dir:
            update_log_dir = self.update_log_dir
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_DIR INPUT REQUIRED - Default Path:{update_log_dir}')
        if not os.path.isdir(update_log_dir):
            os.mkdir(update_log_dir)
        r"""---------- Initializing UPDATE log file name -----------"""
        if not update_log_file:
            update_log_key = f'fundamentals'
            update_log_file = self.update_log_dict[update_log_key]
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_FILE INPUT REQUIRED - Default Path:{update_log_file}')
        r"""---------- Initializing UPDATE log file ----------"""
        if not os.path.isfile(os.path.join(update_log_dir, update_log_file)):
            logger.normal_logger.info(f'[LOADER] UPDATE_LOG_FILE DOES NOT EXIST - Make {update_log_file} in {update_log_dir}')
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(dict(), indent=4), log)
            update_log = dict()            
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = list()
                logger.normal_logger.info("[LOADER] NO FUNDAMENTALS BASKETS CSV")
            if os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = pd.read_csv(os.path.join(from_dir, 'fundamentals.csv'))['ticker'].tolist()
            update_log['Modules'] = list()
            update_log['WhenDownload'] = None
            update_log['WhenDownload_TZ'] = None
            update_log['Baskets'] = baskets_in_csv
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(update_log, indent=4), log)
        r"""---------- Double check for UPDATE log file ---------"""
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))
        if not update_log:
            logger.normal_logger.info('[LOADER] UPDATE_LOG_FILE IS EMPTY - Rewrite with exisiting directories')
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(dict(), indent=4), log)
            update_log = dict()            
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = list()
                logger.normal_logger.info("[LOADER] NO FUNDAMENTALS BASKETS CSV")
            if os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = pd.read_csv(os.path.join(from_dir, 'fundamentals.csv'))['ticker'].tolist()
            update_log['Modules'] = list()
            update_log['WhenDownload'] = None
            update_log['WhenDownload_TZ'] = None
            update_log['Baskets'] = baskets_in_csv
            with open(os.path.join(update_log_dir, update_log_file), 'w') as log:
                json.dump(json.dumps(update_log, indent=4), log)
        r"---------- Initizlizing frequency ----------"
        if not frequency:
            frequency = 2
            logger.normal_logger.info(f"[LOADER] DEFAULT FREQUENCY {frequency}")

        r"---------- Initializing SELECT baskets ----------"
        ## Update log file loading    
        with open(os.path.join(update_log_dir, update_log_file), 'r') as log:
            update_log = json.loads(json.load(log))

        ### Case 1) -> No Baskets    
        if not baskets:
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = list()
                logger.normal_logger.info("[LOADER] NO BASKETS INPUT & NO FUNDAMENTALS BASKETS CSV")
                return
            if os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = pd.read_csv(os.path.join(from_dir, 'fundamentals.csv'))['ticker'].tolist()
            if not update_log:
                logger.normal_logger.info(f'[LOADER] EMPTY UPDATE LOG')
                select_baskets = baskets_in_csv
            if update_log:
                baskets_in_log = update_log['Baskets']
                if not update_log['WhenDownload']: 
                    select_baskets = baskets_in_csv
                    logger.normal_logger.info(f'[LOADER] NO TIME RECORDS LOG')
                if update_log['WhenDownload']:
                    if modules != update_log['Modules']:
                        select_baskets = baskets_in_log
                        logger.normal_logger.info(f'[LOADER] MODULES {modules} CHANGED ALL REUPDATE')
                    if modules == update_log['Modules']:
                        format_time_full = format_time_full ; now = now ; log_date = tz.localize(datetime.datetime.strptime(update_log['WhenDownload'], format_time_full))
                        if np.busday_count(datetime.datetime.strftime(log_date,'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))>= frequency:
                            select_baskets = baskets_in_log 
                            logger.normal_logger.info(f'[LOADER] BASKETS OUTDATED BY {frequency} ALL REUPDATE')
                        if np.busday_count(datetime.datetime.strftime(log_date,'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d')) < frequency:
                            logger.normal_logger.info(f'[LOADER] ALL BASKETS UP-TO-DATE. LOAD FROM LOCAL {from_dir}')
                            datavendor = DataVendor(baskets=select_baskets, country=country)
                            return datavendor.fundamentals_from_local(baskets=select_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)
        ### Case 2) -> Baskets
        if baskets:
            if not update_log:
                logger.normal_logger.info(f'[LOADER] EMPTY UPDATE LOG')
                select_baskets = baskets
            if update_log:
                baskets_in_log = update_log['Baskets']
                if not update_log['WhenDownload']:
                    select_baskets = baskets
                    logger.normal_logger.info(f'[LOADER] NO TIME RECORDS LOG')
                if update_log['WhenDownload']:
                    new_baskets = list(filter(lambda x: x not in baskets_in_log, baskets))
                    old_baskets = list(filter(lambda x: x in baskets_in_log, baskets))
                    if modules != update_log['Modules']:
                        select_baskets = baskets
                        logger.normal_logger.info(f'[LOADER] MODULES {modules} CHANGED ALL REUPDATE')
                    if modules == update_log['Modules']:
                        format_time_full = format_time_full ; now = now ; log_date = tz.localize(datetime.datetime.strptime(update_log['WhenDownload'], format_time_full))
                        if baskets != old_baskets: 
                            select_baskets = baskets
                            logger.normal_logger.info(f'[LOADER] BASKETS CHANGED FROM OLD BASKETS TO NEW BASKETS')
                        if baskets == old_baskets:
                            if np.busday_count(datetime.datetime.strftime(log_date,'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d'))>= frequency:
                                select_baskets = baskets
                                logger.normal_logger.info(f'[LOADER] BASKETS OUTDATED BY {frequency} ALL REUPDATE')
                            if np.busday_count(datetime.datetime.strftime(log_date,'%Y-%m-%d'), datetime.datetime.strftime(now,'%Y-%m-%d')) < frequency:
                                logger.normal_logger.info(f'[LOADER] ALL BASKETS UP-TO-DATE. LOAD FROM LOCAL {from_dir}')
                                datavendor = DataVendor(baskets=old_baskets, country=country)
                                return datavendor.fundamentals_from_local(baskets=old_baskets, from_dir=from_dir, update_log_dir=update_log_dir, update_log_file=update_log_file)

        r""" ---------- Executing DataVendor ----------"""   
        logger.normal_logger.info(f"[LOADER] EXECUTING DATAVENDOR")
        datavendor = DataVendor(baskets=select_baskets, country=country)
        
        r""" --------- fundamentals from yahooquery ----------"""
        if source == 'yahooquery':
            logger.normal_logger.info('[LOADER] * from yahooquery')
            return datavendor.fundamentals_from_yahooquery(baskets=select_baskets, from_dir=from_dir, to_dir=to_dir, 
                                            update_log_dir=update_log_dir, update_log_file=update_log_file, country=country, modules=modules)
            

    def into_local(self, market='kospi'):
        DV = DataVendor()
        return DV.MBM_into_local(market=market)

    def from_local(self, baskets=None, market='GLOBAL', date='2010-01-01', mode='Close', usage=None):
        DV = DataVendor()
        return DV.MBM_from_local(market=market, date=date, mode=mode, baskets=baskets, usage=usage)


