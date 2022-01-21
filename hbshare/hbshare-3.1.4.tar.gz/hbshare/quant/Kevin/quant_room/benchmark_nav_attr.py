import pandas as pd
from hbshare.fe.common.util.data_loader import NavAttributionLoader
import statsmodels.api as sm

fund_id = '510500'
fund_type = 'mutual'
start_date = '20210701'
end_date = '20211217'
factor_type = 'style'
benchmark_id = '000905'


data = NavAttributionLoader(fund_id, fund_type, start_date, end_date, factor_type, benchmark_id).load()
# preprocess
date_list = sorted(data['calendar_df']['calendarDate'].unique())
portfolio_nav_series = data['benchmark_series'].reindex(date_list).dropna().sort_index()
portfolio_nav_series = portfolio_nav_series / portfolio_nav_series.iloc[0]
portfolio_return_series = portfolio_nav_series.pct_change().dropna()
# factor
factor_nav_df = data['factor_data'] / data['factor_data'].iloc[0]
factor_return_df = factor_nav_df.pct_change().dropna().reindex(portfolio_return_series.index).fillna(0.)

model = sm.OLS(portfolio_return_series, sm.add_constant(factor_return_df)).fit()
df = pd.DataFrame(index=factor_return_df.columns.tolist(),
                  columns=['exposure', 'return_attr', 't_stat', 'p_value'])
df.loc[:, 'exposure'] = model.params.drop('const')
df.loc[:, 't_stat'] = model.tvalues.drop('const')
df['t_stat'] = df['t_stat'].round(4)
df.loc[:, 'p_value'] = model.pvalues.drop('const')
df['p_value'] = df['p_value'].round(4)
# cal_return
factor_cum_return = factor_return_df.fillna(0.).add(1.0).prod().subtract(1.0)
perf_attr = df['exposure'].reindex(factor_cum_return.index).multiply(factor_cum_return)
df.loc[:, 'return_attr'] = perf_attr
df.round(4).to_clipboard()