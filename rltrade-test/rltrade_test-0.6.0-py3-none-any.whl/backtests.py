import os
import numpy as np
import pandas as pd
import pypbo as pbo
import pypbo.perf as perf
import plotly.graph_objects as go
from scipy.stats.stats import pearsonr
from scipy.stats import ttest_ind,linregress


def get_metrics(path,live=False):
    path = os.path.join(os.getcwd(),path)
    train_df = pd.read_csv(path+'/train_df.csv')
    train_df['date'] = pd.to_datetime(train_df['date'])
    train_daily_return = train_df.groupby('date')['return with cost'].sum()
    train_total_daily_return = train_daily_return.sum()

    test_df = pd.read_csv(path+'/test_df.csv')
    test_df['date'] = pd.to_datetime(test_df['date'])
    test_daily_return = test_df.groupby('date')['return with cost'].sum()
    test_total_daily_return = test_daily_return.sum()

    def metric(x):
        return np.sqrt(255) * perf.sortino_iid(x)
    
    train_sortino = (252 **0.5) * train_daily_return.mean()/train_daily_return[train_daily_return<=0].std()
    test_sortino = (252 ** 0.5) * test_daily_return.mean()/test_daily_return[test_daily_return<=0].std()

    train_avg_return= train_daily_return.mean()
    train_max_drawdown = train_daily_return.diff(1).min()
    train_calamar = train_avg_return/ train_max_drawdown

    test_avg_return= test_daily_return.mean()
    test_max_drawdown = test_daily_return.diff(1).min()
    test_calamar = test_avg_return/ test_max_drawdown

    train_test_p_value = ttest_ind(train_daily_return,test_daily_return)[1]
    
    if len(train_daily_return) >= len(test_daily_return):
        train_test_corr = pearsonr(train_daily_return.tail(len(test_daily_return)).values,test_daily_return.values)[0]
        train_test_rvalue = linregress(train_daily_return.tail(len(test_daily_return)).values,test_daily_return.values)[2]
        all_return = pd.concat([train_daily_return.tail(len(test_daily_return))] + [test_daily_return],axis=1)
        probability = pbo.pbo(all_return,S=16,metric_func=metric,threshold=0,n_jobs=4,verbose=False,hist=False,plot=False)[0]
    else:
        train_test_corr = pearsonr(test_daily_return.tail(len(train_daily_return)).values,train_daily_return.values)[0]
        train_test_rvalue = linregress(test_daily_return.tail(len(train_daily_return)).values,train_daily_return.values)[2]
        all_return = pd.concat([test_daily_return.tail(len(train_daily_return))] + [train_daily_return],axis=1)
        probability = pbo.pbo(all_return,S=16,metric_func=metric,threshold=0,n_jobs=4,verbose=False,hist=False,plot=False)[0]

    if os.path.exists(path+'/live_df.csv') and live:
        live_df = pd.read_csv(path+'/live_df.csv')
        live_df = live_df.drop_duplicates('date')
        live_daily_return = live_df.groupby('date')['return with cost'].sum()
        live_total_daily_return = live_daily_return.sum()
        live_sortino = (252 ** 0.5) * live_daily_return.mean() / live_daily_return[live_daily_return<=0].std()
        live_calamar = live_daily_return.mean()/live_daily_return.diff(1).min()
        train_live_p_value = ttest_ind(train_daily_return,live_daily_return)[1]
        test_live_p_value = ttest_ind(test_daily_return,live_daily_return)[1]
        if len(train_daily_return) >= len(live_daily_return):
            train_live_corr = pearsonr(train_daily_return.tail(len(live_daily_return)).values,live_daily_return.values)[0]
            train_live_rvalue = linregress(train_daily_return.tail(len(live_daily_return)).values,live_daily_return.values)[2]
        else:
            train_live_corr = pearsonr(live_daily_return.tail(len(train_daily_return)).values,train_daily_return.values)[0]
            train_live_rvalue = linregress(live_daily_return.tail(len(train_daily_return)).values,train_daily_return.values)[2]

        if len(test_daily_return)>= len(live_daily_return):
            test_live_corr = pearsonr(test_daily_return.tail(len(live_daily_return)).values,live_daily_return.values)[0]
            test_live_rvalue = linregress(test_daily_return.tail(len(live_daily_return)).values,live_daily_return.values)[2]
        else:
            test_live_corr = pearsonr(live_daily_return.tail(len(test_daily_return)).values,test_daily_return.values)[0]
            test_live_rvalue = linregress(live_daily_return.tail(len(test_daily_return)).values,test_daily_return.values)[2]

        metrics_df = pd.DataFrame([['sortino',train_sortino,test_sortino,live_sortino],
                                ['calamar',train_calamar,test_calamar,live_calamar],
                                ['total return',train_total_daily_return,test_total_daily_return,live_total_daily_return],
                                ['train live corr',train_live_corr,'-',train_live_corr],
                                ['test live corr','-',test_live_corr,test_live_corr],
                                ['train live p-value',train_live_p_value,'-',train_live_p_value],
                                ['test live p-value','-',test_live_p_value,test_live_p_value],
                                ['train live r2-value',train_live_rvalue**2,'-',train_live_rvalue**2],
                                ['test live r2-value','-',test_live_rvalue**2,test_live_rvalue**2]])

        metrics_df.columns = ['metrics','train','test','live']
    
    else:
        metrics_df = pd.DataFrame([['sortino',train_sortino,test_sortino],
                                    ['calamar',train_calamar,test_calamar],
                                    ['total return',train_total_daily_return,test_total_daily_return],
                                    ['overfit probability',probability,'-'],
                                     ['corr',train_test_corr,'-'],
                                     ['p-value',train_test_p_value,'-'],
                                     ['r2-value',train_test_rvalue**2,'-']])

        metrics_df.columns = ['metrics','train','test']

    print(metrics_df)

def get_symbol_df(path,symbol):
    path = os.path.join(os.getcwd(),path)
    df_train = pd.read_csv(path+'/train_df.csv')
    df_test = pd.read_csv(path+'/test_df.csv')
    df = pd.concat([df_train,df_test])
    df.drop_duplicates(['date','tic'],inplace=True)
    df = df[df['tic'] == symbol]
    df.reset_index(inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    return df

def plot_chart_forex(path,symbol,lot_size):
    df = get_symbol_df(path,symbol)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']))
    fig.add_trace(go.Scatter(
        x=df.query(f'lots == {lot_size}')['date'],
        y=df.query(f'lots == {lot_size}')['close'],
        mode='markers',
        marker={"size":5,"color":"blue"},
        name=f'lot {lot_size}'
    ))
    fig.add_trace(go.Scatter(
        x=df.query('lots == 0')['date'],
        y=df.query('lots == 0')['close'],
        mode='markers',
        marker={"size":5,"color":"pink"},
        name='lot 0'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(f'lots == {-lot_size}')['date'],
        y=df.query(f'lots == {-lot_size}')['close'],
        mode='markers',
        marker={"size":5,"color":"yellow"},
        name=f'lot {-lot_size}'
    ))
    fig.update_layout(
        title=f'Chart for {symbol}',
        xaxis_title = "Date",
        yaxis_title="close",
    )
    fig.show()

def plot_chart_stocks(path,symbol):
    df = get_symbol_df(path,symbol)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']))
    
    q = 'weights >= {} & weights <= {}'
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0,0.1))['date'],
        y=df.query(q.format(0,0.1))['close'],
        mode='markers',
        marker={"size":5,"color":(1,0,0)},
        name='weights 0.0-0.1'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.1,0.2))['date'],
        y=df.query(q.format(0.1,0.2))['close'],
        mode='markers',
        marker={"size":5,"color":(0,1,0)},
        name='weights 0.1-0.2'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.2,0.3))['date'],
        y=df.query(q.format(0.2,0.3))['close'],
        mode='markers',
        marker={"size":5,"color":'#2ff3e0'},
        name='weights 0.2-0.3'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.3,0.4))['date'],
        y=df.query(q.format(0.3,0.4))['close'],
        mode='markers',
        marker={"size":5,"color":"#f8d210"},
        name='weights 0.3-0.4'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.4,0.5))['date'],
        y=df.query(q.format(0.4,0.5))['close'],
        mode='markers',
        marker={"size":5,"color":"#fa26a0"},
        name='weights 0.4-0.5'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.5,0.6))['date'],
        y=df.query(q.format(0.5,0.6))['close'],
        mode='markers',
        marker={"size":5,"color":"#f51720"},
        name='weights 0.5-0.6'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.6,0.7))['date'],
        y=df.query(q.format(0.6,0.7))['close'],
        mode='markers',
        marker={"size":5,"color":"#050a30"},
        name='weights 0.6-0.7'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.7,0.8))['date'],
        y=df.query(q.format(0.7,0.8))['close'],
        mode='markers',
        marker={"size":5,"color":"#000c66"},
        name='weights 0.7-0.8'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.8,0.9))['date'],
        y=df.query(q.format(0.8,0.9))['close'],
        mode='markers',
        marker={"size":5,"color":"#0000ff"},
        name='weights 0.8-0.9'
    ))
    fig.add_trace(go.Scatter(
        x=df.query(q.format(0.9,1))['date'],
        y=df.query(q.format(0.9,1))['close'],
        mode='markers',
        marker={"size":5,"color":"#7ec8e3"},
        name='weights 0.9-1'
    ))
    fig.update_layout(
        title=f'Chart for {symbol}',
        xaxis_title = "Date",
        yaxis_title="close",
    )
    fig.show()


# import pyfolio
# from copy import deepcopy
# from pyfolio import timeseries
# from rltrade import config
# from rltrade.data import IBKRDownloader

# def get_daily_return(df,value_col_name="account_value"):
#     df = deepcopy(df)
#     df = df.groupby(['date'])[value_col_name].sum().pct_change(1).reset_index()
#     df.set_index('date',inplace=True,drop=True)
#     df.index = df.index.tz_localize("UTC")
#     return pd.Series(df[value_col_name],index=df.index)

# def convert_daily_return_to_pyfolio_ts(df):
#     strategy_ret = df.copy()
#     strategy_ret['date'] = pd.to_datetime(strategy_ret['date'])
#     strategy_ret.set_index('date',drop=False,inplace=True)
#     strategy_ret.index = strategy_ret.index.tz_localize("UTC")
#     del strategy_ret['date']
#     return pd.Series(strategy_ret['daily_return'].to_numpy(),index=strategy_ret.index)

# def get_baseline(ticker,sec_types,exchanges,start,end,start_time,end_time,mode,demo):
#     if mode == 'daily':
#         df = IBKRDownloader(start_date=start,
#         end_date=end,ticker_list=ticker,
#         sec_types=sec_types,
#         exchanges=exchanges,
#         start_time=start_time,
#         end_time=end_time,
#         demo=demo,
#         ).fetch_data()
#     elif mode == 'min':
#         df = IBKRDownloader(start_date=start,
#         end_date=end,ticker_list=ticker,
#         sec_types=sec_types,
#         exchanges=exchanges,
#         start_time=start_time,
#         end_time=end_time,
#         demo=demo,
#         ).fetch_min_data()
#     df = df.sort_values(by=['date','tic']).reset_index(drop=True)
#     return df

# def backtest_stats(df,
#                 baseline_start = config.START_TRADE_DATE,
#                 baseline_end = config.END_DATE,
#                 start_time="09:30:00",
#                 end_time = "15:59:00",
#                 baseline_ticker=[],
#                 sec_types=[],
#                 exchanges=[],
#                 value_col_name="account_value",
#                 mode='daily',
#                 demo=True):

#     if value_col_name == "daily_return":
#         df = convert_daily_return_to_pyfolio_ts(df)
    
#     if value_col_name == "account_value":
#         df = get_daily_return(df,value_col_name=value_col_name)
    
#     perf_stats_all = timeseries.perf_stats(returns=df,turnover_denom="AGB")
    
#     baseline_df = get_baseline(ticker=baseline_ticker,sec_types=sec_types,exchanges=exchanges,
#                                 start=baseline_start,end=baseline_end,
#                                 start_time=start_time,end_time=end_time,
#                                 mode=mode,demo=demo)
#     baseline_df = baseline_df[(baseline_df['date']>=baseline_start) & (baseline_df['date'] <= baseline_end)]
#     baseline_df['date'] = pd.to_datetime(baseline_df['date'],format="%Y-%m-%d")
#     baseline_df = baseline_df.fillna(method='ffill').fillna(method='bfill')
#     baseline_returns = get_daily_return(baseline_df,value_col_name="close")
#     perf_baseline = timeseries.perf_stats(returns=baseline_returns,turnover_denom='AGB')

#     df = pd.concat((perf_stats_all,perf_baseline),axis=1)
#     df.columns = ["model","baseline"]
#     return df


# def backtest_plot(account_value,
#                 baseline_start = config.START_TRADE_DATE,
#                 baseline_end = config.END_DATE,
#                 start_time="09:30:00",
#                 end_time="15:59:00",
#                 baseline_ticker='^DJI',
#                 sec_types=[],
#                 exchanges=[],
#                 value_col_name="account_value",
#                 mode='daily',
#                 demo=True):
#     df = deepcopy(account_value)
#     df['date'] = pd.to_datetime(df['date'])

#     if value_col_name == "daily_return":
#         test_returns = convert_daily_return_to_pyfolio_ts(df)
    
#     if value_col_name == "account_value":
#         test_returns = get_daily_return(df,value_col_name=value_col_name)

#     baseline_df = get_baseline(ticker=baseline_ticker,
#                                 sec_types=sec_types,exchanges=exchanges,
#                                 start=baseline_start,end=baseline_end,
#                                 start_time=start_time,end_time=end_time,
#                                 mode=mode,demo=demo)

#     baseline_df['date'] = pd.to_datetime(baseline_df['date'],format="%Y-%m-%d")
#     baseline_df = pd.merge(df['date'],baseline_df,how='left',on='date')
#     baseline_df = baseline_df.fillna(method='ffill').fillna(method='bfill')
#     baseline_returns = get_daily_return(baseline_df,value_col_name="close")

#     with pyfolio.plotting.plotting_context(font_scale=1.1):
#         pyfolio.create_full_tear_sheet(
#             returns=test_returns,
#             benchmark_rets=baseline_returns,
#             set_context=False)