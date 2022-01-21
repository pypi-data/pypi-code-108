import pandas as pd
from WindPy import w
from datetime import datetime

w.start()

valuation_df = pd.read_csv('C:\\Users\\kai.zhang\\Desktop\\可转债\\可转债估值结果.csv')
cb_id_list = valuation_df['cb_id'].tolist()
res = w.wsd(','.join(cb_id_list), "close", "2021-06-01", "2021-06-08", "")

data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
data.index.name = 'trade_date'
data.reset_index(inplace=True)
data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
data = data.set_index('trade_date')

period_ret = data.pct_change(periods=5).iloc[-1]
valuation_df = pd.merge(valuation_df, period_ret.to_frame('period_ret'), left_on='cb_id', right_index=True)
valuation_df['deviation_bs'] = (valuation_df['close'] - valuation_df['B-S']) / valuation_df['B-S']
valuation_df['deviation_tree'] = (valuation_df['close'] - valuation_df['tree']) / valuation_df['tree']
valuation_df['deviation_mc'] = (valuation_df['close'] - valuation_df['mc']) / valuation_df['mc']
n = valuation_df.shape[0] // 10
valuation_df = valuation_df.sort_values(by='deviation_bs').reset_index(drop=True)
for i in range(10):
    valuation_df.loc[i * n:(i + 1) * n, 'sign'] = i
valuation_df.loc[(i + 1) * n:, 'sign'] = 9
a = valuation_df.groupby('sign')['period_ret'].mean()

valuation_df = valuation_df.sort_values(by='deviation_tree').reset_index(drop=True)
for i in range(10):
    valuation_df.loc[i * n:(i + 1) * n, 'sign'] = i
valuation_df.loc[(i + 1) * n:, 'sign'] = 9
b = valuation_df.groupby('sign')['period_ret'].mean()

valuation_df = valuation_df.sort_values(by='deviation_mc').reset_index(drop=True)
for i in range(10):
    valuation_df.loc[i * n:(i + 1) * n, 'sign'] = i
valuation_df.loc[(i + 1) * n:, 'sign'] = 9
c = valuation_df.groupby('sign')['period_ret'].mean()

import matplotlib.pyplot as plt
plt.style.use('seaborn')
df = pd.concat([a, b, c], axis=1)
df.columns = ['B-S', 'Tree', 'MC']
df = df.reset_index()
df['sign'] = df['sign'].apply(lambda x: "Group_{}".format(str(int(x + 1))))

df.set_index('sign').plot.bar()