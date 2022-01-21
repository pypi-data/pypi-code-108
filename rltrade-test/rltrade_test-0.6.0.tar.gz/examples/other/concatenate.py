import pandas as pd

csv_path = 'data/ibkrcontfutgc5mins.csv'
paths = ['data/ibkrcontfutgc5mins1.csv',
    'data/ibkrcontfutgc5mins2.csv',
    'data/ibkrcontfutgc5mins3.csv',
    'data/ibkrcontfutgc5mins4.csv']

df = pd.DataFrame()
for path in paths:
    temp = pd.read_csv(path)
    df = df.append(temp)

df = df.sort_values(by=['tic','date'])
df.to_csv(csv_path,index=False)