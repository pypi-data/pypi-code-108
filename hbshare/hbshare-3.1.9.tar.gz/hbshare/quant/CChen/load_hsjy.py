import pandas as pd
from hbshare.quant.CChen.cons import db_tables, HSJY_PRODUCT_CODE, db
import hbshare as hbs
from datetime import datetime


page_size = 49999


def load_fut_fin(index_code, start_date, end_date, table=db_tables['hsjy_fin_daily_quote']):
    sql_raw = (
            'select '
            'TRADINGDAY as TDATE, '
            'CONTRACTCODE as CODE, '
            'CLOSEPRICE as CLOSE '
            ' from ' + table
            + ' where TRADINGDAY<=TRUNC(to_date(' + end_date.strftime('%Y%m%d') + ', \'yyyymmdd\')) '
            + ' and TRADINGDAY>=TRUNC(to_date(' + start_date.strftime('%Y%m%d') + ', \'yyyymmdd\')) '
            + ' and OPTIONCODE=' + str(HSJY_PRODUCT_CODE[index_code]) + ' order by TRADINGDAY, OPTIONCODE'
    )
    data = pd.DataFrame()
    page = 1
    pages = None
    while 1:
        data_raw = hbs.db_data_query(db=db, sql=sql_raw, page_size=page_size, page_num=page)
        if pages is None:
            pages = data_raw['pages']
        page += 1
        data = data.append(pd.DataFrame(data_raw['data']))
        if page > pages:
            break

    return data.reset_index(drop=True)


if __name__ == '__main__':
    load_fut_fin(index_code='IC', start_date=datetime(2021, 10, 1).date(), end_date=datetime.now().date())
