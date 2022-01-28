import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hbshare.quant.CChen.cons import properties_stk_k, db, db_tables
from hbshare.quant.CChen.func import generate_table
from hbshare.quant.CChen.sql_l import sql_quote
import hbshare as hbs
import pymysql

pymysql.install_as_MySQLdb()

page_size_con = 49999


def ch_stk_quote_to_local(db_path, sql_info, table='ch_stk_quote', page_size=None):
    if page_size is None:
        page_size = page_size_con

    from_table = db_tables['ch_stocks_daily_quote']

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_quote,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='from ' + from_table
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_date_in_db = pd.read_sql_query(
        'select distinct `TDATE` from ' + table + ' order by `TDATE` desc limit 1', db_path
    )
    if len(latest_date_in_db) > 0:
        latest_date = latest_date_in_db['TDATE'][0]
    else:
        latest_date = datetime(2000, 12, 31).date()

    print('\tLatest date in db: ' + str(latest_date))
    while 1:
        latest_date += timedelta(days=1)
        if latest_date > datetime.now().date():
            print('\t\t' + 'No more new quote data')
            return
        sql = (
                'select '
                'TDATE, '
                'SYMBOL, '
                'EXCHANGE, '
                'LCLOSE, '
                'TOPEN, '
                'TCLOSE, '
                'HIGH, '
                'LOW, '
                'VOTURNOVER, '
                'VATURNOVER, '
                'AVGPRICE, '
                'CHG, '
                'PCHG, '
                'PRANGE, '
                'MCAP, '
                'TCAP '
                'from ' + from_table
                + ' where  TDATE=' + latest_date.strftime('%Y%m%d')
        )

        data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
        df = pd.DataFrame(data['data'])
        if len(df) == 0:
            continue
        df['TDATE'] = pd.to_datetime(df['TDATE'].astype(str)).dt.date
        df = df.drop(columns=['ROW_ID']).rename(
            columns={
                'TOPEN': 'OPEN',
                'TCLOSE': 'CLOSE',
                'VOTURNOVER': 'VOLUME',
                'VATURNOVER': 'AMOUNT'
            }
        )
        df.to_sql(table, db_path, if_exists='append', index=False)
        print('\tNew data: ' + str(len(df)) + ', date: ' + latest_date.strftime('%Y-%m-%d'))


def trade_calendar(start_date=None, end_date=None, page_size=None):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()
    if end_date is None:
        end_date = datetime.now().date()
    if page_size is None:
        page_size = page_size_con

    sql = 'select distinct TDATE from ' + db_tables['ch_stocks_daily_quote'] \
          + ' where TDATE<=' + end_date.strftime('%Y%m%d') \
          + ' and TDATE>=' + start_date.strftime('%Y%m%d') \
          + ' order by TDATE'
    data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
    if data['pages'] > 1:
        for p in range(2, data['pages'] + 1):
            data['data'] = data['data'] + hbs.db_data_query(db=db, sql=sql, page_size=page_size, page_num=p)['data']

    return pd.to_datetime(pd.DataFrame(data['data'])['TDATE'], format='%Y%m%d').dt.date.tolist()


def daily_ret_by_vol(start_date=None, end_date=None, min_vol=10000, page_size=None):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()
    if end_date is None:
        end_date = datetime.now().date()
    if page_size is None:
        page_size = page_size_con

    sql = 'select ' + ', '.join(properties_stk_k) + ' from ' + db_tables['ch_stocks_daily_quote'] \
          + ' where TDATE<=' + end_date.strftime('%Y%m%d') \
          + ' and TDATE>=' + start_date.strftime('%Y%m%d') \
          + ' and VOTURNOVER>=' + str(min_vol) + ' order by TDATE, SYMBOL'

    data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
    if data['pages'] > 1:
        for p in range(2, data['pages'] + 1):
            data['data'] = data['data'] + hbs.db_data_query(db=db, sql=sql, page_size=page_size, page_num=p)['data']

    return data


def load_index(index_list, start_date=None, end_date=None, table=db_tables['index_daily_quote'], page_size=None):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()
    if end_date is None:
        end_date = datetime.now().date()
    if page_size is None:
        page_size = page_size_con

    if len(index_list) == 1:
        index_sql = '=\'' + index_list[0] + '\''
    elif len(index_list) > 1:
        index_sql = ' in ' + str(tuple(index_list))
    else:
        index_sql = '=\'000905\''

    sql = 'select ' \
          'JYRQ as tdate, ' \
          'ZQDM as code, ' \
          'QSPJ as pre_close, ' \
          'KPJG as open, ' \
          'SPJG as close, ' \
          'ZGJG as high, ' \
          'ZDJG as low, ' \
          'CJJS as amount,' \
          'ZDFD as PCHG from ' + table \
          + ' where JYRQ<=' + end_date.strftime('%Y%m%d') \
          + ' and JYRQ>=' + start_date.strftime('%Y%m%d') \
          + ' and ZQDM' + index_sql

    data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
    if data['pages'] > 1:
        for p in range(2, data['pages'] + 1):
            data['data'] = data['data'] + hbs.db_data_query(db=db, sql=sql, page_size=page_size, page_num=p)['data']

    return pd.DataFrame(data['data'])


def load_stk(start_date=None, end_date=None, table=db_tables['stocks_daily_quote'], page_size=None):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()
    if end_date is None:
        end_date = datetime.now().date()
    if page_size is None:
        page_size = page_size_con

    sql = 'select ' \
          'JYRQ, ' \
          'ZQDM as code, ' \
          'QSPJ as pre_close, ' \
          'KPJG as open, ' \
          'SPJG as close, ' \
          'ZGJG as high, ' \
          'ZDJG as low, ' \
          'HSBL as TURNOVER, ZDFD as PCHG from ' + table \
          + ' where JYRQ<=' + end_date.strftime('%Y%m%d') \
          + ' and JYRQ>=' + start_date.strftime('%Y%m%d') \
          + ' and (ZQDM like \'6%\' or ZQDM like \'3%\' or ZQDM like \'0%\') ' \
          + ' order by JYRQ, ZQDM'

    data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
    if data['pages'] > 1:
        for p in range(2, data['pages'] + 1):
            data['data'] = data['data'] + hbs.db_data_query(db=db, sql=sql, page_size=page_size, page_num=p)['data']

    return pd.DataFrame(data['data'])


def load_stk_local(sql_path, start_date=None, end_date=None, table='ch_stk_quote'):
    if start_date is None:
        start_date = datetime(2010, 1, 1).date()
    if end_date is None:
        end_date = datetime.now().date()

    data = pd.read_sql_query(
        'select * from ' + table
        + ' where TDATE<=' + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + start_date.strftime('%Y%m%d')
        + ' and (SYMBOL like \'6%\' or SYMBOL like \'3%\' or SYMBOL like \'0%\') '
        + ' order by TDATE, SYMBOL',
        sql_path
    )

    return data


def index_win(index_list, index_data, stk_data, freq='D'):

    cal = pd.DataFrame(pd.to_datetime(stk_data['TDATE'].drop_duplicates().sort_values()))
    cal = cal.set_index('TDATE', drop=False).resample(freq).last()
    cal = cal[~np.isnan(cal['TDATE'])]

    if len(cal) <= 1:
        print('No new data for frequency: ' + freq)
        return

    index_data['TDATE'] = pd.to_datetime(index_data['TDATE']).dt.date

    win_data = pd.DataFrame()

    for t in range(len(cal) - 1):
        t_date = cal.iloc[t][0].date()
        print(t_date)
        if t == 0:
            stk_data_t = stk_data[stk_data['TDATE'] <= t_date].reset_index(drop=True)
            index_data_t = index_data[index_data['TDATE'] <= t_date].reset_index(drop=True)
        else:
            stk_data_t = stk_data[
                np.array(stk_data['TDATE'] <= t_date)
                & np.array(stk_data['TDATE'] > cal.iloc[t - 1][0].date())
            ].reset_index(drop=True)
            index_data_t = index_data[
                np.array(index_data['TDATE'] <= t_date)
                & np.array(index_data['TDATE'] > cal.iloc[t - 1][0].date())
            ].reset_index(drop=True)

        stk_data_t_p = stk_data_t.pivot(index='TDATE', columns='CODE', values='PCHG')
        stk_data_t_p = (stk_data_t_p.fillna(0) + 100) / 100
        stk_data_t_p_r = (stk_data_t_p.prod() - 1) * 100

        index_data_t_p = index_data_t.pivot(index='TDATE', columns='CODE', values='PCHG')
        index_data_t_p = (index_data_t_p.fillna(0) + 100) / 100
        index_data_t_r = (index_data_t_p.prod() - 1) * 100

        stk_r_mean = stk_data_t_p_r.mean()
        stk_r_median = stk_data_t_p_r.median()
        stk_r_99 = stk_data_t_p_r.quantile(0.99)
        stk_r_95 = stk_data_t_p_r.quantile(0.95)
        stk_r_75 = stk_data_t_p_r.quantile(0.75)
        stk_r_25 = stk_data_t_p_r.quantile(0.25)
        stk_r_5 = stk_data_t_p_r.quantile(0.05)
        stk_r_1 = stk_data_t_p_r.quantile(0.01)

        stk_win_r = {}
        stk_win_n = {}
        for i in index_list:
            stk_win_r[i] = stk_data_t_p_r - index_data_t_r[i]
            stk_win_n[i + 'w'] = (stk_win_r[i] > 0).sum()

        result_dict = {
            'TDATE': t_date,
            'MEAN': stk_r_mean,
            'MEDIAN': stk_r_median,
            'Q99': stk_r_99,
            'Q95': stk_r_95,
            'Q75': stk_r_75,
            'Q25': stk_r_25,
            'Q5': stk_r_5,
            'Q1': stk_r_1,
            'STKN': stk_data_t_p_r.count()
        }
        result_dict.update(stk_win_n)
        result_dict.update(index_data_t_r)
        win_data = win_data.append(result_dict, sort=True, ignore_index=True)
        # win_data

    return win_data


if __name__ == '__main__':
    from db_cons import sql_write_path_work, sql_user_work
    # main = load_index(index_list='000905', start_date=datetime(2021, 10, 1))
    # main2 = load_stk(start_date=datetime(2021, 10, 1))

    # start_date = datetime(2021, 1, 1)
    # end_date = datetime.now()
    # index_list = [
    #     '000300',
    #     '000905'
    # ]
    # index_data = load_index(index_list=index_list, start_date=start_date, end_date=end_date)
    # stk_data = load_stk_local(start_date=start_date, end_date=end_date).rename(columns={'SYMBOL': 'CODE'})
    #
    # aa = index_win(
    #     index_data=index_data,
    #     stk_data=stk_data,
    #     index_list=index_list,
    #     freq='D'
    # )
    ch_stk_quote_to_local(db_path=sql_write_path_work['daily'], sql_info=sql_user_work)
    # print()


