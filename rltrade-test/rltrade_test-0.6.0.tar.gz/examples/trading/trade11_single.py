import asyncio
from pytz import timezone
from datetime import datetime
from metaapi_cloud_sdk import MetaApi
from rltrade import config
from rltrade.models import SmartDayTradeForexDynamicSingleSLTFAgent

demo = True
time_frame = "4h" # available 5m, 15m, 30m, 1h, 4h
trade_period = ('2021-12-20','2022-01-12') #(last test date, yesterday's date)
today_date = '2022-01-13'
start_time_str = "00:00:00"
end_time_str = "23:55:00" 
path = 'models/daytrades/forex-train11-single'

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzYTI0YzMwYzFkNDRmZGFmZGI3NmVmYTUxZmQ2MDJmMCIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjM5NDkwMzEzLCJyZWFsVXNlcklkIjoiM2EyNGMzMGMxZDQ0ZmRhZmRiNzZlZmE1MWZkNjAyZjAifQ.DhA6Q-AlWNssi8ScOaWy2Bxo4Hebgw94BDE6PiT9J-TvsuF7OqvdYBQ1IWYEMtsYsg3Ij8p8Wpvn8ZdZeHRkR3vLcQnMH-GZj3DyYkeqovQKk6U3uOobV-GS3meJPZYfw2zItuTDBWxuHDZsVW1ZvF4sItBDmsWIe2svF0NmKE1nu-ephcYVzYo9grr93de_h-QwlP-yeZFeGEqrz3-q5gYWcARJsIR1BX63zePuDHkUK9k5W9Rm28WdB87MHEyMSWhcAZDf8si5MwsPYC3wpzNtzGqORF3UY-w5EmolCtSPMBqM7AI0LKc1n8GPS3ZhnvHkfGhWEdb5gKlCWwshk30tICN24C1bZG06zfs450oLm8ih9ls5oyshcg_xwawNvsA305D7Siz0Pzqr1xnUA8zMz8cVUFZtjdBWCfot05_ziVO0x_mApVyAVC2OA-Sh61RtkwNNpg4bTCzK30OpdiS9GO0HLgnepnuwWOO0T9DTzTAJUxyJcXOzcWcXGdMTWaGAp5ranytU97k8GxDHa5jOS_WvphL24C8QA6of0pYZwHM3Ul5Aw351H1SbJLIqs2AChDoUnpJb9OZb-27ESLZgM1mhU6rwzt8lRRbxUHaXSv5QpM29nPm3k5KrFSv-UTXiX6oU9c1nNh3qLb6FKV_B1CQarcvyx66iUg-1DcU'
domain = 'agiliumtrade.agiliumtrade.ai'

if demo:
    account_id = '9d20d731-3188-42de-9db9-e586675bff23'
else:
    account_id = 'ddc8fb93-e0f5-4ce8-b5d5-8290d23fc143'

# tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
# additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

tech_indicators = [
    "open_2_sma",
    "close_2_tema",
    "tema",
]

additional_indicators = [
    'max_value_price_10',
    'max_value_price_50',
    'max_value_price_100',
    'max_value_price_500',
    'max_value_price_1000',
    'min_value_price_10',
]

env_kwargs = {
    "initial_amount": 50_000, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "max_stop_loss":0.015,
    "max_take_profit":0.015,
    "max_vix_fix":3,
    "min_vix_fix":1,
    "vix_fix_lag":50,
    "lot_size":0.1,
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0.9, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':522}

tz = timezone('EST')
start_time = datetime.strptime(today_date+start_time_str,"%Y-%m-%d%H:%M:%S")
end_time = datetime.strptime(today_date+end_time_str,"%Y-%m-%d%H:%M:%S")

def get_current_time():
    return datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

async def run_loop():
    api = MetaApi(token,{'domain':domain})
    try:
        #connecting it once
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
            print('Account already connected')
        
        streaming_connection = account.get_streaming_connection()
        print('Streaming connection...')
        await streaming_connection.connect()
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await streaming_connection.wait_synchronized()

        current_time = get_current_time()

        #loop
        while current_time < end_time and current_time > start_time:
            agent = SmartDayTradeForexDynamicSingleSLTFAgent("ppo",
                                df=None,
                                ticker_list=None,
                                sec_types=None,
                                exchanges=None,
                                trades_per_stock=None,
                                train_period=None,
                                test_period=None,
                                account=account,
                                time_frame=time_frame,
                                ticker_col_name="tic",
                                tech_indicators=tech_indicators,
                                additional_indicators=additional_indicators,
                                start_time=start_time_str,
                                end_time=end_time_str,
                                env_kwargs=env_kwargs,
                                model_kwargs=PPO_PARAMS,
                                tb_log_name='ppo',
                                epochs=2)

            duration = (current_time-start_time).seconds

            agent.load_model(path) #same path as save
            actions = await agent.get_day_trade_actions(current_time,duration,trade_period)
            await agent.make_day_trade(actions,account,streaming_connection)

            current_time = get_current_time()
            print("-----------------------------------------")
                
    except Exception as err:
            print(api.format_error(err))
    
loop = asyncio.get_event_loop()
loop.run_until_complete(run_loop())