"""
公募基金的Brinson持仓归因模型-dateyes版本
"""
import pandas as pd
from hbshare.fe.common.util.logger import logger
from hbshare.fe.common.util.data_loader import HoldingAttributionLoader
from hbshare.fe.common.util.verifier import verify_type, verify_trading_day, \
    verify_df_not_null, verify_simple_data_duplicate
from hbshare.fe.common.util.helper_func import \
    compute_attr_linking_coef, accumulate_timing_return, accumulate_management_return


class EquityBrinsonAttributionOutputs:
    def __init__(self):
        self.brinson_attr_series = None
        self.sector_attr_dict = None
        self.accumulate_summary = None


class EquityBrinsonAttribution:
    def __init__(self, fund_id, benchmark_id, start_date, end_date):
        """
        @param fund_id: 公募基金代码
        @param benchmark_id: 基准指数代码
        @param start_date: 起始日期
        @param end_date: 结束日期
        """
        self.fund_id = fund_id
        self.benchmark_id = benchmark_id
        self.start_date = start_date
        self.end_date = end_date
        # result init (without risk)
        self.active_weight = None
        self.active_return = None
        self.total_return_df = None

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
        self.data_param = HoldingAttributionLoader(
            self.fund_id, self.benchmark_id, self.start_date, self.end_date, mode='brinson').load()

    def _verify(self):
        if not self.data_param:
            return
        trading_day_list = self.data_param.get('trading_day_list')
        portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        security_return_series_dict = self.data_param.get('security_return_series_dict')
        security_sector_series_dict = self.data_param.get('security_sector_series_dict')
        nav_active_return_dict = self.data_param.get('nav_active_return_dict')
        verify_trading_day(trading_day_list)
        verify_type(portfolio_weight_series_dict, 'portfolio_weight_series_dict', dict)
        verify_type(benchmark_weight_series_dict, 'benchmark_weight_series_dict', dict)
        verify_type(security_return_series_dict, 'security_return_series_dict', dict)
        verify_type(security_sector_series_dict, 'security_sector_series_dict', dict)
        verify_type(nav_active_return_dict, 'nav_active_return_dict', dict)

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

            nav_active_return_series = nav_active_return_dict.get(next_trading_day)
            verify_type(nav_active_return_series, 'nav_active_return_series', pd.Series, next_trading_day)
            verify_df_not_null(nav_active_return_series, 'nav_active_return_series', next_trading_day)

    def _init_data_param(self):
        if not self.data_param:
            return
        self.trading_day_list = self.data_param['trading_day_list']
        self.security_return_series_dict = self.data_param.get('security_return_series_dict')
        self.benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        self.portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        self.security_sector_series_dict = self.data_param.get('security_sector_series_dict')
        self.nav_active_return_dict = self.data_param.get('nav_active_return_dict')
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
            self.security_sector_series_dict[trading_day] = self.security_sector_series_dict[trading_day].reindex(idx)
            self.security_return_series_dict[next_trading_day] = self.security_return_series_dict[
                next_trading_day].reindex(idx)
        # 判断
        for trading_day in self.trading_day_list:
            sector_df = self.security_sector_series_dict[trading_day]
            verify_df_not_null(sector_df, 'sector_df', trading_day)
        self.sector_list = pd.concat(self.security_sector_series_dict).unique().tolist()

    @staticmethod
    def _timing_analysis(weight_portfolio_series, weight_benchmark_series, equity_return_series):
        abs_sum_p_weight = weight_portfolio_series.abs().sum()
        abs_sum_b_weight = weight_benchmark_series.abs().sum()
        norm_weight_portfolio_series = weight_portfolio_series / abs_sum_p_weight if \
            abs_sum_p_weight > 0 else weight_portfolio_series
        norm_weight_benchmark_series = weight_benchmark_series / abs_sum_b_weight if \
            abs_sum_b_weight > 0 else weight_benchmark_series

        if abs_sum_p_weight <= 1e-10 and abs_sum_b_weight <= 1e-10:
            R_portfolio, R_benchmark = 0.0, 0.0
        elif abs_sum_p_weight <= 1e-10:
            R_benchmark = norm_weight_benchmark_series.dot(equity_return_series)
            R_portfolio = R_benchmark
        elif abs_sum_b_weight <= 1e-10:
            R_portfolio = norm_weight_portfolio_series.dot(equity_return_series)
            R_benchmark = R_portfolio
        else:
            R_portfolio = norm_weight_portfolio_series.dot(equity_return_series)
            R_benchmark = norm_weight_benchmark_series.dot(equity_return_series)
        portfolio_total_return = R_portfolio * abs_sum_p_weight
        benchmark_total_return = R_benchmark * abs_sum_b_weight
        timing = (abs_sum_p_weight - abs_sum_b_weight) * R_benchmark
        management = abs_sum_p_weight * (R_portfolio - R_benchmark)

        return timing, management, portfolio_total_return, benchmark_total_return, abs_sum_p_weight, abs_sum_b_weight

    @staticmethod
    def _sector_analysis(weight_portfolio_series, weight_benchmark_series,
                         sector_weight_portfolio_series, sector_weight_benchmark_series, equity_return_series):
        abs_sum_p_weight = weight_portfolio_series.abs().sum()
        abs_sum_b_weight = weight_benchmark_series.abs().sum()
        abs_sum_sector_p_weight = sector_weight_portfolio_series.abs().sum()
        abs_sum_sector_b_weight = sector_weight_benchmark_series.abs().sum()

        norm_sector_weight_portfolio_series = sector_weight_portfolio_series / abs_sum_sector_p_weight if \
            abs_sum_sector_p_weight > 0 else sector_weight_portfolio_series
        norm_sector_weight_benchmark_series = sector_weight_benchmark_series / abs_sum_sector_b_weight if \
            abs_sum_sector_b_weight > 0 else sector_weight_benchmark_series

        if abs_sum_sector_p_weight <= 1e-10 and abs_sum_sector_b_weight <= 1e-10:
            R_portfolio, R_benchmark = 0.0, 0.0
        elif abs_sum_sector_p_weight <= 1e-10:
            R_benchmark = norm_sector_weight_benchmark_series.dot(equity_return_series)
            R_portfolio = R_benchmark
            if abs_sum_p_weight <= 1e-10:
                abs_sum_sector_p_weight = abs_sum_sector_b_weight
        elif abs_sum_sector_b_weight <= 1e-10:
            R_portfolio = norm_sector_weight_portfolio_series.dot(equity_return_series)
            R_benchmark = R_portfolio
            if abs_sum_b_weight <= 1e-10:
                abs_sum_sector_b_weight = abs_sum_sector_p_weight
        else:
            R_portfolio = norm_sector_weight_portfolio_series.dot(equity_return_series)
            R_benchmark = norm_sector_weight_benchmark_series.dot(equity_return_series)

        if abs_sum_b_weight >= 1e-10:
            allocation_return = (abs_sum_sector_p_weight - abs_sum_sector_b_weight) * R_benchmark
        else:
            allocation_return = 0.0
        selection_return = abs_sum_sector_b_weight * (R_portfolio - R_benchmark)
        interaction_return = (abs_sum_sector_p_weight - abs_sum_sector_b_weight) * (R_portfolio - R_benchmark)

        allocation = pd.Series(index=['return'], data=[allocation_return])
        selection = pd.Series(index=['return'], data=[selection_return])
        interaction = pd.Series(index=['return'], data=[interaction_return])
        weight = pd.Series(index=['portfolio', 'benchmark'], data=[abs_sum_sector_p_weight, abs_sum_sector_b_weight])
        sector_portfolio_return = sector_weight_portfolio_series.dot(equity_return_series)
        sector_benchmark_return = sector_weight_benchmark_series.dot(equity_return_series)
        ret = pd.Series(index=['portfolio', 'benchmark'], data=[sector_portfolio_return, sector_benchmark_return])

        return allocation, selection, interaction, weight, ret

    def _single_period_attribution(self, weight_portfolio_series, weight_benchmark_series,
                                   equity_return_series, security_sector_series, sector_list):
        abs_sum_p_weight = weight_portfolio_series.abs().sum()
        abs_sum_b_weight = weight_benchmark_series.abs().sum()
        norm_weight_portfolio_series = weight_portfolio_series / abs_sum_p_weight if \
            abs_sum_p_weight > 0 else weight_portfolio_series
        norm_weight_benchmark_series = weight_benchmark_series / abs_sum_b_weight if \
            abs_sum_b_weight > 0 else weight_benchmark_series

        timing, management, portfolio_total_return, benchmark_total_return, portfolio_weight, benchmark_weight = \
            self._timing_analysis(weight_portfolio_series, weight_benchmark_series, equity_return_series)

        total_return = pd.Series(
            index=['portfolio', 'benchmark'], data=[portfolio_total_return, benchmark_total_return])
        total_weight = pd.Series(index=['portfolio', 'benchmark'], data=[portfolio_weight, benchmark_weight])
        realized_active_return_management_df = pd.DataFrame(
            index=sector_list, columns=['sector_allocation', 'equity_selection', 'interaction'])
        active_sector_weight_series = pd.Series(index=sector_list, name='active', dtype=float)
        portfolio_sector_weight_series = pd.Series(index=sector_list, name='portfolio', dtype=float)
        benchmark_sector_weight_series = pd.Series(index=sector_list, name='benchmark', dtype=float)
        active_sector_return_series = pd.Series(index=sector_list, name='active', dtype=float)
        portfolio_sector_return_series = pd.Series(index=sector_list, name='portfolio', dtype=float)
        benchmark_sector_return_series = pd.Series(index=sector_list, name='benchmark', dtype=float)

        for sector in sector_list:
            equity_universe = security_sector_series[security_sector_series == sector].index.tolist()
            if len(equity_universe) == 0:
                allocation = pd.Series(index=['return'], data=[0.])
                selection = pd.Series(index=['return'], data=[0.])
                interaction = pd.Series(index=['return'], data=[0.])
                weight = pd.Series(index=['portfolio', 'benchmark'], data=[0., 0.])
                ret = pd.Series(index=['portfolio', 'benchmark'], data=[0., 0.])
            else:
                sub_weight_portfolio_series = norm_weight_portfolio_series.reindex(equity_universe)
                sub_weight_benchmark_series = norm_weight_benchmark_series.reindex(equity_universe)
                sub_weight_portfolio_series = sub_weight_portfolio_series.reindex(
                    security_sector_series.index).fillna(0.)
                sub_weight_benchmark_series = sub_weight_benchmark_series.reindex(
                    security_sector_series.index).fillna(0.)
                allocation, selection, interaction, weight, ret = self._sector_analysis(
                    norm_weight_portfolio_series, norm_weight_benchmark_series,
                    sub_weight_portfolio_series, sub_weight_benchmark_series, equity_return_series)
            allocation *= abs_sum_p_weight
            selection *= abs_sum_p_weight
            interaction *= abs_sum_p_weight
            weight *= abs_sum_p_weight
            ret *= abs_sum_p_weight

            realized_active_return_management_df.loc[sector] = \
                [allocation['return'], selection['return'], interaction['return']]
            active_sector_weight_series[sector] = weight['portfolio'] - weight['benchmark']
            portfolio_sector_weight_series[sector] = weight['portfolio']
            benchmark_sector_weight_series[sector] = weight['benchmark']
            active_sector_return_series[sector] = ret['portfolio'] - ret['benchmark']
            portfolio_sector_return_series[sector] = ret['portfolio']
            benchmark_sector_return_series[sector] = ret['benchmark']

        sector_weight_df = pd.concat(
            [portfolio_sector_weight_series, benchmark_sector_weight_series, active_sector_weight_series], axis=1)
        sector_return_df = pd.concat(
            [portfolio_sector_return_series, benchmark_sector_return_series, active_sector_return_series], axis=1)
        active_return_dict = {
            'realized_timing': timing,
            'realized_management_df': realized_active_return_management_df
        }

        return active_return_dict, sector_weight_df, total_return, total_weight, sector_return_df

    @staticmethod
    def _accumulate_attribution(active_return, active_weight, total_return_df):
        active_return['realized_accumulated_timing_series'] = \
            accumulate_timing_return(total_return_df, active_return['realized_period_timing_series'])
        active_return['realized_accumulated_timing_value'] = \
            active_return['realized_accumulated_timing_series'].iloc[-1]

        active_return['realized_accumulated_management_df_dict'] = \
            accumulate_management_return(total_return_df, active_return['realized_period_management_df_dict'])
        trading_day_list = sorted(active_return['realized_accumulated_management_df_dict'].keys())
        active_return['realized_accumulated_management_df'] = \
            active_return['realized_accumulated_management_df_dict'][trading_day_list[-1]]

        active_weight['accumulated_sector_weight_series'] = active_weight['sector_weight_df'].reset_index().set_index(
            'date').groupby('sector').mean()
        active_weight['accumulated_total_weight_series'] = active_weight['total_weight_df'].mean(axis=1)

        coef_series = compute_attr_linking_coef(total_return_df.T)
        accum_sector_portfolio_return = (
                active_return['sector_return_df']['portfolio'] * coef_series).reset_index().groupby('sector')[0].mean()
        accum_sector_portfolio_return.name = 'portfolio'
        accum_sector_benchmark_return = \
            (active_return['sector_return_df']['benchmark'] * coef_series).reset_index().groupby('sector')[0].mean()
        accum_sector_benchmark_return.name = 'benchmark'
        accum_sector_active_return = \
            (active_return['sector_return_df']['active'] * coef_series).reset_index().groupby('sector')[0].mean()
        accum_sector_active_return.name = 'active'
        active_return['realized_accumulated_sector_return_df'] = pd.concat([
            accum_sector_portfolio_return, accum_sector_benchmark_return, accum_sector_active_return], axis=1)

        return active_return, active_weight

    def get_attribution_result(self, is_accumulated=True):
        active_return = {
            "realized_period_timing_series": pd.Series(index=self.trading_day_list[1:], dtype=float),
            "realized_period_management_df_dict": {}
        }
        active_weight = {}
        total_return_df = pd.DataFrame(index=['portfolio', 'benchmark'], columns=self.trading_day_list[1:])
        total_weight_df = pd.DataFrame(index=['portfolio', 'benchmark'], columns=self.trading_day_list[:-1])
        sector_weight_df_dict = {}
        sector_return_df_dict = {}
        for i in range(len(self.trading_day_list) - 1):
            trading_day = self.trading_day_list[i]
            next_trading_day = self.trading_day_list[i + 1]
            weight_portfolio_series = self.portfolio_weight_series_dict[trading_day]
            weight_benchmark_series = self.benchmark_weight_series_dict[trading_day]
            equity_return_series = self.security_return_series_dict[next_trading_day]
            security_sector_series = self.security_sector_series_dict[trading_day]
            active_return_dict, sector_weight_df, total_return, total_weight, sector_return_df = \
                self._single_period_attribution(weight_portfolio_series, weight_benchmark_series,
                                                equity_return_series, security_sector_series, self.sector_list)

            total_return_df[next_trading_day] = total_return
            total_weight_df[trading_day] = total_weight
            active_return['realized_period_timing_series'][next_trading_day] = active_return_dict['realized_timing']
            active_return['realized_period_management_df_dict'][next_trading_day] = \
                active_return_dict['realized_management_df']
            sector_weight_df_dict[trading_day] = sector_weight_df
            sector_return_df_dict[next_trading_day] = sector_return_df

        active_weight['sector_weight_df'] = pd.concat(sector_weight_df_dict)
        active_weight['sector_weight_df'].index.names = ['date', 'sector']
        active_weight['total_weight_df'] = total_weight_df

        active_return['sector_return_df'] = pd.concat(sector_return_df_dict)
        active_return['sector_return_df'].index.names = ['date', 'sector']
        self.active_return = active_return
        self.active_weight = active_weight
        self.total_return_df = total_return_df

        if is_accumulated:
            active_return, active_weight = self._accumulate_attribution(active_return, active_weight, total_return_df)

        # brinson_attr_df = []
        # for date in self.trading_day_list[1:]:
        #     brinson_attr = active_return['realized_period_management_df_dict'][date].sum()
        #     brinson_attr.loc['timing'] = active_return['realized_period_timing_series'].loc[date]
        #     brinson_attr_df.append(brinson_attr.to_frame(date))
        # brinson_attr_df = pd.concat(brinson_attr_df, axis=1).T.sort_index()

        return {
            "active_return": active_return,
            "active_weight": active_weight,
            "total_return_df": total_return_df,
            "nav_return_df": pd.DataFrame(self.nav_active_return_dict)
        }


if __name__ == '__main__':
    attr = EquityBrinsonAttribution(
        fund_id='100038', benchmark_id='000300', start_date='20191220', end_date='20210420').get_attribution_result()