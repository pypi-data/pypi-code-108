#!/usr/bin/python
#coding:utf-8

import numpy as np
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
from openpyxl import load_workbook
import hbshare as hbs


class PortfolioIndexCalculator:
    def __init__(self, file_path):
        self.file_path = file_path
        self._init_params()
        self._load_data()

    def _init_params(self):
        data = pd.read_excel(self.file_path, sheet_name=0, dtype=str)
        self.benchmark_id_dict = data.filter(regex="基准_*").to_dict(orient='records')[0]
        self.start_date = data['起始日期'].values[0]
        self.end_date = data['结束日期'].values[0]
        weight_df = pd.read_excel(self.file_path, sheet_name=1)
        self.portfolio_weight_series = weight_df.set_index('产品代码')['权重']

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        return df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    def _load_fund_nav(self):
        data = []
        for fund_id in self.portfolio_weight_series.index.tolist():
            sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            df = pd.DataFrame(res['data'])
            data.append(df)
        data = pd.concat(data)

        data.rename(columns={"FUND_ID": "fund_id", "ADJ_NAV": "adj_nav"}, inplace=True)

        return data

    def _load_benchmark_data(self):
        data = []
        for key, value in self.benchmark_id_dict.items():
            sql_script = "SELECT JYRQ, ZQDM, SPJG FROM funddb.ZSJY WHERE ZQDM = '{}' and " \
                         "JYRQ >= {} and JYRQ <= {}".format(value, self.start_date, self.end_date)
            res = hbs.db_data_query('readonly', sql_script)
            df = pd.DataFrame(res['data'])
            df = df.rename(columns={"JYRQ": "tradeDate", "SPJG": "close"}).set_index('tradeDate')['close']
            df.name = key
            data.append(df)

        data = pd.concat(data, axis=1)

        return data

    def _load_data(self):
        # calendar
        self.calendar_df = self._load_calendar()
        weekend_list = self.calendar_df[
            (self.calendar_df['isWeekEnd'] == 1) & (self.calendar_df['isOpen'] == 1)]['calendarDate'].tolist()
        # fund_nav
        fund_nav_df = self._load_fund_nav()
        nav_df = pd.pivot_table(fund_nav_df, index='tradeDate', columns='fund_id', values='adj_nav')
        natural_days = [x.strftime("%Y%m%d") for x in pd.date_range(nav_df.index[0], nav_df.index[-1])]
        nav_df = nav_df.reindex(natural_days).interpolate().reindex(weekend_list)
        self.nav_df = nav_df / nav_df.iloc[0]
        # benchmark
        self.benchmark_nav_df = self._load_benchmark_data()

    @staticmethod
    def cal_annual_return(return_series):
        T = len(return_series)
        annual_return = (1 + return_series).prod() ** (52 / T) - 1

        return annual_return

    @staticmethod
    def cal_annual_volatility(return_series):
        vol = return_series.std() * np.sqrt(52)

        return vol

    @staticmethod
    def cal_max_drawdown(nav_series):
        drawdown_series = nav_series / (nav_series.cummax()) - 1

        return drawdown_series.min()

    def cal_sharpe_ratio(self, return_series, rf):
        annual_return = self.cal_annual_return(return_series)
        vol = self.cal_annual_volatility(return_series)
        sharpe_ratio = (annual_return - rf) / vol

        return sharpe_ratio

    @staticmethod
    def cal_month_ret(return_series):
        name = return_series.name
        df = return_series.copy().reset_index()
        df['month'] = df['tradeDate'].apply(lambda x: x[:6])
        month_ret = df.groupby('month')[name].apply(lambda x: (1 + x).prod() - 1)

        max_rise = month_ret.max() if month_ret.max() > 0 else 0
        max_decline = month_ret.min() if month_ret.min() < 0 else 0
        win_ratio = len(month_ret[month_ret > 0]) / month_ret.shape[0]

        return max_rise, max_decline, win_ratio

    def cal_performance_index(self, return_series, nav_series):
        annual_return = self.cal_annual_return(return_series)
        annual_vol = self.cal_annual_volatility(return_series)
        max_drawdown = self.cal_max_drawdown(nav_series)
        sharpe_ratio = self.cal_sharpe_ratio(return_series, rf=0.015)
        calmar_ratio = annual_return / np.abs(max_drawdown)
        max_rise, max_decline, win_ratio = self.cal_month_ret(return_series)

        df = pd.DataFrame(index=["指标", "年化收益", "年化波动", "最大回撤", "夏普比率", "卡玛比率",
                                 "最大月度涨幅", "最大月度跌幅", "月胜率"],
                          data=[return_series.name, annual_return, annual_vol,
                                max_drawdown, sharpe_ratio, calmar_ratio,
                                max_rise, max_decline, win_ratio]).T

        return df

    @staticmethod
    def get_pre_N_date(dt, N):
        pre_dt = dt - MonthEnd(N)
        day = min(pre_dt.day, dt.day)
        actual_pre_date = datetime(pre_dt.year, pre_dt.month, day).strftime('%Y%m%d')

        return actual_pre_date

    def write_to_excel(self, output):
        writer = pd.ExcelWriter(self.file_path, engine='openpyxl')
        book = load_workbook(self.file_path)
        writer.book = book

        fof_nav = output["组合净值"].reset_index().rename(columns={"tradeDate": "日期", "组合": "FOF组合"})
        fof_nav.to_excel(writer, "组合净值", index=False)
        fof_ret = output["组合收益"].reset_index().rename(columns={"tradeDate": "日期", "组合": "FOF组合"})
        fof_ret.to_excel(writer, "组合收益", index=False)
        output['业绩指标'].to_excel(writer, "业绩风险指标", index=False)
        output['区间收益'].to_excel(writer, "业绩风险指标", startrow=10, index=False)
        output['年度收益'].to_excel(writer, "业绩风险指标", startrow=20, index=False)
        output['子基金相关性'].to_excel(writer, "业绩风险指标", startrow=30)

        writer.save()
        writer.close()

    def get_construct_result(self):
        # 组合收益数据
        portfolio_nav = self.nav_df.dot(self.portfolio_weight_series)
        benchmark_nav = self.benchmark_nav_df.reindex(portfolio_nav.index)
        benchmark_nav /= benchmark_nav.iloc[0]
        total_nav_df = pd.merge(
            portfolio_nav.to_frame('组合'), benchmark_nav, left_index=True, right_index=True)
        total_return_df = total_nav_df.pct_change().dropna()
        # 业绩指标
        performance_df = []
        for name in total_return_df.columns:
            df = self.cal_performance_index(total_return_df[name], total_nav_df[name])
            performance_df.append(df)
        performance_df = pd.concat(performance_df)
        # 区间收益
        end_dt = datetime.strptime(total_return_df.index[-1], "%Y%m%d")
        year_start = total_return_df.index[-1][:4] + '0101'
        period_ret1 = (1 + total_return_df[total_return_df.index > year_start]).prod() - 1
        pre_1_month = self.get_pre_N_date(end_dt, 1)
        period_ret_1M = (1 + total_return_df[total_return_df.index > pre_1_month]).prod() - 1
        pre_3_month = self.get_pre_N_date(end_dt, 3)
        period_ret_3M = (1 + total_return_df[total_return_df.index >= pre_3_month]).prod() - 1
        pre_6_month = self.get_pre_N_date(end_dt, 6)
        period_ret_6M = (1 + total_return_df[total_return_df.index >= pre_6_month]).prod() - 1
        pre_12_month = self.get_pre_N_date(end_dt, 12)
        period_ret_12M = (1 + total_return_df[total_return_df.index >= pre_12_month]).prod() - 1
        all_ret = (1 + total_return_df).prod() - 1
        period_ret = pd.concat(
            [period_ret1, period_ret_1M, period_ret_3M, period_ret_6M, period_ret_12M, all_ret], axis=1)
        period_ret.reset_index(inplace=True)
        period_ret.columns = ['指标', '今年以来', '近一月', '近3月', '近6月', '近一年', '起始以来']
        # 年度收益
        tmp = total_return_df.copy()
        tmp['trade_date'] = tmp.index
        tmp['year'] = tmp['trade_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d').year)
        year_ret = tmp.groupby('year').apply(
            lambda x: (1 + x[[a for a in x.columns if a not in ['trade_date', 'year']]]).prod() - 1).T.reset_index()
        year_ret.rename(columns={"index": "指标"}, inplace=True)
        # 子基金相关性
        fund_corr = self.nav_df.pct_change().dropna().corr()

        output = {"组合收益": total_return_df,
                  "组合净值": total_nav_df,
                  "业绩指标": performance_df,
                  "区间收益": period_ret,
                  "年度收益": year_ret,
                  "子基金相关性": fund_corr}

        self.write_to_excel(output)

        return output


if __name__ == '__main__':
    results = PortfolioIndexCalculator("D:\\kevin\\好买30投前指标模板.xlsx").get_construct_result()
