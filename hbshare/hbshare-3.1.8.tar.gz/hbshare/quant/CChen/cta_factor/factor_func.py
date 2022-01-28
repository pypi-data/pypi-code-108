#!/usr/bin/python
# coding:utf-8
from hbshare.quant.CChen.func import generate_table
import pandas as pd
import numpy as np
import pymysql
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pandas.plotting import register_matplotlib_converters
from datetime import datetime

register_matplotlib_converters()

sql_l = '''(
    `ID` bigint not null AUTO_INCREMENT,
    `TDATE`  date not null,
    `EXCHANGE`  int,
    `PCODE`  int,
    `UCODE`  int,
    `CLOSE0`  float,
    `CLOSE` float,
    `CLOSE1` float,
    `POS` int,
    `WEIGHT`  double,
    `RETURN` double,
    `FACTORVALUE` double,
    `FACTOR`  varchar(255),
    primary key (`ID`)
    )
    '''

sql_index = '''(
    `ID` bigint not null AUTO_INCREMENT,
    `TDATE`  date not null,
    `CLOSE` float,
    `FACTOR`  varchar(255),
    primary key (`ID`)
    )
    '''


def factor_table_gen(table, sql_info):
    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='CTA factor based on hsjy data'
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')


def index_table_gen(table, sql_info):
    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_index,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='CTA INDEX'
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')


def index_gen(sql_path, sql_info, table_factor='cta_factor', table_index='cta_index'):
    index_table_gen(table=table_index, sql_info=sql_info)
    end_date_all = pd.read_sql_query(
        'select distinct TDATE from ' + table_factor + ' order by TDATE desc limit 1', sql_path
    )
    factors = pd.read_sql_query('select distinct FACTOR from ' + table_factor, sql_path)
    # factors = pd.read_sql_query(
    #     'select FACTOR from ' + table_factor
    #     + ' where TDATE<=' + end_date_all['TDATE'][0].strftime('%Y%m%d')
    #     + ' group by FACTOR',
    #     sql_path
    # )
    if len(factors) == 0:
        print('No factor return')
        return
    else:
        for i in range(len(factors['FACTOR'])):
            # factor = 'xswr_d1_q75'
            factor = factors['FACTOR'][i]
            last_factor_index = pd.read_sql_query(
                'select * from ' + table_index
                + ' where TDATE<=' + end_date_all['TDATE'][0].strftime('%Y%m%d')
                + ' and FACTOR=\'' + factor
                + '\' order by TDATE desc limit 1',
                sql_path
            )
            if len(last_factor_index) == 0:
                date0 = datetime(1990, 1, 1).date()
                index0 = 1000
            else:
                date0 = last_factor_index['TDATE'][0]
                index0 = last_factor_index['CLOSE'][0]

            print(
                str(i + 1) + '/' + str(len(factors['FACTOR'])) + ', '
                + factor + ', start date: ' + date0.strftime('%Y-%m-%d')
            )

            if date0 == end_date_all['TDATE'][0]:
                print('\tNo new date, ' + date0.strftime('%Y-%m-%d'))
                continue

            factor_data = pd.read_sql_query(
                'select * from ' + table_factor + ' where TDATE>' + date0.strftime('%Y%m%d')
                + ' and FACTOR=\'' + factor + '\' order by TDATE',
                sql_path
            )
            if len(factor_data) > 0:
                factor_data['RETURN'] = factor_data['RETURN'] * factor_data['WEIGHT'] * factor_data['POS']
                factor_data_g = factor_data.groupby(by='TDATE').sum()[['RETURN']].reset_index()
                factor_data_g['ret'] = factor_data_g['RETURN'] / 10000 + 1.0
                factor_data_g['CLOSE'] = factor_data_g['ret'].cumprod()
                factor_data_g['CLOSE'] = factor_data_g['CLOSE'] * index0
                factor_data_g['FACTOR'] = factor
                factor_data_g[['TDATE', 'CLOSE', 'FACTOR']].to_sql(
                    table_index, sql_path, if_exists='append', index=False
                )
                print(
                    '\t' + str(len(factor_data_g)) + ', to sql, '
                    + factor_data_g['TDATE'][len(factor_data_g) - 1].strftime('%Y-%m-%d')
                )
            else:
                print('\tNo new data')


def get_last_position(table, before_date, factor, sql_path):
    existing_cal = pd.read_sql_query(
        'select distinct `TDATE` from ' + table + ' where `TDATE`<=' + before_date.strftime('%Y%m%d')
        + ' and `FACTOR`=\'' + factor + '\' order by `TDATE` desc limit 1',
        sql_path
    )
    if len(existing_cal) >= 1:
        pos = pd.read_sql_query(
            'select * from ' + table + ' where `TDATE`=' + existing_cal['TDATE'][0].strftime('%Y%m%d')
            + ' and `FACTOR`=\'' + factor + '\'',
            sql_path
        )
        print(factor + ', load last date: ' + existing_cal['TDATE'][0].strftime('%Y-%m-%d'))
        return pos

    else:
        print('load last date: None')
        return None


def load_factor(sql_path, factor_name, table='cta_factor'):
    index = factor_name

    data = pd.read_sql_query(
        'select * from ' + table + ' where FACTOR=\'' + index + '\'',
        sql_path
    )
    return data


def factor_stats(data, trade_days=250, show=False):
    data['RETURN'] = data['RETURN'] * data['WEIGHT'] * data['POS']
    data_g = data.groupby(by='TDATE').sum()[['RETURN']].reset_index()
    # data_g = data.groupby(by='TDATE').mean()[['RETURN']].reset_index()
    data_g['ret'] = data_g['RETURN'] / 10000 + 1
    data_g['ind'] = data_g['ret'].cumprod()
    data_g['max_ind'] = data_g['ind'].cummax()
    cumulative_return = data_g['ind'][len(data_g) - 1] / data_g['ind'][0] - 1.0
    annualized_return = (cumulative_return + 1.0) ** (
            365 / (data_g['TDATE'][len(data_g) - 1] - data_g['TDATE'][0]).days
    ) - 1
    return_sample = ((data_g['ind'] - data_g['ind'].shift(1)) / data_g['ind'].shift(1))[1:]
    annualized_return_average = (return_sample.mean() + 1) ** trade_days - 1
    sigma = return_sample.std(ddof=1) * np.sqrt(trade_days)

    data_g['dd'] = (data_g['ind'] - data_g['max_ind']) / data_g['max_ind']
    data_g['year'] = data_g['TDATE'].apply(lambda x: x.year)

    range_dates = [data_g['TDATE'][0]]

    year_slice = data_g.drop_duplicates(subset=['year'], keep='last')

    if len(year_slice) > 0:
        range_dates += year_slice['TDATE'].tolist()

    result = {
        '累计收益': cumulative_return,
        '最大回撤': min(data_g['dd'][1:]),
        '年化收益率（头尾）': annualized_return,
        '年化收益率（平均）': annualized_return_average,
        '波动率': sigma
    }

    if show:
        print(
            '累计收益： \n\t%.2f%%' % round(cumulative_return * 100, 2)
        )
        print(
            '最大回撤：      \n\t%.2f%%' % round(min(data_g['dd'][1:]) * 100, 2)
        )
        print(
            '年化收益率（头尾）： \n\t%.2f%%' % round(annualized_return * 100, 2)
        )
        print(
            '年化收益率（平均）： \n\t%.2f%%' % round(annualized_return_average * 100, 2)
        )
        print(
            '波动率： \n\t%.2f%%' % round(sigma * 100, 2)
        )
        print(
            '收益波动比： \n\t%.2f' % round(annualized_return_average / sigma, 2)
        )
        if min(data_g['dd'][1:]) != 0:
            print(
                '收益回撤比：        \n\t%.2f' % round(-annualized_return_average / min(data_g['dd'][1:]), 2)
            )
        else:
            print(
                '收益回撤比：       \n\tinf'
            )

        print('')
        for i in range(1, len(range_dates)):
            range_return = (
                                   data_g[data_g['TDATE'] == range_dates[i]]['ind'].tolist()[0]
                                   / data_g[data_g['TDATE'] == range_dates[i - 1]]['ind'].tolist()[0]
                           ) - 1
            result[range_dates[i - 1].strftime('%Y/%m/%d') + ' - ' + range_dates[i].strftime('%Y/%m/%d')] = range_return
            print(
                range_dates[i - 1].strftime('%Y/%m/%d') + ' - ' + range_dates[i].strftime('%Y/%m/%d')
                + ':\t收益：%.2f%%' % round(range_return * 100, 2)
            )
    return data_g, result


def factor_plot(data, plot_title):
    def to_percent(temp, position):
        return '%.2f' % (100 * temp) + '%'

    data_g = data
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.fill_between(data_g['TDATE'], data_g['dd'], color='gray', alpha=0.3)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))

    ax2 = ax1.twinx()
    ax2.plot(data_g['TDATE'], data_g['ind'])

    plt.title(plot_title)
    plt.show()


def factor_compute(
        window_days_list,
        to_sql_path,
        sql_info,
        start_date=datetime(2010, 1, 1).date(),
        end_date=datetime.now(),
        to_table='cta_factor',
        data=None,
        factor_func=None,
        **kwargs
):
    if 'min_volume' in kwargs:
        min_volume = kwargs['min_volume']
    else:
        min_volume = 10000

    factor_table_gen(table=to_table, sql_info=sql_info)

    for window_days in window_days_list:
        if 'hedge_ratio_list' in kwargs:
            for quantile in kwargs['hedge_ratio_list']:
                index_name = factor_func.__name__ + '_d' + str(window_days) + '_q' + str(quantile)
                exist_index = get_last_position(
                    table=to_table,
                    before_date=end_date,
                    factor=index_name,
                    sql_path=to_sql_path
                )
                if exist_index is not None:
                    start_date0 = exist_index['TDATE'][0]
                else:
                    start_date0 = start_date

                pos = factor_func(
                    start_date=start_date0,
                    data=data,
                    window_days=window_days,
                    quantile=quantile,
                    min_volume=min_volume,
                    **kwargs
                )
                if pos is not None:
                    pos.to_sql(to_table, to_sql_path, if_exists='append', index=False)
                    print('\t' + index_name + ' to sql, ' + pos['TDATE'].tolist()[-1].strftime('%Y-%m-%d'))
                else:
                    print('\t' + index_name + ', no new data')

        else:
            index_name = factor_func.__name__ + '_d' + str(window_days)
            exist_index = get_last_position(
                table=to_table,
                before_date=end_date,
                factor=index_name,
                sql_path=to_sql_path
            )

            if exist_index is not None:
                start_date0 = exist_index['TDATE'][0]
            else:
                start_date0 = start_date

            pos = factor_func(
                start_date=start_date0, data=data, window_days=window_days, min_volume=min_volume, **kwargs
            )
            if pos is not None:
                pos.to_sql(to_table, to_sql_path, if_exists='append', index=False)
                print('\t' + index_name + ' to sql, ' + pos['TDATE'].tolist()[-1].strftime('%Y-%m-%d'))
            else:
                print('\t' + index_name + ', no new data')


if __name__ == '__main__':
    index_gen()
