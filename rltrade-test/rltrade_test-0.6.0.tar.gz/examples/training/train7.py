from rltrade import config
from rltrade.data import IBKRDownloader
from rltrade.backtests import get_metrics
from rltrade.models import SmartPortfolioWithShortAgent


demo = True
train_period = ('2012-01-01','2020-08-01') #for training the model
test_period = ('2020-08-02','2021-12-01') #for trading and backtesting
path = 'models/stocks/new stocks'

ticker_list = ['pall','sm','edf','edi','msb','glq','rio','ebr','pht','gof','spy','qqq','tlt','jbss','iaf',
                'omp','fof','awp','htd','pbr a','iauf','igr','ccd','aapl']
sec_types = ['STK'] * len(ticker_list)
exchanges = ['SMART'] * len(ticker_list)
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    "initial_amount": 70_000, 
    "ticker_col_name":"tic",
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}
    
PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':482}

print('Downloading Data')
df = IBKRDownloader(start_date = train_period[0], # first date
                    end_date = test_period[1], #last date
                    ticker_list = ticker_list,
                    sec_types=sec_types,
                    exchanges=exchanges,
                    demo=demo,
                    ).fetch_data() #requires subscription

agent = SmartPortfolioWithShortAgent("ppo",
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
                    epochs=5)

agent.train_model_filter() #training model on trading period
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period
get_metrics(path)