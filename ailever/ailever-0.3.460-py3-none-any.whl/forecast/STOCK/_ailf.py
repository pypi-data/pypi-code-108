from ._stattools import regressor, scaler
from ._deepNN import StockReader, Model, Criterion
import os
from copy import deepcopy
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
import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import DataLoader


dummies = type('dummies', (dict,), {})

class Ailf:
    r"""
    Examples:
	>>> from ailever.forecast.STOCK import krx, Ailf
	>>> ...
        >>> Df = krx.kospi('2018-01-01')
        >>> ailf = Ailf(Df, filter_period=300, criterion=1.5, GC=False, V=True)
        >>> ailf.Granger_C(['삼성전자', '현대차'])
        >>> ailf.KRXreport(ailf.index[0], long_period=200, short_period=30, back_shifting=0, return_Xy=False)
        >>> ailf.KRXforecast(ailf.index[0], long_period=200, short_period=30, back_shifting=0)
        >>> ailf.KRXdecompose(ailf.index[0], long_period=200, short_period=30, back_shifting=0, decompose_type='stl', resid_transform=True, scb=(0.3, 0.7))
        >>> ailf.TSA(ailf.index[0], long_period=200, short_period=30, back_shifting=0, sarimax_params=((2,0,2),(0,0,0,12)))

    Examples:
	>>> from ailever.forecast.STOCK import krx, Ailf
	>>> ...
        >>> Df = krx.kospi('2018-01-01')
        >>> ailf = Ailf(Df, filter_period=300, criterion=1.5, GC=False, V=True)
        >>> ailf.Granger_C(['삼성전자', '현대차'])
        >>> ailf.train(ailf.index[0], epochs=5000, breaking=0.0001, details=False, onlyload=False)
        >>> ailf.KRXreport(ailf.index[0], long_period=200, short_period=30, back_shifting=0, return_Xy=False)
        >>> ailf.KRXforecast(ailf.index[0], long_period=200, short_period=30, back_shifting=0)
        >>> ailf.KRXdecompose(ailf.index[0], long_period=200, short_period=30, back_shifting=0, decompose_type='stl', resid_transform=True, scb=(0.3, 0.7))
        >>> ailf.TSA(ailf.index[0], long_period=200, short_period=30, back_shifting=0, sarimax_params=((2,0,2),(0,0,0,12)))

    Examples:
	>>> from ailever.forecast.STOCK import krx, Ailf
	>>> ...
        >>> Df = krx.kospi('2018-01-01')
        >>> ailf = Ailf(Df, filter_period=300, criterion=1.5, GC=False, V=True)
        >>> ailf.Granger_C(['삼성전자', '현대차'])
        >>> ailf.train(ailf.index[0], onlyload=True)
        >>> ailf.KRXreport(ailf.index[0], long_period=200, short_period=30, back_shifting=0, return_Xy=False)
        >>> ailf.KRXforecast(ailf.index[0], long_period=200, short_period=30, back_shifting=0)
        >>> ailf.KRXdecompose(ailf.index[0], long_period=200, short_period=30, back_shifting=0, decompose_type='stl', resid_transform=True, scb=(0.3, 0.7))
        >>> ailf.TSA(ailf.index[0], long_period=200, short_period=30, back_shifting=0, sarimax_params=((2,0,2),(0,0,0,12)))
    """

    def __init__(self, Df, filter_period=300, criterion=1.5, GC=False, V='KS11'):
	# .Log folder
        if not os.path.isdir('.Log') : os.mkdir('.Log')
        # Korean Font Set
        for font in fm.fontManager.ttflist:
            if font.name == 'NanumBarunGothic':
                plt.rcParams["font.family"] = font.name
                break

        self.deepNN = None
        self.Df = Df

        norm = scaler.standard(self.Df[0][-filter_period:])
        yhat = regressor(norm)
        container = yhat[-1,:] - yhat[0,:]
        self.index = np.where(container>=criterion)[0]

        recommended_stock_info = self.Df[1].iloc[self.index]
        alert = list(zip(recommended_stock_info.Name.tolist(), recommended_stock_info.Symbol.tolist())); print(alert)
        
        self.dummies = dummies()

        if GC:
            self.Granger_C()

	# Visualization
        if V:
            df = pd.DataFrame(self.Df[0][:, self.index])
            df.columns = self.Df[1].iloc[self.index].Name
            ks11 = Df[3][V][self.Df[4]][-len(df):].reset_index().drop('index', axis=1)
            ks11.columns = [V]
            df = pd.concat([ks11, df], axis=1)

            plt.figure(figsize=(13,25)); layout = (5,1); axes = dict()
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



    def _train_init(self, stock_num=None):
        StockDataset = StockReader(self.Df, stock_num)
        train_dataset = StockDataset.type('train')
        validation_dataset = StockDataset.type('validation')

        self.train_dataloader = DataLoader(train_dataset, batch_size=100, shuffle=True, drop_last=True)
        self.validation_dataloader = DataLoader(validation_dataset, batch_size=100, shuffle=False, drop_last=True)

    def train(self, stock_num=None, epochs=2000, breaking=0.0001, details=False, onlyload=False):
        stock_num = self._querying(stock_num)
        self._train_init(stock_num)
        selected_stock_info = self.Df[1].iloc[stock_num]
        symbol = selected_stock_info.Symbol

        if torch.cuda.is_available() : device = torch.device('cuda')
        else : device = torch.device('cpu')
        
        if details:
            h_dim = int(input('* hidden dimension (default 32, int) : '))
            attn_drop = float(input('* drop rate of each attention (default 0.1, float) : '))
            attn_head = int(input('* number of head on each attention : (default 2, int) : '))
            n_layers = int(input('* number of the attention layer (default 1, int) : '))
            model = Model(h_dim, attn_drop, attn_head, n_layers)
        else:
            model = Model()

        if onlyload:
            urlretrieve(f'https://github.com/ailever/openapi/raw/master/forecast/stock/model{symbol}.pth', f'./.Log/model{symbol}.pth')
            model.load_state_dict(torch.load(f'.Log/model{symbol}.pth'))
            print(f'[AILF] The file ".Log/model{symbol}.pth" is successfully loaded!')
            self.deepNN = model
            self.deepNN.stock_info = selected_stock_info
            return None
        else:
            if os.path.isfile(f'.Log/model{symbol}.pth'):
                model.load_state_dict(torch.load(f'.Log/model{symbol}.pth'))
                print(f'[AILF] The file ".Log/model{symbol}.pth" is successfully loaded!')

        model = model.to(device)
        criterion = Criterion().to(device)
        optimizer = optim.Adam(model.parameters(), lr=1e-2, weight_decay=1e-6)

        for epoch in range(epochs):
            # Training
            for batch_idx, (x_train, y_train) in enumerate(self.train_dataloader):
                # forward
                hypothesis = model(x_train)
                cost = criterion(hypothesis, y_train)
                
                # backward
                optimizer.zero_grad()
                cost.backward()
                optimizer.step()

                if epoch%100 == 0:
                    print(f'[TRAIN][{epoch}/{epochs}] :', cost)
            if cost < breaking : break

            # Validation
            with torch.no_grad():
                model.eval()
                for batch_idx, (x_train, y_train) in enumerate(self.validation_dataloader):
                    # forward
                    hypothesis = model(x_train)
                    cost = criterion(hypothesis, y_train)
                    
                    if epoch%100 == 0:
                        print(f'[VAL][{epoch}/{epochs}] :', cost)
        
        # model save
        self.deepNN = model
        self.deepNN.stock_info = selected_stock_info
        torch.save(model.state_dict(), f'.Log/model{symbol}.pth')
        print(f'[AILF] The file ".Log/model{symbol}.pth" is successfully saved!')
        
        if not os.path.isfile('.Log/model_spec.json'):
            with open('.Log/model_spec.json', 'w') as f:
                json.dump(dict(), f, indent=4)

        with open('.Log/model_spec.json', 'r') as f:
            self.model_spec = json.load(f)

        self.model_spec[f'{symbol}'] = cost.tolist()

        with open('.Log/model_spec.json', 'w') as f:
            json.dump(self.model_spec, f, indent=4)


    def KRXreport(self, i=None, long_period=200, short_period=30, back_shifting=0, return_Xy=False):
        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting) # args params
        selected_stock_info = self.Df[1].iloc[info[0]]
        symbol = selected_stock_info.Symbol

        urlretrieve('https://raw.githubusercontent.com/ailever/openapi/master/forecast/stock/model_spec.json', './.Log/model_spec.json')
        with open('.Log/model_spec.json', 'r') as f:
            self.model_spec = json.load(f)

        ##########################################################################

        _, axes = plt.subplots(4,1,figsize=(13,15))
        axes[0].grid(True)
        axes[1].grid(True)
        axes[2].grid(True)
        axes[3].grid(True)

        axes[0].set_title(f'{selected_stock_info.Name}({selected_stock_info.Symbol})')

        try:
            df = fdr.DataReader(symbol)
            X = df.Close.values[-info[1]:]
        except:
            X = self.Df[0][:, info[0]][-info[1]:]
        norm = scaler.standard(X)
        yhat = regressor(norm)
        Yhat = yhat*X.std(ddof=1) + X.mean(axis=0)
        axes[0].plot(Yhat[-info[2]:], lw=0.5, label='longterm-trend')

        try:
            df = fdr.DataReader(symbol)
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
            axes[0].text(len(X_Open)*0.8, X_Open[-1]+itv, f'Upper-Bound:{int(X_Open[-1]+itv)}')
            axes[0].text(len(X_Open)*0.8, X_Open[-1]-itv, f'Lower-Bound:{int(X_Open[-1]-itv)}')
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
        ydata = smt.acf(_norm-_yhat, nlags=len(_yhat))
        degree = 2
        coef = np.polyfit(xdata, ydata, degree) #; print(f'Coefficients: {coef}')

        x = ydata - taylor_series(xdata, coef)
        x = scaler.minmax(x)

        index = {}
        index['min'] = np.where((x>=0) & (x<0.1))[0]
        index['down'] = np.where((x>=0.1) & (x<0.45))[0]
        index['mid'] = np.where((x>=0.45)&(x<0.55))[0]
        index['up'] = np.where((x<0.9) & (x>=0.55))[0]
        index['max'] = np.where((x<=1) & (x>=0.9))[0]
        if _yhat[-1] - _yhat[0] > 0: # ascend field
            axes[0].plot(index['min'], X[index['min']], lw=0, c='red', markersize=10, marker='^', label='S.B.S.')
            axes[0].plot(index['down'], X[index['down']], lw=0, c='red', alpha=0.3, marker='^', label='W.B.S.')
            axes[0].plot(index['mid'], X[index['mid']], lw=0, c='green', marker='o', label='b.S.')
            axes[0].plot(index['up'], X[index['up']], lw=0, c='blue', alpha=0.3, marker='v', label='W.S.S.')
            axes[0].plot(index['max'], X[index['max']], lw=0, c='blue', markersize=10, marker='v', label='S.S.S.')
        else: # descend field
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
        
        self.dummies['KRXreport'] = dict()
        self.dummies['KRXreport']['slopes1'] = slopes1
        self.dummies['KRXreport']['slopes2'] = slopes2

        axes[1].plot(self.Df[0][-info[1]:,info[0]])
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1), c='red')
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0, ls=':', c='red')
        axes[1].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*2, ls=':', c='red')
        if back_shifting == 0 : sp = self.Df[0][:,info[0]][-info[2]:].mean()
        else : sp = self.Df[0][:,info[0]][-info[3]-info[2]:-info[3]].mean()
        axes[1].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0], [sp,sp], c='black')
        axes[1].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1, sp, f'S.P.:{info[2]}')

        axes[2].plot(slopes1[::-1][-info[1]:])
        axes[2].axhline(0, ls=':', c='black')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1), c='red')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0, ls=':', c='red')
        axes[2].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*1, ls=':', c='red')
        axes[2].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0], [0,0], c='black')
        axes[2].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1, 0, f'S.P.:{info[2]}')

        axes[3].plot(slopes2[::-1][-info[1]:])
        axes[3].axhline(0, ls=':', c='black')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*(-1), c='red')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*0, ls=':', c='red')
        axes[3].axvline(len(self.Df[0][-info[1]:])-info[3]-info[2]*1, ls=':', c='red')
        axes[3].plot([len(self.Df[0][-info[1]:])-info[3]-info[2]*1, len(self.Df[0][-info[1]:])-info[3]-info[2]*0], [0,0], c='black')
        axes[3].text(len(self.Df[0][-info[1]:])-info[3]-info[2]*1, 0, f'S.P.:{info[2]}')


        plt.tight_layout()
        plt.show()
        print(selected_stock_info)
        
        if torch.cuda.is_available() : device = torch.device('cuda')
        else : device = torch.device('cpu')
        _ont = 2*(x - 0.5)
        xset = np.c_[_norm, _ont]
        xset = torch.from_numpy(xset).type(torch.FloatTensor).unsqueeze(0).to(device)


        # when there exist the file '.Log/model{~}.pth',
        try: 
            # when self.KRXreport() is called after self.train()
            if self.deepNN: 
                # when first argument(self.train(-, ~) = self.KRXreport(-, ~)) is same,
                if self.deepNN.stock_info.Symbol == symbol: 
                    prob = self.deepNN(xset).squeeze()
                    print('Probability :', prob)
                    print('Cost :', self.model_spec[f'{symbol}'])
                # when first argument(self.train(-, ~) = self.KRXreport(-, ~)) is different,
                else: 
                    urlretrieve(f'https://github.com/ailever/openapi/raw/master/forecast/stock/model{symbol}.pth', f'./.Log/model{symbol}.pth')
                    self.deepNN = Model()
                    self.deepNN.load_state_dict(torch.load(f'.Log/model{symbol}.pth', map_location=torch.device(device)))
                    self.deepNN.stock_info = selected_stock_info
                    prob = self.deepNN(xset).squeeze()
                    print('Probability :', prob)
                    print('Cost :', self.model_spec[f'{symbol}'])

            # when self.KRXreport() is called before self.train()
            elif os.path.isfile(f'.Log/model{symbol}.pth'):
                self.deepNN = Model()
                self.deepNN.load_state_dict(torch.load(f'.Log/model{symbol}.pth', map_location=torch.device(device)))
                self.deepNN.stock_info = selected_stock_info
                prob = self.deepNN(xset).squeeze()
                print('Probability :', prob)
                print('Cost :', self.model_spec[f'{symbol}'])

            # when self.KRXreport() is called before self.train()
            else: 
                urlretrieve(f'https://github.com/ailever/openapi/raw/master/forecast/stock/model{symbol}.pth', f'./.Log/model{symbol}.pth')
                self.deepNN = Model()
                self.deepNN.load_state_dict(torch.load(f'.Log/model{symbol}.pth', map_location=torch.device(device)))
                self.deepNN.stock_info = selected_stock_info
                prob = self.deepNN(xset).squeeze()
                print('Probability :', prob)
                print('Cost :', self.model_spec[f'{symbol}'])

        # when there not exist the file 'model{~}.pth',
        except: 
            prob = None
            print('Probability :', prob)

        if return_Xy:
            return xset, prob


    def KRXforecast(self, i=None, long_period=200, short_period=30, back_shifting=0):
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


        with plt.style.context('bmh'):
            layout = (8, 2)
            axes = {}
            fig = plt.figure(figsize=(13,20))
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

                if key.split(',')[0] == 'M':
                    if key.split(',')[1] == 'Ad':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})', ax=axes['0,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['0,0'])
                    elif key.split(',')[1] == 'M':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['1,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['1,0'])
                    elif key.split(',')[1] == 'A':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['2,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['2,0'])
                    elif key.split(',')[1] == 'N':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['3,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['3,0'])
                elif key.split(',')[0] == 'A':
                    if key.split(',')[1] == 'Ad':
                        model.fittedvalues.plot(style='--',  color='blue', label=r'$ETS$'+f'({key})',ax=axes['4,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['4,0'])
                    elif key.split(',')[1] == 'M':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['5,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['5,0'])
                    elif key.split(',')[1] == 'A':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['6,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['6,0'])
                    elif key.split(',')[1] == 'N':
                        model.fittedvalues.plot(style='--', color='blue', label=r'$ETS$'+f'({key})',ax=axes['7,0'])
                        forecast.plot(color='red', label=r'$ETS$'+f'({key})', ax=axes['7,0'])

                for i in range(8):
                    #axes[f'{i},0'].legend()
                    pass

                plt.tight_layout()

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


    def KRXdecompose(self, i=None, long_period=200, short_period=30, back_shifting=0, decompose_type='stl', resid_transform=False, scb=(0.1,0.9)):
        i = self._querying(i)
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]

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

        dropna_resid = result.resid[np.argwhere(np.logical_not(np.isnan(result.resid))).squeeze()]

        print(f'* {selected_stock_info.Name}({selected_stock_info.Symbol})')
        with plt.style.context('bmh'):
            layout = (6, 2)
            axes = {}
            fig = plt.figure(figsize=(13,15))
            axes['0,0'] = plt.subplot2grid(layout, (0, 0), colspan=2)
            axes['1,0'] = plt.subplot2grid(layout, (1, 0), colspan=2)
            axes['2,0'] = plt.subplot2grid(layout, (2, 0), colspan=2)
            axes['3,0'] = plt.subplot2grid(layout, (3, 0), colspan=2)
            axes['4,0'] = plt.subplot2grid(layout, (4, 0), colspan=1)
            axes['4,1'] = plt.subplot2grid(layout, (4, 1), colspan=1)
            axes['5,0'] = plt.subplot2grid(layout, (5, 0), colspan=1)
            axes['5,1'] = plt.subplot2grid(layout, (5, 1), colspan=1)

            axes['0,0'].set_title(f'{selected_stock_info.Name}({selected_stock_info.Symbol}) : Observed')
            axes['1,0'].set_title('Trend')
            axes['2,0'].set_title('Seasonal')
            axes['3,0'].set_title('Resid')
            axes['5,0'].set_title('Normal Q-Q')
            axes['5,1'].set_title('Probability Plot')

            # Decompose
            axes['0,0'].plot(result.observed)
            axes['1,0'].plot(result.trend)
            axes['2,0'].plot(result.seasonal)
            axes['3,0'].plot(result.resid)

            # Seasonality 
            x = scaler.minmax(result.seasonal)
            index = {}
            index['min'] = np.where((x<scb[0]) & (x>=0))[0]
            index['max'] = np.where((x<=1) & (x>scb[1]))[0]
            axes['2,0'].plot(index['min'], result.seasonal[index['min']], lw=0, marker='^')
            axes['2,0'].plot(index['max'], result.seasonal[index['max']], lw=0, marker='v')

            # ACF/PACF
            smt.graphics.plot_acf(dropna_resid, lags=info[2], ax=axes['4,0'], alpha=0.5)
            smt.graphics.plot_pacf(dropna_resid, lags=info[2], ax=axes['4,1'], alpha=0.5)
            # Residual Analysis
            sm.qqplot(dropna_resid, line='s', ax=axes['5,0'])
            stats.probplot(dropna_resid, sparams=(dropna_resid.mean(), dropna_resid.std()), plot=axes['5,1'])
            plt.tight_layout()
            plt.show()

        self._stationary(dropna_resid)

        # Profit
        if back_shifting == 0:
            yhat = regressor(result.trend[-info[2]:])
            trend_profit = (yhat[-1] - yhat[0])/(len(yhat)-1)
            seasonal = result.seasonal[-info[2]:]
            seasonal_profit = max(seasonal) - min(seasonal)
        else:
            yhat = regressor(result.trend[-info[3]-info[2]:-info[3]])
            trend_profit = (yhat[-1] - yhat[0])/(len(yhat)-1)
            seasonal = result.seasonal[-info[3]-info[2]:-info[3]]
            seasonal_profit = max(seasonal) - min(seasonal)

        print(f'* Trend Profit(per day) : {trend_profit}')
        print(f'* MAX Seasonal Profit : {seasonal_profit}')
        print(f'* MAX Risk by Residual : {min(dropna_resid)}')



    def TSA(self, i=None, long_period=200, short_period=5, back_shifting=3, sarimax_params=((2,0,2),(0,0,0,12))):

        if not i:
            i = self.index[0]
        info = (i, long_period, short_period, back_shifting)
        selected_stock_info = self.Df[1].iloc[info[0]]

        _, axes = plt.subplots(5,1, figsize=(13,12))
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

