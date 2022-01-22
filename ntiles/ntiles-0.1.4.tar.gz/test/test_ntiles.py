#%%

import pandas as pd
from toolbox.constitutes.constitute_adjustment import ConstituteAdjustment
from ntiles.tears import NTile
from ntiles.portals.pricing_portal import PricingPortal


#%%
internet_uni = pd.read_csv('/Users/alex/Documents/Notebook/internet_uni/data/index/internet_uni.csv',
                           usecols=['lpermno', 'int_from', 'int_thru']).rename(
    {'int_from': 'from', 'int_thru': 'thru'}, axis=1)

start = pd.Timestamp('2017')
end = pd.Timestamp('2021')

ca = ConstituteAdjustment('lpermno')
ca.add_index_info(index_constitutes=internet_uni, start_date=start, end_date=end,
                  date_format='%Y-%m-%d')
#%%
traffic_df = pd.read_csv('/Users/alex/Desktop/traffic_history.csv').rename({'datadate': 'date'},
                                                                           axis=1).drop_duplicates(
    subset=['date', 'lpermno'])
traffic_df = traffic_df[traffic_df['weburl'] != 'apple.com']
traffic_df['rank'] = traffic_df['rank'].astype(float)
traffic_df['pvp_million'] = traffic_df['pvp_million'].astype(float)
traffic_df['pvp_user'] = traffic_df['pvp_user'].astype(float)
traffic_df['reach_per_million'] = traffic_df['reach_per_million'].astype(float)
#traffic_df['date'] = pd.to_datetime(traffic_df['date'], format='%Y-%m-%d').dt.to_period(freq='D')
traffic_df = traffic_df.set_index(['date', 'lpermno']).unstack().shift(1).stack().reset_index()

factor_df = ca.adjust_data_for_membership(data=traffic_df, contents='factor', date_format='%Y-%m-%d', )
factor_df = factor_df.reset_index()
factor_df['date'] = factor_df['date'].dt.to_period('D')
factor_df = factor_df.set_index(['date', 'lpermno'])

alpha = factor_df['pvp_million'] / factor_df['pvp_user']


#%%
assets = internet_uni.lpermno.astype(str).unique().tolist()
portal = PricingPortal(assets, start, end)
tile = NTile(portal)


tile.ntile_return_tearsheet(alpha, 5, 5, False)
