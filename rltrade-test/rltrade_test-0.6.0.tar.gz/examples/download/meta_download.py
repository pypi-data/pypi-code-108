import asyncio
from metaapi_cloud_sdk import MetaApi
from rltrade.data import OandaDownloader

"""
time_frame - last date available
4h  - '2017-12-01'
1h  - '2020-06-19'
30m - '2021-11-18'
15m - '2021-12-03'
5m -  '2021-10-01'
"""

csv_path = 'data/metasinglegold5m.csv' # path with .csv extenstion

time_frame = "5m"
train_period = ('2021-10-01','2021-11-01')
test_period = ('2021-11-02','2021-12-02')
start_time = "00:00:00"
end_time = "23:55:00" 

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzYTI0YzMwYzFkNDRmZGFmZGI3NmVmYTUxZmQ2MDJmMCIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjM5NDkwMzEzLCJyZWFsVXNlcklkIjoiM2EyNGMzMGMxZDQ0ZmRhZmRiNzZlZmE1MWZkNjAyZjAifQ.DhA6Q-AlWNssi8ScOaWy2Bxo4Hebgw94BDE6PiT9J-TvsuF7OqvdYBQ1IWYEMtsYsg3Ij8p8Wpvn8ZdZeHRkR3vLcQnMH-GZj3DyYkeqovQKk6U3uOobV-GS3meJPZYfw2zItuTDBWxuHDZsVW1ZvF4sItBDmsWIe2svF0NmKE1nu-ephcYVzYo9grr93de_h-QwlP-yeZFeGEqrz3-q5gYWcARJsIR1BX63zePuDHkUK9k5W9Rm28WdB87MHEyMSWhcAZDf8si5MwsPYC3wpzNtzGqORF3UY-w5EmolCtSPMBqM7AI0LKc1n8GPS3ZhnvHkfGhWEdb5gKlCWwshk30tICN24C1bZG06zfs450oLm8ih9ls5oyshcg_xwawNvsA305D7Siz0Pzqr1xnUA8zMz8cVUFZtjdBWCfot05_ziVO0x_mApVyAVC2OA-Sh61RtkwNNpg4bTCzK30OpdiS9GO0HLgnepnuwWOO0T9DTzTAJUxyJcXOzcWcXGdMTWaGAp5ranytU97k8GxDHa5jOS_WvphL24C8QA6of0pYZwHM3Ul5Aw351H1SbJLIqs2AChDoUnpJb9OZb-27ESLZgM1mhU6rwzt8lRRbxUHaXSv5QpM29nPm3k5KrFSv-UTXiX6oU9c1nNh3qLb6FKV_B1CQarcvyx66iUg-1DcU'
domain = 'agiliumtrade.agiliumtrade.ai'
account_id = 'ddc8fb93-e0f5-4ce8-b5d5-8290d23fc143'

# ticker_list = ['AUDUSD','EURUSD','NZDUSD','USDCAD','USDCHF','GBPUSD']
ticker_list = ['GOLD']

async def download():
    api = MetaApi(token,{'domain':domain})

    try:
        account = await api.metatrader_account_api.get_account(account_id)

        if account.state != 'DEPLOYED':
            print("Deploying account")
            await account.deploy()
        else:
            print('Account already deployed')
        if account.connection_status != 'CONNECTED':
            print('Waiting for API server to connect to broker (may take couple of minutes)')
            await account.wait_connected()
        else:
            print("Account already connected")
    
        oa = OandaDownloader(
            account = account,
            time_frame=time_frame,
            start_date=train_period[0],
            end_date=test_period[1],
            start_time=start_time,
            end_time=end_time,
            ticker_list=ticker_list)

        if time_frame == '1d':
            df = await oa.fetch_daily_data()
        else:
            df = await oa.fetch_data()
        
        df= df.sort_values(by=['date','tic'])
        df.to_csv(csv_path,index=False)

    except Exception as err:
        print(api.format_error(err))


asyncio.run(download())