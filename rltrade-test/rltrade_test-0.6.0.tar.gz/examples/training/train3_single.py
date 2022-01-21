from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartDayTradeSingleAgent

demo = True
time_frame = '4 hours' # options 1 min, 5 mins, 15 mins. 1 hour , 4 hours, 1 day 
train_period = ('2021-10-17','2021-11-18') #for training the model
test_period = ('2021-11-18','2021-12-20') #for trading and backtesting

csv_path = 'data/ibkrcontfutsingle4hours.csv' # path with .csv extension
path = 'models/daytrades/CL'

ticker_list = ['CLG2']
sec_types = ['FUT']
exchanges = ['NYMEX']
trades_per_stock = [2]

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
    "initial_amount": 10_000, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "max_vix_fix":5,
    "min_vix_fix":0.1,
    "vix_fix_lag":50,
    "target_metrics":['asset','unrealized'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0.9, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':522}

df = load_csv(csv_path) # run the download script first

agent = SmartDayTradeSingleAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    sec_types = sec_types,
                    trades_per_stock=trades_per_stock,
                    exchanges=exchanges,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    time_frame=time_frame,
                    tb_log_name='ppo',
                    epochs=10)

agent.train_model()
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
get_metrics(path)
