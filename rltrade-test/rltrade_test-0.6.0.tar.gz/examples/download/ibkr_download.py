from rltrade.data import IBKRDownloader

demo = True
time_frame = '5 mins' # options 1 min, 5 mins, 15 mins. 1 hour , 4 hours, 1 day 
start_date = '2021-03-17'
end_date = '2021-05-17'

csv_path = 'data/ibkrcontfutgc5mins4.csv' # path with .csv extension

ticker_list = ['GC']
sec_types = ['CONTFUT']
exchanges = ['NYMEX']

change_name = False # for changing name of ticker else keep False
ticker_list2 = ['GOLD']
sec_types2 = ['-']
exchanges2 = ['-']

ib = IBKRDownloader(start_date = start_date, # first date
                    end_date = end_date, #last date
                    ticker_list = ticker_list,
                    time_frame=time_frame,
                    sec_types=sec_types,
                    exchanges=exchanges,
                    demo=demo)
                    
if time_frame == '1 day':
    df = ib.fetch_daily_data()
else:
    df = ib.fetch_data()

df = df.sort_values(by=['date','tic'])

if change_name:
    for i in range(len(ticker_list)):
        df.loc[df['tic']==ticker_list[i],'tic'] = ticker_list2[i]
        df.loc[df['tic']==ticker_list[i],'sec'] = sec_types2[i]
        df.loc[df['tic']==ticker_list[i],'exchange'] = exchanges2[i]

df.to_csv(csv_path,index=False)