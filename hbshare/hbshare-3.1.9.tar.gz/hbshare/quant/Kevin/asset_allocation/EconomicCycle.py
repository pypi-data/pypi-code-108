"""
经济周期判断程序
"""
import pandas as pd
from datetime import datetime
# from hbshare.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class EconomicCycle:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_cycle'

    def get_eco_increase_data(self):
        """
        经济增长类数据
        """
        index_dict = {
            "M5525763": "社融增速",
            "M0001385": "M2增速",
            "M0039354": "GDP增速",
            "M0017126": "制造业PMI",
            "S0027013": "发电量同比",
            "M0012303": "消费者信心指数",
            "M0001428": "社零总额增速",
            "M1001654": "十年期国债到期收益率",
            "M1001646": "一年期国债到期收益率",
            "S5042881": "商品价格指数",
            "M0000545": "工业增加值",
            "M5650805": "失业率",
            "M5792266": "产能利用率",
            "S2707396": "30大中城市_商品房成交面积_当月值",
            "M0000273": "固定资产投资累计同比",
            "M0000609": "进口金额同比",
            "M0000557": "工业企业利润",
            "S0206721": "制造业利润总额累计同比",
            "S0206720": "采矿业利润总额累计同比",
            "S0206722": "电热燃气及水的生产和供应业利润总额累计同比",
            "S6114596": "汽车销量当月同比",
            "S0028199": "彩电产量当月同比"
                      }
        res = w.edb(','.join(list(index_dict.keys())), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch economic cycle data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=index_dict, inplace=True)

        date_list = [datetime.strftime(x, '%Y%m%d') for x in pd.date_range(self.start_date, self.end_date, freq='M')]
        data = data.set_index('trade_date').fillna(method='ffill').reindex(date_list)
        data['社融与M2增速差'] = data['社融增速'] - data['M2增速']
        data['国债期限利差'] = data['十年期国债到期收益率'] - data['一年期国债到期收益率']
        data['30大中城市商品房成交面积同比'] = data['30大中城市_商品房成交面积_当月值'].pct_change(periods=12)
        data = data.drop(
            ['社融增速', 'M2增速', '十年期国债到期收益率', '一年期国债到期收益率', '30大中城市_商品房成交面积_当月值'], axis=1)
        # 负向调整
        data['失业率'] *= -1

        return data

    def get_liquidity_data(self):
        """
        宏观流动性数据
        """
        index_dict = {
            "S2707412": "70个大中城市新建商品住宅价格指数环比",
            "M5525763": "社融增速",
            "M0096870": "贷款市场报价利率LPR_一年",
            "M0010055": "银行间同业拆借利率加权平均值_14天",
            "M0017140": "SHIBOR_2W",
            "M6404532": "实体经济杠杆率",
            "M0009970": "信贷余额",
            "M0017126": "制造业PMI",
            "M1008942": "信用利差",
            "M0001383": "M1同比",
            "M0001385": "M2同比",
            "M0041371": "七天逆回购利率",
            "M0009937": "银行间质押式回购加权利率",
            "M0043821": "中小机构存款准备金率",
            "M0061518": "大型机构存款准备金率",
            "M1004907": "国开债到期收益率_1Y",
            "M1004906": "国开债到期收益率_6M",
            "M0010096": "超储率"
        }

        res = w.edb(','.join(list(index_dict.keys())), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch economic cycle data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=index_dict, inplace=True)

        date_list = [datetime.strftime(x, '%Y%m%d') for x in pd.date_range(self.start_date, self.end_date, freq='M')]
        data = data.set_index('trade_date').fillna(method='ffill').reindex(date_list)

        data['国开债到期收益率期现差值'] = data['国开债到期收益率_1Y'] - data['国开债到期收益率_6M']
        data = data.drop(['国开债到期收益率_1Y', '国开债到期收益率_6M'], axis=1)
        # 负向调整
        neg_cols = ['贷款市场报价利率LPR_一年', '银行间同业拆借利率加权平均值_14天', 'SHIBOR_2W', '七天逆回购利率',
                    '银行间质押式回购加权利率', '中小机构存款准备金率', '大型机构存款准备金率', '国开债到期收益率期现差值', '超储率']
        for col in neg_cols:
            data[col] *= -1

        return data

    def calculate_economic_cycle(self):
        eco_increase_data = self.get_eco_increase_data()
        currency_data = self.get_liquidity_data()

        increase_diff = eco_increase_data.diff().dropna(how='all')
        increase_diff['制造业PMI'] = eco_increase_data['制造业PMI'][1:]
        increase_diff['制造业PMI'] -= 50.
        increase_count_df = increase_diff.gt(0.).sum(axis=1).to_frame('增长观点个数').merge(
            increase_diff.eq(0.).sum(axis=1).to_frame('维持不变个数'), left_index=True, right_index=True).merge(
            increase_diff.lt(0.).sum(axis=1).to_frame('衰退观点个数'), left_index=True, right_index=True)
        increase_count_df['经济增长概率'] = increase_count_df['增长观点个数'] / (increase_count_df.sum(axis=1))

        currency_diff = currency_data.diff().dropna(how='all')
        currency_diff['制造业PMI'] = currency_data['制造业PMI'][1:]
        currency_diff['制造业PMI'] -= 50.
        currency_count_df = currency_diff.gt(0.).sum(axis=1).to_frame('增长观点个数').merge(
            currency_diff.eq(0.).sum(axis=1).to_frame(name='维持不变个数'), left_index=True, right_index=True).merge(
            currency_diff.lt(0.).sum(axis=1).to_frame(name='衰退观点个数'), left_index=True, right_index=True)
        currency_count_df['宽松概率'] = currency_count_df['增长观点个数'] / (currency_count_df.sum(axis=1))

        return increase_count_df, currency_count_df


if __name__ == '__main__':
    EconomicCycle('2008-12-20', '2021-06-08', is_increment=0).calculate_economic_cycle()
