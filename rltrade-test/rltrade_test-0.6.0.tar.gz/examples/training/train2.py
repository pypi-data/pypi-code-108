from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartPortfolioAgent

demo = True
csv_path = 'testdata/ibkrfut1d.csv' # path with .csv extension
train_period = ('2020-12-01','2021-06-01') #for training the model
test_period = ('2021-06-01','2021-12-29') #for trading and backtesting

path = 'models/future/ESCL'
ticker_list = ['ESH2','CLG2']
sec_types = ['FUT','FUT']
exchanges = ['GLOBEX','NYMEX']

# tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
# additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

tech_indicators = [
    "open_2_sma",
    "close_2_tema",
    "tema"
]

additional_indicators = [
    "max_value_price_5",
    "max_value_price_22",
    "max_value_price_66",
    "max_value_price_1year",
    "max_value_price_3year",
    "max_value_price_5year",
    "min_value_price_5",
]

env_kwargs = {
    "initial_amount": 50_828, 
    "ticker_col_name":"tic",
    "filter_threshold":0.25, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','sortino','calamar','skew','kurtosis'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}
    
PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':252}


df = load_csv(csv_path) # run download script before this

agent = SmartPortfolioAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    sec_types=sec_types,
                    exchanges=exchanges,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    demo=demo,
                    epochs=9)

agent.train_model()
# agent.train_model_filter() #training model on trading period
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
get_metrics(path)