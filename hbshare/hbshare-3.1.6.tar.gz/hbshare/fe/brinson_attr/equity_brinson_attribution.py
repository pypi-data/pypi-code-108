"""
公募基金的Brinson持仓归因模型
"""
import pandas as pd
from hbshare.fe.common.util.logger import logger
from hbshare.fe.common.util.data_loader import EquityBrinsonAttributionLoader
from hbshare.fe.common.util.verifier import verify_type, verify_trading_day, \
    verify_df_not_null, verify_simple_data_duplicate
from hbshare.fe.common.util.config import industry_names
# from hbshare.rm_associated.util.helper_func import \
#     compute_attr_linking_coef, accumulate_timing_return, accumulate_management_return
# from hbshare.rm_associated.util.plot_util import draw_brinson_area_bar, draw_heatmap_brinson, \
#     draw_weight_compare_brinson


class EquityBrinsonAttributionOutputs:
    def __init__(self):
        self.realized_period_attr_df = None
        self.sector_attr_df = None

    def to_dict(self):
        return {
            "realized_period_attr_df": self.realized_period_attr_df,
            "sector_attr_df": self.sector_attr_df
        }


class EquityBrinsonAttribution:
    def __init__(self, fund_id, benchmark_id, start_date, end_date):
        """
        @param fund_id: 公募基金代码
        @param benchmark_id: 基准股票指数id
        @param start_date: 起始日期
        @param end_date: 结束日期
        """
        self.fund_id = fund_id
        self.benchmark_id = benchmark_id
        self.start_date = start_date
        self.end_date = end_date

        self._verify_input_param()
        self._load_data()
        self._verify()
        self._init_data_param()

    def _verify_input_param(self):
        verify_type(self.fund_id, 'fund_id', str)
        verify_type(self.benchmark_id, 'benchmark_id', str)
        verify_type(self.start_date, 'start_date', str)
        verify_type(self.end_date, 'end_date', str)

    def _load_data(self):
        self.data_param = EquityBrinsonAttributionLoader(
            self.fund_id, self.benchmark_id, self.start_date, self.end_date).load()

    def _verify(self):
        if not self.data_param:
            return
        trading_day_list = self.data_param.get('trading_day_list')
        portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        security_return_series_dict = self.data_param.get('security_return_series_dict')
        security_sector_series_dict = self.data_param.get('security_sector_series_dict')
        nav_based_return_dict = self.data_param.get('nav_based_return_dict')
        verify_trading_day(trading_day_list)
        verify_type(portfolio_weight_series_dict, 'portfolio_weight_series_dict', dict)
        verify_type(benchmark_weight_series_dict, 'benchmark_weight_series_dict', dict)
        verify_type(security_return_series_dict, 'security_return_series_dict', dict)
        verify_type(security_sector_series_dict, 'security_sector_series_dict', dict)
        verify_type(nav_based_return_dict, 'nav_based_return_dict', dict)

        for i in range(len(trading_day_list) - 1):
            trading_day = trading_day_list[i]
            next_trading_day = trading_day_list[i + 1]

            portfolio_weight_series = portfolio_weight_series_dict.get(trading_day)
            verify_type(portfolio_weight_series, 'portfolio_weight_series', pd.Series, trading_day)
            verify_df_not_null(portfolio_weight_series, 'portfolio_weight_series', trading_day)
            verify_simple_data_duplicate(portfolio_weight_series.index, 'portfolio_weight_series.index', trading_day)

            benchmark_weight_series = benchmark_weight_series_dict.get(trading_day)
            verify_type(benchmark_weight_series, 'benchmark_weight_series', pd.Series, trading_day)
            verify_df_not_null(benchmark_weight_series, 'benchmark_weight_series', trading_day)
            verify_simple_data_duplicate(benchmark_weight_series.index, 'benchmark_weight_series.index', trading_day)

            security_sector_series = security_sector_series_dict.get(trading_day)
            verify_type(security_sector_series, 'security_sector_series', pd.Series, trading_day)
            verify_simple_data_duplicate(security_sector_series.index, 'security_sector_series.index', trading_day)

            security_return_series = security_return_series_dict.get(next_trading_day)
            verify_type(security_return_series, 'security_return_series', pd.Series, next_trading_day)
            verify_df_not_null(security_return_series, 'security_return_series', next_trading_day)
            verify_simple_data_duplicate(security_return_series.index, 'security_return_series.index', next_trading_day)

            nav_based_return_series = nav_based_return_dict.get(next_trading_day)
            verify_type(nav_based_return_series, 'nav_based_return_series', pd.Series, next_trading_day)
            verify_df_not_null(nav_based_return_series, 'nav_based_return_series', next_trading_day)

    def _init_data_param(self):
        if not self.data_param:
            return
        self.trading_day_list = self.data_param['trading_day_list']
        self.portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        self.benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        self.security_return_series_dict = self.data_param.get('security_return_series_dict')
        self.security_sector_series_dict = self.data_param.get('security_sector_series_dict')
        self.nav_based_return_dict = self.data_param.get('nav_based_return_dict')
        for i in range(len(self.trading_day_list) - 1):
            trading_day = self.trading_day_list[i]
            next_trading_day = self.trading_day_list[i + 1]
            idx = self.portfolio_weight_series_dict[trading_day].index.union(
                self.benchmark_weight_series_dict[trading_day].index)
            has_data_idx = idx.intersection(self.security_return_series_dict[next_trading_day].index)
            if len(has_data_idx) < len(idx):
                logger.warning('%s losing equity [%s] during intersection with %s equity_reinvest_return_series' % (
                    trading_day, ','.join(map(str, set(idx) - set(has_data_idx))), next_trading_day))
            idx = has_data_idx
            has_data_idx = idx.intersection(self.security_sector_series_dict[trading_day].index)
            if len(has_data_idx) < len(idx):
                logger.warning('%s losing equity [%s] during intersection with %s security_sector_series' % (
                    trading_day, ','.join(map(str, set(idx) - set(has_data_idx))), trading_day))
            idx = has_data_idx
            self.portfolio_weight_series_dict[trading_day] = self.portfolio_weight_series_dict[trading_day].reindex(
                idx).fillna(0.)
            self.benchmark_weight_series_dict[trading_day] = self.benchmark_weight_series_dict[trading_day].reindex(
                idx).fillna(0.)
            self.security_return_series_dict[next_trading_day] = self.security_return_series_dict[
                next_trading_day].reindex(idx)
            self.security_sector_series_dict[trading_day] = self.security_sector_series_dict[trading_day].reindex(idx)
        # 判断
        for trading_day in self.trading_day_list[:-1]:
            sector_df = self.security_sector_series_dict[trading_day]
            verify_df_not_null(sector_df, 'sector_df', trading_day)
        self.sector_list = pd.concat(self.security_sector_series_dict).unique().tolist()

    @staticmethod
    def _calculate_asset_allo(weight_portfolio_series, weight_benchmark_series,
                              equity_return_series, nav_based_return_series):
        sum_p_weight = weight_portfolio_series.sum()
        sum_b_weight = weight_benchmark_series.sum()
        norm_weight_portfolio_series = \
            weight_portfolio_series / sum_p_weight if sum_p_weight > 0 else weight_portfolio_series
        norm_weight_benchmark_series = \
            weight_benchmark_series / sum_b_weight if sum_b_weight > 0 else weight_benchmark_series

        R_bond = nav_based_return_series.loc['bond_bm']

        R_portfolio_equity = norm_weight_portfolio_series.dot(equity_return_series)
        R_portfolio = R_portfolio_equity * sum_p_weight + R_bond * (1 - sum_p_weight)
        R_benchmark_equity = norm_weight_benchmark_series.dot(equity_return_series)
        R_benchmark = R_benchmark_equity * sum_b_weight + R_bond * (1 - sum_b_weight)
        asset_allo = (sum_p_weight - sum_b_weight) * (R_benchmark_equity - R_bond)

        return asset_allo, R_portfolio, R_benchmark

    @staticmethod
    def _sector_analysis(weight_portfolio_series, weight_benchmark_series, sector_weight_portfolio_series,
                         sector_weight_benchmark_series, equity_return_series):
        sum_p_weight = weight_portfolio_series.sum()
        sum_b_weight = weight_benchmark_series.sum()
        sum_sector_p_weight = sector_weight_portfolio_series.sum()
        sum_sector_b_weight = sector_weight_benchmark_series.sum()

        norm_weight_benchmark_series = weight_benchmark_series / sum_b_weight if \
            sum_b_weight > 0 else weight_benchmark_series
        norm_sector_weight_portfolio_series = sector_weight_portfolio_series / sum_sector_p_weight if \
            sum_sector_p_weight > 0 else sector_weight_portfolio_series
        norm_sector_weight_benchmark_series = sector_weight_benchmark_series / sum_sector_b_weight if \
            sum_sector_b_weight > 0 else sector_weight_benchmark_series

        R_benchmark_sector = norm_sector_weight_benchmark_series.dot(equity_return_series)
        R_benchmark_equity = norm_weight_benchmark_series.dot(equity_return_series)
        R_portfolio_sector = norm_sector_weight_portfolio_series.dot(equity_return_series)

        sector_allo = (sum_sector_p_weight / sum_p_weight - sum_sector_b_weight / sum_b_weight) * (
                R_benchmark_sector - R_benchmark_equity)
        equity_selection = (sum_sector_p_weight / sum_p_weight) * (R_portfolio_sector - R_benchmark_sector)
        weight = pd.Series(index=['portfolio', 'benchmark'], data=[sum_sector_p_weight, sum_sector_b_weight])
        sector_portfolio_return = sector_weight_portfolio_series.dot(equity_return_series)
        sector_benchmark_return = sector_weight_benchmark_series.dot(equity_return_series)
        ret = pd.Series(index=['portfolio', 'benchmark'], data=[sector_portfolio_return, sector_benchmark_return])

        return sector_allo, equity_selection, weight, ret

    def _single_period_attribution(self, weight_portfolio_series, weight_benchmark_series,
                                   equity_return_series, security_sector_series, nav_based_return_series):
        sum_p_weight = weight_portfolio_series.sum()
        sum_b_weight = weight_benchmark_series.sum()

        asset_allo, portfolio_total_return, benchmark_total_return = self._calculate_asset_allo(
            weight_portfolio_series, weight_benchmark_series, equity_return_series, nav_based_return_series)

        total_weight = pd.Series(index=['portfolio', 'benchmark'], data=[sum_p_weight, sum_b_weight])
        sector_return_attr_df = pd.DataFrame(index=self.sector_list, columns=['sector_allo', 'equity_selection'])
        active_sector_weight_series = pd.Series(index=self.sector_list, name='active_weight', dtype=float)
        portfolio_sector_weight_series = pd.Series(index=self.sector_list, name='portfolio_weight', dtype=float)
        benchmark_sector_weight_series = pd.Series(index=self.sector_list, name='benchmark_weight', dtype=float)
        active_sector_return_series = pd.Series(index=self.sector_list, name='active_return', dtype=float)
        portfolio_sector_return_series = pd.Series(index=self.sector_list, name='portfolio_return', dtype=float)
        benchmark_sector_return_series = pd.Series(index=self.sector_list, name='benchmark_return', dtype=float)

        for sector in self.sector_list:
            equity_universe = security_sector_series[security_sector_series == sector].index.tolist()
            if len(equity_universe) == 0:
                sector_allo = 0.
                equity_selection = 0.
                weight = pd.Series(index=['portfolio', 'benchmark'], data=[0., 0.])
                ret = pd.Series(index=['portfolio', 'benchmark'], data=[0., 0.])
            else:
                sub_weight_portfolio_series = weight_portfolio_series.reindex(equity_universe).reindex(
                    security_sector_series.index).fillna(0.)
                sub_weight_benchmark_series = weight_benchmark_series.reindex(equity_universe).reindex(
                    security_sector_series.index).fillna(0.)
                sector_allo, equity_selection, weight, ret = self._sector_analysis(
                    weight_portfolio_series, weight_benchmark_series,
                    sub_weight_portfolio_series, sub_weight_benchmark_series, equity_return_series)
            sector_allo *= sum_p_weight
            equity_selection *= sum_p_weight

            sector_return_attr_df.loc[sector] = [sector_allo, equity_selection]
            active_sector_weight_series.loc[sector] = weight['portfolio'] - weight['benchmark']
            portfolio_sector_weight_series.loc[sector] = weight['portfolio']
            benchmark_sector_weight_series.loc[sector] = weight['benchmark']
            active_sector_return_series.loc[sector] = ret['portfolio'] - ret['benchmark']
            portfolio_sector_return_series.loc[sector] = ret['portfolio']
            benchmark_sector_return_series.loc[sector] = ret['benchmark']

        sector_weight_df = pd.concat(
            [portfolio_sector_weight_series, benchmark_sector_weight_series, active_sector_weight_series], axis=1)
        sector_return_df = pd.concat(
            [portfolio_sector_return_series, benchmark_sector_return_series, active_sector_return_series], axis=1)
        sector_return_attr_df['management'] = sector_return_attr_df.sum(axis=1)

        r_p = nav_based_return_series.loc['portfolio']
        r_b = nav_based_return_series.loc['equity_bm'] * sum_b_weight + \
            (1 - sum_b_weight) * nav_based_return_series.loc['bond_bm']

        trading_return = (r_p - r_b) - (portfolio_total_return - benchmark_total_return)
        realized_period_attr_series = \
            pd.Series(index=['portfolio', 'benchmark', 'asset_allo', 'sector_allo', 'equity_selection', 'trading'],
                      data=[r_p, r_b, asset_allo, sector_return_attr_df['sector_allo'].sum(),
                            sector_return_attr_df['equity_selection'].sum(), trading_return])

        return realized_period_attr_series, sector_weight_df, sector_return_df, sector_return_attr_df, total_weight

    def get_attribution_result(self):
        output = EquityBrinsonAttributionOutputs()
        if not self.data_param:
            return output.to_dict()
        realized_period_attr_df = pd.DataFrame(
            index=['portfolio', 'benchmark', 'asset_allo', 'sector_allo', 'equity_selection', 'trading'],
            columns=self.trading_day_list[1:]).T
        total_weight_df = pd.DataFrame(index=['portfolio', 'benchmark'], columns=self.trading_day_list[1:])
        sector_attr_df_dict = {}
        all_sectors = list(industry_names.keys())
        for i in range(len(self.trading_day_list) - 1):
            trading_day = self.trading_day_list[i]
            next_trading_day = self.trading_day_list[i + 1]
            weight_portfolio_series = self.portfolio_weight_series_dict[trading_day]
            weight_benchmark_series = self.benchmark_weight_series_dict[trading_day]
            equity_return_series = self.security_return_series_dict[next_trading_day]
            security_sector_series = self.security_sector_series_dict[trading_day]
            nav_based_return_series = self.nav_based_return_dict[next_trading_day]
            realized_period_attr_series, sector_weight_df, sector_return_df, active_attr_df, total_weight = \
                self._single_period_attribution(
                    weight_portfolio_series, weight_benchmark_series,
                    equity_return_series, security_sector_series, nav_based_return_series)

            realized_period_attr_df.loc[next_trading_day] = realized_period_attr_series

            sector_weight_df = sector_weight_df.reindex(all_sectors).fillna(0.)
            sector_return_df = sector_return_df.reindex(all_sectors).fillna(0.)
            active_attr_df = active_attr_df.reindex(all_sectors).fillna(0.)
            sector_attr_df_dict[next_trading_day] = \
                pd.concat([sector_weight_df, sector_return_df, active_attr_df], axis=1)

            total_weight_df[next_trading_day] = total_weight

        realized_period_attr_df = pd.merge(realized_period_attr_df, total_weight_df.T,
                                           left_index=True, right_index=True, suffixes=('_return', '_weight'))
        realized_period_attr_df.index.name = 'trade_date'
        realized_period_attr_df.reset_index(inplace=True)
        realized_period_attr_df['fund_id'] = self.fund_id

        sector_attr_df = pd.concat(sector_attr_df_dict).reset_index().rename(
            columns={"level_0": "trade_date", "level_1": "industry"})
        sector_attr_df['fund_id'] = self.fund_id

        output.realized_period_attr_df = realized_period_attr_df
        output.sector_attr_df = sector_attr_df

        # if isPlot:
        #     tmp = output.realized_period_attr_df.copy()
        #     tmp['active_return'] = tmp['portfolio_return'] - tmp['benchmark_return']
        #     tmp = tmp.set_index('trade_date')[[
        #         'active_return', 'asset_allo', 'sector_allo', 'equity_selection', 'trading']]
        #     tmp = (100 * tmp).astype(float).round(2)
        #
        #     sector_tmp = pd.pivot_table(
        #         sector_attr_df, index='trade_date', columns='industry', values='sector_allo').sort_index().T
        #     sector_tmp = (100 * sector_tmp).astype(float).round(2).T
        #
        #     selection_tmp = pd.pivot_table(
        #         sector_attr_df, index='trade_date', columns='industry', values='equity_selection').sort_index().T
        #     selection_tmp = (100 * selection_tmp).astype(float).round(2).T
        #
        #     weight_tmp = output.realized_period_attr_df.set_index(
        #         'trade_date')[['portfolio_weight', 'benchmark_weight']]
        #     weight_tmp = (100 * weight_tmp).astype(float).round(1)
        #
        #     pic1 = draw_brinson_area_bar(tmp)
        #     pic1.render('D:\\kevin\\123.html')
        #     pic2 = draw_heatmap_brinson(sector_tmp)
        #     pic2.render('D:\\kevin\\456.html')
        #     pic3 = draw_heatmap_brinson(selection_tmp)
        #     pic3.render('D:\\kevin\\789.html')
        #     pic4 = draw_weight_compare_brinson(weight_tmp)
        #     pic4.render('D:\\kevin\\100.html')

        return output.to_dict()


if __name__ == '__main__':
    attr_result = EquityBrinsonAttribution(
        fund_id='110011', benchmark_id='000300', start_date='20210630', end_date='20220104').get_attribution_result()
    print(attr_result['realized_period_attr_df'])