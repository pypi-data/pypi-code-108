from rltrade import config
from rltrade.backtests import get_metrics
from rltrade.data import FeatureEngineer,load_csv,DayTradeFeatureEngineer

# path = 'models/dailytrade/forex-train12-single'
path = 'models/daytrades/forex-train11-single-2'
get_metrics(path)

# tech_indicators = [
#     "open_2_sma",
#     "close_2_tema",
#     "tema",
# ]

# additional_indicators = [
#     "max_value_price_5",
#     "max_value_price_22",
#     "max_value_price_66",
#     "max_value_price_1year",
#     "max_value_price_3year",
#     "max_value_price_5year",
#     "vix_fix_22"
# ]

# fe = FeatureEngineer(additional_indicators=additional_indicators,
#                     stock_indicator_list=tech_indicators,
#                     cov_matrix=False) 

# df = load_csv('testdata/metasingle1d.csv')
# train_period = ('2012-08-04','2021-01-01') #for training the model
# # df = fe.time_series_split(df,train_period[0],train_period[1])
# # df = fe.clean_data(df)
# # df = fe.add_max_value(df,5,'max_value_5','close')
# # df = fe.add_max_value(df,22,'max_value_22','close')
# # df = fe.add_vix_fix(df,22,'vix_fix_22')
# # df = df.sort_values(by=['date'])
# df = fe.create_data(df)
# df = fe.time_series_split(df,train_period[0],train_period[1])
# print(df)
# print(df['vix_fix_22'])


