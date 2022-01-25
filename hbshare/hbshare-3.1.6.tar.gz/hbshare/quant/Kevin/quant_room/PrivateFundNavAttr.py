"""
私募指增产品2021年以来的净值归因
"""
import os
import pandas as pd
from datetime import datetime
import hbshare as hbs
from hbshare.fe.common.util.regressions import Regression


class PrivateFundNavAttr:
    def __init__(self, path, start_date, end_date, nav_frequency='day'):
        self.path = path
        self.start_date = start_date
        self.end_date = end_date
        self.nav_frequency = nav_frequency
        self._load_data()

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isWeekEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    def _load_fund_nav_data(self):
        fund_info = pd.read_excel(os.path.join(self.path, '股票量化池.xlsx'), sheet_name=0, header=1)
        fund_info = fund_info.fillna(method='ffill')
        fund_info = fund_info[fund_info['策略类型'] == '指数增强'][['分类', '基金管理人', '基金简称', '基金代码', '净值状态']]
        fund_nav_dict = dict()
        # from sql
        fund_id_list = fund_info[fund_info['净值状态'] == 'DB']['基金代码'].tolist()
        for fund_id in fund_id_list:
            fund_name = fund_info.set_index('基金代码').loc[fund_id, '基金简称']
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data'])
            fund_nav_dict[fund_name] = data.set_index('TRADEDATE')['ADJ_NAV']
        # from excel
        raw_dict = pd.read_excel(os.path.join(self.path, '指增净值.xlsx'), sheet_name=None)
        for fund_name, nav_df in raw_dict.items():
            if type(nav_df['净值日期'].tolist()[0]) != str:
                nav_df['净值日期'] = nav_df['净值日期'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            nav_df['净值日期'] = nav_df['净值日期'].apply(lambda x: x.replace('-', ''))
            nav_df = nav_df[
                (nav_df['净值日期'] >= self.start_date) & (nav_df['净值日期'] <= self.end_date)].sort_values(by='净值日期')
            fund_nav_dict[fund_name] = nav_df.set_index('净值日期')['累计单位净值']
        # 增加对比: 西部利得量化成长
        fund_name = '西部利得量化成长'
        sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.hbcl accumulate_return from " \
                     "funddb.jjxx1 a, funddb.jjhb b where a.cpfl = '2' and a.jjdm = b.jjdm " \
                     "and a.jjzt not in ('3', 'c') " \
                     "and a.m_opt_type <> '03' and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                     "order by b.jzrq".format('000006', self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script)
        data = pd.DataFrame(res['data'])
        data['ADJ_NAV'] = 0.01 * data['ACCUMULATE_RETURN'] + 1
        fund_nav_dict[fund_name] = data.set_index('TRADEDATE')['ADJ_NAV']

        # 周度版本
        if self.nav_frequency == 'week':
            trading_day_list = self._load_calendar()
            # 周度采样
            for name, nav_df in fund_nav_dict.items():
                fund_nav_dict[name] = nav_df.reindex(trading_day_list).dropna()
            # 补充几只
            f_dict = {"灵均进取1号": "SW3470", "鸣石春天十三号": "SX2090", "世纪前沿指数增强2号": "SGP682", "念空瑞景1号": "SGZ812"}
            for name, fund_id in f_dict.items():
                sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                             "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                             "and a.jjzt not in ('3') " \
                             "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                             "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
                res = hbs.db_data_query("highuser", sql_script, page_size=5000)
                data = pd.DataFrame(res['data'])
                fund_nav_dict[name] = data.set_index('TRADEDATE')['ADJ_NAV']
            # 邮件中提取的净值数据
            append_nav_dict = pd.read_excel(os.path.join(self.path, '佳期指增产品历史业绩.xlsx'), sheet_name=None)
            for fund_name, nav_df in append_nav_dict.items():
                nav_df['净值日期'] = nav_df['净值日期'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
                nav_df = nav_df[(nav_df['净值日期'] >= self.start_date) & (nav_df['净值日期'] <= self.end_date)]
                fund_nav_dict[fund_name] = nav_df.set_index('净值日期')['单位净值']

        self.fund_nav_dict = fund_nav_dict

    def _load_factor_data(self):
        """
        芯片：国证芯片
        锂电池：锂电池（中信）
        化工：细分化工
        有色：中证有色
        光伏：光伏产业
        @return:
        """
        factor_name_dict = {
            "创成长": "399296", "科创50": "000688", "有色": "930708", "化工": "000813",
            "芯片": "980017", "光伏": "931151", "新能源车": "399417"}
        factor_data = []
        for key, value in factor_name_dict.items():
            sql_script = "SELECT JYRQ as TRADEDATE, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' and JYRQ >= " \
                         "{} and JYRQ <= {}".format(value, self.start_date, self.end_date)
            res = hbs.db_data_query('readonly', sql_script)
            data = pd.DataFrame(res['data'])
            # data['factor_ret'] = data['TCLOSE'].pct_change()
            data['factor_name'] = key
            data = data[['TRADEDATE', 'factor_name', 'TCLOSE']].dropna()
            factor_data.append(data)

        factor_data = pd.concat(factor_data)
        factor_data = pd.pivot_table(
            factor_data, index='TRADEDATE', columns='factor_name', values='TCLOSE').sort_index()

        self.factor_data = factor_data

    def _load_data(self):
        self._load_fund_nav_data()
        self._load_factor_data()

    @staticmethod
    def _perf_attr(account_return, factor_df, beta_series):
        calc_df = factor_df[beta_series.index.tolist()]

        idx = account_return.index.intersection(calc_df.index)
        calc_df = calc_df.loc[idx]

        factor_cum_return = calc_df.fillna(0.).add(1.0).prod().subtract(1.0)
        perf_attr = beta_series.multiply(factor_cum_return)
        perf_attr = pd.merge(beta_series.to_frame('factor_exposure'), perf_attr.to_frame('return_attr'),
                             left_index=True, right_index=True)

        return perf_attr

    def get_construct_result(self):
        # 回归参数
        lower, upper = None, None
        strategy_method, attribution_effort = 'ols', 'weak'

        attr_df = []
        for name, nav_df in self.fund_nav_dict.items():
            nav_df = nav_df.sort_index()
            idx = nav_df.index.intersection(self.factor_data.index)
            portfolio_return_series = nav_df.reindex(idx).pct_change().dropna()
            factor_df = self.factor_data.reindex(idx).pct_change().dropna()

            # from statsmodels.stats.outliers_influence import variance_inflation_factor
            # import numpy as np
            # name = factor_df.columns
            # x = np.matrix(factor_df)
            # VIF_list = [variance_inflation_factor(x, i) for i in range(x.shape[1])]
            # VIF = pd.DataFrame({'feature': name, "VIF": VIF_list})

            # factor_df = factor_df[['光伏', '化工', '有色', '芯片', '锂电池']]

            sr_obj = Regression(factor_df, portfolio_return_series,
                                upper=upper, lower=lower,
                                method=strategy_method, effort=attribution_effort)
            solve_dict = sr_obj.solve()
            factor_beta_series = solve_dict['solution_with_alpha']
            factor_beta_series.loc['r_square'] = solve_dict['r_square']

            factor_beta_series = factor_beta_series.to_frame('exposure')
            factor_beta_series.index.name = 'factor_name'
            factor_beta_series.reset_index(inplace=True)
            factor_beta_series['fund_name'] = name
            attr_df.append(factor_beta_series)

        attr_df = pd.concat(attr_df)
        attr_df = pd.pivot_table(attr_df, index='fund_name', columns='factor_name', values='exposure')
        cols = [x for x in attr_df.columns if x not in ['alpha', 'r_square']]
        if self.nav_frequency == 'day':
            attr_df['alpha'] *= 5
        attr_df.rename(columns={"alpha": "weekly_alpha", "fund_name": "标的名称"}, inplace=True)
        attr_df = attr_df[['weekly_alpha'] + cols + ['r_square']].round(5).reset_index()

        return attr_df


if __name__ == '__main__':
    attr_res = PrivateFundNavAttr('D:\\kevin\\绩效归因\\指增净值归因', '20201231', '20210806', 'day').get_construct_result()
    attr_res.to_csv('D:\\kevin\\attr_df.csv', index=False, encoding='gbk')