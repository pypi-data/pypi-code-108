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
    def __init__(self):
        self['0,0'] = None

    def updateR0C0(self):
        self['0,0'] = [html.Div([dcc.RadioItems(id="market",
                                                options=[{'label':market, 'value':market} for market in markets],
                                                value='NYSE'),
                                 dcc.Dropdown(id='company',
                                              options=[{"label": x, "value": x} for x in df['NYSE'].Name],
                                              value='Goldman Sachs Group Inc',
                                              clearable=False),
                                 html.Br(),
                                 html.H2("Time Series"),
                                 dcc.RadioItems(id="plot-type",
                                                options=[{'label': 'Line', 'value':'L'},
                                                         {'label': 'Scatter', 'value':'S'}],
                                                value='L'),
                                 dcc.Graph(id='graph1'),
                                 html.H4("Time Series : Auto-Correlation"),
                                 dcc.Graph(id='graph2'),
                                 dcc.Graph(id='graph3'),
                                 html.H2("Difference"),
                                 dcc.Graph(id='graph4'),
                                 html.H4("Difference : Auto-Correlation"),
                                 dcc.Graph(id='graph5'),
                                 dcc.Graph(id='graph6')])]

@app.callback(
    Output('company', 'options'),
    Output('company', 'value'),
    Input('market', 'value')
)
def stock_market(market):
    value = df[f'{market}'].Name.iloc[0]
    options = [{"label": x, "value": x} for x in df[f'{market}'].Name]
    return options, value

@app.callback(
    Output('graph1', "figure"),
    Output('graph2', "figure"),
    Output('graph3', "figure"),
    Output('graph4', "figure"),
    Output('graph6', "figure"),
    Output('graph5', "figure"),
    Input('market', "value"),
    Input('company', "value"),
    Input('plot-type', "value"),
)
def display_timeseries(market, company, plot_type):
    stock_info = df[f'{market}'][df[f'{market}'].Name==company]
    symbol = str(stock_info.Symbol.values[0])
    price = fdr.DataReader(symbol, exchange=market)
    stock_df = price
    time_series = stock_df['Close']

    # FIG1
    if plot_type == 'L':
        fig1 = px.line(stock_df.reset_index(), x='Date', y='Close')
        fig1.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                           dict(count=3, label="3m", step="month", stepmode="backward"),
                                                           dict(count=6, label="6m", step="month", stepmode="backward"),
                                                           dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                           dict(count=1, label="1y", step="year", stepmode="backward"),
                                                           dict(count=3, label="3y", step="year", stepmode="backward"),
                                                           dict(count=5, label="5y", step="year", stepmode="backward"),
                                                           dict(step="all")])))
    elif plot_type == 'S':
        fig1 = px.scatter(stock_df['Close'], trendline='ols', title=f'{company}')
        fig1.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                           dict(count=3, label="3m", step="month", stepmode="backward"),
                                                           dict(count=6, label="6m", step="month", stepmode="backward"),
                                                           dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                           dict(count=1, label="1y", step="year", stepmode="backward"),
                                                           dict(count=3, label="3y", step="year", stepmode="backward"),
                                                           dict(count=5, label="5y", step="year", stepmode="backward"),
                                                           dict(step="all")])))

    # FIG2
    ACF = smt.acf(time_series, alpha=0.05)[0]
    ACF_LOWER = smt.acf(time_series, alpha=0.05)[1][:, 0]
    ACF_UPPER = smt.acf(time_series, alpha=0.05)[1][:, 1]
    ACF_DF = pd.DataFrame(data={'acf':ACF, 'acf_lower':ACF_LOWER, 'acf_upper':ACF_UPPER})

    acf = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf'],
        mode = 'lines',
        name = 'ACF(MA)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    acf_lower = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    acf_upper = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [acf, acf_lower, acf_upper]
    fig2 = go.Figure(data = data)

    # FIG3
    PACF = smt.pacf(time_series, alpha=0.05)[0]
    PACF_LOWER = smt.pacf(time_series, alpha=0.05)[1][:, 0]
    PACF_UPPER = smt.pacf(time_series, alpha=0.05)[1][:, 1]
    PACF_DF = pd.DataFrame(data={'pacf':PACF, 'pacf_lower':PACF_LOWER, 'pacf_upper':PACF_UPPER})

    pacf = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf'],
        mode = 'lines',
        name = 'PACF(AR)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    pacf_lower = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    pacf_upper = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [pacf, pacf_lower, pacf_upper]
    fig3 = go.Figure(data = data)

    # FIG4
    fig4 = px.line(stock_df.diff().reset_index(), x='Date', y='Close')
    fig4.update_xaxes(rangeslider_visible=True,
                      rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                       dict(count=3, label="3m", step="month", stepmode="backward"),
                                                       dict(count=6, label="6m", step="month", stepmode="backward"),
                                                       dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                       dict(count=1, label="1y", step="year", stepmode="backward"),
                                                       dict(count=3, label="3y", step="year", stepmode="backward"),
                                                       dict(count=5, label="5y", step="year", stepmode="backward"),
                                                       dict(step="all")])))

    # FIG5
    ACF = smt.acf(time_series.diff().dropna(), alpha=0.05)[0]
    ACF_LOWER = smt.acf(time_series.diff().dropna(), alpha=0.05)[1][:, 0]
    ACF_UPPER = smt.acf(time_series.diff().dropna(), alpha=0.05)[1][:, 1]
    ACF_DF = pd.DataFrame(data={'acf':ACF, 'acf_lower':ACF_LOWER, 'acf_upper':ACF_UPPER})

    acf = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf'],
        mode = 'lines',
        name = 'ACF(MA)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    acf_lower = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    acf_upper = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [acf, acf_lower, acf_upper]
    fig5 = go.Figure(data = data)

    # FIG6
    PACF = smt.pacf(time_series.diff().dropna(), alpha=0.05)[0]
    PACF_LOWER = smt.pacf(time_series.diff().dropna(), alpha=0.05)[1][:, 0]
    PACF_UPPER = smt.pacf(time_series.diff().dropna(), alpha=0.05)[1][:, 1]
    PACF_DF = pd.DataFrame(data={'pacf':PACF, 'pacf_lower':PACF_LOWER, 'pacf_upper':PACF_UPPER})

    pacf = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf'],
        mode = 'lines',
        name = 'PACF(AR)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    pacf_lower = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    pacf_upper = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [pacf, pacf_lower, pacf_upper]
    fig6 = go.Figure(data = data)

    return fig1, fig2, fig3, fig4, fig5, fig6
