import pandas as pd
from scipy.stats import linregress
from rltrade import config
from rltrade.data import DiffrencedFeatureEngineer,load_csv

csv_path = 'testdata/meta.csv'

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DIFF_STOCK_INDICATORS
all_indicators = tech_indicators + additional_indicators

df = load_csv(csv_path) 
fe = DiffrencedFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators) 

df = fe.create_data(df)
df['daily_return'] = df.groupby('tic')['close'].pct_change(1)
df = df.dropna()

r2_list = []
for indicator in tech_indicators+additional_indicators:
    r2_score = linregress(df['daily_return'],df[indicator])[2]
    r2_list.append([indicator,r2_score])

df_score = pd.DataFrame(r2_list,columns=['feature','r2_score'])
df_score = df_score.sort_values(by=['r2_score'],ascending=False)
print(df_score)
df_score.to_csv('r2featureimportance.csv',index=False)