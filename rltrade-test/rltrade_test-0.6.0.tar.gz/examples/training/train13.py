from rltrade import config
from rltrade.models import SmartPortfolioDiffAgent
from rltrade.data import IBKRDownloader, load_csv
from rltrade.backtests import get_metrics

demo = True
time_frame = '1d'
train_period = ('2012-01-01','2020-08-01') #for training the model
test_period = ('2020-08-02','2021-12-29') #for trading and backtesting

csv_path = 'testdata/ibkr.csv'
path = 'models/stocks/train13'

# ticker_list = config.ALL_STOCKS_LIST
ticker_list = ['pall', 'rio', 'spy', 'tlt', 'jbss', 'aapl']
sec_types = ['STK'] * len(ticker_list)
exchanges = ['SMART'] * len(ticker_list)
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DIFF_STOCK_INDICATORS

# tech_indicators = [
#     "open_2_sma",
#     "close_2_tema",
#     "tema"
# ]

# additional_indicators = [
#     "max_value_price_5",
#     "max_value_price_22",
#     "max_value_price_66",
#     "max_value_price_1year",
#     "max_value_price_3year",
#     "max_value_price_5year",
#     "min_value_price_5",
# ]

env_kwargs = {
    "initial_amount": 26_207, 
    "ticker_col_name":"tic",
    "filter_threshold":0.25, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','sortino','calamar','skew','kurtosis'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}
    
PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':252}


df = load_csv(csv_path) # run download script before this

agent = SmartPortfolioDiffAgent("ppo",
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
                    time_frame= time_frame,
                    tb_log_name='ppo',
                    demo=demo,
                    epochs=9)

# agent.train_model()
agent.train_model_filter() #training model on trading period
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
get_metrics(path)