# coding=utf-8
from __future__ import unicode_literals, division

import datetime

import pandas as pd
import os

import struct
from jotdx.reader.base_reader import TdxFileNotFoundException
from jotdx.reader.base_reader import BaseReader

"""
读取通达信数据
"""


class TdxExHqDailyBarReader(BaseReader):

    def __init__(self, vipdoc_path=None):
        self.vipdoc_path = vipdoc_path

    def parse_data_by_file(self, fname):
        if not os.path.isfile(fname):
            raise TdxFileNotFoundException('no tdx kline data, pleaes check path %s', fname)

        with open(fname, 'rb') as f:
            content = f.read()
            return self.unpack_records('<hhffffIIf', content)

        return []

    def get_df(self, code_or_file):
        # 只传入了一个参数
        data = [self._df_convert(row) for row in self.parse_data_by_file(code_or_file)]

        df = pd.DataFrame(
            data=data,
            columns=('date', 'open', 'high', 'low', 'close',
                     'amount', 'volume', 'jiesuan', 'hk_stock_amount')
        )
        # df.index = pd.to_datetime(df.date)

        # TODO 通达信这里还是有点问题,
        # (1) 按照现在这么写, 如果是星期一, 那么0点前的数据推到了星期日,
        #  0点后到9点开盘前应该是上周五晚上的行情, 算作星期一凌晨
        # 暂时不影响回测, 这里有个小坑注意
        ddelay = datetime.timedelta(days=1)
        df['date'] = pd.to_datetime(df['date']).apply(lambda x: x if 0 <= x.hour < 16 else x - ddelay)

        df = df.set_index('date')

        return df

    def _df_convert(self, row):
        t_date = row[0]
        year = int(t_date / 2048 + 2036)
        year = (year - 32) if (year > datetime.datetime.now().year) else year

        month = int(t_date % 2048 / 100)
        day = t_date % 2048 % 100

        t_time = row[1]
        hour = int(t_time / 60)
        min = t_time % 60

        datetimep = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=min)

        offset = 1
        (hk_stock_amount,) = struct.unpack('<f', struct.pack('<I', row[5 + offset]))
        new_row = (
            datetimep,
            row[1 + offset],
            row[2 + offset],
            row[3 + offset],
            row[4 + offset],
            row[5 + offset],
            row[6 + offset],
            row[7 + offset],
            hk_stock_amount
        )

        return new_row


if __name__ == '__main__':
    tdx_reader = TdxExHqDailyBarReader()
    try:
        print(tdx_reader.get_df("/Users/rainx/tmp/vipdoc/ds/29#A1801.day"))
        # print(tdx_reader.get_df("/Volumes/share/transfer/76#AG200.day"))

    except TdxFileNotFoundException as e:
        pass
