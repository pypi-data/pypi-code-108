"""
可转债估值测试
"""
import hbshare as hbs
import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import pickle
import os
from datetime import datetime, timedelta
from cb_pricing_BS import cbPricingBlackScholes
from cb_pricing_Tree import cbPricingTree
from cb_pricing_MC import cbPricingMC
from WindPy import w

w.start()


class CbValuation:
    """
    计算对应正股的波动率和股票价格
    """
    def __init__(self, date, stock_ticker):
        self.date = date
        self.stock_ticker = stock_ticker
        self._load_data()

    def _load_data(self):
        pre_dt = datetime.strptime(self.date, '%Y/%m/%d') - timedelta(days=400)
        pre_date = pre_dt.strftime('%Y%m%d')
        end_date = datetime.strptime(self.date, '%Y/%m/%d').strftime('%Y%m%d')
        sql_script = "SELECT SYMBOL, TDATE, TCLOSE FROM finchina.CHDQUOTE WHERE" \
                     " TDATE >= {} and TDATE <= {} and SYMBOL = {}".format(pre_date, end_date, self.stock_ticker)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(
            columns={"SYMBOL": "ticker", "TDATE": "trade_date", "TCLOSE": "price"})
        data['trade_date'] = data['trade_date'].apply(lambda x: str(x))
        data = data[data['price'] > 0]

        self.vol = data['price'].pct_change()[-250:].std() * np.sqrt(250)
        self.stock_price = data.set_index('trade_date').iloc[-1]['price']


class CbValuationTest:
    """
    批量计算可转债价值
    """
    def __init__(self, basic_info, bond_ytm):
        self.basic_info = basic_info
        self.bond_ytm = bond_ytm
        self.prepared_data = None
        self._load_data()
        self._load_cb_price()

    def _load_data(self):
        if os.path.exists("C:\\Users\\kai.zhang\\Desktop\\可转债\\cb_params.pkl"):
            with open("C:\\Users\\kai.zhang\\Desktop\\可转债\\cb_params.pkl", "rb") as f:
                self.prepared_data = pickle.load(f)
        else:
            basic_info = self.basic_info.copy()
            basic_info = basic_info[basic_info['发行信用等级'] != 'A']
            cb_id_list = basic_info['证券代码'].tolist()
            basic_info = basic_info.set_index('证券代码')
            prepared_data = {}
            for cb_id in tqdm(cb_id_list):
                ConvPrice = basic_info.loc[cb_id, '转股价']
                Maturity = datetime.strftime(basic_info.loc[cb_id, '到期日期'], '%Y/%m/%d')
                ConvertStart = 5.5
                coupon_info = basic_info.loc[cb_id, '票面利率说明']
                coupon = [float(x) for x in re.findall(r"\d+\.?\d*", coupon_info)]
                coupon[-1] = basic_info.loc[cb_id, '到期赎回价']

                recall = [ConvertStart,
                          basic_info.loc[cb_id, '赎回触发计算时间区间'].astype(int),
                          basic_info.loc[cb_id, '赎回触发计算最大时间区间'].astype(int),
                          basic_info.loc[cb_id, '赎回触发比例'].astype(int)]

                resell = [(basic_info.loc[cb_id, '相对回售期'] / 24).astype(int),
                          basic_info.loc[cb_id, '回售触发计算时间区间'].astype(int),
                          basic_info.loc[cb_id, '回售触发计算时间区间'].astype(int),
                          basic_info.loc[cb_id, '回售触发比例'].astype(int),
                          103]

                term_CB = {
                    "ConvPrice": ConvPrice,
                    "Maturity": Maturity,
                    "ConvertStart": ConvertStart,
                    "Coupon": coupon,
                    "Recall": recall,
                    "Resell": resell
                }
                term_CB['Recall'][-1] *= term_CB['ConvPrice'] / 100
                term_CB['Resell'][-2] *= term_CB['ConvPrice'] / 100
                term_CB['Resell'][-1] *= term_CB['ConvPrice'] / 100

                now_date = '2021/6/1'
                ticker = basic_info.loc[cb_id, '正股代码'].split('.')[0]

                cb_value = CbValuation(date=now_date, stock_ticker=ticker)
                vol, stock_price = cb_value.vol, cb_value.stock_price

                credit = basic_info.loc[cb_id, '发行信用等级']
                year_to_maturity = \
                    (datetime.strptime(Maturity, '%Y/%m/%d') - datetime.strptime(now_date, '%Y/%m/%d')).days // 365
                year_to_maturity = max(year_to_maturity, 1)

                rate = self.bond_ytm[self.bond_ytm['信用评级'] == credit][year_to_maturity].values[0] / 100

                prepared_data[cb_id] = {
                    "stock_price": stock_price,
                    "term_CB": term_CB,
                    "now_date": now_date,
                    "vol": vol,
                    "rate": rate
                }

            self.prepared_data = prepared_data

        with open("C:\\Users\\kai.zhang\\Desktop\\可转债\\cb_params.pkl", "wb") as f:
            pickle.dump(self.prepared_data, f)

    def _load_cb_price(self):
        basic_info = self.basic_info.copy()
        basic_info = basic_info[basic_info['发行信用等级'] != 'A']
        cb_id_list = basic_info['证券代码'].tolist()

        res = w.wsd(','.join(cb_id_list), "close", "2021-06-01", "2021-06-01", "")

        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch cb data error")
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times)
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times)
            data.columns = ['close']

        self.cb_price = data

    def calculate(self):
        bs_list = []
        tree_list = []
        mc_list = []
        for key, value in tqdm(self.prepared_data.items()):
            stock_price, term_CB, now_date, vol, rate = \
                value['stock_price'], value['term_CB'], value['now_date'], value['vol'], value['rate']

            # B-S估值
            straightBondValue, call_value = cbPricingBlackScholes(stock_price, term_CB, now_date, vol, rate)
            bs_list.append(straightBondValue + call_value)
            # 二叉树估值
            tree_list.append(cbPricingTree(stock_price, term_CB, now_date, vol, rate))
            # MC估值
            mc_list.append(cbPricingMC(stock_price, term_CB, now_date, vol, rate))

        valuation_df = pd.DataFrame({"cb_id": list(self.prepared_data.keys()), "B-S": bs_list,
                                     "tree": tree_list, "mc": mc_list})
        valuation_df = pd.merge(valuation_df, self.cb_price, left_on='cb_id', right_index=True)
        valuation_df.to_csv('C:\\Users\\kai.zhang\\Desktop\\可转债\\可转债估值结果.csv', index=False)


if __name__ == '__main__':
    # # 可转债的基本资料
    # term_CB = {
    #     "ConvPrice": 10.66,
    #     "Maturity": "2021/2/1",
    #     "ConvertStart": 5.5,
    #     "Coupon": [0.2, 0.5, 1.0, 1.5, 1.5, 106.6],
    #     "Recall": [5.5, 15, 30, 130],
    #     "Resell": [2, 30, 30, 70, 103]
    # }
    #
    # now_date = '2015/9/22'
    # ticker = '601727'
    #
    # cb_value = CbValuation(date=now_date, stock_ticker=ticker)
    # vol, stock_price = cb_value.vol, cb_value.stock_price
    # # 同等级/期限的企业债收益率
    # rate = 0.029659
    #
    # cb_price_bs = cbPricingBlackScholes(stock_price, term_CB, now_date, vol, rate)
    # cb_price_tree = cbPricingTree(stock_price, term_CB, now_date, vol, rate)
    # term_CB['Recall'][-1] *= term_CB['ConvPrice'] / 100
    # term_CB['Resell'][-2] *= term_CB['ConvPrice'] / 100
    # term_CB['Resell'][-1] *= term_CB['ConvPrice'] / 100
    # cb_price_mc = cbPricingMC(stock_price, term_CB, now_date, vol, rate)

    cb_info = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\可转债\\可转债基本资料.xlsx").dropna()
    ytm_data = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\可转债\\企业债到期收益率.xlsx")
    CbValuationTest(basic_info=cb_info, bond_ytm=ytm_data).calculate()