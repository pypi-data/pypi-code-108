from pytz import timezone
from rltrade import config
from datetime import datetime
from rltrade.models import SmartDayTradeSingleAgent

#include the dates from valid trading date after test period to yesterday's date
#please do not overlap dates with test period used during training model.
demo = True
time_frame = '4 hours' # options 1 min, 5 mins, 15 mins. 1 hour , 4 hours, 1 day 
trade_period = ('2021-12-20','2022-01-20') #yesterday's date
today_date = '2022-01-21'
accountid = "DU1770002"
path = 'models/daytrades/CL'

ticker_list = ['CLG2']
sec_types = ['FUT']
exchanges = ['NYMEX']

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

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
    "max_vix_fix":3,
    "min_vix_fix":1,
    "vix_fix_lag":50,
    "target_metrics":['asset','unrealized'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0.9, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':522}

tz = timezone('EST')
start_time = datetime.strptime(today_date+" 09:30:00","%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(today_date+" 15:59:00","%Y-%m-%d %H:%M:%S")

def get_current_time():
    return datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

current_time = get_current_time()

while current_time < end_time and current_time > start_time:
    agent = SmartDayTradeSingleAgent("ppo",
                        df=None,
                        ticker_list=None,
                        train_period=None,
                        test_period=None,
                        sec_types=None,
                        exchanges=None,
                        trades_per_stock=None,
                        ticker_col_name="tic",
                        tech_indicators=tech_indicators,
                        additional_indicators=additional_indicators,
                        env_kwargs=env_kwargs,
                        model_kwargs=PPO_PARAMS,
                        tb_log_name='ppo',
                        time_frame=time_frame,
                        demo=demo,
                        epochs=9)

    duration = (current_time-start_time).seconds

    agent.load_model(path) #same path as save
    contracts = agent.get_day_trade_actions(current_time,duration,trade_period)

    print(contracts)

    current_time = get_current_time()
    if current_time > end_time:
        print("closing all trade positions")
        agent.close_all_day_trade_positions(accountid=accountid)
        break

    agent.make_day_trade(contracts,accountid=accountid)

    current_time = get_current_time()
    print("-----------------------------------------")