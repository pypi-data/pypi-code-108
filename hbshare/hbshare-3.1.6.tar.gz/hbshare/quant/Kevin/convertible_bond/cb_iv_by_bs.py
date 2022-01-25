"""
转债隐含波动率的计算程序
"""
import pandas as pd
import re
from cb_pricing_BS import cbPricingBlackScholes
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
# from hbshare.rm_associated.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class cbIVCalculator:
    def __init__(self, trade_date, is_increment=1):
        self.trade_date = trade_date
        self.is_increment = is_increment
        self.table_name = 'cb_iv_and_premium'
        self._load_data()

    def _load_data(self):
        # 存续
        basic_info_1 = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\可转债\\data\\可转债基本信息.xlsx").dropna()
        # 已摘牌未到期
        basic_info_2 = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\可转债\\data\\已摘牌未到期可转债.xlsx").dropna()
        # 已经退市
        basic_info_3 = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\可转债\\data\\已退市可转债.xlsx").dropna()
        basic_info = pd.concat(
            [basic_info_1, basic_info_2, basic_info_3], axis=0).sort_values(by='证券代码').drop_duplicates()
        basic_info.rename(columns={basic_info.columns[-1]: "redeem"}, inplace=True)
        basic_info['temp1'] = basic_info['上市日期'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        basic_info['temp2'] = basic_info['摘牌日期'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # 2018年开始回测，18年之前的剔除
        basic_info = basic_info[(basic_info['temp2'] > self.trade_date) & (basic_info['temp1'] < self.trade_date)]
        cb_id_list = basic_info['证券代码'].unique()
        # 转股价 & 转债收盘价
        res = w.wss(','.join(cb_id_list), "convprice,close", "tradeDate={};priceAdj=U;cycle=D".format(self.trade_date))
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch ConvPrice data error: trade_date = {}".format(self.trade_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Codes).T
        data.index.name = '证券代码'
        data = data.rename(columns={"CONVPRICE": "ConvPrice", "CLOSE": "cb_price"}).reset_index().dropna()
        basic_info = pd.merge(basic_info, data, on='证券代码')
        # 正股收盘价
        ticker_list = basic_info['正股代码'].unique()
        res = w.wss(','.join(ticker_list), "close", "tradeDate={};priceAdj=U;cycle=D".format(self.trade_date))
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch stock close data error: trade_date = {}".format(self.trade_date))
        else:
            data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times)
        data.columns = ['closePrice']
        data.index.name = "正股代码"
        data = data.reset_index().dropna()
        basic_info = pd.merge(basic_info, data, on='正股代码')

        self._extract_info(basic_info)

        trade_dt = datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - timedelta(days=20)).strftime('%Y%m%d')
        res = w.edb("M1001795", pre_date, self.trade_date, "Fill=Previous")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch R007 data error: trade_date = {}".format(self.trade_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
        data.index.name = 'trade_date'
        data.reset_index(inplace=True)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # rf_rate = data.set_index('trade_date').loc[self.trade_date, 'M1001795']
        rf_rate = data[data['trade_date'] <= self.trade_date]['M1001795'].tolist()[-1]

        self.rf_rate = rf_rate / 100.

    def _extract_info(self, df):
        basic_info = df.set_index('证券代码')
        info_dict = {}
        for cb_code in basic_info.index.tolist():
            list_date = datetime.strftime(basic_info.loc[cb_code, '上市日期'], '%Y/%m/%d')
            Maturity = datetime.strftime(basic_info.loc[cb_code, '摘牌日期'], '%Y/%m/%d')
            ticker = basic_info.loc[cb_code, '正股代码']
            coupon_list = [float(x) for x in re.findall(r"\d+\.?\d*", basic_info.loc[cb_code, '票面利率说明'])]
            coupon_list[-1] = basic_info.loc[cb_code, 'redeem']
            ConvPrice = basic_info.loc[cb_code, 'ConvPrice']
            cb_price = basic_info.loc[cb_code, 'cb_price']
            stock_price = basic_info.loc[cb_code, 'closePrice']

            info_dict[cb_code] = {"ticker": ticker,
                                  "list_date": list_date,
                                  "Maturity": Maturity,
                                  "Coupon": coupon_list,
                                  "ConvPrice": ConvPrice,
                                  "cb_price": cb_price,
                                  "stock_price": stock_price
                                  }

        self.data_param = info_dict

    @staticmethod
    def _binary_search(param):
        stock_price, cb_param, trade_date, rf_rate, cb_price = param

        low = 0
        height = 5
        bond_value, option_value = cbPricingBlackScholes(
            stock_price, cb_param, trade_date, height, rf_rate, isPrint=False)
        while height - low > 0.0001:
            mid = (low + height) / 2
            if cbPricingBlackScholes(
                    stock_price, cb_param, trade_date, mid, rf_rate, isPrint=False)[1] < cb_price - bond_value:
                low = mid
            else:
                height = mid

        return round(height, 4)

    def get_cb_volatility(self):
        data_param = self.data_param

        code_list = []
        premium_list = []
        iv_list = []
        for cb_code, cb_param in data_param.items():
            stock_price = cb_param['stock_price']
            trade_date = datetime.strptime(self.trade_date, '%Y%m%d').strftime('%Y/%m/%d')

            if cb_param['list_date'] > self.trade_date:
                continue

            rf_rate = self.rf_rate
            cb_price = cb_param['cb_price']
            cb_value = 100 * stock_price / cb_param['ConvPrice']
            premium = (cb_price - cb_value) / cb_value

            param = (stock_price, cb_param, trade_date, rf_rate, cb_price)
            iv = self._binary_search(param)

            code_list.append(cb_code)
            premium_list.append(premium)
            iv_list.append(iv)

        iv_df = pd.DataFrame({"code": code_list, "premium": premium_list, "iv": iv_list})
        # outlier
        # iv_df = iv_df[(iv_df['iv'] > 0.0001) & (iv_df['iv'] < 1)]
        iv_df['trade_date'] = self.trade_date
        iv_df['ticker'] = iv_df['code'].apply(lambda x: x.split('.')[0])
        iv_df['premium'] = iv_df['premium'].round(4)

        return iv_df[['trade_date', 'ticker', 'iv', 'premium']]

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_cb_volatility()
            sql_script = "delete from {} where trade_date = {}".format(
                self.table_name, self.trade_date)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table cb_iv_and_premium(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(20),
                iv decimal(5, 4),
                premium decimal(5, 4)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_cb_volatility()
            WriteToDB().write_to_db(data, self.table_name)


class CBMarketIV:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM cb_iv_and_premium WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        data = data[(data['iv'] > 0.001) & (data['iv'] < 1)]

        self.data = data[['trade_date', 'cr5', 'cr10', 'avg_mkt', 'close']]


if __name__ == '__main__':
    # sdate = '20210101'
    # edate = '20210924'
    # trading_day_list = get_trading_day_list(sdate, edate, frequency="day")
    #
    # from tqdm import tqdm
    # all_df = []
    # for date in tqdm(trading_day_list):
    #     cbIVCalculator(trade_date=date, is_increment=1).get_construct_result()

    cbIVCalculator('20210104', is_increment=1).get_construct_result()

    # CBMarketIV('20180101', '20210924')

    # from tqdm import tqdm
    # all_df = []
    # for date in tqdm(trading_day_list):
    #     res_df = cbIVCalculator(trade_date=date).get_construct_result()
    #     all_df.append(res_df)
    #
    # all_df = pd.concat(all_df)
    # all_df.to_csv('D:\\kevin\\可转债隐含波动率.csv', index=False)

    #
    # all_df = pd.read_csv("D:\\kevin\\可转债隐含波动率.csv", dtype={"trade_date": str})
    # a = all_df.groupby('trade_date')['iv'].quantile(0.2).to_frame(name='low').merge(
    #     all_df.groupby('trade_date')['iv'].quantile(0.5).to_frame(name='medium'), left_index=True, right_index=True).merge(
    #     all_df.groupby('trade_date')['iv'].quantile(0.8).to_frame(name='high'), left_index=True, right_index=True)
    # a = a[a.index <= '20210917']