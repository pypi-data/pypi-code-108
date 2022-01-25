#!/usr/bin/python
# coding:utf-8
hb_ip = '192.168.223.152'

sql_user_hb = {
    'ip': hb_ip,
    'user': 'readonly',
    'pass': 'c24mg2e6',
    'port': '3306'
}

sql_write_path_hb = {
    'commodities':
        'mysql+mysqldb://%s:%s@%s:%s/commodities?charset=utf8'
        % (sql_user_hb['user'], sql_user_hb['pass'], hb_ip, sql_user_hb['port']),
    'stocks':
        'mysql+mysqldb://%s:%s@%s:%s/stocks?charset=utf8'
        % (sql_user_hb['user'], sql_user_hb['pass'], hb_ip, sql_user_hb['port']),
    'work':
        'mysql+mysqldb://%s:%s@%s:%s/work?charset=utf8'
        % (sql_user_hb['user'], sql_user_hb['pass'], hb_ip, sql_user_hb['port']),
    'daily':
        'mysql+mysqldb://%s:%s@%s:%s/daily_data?charset=utf8'
        % (sql_user_hb['user'], sql_user_hb['pass'], hb_ip, sql_user_hb['port']),
}

index_underlying = {
    'IC': '中证500',
    'IF': '沪深300',
    'IH': '上证50'
}
underlying_code = {
    'IC': '000905',
    'IF': '000300',
    'IH': '000015',
}

# 交易所代码
HSJY_EXCHANGE_SHFE = 10
HSJY_EXCHANGE_INE = 11
HSJY_EXCHANGE_DCE = 13
HSJY_EXCHANGE_CZCE = 15
HSJY_EXCHANGE_CFFEX = 20

exchange_list = [
    HSJY_EXCHANGE_CFFEX,
    HSJY_EXCHANGE_DCE,
    HSJY_EXCHANGE_INE,
    HSJY_EXCHANGE_CZCE,
    HSJY_EXCHANGE_SHFE
]

exchange_dict = {
    HSJY_EXCHANGE_CFFEX: '中金所',
    HSJY_EXCHANGE_DCE: '大商所',
    HSJY_EXCHANGE_INE: '能源所',
    HSJY_EXCHANGE_CZCE: '郑商所',
    HSJY_EXCHANGE_SHFE: '上期所'
}

# 品种代码
HSJY_PRODUCT_CODE = {
    'IH': 46,
    'IF': 3145,
    'IC': 4978
}

# 虚拟合约代码
HSJY_VIRTUAL_CONTRACT = {
    'FINANCE': {
        'IF': {
            '当月': 2000440,
            '次月': 2000441,
            '当季': 2000442,
            '次季': 2000443,
        },
        'IC': {
            '当月': 2006539,
            '次月': 2006540,
            '当季': 2006541,
            '次季': 2006542,
        },
        'IH': {
            '当月': 2006535,
            '次月': 2006536,
            '当季': 2006537,
            '次季': 2006538,
        },
    }
}

HSJY_PRODUCT_TABLE = 'Fut_FuturesContract'
HSJY_CONTRACT_TABLE = 'Fut_ContractMain'

# Fut_FuturesContract常用字段
properties_product = [
    'ID',
    'ContractName'.upper(),
    'TradingCode'.upper(),
    # 'ContractOption'.upper(),
    'Exchange'.upper(),
    'ContractMulti'.upper(),
    'PriceUnit'.upper(),
    'LittlestChangeUnit'.upper(),
    'ContractInnerCode'.upper(),
]

# Fut_ContractMain常用字段
properties_contract = [
    'ID',
    'ContractInnerCode'.upper(),
    'ContractCode'.upper(),
    'ContractName'.upper(),
    'ExchangeCode'.upper(),
    'ContractMultiplier'.upper(),
    'PriceUnit'.upper(),
    'LittlestChangeUnit'.upper(),
    'DeliveryYear'.upper(),
    'DeliveryMonth'.upper(),
    'LastTradingDate'.upper(),
    # 'OptionCode'.upper(),
    'VarietyInnerCode'.upper(),
]

# FUT_DAILYQUOTE 常用字段，商品期货
properties_com_k = [
    'ID',
    'InnerCode'.upper(),
    'EndDate'.upper(),
    # 'DATE_ADD(EndDate, INTERVAL -8 HOUR) as date'.upper(),
    'ReportPeriod'.upper(),
    'Exchange'.upper(),
    'ContractName'.upper(),
    'SettlementYear'.upper(),
    'SettlementMonth'.upper(),
    'OpenPrice'.upper(),
    'HighPrice'.upper(),
    'LowPrice'.upper(),
    'ClosePrice'.upper(),
    'SettlePrice'.upper(),
    'Volume'.upper(),
    'OpenInterest'.upper(),
    'OpenInterestChange'.upper(),
    'Turnover'.upper(),
]

# FUT_TRADINGQUOTE 常用字段，金融期货
properties_fin_k = [
    'ID',
    'ContractInnerCode'.upper(),
    'TradingDay'.upper(),
    # 'DATE_ADD(EndDate, INTERVAL -8 HOUR) as date'.upper(),
    # 'ReportPeriod'.upper(),
    'OptionCode'.upper(),
    'ExchangeCode'.upper(),
    'ContractCode'.upper(),
    # 'SettlementYear'.upper(),
    # 'SettlementMonth'.upper(),
    'OpenPrice'.upper(),
    'HighPrice'.upper(),
    'LowPrice'.upper(),
    'ClosePrice'.upper(),
    'SettlePrice'.upper(),
    'TurnoverVolume'.upper(),  # 成交量
    'TurnoverValue'.upper(),  # 成交额
    'OpenInterest'.upper(),  # 持仓量
    'ChangePCTOpenInterest'.upper(),
]


# FINCHINA.CHDQUOTE 字段，股票
properties_stk_k = [
    'TDATE',
    'EXCHANGE',
    'SYMBOL',
    'SNAME',
    'LCLOSE',
    'TOPEN',
    'TCLOSE',
    'HIGH',
    'LOW',
    'VOTURNOVER',
    'VATURNOVER',
    'CHG',
    'PCHG',
    'MCAP',
    'TCAP',
    'TURNOVER',
]


db = 'readonly'
db_tables = {
    'hsjy_com_daily_quote': 'HSJY_GG.Fut_DailyQuote'.upper(),
    'hsjy_fin_daily_quote': 'HSJY_GG.Fut_TradingQuote'.upper(),
    'hsjy_fut_contract_info': 'HSJY_GG.Fut_ContractMain'.upper(),
    'hsjy_cons_info': 'HSJY_GG.CT_Product'.upper(),
    'hsjy_product_info': 'HSJY_GG.Fut_FuturesContract'.upper(),
    'hsjy_wr': 'HSJY_GG.Fut_WRStatByOption'.upper(),
    'hsjy_member_rank': 'HSJY_GG.FUT_MEMBERRANKBYCONTRACT',
    'ch_stocks_daily_quote': 'FINCHINA.CHDQUOTE',
    'index_daily_quote': 'FUNDDB.ZSJY',
    'stocks_daily_quote': 'FUNDDB.ZGJY',
}

wind_sec = {
    'CCFI.WI': 'Wind商品指数',
    'NMFI.WI': 'Wind贵金属',
    'NFFI.WI': 'Wind有色',
    'JJRI.WI': 'Wind煤焦钢矿',
    'NMBM.WI': 'Wind非金属建材',
    'ENFI.WI': 'Wind能源',
    'CIFI.WI': 'Wind化工',
    'CRFI.WI': 'Wind谷物',
    'OOFI.WI': 'Wind油脂油料',
    'SOFI.WI': 'Wind软商品',
    'APFI.WI': 'Wind农副产品'
}
