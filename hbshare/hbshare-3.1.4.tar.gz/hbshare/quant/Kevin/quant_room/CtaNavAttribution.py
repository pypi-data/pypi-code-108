"""
CTA基金的净值归因模块
结构：
1、整体区间的归因结果；
2、滚动月度的归因结果：暴露+收益的时序图；
"""
import pandas as pd
from sqlalchemy import create_engine
from hbshare.fe.common.util.verifier import verify_type
from hbshare.fe.common.util.data_loader import CtaNavAttributionLoader
from hbshare.fe.common.util.regressions import Regression
from hbshare.fe.common.util.config import cta_factors
# from hbshare.rm_associated.util.config import cta_factors, cta_factor_map_dict
# from hbshare.rm_associated.util.plot_util import draw_summary_bar_style, draw_area_bar, draw_heatmap


class CtaNavAttribution:
    def __init__(self, fund_id, start_date, end_date):
        self.fund_id = fund_id
        self.start_date = start_date
        self.end_date = end_date
        self._verify_input_param()
        self._load_data()

    def _verify_input_param(self):
        verify_type(self.fund_id, 'fund_id', str)
        verify_type(self.start_date, 'start_date', str)
        verify_type(self.end_date, 'end_date', str)

    def _load_data(self):
        data = CtaNavAttributionLoader(
            self.fund_id, self.start_date, self.end_date, cta_factors).load()
        self.trading_day_list = data['trading_day_list']
        self.fund_nav_series = data['fund_nav_series']
        self.factor_data = data['factor_data']

    @staticmethod
    def _process_data(df):
        factor_df = df.copy()
        factor_df['rev_short'] = -1 * factor_df['tsmom_d1']
        factor_df['tendency_medium'] = factor_df[['tsmom_d2', 'tsmom_d3', 'tsmom_d5']].mean(axis=1)
        # factor_df['tendency_long'] = factor_df[['tsmom_d10', 'tsmom_d20', 'tsmom_d30']].mean(axis=1)
        factor_df['tendency_long'] = factor_df[['tsmom_d10', 'tsmom_d20']].mean(axis=1)
        factor_df['roll_return'] = factor_df['carry_d20_q70']
        factor_df['basis_mom_short'] = factor_df['tsbasismom_d5']
        factor_df['basis_mom_long'] = factor_df['tsbasismom_d20']

        # factor_df = factor_df[['tsmom_d5', 'tsmom_d20', 'roll_return', 'basis_mom_5', 'basis_mom_20']]
        # factor_df = factor_df[['tendency_medium', 'tendency_long', 'roll_return', 'basis_mom_5', 'basis_mom_20']]
        # factor_df = factor_df[['tsmom_d1', 'tsmom_d5', 'tsmom_d20', 'roll_return', 'basis_mom_5', 'basis_mom_20']]
        factor_df = factor_df[
            ['rev_short', 'tendency_medium', 'tendency_long', 'roll_return', 'basis_mom_short', 'basis_mom_long']]

        return factor_df

    @staticmethod
    def _calculate_period_attr(return_series, factor_df, start_date, end_date):
        lower, upper = None, None
        strategy_method, attribution_effort = 'ols', 'weak'

        period_return_series = return_series[(return_series.index > start_date) & (return_series.index <= end_date)]
        period_factor_df = factor_df[(factor_df.index > start_date) & (factor_df.index <= end_date)]

        sr_obj = Regression(period_factor_df, period_return_series, upper=upper, lower=lower,
                            method=strategy_method, effort=attribution_effort)
        solve_dict = sr_obj.solve()
        factor_beta_series = solve_dict['solution'].reindex(
            ['rev_short', 'tendency_medium', 'tendency_long', 'roll_return', 'basis_mom_short', 'basis_mom_long'])
        r_square = solve_dict['r_square']

        calc_df = factor_df[factor_beta_series.index.tolist()]
        factor_cum_return = calc_df.fillna(0.).add(1.0).prod().subtract(1.0)
        perf_attr = factor_beta_series.multiply(factor_cum_return)
        perf_attr = pd.merge(factor_beta_series.to_frame('factor_exposure'), perf_attr.to_frame('return_attr'),
                             left_index=True, right_index=True)

        return perf_attr, r_square

    def calculate(self):
        idx = self.fund_nav_series.index.intersection(self.factor_data.index)
        return_series = self.fund_nav_series.reindex(idx).sort_index().pct_change().dropna()
        factor_df = self.factor_data.reindex(idx).sort_index().pct_change().dropna()
        factor_df = self._process_data(factor_df)

        # overall attr
        perf_attr, r_square = self._calculate_period_attr(
            return_series, factor_df, self.start_date, self.end_date)
        perf_attr.index.name = 'style_factor'
        attr_summary = perf_attr.reset_index()

        # rolling attr
        exposure_list = []
        return_attr_list = []
        ac_date_list = []
        r_square_list = []
        date_list = [x for x in self.trading_day_list if x >= self.start_date]
        for date in date_list:
            period_start = self.trading_day_list[self.trading_day_list.index(date) - 6]
            period_nav_series = self.fund_nav_series[
                (self.fund_nav_series.index > period_start) & (self.fund_nav_series.index <= date)]
            if len(period_nav_series) <= 20:
                continue
            perf_attr, r_square = self._calculate_period_attr(
                return_series, factor_df, period_start, date)
            ac_date_list.append(date)
            r_square_list.append(r_square)

            exposure_series = perf_attr['factor_exposure']
            exposure_series.name = date

            return_attr_series = perf_attr['return_attr']
            return_attr_series.name = date

            exposure_list.append(exposure_series)
            return_attr_list.append(return_attr_series)

        exposure_series_all = pd.concat(exposure_list, axis=1).T.sort_index()
        return_attr_series_all = pd.concat(return_attr_list, axis=1).T.sort_index()
        r_square_series = pd.Series(index=ac_date_list, data=r_square_list)

        output = {
            "attr_summary": attr_summary,
            "exposure_series": exposure_series_all,
            "return_attr_series": return_attr_series_all,
            "r_square_series": r_square_series
        }

        return output


def get_fund_list_from_mysql():
    sql_params = {
        "ip": "192.168.223.152",
        "user": "readonly",
        "pass": "c24mg2e6",
        "port": "3306",
        "database": "work"
    }
    engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'],
                                                            sql_params['ip'],
                                                            sql_params['port'], sql_params['database'])

    sql_script = "SELECT * FROM fund_list where class = 'cta'"
    engine = create_engine(engine_params)
    fund_info = pd.read_sql(sql_script, engine)
    # fof
    fund_info = fund_info[fund_info['fof'] == 1]

    return fund_info


if __name__ == '__main__':
    # fund_df = get_fund_list_from_mysql()
    # fund_df = fund_df[['code', 'name', 'type']]
    # fund_df = fund_df[~fund_df['code'].isin(['SGZ853', 'SJJ884'])]
    #
    # for f_id in fund_df['code'].tolist():
    #     attr_res = CtaNavAttribution(f_id, '20191227', '20210903').get_construct_result()
    #     fund_df.loc[fund_df['code'] == f_id,
    #                 ['tendency_short', 'tendency_medium', 'tendency_long',
    #                  'roll_return', 'basis_mom_5', 'basis_mom_20', 'r_square']] = attr_res['exposure'].tolist()[1:]
    #
    # print(fund_df)

    res = CtaNavAttribution('SGU333', '20191227', '20211015').calculate()

    # factor_order = list(cta_factor_map_dict.keys())
    # attribution_df = res['attr_summary'].set_index('style_factor').reindex(factor_order)
    # attribution_df['factor_exposure'] = attribution_df['factor_exposure'].round(2)
    # attribution_df['return_attr'] = (attribution_df['return_attr'] * 100).round(2)
    # attribution_df.index = attribution_df.index.map(cta_factor_map_dict)
    # summary_bar = draw_summary_bar_style(attribution_df)
    # summary_bar.render("D:\\kevin\\123.html")
    #
    # exposure_series = res['exposure_series'].round(3)
    # exposure_series.columns = [cta_factor_map_dict[x] for x in exposure_series.columns]
    # exposure_heatmap = draw_heatmap(exposure_series, title="因子暴露时序分析", min_value=-1, max_value=1)
    # exposure_heatmap.render('D:\\kevin\\456.html')
    #
    # return_attr_series = (res['return_attr_series'][factor_order] * 100).round(2)
    # return_attr_series.columns = [cta_factor_map_dict[x] for x in return_attr_series.columns]
    # return_attr_stack_bar = draw_area_bar(return_attr_series, title="风格收益贡献时序分析")
    # return_attr_stack_bar.render('D:\\kevin\\789.html')