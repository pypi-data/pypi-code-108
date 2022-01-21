"""
板块指数更新程序
"""
import pandas as pd
import numpy as np
from hbshare.fe.common.util.data_loader import SectorIndexCalculatorLoader
from hbshare.fe.common.util.config import industry_cluster_dict_new
from sqlalchemy import create_engine


class SectorIndexCalculator:
    def __init__(self, start_date, end_date, write2db=False):
        self.start_date = start_date
        self.end_date = end_date
        self.write2db = write2db
        self._load_data()

    def _load_data(self):
        self.industry_data = SectorIndexCalculatorLoader(self.start_date, self.end_date).load()

    def get_construct_result(self):
        industry_data = self.industry_data.copy()

        tmp = pd.pivot_table(
            industry_data, index='TRADEDATE', columns='INDEXNAME', values='TCLOSE').sort_index()
        industry_return = tmp.pct_change().dropna()
        industry_return = industry_return[industry_return.index >= self.start_date]

        tmp = pd.pivot_table(
            industry_data, index='TRADEDATE', columns='INDEXNAME', values='NEG_MKV').sort_index().fillna(method='ffill')
        industry_mkt = tmp.shift(1).dropna()
        industry_mkt = industry_mkt[industry_mkt.index >= self.start_date]

        assert(industry_return.shape == industry_mkt.shape)

        sector_return = []
        for key, value in industry_cluster_dict_new.items():
            weight = industry_mkt[value].divide(industry_mkt[value].sum(axis=1), axis='rows')
            ret_array = np.diag(weight.dot(industry_return[value].T))
            sector_series = pd.Series(index=industry_return.index, data=ret_array)
            sector_return.append(sector_series.to_frame(name=key))

        sector_return = pd.concat(sector_return, axis=1)

        sector_return = sector_return.reset_index().rename(
            columns={"大金融": "BIGFINANCE", "消费": "CONSUMING", "周期": "CYCLE", "制造": "MANUFACTURE"})

        if self.write2db:
            engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
                'admin', 'mysql', '192.168.223.152', '3306', 'riskmodel'))

            sector_return.to_sql('sector_return', engine, index=False, if_exists='append')

        return sector_return


if __name__ == '__main__':
    # res = SectorIndexCalculator('20210705', '20210820', write2db=True).get_construct_result()
    res = SectorIndexCalculator('20211201', '20211222').get_construct_result()
    print(res)