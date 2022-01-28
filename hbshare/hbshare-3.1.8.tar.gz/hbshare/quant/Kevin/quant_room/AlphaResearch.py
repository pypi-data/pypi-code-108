"""
Alpha相关探索研究
"""
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
from datetime import datetime
import hbshare as hbs
import pandas as pd
from hbshare.quant.Kevin.quant_room.QuarterAssetAllocationReport import plotly_bar
from hbshare.fe.common.util.data_loader import get_trading_day_list
from tqdm import tqdm


class IndexStyleComparer:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM stock_index_style_exposure where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # exposure_500
        data1 = data[data['benchmark_id'] == '000905']
        data1 = pd.pivot_table(
            data1, index='trade_date', columns='factor_name', values='exposure').sort_index()[style_names]
        # exposure_1000
        data2 = data[data['benchmark_id'] == '000852']
        data2 = pd.pivot_table(
            data2, index='trade_date', columns='factor_name', values='exposure').sort_index()[style_names]
        # factor_return
        sql_script = "SELECT * FROM factor_return where " \
                     "TRADE_DATE >= {} and TRADE_DATE <= {}".format(self.start_date, self.end_date)
        engine = create_engine(engine_params)
        factor_return = pd.read_sql(sql_script, engine)
        factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        factor_return = pd.pivot_table(
            factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_names]
        self.factor_return = (1 + factor_return).cumprod().reindex(data1.index).pct_change().shift(-1).dropna()

        self.exposure_500 = data1.reindex(self.factor_return.index)
        self.exposure_1000 = data2.reindex(self.factor_return.index)

    def run(self):
        factor_return = self.factor_return
        exposure_500, exposure_1000 = self.exposure_500, self.exposure_1000

        style_attr = pd.merge(factor_return.multiply(exposure_500).sum().to_frame('中证500'),
                              factor_return.multiply(exposure_1000).sum().to_frame('中证1000'),
                              left_index=True, right_index=True)
        style_attr['差值'] = style_attr['中证500'] - style_attr['中证1000']

        plotly_bar(style_attr, title_text="500指增 vs 1000指增风格收益", save_path="D:\\123.html")


def load_benchmark_components(date):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000300', '000905', '000852']:
        inner_code = inner_code_series.loc[benchmark_id]
        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight.append(weight_df[['ticker', 'benchmark_id']])

    return pd.concat(weight)


def load_specific_return(date):
    sql_script = "SELECT * FROM st_ashare.r_st_barra_specific_return where TRADE_DATE = '{}'".format(date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    s_ret = pd.DataFrame(res['data'])
    s_ret['ticker'] = s_ret['ticker'].apply(lambda x: x.zfill(6))
    s_ret = s_ret.set_index('ticker')['s_ret']

    return s_ret


def run_spec(sdate, edate):
    trading_day_list = get_trading_day_list(sdate, edate)
    month_list = get_trading_day_list(sdate, edate, frequency='month')

    all_data = []
    for i in tqdm(range(len(month_list) - 1)):
        month = month_list[i]
        next_month = month_list[i + 1]
        period_list = [x for x in trading_day_list if month < x <= next_month]
        benchmark_weight = load_benchmark_components(month)

        data = []
        for date in period_list:
            spec_ret = load_specific_return(date)
            df = pd.merge(benchmark_weight, spec_ret.to_frame('s_ret'), left_on='ticker', right_index=True, how='right')
            df = df.fillna('other').reset_index(drop=True)

            describe_df = pd.concat([df.groupby('benchmark_id')['s_ret'].mean().to_frame(name='mean'),
                                     df.groupby('benchmark_id')['s_ret'].std().to_frame(name='std'),
                                     df.groupby('benchmark_id')['s_ret'].skew().to_frame(name='skew'),
                                     df.groupby('benchmark_id')['s_ret'].apply(
                                         lambda x: x.kurt()).to_frame(name='kurt')], axis=1)
            describe_df = describe_df.unstack().reset_index()
            describe_df.columns = ['type', 'benchmark_id', 'value']
            describe_df['trade_date'] = date
            data.append(describe_df)
        data = pd.concat(data)
        all_data.append(data)

    all_data = pd.concat(all_data)

    mean_df = pd.pivot_table(
        all_data[all_data['type'] == 'mean'], index='trade_date', columns='benchmark_id', values='value').sort_index()
    std_df = pd.pivot_table(
        all_data[all_data['type'] == 'std'], index='trade_date', columns='benchmark_id', values='value').sort_index()


if __name__ == '__main__':
    IndexStyleComparer('20201220', '20220113').run()
    # run_spec('20201220', '20220113')