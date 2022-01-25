from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from hbshare.quant.CChen.cta_factor.factor_func import factor_compute
from hbshare.quant.CChen.cta_factor.factor_algo import (
    carry, tsmom, tsrev, xsmom, xsrev, tswr, xswr, mr, mrchg, tsmr, tsbasismom, xsbasismom, tspoichg, xspoichg, xssigma
)


def run(sql_path, sql_info):
    start_date = datetime(2010, 1, 1).date()
    # end_date = datetime(2021, 4, 9).date()
    end_date = datetime.now().date()

    window_days_list = [1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 90, 100, 150, 200, 250]
    liq_d = 20

    table = 'hsjy_fut_com_index'
    table_wr = 'hsjy_fut_wr'
    table_mr = 'hsjy_fut_memberrank'
    table_contracts_info = 'hsjy_fut_info_c'
    table_raw = 'hsjy_fut_com'

    data = pd.read_sql_query(
        'select * from ' + table + ' where TDATE<='
        + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + (start_date - timedelta(days=500)).strftime('%Y%m%d')
        + ' order by TDATE',
        sql_path
    )
    data_wr0 = pd.read_sql_query(
        'select TDATE, EXCHANGE, PCODE, PNAME, WRQCURRENT from ' + table_wr + ' where TDATE<='
        + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + (start_date - timedelta(days=500)).strftime('%Y%m%d')
        + ' and FREQ=5 order by TDATE',
        sql_path
    )
    calendar = data[['TDATE']].sort_values(by='TDATE').drop_duplicates().reset_index(drop=True)
    data_wr = pd.DataFrame()
    for e in data['EXCHANGE'].drop_duplicates().tolist():
        PCODEs = data[data['EXCHANGE'] == e]['PCODE'].drop_duplicates().tolist()
        for p in PCODEs:
            data_wr_p = data_wr0[np.array(data_wr0['EXCHANGE'] == e) & np.array(data_wr0['PCODE'] == p)]
            data_wr_p = pd.merge(calendar, data_wr_p, on='TDATE', how='left').fillna(method='ffill')
            data_wr_p = data_wr_p[data_wr_p['WRQCURRENT'] >= 0].reset_index(drop=True)
            data_wr = pd.concat([data_wr, data_wr_p])
    data_wr = data_wr.reset_index(drop=True)

    data_mr = pd.read_sql_query(
        'select TDATE, CCODE, INDICATORCODE as SIDE, sum(INDICATORVOL) as MR, sum(INDICATORCHG) as MRCHG from ' + table_mr
        + ' where TDATE<=' + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + (start_date - timedelta(days=500)).strftime('%Y%m%d')
        + ' and INDICATORCODE in (3, 4) GROUP BY INDICATORCODE, TDATE, CCODE order by TDATE, CCODE, INDICATORCODE',
        sql_path
    )
    data_info = pd.read_sql_query(
        'select * from ' + table_contracts_info, sql_path
    )
    data_mr = pd.merge(data_mr, data_info[['CCODE', 'EXCHANGE', 'PCODE']], on='CCODE', how='left')
    data_mr = data_mr.groupby(by=['TDATE', 'SIDE', 'EXCHANGE', 'PCODE']).sum().reset_index()
    data_mr['SIDE'] = data_mr['SIDE'].apply(lambda x: 1 if x == 3 else (-1 if x == 4 else 0))
    data_mr['MR'] = data_mr['MR'] * data_mr['SIDE']
    data_mr['MRCHG'] = data_mr['MRCHG'] * data_mr['SIDE']

    data_contracts = pd.read_sql_query(
        'select * from ' + table_raw + ' where CCODE in ' + str(tuple(np.unique(data[['CCODE', 'CCODE2']].dropna())))
        + ' order by CCODE, TDATE',
        sql_path
    )

    factor_compute(
        window_days_list=[10, 20, 30, 50, 90, 150, 250], hedge_ratio_list=[50, 75], data=data, factor_func=xssigma,
        liq_days=liq_d, data_raw=data_contracts, sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list[:10], hedge_ratio_list=[50, 75], data=data, factor_func=xsbasismom,
        liq_days=liq_d, data_raw=data_contracts, sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list[:10], data=data, factor_func=tsbasismom, liq_days=liq_d,
        data_raw=data_contracts, sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=[20, 50], hedge_ratio_list=[50, 60, 70, 80, 90], data=data, factor_func=carry, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, data=data, factor_func=tsmom, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, data=data, factor_func=tsrev, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, hedge_ratio_list=[50, 75], data=data, factor_func=xsmom, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, hedge_ratio_list=[50, 75], data=data, factor_func=xsrev, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, data=data, factor_func=tspoichg, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list, hedge_ratio_list=[50, 75], data=data, factor_func=xspoichg, liq_days=liq_d,
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list,
        hedge_ratio_list=[50, 75],
        data=data,
        data_wr=data_wr,
        factor_func=xswr,
        liq_days=liq_d,
        price_field='OPEN',
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list,
        data=data,
        data_wr=data_wr,
        factor_func=tswr,
        liq_days=liq_d,
        price_field='OPEN',
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list,
        data=data,
        data_mr=data_mr,
        factor_func=mr,
        liq_days=liq_d,
        price_field='OPEN',
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list,
        data=data,
        data_mr=data_mr,
        factor_func=mrchg,
        liq_days=liq_d,
        price_field='OPEN',
        sql_info=sql_info, to_sql_path=sql_path
    )

    factor_compute(
        window_days_list=window_days_list,
        data=data,
        data_mr=data_mr,
        factor_func=tsmr,
        liq_days=liq_d,
        price_field='OPEN',
        sql_info=sql_info, to_sql_path=sql_path
    )


