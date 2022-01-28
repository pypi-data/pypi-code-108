from ailever.investment import __fmlops_bs__ as fmlops_bs
from ._base_transfer import DataTransferCore
from .logger import Logger
from .fmlops_loader_system import Loader, Preprocessor, parallelize
from .fmlops_loader_system.datavendor import DataVendor
from .mathematical_modules import regressor, scaler


import os
from re import I
from copy import deepcopy
from datetime import datetime
from pytz import timezone
import csv
import json
from itertools import combinations
from urllib.request import urlretrieve
import numpy as np
from numpy import linalg
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import FinanceDataReader as fdr
import statsmodels.api as sm
import statsmodels.tsa.api as smt
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.tsa.stattools import adfuller


core = fmlops_bs.core['FS']
from_dir = core.path
to_dir = core.path
logger = Logger()
loader = Loader()

class Screener(DataTransferCore):
    fundamentals_modules_fromyahooquery_dict = DataVendor.fundamentals_modules_fromyahooquery_dict
    fundamentals_modules_fromyahooquery = DataVendor.fundamentals_modules_fromyahooquery
    fmf = DataVendor.fundamentals_modules_fromyahooquery
    
    def __init__(self):
        self._decision_profiling()

    def _decision_profiling(self):
        self.decision_matrix  = None

    def _momentum_engine(self):
        pass

    def _fundamentals_engine(self):
        pass

    @staticmethod
    def fundamentals_screener(baskets=None, from_dir=from_dir, to_dir=to_dir, period=None, modules=None, sort_by=None, interval=None, frequency = None,country='united states', output='list'):
        """
        sory_by option
        ['DividendYield', 'FiveYrsDividendYield', 'DividendRate', 'Beta', 'EVtoEBITDA', 'Marketcap', 'EnterpriseValue']"""
        module_dict = Screener.fundamentals_modules_fromyahooquery_dict
        order_type = {'DividendYield': True, 'FiveYrsDiviendYield': False, 'DiviendRate': False, 'Beta': True, 'EVtoEBITDA': True, 'Marketcap': False, 'EnterpriseValue': False}
        if not from_dir:
            from_dir = from_dir   
            logger.normal_logger.info(f'[SCREENER] FROM_DIR INPUT REQUIRED - Default Path:{from_dir}')
        if not to_dir:
            to_dir = to_dir
            logger.normal_logger.info(f'[SCREENER] TO_DIR INPUT REQUIRED - Default Path:{to_dir}')
        if country == 'united states':
            today = datetime.now(timezone('US/Eastern'))
            tz = timezone('US/Eastern')
        if country == 'korea':
            today = datetime.now(timezone('Asia/Seoul'))
        if not interval:
            interval = '1d'
        if not baskets: 
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = list()
                logger.normal_logger.info(f"[SCREENER] NO BASKETS EXISTS from {from_dir}")
                return
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = pd.read_csv(os.path.join(from_dir, 'fundamentals.csv'))['ticker'].tolist()         
            baskets = baskets_in_csv ; num_baskets = len(baskets) 
            logger.normal_logger.info(f'[SCREENER] BASKETS INPUT REQUIRED - Default Basket: {num_baskets} baskets in the directory:{from_dir}.')    

        logger.normal_logger.info(f'[SCREENER] UPDATE FOR BASKETS')
        loader = Loader()
        if not modules:
            modules = list(loader.fmf)
        if not sort_by:
            preresults_pdframe = loader.fundamentals_loader(baskets=baskets, from_dir=from_dir, to_dir=to_dir, interval=interval, country=country, modules=modules, frequency=frequency).pdframe
        if sort_by:
            preresults_pdframe = loader.fundamentals_loader(baskets=baskets, from_dir=from_dir, to_dir=to_dir, interval=interval, country=country, modules=modules, frequency=frequency).pdframe[[module_dict[sort_by][2]]].sort_values(module_dict[sort_by][2], ascending=order_type[sort_by]) 
        results_list =  preresults_pdframe.index.tolist() 
        top10 = results_list[:10]
        results_pdframe = preresults_pdframe
        logger.normal_logger.info(f'[SCREENER] {sort_by} RANK YIELED: TOP 10 {top10}')
        if output=='list':
            return results_list
        if output=='pdframe':
            return results_pdframe

    @staticmethod
    def momentum_screener(baskets=None, from_dir=from_dir, interval=None, country='united states', period=None, to_dir=to_dir, output='list'):
        if not period:
            period = 10
            logger.normal_logger.info(f'[SCREENER] PERIOD INPUT REQUIRED - Default Period:{period}')
        if not from_dir:
            from_dir = from_dir
            logger.normal_logger.info(f'[SCREENER] FROM_DIR REQUIRED - Default Path:{from_dir}')
        if not to_dir:
            to_dir = to_dir
            logger.normal_logger.info(f'[SCREENER] TO_DIR INPUT REQUIRED - Default Path:{to_dir}')
        if not interval:
            interval ='1d'
            logger.normal_logger.info(f'[SCREENER] DEFAULT INTERVAL {interval}')
        if not baskets:            
            serialized_objects = os.listdir(from_dir)
            serialized_object =list(filter(lambda x: (x[-3:] == 'csv') and ('_' not in x) and ("+" not in x), serialized_objects))
            baskets_in_dir = list(map(lambda x: x[:-4], serialized_object))
            if not baskets_in_dir:
                logger.normal_logger.info(f'[SCREENER] NO BASKETS EXISTS in {from_dir}')
                return
            baskets = baskets_in_dir ; num_baskets = len(baskets) 
            logger.normal_logger.info(f'[SCREENER] BASKETS INPUT REQUIRED - Default Basket: {num_baskets} baskets in the directory:{from_dir}.')    

        logger.normal_logger.info(f'[SCREENER] UPDATE FOR BASKETS')
        loader = Loader()
        loader.ohlcv_loader(baskets=baskets, from_dir=from_dir, to_dir=to_dir, interval=interval, country=country)
        
        logger.normal_logger.info(f'[SCREENER] RECOMMANDATIONS BASED ON LATEST {period} DAYS.')
        
        prllz = parallelize(baskets=baskets, path=from_dir,
                            object_format='csv',
                            base_column='close',
                            date_column='date')

        base = prllz.ndarray
        tickers = prllz.pdframe.columns
        mapper = {idx:ticker for idx, ticker in enumerate(tickers)}

        x, y = np.arange(base.shape[0]), base
        bias = np.ones_like(x)
        X = np.c_[bias, x]

        b = linalg.inv(X.T@X) @ X.T @ y
        yhat = X@b
        recommand = yhat[-1] - yhat[-2]
        
        results_list = list(map(lambda x:mapper[x], np.argsort(recommand)[::-1]))
        results_pdframe = pd.DataFrame(results_list, columns= ['ticker'])
        rank_ndarray = results_pdframe.index.values + 1
        rank_series = pd.Series(rank_ndarray)
        rank_series.name = 'rank+'+str(period)
        results_pdframe = pd.concat([results_pdframe, rank_series], axis=1).set_index('ticker')
        recent_date = datetime.strftime(prllz.pdframe.index[-1], "%Y%m%d")
        results_pdframe.to_csv(f'momentum+screener+{period}+{recent_date}.csv', index=False)
        logger.normal_logger.info('[SCREENER] TOP 10 MOMENTUM FOR {period}: {top10}'.format(period=period, top10=results_list[:10]))
        
        if output=='list':
            return results_list
        if output=='pdframe':
            return results_pdframe
    
    @staticmethod
    def pct_change_screener(baskets=None, from_dir=None, to_dir=None, window=None, sort_by=None, ascending=None, interval=None, country='united states', output='list'):
        if not from_dir:
            path = from_dir   
            logger.normal_logger.info(f'[SCREENER] FROM_DIR INPUT REQUIRED - Default Path:{path}')
        if not to_dir:
            to_dir = to_dir
            logger.normal_logger.info(f'[SCREENER] TO_DIR INPUT REQUIRED - Default Path:{from_dir}')
        if country == 'united states':
            today = datetime.now(timezone('US/Eastern'))
            tz = timezone('US/Eastern')
        if country == 'korea':
            today = datetime.now(timezone('Asia/Seoul'))
        if not interval:
            interval = '1d'
        if not window:
            window = [1,5,20,60,120,240]
        if not sort_by:
            sort_by = 1
        sort_by_column = f'close+change{sort_by}'
        if not ascending:
            ascending = False
        if not baskets: 
            if not os.path.isfile(os.path.join(from_dir, 'pct_change.csv')):
                baskets_in_csv = list()
                logger.normal_logger.info(f"[SCREENER] NO BASKETS EXISTS from {from_dir}")
                return
            if not os.path.isfile(os.path.join(from_dir, 'fundamentals.csv')):
                baskets_in_csv = pd.read_csv(os.path.join(from_dir, 'pct_change.csv'))['ticker'].tolist()         
            baskets = baskets_in_csv ; num_baskets = len(baskets) 
            logger.normal_logger.info(f'[SCREENER] BASKETS INPUT REQUIRED - Default Basket: {num_baskets} baskets in the directory:{from_dir}.')    

        logger.normal_logger.info(f'[SCREENER] ACCESS PREPROCESSOR')
        pre = Preprocessor()
        preresults_dict = pre.pct_change(baskets=baskets, from_dir=from_dir, to_dir=to_dir, interval=interval, country=country, target_column='close', window=window, merge=False, kind='ticker').dict
        main_frame_list = list()
        for ticker in list(preresults_dict.keys()):
            ticker_frame = preresults_dict[ticker].iloc[-1:]
            ticker_frame['ticker'] = ticker
            ticker_frame.reset_index(inplace=True)
            ticker_frame.set_index('ticker', inplace=True)
            main_frame_list.append(ticker_frame)
        main_pdframe = pd.concat(main_frame_list, axis=0)
        
        try:
            main_pdframe = main_pdframe.sort_values(sort_by_column, ascending=ascending)
        except:
            logger.normal_logger.info(f"[SCREENER] NO RESPECTIVE PCT CHANGE EXISTS: Winodw {window}")
        
        results_pdframe = main_pdframe
        results_list = main_pdframe.index.tolist()
        top10 = results_list[:10]
        logger.normal_logger.info(f'[SCREENER] {sort_by_column} RANK YIELED: TOP 10 {top10}')
        if output=='list':
            return results_list
        if output=='pdframe':
            return results_pdframe


    @staticmethod
    def csv_compiler(from_dir, to_dir, now, format_time, target_list):
        return
        csv_list = list()
        with open(from_dir, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                csv_list.append(row)

        "recent_record = tz.localize(datetime.strptime(csv_list[-1][0], format_time))"
        if now < recent_record:
            logger.normal_logger.info("[SCREENER] File IS UP-TO-DATE")
        if now >= recent_record:
            with open(to_dir, 'a', newline="") as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(target_list.insert(0, datetime.strftime(now, format_time)))
                logger.normal_logger.info('[SCREEENR] {now} LIST ADDED TO {to_dir}')
    

dummies = type('dummies', (dict,), {})
class ScreenerModule:
    def __init__(self, baskets, market='GLOBAL', date='2010-01-01', mode='Close'):
        self.prllz_df = loader.from_local(baskets=baskets, market=market, date=date, mode=mode)
        self.price_DTC = loader.from_local(baskets=baskets, market=market, date=date, mode=mode, usage='dataset')
        self.price_array = self.prllz_df[0] # self.price_array = self.price_DTC.ndarray
        self.securities = self.prllz_df[1]
        self.init_screening()

    def init_screening(self):
        self.highest_intrinsic_values = None
        self.highest_momenta = self.evaluate_momentum(self.prllz_df)
 
    def evaluate_momentum(self, Df=None, ADf=None, filter_period=300, capital_priority=True, regressor_criterion=1.5, seasonal_criterion=0.3, GC=False, V='KS11', download=False):
        assert bool(Df or ADf), 'Dataset Df or ADf must be defined.'
        self.dummies = dummies()
        self.dummies.__init__ = dict()

        if ADf:
            self.ADf = ADf
            self.Df = self.ADf['Close']
        else:
            self.Df = Df
        
        if capital_priority:
            norm = scaler.standard(self.Df[0][-filter_period:])
            self._portfolio_dataset = deepcopy(norm)
        else:
            norm = scaler.minmax(self.Df[0][-filter_period:])
            self._portfolio_dataset = deepcopy(norm)

        yhat = regressor(norm)
        container = yhat[-1,:] - yhat[0,:]

        self.index = list()
        self._index0 = np.where(container>=regressor_criterion)[0]

        recommended_stock_info = self.Df[1].iloc[self._index0]
        alert = list(zip(recommended_stock_info.Name.tolist(), recommended_stock_info.Symbol.tolist())); print(alert)
        

        # Short Term Investment Stock
        long_period = 300
        short_period = 30
        back_shifting = 0
        print('\n* Short Term Trade List')
        for i in self._index0:
            info = (i, long_period, short_period, back_shifting)
            selected_stock_info = self.Df[1].iloc[info[0]]
            result = self._stock_decompose(info[0], info[1], info[2], info[3], decompose_type='stl', resid_transform=True)

            x = scaler.minmax(result.seasonal)
            index = {}
            index['ref'] = set([295,296,297,298,299])
            index['min'] = set(np.where((x<seasonal_criterion) & (x>=0))[0])
            if index['ref']&index['min']:
                self.index.append(info[0])
                print(f'  - {selected_stock_info.Name}({selected_stock_info.Symbol}) : {info[0]}')

        if GC:
            self.Granger_C()

        # Visualization
        if V:
            df = pd.DataFrame(self.Df[0][:, self.index])
            df.columns = self.Df[1].iloc[self.index].Name
            ks11 = Df[3][V][self.Df[4]][-len(df):].reset_index().drop('index', axis=1)
            ks11.columns = [V]
            df = pd.concat([ks11, df], axis=1)

            plt.figure(figsize=(25,25)); layout = (5,1); axes = dict()
            axes[0] = plt.subplot2grid(layout, (0, 0), rowspan=1)
            axes[1] = plt.subplot2grid(layout, (1, 0), rowspan=1)
            axes[2] = plt.subplot2grid(layout, (2, 0), rowspan=1)
            axes[3] = plt.subplot2grid(layout, (3, 0), rowspan=2)

            for name, stock in zip(df.columns, df.values.T):
                axes[0].plot(stock, label=name)
                axes[0].text(len(stock), stock[-1], name)
            axes[0].set_title('STOCK')
            axes[0].legend(loc='lower left')
            axes[0].grid(True)

            df.diff().plot(ax=axes[1])
            axes[1].set_title('DIFF')
            axes[1].legend(loc='lower left')
            axes[1].grid(True)

            for i, name in enumerate(df.columns):
                pd.plotting.autocorrelation_plot(df.diff().dropna().iloc[:,i], ax=axes[2], label=name)
            axes[2].set_title('ACF')
            axes[2].grid(True)
            axes[2].legend(loc='upper right')
            
            # Correlation
            axes[3].set_title('Correlation')
            sns.set_theme(style="white")
            sns.despine(left=True, bottom=True)
            mask = np.triu(np.ones_like(df.corr(), dtype=bool))
            cmap = sns.diverging_palette(230, 20, as_cmap=True)
            sns.heatmap(df.corr(), mask=mask, cmap=cmap, square=True, annot=True, linewidths=.5, ax=axes[3])
            
            plt.tight_layout()
            if download:
                plt.savefig('IAF.pdf')
            #plt.show()

    def Granger_C(self, stocks=None):
        # >>> ailf.Granger_C(['삼성전자', '삼성전자우'])
        if not stocks:
            IndexSet = self.index
        else:
            assert len(stocks) >= 2, 'The Size of IndexSet must have 2 at least.'

            IndexSet = []
            for stock in stocks:
                stock_info = self.Df[1].Name == stock
                IndexSet.append(np.argmax(stock_info.values.astype(np.int)))

        causalities = dict()
        for i,j in combinations(IndexSet, 2):
            sample1 = np.c_[self.Df[0][:,i], self.Df[0][:,j]]
            sample2 = np.c_[self.Df[0][:,j], self.Df[0][:,i]]
            causalities[f'{i},{j}'] = self._Granger_C(sample1, sample2, maxlag=5)

        for i, (key, value) in enumerate(causalities.items()):
            index_x, index_y = np.where(value < 0.05)
            stock_num1 = int(key.split(',')[0])
            stock_num2 = int(key.split(',')[1])
            print('[ *', self.Df[1].iloc[stock_num1].Name, ':', self.Df[1].iloc[stock_num2].Name, ']')
            for lag, stock in zip(index_x, index_y):
                lag += 1
                stock_num = int(key.split(',')[stock])
                print(f'At the {lag} lag, {self.Df[1].iloc[stock_num].Name} is granger caused by') 

    @staticmethod
    def _Granger_C(sample1, sample2, maxlag=5):
        x = sm.tsa.stattools.grangercausalitytests(sample1, maxlag=maxlag, verbose=False)
        y = sm.tsa.stattools.grangercausalitytests(sample2, maxlag=maxlag, verbose=False)

        _x_pvals = []
        _y_pvals = []
        x_pvals = []
        y_pvals = []
        for i in range(1,maxlag+1):
            for value_x, value_y in zip(x[i][0].values(), y[i][0].values()):
                _x_pvals.append(value_x[1])
                _y_pvals.append(value_y[1])
            x_pval = sum(_x_pvals)/len(_x_pvals)
            y_pval = sum(_y_pvals)/len(_y_pvals)
            x_pvals.append(x_pval)
            y_pvals.append(y_pval)
        return np.array(list(zip(x_pvals, y_pvals)))


    def _querying(self, i=None):
        # i : (None) >
        if not i:
            i = self.index[0]

        # i : (str)Name >
        elif isinstance(i, str):
            SL = fdr.StockListing('KRX')
            selected_stock_info = SL.query(f"Name == '{i}'")
            # when self.Df[2](exception list info) have info for i
            if selected_stock_info.Symbol.tolist()[0] in self.Df[2]:
                price = fdr.DataReader(selected_stock_info.Symbol.values[0])[f"{self.Df[4]}"].values[-len(self.Df[0]):]
                _Df0 = np.c_[self.Df[0], price]
                _Df1 = self.Df[1].append(selected_stock_info)

                idx = self.Df[2].index(selected_stock_info.Symbol.values[0])
                self.Df[2].pop(idx)
                _Df2 = self.Df[2]
                _Df3 = self.Df[3]
                _Df4 = self.Df[4]
                
                self.Df = (_Df0, _Df1, _Df2, _Df3, _Df4)
                stock_info = self.Df[1].Name == selected_stock_info.Name.values[0]
                i = np.argmax(stock_info.values.astype(np.int))
                self.index = np.r_[self.index, i]

            # when self.Df[2](exception list info) don't have info for i
            else:
                stock_info = self.Df[1].Name == selected_stock_info.Name.values[0]
                i = np.argmax(stock_info.values.astype(np.int))
                self.index = np.r_[self.index, i]

        # i : (np.int64) ailf.index >
        else:
            pass

        return i


    def IndexReport(self, i=None, long_period=200, short_period=30, back_shifting=0, download=False):
        self.dummies.IndexReport = dict()

        with plt.style.context('seaborn-whitegrid'):
            _, axes = plt.subplots(4,1,figsize=(25,15))

        if not i:
            i = 'KS11'
        info = (i, long_period, short_period, back_shifting) # args params

        ##########################################################################
        print(f'* {info[0]}')
        
        axes[0].grid(True)
        axes[1].grid(True)
        axes[2].grid(True)
        axes[3].grid(True)
        axes[0].set_title(f'{info[0]}')

        try:
            print('* latest data loading ...')
            df = fdr.DataReader(info[0])
            X = df[self.Df[4]].values[-info[1]:]
        except:
            print('... fail')
            X = self.Df[3][info[0]][-info[1]:]

        norm = scaler.standard(X)
        yhat = regressor(norm)
        Yhat = yhat*X.std(ddof=1) + X.mean(axis=0)
        axes[0].plot(Yhat[-info[2]:], lw=0.5, label='longterm-trend')

        try:
            if info[3] == 0:
                X = df.Close.values[-info[2]:]
                X_High = df.High.values[-info[2]:]
                X_Low = df.Low.values[-info[2]:]
                X_Open = df.Open.values[-info[2]:]
            elif info[3] > 0:
                X = df.Close.values[-info[3]-info[2]:-info[3]]
                X_High = df.High.values[-info[3]-info[2]:-info[3]]
                X_Low = df.Low.values[-info[3]-info[2]:-info[3]]
                X_Open = df.Open.values[-info[3]-info[2]:-info[3]]
        except:
            if info[3] == 0:
                X = self.Df[3][info[0]][-info[2]:]
            elif info[3] > 0:
                X = self.Df[3][info[0]][-info[3]-info[2]:-info[3]]

        _norm = scaler.standard(X)
        _yhat = regressor(_norm)

        x = _norm - _yhat
        x = scaler.minmax(x)

        index = {}
        index['lower'] = np.where((x>=0) & (x<0.2))[0]
        index['upper'] = np.where((x<=1) & (x>0.8))[0]

        try:
            data = X_High - X_Low
            interval = stats.t.interval(alpha=0.99, df=len(data)-1, loc=np.mean(data), scale=stats.sem(data)) 
            itv = (interval[1] - interval[0])/2

            axes[0].fill_between(x=range(len(X_Open)), y1=X_High, y2=X_Low, alpha=0.7, color='lightgray')
            axes[0].fill_between(x=range(len(X)), y1=X+itv, y2=X-itv, alpha=0.3, color='green')
            axes[0].text(len(X)*0.8, X[-1]+itv, f'Upper-Bound:{int(X[-1]+itv)}')
            axes[0].text(len(X)*0.8, X[-1]-itv, f'Lower-Bound:{int(X[-1]-itv)}')
            axes[0].plot(X_Open, color='green', label='TS(Open)')
            axes[0].plot(X, color='green', lw=3, label='TS(Close)')
            axes[0].plot(index['lower'], X[index['lower']], lw=0, marker='_', label='Lower Bound')
            axes[0].plot(index['upper'], X[index['upper']], lw=0, marker='_', label='Upper Bound')
            axes[0].plot(_yhat*X.std(ddof=1) + X.mean(axis=0), c='orange', label='shortterm-trend')
        except:
            axes[0].plot(X, label='time-series')
            axes[0].plot(index['lower'], X[index['lower']], lw=0, marker='_', label='Lower Bound')
            axes[0].plot(index['upper'], X[index['upper']], lw=0, marker='_', label='Upper Bound')
            axes[0].plot(_yhat*X.std(ddof=1) + X.mean(axis=0), c='orange', label='shortterm-trend')

        # Correlation Analysis
        def taylor_series(x, coef):
            degree = len(coef) - 1
            value = 0
            for i in range(degree+1):
                value += coef[i]*x**(degree-i)
            return value

        xdata = np.linspace(-10,10,len(_yhat))
        ydata = smt.acf(_norm-_yhat, nlags=len(_yhat), fft=False)
        degree = 3
        coef = np.polyfit(xdata, ydata, degree) #; print(f'Coefficients: {coef}')

        x = ydata - taylor_series(xdata, coef)
        x = scaler.minmax(x)[::-1]

        index = {}
        index['min'] = np.where((x>=0) & (x<0.1))[0]
        index['down'] = np.where((x>=0.1) & (x<0.45))[0]
        index['mid'] = np.where((x>=0.45)&(x<0.55))[0]
        index['up'] = np.where((x<0.9) & (x>=0.55))[0]
        index['max'] = np.where((x<=1) & (x>=0.9))[0]
        if _yhat[-1] - _yhat[0] > 0:
            axes[0].plot(index['min'], X[index['min']], lw=0, c='red', markersize=10, marker='^', label='S.B.S.')
            axes[0].plot(index['down'], X[index['down']], lw=0, c='red', alpha=0.3, marker='^', label='W.B.S.')
            axes[0].plot(index['mid'], X[index['mid']], lw=0, c='green', marker='o', label='b.S.')
            axes[0].plot(index['up'], X[index['up']], lw=0, c='blue', alpha=0.3, marker='v', label='W.S.S.')
            axes[0].plot(index['max'], X[index['max']], lw=0, c='blue', markersize=10, marker='v', label='S.S.S.')
        else:
            axes[0].plot(index['min'], X[index['min']], lw=0, c='blue', markersize=10, marker='v', label='S.S.S.')
            axes[0].plot(index['down'], X[index['down']], lw=0, c='blue', alpha=0.3, marker='v', label='W.S.S')
            axes[0].plot(index['mid'], X[index['mid']], lw=0, c='green', marker='o', label='b.S.')
            axes[0].plot(index['up'], X[index['up']], lw=0, c='red', alpha=0.3, marker='^', label='W.B.S.')
            axes[0].plot(index['max'], X[index['max']], lw=0, c='red', markersize=10, marker='^', label='S.B.S.')

        axes[0].legend(loc='upper left')

        
        slopes1 = []
        slopes2 = []
        for shifting in range(0,len(self.Df[3][info[0]])):
            if shifting+info[2] > len(self.Df[3][info[0]])-1: break

            if shifting == 0 :
                x = np.arange(len(self.Df[3][info[0]][-info[2]:]))
                y = self.Df[3][info[0]][self.Df[4]][-info[2]:].values
            else:
                x = np.arange(len(self.Df[3][info[0]][-shifting-info[2]:-shifting]))
                y = self.Df[3][info[0]][self.Df[4]][-shifting-info[2]:-shifting].values
            bias = np.ones_like(x)
            X = np.c_[bias, x]

            b = linalg.inv(X.T@X) @ X.T @ y
            yhat = X@b
            slopes1.append((yhat[-1] - yhat[0])/(info[2]-1))
            slopes2.append((y[-1] - y[0])/(info[2]-1))
        
        self.dummies.IndexReport['slopes1'] = slopes1
        self.dummies.IndexReport['slopes2'] = slopes2

        axes[1].plot(self.Df[3][info[0]][self.Df[4]][-info[1]:].values)
        proper_value = np.mean(self.Df[3][info[0]][self.Df[4]][-info[1]:].values)
        axes[1].axhline(proper_value, ls=':', c='black')
        axes[1].text(info[1]-info[2], proper_value, f'{proper_value}')
        axes[1].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[1].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[1].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*2-1, ls=':', c='red')
        if back_shifting == 0 : sp = self.Df[3][info[0]][self.Df[4]][-info[2]:].mean()
        else : sp = self.Df[3][info[0]][self.Df[4]][-info[3]-info[2]:-info[3]].mean()
        axes[1].plot([len(self.Df[3][info[0]][self.Df[4]][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1], [sp,sp], c='black')
        axes[1].text(len(self.Df[3][info[0]][self.Df[4]][-info[1]:])-info[3]-info[2]*1-1, sp, f'S.P.:{info[2]}')

        slopes = np.array(slopes1[::-1][-info[1]:])
        zero_arr = np.zeros_like(slopes)
        slope_index = {}
        slope_index['up'] = np.where(slopes>0)[0]
        slope_index['down'] = np.where(slopes<0)[0]
        axes[2].plot(slopes)
        axes[2].scatter(slope_index['up'], zero_arr[slope_index['up']], marker='s', alpha=0.5, c='red')
        axes[2].scatter(slope_index['down'], zero_arr[slope_index['down']], marker='s', alpha=0.5, c='blue')
        axes[2].axhline(0, ls=':', c='black')
        axes[2].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[2].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[2].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, ls=':', c='red')
        axes[2].plot([len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1], [0,0], c='black')
        axes[2].text(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, 0, f'S.P.:{info[2]}')
        
        slopes = np.array(slopes2[::-1][-info[1]:])
        zero_arr = np.zeros_like(slopes)
        slope_index = {}
        slope_index['up'] = np.where(slopes>0)[0]
        slope_index['down'] = np.where(slopes<0)[0]
        axes[3].plot(slopes)
        axes[3].scatter(slope_index['up'], zero_arr[slope_index['up']], marker='s', alpha=0.5, c='red')
        axes[3].scatter(slope_index['down'], zero_arr[slope_index['down']], marker='s', alpha=0.5, c='blue')
        axes[3].axhline(0, ls=':', c='black')
        axes[3].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[3].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[3].axvline(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, ls=':', c='red')
        axes[3].plot([len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*0-1], [0,0], c='black')
        axes[3].text(len(self.Df[3][info[0]][-info[1]:])-info[3]-info[2]*1-1, 0, f'S.P.:{info[2]}')

        plt.tight_layout()
        if download:
            plt.savefig(f'{info[0]}.pdf')
        #plt.show()


    def StockReport(self, i=None, long_period=200, short_period=30, back_shifting=0, return_Xy=False, download=False):
        self.dummies.StockReport = dict()

        with plt.style.context('seaborn-whitegrid'):
            # Korean Font Set
            _, axes = plt.subplots(4,1,figsize=(25,15))

        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting) # args params
        selected_stock_info = self.Df[1].iloc[info[0]]; print(f'* {selected_stock_info.Name}({selected_stock_info.Symbol})')
        symbol = selected_stock_info.Symbol


        ##########################################################################
        

        axes[0].grid(True)
        axes[1].grid(True)
        axes[2].grid(True)
        axes[3].grid(True)

        axes[0].set_title(f'{selected_stock_info.Name}({selected_stock_info.Symbol})')

        try:
            print('* latest data loading ...')
            df = fdr.DataReader(symbol)
            X = df[self.Df[4]].values[-info[1]:]
        except:
            print('... fail')
            X = self.Df[0][:, info[0]][-info[1]:]
        norm = scaler.standard(X)
        yhat = regressor(norm)
        Yhat = yhat*X.std(ddof=1) + X.mean(axis=0)
        axes[0].plot(Yhat[-info[2]:], lw=0.5, label='longterm-trend')

        try:
            if info[3] == 0:
                X = df.Close.values[-info[2]:]
                X_High = df.High.values[-info[2]:]
                X_Low = df.Low.values[-info[2]:]
                X_Open = df.Open.values[-info[2]:]
            elif info[3] > 0:
                X = df.Close.values[-info[3]-info[2]:-info[3]]
                X_High = df.High.values[-info[3]-info[2]:-info[3]]
                X_Low = df.Low.values[-info[3]-info[2]:-info[3]]
                X_Open = df.Open.values[-info[3]-info[2]:-info[3]]
        except:
            if info[3] == 0:
                X = self.Df[0][:, info[0]][-info[2]:]
            elif info[3] > 0:
                X = self.Df[0][:, info[0]][-info[3]-info[2]:-info[3]]

        _norm = scaler.standard(X)
        _yhat = regressor(_norm)

        x = _norm - _yhat
        x = scaler.minmax(x)

        index = {}
        index['lower'] = np.where((x>=0) & (x<0.2))[0]
        index['upper'] = np.where((x<=1) & (x>0.8))[0]

        try:
            data = X_High - X_Low
            interval = stats.t.interval(alpha=0.99, df=len(data)-1, loc=np.mean(data), scale=stats.sem(data)) 
            itv = (interval[1] - interval[0])/2

            axes[0].fill_between(x=range(len(X_Open)), y1=X_High, y2=X_Low, alpha=0.7, color='lightgray')
            axes[0].fill_between(x=range(len(X)), y1=X+itv, y2=X-itv, alpha=0.3, color='green')
            axes[0].text((info[2]-1)*0.8, X[-1]+itv, f'Upper-Bound:{int(X[-1]+itv)}')
            axes[0].text((info[2]-1)*0.8, X[-1]-itv, f'Lower-Bound:{int(X[-1]-itv)}')
            axes[0].plot(X_Open, color='green', label='TS(Open)')
            axes[0].plot(X, color='green', lw=3, label='TS(Close)')
            axes[0].plot(index['lower'], X[index['lower']], lw=0, marker='_', label='Lower Bound')
            axes[0].plot(index['upper'], X[index['upper']], lw=0, marker='_', label='Upper Bound')
            axes[0].plot(_yhat*X.std(ddof=1) + X.mean(axis=0), c='orange', label='shortterm-trend')
        except:
            axes[0].plot(X, label='time-series')
            axes[0].plot(index['lower'], X[index['lower']], lw=0, marker='_', label='Lower Bound')
            axes[0].plot(index['upper'], X[index['upper']], lw=0, marker='_', label='Upper Bound')
            axes[0].plot(_yhat*X.std(ddof=1) + X.mean(axis=0), c='orange', label='shortterm-trend')

        # Correlation Analysis
        def taylor_series(x, coef):
            degree = len(coef) - 1
            value = 0
            for i in range(degree+1):
                value += coef[i]*x**(degree-i)
            return value

        xdata = np.linspace(-10,10,len(_yhat))
        ydata = smt.acf(_norm-_yhat, nlags=len(_yhat), fft=False)
        degree = 3
        coef = np.polyfit(xdata, ydata, degree) #; print(f'Coefficients: {coef}')

        x = ydata - taylor_series(xdata, coef)
        x = scaler.minmax(x)[::-1]

        index = {}
        index['min'] = np.where((x>=0) & (x<0.1))[0]
        index['down'] = np.where((x>=0.1) & (x<0.45))[0]
        index['mid'] = np.where((x>=0.45)&(x<0.55))[0]
        index['up'] = np.where((x<0.9) & (x>=0.55))[0]
        index['max'] = np.where((x<=1) & (x>=0.9))[0]
        if _yhat[-1] - _yhat[0] > 0:
            axes[0].plot(index['min'], X[index['min']], lw=0, c='red', markersize=10, marker='^', label='S.B.S.')
            axes[0].plot(index['down'], X[index['down']], lw=0, c='red', alpha=0.3, marker='^', label='W.B.S.')
            axes[0].plot(index['mid'], X[index['mid']], lw=0, c='green', marker='o', label='b.S.')
            axes[0].plot(index['up'], X[index['up']], lw=0, c='blue', alpha=0.3, marker='v', label='W.S.S.')
            axes[0].plot(index['max'], X[index['max']], lw=0, c='blue', markersize=10, marker='v', label='S.S.S.')
        else:
            axes[0].plot(index['min'], X[index['min']], lw=0, c='blue', markersize=10, marker='v', label='S.S.S.')
            axes[0].plot(index['down'], X[index['down']], lw=0, c='blue', alpha=0.3, marker='v', label='W.S.S')
            axes[0].plot(index['mid'], X[index['mid']], lw=0, c='green', marker='o', label='b.S.')
            axes[0].plot(index['up'], X[index['up']], lw=0, c='red', alpha=0.3, marker='^', label='W.B.S.')
            axes[0].plot(index['max'], X[index['max']], lw=0, c='red', markersize=10, marker='^', label='S.B.S.')

        axes[0].legend(loc='upper left')

        
        slopes1 = []
        slopes2 = []
        for shifting in range(0,len(self.Df[0])):
            if shifting+info[2] > len(self.Df[0])-1: break

            if shifting == 0 :
                x = np.arange(len(self.Df[0][:,info[0]][-info[2]:]))
                y = self.Df[0][:,info[0]][-info[2]:]
            else:
                x = np.arange(len(self.Df[0][:,info[0]][-shifting-info[2]:-shifting]))
                y = self.Df[0][:,info[0]][-shifting-info[2]:-shifting]
            bias = np.ones_like(x)
            X = np.c_[bias, x]

            b = linalg.inv(X.T@X) @ X.T @ y
            yhat = X@b
            slopes1.append((yhat[-1] - yhat[0])/(info[2]-1))
            slopes2.append((y[-1] - y[0])/(info[2]-1))
        
        self.dummies.StockReport['slopes1'] = slopes1
        self.dummies.StockReport['slopes2'] = slopes2

        axes[1].plot(self.Df[0][-info[1]:,info[0]])
        proper_value = np.mean(self.Df[0][-info[1]:,info[0]])
        axes[1].axhline(proper_value, ls=':', c='black')
        axes[1].text(info[1]-info[2], proper_value, f'{proper_value}')
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*2-1, ls=':', c='red')
        if back_shifting == 0 : sp = self.Df[0][:,info[0]][-info[2]:].mean()
        else : sp = self.Df[0][:,info[0]][-info[3]-info[2]:-info[3]].mean()
        axes[1].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1], [sp,sp], c='black')
        axes[1].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, sp, f'S.P.:{info[2]}')

        slopes = np.array(slopes1[::-1][-info[1]:])
        zero_arr = np.zeros_like(slopes)
        slope_index = {}
        slope_index['up'] = np.where(slopes>0)[0]
        slope_index['down'] = np.where(slopes<0)[0]
        axes[2].plot(slopes)
        axes[2].scatter(slope_index['up'], zero_arr[slope_index['up']], marker='s', c='red')
        axes[2].scatter(slope_index['down'], zero_arr[slope_index['down']], marker='s', c='blue')
        axes[2].axhline(0, ls=':', c='black')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, ls=':', c='red')
        axes[2].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1], [0,0], c='black')
        axes[2].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, 0, f'S.P.:{info[2]}')

        slopes = np.array(slopes2[::-1][-info[1]:])
        zero_arr = np.zeros_like(slopes)
        slope_index = {}
        slope_index['up'] = np.where(slopes>0)[0]
        slope_index['down'] = np.where(slopes<0)[0]
        axes[3].plot(slopes)
        axes[3].scatter(slope_index['up'], zero_arr[slope_index['up']], marker='s', c='red')
        axes[3].scatter(slope_index['down'], zero_arr[slope_index['down']], marker='s', c='blue')
        axes[3].axhline(0, ls=':', c='black')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1)-1, c='red')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1, ls=':', c='red')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, ls=':', c='red')
        axes[3].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0-1], [0,0], c='black')
        axes[3].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1-1, 0, f'S.P.:{info[2]}')


        plt.tight_layout()
        if download:
            plt.savefig(f'{selected_stock_info.Name}({selected_stock_info.Symbol}).pdf')
        #plt.show()
        print(selected_stock_info)
        
        if torch.cuda.is_available() : device = torch.device('cuda')
        else : device = torch.device('cpu')
        _ont = 2*(x - 0.5)
        xset = np.c_[_norm, _ont]
        xset = torch.from_numpy(xset).type(torch.FloatTensor).unsqueeze(0).to(device)

        prob = None
        print('Probability :', prob)

        if return_Xy:
            return xset, prob


    def StockForecast(self, i=None, long_period=200, short_period=30, back_shifting=0, download=False):
        self.dummies.StockForecast = dict()

        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]
        print(f'* {selected_stock_info.Name}({selected_stock_info.Symbol})')

        smoothing = {}
        smoothing['M,M,M'] = ['mul', 'mul', 'mul', False]
        smoothing['M,M,A'] = ['mul', 'mul', 'add', False]
        smoothing['M,M,N'] = ['mul', 'mul', None, False]
        smoothing['M,A,M'] = ['mul', 'add', 'mul', False]
        smoothing['M,A,A'] = ['mul', 'add', 'add', False]
        smoothing['M,A,A'] = ['mul', 'add', None, False]
        smoothing['M,N,M'] = ['mul', None, 'mul', False]
        smoothing['M,N,A'] = ['mul', None, 'add', False]
        smoothing['M,N,A'] = ['mul', None, None, False]
        smoothing['M,Ad,M'] = ['mul', 'add', 'mul', True]
        smoothing['M,Ad,A'] = ['mul', 'add', 'add', True]
        smoothing['M,Ad,A'] = ['mul', 'add', None, True]

        smoothing['A,M,M'] = ['add', 'mul', 'mul', False]
        smoothing['A,M,A'] = ['add', 'mul', 'add', False]
        smoothing['A,M,N'] = ['add', 'mul', None, False]
        smoothing['A,A,M'] = ['add', 'add', 'mul', False]
        smoothing['A,A,A'] = ['add', 'add', 'add', False]
        smoothing['A,A,A'] = ['add', 'add', None, False]
        smoothing['A,N,M'] = ['add', None, 'mul', False]
        smoothing['A,N,A'] = ['add', None, 'add', False]
        smoothing['A,N,A'] = ['add', None, None, False]
        smoothing['A,Ad,M'] = ['add', 'add', 'mul', True]
        smoothing['A,Ad,A'] = ['add', 'add', 'add', True]
        smoothing['A,Ad,A'] = ['add', 'add', None, True]


        with plt.style.context('seaborn-whitegrid'):
            layout = (8, 2)
            axes = {}
            fig = plt.figure(figsize=(25,25))
            axes['0,0'] = plt.subplot2grid(layout, (0, 0), colspan=2)
            axes['1,0'] = plt.subplot2grid(layout, (1, 0), colspan=2)
            axes['2,0'] = plt.subplot2grid(layout, (2, 0), colspan=2)
            axes['3,0'] = plt.subplot2grid(layout, (3, 0), colspan=2)
            axes['4,0'] = plt.subplot2grid(layout, (4, 0), colspan=2)
            axes['5,0'] = plt.subplot2grid(layout, (5, 0), colspan=2)
            axes['6,0'] = plt.subplot2grid(layout, (6, 0), colspan=2)
            axes['7,0'] = plt.subplot2grid(layout, (7, 0), colspan=2)

            axes['0,0'].set_title('ETS(M,Ad,_) : Multiplicative(dampling)')
            axes['1,0'].set_title('ETS(M,M,_) : Multiplicative(non-dampling)')
            axes['2,0'].set_title('ETS(M,A,_) : Multiplicative(non-dampling)')
            axes['3,0'].set_title('ETS(M,N,_) : Multiplicative(non-dampling)')
            axes['4,0'].set_title('ETS(A,Ad,_) : Additive(damping)')
            axes['5,0'].set_title('ETS(A,M,_) : Additive(non-dampling)')
            axes['6,0'].set_title('ETS(A,A,_) : Additive(non-dampling)')
            axes['7,0'].set_title('ETS(A,N,_) : Additive(non-dampling)')

            if back_shifting == 0:
                target = pd.Series(self.Df[0][-info[1]:, info[0]].astype(np.float64))
            else:
                target = pd.Series(self.Df[0][-info[3]-info[1]:-info[3], info[0]].astype(np.float64))

            for i in range(8):
                target.plot(marker='o', color='black', label=f'{selected_stock_info.Name}', ax=axes[f'{i},0'])
                axes[f'{i},0'].axvline(info[1], ls=':', color='red')
                axes[f'{i},0'].axvline(info[1]+info[2], ls='-', color='red')
                axes[f'{i},0'].plot([info[1],info[1]+info[2]], [target.mean()]*2, ls='-', color='black')
                axes[f'{i},0'].text((info[1]+info[1]+info[2])/2, target.mean(), f'S.P.:{info[2]}')
                if back_shifting != 0 :
                    if info[3] <= info[2]:
                        axes[f'{i},0'].plot(range(info[1], info[1]+info[3]), self.Df[0][-info[3]:, info[0]], marker='o', color='black', label=f'{selected_stock_info.Name}')
                    else:
                        axes[f'{i},0'].plot(range(info[1], info[1]+info[2]), self.Df[0][-info[3]:-info[3]+info[2], info[0]], marker='o', color='black', label=f'{selected_stock_info.Name}')

            for key, model_info in smoothing.items():
                model = smt.ETSModel(target, seasonal_periods=info[2], error=model_info[0], trend=model_info[1], seasonal=model_info[2], damped_trend=model_info[3]).fit(use_boxcox=True)
                forecast = model.forecast(info[2])
                try:
                    forecast_bound = model.get_prediction(start=0, end=info[1]+info[2]-1).summary_frame(alpha=0.05)[['pi_lower', 'pi_upper']][-info[2]:]
                except:
                    forecast_bound = None

                if key.split(',')[0] == 'M':
                    if key.split(',')[1] == 'Ad':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})', ax=axes['0,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['0,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['0,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'M':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['1,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['1,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['1,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'A':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['2,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['2,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['2,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'N':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['3,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['3,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['3,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                elif key.split(',')[0] == 'A':
                    if key.split(',')[1] == 'Ad':
                        model.fittedvalues.plot(style='--',  color='blue', label=r'$ETS$'+f'({key})',ax=axes['4,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['4,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['4,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'M':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['5,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['5,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['5,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'A':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['6,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['6,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['6,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)
                    elif key.split(',')[1] == 'N':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['7,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['7,0'])
                        if isinstance(forecast_bound, (pd.core.frame.DataFrame, )):
                            axes['7,0'].fill_between(forecast_bound.index, forecast_bound.iloc[:,0], forecast_bound.iloc[:,1], color='k', alpha=0.15)

            for i in range(8):
                axes[f'{i},0'].legend(loc='upper left')

            plt.tight_layout()
            if download:
                plt.savefig(f'{selected_stock_info.Name}({selected_stock_info.Symbol}).pdf')
            #plt.show()


    @staticmethod
    def _stationary(time_series):
        """
        Augmented Dickey-Fuller test

        Null Hypothesis (H0): [if p-value > 0.5, non-stationary]
        >   Fail to reject, it suggests the time series has a unit root, meaning it is non-stationary.
        >   It has some time dependent structure.
        Alternate Hypothesis (H1): [if p-value =< 0.5, stationary]
        >   The null hypothesis is rejected; it suggests the time series does not have a unit root, meaning it is stationary.
        >   It does not have time-dependent structure.
        """
        result = adfuller(time_series)

        print(f'[Augmented Dickey-Fuller test : p-value] : {result[1]}')
        if result[1] < 0.05:
            print(" : The residual of time series is 'stationary' process")
            return True
        else:
            print(" : The residual of time series is 'non-stationary' process")
            return False


    def _stock_decompose(self, i, long_period, short_period, back_shifting, decompose_type, resid_transform):
        info = (i, long_period, short_period, back_shifting)

        if decompose_type == 'classic':
            if back_shifting == 0:
                result = seasonal_decompose(self.Df[0][-info[1]:, info[0]], period=info[2], two_sided=False)
            else:
                result = seasonal_decompose(self.Df[0][-info[3]-info[1]:-info[3], info[0]], period=info[2], two_sided=False)
        elif decompose_type == 'stl':
            if back_shifting == 0:
                result = STL(self.Df[0][-info[1]:, info[0]], period=info[2]).fit()
            else:
                result = STL(self.Df[0][-info[3]-info[1]:-info[3], info[0]], period=info[2]).fit()

        if resid_transform:
            resid = result.resid[np.logical_not(np.isnan(result.resid))]
            si = np.argsort(resid)[::-1]
            sii = np.argsort(np.argsort(resid)[::-1])
            new_resid = np.diff(resid[si])[np.delete(sii, np.argmax(sii))]
            new_resid = np.insert(new_resid, np.argmax(sii), 0)

            origin_resid = deepcopy(result.resid)
            result.resid[np.argwhere(np.logical_not(np.isnan(result.resid))).squeeze()] = new_resid
            result.seasonal[:] = result.seasonal + (origin_resid - result.resid)

        return result


    def StockDecompose(self, i=None, long_period=200, short_period=30, back_shifting=0,
                                decompose_type='stl', resid_transform=False, scb=(0.1,0.9), optimize=False, download=False):
        self.dummies.StockDecompose = dict()

        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]

        result = self._stock_decompose(info[0], info[1], info[2], info[3], decompose_type=decompose_type, resid_transform=resid_transform)
        dropna_resid = result.resid[np.argwhere(np.logical_not(np.isnan(result.resid))).squeeze()]

        self.dummies.StockDecompose['observed'] = result.observed
        self.dummies.StockDecompose['trend'] = result.trend
        self.dummies.StockDecompose['seasonal'] = result.seasonal
        self.dummies.StockDecompose['resid'] = result.resid

        print(f'* {selected_stock_info.Name}({selected_stock_info.Symbol})')
        with plt.style.context('ggplot'):
            layout = (7, 2)
            axes = {}
            fig = plt.figure(figsize=(25,20))
            axes['0,0'] = plt.subplot2grid(layout, (0, 0), colspan=2)
            axes['1,0'] = plt.subplot2grid(layout, (1, 0), colspan=2)
            axes['2,0'] = plt.subplot2grid(layout, (2, 0), colspan=2)
            axes['3,0'] = plt.subplot2grid(layout, (3, 0), colspan=2)
            axes['4,0'] = plt.subplot2grid(layout, (4, 0), colspan=2)
            axes['5,0'] = plt.subplot2grid(layout, (5, 0), colspan=1)
            axes['5,1'] = plt.subplot2grid(layout, (5, 1), colspan=1)
            axes['6,0'] = plt.subplot2grid(layout, (6, 0), colspan=1)
            axes['6,1'] = plt.subplot2grid(layout, (6, 1), colspan=1)

            axes['0,0'].set_title(f'{selected_stock_info.Name}({selected_stock_info.Symbol}) : Observed')
            axes['1,0'].set_title('Differencing')
            axes['2,0'].set_title('Trend')
            axes['3,0'].set_title('Seasonal')
            axes['4,0'].set_title('Resid')
            axes['6,0'].set_title('Normal Q-Q')
            axes['6,1'].set_title('Probability Plot')

            # Decompose
            axes['0,0'].plot(result.observed)
            axes['1,0'].plot(np.diff(result.observed))
            axes['2,0'].plot(result.trend)
            axes['3,0'].plot(result.seasonal)
            axes['4,0'].plot(result.resid)
            axes['0,0'].axvline(info[1]-info[2]-1, c='red', ls=':')
            axes['2,0'].axvline(info[1]-info[2]-1, c='red', ls=':')
            axes['3,0'].axvline(info[1]-info[2]-1, c='red', ls=':')
            axes['4,0'].axvline(info[1]-info[2]-1, c='red', ls=':')
            axes['0,0'].axvline(info[1]-1, c='red')
            axes['2,0'].axvline(info[1]-1, c='red')
            axes['3,0'].axvline(info[1]-1, c='red')
            axes['4,0'].axvline(info[1]-1, c='red')
            axes['3,0'].axhline(0, c='black', ls=':')
            axes['4,0'].axhline(0, c='black', ls=':')

            # Seasonality (1)
            _O = result.observed[-info[2]:]
            _S = result.seasonal[-info[2]:]
            idx = np.argmax(_S)
            axes['3,0'].plot(info[1]-info[2]+idx, _S[idx], lw=0, c='red', marker='*', markersize=10)
            axes['3,0'].text(info[1]-info[2]+idx, _S[idx], f'{int(_O[idx])}')
            axes['3,0'].plot(info[1]-1, _S[-1], lw=0, c='blue', marker='*', markersize=10)
            axes['3,0'].text(info[1]-1, _S[-1], f'{int(_O[-1])}')
            axes['3,0'].arrow(x=info[1]-info[2]+idx, y=_S[idx], dx=info[2]-idx-1, dy=_S[-1]-_S[idx], width=0.03, color='green') 
            axes['3,0'].text((2*info[1]-info[2]+idx-1)/2, (_S[idx]+_S[-1])/2, f'{int(_O[idx]-_O[-1])}')

            # Seasonality (2)
            x = scaler.minmax(result.seasonal)
            index = {}
            index['min'] = np.where((x<scb[0]) & (x>=0))[0]
            index['max'] = np.where((x<=1) & (x>scb[1]))[0]
            axes['3,0'].plot(index['min'], result.seasonal[index['min']], lw=0, marker='^')
            axes['3,0'].plot(index['max'], result.seasonal[index['max']], lw=0, marker='v')

            # Seasonality (3)
            zero_arr = np.zeros_like(result.seasonal)
            diff = np.diff(result.seasonal)
            index['up'] = np.where(diff>0)[0]
            index['down'] = np.where(diff<0)[0]
            axes['3,0'].scatter(index['up'], zero_arr[index['up']], marker='s', c='red')
            axes['3,0'].scatter(index['down'], zero_arr[index['down']], marker='s', c='blue')

            # ACF/PACF
            smt.graphics.plot_acf(dropna_resid, lags=info[2], ax=axes['5,0'], alpha=0.5)
            smt.graphics.plot_pacf(dropna_resid, lags=info[2], ax=axes['5,1'], alpha=0.5)
            # Residual Analysis
            sm.qqplot(dropna_resid, line='s', ax=axes['6,0'])
            stats.probplot(dropna_resid, sparams=(dropna_resid.mean(), dropna_resid.std()), plot=axes['6,1'])
            plt.tight_layout()
            if download:
                plt.savefig(f'{selected_stock_info.Name}({selected_stock_info.Symbol}).pdf')
            #plt.show()
            

        self._stationary(dropna_resid)

        def calculate_profit(_result=result, _short_period=info[2], printer=False):
            _T = _result.trend[-_short_period:]
            _S = _result.seasonal[-_short_period:]
            _dropna_resid = _result.resid[np.argwhere(np.logical_not(np.isnan(_result.resid))).squeeze()]
            _R = _dropna_resid[-_short_period:]

            # Profit per day : Estimation
            yhat = regressor(_T)
            trend_profit = (yhat[-1] - yhat[0])/(len(yhat)-1)
            idx = np.argmax(_S)
            max_seasonal_profit = _S[idx] - _S[-1]
            seasonal_profit = -max_seasonal_profit/(_short_period-1-idx)
            if resid_transform:
                resid_profit = min(_dropna_resid)
            else:
                resid_profit = min(_R)
            total_profit = trend_profit + seasonal_profit + resid_profit

            # Profit per day : True
            _trend_profit = _T[-1] - _T[-2]
            _seasonal_profit = _S[-1] - _S[-2]
            _resid_profit = _R[-1] - _R[-2]
            
            _total_profit = _trend_profit + _seasonal_profit + _resid_profit
            optimal_error = np.sqrt((total_profit - _total_profit)**2)

            if printer:
                period = info[2] - (1 + idx) 
                objective_profit = -1*(_result.observed[-1] - _result.observed[-_short_period+idx])

                print(f'\n[Objective Profit, Period, Deviation] : [{objective_profit}]/[{period}]/[{optimal_error}]')
                print(f'* Total Profit(per day) : E[{total_profit}]/T[{_total_profit}]')
                print(f'* Trend Profit(per day) : E[{trend_profit}]/T[{_trend_profit}]')
                print(f'* Seasonal Profit(per day) : E[{seasonal_profit}]/T[{_seasonal_profit}]')
                print(f'* Resid Profit(per day) : E[{resid_profit}]/T[{_resid_profit}]')
                estimate_profit = {}
                estimate_profit['total'] = total_profit
                estimate_profit['trend'] = trend_profit
                estimate_profit['seasonal'] = seasonal_profit
                estimate_profit['resid'] = resid_profit
                return estimate_profit
            
            return optimal_error
        
        if optimize:
            assert resid_transform == True, 'The resid_transform arg must be True'
            optimal_errors = {}
            # step <= short_period
            for step in range(2, info[2]+1):
                _optimal_errors = [np.inf,np.inf]
                _result = self._stock_decompose(info[0], info[1], step, info[3], decompose_type=decompose_type, resid_transform=resid_transform)
                for _sp in range(2, step+1):
                    _optimal_errors.append(calculate_profit(_result, _short_period=_sp, printer=False))
                _optimal_short_period = np.argmin(np.array(_optimal_errors))
                _optimal_error = _optimal_errors[_optimal_short_period]
                optimal_errors[step] = (_optimal_short_period, _optimal_error)
            
            steps = []
            optimal_short_period_set = []
            optimal_error_set = []
            best_optimality_set = {}
            print()
            for step, (_optimal_short_period, _optimal_error) in optimal_errors.items():
                print(f'- short_period/optimal_short_period/optimal_error : {step}/{_optimal_short_period}/{_optimal_error}')
                steps.append(step)
                optimal_short_period_set.append(_optimal_short_period)
                optimal_error_set.append(_optimal_error)
                if step == _optimal_short_period:
                    best_optimality_set[step] = _optimal_error

            idx = np.argmin(optimal_error_set)
            step = steps[idx]
            mle_optimal_short_period = optimal_short_period_set[idx]
            mle_optimal_error = optimal_error_set[idx]
            print(f'>>> recommendation with MLE >> short_period/optimal_short_period/error : {step}/{mle_optimal_short_period}/{mle_optimal_error}')

            idx = np.argmin(list(best_optimality_set.values()))
            best_optimal_short_period = list(best_optimality_set.keys())[idx]
            best_optimal_error = list(best_optimality_set.values())[idx]
            print(f'>>> best optimal short period/error : {best_optimal_short_period}/{best_optimal_error} > select it as an argument for the short_period')

        calculate_profit(result, info[2], printer=True)
        

    def _stock_estimate(self, i, long_period, short_period, back_shifting):
        info = (i, long_period, short_period, back_shifting)

        selected_stock_info = self.Df[1].iloc[info[0]]
        df = fdr.DataReader(selected_stock_info.Symbol)

        df1 = df[-info[1]:]
        idx_willup = df1.Close.diff().shift(-1) > 0
        idx_willdown = df1.Close.diff().shift(-1) < 0
        idx_doneup = df1.Change > 0
        idx_donedown = df1.Change < 0
        df1_willup = df1[idx_willup.values]
        df1_willdown = df1[idx_willdown.values]
        df1_doneup = df1[idx_doneup.values]
        df1_donedown = df1[idx_donedown.values]
        if len(df1_willup) == len(df1_doneup):
            df_up = np.c_[df1_willup.Close.values, df1_doneup.Open.values, df1_doneup.High.values, df1_doneup.Low.values]
            df_up = df_up.astype(np.float64)
        else:
            df_up = np.c_[df1_willup.Close.values, df1_doneup.Open.values[:-1], df1_doneup.High.values[:-1], df1_doneup.Low.values[:-1]]
            df_up = df_up.astype(np.float64)

        if len(df1_willdown) == len(df1_donedown):
            df_down = np.c_[df1_willdown.Close.values, df1_donedown.Open.values]
            df_down = df_down.astype(np.float64)
        else:
            df_down = np.c_[df1_willdown.Close.values, df1_donedown.Open.values[:-1]]
            df_down = df_down.astype(np.float64)

        #down_OC_diff = df_down[:,1] - df_down[:,0]
        up_OC_diff = df_up[:,1] - df_up[:,0]
        up_LC_diff = df_up[:,3] - df_up[:,0]
        up_HC_diff = df_up[:,2] - df_up[:,0]
        up_LO_diff = df_up[:,3] - df_up[:,1]
        up_HO_diff = df_up[:,2] - df_up[:,1]

        hypothesis_test_dataset = {}
        hypothesis_test_dataset['Up Case: Previous Close Price > Today Open Price'] = up_OC_diff 
        hypothesis_test_dataset['Up Case[Buy Point]  : Previous Close Price > Today Low Price'] = up_LC_diff
        hypothesis_test_dataset['Up Case[Sell Point] : Previous Close Price > Today High Price'] = up_HC_diff
        hypothesis_test_dataset['Up Case[Buy Point]  : Today Open Price > Today Low Price'] = up_LO_diff
        hypothesis_test_dataset['Up Case[Sell Point] : Today Open Price > Today High Price'] = up_HO_diff
        
        #down_OC_ratio = df_down[:,1] / df_down[:,0]
        up_OC_ratio = df_up[:,1] / df_up[:,0]
        up_LC_ratio = df_up[:,3] / df_up[:,0]
        up_HC_ratio = df_up[:,2] / df_up[:,0]
        up_LO_ratio = df_up[:,3] / df_up[:,1]
        up_HO_ratio = df_up[:,2] / df_up[:,1]
        
        PP1 = (df_up[:,0] * up_LC_ratio).mean() # Based-close purchase
        SP1 = (df_up[:,0] * up_HC_ratio).mean() # Based-close selling
        PP2 = (df_up[:,1] * up_LO_ratio).mean() # Based-open purchase
        SP2 = (df_up[:,1] * up_HO_ratio).mean() # Based-open selling

        PP1_error = np.sum((df_up[:,0] - SP1)**2)/(info[1]-2)
        SP1_error = np.sum((df_up[:,0] - PP1)**2)/(info[1]-2)
        PP2_error = np.sum((df_up[:,1] - SP2)**2)/(info[1]-2)
        SP2_error = np.sum((df_up[:,1] - PP2)**2)/(info[1]-2)
        
        if PP1_error > PP2_error:
            print(f'When purchasing stock, consider a method with based-open. (based-close error:{round(PP1_error,4)})/(based-open error:{round(PP2_error,4)})')
        else:
            print(f'When purchasing stock, consider a method with based-close. (based-close error:{round(PP1_error,4)})/(based-open error:{round(PP2_error,4)})')
        
        if SP1_error > SP2_error:
            print(f'When selling stock, consider a method with based-open. (based-close error:{round(SP1_error,4)})/(based-open error:{round(SP2_error,4)})')
        else:
            print(f'When selling stock, consider a method with based-close. (based-close error:{round(SP1_error,4)})/(based-open error:{round(SP2_error,4)})')

        return hypothesis_test_dataset



    def StockEstimate(self, i=None, long_period=200, short_period=20, back_shifting=0, decompose_type='stl', resid_transform=False, scb=(0.1,0.9)):
        self.dummies.StockInvest = dict()

        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]
        dataset = self._stock_estimate(info[0], info[1], info[2], info[3])
        
        df = fdr.DataReader(selected_stock_info.Symbol)
        previous_close_price = df.Close[-1]
        print(f'* {selected_stock_info.Name}({selected_stock_info.Symbol}) : {previous_close_price} <Close Price>')
        print(f'  During {info[1]} days,')
        confs = [0.70, 0.90, 0.95, 0.99]
        for name, data in dataset.items():
            print(f'* {name}')
            long_period_mean = data.mean()
            long_period_std = data.std(ddof=1)
            short_period_mean = data[-info[2]:].mean()
            short_period_std = data[-info[2]:].std(ddof=1)
            for conf in confs:
                t_stat = abs(stats.t.ppf((1 - conf)*0.5, info[1]-1))
                z_stat = abs(stats.norm.ppf((1 - conf)*0.5, 0, 1))
                z_left_side = long_period_mean - z_stat*long_period_std/np.sqrt(info[1])
                z_right_side = long_period_mean + z_stat*long_period_std/np.sqrt(info[1])
                t_left_side = short_period_mean - t_stat*short_period_std/np.sqrt(info[2])
                t_right_side = short_period_mean + t_stat*short_period_std/np.sqrt(info[2])
                left_side = 0.8*t_left_side + 0.2*z_left_side
                right_side = 0.8*t_right_side + 0.2*z_right_side
                print(f'  - Shifting Interval Est.({conf*100}%) : {round(left_side,4)} < {round(short_period_mean,4)} < {round(right_side,4)}') 



    def TSA(self, i=None, long_period=200, short_period=5, back_shifting=3, sarimax_params=((2,0,2),(0,0,0,12))):
        if not i:
            i = self.index[0]
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]

        _, axes = plt.subplots(5,1, figsize=(25,12))
        if back_shifting == 0 :
            x = self.Df[0][:, info[0]][-info[2]:]
        else:
            x = self.Df[0][:, info[0]][-info[3]-info[2]:-info[3]]
        x_ = np.sort(x)
        index1 = np.where(x == x_)[0]
        index2 = np.where(x == x_[::-1])[0]

        axes[0].plot(x_, c='red', marker='o')
        axes[0].plot(x_[::-1], c='blue', marker='o')
        axes[0].plot(x, lw=5, c='black', marker='o')
        axes[0].plot(index1, x[index1], color='red', lw=0, marker='^')
        axes[0].plot(index2, x[index2], color='blue', lw=0, marker='v')
        axes[0].axhline((x_[0]+x_[-1])/2, ls=':')
        axes[0].axvline(info[2]-1, ls=':', c='black')
        axes[0].grid(True)
        axes[0].set_title(f'{selected_stock_info.Name}({selected_stock_info.Symbol})')

        if -info[3]+info[2] >= 0:
            y = self.Df[0][:, info[0]][-info[3]-info[2]:]
        else:
            y = self.Df[0][:, info[0]][-info[3]-info[2]:-info[3]+info[2]]
        axes[1].plot(x, lw=5, c='black', marker='o')
        axes[1].plot(y, marker='o')
        axes[1].axvline(info[2]-1, ls=':', c='black')
        axes[1].grid(True)


        p, d, q = sarimax_params[0]
        P, D, Q, S = sarimax_params[1]
        time_series = np.diff(self.Df[0][:, info[0]])
        time_series = pd.Series(time_series)
        if back_shifting == 0:
            train = time_series[-info[1]:]
            test = pd.Series(range(info[2]))
            test.index = pd.RangeIndex(start=train.index.stop, stop=train.index.stop+info[2])
        elif -back_shifting+short_period>=0:
            train = time_series[-info[3]-info[1]:-info[3]]
            test = time_series[-info[3]:]
        else:
            train = time_series[-info[3]-info[1]:-info[3]]
            test = time_series[-info[3]:-info[3]+info[2]]

        model = smt.SARIMAX(train, order=(p,d,q), seasonal_order=(P,D,Q,S)).fit(trend='c')
        prediction_train = model.predict()
        prediction_test = model.get_forecast(len(test)).predicted_mean
        prediction_test_bound = model.get_forecast(len(test)).conf_int()

        time_series.plot(label='stock', c='r', ax=axes[2])
        axes[2].plot(train.index, prediction_train, c='green', lw=3)
        axes[2].plot(test.index, prediction_test, c='purple', lw=3, label='predict')
        axes[2].plot(test.index, pd.DataFrame(prediction_test_bound, index=test.index).iloc[:,0], c='r', ls=':')
        axes[2].plot(test.index, pd.DataFrame(prediction_test_bound, index=test.index).iloc[:,1], c='r',ls=':')
        axes[2].fill_between(pd.DataFrame(prediction_test_bound, index=test.index).index,
                          pd.DataFrame(prediction_test_bound, index=test.index).iloc[:,0],
                          pd.DataFrame(prediction_test_bound, index=test.index).iloc[:,1], color='k', alpha=0.15)

        axes[2].grid(True)
        axes[2].legend()


        x = np.diff(x)
        x_ = np.diff(np.diff(x))
        index1 = np.where(x == x_)[0]
        index2 = np.where(x == x_[::-1])[0]
        axes[3].plot(x_, c='red', marker='o')
        axes[3].plot(x_[::-1], c='blue', marker='o')
        axes[3].plot(x, c='black', lw=5, marker='o')
        axes[3].plot(index1, x[index1], color='red', lw=0, marker='^')
        axes[3].plot(index2, x[index2], color='blue', lw=0, marker='v')
        axes[3].axhline(0, ls=':', c='black')
        axes[3].axvline(info[2]-2, ls=':', c='black')
        axes[3].grid(True)

        y = np.diff(y)
        axes[4].plot(x, lw=5, c='black', marker='o')
        axes[4].plot(y, marker='o')
        axes[4].plot(range(info[2]-1, info[2]-1+len(prediction_test)), prediction_test, marker='o', lw=5, c='purple', label='prediction')
        axes[4].fill_between(x=range(info[2]-1, info[2]-1+len(prediction_test)), y1=prediction_test_bound['lower y'], y2=prediction_test_bound['upper y'], color='lightgray')
        axes[4].axvline(info[2]-2, ls=':', c='black')
        axes[4].axhline(0, ls=':', c='black')
        axes[4].grid(True)
        axes[4].legend()
        plt.tight_layout()

