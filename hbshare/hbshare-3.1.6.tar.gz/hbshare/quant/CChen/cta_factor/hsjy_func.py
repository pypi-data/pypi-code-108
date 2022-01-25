import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from hbshare.quant.CChen.func import generate_table
import pymysql
from hbshare.quant.CChen.cons import (
    HSJY_EXCHANGE_INE,
    HSJY_EXCHANGE_CZCE,
    HSJY_EXCHANGE_SHFE,
    HSJY_EXCHANGE_DCE
)

sql_l = '''(
    `ID`  bigint not null,
    `TDATE`  date not null,
    `EXCHANGE` int,
    `PCODE` int,
    `CCODE` int comment\'当日对应主力合约HSJY代码\',
    `CCODE2` int comment\'当日对应次主力合约HSJY代码\',
    `SYEAR` int,
    `SMONTH` int,
    `DDATE` date comment\'当日主力合约交割日\',
    `LDATE` date comment\'当日主力合约最后交易日\',
    `OPEN` float,
    `HIGH` float,
    `LOW` float,
    `CLOSE` float,
    `RY` float comment\'当日展期收益率，使用当日主力与次主力构建\',
    `VOL` int comment\'对应单个合约当日成交量\',
    `OI` int comment\'对应单个合约当日持仓量\',
    `AMT` double comment\'对应单个合约当日成交额\',
    `PVOL` int comment\'对应品种当日全部合约成交量\',
    `POI` int comment\'对应品种当日全部合约持仓量\',
    `PAMT` double comment\'对应品种当日全部合约成交额\',
    primary key (`ID`)
    )
    '''


def hsjy_fut_index(
        db_path, sql_info, exchanges=None, table=None, data_table=None, oi_days=5
):
    if table is None:
        table = 'hsjy_fut_com_index'

    if data_table is None:
        data_table = 'hsjy_fut_com'

    if exchanges is None:
        exchanges = [HSJY_EXCHANGE_SHFE, HSJY_EXCHANGE_DCE, HSJY_EXCHANGE_CZCE, HSJY_EXCHANGE_INE]

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='HSJY commodities index'
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    engine = create_engine(db_path)

    calendar_all = pd.read_sql_query(
        'select distinct TDATE from ' + data_table + ' order by TDATE', engine
    )['TDATE'].tolist()
    for e in exchanges:
        existing_p_code = pd.read_sql_query(
            'select distinct `PCODE` from ' + data_table + ' where `EXCHANGE`=' + str(e), engine
        )
        for i in range(len(existing_p_code)):
            code_p = existing_p_code['PCODE'][i]
            # e = 15
            # code_p = 360
            print(str(e) + ', ' + str(i + 1) + ' / ' + str(len(existing_p_code)) + ', ' + str(code_p))
            existing_index = pd.read_sql_query(
                'select * from ' + table + ' where `PCODE`=\'' + str(code_p) + '\' and `EXCHANGE`=' + str(e)
                + ' order by `TDATE` desc limit 1',
                engine
            )
            if len(existing_index) > 0:
                last_date = existing_index['TDATE'][0]
                last_close = existing_index['CLOSE'][0]
            else:
                last_date = calendar_all[0]
                last_close = 1000

            data = pd.read_sql_query(
                'select * from ' + data_table + ' where `TDATE`>='
                + (calendar_all[max(0, calendar_all.index(last_date) - oi_days)]).strftime('%Y%m%d')
                + ' and `PCODE`=\'' + str(code_p) + '\' and `EXCHANGE`=' + str(e)
                + ' order by `TDATE`', engine
            )
            data_info = data[['CCODE', 'LDATE']].drop_duplicates(subset=['CCODE']).reset_index(drop=True)
            # data_info = pd.read_sql_query(
            #     'select * from ' + info_table + ' where `PCODE`=\'' + str(code_p) + '\' and `EXCHANGE`=' + str(e),
            #     engine
            # )
            calendar = data['TDATE'].drop_duplicates().tolist()
            if len(calendar) == 0:
                continue
            if calendar[-1] <= last_date:
                continue

            if last_date == calendar_all[0]:
                last_date = calendar[oi_days]
                data_index0 = pd.DataFrame(
                    {
                        'TDATE': last_date,
                        'EXCHANGE': data['EXCHANGE'][0],
                        'PCODE': code_p,
                        'CLOSE': last_close,
                        'DDATE': None,
                        'LDATE': None,
                        'CCODE': None,
                        'CCODE2': None,
                    }, index=[0]
                )
                existing_index = data_index0
                data_index0['ID'] = (
                        (data_index0['EXCHANGE'] * 1000 + data_index0['PCODE']) * 100000000
                        + data_index0['TDATE'].apply(lambda x: int(x.strftime('%Y%m%d')))
                )
                data_index0.to_sql(table, engine, if_exists='append', index=False)

            date_l = []
            ccode_l = [existing_index['CCODE'][0]]
            ccode2_l = [existing_index['CCODE2'][0]]
            ddate_l = [existing_index['DDATE'][0]]
            ldate_l = [existing_index['LDATE'][0]]
            open_l = []
            high_l = []
            low_l = []
            close_l = [last_close]
            ry_l = []
            vol_l = []
            oi_l = []
            amt_l = []
            pvol_l = []
            poi_l = []
            pamt_l = []
            for d in range(calendar.index(last_date) + 1, len(calendar)):
                if calendar[d] == data['LDATE'].max():
                    print(str(code_p) + ' terminated')
                    break

                data_today = data[data['TDATE'] == calendar[d]]

                # 前前交易日收盘后根据过去oi_days交易日平均持仓量确定主力合约，
                # 前个交易日收盘进入合约，
                # 当天开始计算涨跌
                data_oi_all = pd.merge(data[
                                           np.array(data['TDATE'] < calendar[d - 1])
                                           & np.array(data['TDATE'] >= calendar[d - oi_days - 1])
                                           ].fillna(0), data_today[['CCODE']], on='CCODE', how='inner'
                                       )

                data_oi = pd.merge(
                    data_oi_all[
                        ['CCODE', 'OI']
                    ].groupby('CCODE').mean().sort_values(by=['OI'], ascending=False).reset_index(),
                    data_info, on='CCODE', how='left'
                )

                # 还有7日进入交割月的合约不作为主力合约备选
                data_oi['date_check'] = data_oi['LDATE'].apply(
                    lambda x:
                    1 if x.year * 100 + x.month > (
                            (calendar[d] + timedelta(days=7)).year * 100 + (calendar[d] + timedelta(days=7)).month
                        )
                    else 0
                )
                data_oi = data_oi[
                    np.array(data_oi['date_check'] == 1)
                    & np.array(data_oi['OI'] > 0)
                ][['CCODE', 'OI', 'LDATE']].reset_index(drop=True)

                if len(data_oi) > 1:
                    ccode = data_oi['CCODE'][0]
                    ccode2 = data_oi['CCODE'][1]
                elif len(data_oi) == 1:
                    ccode = data_oi['CCODE'][0]
                    ccode2 = data_oi['CCODE'][0]
                else:
                    ccode = ccode_l[-1]
                    ccode2 = ccode2_l[-1]

                data_c = data_today[data_today['CCODE'] == ccode].reset_index(drop=True)

                if len(data_c) == 0:
                    # 合约断档，即类似燃油停市后重新上市情况
                    date_l.append(calendar[d])
                    ccode_l.append(None)
                    ccode2_l.append(None)
                    ddate_l.append(None)
                    ldate_l.append(None)
                    open_l.append(close_l[-1])
                    high_l.append(close_l[-1])
                    low_l.append(close_l[-1])
                    close_l.append(close_l[-1])
                    vol_l.append(None)
                    oi_l.append(None)
                    amt_l.append(None)
                    pvol_l.append(None)
                    poi_l.append(None)
                    pamt_l.append(None)
                    ry_l.append(None)
                    print(
                        str(e) + ', ' + str(i + 1) + ' / ' + str(len(existing_p_code)) + ', '
                        + str(code_p) + '\tCurrent date: ' + str(calendar[d])
                        + '\t No contracts'
                    )
                else:
                    # 主力合约不转移至老合约
                    if len(ddate_l) > 0 and ddate_l[-1] is not None:
                        if data_c['DDATE'][0] < ddate_l[-1]:
                            ccode = ccode_l[-1]
                            code_list = data_oi['CCODE'].tolist()
                            if ccode in code_list:
                                code_list.pop(code_list.index(ccode))
                            ccode2 = code_list[0]

                    data_c = data[
                        np.array(data['TDATE'] <= calendar[d])
                        & np.array(data['TDATE'] >= calendar[d - 3])
                        & np.array(data['CCODE'] == ccode)
                        ].sort_values(by='TDATE', ascending=False).reset_index(drop=True)

                    # 获取上个交易日对应主力合约本交易日的情况，换主力合约时用
                    # 即换主力合约时通过两个交易日进行换仓，每个交易日换50%仓位
                    if ccode_l[-1] is not None:
                        data_c0 = data[
                            np.array(data['TDATE'] <= calendar[d])
                            & np.array(data['TDATE'] >= calendar[d - 3])
                            & np.array(data['CCODE'] == ccode_l[-1])
                            ].sort_values(by='TDATE', ascending=False).reset_index(drop=True)
                        if len(data_c0) <= 1:
                            data_c0 = data_c
                    else:
                        data_c0 = data_c

                    data_c_sub = data[
                        np.array(data['TDATE'] == calendar[d]) & np.array(data['CCODE'] == ccode2)
                    ].reset_index(drop=True)

                    if len(data_c_sub) == 0:
                        data_c_sub = pd.DataFrame(
                            {
                                'CLOSE': np.nan,
                                'DDATE': None
                            }, index=[0]
                        )

                    date_l.append(calendar[d])
                    ccode_l.append(ccode)
                    ccode2_l.append(ccode2)
                    ddate_l.append(data_c['DDATE'][0])
                    ldate_l.append(data_c['LDATE'][0])

                    if len(data_c) > 1 and data_c['OPEN'][0] > 0 and data_c['CLOSE'][1] > 0:
                        open_r = data_c['OPEN'][0] / data_c['CLOSE'][1] - 1
                    else:
                        open_r = 0
                    if len(data_c0) > 1 and data_c0['OPEN'][0] > 0 and data_c0['CLOSE'][1] > 0:
                        open_r0 = data_c0['OPEN'][0] / data_c0['CLOSE'][1] - 1
                    else:
                        open_r0 = 0
                    open_l.append((open_r / 2 + open_r0 / 2 + 1) * close_l[-1])

                    if len(data_c) > 1 and data_c['CLOSE'][0] > 0 and data_c['CLOSE'][1] > 0:
                        close_r = data_c['CLOSE'][0] / data_c['CLOSE'][1] - 1
                    else:
                        close_r = 0
                    if len(data_c0) > 1 and data_c0['CLOSE'][0] > 0 and data_c0['CLOSE'][1] > 0:
                        close_r0 = data_c0['CLOSE'][0] / data_c0['CLOSE'][1] - 1
                    else:
                        close_r0 = 0
                    close_l.append(
                        (close_r / 2 + close_r0 / 2 + 1) * close_l[-1]
                    )

                    print(
                        str(e) + ', ' + str(i + 1) + ' / ' + str(len(existing_p_code)) + ', '
                        + str(code_p) + '\tCurrent date: ' + str(calendar[d])
                        + '\t' + str(ccode) + '\t' + str(ccode2)
                        + '\t Delivery date: ' + str(data_c['DDATE'][0])
                        + '\t Delivery date2: ' + str(data_c_sub['DDATE'][0])
                        + '\t close: ' + str(round(close_l[-1], 2))
                        + '\t return: ' + str(round((close_l[-1] / close_l[-2] - 1) * 100, 2)) + '%'
                    )

                    vol_l.append(data_c['VOL'][0])
                    oi_l.append(data_c['OI'][0])
                    amt_l.append(data_c['AMT'][0])
                    pvol_l.append(data_today['VOL'].sum())
                    poi_l.append(data_today['OI'].sum())
                    pamt_l.append(data_today['AMT'].sum())

                    if (
                            data_c['DDATE'][0] is not None
                            and data_c_sub['DDATE'][0] is not None
                            and (data_c_sub['DDATE'][0] - data_c['DDATE'][0]).days != 0
                            and data_c['CLOSE'][0] > 0
                            and data_c_sub['CLOSE'][0] > 0
                    ):
                        ry_l.append(
                            np.log(
                                data_c['CLOSE'][0] / data_c_sub['CLOSE'][0]
                            ) / (data_c_sub['DDATE'][0] - data_c['DDATE'][0]).days * 365
                        )
                    else:
                        ry_l.append(None)

            data_index = pd.DataFrame(
                {
                    'TDATE': date_l,
                    'EXCHANGE': data['EXCHANGE'][0],
                    'PCODE': code_p,
                    'CCODE': ccode_l[1:],
                    'CCODE2': ccode2_l[1:],
                    'DDATE': ddate_l[1:],
                    'LDATE': ldate_l[1:],
                    'OPEN': open_l,
                    'CLOSE': close_l[1:],
                    'RY': ry_l,
                    'VOL': vol_l,
                    'OI': oi_l,
                    'AMT': amt_l,
                    'PVOL': pvol_l,
                    'POI': poi_l,
                    'PAMT': pamt_l,
                }, index=range(len(date_l))
            )
            data_index['ID'] = (
                    (data_index['EXCHANGE'] * 1000 + data_index['PCODE']) * 100000000
                    + data_index['TDATE'].apply(lambda x: int(x.strftime('%Y%m%d')))
            )
            data_index.to_sql(table, engine, if_exists='append', index=False)


if __name__ == '__main__':
    t1 = datetime.now()
    hsjy_fut_index()
    t2 = datetime.now()

    print(t2)
    print(t2 - t1)

