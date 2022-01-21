from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartDayTradeForexAgent


"""
time_frame - last date available
4h  - '2017-12-01'
1h  - '2020-06-19'
30m - '2021-11-18'
15m - '2021-12-03'
5m -  '2021-10-01'
"""

time_frame = "4h" # available 5m, 15m, 30m, 1h, 4h
train_period = ('2017-10-01','2021-01-01') #for training the model
test_period =  ('2021-01-01','2021-12-20')
start_time = "00:00:00"
end_time = "23:55:00" 

csv_path = 'testdata/meta4h.csv'
path = 'models/daytrades/forex'

ticker_list = ['AUDUSD','EURUSD','NZDUSD','USDCAD','USDCHF','GBPUSD']
# ticker_list = ['USDCAD','USDCHF']
sec_types = ['-'] * len(ticker_list)
exchanges = ['-'] * len(ticker_list)
trades_per_stock = [2] * len(ticker_list) # max number per day is 24h/time_frame

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
    "stop_loss":0.015,
    "take_profit":0.015,
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':522}

def train_model():

    df = load_csv(csv_path)

    agent = SmartDayTradeForexAgent("ppo",
                        df=df,
                        account=None,
                        time_frame=time_frame,
                        ticker_list=ticker_list,
                        sec_types = sec_types,
                        trades_per_stock=trades_per_stock,
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
                        epochs=10)

    agent.train_model()
    agent.save_model(path) #save the model for trading

    df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
    get_metrics(path)

train_model()