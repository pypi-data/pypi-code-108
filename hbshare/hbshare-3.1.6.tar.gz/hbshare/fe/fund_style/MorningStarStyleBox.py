"""
晨星基金风格箱模型
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from hbshare.fe.common.util.data_loader import MorningStarBoxStyleLoader
from hbshare.fe.common.util.verifier import verify_type, verify_simple_data_duplicate


class MorningStarStyleCalculator:
    def __init__(self, trade_date, mode="main"):
        """
        @param trade_date: 月末的交易日期
        @param mode: 模式，"main"代表是十大重仓的风格，"all"代表全持仓风格
        """
        self.trade_date = trade_date
        self.mode = mode
        self._load_data()
        self._verify()
        self._init_data_param()

    def _load_data(self):
        self.data_param = MorningStarBoxStyleLoader(self.trade_date, self.mode).load()

    def _verify(self):
        if not self.data_param:
            return
        equity_value = self.data_param.get('equity_value')
        verify_type(equity_value, 'equity_value', pd.DataFrame)
        verify_simple_data_duplicate(equity_value.index, 'equity_value.index')

        equity_growth = self.data_param.get('equity_growth')
        verify_type(equity_growth, 'equity_growth', pd.DataFrame)

        fund_holding = self.data_param.get('fund_holding')
        verify_type(fund_holding, 'fund_holding', pd.DataFrame)

    def _init_data_param(self):
        if not self.data_param:
            return
        equity_value = self.data_param.get('equity_value')
        equity_growth = self.data_param.get('equity_growth')
        fund_holding = self.data_param.get('fund_holding')

        self.quotation_date = self.data_param.get('quotation_date')
        idx = equity_value.index.intersection(equity_growth['ticker'].unique())
        self.equity_value = equity_value.reindex(idx)
        self.equity_growth = equity_growth[equity_growth['ticker'].isin(idx)]
        fund_holding = pd.pivot_table(fund_holding, index='ticker', columns='fund_id', values='weight').fillna(0.)
        idx = idx.intersection(fund_holding.index)
        fund_holding = fund_holding.reindex(idx)
        cols = fund_holding.sum()[fund_holding.sum() > 0.].index.tolist()
        self.fund_holding = fund_holding[cols]

    @staticmethod
    def _cal_cap_bound(equity_df, lower=0.75, upper=0.90):
        df = equity_df.copy()
        df.sort_values(by='marketValue', ascending=False, inplace=True)
        df['tmp'] = (df['marketValue'] / df['marketValue'].sum()).cumsum()
        lmt = df[df['tmp'] <= lower]['marketValue'].min()
        mst = df[df['tmp'] <= upper]['marketValue'].min()
        del df['tmp']
        l_cap = df[df['marketValue'] >= lmt]
        m_cap = df[(df['marketValue'] < lmt) & (df['marketValue'] >= mst)]
        s_cap = df[df['marketValue'] < mst]

        return mst, lmt, l_cap, m_cap, s_cap

    @staticmethod
    def _cal_value_score(data):
        df = data.copy()
        df['EP'] = 1.0 / df['PE']
        df['BP'] = 1.0 / df['PB']
        df['CFP'] = 1.0 / df['PCF']
        factor_list = ['EP', 'BP', 'CFP', 'DIVIDENDRATIO']
        value_df = df[factor_list].dropna(how='all').fillna(0.)
        value_df = value_df.apply(lambda x: x.rank() / len(x.dropna()))

        weight = pd.DataFrame(
            [[1. / len(factor_list)] * len(factor_list)] * len(value_df), index=value_df.index, columns=factor_list)
        weight = ~pd.isnull(value_df) * weight
        weight = weight.divide(weight.sum(axis=1), axis=0)

        value_series = weight.multiply(value_df).sum(axis=1)

        return value_series

    @staticmethod
    def _cal_growth_score(data):
        df = data.copy()
        factor_list = ['revenue', 'profit', 'asset']
        growth_df = df[factor_list].dropna(how='all')
        growth_df = growth_df.apply(lambda x: x.rank() / len(x.dropna()))

        weight = pd.DataFrame(
            [[1. / len(factor_list)] * len(factor_list)] * len(growth_df), index=growth_df.index, columns=factor_list)
        weight = ~pd.isnull(growth_df) * weight
        weight = weight.divide(weight.sum(axis=1), axis=0)

        growth_series = weight.multiply(growth_df).sum(axis=1)

        return growth_series

    @staticmethod
    def _lg(df):
        flag = sm.add_constant(np.arange(len(df)))
        ols_fit = sm.OLS(df.values, flag).fit()
        rate = ols_fit.params[1] / df.abs().mean()

        return rate

    def _calculate_growth_score(self):
        data = self.equity_growth.copy()
        revenue_cagr = pd.pivot_table(
            data, index='endDate', columns='ticker', values='revenue').sort_index().apply(self._lg)
        profit_cagr = pd.pivot_table(
            data, index='endDate', columns='ticker', values='net_profit').sort_index().apply(self._lg)
        asset_cagr = pd.pivot_table(
            data, index='endDate', columns='ticker', values='t_asset').sort_index().apply(self._lg)
        growth_score = revenue_cagr.to_frame('revenue').merge(
            profit_cagr.to_frame('profit'), left_index=True, right_index=True).merge(
            asset_cagr.to_frame('asset'), left_index=True, right_index=True)

        return growth_score

    def get_equity_score(self, growth_score):
        equity_df = self.equity_value.merge(growth_score, left_index=True, right_index=True)
        mst, lmt, l_cap, m_cap, s_cap = self._cal_cap_bound(equity_df)
        cut_list = [l_cap, m_cap, s_cap]
        raw_x_list = []
        for df in cut_list:
            value_series = self._cal_value_score(df)
            growth_series = self._cal_growth_score(df)
            vcg_series = (growth_series - value_series).dropna()

            vcg_df = pd.merge(
                vcg_series.to_frame('vcg'), equity_df['negMarketValue'],
                left_index=True, right_index=True).sort_values(by='vcg')
            vcg_df['tmp'] = vcg_df['negMarketValue'].cumsum() / vcg_df['negMarketValue'].sum()
            gt = vcg_df[vcg_df['tmp'] <= 2. / 3]['vcg'].max()
            vt = vcg_df[vcg_df['tmp'] <= 1. / 3]['vcg'].max()

            raw_x_list.append(100 * (1 + (vcg_series - vt) / (gt - vt)))

        raw_x = pd.concat(raw_x_list)
        raw_y = 100 * (1 + (np.log(equity_df['marketValue']) - np.log(mst)) / (np.log(lmt) - np.log(mst)))
        raw_df = pd.merge(raw_x.to_frame('vcg_score'), raw_y.to_frame('cap_score'),
                          left_index=True, right_index=True).reset_index()
        raw_df.rename(columns={"index": "ticker"}, inplace=True)

        return raw_df

    def get_construct_results(self):
        growth_score = self._calculate_growth_score()
        equity_score = self.get_equity_score(growth_score)

        vcg_series = equity_score.set_index('ticker')['vcg_score'].reindex(self.fund_holding.index)
        cap_series = equity_score.set_index('ticker')['cap_score'].reindex(self.fund_holding.index)
        holding_df = self.fund_holding.div(self.fund_holding.sum(), axis=1)
        fund_vcg = holding_df.T.dot(vcg_series)
        fund_cap = holding_df.T.dot(cap_series)
        fund_score = pd.merge(fund_cap.to_frame('cap_score'), fund_vcg.to_frame('vcg_score'),
                              left_index=True, right_index=True).reset_index()
        # category
        fund_score.loc[fund_score['cap_score'] < 100, 'cap_cate'] = "小盘"
        fund_score.loc[(fund_score['cap_score'] >= 100) & (fund_score['cap_score'] <= 200), 'cap_cate'] = "中盘"
        fund_score.loc[fund_score['cap_score'] > 200, 'cap_cate'] = "大盘"
        fund_score.loc[fund_score['vcg_score'] < 125, 'vcg_cate'] = "价值型"
        fund_score.loc[(fund_score['vcg_score'] >= 125) & (fund_score['vcg_score'] <= 175), 'vcg_cate'] = "平衡型"
        fund_score.loc[fund_score['vcg_score'] > 175, 'vcg_cate'] = "成长型"
        fund_score['category'] = fund_score['cap_cate'] + fund_score['vcg_cate']
        fund_score['type'] = self.mode
        # fund_score['trade_date'] = self.trade_date
        fund_score['trade_date'] = self.data_param['report_date']
        fund_score = fund_score[['trade_date', 'fund_id', 'type', 'cap_score', 'vcg_score', 'category']]

        # equity style
        equity_score.loc[equity_score['cap_score'] < 100, 'cap_cate'] = "小盘"
        equity_score.loc[(equity_score['cap_score'] >= 100) & (equity_score['cap_score'] <= 200), 'cap_cate'] = "中盘"
        equity_score.loc[equity_score['cap_score'] > 200, 'cap_cate'] = "大盘"
        equity_score.loc[equity_score['vcg_score'] < 100, 'vcg_cate'] = "价值型"
        equity_score.loc[(equity_score['vcg_score'] >= 100) & (equity_score['vcg_score'] <= 200), 'vcg_cate'] = "均衡型"
        equity_score.loc[equity_score['vcg_score'] > 200, 'vcg_cate'] = "成长型"
        equity_score['category'] = equity_score['cap_cate'] + equity_score['vcg_cate']
        equity_score['type'] = self.mode
        # equity_score['trade_date'] = self.quotation_date
        equity_score['trade_date'] = self.data_param['report_date']
        equity_score = equity_score[['trade_date', 'ticker', 'type', 'cap_score', 'vcg_score', 'category']]

        # wind_fund_cate = pd.read_excel("D:\\kevin\\Wind_2020_annual_style_cate.xlsx").dropna()
        # wind_fund_cate.columns = ['fund_id', 'name', 'fund_type', 'category_wind']
        # wind_fund_cate['fund_id'] = wind_fund_cate['fund_id'].apply(lambda x: x.split('.')[0])
        # wind_fund_cate['category_wind'] = wind_fund_cate['category_wind'].apply(lambda x: x[:4] + '型')
        # df = pd.merge(fund_score[['fund_id', 'category']], wind_fund_cate, on='fund_id')
        # df['cap_cate'] = df['category'].apply(lambda x: x[:2])
        # df['cap_cate_wind'] = df['category_wind'].apply(lambda x: x[:2])
        # df['vcg_cate'] = df['category'].apply(lambda x: x[2:])
        # df['vcg_cate_wind'] = df['category_wind'].apply(lambda x: x[2:])

        return {"equity_score": equity_score, "fund_score": fund_score}


if __name__ == '__main__':
    # 跑历史
    # from hbshare.rm_associated.util.data_loader import get_trading_day_list
    # date_list = get_trading_day_list('20100101', '20211115', frequency='month')
    #
    # for date in date_list:
    #     if date[4:6] in ['01', '07', '10']:
    #         res = MorningStarStyleCalculator(date, mode='main').get_construct_results()
    #     elif date[4:6] in ['04', '08']:
    #         res = MorningStarStyleCalculator(date, mode='all').get_construct_results()
    #         print(res)
    #     else:
    #         res = None
    #     print("当期日期: {}".format(date))
    #     print(res)
    res = MorningStarStyleCalculator('20210430', mode='main').get_construct_results()
    print(res)
