"""
2021下半年FOF和代销产品净值风格归因
"""
import os
import pandas as pd
from datetime import datetime
import hbshare as hbs
from MyUtil.data_loader import get_fund_nav_from_work
from hbshare.fe.common.util.regressions import Regression


fund_map_dict = {
    "启林中证500指数增强1号": "SGY379",
    "量锐62号": "SGR954",
    "明汯量化中小盘增强1号": "SGG585",
    "明汯价值成长1期3号": "SEE194",
    "天演赛能": "P22984",
    "衍复指增三号": "SJH866",
    "铭量中证500增强1号": "SLY644",
    "因诺聚配中证500指数增强": "SGX346"
}


if __name__ == '__main__':
    start_date = '20210101'
    end_date = '20211231'
    data = get_fund_nav_from_work(start_date, end_date, 'SGG585')
    print(data)