from rltrade import config
from rltrade.models import SmartDRLAgent
from rltrade.data import YahooDownloader
from rltrade.backtests import backtest_plot,backtest_stats


train_period = ('2018-01-01','2019-01-01') #for training the model
test_period = ('2019-01-01','2021-01-01') #for trading and backtesting
ticker_list = config.DOW_30_TICKER
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    "hmax": 100, 
    "initial_amount": 100000, 
    "transaction_cost_pct": 0.001, 
    "ticker_col_name":"tic",
    "filter_threshold":0.3, #between 0.2 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino','calamar'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1e-4}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

print('Downloading Data')
df = YahooDownloader(start_date = train_period[0], # first date
                    end_date = test_period[1], #last date
                    ticker_list = ticker_list).fetch_data()

agent = SmartDRLAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    total_timesteps=500)

print("Training")
# agent.train_model()
agent.train_model_filter() #training model on trading period

print("Making Prediction")
df_daily_return,df_actions = agent.make_prediction() #testing model on testing period

perf_stats_all = backtest_stats(df=df_daily_return,
                                baseline_ticker=["^DJI"],
                                value_col_name="daily_return",
                                baseline_start = test_period[0], 
                                baseline_end = test_period[1])

print(perf_stats_all)

backtest_plot(account_value=df_daily_return,
            baseline_ticker=["^DJI"],
            value_col_name="daily_return",
            baseline_start = test_period[0], 
            baseline_end = test_period[1])