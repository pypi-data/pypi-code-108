#from EYESApp import app
from .EYESApp import app

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import os
from datetime import datetime
import copy
import numpy as np
import pandas as pd
import statsmodels.tsa.api as smt
import FinanceDataReader as fdr


today = datetime.today()
df = {}
markets = ['NYSE', 'NASDAQ', 'AMEX', 'KRX', 'KOSPI', 'KOSDAQ', 'KONEX', 'KRX-DELISTING', 'KRX-ADMINISTRATIVE', 'SSE', 'SZSE', 'HKEX', 'TSE', 'HOSE']
for market in markets:
    if os.path.isfile(f'{market}.csv'):
        df[f'{market}'] = pd.read_csv(f'{market}.csv').drop('Unnamed: 0', axis=1)

class Components(dict):
    def updateR0C0(self):
        self['0,0'] = [dcc.Graph(figure=self._loader('KRX', '삼성전자'))]
    def updateR0C1(self):
        self['0,1'] = [dcc.Graph(figure=self._loader('KRX', 'SK하이닉스'))]
    def updateR1C0(self):
        self['1,0'] = [dcc.Graph(figure=self._loader('KRX', 'LG화학'))]
    def updateR1C1(self):
        self['1,1'] = [dcc.Graph(figure=self._loader('KRX', '현대차'))]
    def updateR2C0(self):
        self['2,0'] = [dcc.Graph(figure=self._loader('KRX', '삼성바이오로직스'))]
    def updateR2C1(self):
        self['2,1'] = [dcc.Graph(figure=self._loader('KRX', '셀트리온'))]
    def updateR3C0(self):
        self['3,0'] = [dcc.Graph(figure=self._loader('KRX', 'NAVER'))]
    def updateR3C1(self):
        self['3,1'] = [dcc.Graph(figure=self._loader('KRX', '삼성SDI'))]
    def updateR4C0(self):
        self['4,0'] = [dcc.Graph(figure=self._loader('KRX', '카카오'))]
    def updateR4C1(self):
        self['4,1'] = [dcc.Graph(figure=self._loader('KRX', '현대모비스'))]
    def updateR5C0(self):
        self['5,0'] = [dcc.Graph(figure=self._loader('KRX', '기아차'))]
    def updateR5C1(self):
        self['5,1'] = [dcc.Graph(figure=self._loader('KRX', '삼성물산'))]
    def updateR6C0(self):
        self['6,0'] = [dcc.Graph(figure=self._loader('KRX', 'SK이노베이션'))]
    def updateR6C1(self):
        self['6,1'] = [dcc.Graph(figure=self._loader('KRX', 'LG생활건강'))]
    def updateR7C0(self):
        self['7,0'] = [dcc.Graph(figure=self._loader('KRX', 'POSCO'))]
    def updateR7C1(self):
        self['7,1'] = [dcc.Graph(figure=self._loader('KRX', 'LG전자'))]
    def updateR8C0(self):
        self['8,0'] = [dcc.Graph(figure=self._loader('KRX', '엔씨소프트'))]
    def updateR8C1(self):
        self['8,1'] = [dcc.Graph(figure=self._loader('KRX', 'SK텔레콤'))]
    def updateR9C0(self):
        self['9,0'] = [dcc.Graph(figure=self._loader('KRX', 'SK'))]
    def updateR9C1(self):
        self['9,1'] = [dcc.Graph(figure=self._loader('KRX', 'KB금융'))]
    def updateR10C0(self):
        self['10,0'] = [dcc.Graph(figure=self._loader('KRX', 'LG'))]
    def updateR10C1(self):
        self['10,1'] = [dcc.Graph(figure=self._loader('KRX', '신한지주'))]



    def _loader(self, market, company):
        stock_info = df[f'{market}'][df[f'{market}'].Name==company]
        symbol = str(stock_info.Symbol.values[0])
        price = fdr.DataReader(symbol, exchange=market)
        stock_df = price
        time_series = stock_df['Close']
        fig = px.scatter(stock_df.reset_index(), x='Date', y='Close', title=f'{company}', trendline="ols")
        fig.update_xaxes(rangeslider_visible=True,
                         rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                          dict(count=3, label="3m", step="month", stepmode="backward"),
                                                          dict(count=6, label="6m", step="month", stepmode="backward"),
                                                          dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                          dict(count=1, label="1y", step="year", stepmode="backward"),
                                                          dict(count=3, label="3y", step="year", stepmode="backward"),
                                                          dict(count=5, label="5y", step="year", stepmode="backward"),
                                                          dict(step="all")])))

        return fig
