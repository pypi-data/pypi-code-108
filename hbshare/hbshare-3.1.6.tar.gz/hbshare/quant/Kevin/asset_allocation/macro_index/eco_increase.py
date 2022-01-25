"""
经济增长类指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class EconomyIncrease:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_eco_increase'

    def get_eco_increase_data(self):
        """
        经济增长类数据：GDP不变价当季同比（实际增速）、GDP现价当季值、GDP平减指数当季同比、失业率、制造业PMI、工业增加值: 当月同比、
                    发电量：当月同比、消费者信心指数、
                    70个大中城市新建商品住宅价格指数:环比、商品房销售面积：累计同比、房地产开发投资完成额：住宅：累计同比、百城住宅价格指数:同比、
                    工业企业：产成品存货：累计同比、工业企业：利润总额：累计同比、工业产能利用率、
                    销量：挖掘机：主要企业：当月同比、
                    九鞅货币条件指数、克强指数：当月值、
                    固定资产投资完成额： 累计同比（总体、制造业、基建、房地产）、中国出口集装箱运价指数(CCFI)、OECD综合领先指标:中国
        """
        index_list = ['M0039354', 'M5567876', 'M5439528', 'M5650805', 'M0017126', 'M0000545',
                      'S0027013', 'M0012303',
                      'S2707412', 'S0073300', 'S0049576', 'S2704485',
                      'M0000561', 'M0000557', 'M5792266',
                      'S6002167',
                      'M6641342', 'M5407921',
                      'M0000273', 'M0000357', 'M5440435', 'M0000449',
                      'S0000066', 'G1000116']
        name_dict = {'M0039354': 'GDP_real', 'M5567876': 'GDP_current_price', 'M5439528': "GDP_deflator",
                     'M5650805': 'unemployment',
                     'M0017126': 'PMI', 'M0000545': "IVA_yoy",
                     'S0027013': 'generating_cap_yoy', 'M0012303': 'Consumer_Index',
                     'S2707412': 'house_price_yoy', 'S0073300': 'house_sell_yoy',
                     'S0049576': "house_investment_yoy", 'S2704485': "hundred_house_price_yoy",
                     'M0000561': 'ind_goods_cum_yoy', 'M0000557': 'ind_income_cum_yoy', 'M5792266': 'ind_cu_rate',
                     'S6002167': 'excavator_yoy',
                     'M6641342': 'jy_curr_index', 'M5407921': 'kq_index',
                     'M0000273': 'FAI_cum_yoy', 'M0000357': 'FAI_mf_cum_yoy',
                     'M5440435': 'FAI_fm_cum_yoy', 'M0000449': 'FAI_re_cum_yoy',
                     'S0000066': 'CCFI', 'G1000116': "OECD_leading_indicator"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch economy increase data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        data['GDP_deflator'] = data['GDP_deflator'].round(2)
        data['IVA_yoy'] = data['IVA_yoy'].round(1)
        data['OECD_leading_indicator'] = data['OECD_leading_indicator'].round(2)
        data['jy_curr_index'] = data['jy_curr_index'].round(4)
        data['kq_index'] = data['kq_index'].round(2)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_eco_increase_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                    create table mac_eco_increase(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    GDP_real decimal(6, 1),
                    GDP_current_price decimal(9, 2),
                    GDP_deflator decimal(4, 2),
                    unemployment decimal(3, 1),
                    PMI decimal(4, 1),
                    IVA_yoy decimal(4, 1),
                    generating_cap_yoy decimal(6, 2),
                    Consumer_Index decimal(6, 2),
                    house_price_yoy decimal(4, 2),
                    house_sell_yoy decimal(5, 2),
                    house_investment_yoy decimal(5, 2),
                    hundred_house_price_yoy decimal(4, 2),
                    ind_goods_cum_yoy decimal(5, 2),
                    ind_income_cum_yoy decimal(5, 2),
                    ind_cu_rate decimal(5, 2),
                    excavator_yoy decimal(5, 2),
                    jy_curr_index decimal(5, 4),
                    kq_index decimal(5, 2),
                    FAI_cum_yoy decimal(5, 2),
                    FAI_mf_cum_yoy decimal(5, 2),
                    FAI_fm_cum_yoy decimal(5, 2),
                    FAI_re_cum_yoy decimal(5, 2),
                    CCFI decimal(6, 2),
                    OECD_leading_indicator decimal(6, 2)) 
                """
            create_table(self.table_name, sql_script)
            data = self.get_eco_increase_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    EconomyIncrease('2005-01-01', '2021-06-10', is_increment=0).get_construct_result()