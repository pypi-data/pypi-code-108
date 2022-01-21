from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartDailyTradeForexAgent


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
path = 'models/dailytrade/forex-train10'


ticker_list = ['AUDUSD','EURUSD','NZDUSD','USDCAD','USDCHF','GBPUSD']
# ticker_list = ['USDCAD','USDCHF']
sec_types = ['-'] * len(ticker_list)
exchanges = ['-'] * len(ticker_list)

#CADCHF - 3 epochs
#EURGBP - 2 epochs
#AUDNZD - 2 epochs

# tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
# additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

tech_indicators = [
    "open_2_sma",
    "close_2_tema",
    "tema",
]

additional_indicators = [
    "max_value_price_5",
    "max_value_price_22",
    "max_value_price_66",
    "max_value_price_1year",
    "max_value_price_3year",
    "max_value_price_5year",
]

env_kwargs = {
    "initial_amount": 17500, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "stop_loss":0.015,
    "take_profit":0.015,
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':252}

def train_model():
    df = load_csv(csv_path)

    agent = SmartDailyTradeForexAgent("ppo",
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
                        model_kwargs=PPO_PARAMS,
                        tb_log_name='ppo',
                        epochs=4)

    agent.train_model()
    agent.save_model(path) #save the model for trading

    df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
    get_metrics(path)


train_model()