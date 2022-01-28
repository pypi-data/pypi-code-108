"""
线上和本地的净值归因结果的校验程序
"""
import pandas as pd
import hbshare as hbs
from hbshare.fe.nav_attr.nav_attribution import StyleAttribution


class NavAttributionCheck:
    def __init__(self, fund_id, fund_type, start_date, end_date, factor_type, benchmark_id, nav_frequency):
        self.fund_id = fund_id
        self.fund_type = fund_type
        self.start_date = start_date
        self.end_date = end_date
        self.factor_type = factor_type
        self.benchmark_id = benchmark_id
        self.nav_frequency = nav_frequency

    def get_online_res_from_mysql(self, local_res):
        if self.fund_type == 'mutual':
            db_name = 'st_fund'
            user_name = 'funduser'
        else:
            db_name = 'st_hedge'
            user_name = 'highuser'
        output_online = {}
        # exposure_series
        sql_script = "SELECT * FROM {}.r_st_nav_attr_df where jjdm = '{}' and tjrq >= {} and tjrq <= {}".format(
            db_name, self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query(user_name, sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        data = data[data['attr_type'] == self.factor_type]
        data = data[['data_type', 'style_factor', 'tjrq', 'data_value']]
        output_online['exposure_series'] = pd.pivot_table(
            data[data['data_type'] == 'exposure'],
            index='tjrq', columns='style_factor', values='data_value').sort_index()
        # return_attr_series
        output_online['return_attr_series'] = pd.pivot_table(
            data[data['data_type'] == 'return'],
            index='tjrq', columns='style_factor', values='data_value').sort_index()
        # r_square_series
        output_online['r_square_series'] = data[data['data_type'] == 'r_square'].set_index('tjrq')['data_value']
        # style_allo_bar
        sql_script = "SELECT * FROM {}.r_st_nav_style_allo_bar where jjdm = '{}' and tjrq >= {} and tjrq <= {}".format(
            db_name, self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query(user_name, sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        data = data[data['attr_type'] == self.factor_type]
        output_online['style_allo_bar'] = data.set_index('tjrq')[['benchmark', 'allocation', 'selection']].sort_index()
        # style_allo_line
        sql_script = "SELECT * FROM {}.r_st_nav_style_allo_line where jjdm = '{}' and tjrq >= {} and tjrq <= {}".format(
            db_name, self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query(user_name, sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        data = data[data['attr_type'] == self.factor_type]
        tmp = data.set_index('tjrq')[['portfolio', 'benchmark', 'dynamic_style_bm']].sort_index()
        tmp = (1 + tmp).pct_change().dropna()
        output_online['style_allo_line'] = \
            tmp.reindex(local_res['style_allo_line'].index).fillna(0.).add(1.0).cumprod().subtract(1.)

        return output_online

    def compare_results(self):
        local_res = \
            StyleAttribution(fund_id=self.fund_id, fund_type=self.fund_type, start_date=self.start_date,
                             end_date=self.end_date, factor_type=self.factor_type,
                             benchmark_id=self.benchmark_id, nav_frequency=self.nav_frequency).get_all(processed=False)
        online_res = self.get_online_res_from_mysql(local_res)

        return online_res, local_res


if __name__ == '__main__':
    data_ol, data_lc = \
        NavAttributionCheck(fund_id='002943', fund_type='mutual', start_date='20161220', end_date='20220107',
                            factor_type='style_allo', benchmark_id='000985', nav_frequency='day').compare_results()
    print(data_ol['exposure_series'])
    print("\n")
    print(data_lc['exposure_series'].round(6))
