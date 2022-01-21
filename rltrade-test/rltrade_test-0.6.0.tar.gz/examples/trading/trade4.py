from pytz import timezone
from rltrade import config
from datetime import datetime
from rltrade.models import SmartDayTradeAgent2

demo = True
trade_period = ('2021-12-10','2021-12-13') #(last test date, yesterday's date)
today_date = '2021-12-13'
start_time_str = "09:30:00"
end_time_str = "10:00:00"
accountid = "DU1770002"
path = 'models/daytrades/ESNQ'

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

env_kwargs = {
    "initial_amount": 50_000, #this is worth of stocks being traded long/short
    "ticker_col_name":"tic",
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','calamar','skew','kurtosis'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':2000}

tz = timezone('EST')
start_time = datetime.strptime(today_date+start_time_str,"%Y-%m-%d%H:%M:%S")
end_time = datetime.strptime(today_date+end_time_str,"%Y-%m-%d%H:%M:%S")

def get_current_time():
    return datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

current_time = get_current_time()

while current_time < end_time and current_time > start_time:
    agent = SmartDayTradeAgent2("ppo",
                        df=None,
                        ticker_list=None,
                        sec_types=None,
                        exchanges=None,
                        train_period=None,
                        test_period=None,
                        start_time=start_time_str,
                        end_time=end_time_str,
                        ticker_col_name="tic",
                        tech_indicators=tech_indicators,
                        additional_indicators=additional_indicators,
                        env_kwargs=env_kwargs,
                        model_kwargs=PPO_PARAMS,
                        tb_log_name='ppo',
                        demo=demo,
                        epochs=10,
                        mode='min')

    duration = (current_time-start_time).seconds

    agent.load_model(path) #same path as save
    actions = agent.get_day_trade_actions(current_time,duration,trade_period)

    print(actions)

    current_time = get_current_time()
    if current_time > end_time:
        print("closing all trade positions")
        agent.close_all_day_trade_positions(accountid=accountid)
        break

    agent.make_day_trade(actions,accountid=accountid)

    current_time = get_current_time()
    print("-----------------------------------------")