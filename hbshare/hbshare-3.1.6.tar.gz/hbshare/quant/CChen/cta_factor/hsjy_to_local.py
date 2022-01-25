import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from hbshare.quant.CChen.func import generate_table
import hbshare as hbs
import pymysql
from hbshare.quant.CChen.cons import (
    db,
    db_tables,
    HSJY_EXCHANGE_INE,
    HSJY_EXCHANGE_CZCE,
    HSJY_EXCHANGE_SHFE,
    HSJY_EXCHANGE_DCE,
    HSJY_EXCHANGE_CFFEX
)

page_size_con = 49999

sql_l = '''(
    `JSID` bigint not null COMMENT \'恒生聚源ID\',
    `TDATE`  date not null COMMENT \'交易日期\',
    `EXCHANGE` int COMMENT \'交易所\',
    `CCODE` int COMMENT \'合约代码-恒生聚源\',
    `PCODE` int COMMENT \'品种代码-恒生聚源\',
    `DYEAR` int COMMENT \'交割年\',
    `DMONTH` int COMMENT \'交割月\',
    `DDATE` date COMMENT \'交割日期\',
    `LDATE` date COMMENT \'最后交易日期\',
    `OPEN` float,
    `HIGH` float,
    `LOW` float,
    `CLOSE` float,
    `SETTLE` float,
    `VOL` int,
    `OI` int,
    `OICHG` int,
    `AMT` double,
    primary key (`JSID`)
    )
    '''

sql_l_info = '''(
    `JSID` bigint not null COMMENT \'恒生聚源ID\',
    `EXCHANGE` int COMMENT \'交易所\',
    `CNAME` varchar(255) COMMENT \'合约名称\',
    `CCODE` bigint COMMENT \'合约代码-恒生聚源\',
    `PCODE` int COMMENT \'品种代码-恒生聚源\',
    `PCODED` bigint COMMENT \'品种唯一代码-恒生聚源\',
    `EDATE` date COMMENT \'上市日期\',
    `DDATE` date COMMENT \'交割日期\',
    `LDATE` date COMMENT \'最后交易日期\',
    `MULT` int comment \'合约乘数\',
    `MULTINFO` varchar(255) COMMENT \'每手合约乘数\',
    `PRICEUNIT` varchar(255) COMMENT \'报价单位\',
    `SLIP` varchar(255) COMMENT \'最小变动价位\',
    `CHGLIMIT`  varchar(255) COMMENT \'涨跌停幅度\',
    primary key (`JSID`)
    )
    '''

sql_l_info_p = '''(
    `JSID` bigint not null COMMENT \'恒生聚源ID\',
    `EXCHANGE` int COMMENT \'交易所\',
    `PNAME` varchar(255) COMMENT \'品种名称\',
    `PCODED` bigint COMMENT \'品种唯一代码-恒生聚源\',
    `PCODE` int COMMENT \'品种代码-恒生聚源\',
    `CODE` varchar(255) COMMENT \'交易所代码\',
    `PTYPE` int COMMENT \'品种合约类型-恒生聚源\',
    primary key (`JSID`)
    )
    '''

sql_l_wr = '''(
    `JSID` bigint not null COMMENT \'恒生聚源ID\',
    `TDATE`  date not null COMMENT \'交易日期\',
    `EXCHANGE` int COMMENT \'交易所\',
    `PCODE` int COMMENT \'品种代码-恒生聚源\',
    `PNAME` varchar(255) COMMENT \'品种名称\',
    `FREQ` int COMMENT \'公布频率\',
    `UNITCODE` int COMMENT \'单位代码\',
    `UNITNAME` varchar(255) COMMENT \'单位名称\',
    `WRQPRIOR` int  COMMENT \'上期仓单量\',
    `WRQINCREASE` int COMMENT \'仓单增加量\',
    `WRQWRITEOFF` int COMMENT \'仓单注销量\',
    `WRQCURRENT` int COMMENT \'本期仓单量\',
    `WRQPREDICTION` int COMMENT \'有效预报量\',
    `STOCKPRIOR` int COMMENT \'上期库存小计\',
    `STOCKCURRENT` int COMMENT \'本期库存小计\',
    `AVAILABLESTOCKPRIOR` int COMMENT \'上期可用库容量\',
    `AVAILABLESTOCKCURRENT` int COMMENT \'本期可用库容量\',
    primary key (`JSID`)
    )
    '''

sql_l_member = '''(
    `JSID` bigint not null COMMENT \'恒生聚源ID\',
    `TDATE`  date not null COMMENT \'交易日期\',
    `EXCHANGE` int COMMENT \'交易所\',
    `CCODE` bigint COMMENT \'合约代码-恒生聚源\',
    `CONTRACT` varchar(255) COMMENT \'交易代码，品种代码+到期日期\',
    `RANKN` int COMMENT \'名次\',
    `MCODE` varchar(255) COMMENT \'会员号\',
    `MNAME` varchar(255) COMMENT \'会员简称\',
    `INDICATORCODE` int COMMENT \'指标代码\',
    `INDICATORNAME` varchar(255) COMMENT \'指标名称\',
    `INDICATORVOL` int COMMENT \'指标数量(手)\',
    `INDICATORCHG` int COMMENT \'较上期增减量(手)\',
    primary key (`JSID`)
    )
    '''


def trans_data(data, contract_info, data_info=None):
    df = pd.DataFrame(data)
    df['TDATE'] = pd.to_datetime(df['ENDDATE']).dt.date
    df['DDATE'] = df['INNERCODE'].apply(
        lambda x: contract_info[
            contract_info['CCode'.upper()] == x
            ].reset_index(drop=True)['DDATE'][0]
    )
    df['DDATE'] = pd.to_datetime(df['DDATE']).dt.date
    df['LDATE'] = df['INNERCODE'].apply(
        lambda x: contract_info[
            contract_info['CCode'.upper()] == x
            ].reset_index(drop=True)['LDate'.upper()][0]
    )
    df['LDATE'] = pd.to_datetime(df['LDATE']).dt.date
    # df['PRODUCT'] = df['OPTIONCODE'].apply(
    #     lambda x: data_info[data_info['PRODUCTCODE'] == str(x)].reset_index(drop=True)['PRODUCTNAME'][0]
    # )
    df = df.rename(
        columns={
            'CONTRACTNAME': 'NAME',
            'SETTLEMENTYEAR': 'DYEAR',
            'SETTLEMENTMONTH': 'DMONTH',
            'OPENPRICE': 'OPEN',
            'HIGHPRICE': 'HIGH',
            'LOWPRICE': 'LOW',
            'CLOSEPRICE': 'CLOSE',
            'SETTLEPRICE': 'SETTLE',
            'PREVSETTLEPRICE': 'PRESETTLE',
            'VOLUME': 'VOL',
            'OPENINTEREST': 'OI',
            'OPENINTERESTCHANGE': 'OICHG',
            'TURNOVER': 'AMT',
            'OPTIONCODE': 'PCODE',
            'INNERCODE': 'CCODE'
        }
    )[
        [
            'TDATE',
            'EXCHANGE',
            # 'NAME',
            'CCODE',
            'PCODE',
            'DYEAR',
            'DMONTH',
            'DDATE',
            'LDATE',
            # 'PRESETTLE',
            'OPEN',
            'HIGH',
            'LOW',
            'CLOSE',
            'SETTLE',
            'VOL',
            'OI',
            'OICHG',
            'AMT',
            'JSID'
        ]
    ]
    return df


def hsjy_fut_wr(db_path, sql_info, exchanges=None, table='hsjy_fut_wr', page_size=None):
    if page_size is None:
        page_size = page_size_con

    if exchanges is None:
        exchanges = [HSJY_EXCHANGE_SHFE, HSJY_EXCHANGE_DCE, HSJY_EXCHANGE_CZCE, HSJY_EXCHANGE_INE, HSJY_EXCHANGE_CFFEX]

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l_wr,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='from ' + db_tables['hsjy_wr']
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_jsid_in_db = pd.read_sql_query(
        'select distinct `JSID` from ' + table + ' order by `JSID` desc limit 1', create_engine(db_path)
    )
    if len(latest_jsid_in_db) > 0:
        latest_jsid = latest_jsid_in_db['JSID'][0]
    else:
        latest_jsid = 0

    print('\t' + 'Latest jsid in db: ' + str(latest_jsid))

    if len(exchanges) > 1:
        ex_sql = 'EXCHANGE in ' + str(tuple(exchanges))
    elif len(exchanges) == 1:
        ex_sql = 'EXCHANGE=\'' + exchanges[0] + '\''
    else:
        raise ValueError('No exchange')

    while 1:
        sql = (
                'select * from (select * from ' + db_tables['hsjy_wr']
                + ' where JSID>' + str(latest_jsid)
                + ' and ' + ex_sql.replace('EXCHANGE', 'EXCHANGECODE')
                + ' order by JSID) where rownum<=' + str(page_size)
        ).replace(
            '*', 'JSID, ENDDATE, EXCHANGECODE, REPORTPERIOD, OPTIONCODE, OPTIONNAME, UNITCODE, UNITNAME, '
                 'WRQPrior, WRQIncrease, WRQWriteOff, WRQCurrent, WRQPrediction, StockPrior, StockCurrent, '
                 'AvailableStockPrior, AvailableStockCurrent'.upper()
        )

        wr_info = hbs.db_data_query(
            db=db,
            sql=sql,
            page_size=page_size
        )
        df = pd.DataFrame(wr_info['data']).rename(
            columns={
                'ENDDATE': 'TDATE',
                'EXCHANGECODE': 'EXCHANGE',
                'REPORTPERIOD': 'FREQ',
                'OPTIONCODE': 'PCODE',
                'OPTIONNAME': 'PNAME',
            }
        )
        if len(df) == 0:
            print('\t\t' + 'No more new info data')
            return
        col = df.columns.tolist()
        col.pop(col.index('ROW_ID'))
        df[col].to_sql(table, create_engine(db_path), if_exists='append', index=False)
        latest_jsid = df['JSID'].tolist()[-1]
        print('\tNew data: ' + str(len(df)) + ', JSID: ' + str(latest_jsid))


def hsjy_fut_com_info(db_path, sql_info, exchanges=None, table='hsjy_fut_info_c', page_size=None):
    if page_size is None:
        page_size = page_size_con

    if exchanges is None:
        exchanges = [HSJY_EXCHANGE_SHFE, HSJY_EXCHANGE_DCE, HSJY_EXCHANGE_CZCE, HSJY_EXCHANGE_INE, HSJY_EXCHANGE_CFFEX]

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l_info,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='from ' + db_tables['hsjy_fut_contract_info']
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_jsid_in_db = pd.read_sql_query(
        'select distinct `JSID` from ' + table + ' order by `JSID` desc limit 1', create_engine(db_path)
    )
    if len(latest_jsid_in_db) > 0:
        latest_jsid = latest_jsid_in_db['JSID'][0]
    else:
        latest_jsid = 0

    print('\t' + 'Latest jsid in db: ' + str(latest_jsid))

    if len(exchanges) > 1:
        ex_sql = 'EXCHANGE in ' + str(tuple(exchanges))
    elif len(exchanges) == 1:
        ex_sql = 'EXCHANGE=\'' + exchanges[0] + '\''
    else:
        raise ValueError('No exchange')

    while 1:
        sql = (
                'select * from (select * from ' + db_tables['hsjy_fut_contract_info']
                + ' where JSID>' + str(latest_jsid)
                + ' and IFREAL=1 and ' + ex_sql.replace('EXCHANGE', 'EXCHANGECODE')
                + ' order by JSID) where rownum<=' + str(page_size)
        ).replace(
            '*', 'JSID, CONTRACTINNERCODE, CONTRACTNAME, EXCHANGECODE, OPTIONCODE, LASTTRADINGDATE, DELIVERYDATE, '
                 'EffectiveDate, CMValue, ContractMultiplier, '
                 'PriceUnit, LittlestChangeUnit, ChangePCTLimit, VarietyInnerCode'.upper()
        )

        contract_info = hbs.db_data_query(
            db=db,
            sql=sql,
            page_size=page_size
        )
        df = pd.DataFrame(contract_info['data']).rename(
            columns={
                'CONTRACTINNERCODE': 'CCODE',
                'CONTRACTNAME': 'CNAME',
                'EXCHANGECODE': 'EXCHANGE',
                'OPTIONCODE': 'PCODE',
                'VarietyInnerCode'.upper(): 'PCODED',
                'EffectiveDate'.upper(): 'EDATE',
                'LASTTRADINGDATE': 'LDATE',
                'DELIVERYDATE': 'DDATE',
                'CMVALUE': 'MULT',
                'ContractMultiplier'.upper(): 'MULTINFO',
                'LittlestChangeUnit'.upper(): 'SLIP',
                'ChangePCTLimit'.upper(): 'CHGLIMIT',
            }
        )
        if len(df) == 0:
            print('\t\t' + 'No more new info data')
            return
        df[
            [
                'JSID', 'CCODE', 'CNAME', 'EXCHANGE', 'PCODE', 'PCODED', 'EDATE', 'LDATE', 'DDATE',
                'MULT', 'MULTINFO', 'SLIP', 'CHGLIMIT', 'PRICEUNIT'
            ]
        ].to_sql(table, create_engine(db_path), if_exists='append', index=False)
        latest_jsid = df['JSID'].tolist()[-1]
        print('\tNew data: ' + str(len(df)) + ', JSID: ' + str(latest_jsid))


def hsjy_fut_pro_info(db_path, sql_info, exchanges=None, table='hsjy_fut_info_p', page_size=None):
    if page_size is None:
        page_size = page_size_con

    if exchanges is None:
        exchanges = [HSJY_EXCHANGE_SHFE, HSJY_EXCHANGE_DCE, HSJY_EXCHANGE_CZCE, HSJY_EXCHANGE_INE, HSJY_EXCHANGE_CFFEX]

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l_info_p,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='from ' + db_tables['hsjy_product_info']
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_jsid_in_db = pd.read_sql_query(
        'select distinct `JSID` from ' + table + ' order by `JSID` desc limit 1', create_engine(db_path)
    )
    if len(latest_jsid_in_db) > 0:
        latest_jsid = latest_jsid_in_db['JSID'][0]
    else:
        latest_jsid = 0

    print('\t' + 'Latest jsid in db: ' + str(latest_jsid))

    if len(exchanges) > 1:
        ex_sql = 'EXCHANGE in ' + str(tuple(exchanges))
    elif len(exchanges) == 1:
        ex_sql = 'EXCHANGE=\'' + exchanges[0] + '\''
    else:
        raise ValueError('No exchange')

    while 1:
        sql = (
                'select * from (select * from ' + db_tables['hsjy_product_info']
                + ' where JSID>' + str(latest_jsid)
                + ' and ' + ex_sql + ' order by JSID) where rownum<=' + str(page_size)
        ).replace(
            '*', 'JSID, CONTRACTINNERCODE, CONTRACTNAME, EXCHANGE, TradingCode, ContractType, ContractOption'.upper()
        )

        contract_info = hbs.db_data_query(
            db=db,
            sql=sql,
            page_size=page_size
        )
        df = pd.DataFrame(contract_info['data']).rename(
            columns={
                'CONTRACTINNERCODE': 'PCODED',
                'CONTRACTNAME': 'PNAME',
                'ContractOption'.upper(): 'PCODE',
                'TradingCode'.upper(): 'CODE',
                'ContractType'.upper(): 'PTYPE'
            }
        )
        if len(df) == 0:
            print('\t\t' + 'No more new info data')
            return
        df[
            [
                'JSID', 'EXCHANGE', 'PCODE', 'PNAME', 'PCODED', 'CODE', 'PTYPE'
            ]
        ].to_sql(table, create_engine(db_path), if_exists='append', index=False)
        latest_jsid = df['JSID'].tolist()[-1]
        print('\tNew data: ' + str(len(df)) + ', JSID: ' + str(latest_jsid))


def hsjy_fut_com(
        db_path, sql_info, exchanges=None, table='hsjy_fut_com', table_info='hsjy_fut_info_c', page_size=None
):
    if page_size is None:
        page_size = page_size_con

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
            table_comment='from ' + db_tables['hsjy_com_daily_quote']
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_jsid_in_db = pd.read_sql_query(
        'select distinct `JSID` from ' + table + ' order by `JSID` desc limit 1', create_engine(db_path)
    )
    if len(latest_jsid_in_db) > 0:
        latest_jsid = latest_jsid_in_db['JSID'][0]
    else:
        latest_jsid = 0

    print('\tLatest jsid in db: ' + str(latest_jsid))

    if len(exchanges) > 1:
        ex_sql = 'EXCHANGE in ' + str(tuple(exchanges))
    elif len(exchanges) == 1:
        ex_sql = 'EXCHANGE=\'' + exchanges[0] + '\''
    else:
        raise ValueError('No exchange')

    contract_info = pd.read_sql_query('select * from ' + table_info, create_engine(db_path))

    while 1:
        sql = (
                'select * from (select * from ' + db_tables['hsjy_com_daily_quote']
                + ' where  ENDDATE>=TRUNC(to_date(' + datetime(1999, 12, 31).strftime('%Y%m%d')
                + ', \'yyyymmdd\')) and JSID>' + str(latest_jsid)
                + ' and ' + ex_sql + ' order by JSID) where rownum<=' + str(page_size)
        )

        data = hbs.db_data_query(db=db, sql=sql, page_size=page_size)
        if len(data['data']) == 0:
            print('\t\t' + 'No more new quote data')
            return

        df = trans_data(
            data=data['data'], contract_info=contract_info,
            # data_info=df_info
        )
        df.to_sql(table, create_engine(db_path), if_exists='append', index=False)
        latest_jsid = df['JSID'].tolist()[-1]
        print('\tNew data: ' + str(len(df)) + ', JSID: ' + str(latest_jsid))


def hsjy_fut_member(db_path, sql_info, table='hsjy_fut_memberrank', page_size=None):
    if page_size is None:
        page_size = page_size_con

    try:
        generate_table(
            database='daily_data',
            table=table,
            generate_sql=sql_l_member,
            sql_ip=sql_info['ip'],
            sql_user=sql_info['user'],
            sql_pass=sql_info['pass'],
            table_comment='from ' + db_tables['hsjy_member_rank']
        )
        print(table + ' generated')
    except pymysql.err.InternalError:
        print(table + ' exists')

    latest_jsid_in_db = pd.read_sql_query(
        'select distinct `JSID` from ' + table + ' order by `JSID` desc limit 1', create_engine(db_path)
    )
    if len(latest_jsid_in_db) > 0:
        latest_jsid = latest_jsid_in_db['JSID'][0]
    else:
        latest_jsid = 0

    print('\tLatest jsid in db: ' + str(latest_jsid))

    while 1:
        member_sql = (
                'select * from (select * from ' + db_tables['hsjy_member_rank']
                + ' where JSID>' + str(latest_jsid)
                + ' order by JSID) where rownum<=' + str(page_size)
        ).replace(
            '*', 'JSID, ENDDATE, EXCHANGECODE, ContractInnerCode, ContractCode, RankNumber, MemberCode, MemberAbbr, '
                 'IndicatorCode, IndicatorName, IndicatorVolume, ChangeVolume'.upper()
        )
        member_rank_info = hbs.db_data_query(
            db=db,
            sql=member_sql,
            page_size=page_size
        )
        df = pd.DataFrame(member_rank_info['data']).rename(
            columns={
                'ENDDATE': 'TDATE',
                'EXCHANGECODE': 'EXCHANGE',
                'ContractInnerCode'.upper(): 'CCODE',
                'ContractCode'.upper(): 'CONTRACT',
                'RankNumber'.upper(): 'RANKN',
                'MemberCode'.upper(): 'MCODE',
                'MemberAbbr'.upper(): 'MNAME',
                'IndicatorVolume'.upper(): 'INDICATORVOL',
                'ChangeVolume'.upper(): 'INDICATORCHG'
            }
        )
        if len(df) == 0:
            print('\t\t' + 'No more new member rank data')
            return
        col = df.columns.tolist()
        col.pop(col.index('ROW_ID'))
        df[col].to_sql(table, create_engine(db_path), if_exists='append', index=False)
        latest_jsid = df['JSID'].tolist()[-1]
        print('\tNew data: ' + str(len(df)) + ', JSID: ' + str(latest_jsid))

