#!/usr/bin/python
#coding:utf-8
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated import engine_params
from datetime import datetime
import pywt


start_date = '20120101'
end_date = '20200408'


sql_script = "SELECT * FROM turnover_structure WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(start_date, end_date)
engine = create_engine(engine_params)
data = pd.read_sql(sql_script, engine)
data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

data = data[['trade_date', 'cr5', 'cr10', 'avg_mkt', 'close']]
db4 = pywt.Wavelet('db4')
coeffs = pywt.wavedec(np.array(data['cr5']), db4)
# coeffs[len(coeffs) - 1] *= 0
# coeffs[len(coeffs) - 2] *= 0
# coeffs[len(coeffs) - 3] *= 0
# coeffs[len(coeffs) - 4] *= 0
# coeffs[len(coeffs) - 5] *= 0
# coeffs[len(coeffs) - 6] *= 0

threshold = 0.9
for i in range(1, len(coeffs)):
    coeffs[i] = pywt.threshold(coeffs[i], threshold*max(coeffs[i]))  # 将噪声滤波

meta = pywt.waverec(coeffs, db4)
data['cr5_denoise'] = meta[:-1]
data.set_index('trade_date')[['cr5', 'cr5_denoise']].plot.line()