from pytz import timezone
from rltrade import config
from datetime import datetime
from rltrade.models import SmartDayTradeAgent

demo = True
trade_period = ('2021-11-30','2021-12-02') #(last test date, yesterday's date)
today_date = '2021-12-03'
accountid = "DU1770002"
path = 'models/daytrades/ESCL'

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

env_kwargs = {
    "initial_amount": 150000, #this is worth of stocks being traded long/short
    "ticker_col_name":"tic",
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

tz = timezone('EST')
start_time = datetime.strptime(today_date+" 09:30:00","%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(today_date+" 15:59:00","%Y-%m-%d %H:%M:%S")

def get_current_time():
    return datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

current_time = get_current_time()

while current_time < end_time and current_time > start_time:
    agent = SmartDayTradeAgent("ppo",
                        df=None,
                        ticker_list=None,
                        sec_types=None,
                        exchanges=None,
                        train_period=None,
                        test_period=None,
                        ticker_col_name="tic",
                        tech_indicators=tech_indicators,
                        additional_indicators=additional_indicators,
                        env_kwargs=env_kwargs,
                        model_kwargs=PPO_PARAMS,
                        tb_log_name='ppo',
                        demo=demo,
                        epochs=5,
                        mode='min')

    duration = (current_time-start_time).seconds

    agent.load_model(path) #same path as save
    actions,weights = agent.get_day_trade_actions(current_time,duration,trade_period)

    print(actions,weights)

    current_time = get_current_time()
    if current_time > end_time:
        print("closing all trade positions")
        agent.close_all_day_trade_positions(accountid=accountid)
        break

    agent.make_day_trade(actions,weights,accountid=accountid)
    agent.save_model(path) #save the changes after trade

    current_time = get_current_time()
    print("-----------------------------------------")