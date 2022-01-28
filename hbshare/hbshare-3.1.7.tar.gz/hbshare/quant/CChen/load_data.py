#!/usr/bin/python
# coding:utf-8
import pandas as pd
import numpy as np
import pymysql
from datetime import datetime
from sqlalchemy import create_engine

pymysql.install_as_MySQLdb()


def load_calendar(start_date=None, end_date=None, freq='', db_path='', table='stocks_index_ts'):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()

    if end_date is None:
        end_date = datetime.now().date()

    engine_stocks = create_engine(db_path)
    trade_cal = pd.read_sql_query(
        'select distinct t_date from ' + table
        + ' where t_date>=' + start_date.strftime('%Y%m%d') + ' and t_date<='
        + end_date.strftime('%Y%m%d') + ' order by t_date',
        engine_stocks
    )
    if freq.lower() in ['w', 'week', 'weekly']:
        trade_cal = trade_cal.set_index(pd.to_datetime(trade_cal['t_date'])).resample('W').max().reset_index(drop=True)
    elif freq.lower() in ['m', 'month', 'monthly']:
        trade_cal = trade_cal.set_index(pd.to_datetime(trade_cal['t_date'])).resample('M').max().reset_index(drop=True)
    return trade_cal[trade_cal['t_date'] >= start_date].reset_index(drop=True)


# 交易日的日期戳(周度或月度)
# 如果当月未结束会以当月最后一个交易日当作当月的最后一个值
def load_calendar_extra(start_date=None, end_date=None, freq='', db_path=''):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()

    if end_date is None:
        end_date = datetime.now().date()

    if freq.lower() in ['w', 'week', 'weekly']:
        cal_spe = load_calendar(start_date=start_date, end_date=end_date, freq=freq, db_path=db_path)
    elif freq.lower() in ['month', 'monthly']:
        cal_spe = load_calendar(start_date=start_date, end_date=end_date, freq=freq, db_path=db_path)
        cal_week = load_calendar(start_date=start_date, end_date=end_date, freq='w', db_path=db_path)
        cal_extra = cal_week[cal_week['t_date'] > cal_spe['t_date'][len(cal_spe) - 1]].reset_index(drop=True)
        if len(cal_extra) > 0:
            cal_spe = cal_spe.append(cal_extra.loc[len(cal_extra) - 1]).reset_index(drop=True)
    else:
        cal_spe = load_calendar(start_date=start_date, end_date=end_date, db_path=db_path)
    return cal_spe


# 输入产品列表，输出对应产品的周净值或月净值
# 输入：DataFrame，输出：DataFrame
# 如果first_date设置的太早会自动剔除前期空值
# 净值第一次变化的时间点为数据起点（此条取消）
def load_funds_data(
        fund_list, first_date=None, end_date=None, freq='w', fillna=True, all_aligned=False,
        db_path='', cal_db_path='', print_info=False, drop_1=False,
):
    if first_date is None:
        first_date = datetime.now().date()

    if end_date is None:
        end_date = datetime.now().date()

    cal = load_calendar(end_date=end_date, db_path=cal_db_path)
    cal_weekly = load_calendar_extra(freq='w', end_date=end_date, db_path=cal_db_path)

    cal_spe = load_calendar_extra(freq=freq, end_date=end_date, db_path=cal_db_path)
    cal_all = cal_spe.copy()
    i_dates = []
    if len(fund_list) == 1:
        sql_l = 'code=\'' + fund_list['code'][0] + '\''
    else:
        sql_l = 'code in ' + str(tuple(fund_list['code']))

    fund_data_all = pd.read_sql_query(
        'select * from fund_data where ' + sql_l + ' and t_date<=' + end_date.strftime('%Y%m%d')
        + ' order by t_date',
        create_engine(db_path)
    )[['t_date', 'nav', 'code']]
    fund_data_all['code'] = fund_data_all['code'].apply(lambda x: x.lower())

    for i in range(len(fund_list)):
        fund_code = fund_list['code'][i].lower()
        fund_name = fund_list['name'][i]
        if print_info:
            print('Loading ' + fund_name + ' ' + freq + '；')
        # if first_date > fund_list['first_date'][i]:
        #     first_date = fund_list['first_date'][i]

        fund_data = fund_data_all[
            fund_data_all['code'] == fund_code
        ][['t_date', 'nav']].rename(columns={'nav': fund_name})
        fund_data = fund_data.drop_duplicates(['t_date'], keep='first').reset_index(drop=True)

        # 天眼赛能特殊处理
        if fund_code == 'P22984'.lower():
            fund_data = fund_data[fund_data['t_date'] >= datetime(2019, 8, 2).date()].reset_index(drop=True)

        fund_data = pd.merge(cal, fund_data, on='t_date', how='left')

        if fillna:
            # latest_date_i = fund_data[fund_data[fund_name] > 0].index[-1]
            # fund_data = fund_data.fillna(method='ffill')
            try:
                latest_date = fund_data[fund_data[fund_name] > 0].reset_index()['t_date'].tolist()[-1]
            except IndexError:
                latest_date = fund_data.reset_index()['t_date'].tolist()[0]
            if freq != '':
                try:
                    latest_date_week = cal_weekly[
                        cal_weekly['t_date'] >= latest_date
                    ].reset_index(drop=True)['t_date'][0]
                except:
                    latest_date_week = end_date
                latest_date_i = fund_data[fund_data['t_date'] >= latest_date_week].index[0]
            else:
                latest_date_i = fund_data[fund_data['t_date'] >= latest_date].index[0]
            fund_data = fund_data.fillna(method='ffill')

            # 最新净值之后不填充空置
            if (
                    len(fund_data) > latest_date_i + 1
            ) and (
                    fund_data['t_date'][latest_date_i] <= cal_spe['t_date'].tolist()[-2]
            ):
                fund_data.loc[latest_date_i + 1:, fund_name] = np.nan

            if freq in ['month', 'monthly']:
                if all_aligned:
                    # 算月度净值时先统一成周净值再转换成日净值，去掉部分日净值以同一所有产品净值频率，不直接按日净值转换为月净值
                    fund_data = pd.merge(cal_weekly, fund_data, on='t_date', how='left')
                try:
                    nav_end_date = fund_data[fund_data[fund_name] > 0]['t_date'].tolist()[-1]
                except IndexError:
                    nav_end_date = fund_data['t_date'].tolist()[0]
                fund_data = pd.merge(cal, fund_data, on='t_date', how='left')
                fund_data = fund_data.fillna(method='ffill')
                if cal_spe['t_date'].tolist()[-1] > nav_end_date:
                    date_i = cal_spe[cal_spe['t_date'] > nav_end_date]['t_date'].tolist()[0]
                    fund_data.loc[fund_data[fund_data['t_date'] >= date_i].index[0]:, fund_name] = np.nan
                else:
                    pass

        fund_data = pd.merge(cal_spe, fund_data, on='t_date', how='left')

        # 剔除产品运行前期净值长期横盘情况
        if drop_1:
            for d in range(len(fund_data)):
                if fund_data.iloc[d:d + 1][fund_name][d] == 1 and fund_data.iloc[d + 1:d + 2][fund_name][d + 1] != 1:
                    fund_data = fund_data.iloc[d:].reset_index(drop=True)
                    break
        try:
            i_dates.append(fund_data['t_date'][fund_data[fund_name] > 0].tolist()[0])
        except IndexError:
            pass
            # i_dates.append(np.nan)
        cal_all = pd.merge(cal_all, fund_data, on='t_date', how='left')

    i_date = np.nanmin(i_dates)
    if i_date > first_date:
        first_date = i_date
    return cal_all[cal_all['t_date'] >= first_date].reset_index(drop=True)


# 输入产品列表，输出对应产品的周超额净值或月超额净值
# 输入：DataFrame，输出：DataFrame
# 输入的DataFrame中需要包含对应benchmark的code列
# 如果first_date设置的太早会自动剔除前期空值
# 指增产品只对净值大于1的序列进行计算，防止净值从1开始跳跃过大（此条取消）
def load_funds_alpha(
        fund_list, first_date=datetime.now().date(), end_date=datetime.now().date(), freq='w',
        fillna=True, all_aligned=False,
        db_path='', cal_db_path='', index_table='stocks_index_ts', print_info=False
):
    cal = load_calendar(end_date=end_date, db_path=cal_db_path)
    cal_weekly = load_calendar_extra(freq='w', end_date=end_date, db_path=cal_db_path)

    cal_spe = load_calendar_extra(freq=freq, end_date=end_date, db_path=cal_db_path)
    cal_eav = cal_spe.copy()
    cal_excess = cal_spe.copy()

    if len(fund_list) == 1:
        sql_l = 'code=\'' + fund_list['code'][0] + '\''
    else:
        sql_l = 'code in ' + str(tuple(fund_list['code']))

    fund_data_all = pd.read_sql_query(
        'select * from fund_data where ' + sql_l + ' and t_date<=' + end_date.strftime('%Y%m%d')
        + ' order by t_date',
        create_engine(db_path)
    )[['t_date', 'nav', 'code']]
    fund_data_all['code'] = fund_data_all['code'].apply(lambda x: x.lower())

    for i in range(len(fund_list)):
        fund_code = fund_list['code'][i].lower()
        fund_name = fund_list['name'][i]
        benchmark = fund_list['benchmark'][i]
        if print_info:
            print('Loading ' + fund_name + ' ' + freq + ' 超额；')
        # if first_date > fund_list['first_date'][i]:
        #     first_date = fund_list['first_date'][i]

        fund_data = fund_data_all[
            fund_data_all['code'] == fund_code
            ][['t_date', 'nav']].rename(columns={'nav': fund_name})
        fund_data = fund_data.drop_duplicates(['t_date'], keep='first').reset_index(drop=True)

        # 衍复指增三号特殊处理
        if fund_code == 'SJH866'.lower():
            fund_data = fund_data[fund_data['t_date'] >= datetime(2020, 2, 14).date()].reset_index(drop=True)

        # 天眼赛能特殊处理
        if fund_code == 'P22984'.lower():
            fund_data = fund_data[fund_data['t_date'] >= datetime(2019, 8, 2).date()].reset_index(drop=True)

        benchmark_data = pd.read_sql_query(
            'select t_date, close from ' + index_table
            + ' where t_date<=' + end_date.strftime('%Y%m%d')
            + ' and code="' + benchmark + '" order by t_date',
            create_engine(cal_db_path)
        ).rename(columns={'close': 'bm'})

        # fund_data = pd.merge(fund_data, benchmark_data, on='t_date', how='left')

        fund_aligned = pd.merge(cal, fund_data, on='t_date', how='left')
        if fillna:
            latest_date_i = fund_aligned[fund_aligned[fund_name] > 0].index[-1]
            fund_aligned = fund_aligned.fillna(method='ffill')

            # 最新净值之后不填充空置
            if len(fund_aligned) > latest_date_i + 1:
                fund_aligned.loc[latest_date_i + 1:, fund_name] = np.nan

            if freq in ['month', 'monthly']:
                if all_aligned:
                    # 算月度净值时先统一成周净值再转换成日净值，去掉部分日净值以同一所有产品净值频率，不直接按日净值转换为月净值
                    fund_aligned = pd.merge(cal_weekly, fund_aligned, on='t_date', how='left')
                fund_aligned = pd.merge(cal, fund_aligned, on='t_date', how='left')
                fund_aligned = fund_aligned.fillna(method='ffill')

        fund_aligned = pd.merge(cal_spe['t_date'], fund_aligned, on='t_date', how='left')

        # 剔除产品运行前期净值长期横盘情况
        # for d in range(len(fund_aligned)):
        #     if (
        #             fund_aligned.iloc[d:d + 1][fund_name][d] == 1
        #             and fund_aligned.iloc[d + 1:d + 2][fund_name][d + 1] != 1
        #     ):
        #         fund_aligned = fund_aligned.iloc[d + 1:].reset_index(drop=True)
        #         break

        fund_aligned = pd.merge(fund_aligned, benchmark_data, on='t_date', how='left')
        fund_aligned['ret'] = fund_aligned[fund_name] / fund_aligned[fund_name].shift(1) - 1
        fund_aligned['bm_ret'] = fund_aligned['bm'] / fund_aligned['bm'].shift(1) - 1
        fund_aligned['excess'] = fund_aligned['ret'] - fund_aligned['bm_ret']
        fund_aligned['eav'] = (fund_aligned['excess'] + 1).cumprod()
        fund_aligned.loc[fund_aligned[fund_aligned['eav'] > 0].index[0] - 1, 'eav'] = 1

        cal_spe = pd.merge(cal_spe, fund_aligned[['t_date', fund_name]], on='t_date', how='left')
        cal_eav = pd.merge(
            cal_eav, fund_aligned[['t_date', 'eav']].rename(columns={'eav': fund_name}), on='t_date', how='left'
        )
        cal_excess = pd.merge(
            cal_excess,
            fund_aligned[['t_date', 'excess']].rename(columns={'excess': fund_name}),
            on='t_date',
            how='left'
        )

    i_date = fund_list['first_date'].min()
    if i_date > first_date:
        first_date = i_date

    result = {
        'nav': cal_spe[cal_spe['t_date'] >= first_date].reset_index(drop=True),
        'eav': cal_eav[cal_eav['t_date'] >= first_date].reset_index(drop=True),
        'excess': cal_excess[cal_excess['t_date'] >= first_date].reset_index(drop=True)
    }
    return result


# 跟踪池标的列表传入HBDB
def fund_pool_to_hb(fund_df, table='fund_pool', sql_path='', sql_ip='', sql_user='', sql_pass='', database=''):
    sql_l = '''
    (
    id bigint not null AUTO_INCREMENT,
    name  varchar(100),
    type0  varchar(100),
    type1  varchar(100),
    primary key (id)
    )
    '''
    db = pymysql.connect(sql_ip, sql_user, sql_pass, database)
    cursor = db.cursor()
    try:
        sql = 'create table `' + table + '` ' + sql_l + ' comment=\'量化产品跟踪池\''
        cursor.execute(sql)
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    cursor.execute('truncate table ' + table)
    print('Clear ' + table)
    db.close()
    fund_df.to_sql(table, sql_path, if_exists='append', index=False)


# 跟踪池标的净值传入HBDB
def fund_data_to_hb(path_local, path_hb, sql_hb, database, tables=None):
    # engine_work = create_engine(sql_write_path_work['work'])
    # engine_hb = create_engine(sql_write_path_hb['work'])

    if tables is None:
        tables = [
            'fund_data',
            'fund_list',
        ]

    for t in tables:
        print(t)

        id_in_hb = pd.read_sql_query(
            'select `id` from ' + t + ' order by `id` desc', path_hb
        )
        id_in_local = pd.read_sql_query(
            'select `id` from ' + t + ' order by `id` desc', path_local
        )

        id_hb_diff = set(id_in_hb['id']).difference(set(id_in_local['id']))
        if len(id_hb_diff) > 0:
            db_hb = pymysql.connect(sql_hb['ip'], sql_hb['user'], sql_hb['pass'], database)
            cursor = db_hb.cursor()
            if len(id_hb_diff) > 1:
                cursor.execute(
                    'delete from ' + t + ' where `id` in ' + str(tuple(id_hb_diff))
                )
            else:
                cursor.execute(
                    'delete from ' + t + ' where `id`=' + str(list(id_hb_diff)[0])
                )
            db_hb.commit()
            db_hb.close()
            print('\tdelete: ' + str(len(id_hb_diff)))

        data_hb_last_one = pd.read_sql_query(
            'select `id` from ' + t + ' order by `id` desc limit 1', path_hb
        )
        if len(data_hb_last_one) > 0:
            id_num = data_hb_last_one['id'][0]
        else:
            id_num = -1

        data_work_new = pd.read_sql_query(
            'select * from ' + t + ' where `id`>' + str(id_num), path_local
        )

        data_work_new.to_sql(t, path_hb, if_exists='append', index=False)

        print('\tnew data: ' + str(len(data_work_new)))



