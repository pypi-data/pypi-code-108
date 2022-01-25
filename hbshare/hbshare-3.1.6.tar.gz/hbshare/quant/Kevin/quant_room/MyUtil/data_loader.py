"""
取数function模块
"""
import hbshare as hbs
import pandas as pd
import datetime
from sqlalchemy import create_engine

sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "work"
}
engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'],
                                                        sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])


def get_trading_day_list(start_date, end_date, frequency='day'):
    """
    获取日期序列
    """
    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
        start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
    df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

    calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    if frequency == "day":
        trading_day_list = calendar_df[calendar_df['isOpen'] == 1]['calendarDate'].tolist()
    elif frequency == "week":
        trading_day_list = calendar_df[calendar_df['isWeekEnd'] == 1]['calendarDate'].tolist()
    elif frequency == 'month':
        trading_day_list = calendar_df[calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
    else:
        trading_day_list = calendar_df['calendarDate'].tolist()

    return trading_day_list


def get_fund_nav_from_sql(start_date, end_date, fund_dict):
    """
    获取db的私募基金净值数据
    """
    nav_series_list = []
    for name, fund_id in fund_dict.items():
        sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                     "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                     "and a.jjzt not in ('3') " \
                     "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                     "order by b.jzrq".format(fund_id, start_date, end_date)
        res = hbs.db_data_query("highuser", sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
        data.name = name
        nav_series_list.append(data)
    df = pd.concat(nav_series_list, axis=1).sort_index()

    return df


def get_fund_nav_from_work(start_date, end_date, fund_id):
    sql_script = "SELECT name, t_date, nav FROM fund_data where " \
                 "t_date >= {} and t_date <= {} and code = '{}'".format(start_date, end_date, fund_id)
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['t_date'] = data['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

    return data