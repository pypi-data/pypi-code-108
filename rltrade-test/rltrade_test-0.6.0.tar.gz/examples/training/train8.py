from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartTradeAgent


"""
time_frame - last date available
1d - (2018-01-07)
"""

time_frame = "1d" #keep is 1d in this file or else it won't work
train_period = ('2012-08-04','2021-01-01') #for training the model
test_period = ('2021-01-02','2021-12-20') #for testing the model
start_time = "17:00:00"
end_time = "23:55:00" #does not matter in daily trading.

csv_path = 'testdata/meta1d.csv'
path = 'models/dailytrade/forex-CADCHF'

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzYTI0YzMwYzFkNDRmZGFmZGI3NmVmYTUxZmQ2MDJmMCIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjM5NDkwMzEzLCJyZWFsVXNlcklkIjoiM2EyNGMzMGMxZDQ0ZmRhZmRiNzZlZmE1MWZkNjAyZjAifQ.DhA6Q-AlWNssi8ScOaWy2Bxo4Hebgw94BDE6PiT9J-TvsuF7OqvdYBQ1IWYEMtsYsg3Ij8p8Wpvn8ZdZeHRkR3vLcQnMH-GZj3DyYkeqovQKk6U3uOobV-GS3meJPZYfw2zItuTDBWxuHDZsVW1ZvF4sItBDmsWIe2svF0NmKE1nu-ephcYVzYo9grr93de_h-QwlP-yeZFeGEqrz3-q5gYWcARJsIR1BX63zePuDHkUK9k5W9Rm28WdB87MHEyMSWhcAZDf8si5MwsPYC3wpzNtzGqORF3UY-w5EmolCtSPMBqM7AI0LKc1n8GPS3ZhnvHkfGhWEdb5gKlCWwshk30tICN24C1bZG06zfs450oLm8ih9ls5oyshcg_xwawNvsA305D7Siz0Pzqr1xnUA8zMz8cVUFZtjdBWCfot05_ziVO0x_mApVyAVC2OA-Sh61RtkwNNpg4bTCzK30OpdiS9GO0HLgnepnuwWOO0T9DTzTAJUxyJcXOzcWcXGdMTWaGAp5ranytU97k8GxDHa5jOS_WvphL24C8QA6of0pYZwHM3Ul5Aw351H1SbJLIqs2AChDoUnpJb9OZb-27ESLZgM1mhU6rwzt8lRRbxUHaXSv5QpM29nPm3k5KrFSv-UTXiX6oU9c1nNh3qLb6FKV_B1CQarcvyx66iUg-1DcU'
domain = 'agiliumtrade.agiliumtrade.ai'
account_id = 'ddc8fb93-e0f5-4ce8-b5d5-8290d23fc143'

# ticker_list = ['AUDUSD','EURUSD','NZDUSD','USDCAD','USDCHF','GBPUSD']
# sec_types = ['-','-','-','-','-','-']
# exchanges = ['-','-','-','-','-','-']

ticker_list = ['USDCAD','USDCHF']
sec_types = ['-','-']
exchanges = ['-','-']

#CADCHF - 3 epochs
#EURGBP - 2 epochs
#AUDNZD - 2 epochs

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    "initial_amount": 17500, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "stop_loss":0.015,
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

A2C_PARAMS = {"ent_coef": 0.01, 
            "learning_rate": 0.0001}

def train_model():

    df = load_csv(csv_path)
    agent = SmartTradeAgent("a2c",
                        df=df,
                        account=None,
                        time_frame=time_frame,
                        ticker_list=ticker_list,
                        sec_types = sec_types,
                        exchanges=exchanges,
                        ticker_col_name="tic",
                        tech_indicators=tech_indicators,
                        additional_indicators=additional_indicators,
                        train_period=train_period,
                        test_period=test_period,
                        start_time=start_time,
                        end_time=end_time,
                        env_kwargs=env_kwargs,
                        model_kwargs=A2C_PARAMS,
                        tb_log_name='a2c',
                        epochs=3)

    agent.train_model()
    agent.save_model(path) #save the model for trading

    df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
    get_metrics(path)

train_model()