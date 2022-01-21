from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartDayTradeForexStaticSLTFDynamicVolititySingleAgent


"""
time_frame - last date available
4h  - '2017-12-01'
1h  - '2020-06-19'
30m - '2021-11-18'
15m - '2021-12-03'
5m -  '2021-10-01'
"""

time_frame = "5m"
train_period = ('2021-03-29','2021-09-01')
test_period = ('2021-09-02','2022-01-17')
start_time = "00:00:00"
end_time = "23:55:00" 

csv_path = 'data/ibkrcontfutgc5mins.csv' # path with .csv extension
path = 'models/daytrades/forex-train11-single-2'


ticker_list = ['GC']
sec_types = ['CONTFUT']
exchanges = ['NYMEX'] 
trades_per_stock = [100] # max number per day is 24h/time_frame

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

# tech_indicators = [
#     "open_2_sma",
#     "close_2_tema",
#     "tema",
# ]

# additional_indicators = [
#     'max_value_price_10',
#     'max_value_price_50',
#     'max_value_price_100',
#     'max_value_price_500',
#     'max_value_price_1000',
#     'min_value_price_10',
# ]


env_kwargs = {
    "initial_amount": 17_300, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "stop_loss":0.01,
    "take_profit":0.03,
    "max_vix_fix":5,
    "min_vix_fix":0.1,
    "vix_fix_lag":50,
    "lot_size":0.01,
    "target_metrics":['asset','unrealized'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0.9, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 10}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':288}

def train_model():

    df = load_csv(csv_path) # run the download script first

    agent = SmartDayTradeForexStaticSLTFDynamicVolititySingleAgent("ppo",
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
                        epochs=4)

    agent.train_model()
    agent.save_model(path) #save the model for trading

    df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
    get_metrics(path)


train_model()