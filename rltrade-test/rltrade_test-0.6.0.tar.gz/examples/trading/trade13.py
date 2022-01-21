from rltrade import config
from rltrade.models import SmartPortfolioDiffAgent

#include the dates from valid trading date after test period to yesterday's date
#please do not overlap dates with test period used during training model.
demo = True
time_frame = '1d'
trade_period = ('2021-12-29','2022-01-13') #example testing day
accountid = "DU1770002"
path = 'models/stocks/train13'

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
    # this is total money spend in value used, to determine how many stocks to buy so please be carefull with it.
    #if there are already stocks availabe in the portfolio It might not buy new stock and sell if there are too many.
    "initial_amount": 26_207,
    "ticker_col_name":"tic",
    "filter_threshold":0.25, #filter threshold only matter while training
    "target_metrics":['asset','sortino','calamar','skew','kurtosis'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':252}

agent = SmartPortfolioDiffAgent("ppo",
                    df=None,
                    ticker_list=None,
                    train_period=None,
                    test_period=None,
                    sec_types=None,
                    exchanges=None,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    demo=demo,
                    epochs=9)

agent.load_model(path) #same path as save
actions = agent.get_trade_actions(trade_period)
agent.make_trade(actions,accountid=accountid)