import os
import time
import numpy as np
import pandas as pd
import pytz
from stable_baselines3.common.vec_env import DummyVecEnv
import torch
from rltrade.environments import (SmartDailyTradeForexDynamicSLTFEnv, 
                        SmartDailyTradeForexDynamicSLTFLongOrShortEnv, SmartDailyTradeForexDynamicSLTFSingleSymbolEnv, SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv, 
                        SmartDayTradeEnv3, SmartDayTradeForexDynamicSLTFLongOrShortEnv, SmartDayTradeForexDynamicSingleSLTFEnv, SmartDayTradeForexEnv,
                        SmartDayTradeForexDynamicSLTFEnv,
                        SmartDailyTradeForexEnv, SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv, SmartDayTradeSingleEnv,SmartPortfolioEnv, 
                        SmartPortfolioWithShortEnv,SmartDailyTradeForexDynamicSLTFDiffEnv,
                        SmartDayTradeEnv,SmartDayTradeEnv2, SmartSimpleForexDayTradeSingleEnv, SmartTradeEnv)

from stable_baselines3 import DDPG
from stable_baselines3.common.noise import (
    NormalActionNoise,
    OrnsteinUhlenbeckActionNoise,
)

from rltrade import config

from stable_baselines3 import A2C
from stable_baselines3 import PPO
from stable_baselines3 import TD3
from stable_baselines3.common.noise import (
    NormalActionNoise,
    OrnsteinUhlenbeckActionNoise,
)
from stable_baselines3.common.utils import set_random_seed

from stable_baselines3 import SAC

import asyncio
from metaapi_cloud_sdk import MetaApi
from rltrade.data import DiffrencedFeatureEngineer, FeatureEngineer,IBKRDownloader,DayTradeFeatureEngineer,OandaDownloader
from rltrade.ibkr import api_connect, buy_stock,sell_stock,get_stock_info


MODELS = {"a2c": A2C, "ddpg": DDPG, "td3": TD3, "sac": SAC, "ppo": PPO}

MODEL_KWARGS = {x: config.__dict__[f"{x.upper()}_PARAMS"] for x in MODELS.keys()}

NOISE = {
    "normal": NormalActionNoise,
    "ornstein_uhlenbeck": OrnsteinUhlenbeckActionNoise,
}

#################################
# Agent For portfolio Management#
#################################
class SmartPortfolioAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        time_frame='1 day',
        df=None,
        train_period=None,
        test_period=None,
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.time_frame = time_frame
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartPortfolioEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42) 
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df
    
    def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        self.data = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo,
                        time_frame=self.time_frame
                        ).fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartPortfolioEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return actions_memory[0].iloc[-1]
    
    def make_trade(self,actions,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print("stock data",stock_data)
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            if sectype == 'STK':
                current_price = stock_data[tic][0]
                num_stock =  int(self.env_kwargs['initial_amount'] * actions[i].item())/current_price
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                current_price = stock_data[tic[:-2]][0]
                num_stock =  int(self.env_kwargs['initial_amount'] * actions[i].item())/current_price
                current_quantity = stock_data[tic[:-2]][1]
            
            if current_price == -1:
                print(f"Price data for {tic} is not available")
                continue

            quantity = int(num_stock-current_quantity)
            print("quantity",quantity)
            print("in account",stock_data[tic][1])
            if quantity > 0:
                print("buying {} stocks of {}".format(quantity,tic))
                trade_log.loc[len(trade_log.index)] = [tic,"buy",quantity]
                buy_stock(app,tic,sectype,exchange,quantity)
            elif quantity < 0:
                print("selling {} stocks of {}".format(abs(quantity),tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"sell",abs(quantity)]
                sell_stock(app,tic,sectype,exchange,abs(quantity))
            else:
                print("Holding ticker {}".format(tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
        print("Trade Log")
        print(trade_log)
        app.disconnect()
    
    def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S").replace('-','')
        duration = f"{duration} S"
        self.trade_period = trade_period
        ib = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo)
        self.data = ib.fetch_min_data()
        time.sleep(3)
        print("Downloading Todays Data")
        todays_data = ib.fetch_todays_min_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp['date'] = pd.to_datetime(temp['date'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        print(temp)
        environment = SmartPortfolioEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        weights = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                weights.append(action)
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return weights[-1][0],actions_memory[0].iloc[-1]
    
    def make_day_trade(self,actions,weights,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        for i,tic in enumerate(ticker_list):
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            quantity = int((self.env_kwargs['initial_amount'] * actions[i].item())/stock_data[tic][0])
            weight = -1 if weights[i] < 0.5 else 1
            quantity = quantity * weight
            current_quantity = stock_data[tic][1]
            print(quantity,current_quantity)
            if quantity == current_quantity or quantity == 0:
                print(f"No Action {tic}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = quantity - current_quantity
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sec,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_buy = quantity - current_quantity
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                        buy_stock(app,tic,sec,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sec,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_sell = abs(quantity - current_quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                        sell_stock(app,tic,sec,exchange,to_sell)

        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def close_all_day_trade_positions(self,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid=accountid,demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            quantity = int(stock_data[tic][0])
            if quantity < 0:
                buy_stock(app,tic,sec,exchange,abs(quantity))
            elif quantity > 0:
                sell_stock(app,tic,sec,exchange,quantity)
            elif quantity == 0:
                print(f"{tic} Position already closed")
        app.disconnect()
        time.sleep(5)
    
    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output
    
    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

############################
#portfoli agent with short#
###########################
class SmartPortfolioWithShortAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        df=None,
        train_period=None,
        test_period=None,
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 
        set_random_seed(42)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartPortfolioWithShortEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartPortfolioWithShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartPortfolioWithShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df
    
    def get_trade_actions(self,trade_period):
        print("Downloading Data")
        self.trade_period = trade_period
        self.data = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo,
                        ).fetch_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartPortfolioWithShortEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return actions_memory[0].iloc[-1]
    
    def make_trade(self,actions,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            if sectype == 'STK':
                quantity = int((self.env_kwargs['initial_amount'] * actions[i].item())/stock_data[tic][0])
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                quantity = int((self.env_kwargs['initial_amount'] * actions[i].item())/stock_data[tic[:-2]][0])
                current_quantity = stock_data[tic[:-2]][1]

            print(quantity,current_quantity)
            if quantity == current_quantity or quantity == 0:
                print(f"No Action {tic}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = quantity - current_quantity
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sectype,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_buy = quantity - current_quantity
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sectype,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_sell = abs(quantity - current_quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_sell)

        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output
    
    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs
    
############################
#New agent for day trading #
############################ 
class SmartDayTradeAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        mode='daily',
        df=None,
        train_period=None,
        test_period=None,
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.mode = mode
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True,
                    mode=self.mode) 
        set_random_seed(42)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return account_memory[0], actions_memory[0]
    
    
    def get_day_trade_actions(self,time_now,duration,trade_period):
        print("Downloading Data")
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S").replace('-','')
        duration = f"{duration} S"
        self.trade_period = trade_period
        ib = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo)
        self.data = ib.fetch_min_data()
        time.sleep(3)
        print("Downloading Todays Data")
        todays_data = ib.fetch_todays_min_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp['date'] = pd.to_datetime(temp['date'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        print(temp)
        environment = SmartDayTradeEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        weights = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                weights = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        actions = [(x*2 -1) for x in weights[-1][:len(self.ticker_list)]]
        weights = self.softmax_normalization(weights[-1][len(self.ticker_list):])
        return actions,weights
    

    def make_day_trade(self,actions,weights,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,
                    self.exchanges,accountid,self.demo,)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        total_used = 0
        
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            amount = self.env_kwargs['initial_amount'] * weights[i] * actions[i]
            total_used += amount

            if sectype == 'STK':
                quantity = int((self.env_kwargs['initial_amount'] * weights[i] * actions[i])/stock_data[tic][0])
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                quantity = int((self.env_kwargs['initial_amount'] * weights[i] * actions[i])/stock_data[tic[:-2]][0])
                current_quantity = stock_data[tic[:-2]][1]

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    sell_stock(app,tic,sectype,exchange,current_quantity)
                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    buy_stock(app,tic,sectype,exchange,abs(current_quantity))
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = abs(quantity - current_quantity)
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sectype,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                        to_sell = abs(current_quantity - quantity)
                        print("sell {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_buy)
                    elif current_quantity < quantity:
                        to_buy = abs(quantity - current_quantity)
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long more",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sectype,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                        to_sell = abs(current_quantity - quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short more",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_buy)
                    elif current_quantity < quantity:
                        to_buy = abs(current_quantity - quantity)
                        print("buy to adjust {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",to_sell]
                        buy_stock(app,tic,sectype,exchange,to_sell)

        print(f"Total amount used {total_used}")
        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output
    
    def close_all_day_trade_positions(self,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = self.ticker_list
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid=accountid,demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            quantity = int(stock_data[tic][0])
            if sectype == 'STK':
                tic = tic.upper()
            elif sectype == 'FUT':
                tic = tic.upper()[:-2]

            if quantity < 0:
                buy_stock(app,tic,sectype,exchange,abs(quantity))
            elif quantity > 0:
                sell_stock(app,tic,sectype,exchange,quantity)
            elif quantity == 0:
                print(f"{tic} Position already closed")

        app.disconnect()
        time.sleep(5)
    
    def save_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        os.makedirs(path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(path+'/ext_data.csv',index=False)
        self.df.to_csv(path+'/df.csv',index=False)
        self.model.save(path+'/model')

    def load_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(path+'/df.csv')
        self.ext_data = pd.read_csv(path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs
        self.path = path

    def train_model(self):
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.ticker_list = environment.ticker_list
        self.sec_types = environment.sec_types
        self.exchanges = environment.exchanges
        self.model = model
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.ticker_list)]
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.model = model

###########################################
# Agent For portfolio Management with Diff#
###########################################
class SmartPortfolioDiffAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        time_frame = '1 day',
        df=None,
        train_period=None,
        test_period=None,
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.time_frame = time_frame
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = DiffrencedFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartPortfolioEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42) 
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df
    
    def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        self.data = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo,
                        time_frame = self.time_frame,
                        ).fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartPortfolioEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return actions_memory[0].iloc[-1]
    
    def make_trade(self,actions,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print("stock data",stock_data)
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            if sectype == 'STK':
                current_price = stock_data[tic][0]
                num_stock =  int(self.env_kwargs['initial_amount'] * actions[i].item())/current_price
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                current_price = stock_data[tic[:-2]][0]
                num_stock =  int(self.env_kwargs['initial_amount'] * actions[i].item())/current_price
                current_quantity = stock_data[tic[:-2]][1]
            
            if current_price == -1:
                print(f"Price data for {tic} is not available")
                continue

            quantity = int(num_stock-current_quantity)
            print("quantity",quantity)
            print("in account",stock_data[tic][1])
            if quantity > 0:
                print("buying {} stocks of {}".format(quantity,tic))
                trade_log.loc[len(trade_log.index)] = [tic,"buy",quantity]
                buy_stock(app,tic,sectype,exchange,quantity)
            elif quantity < 0:
                print("selling {} stocks of {}".format(abs(quantity),tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"sell",abs(quantity)]
                sell_stock(app,tic,sectype,exchange,abs(quantity))
            else:
                print("Holding ticker {}".format(tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
        print("Trade Log")
        print(trade_log)
        app.disconnect()
    
    def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S").replace('-','')
        duration = f"{duration} S"
        self.trade_period = trade_period
        ib = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        demo=self.demo)
        self.data = ib.fetch_min_data()
        time.sleep(3)
        print("Downloading Todays Data")
        todays_data = ib.fetch_todays_min_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp['date'] = pd.to_datetime(temp['date'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        print(temp)
        environment = SmartPortfolioEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        weights = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                weights.append(action)
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return weights[-1][0],actions_memory[0].iloc[-1]
    
    def make_day_trade(self,actions,weights,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        for i,tic in enumerate(ticker_list):
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            quantity = int((self.env_kwargs['initial_amount'] * actions[i].item())/stock_data[tic][0])
            weight = -1 if weights[i] < 0.5 else 1
            quantity = quantity * weight
            current_quantity = stock_data[tic][1]
            print(quantity,current_quantity)
            if quantity == current_quantity or quantity == 0:
                print(f"No Action {tic}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = quantity - current_quantity
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sec,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_buy = quantity - current_quantity
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                        buy_stock(app,tic,sec,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sec,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        print(f"No Action {tic}")
                        trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
                    elif current_quantity < quantity:
                        to_sell = abs(quantity - current_quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                        sell_stock(app,tic,sec,exchange,to_sell)

        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def close_all_day_trade_positions(self,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid=accountid,demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            quantity = int(stock_data[tic][0])
            if quantity < 0:
                buy_stock(app,tic,sec,exchange,abs(quantity))
            elif quantity > 0:
                sell_stock(app,tic,sec,exchange,quantity)
            elif quantity == 0:
                print(f"{tic} Position already closed")
        app.disconnect()
        time.sleep(5)
    
    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output
    
    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

################################
#Day Trading for single future #
################################
class SmartDayTradeSingleAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        time_frame= '4 hours',
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.time_frame = time_frame
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.max_vix_fix = self.env_kwargs['max_vix_fix']
        self.min_vix_fix = self.env_kwargs['min_vix_fix']
        self.vix_fix_lag = self.env_kwargs['vix_fix_lag']
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeSingleEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeSingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeSingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S").replace('-','')
        duration = f"{duration} S"
        self.trade_period = trade_period
        ib = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        start_time=self.start_time,
                        end_time=self.end_time,
                        demo=self.demo,
                        time_frame=self.time_frame)
        self.data = ib.fetch_data()
        time.sleep(3)
        print("Downloading Todays Data")
        todays_data = ib.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp['date'] = pd.to_datetime(temp['date'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(self.vix_fix_lag*len(self.ticker_list))
        environment = SmartDayTradeSingleEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        # total_contracts = 5
        # print(actions)
        # actions = np.array([int(x*total_contracts) for x in actions[-1]])
        # abs_actions = [abs(x) for x in actions]
        # top_actions = np.argsort(abs_actions)[::-1]
        # contracts = np.zeros(total_contracts)

        # for i in top_actions:
        #     if total_contracts - abs_actions[i] >=0:
        #         contracts[i] = actions[i]
        #         total_contracts -= abs_actions[i]
        #         total_contracts = max(0,total_contracts)
        #     else:
        #         contracts[i] = total_contracts
        # total_contracts = 2
        # contracts = np.array([int(x*total_contracts) for x in actions[-1]])

        contracts = list()
        for a in actions[-1]:
            if a == 0:
                contracts.append(-1)
            elif a == 1:
                contracts.append(0)
            elif a == 2:
                contracts.append(1)
        
        contracts = np.array(contracts)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return contracts

    def make_day_trade(self,actions,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,
                    self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        total_used = 0
        
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]

            if sectype == 'STK':
                quantity = actions[i]
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                quantity = actions[i]
                current_quantity = stock_data[tic[:-2]][1]

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    sell_stock(app,tic,sectype,exchange,current_quantity)
                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    buy_stock(app,tic,sectype,exchange,abs(current_quantity))
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = abs(quantity - current_quantity)
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sectype,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        to_sell = abs(current_quantity - quantity)
                        print("sell {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_sell)
                    elif current_quantity < quantity:
                        to_buy = abs(quantity - current_quantity)
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long more",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sectype,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        to_sell = abs(current_quantity - quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short more",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_sell)
                    elif current_quantity < quantity:
                        to_buy = abs(current_quantity - quantity)
                        print("buy to adjust {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)

        print(f"Total amount used {total_used}")
        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def close_all_day_trade_positions(self,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = self.ticker_list
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid=accountid,demo=self.demo)
        print(stock_data)
        for i,tic in enumerate(self.ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            if sectype == 'STK':
                tic = tic.upper()
                quantity = int(stock_data[tic][1])
            elif sectype == 'FUT':
                tic = tic.upper()
                quantity = int(stock_data[tic[:-2]][1])
            
            print(quantity)
            if quantity < 0:
                buy_stock(app,tic,sectype,exchange,abs(quantity))
            elif quantity > 0:
                sell_stock(app,tic,sectype,exchange,quantity)
            elif quantity == 0:
                print(f"{tic} Position already closed")

        app.disconnect()
        time.sleep(5)
    
    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs




####################
# Smart DayTrade 2 #
####################
class SmartDayTradeAgent2:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        mode='daily',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        demo=True,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.mode = mode
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None
        self.demo=demo

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True,
                    mode=self.mode) 
        set_random_seed(42)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeEnv2(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    
    def get_day_trade_actions(self,time_now,duration,trade_period):
        print("Downloading Data")
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S").replace('-','')
        duration = f"{duration} S"
        self.trade_period = trade_period
        ib = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list,
                        sec_types=self.sec_types,
                        exchanges=self.exchanges,
                        start_time=self.start_time,
                        end_time=self.end_time,
                        demo=self.demo)
        self.data = ib.fetch_min_data()
        time.sleep(3)
        print("Downloading Todays Data")
        todays_data = ib.fetch_todays_min_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp['date'] = pd.to_datetime(temp['date'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        print(temp)
        environment = SmartDayTradeEnv2(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        # total_contracts = 5
        # print(actions)
        # actions = np.array([int(x*total_contracts) for x in actions[-1]])
        # abs_actions = [abs(x) for x in actions]
        # top_actions = np.argsort(abs_actions)[::-1]
        # contracts = np.zeros(total_contracts)

        # for i in top_actions:
        #     if total_contracts - abs_actions[i] >=0:
        #         contracts[i] = actions[i]
        #         total_contracts -= abs_actions[i]
        #         total_contracts = max(0,total_contracts)
        #     else:
        #         contracts[i] = total_contracts
        # total_contracts = 2
        # contracts = np.array([int(x*total_contracts) for x in actions[-1]])

        contracts = list()
        for a in actions[-1]:
            if a == 0:
                contracts.append(-1)
            elif a == 1:
                contracts.append(0)
            elif a == 2:
                contracts.append(1)
        
        contracts = np.array(contracts)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return contracts

    def make_day_trade(self,actions,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_data = get_stock_info(app,ticker_list,self.sec_types,
                    self.exchanges,accountid,self.demo)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        print(stock_data)
        total_used = 0
        
        for i,tic in enumerate(ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]

            if sectype == 'STK':
                quantity = actions[i]
                current_quantity = stock_data[tic][1]
            elif sectype == 'FUT':
                quantity = actions[i]
                current_quantity = stock_data[tic[:-2]][1]

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    sell_stock(app,tic,sectype,exchange,current_quantity)
                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    buy_stock(app,tic,sectype,exchange,abs(current_quantity))
            
            elif quantity > 0:
                if current_quantity <= 0:
                    to_buy = abs(quantity - current_quantity)
                    print("long {} stocks of {}".format(to_buy,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"long",to_buy]
                    buy_stock(app,tic,sectype,exchange,to_buy)
                elif current_quantity > 0:
                    if current_quantity > quantity:
                        to_sell = abs(current_quantity - quantity)
                        print("sell {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_sell)
                    elif current_quantity < quantity:
                        to_buy = abs(quantity - current_quantity)
                        print("long {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long more",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)
            
            elif quantity < 0:
                if current_quantity >=0:
                    to_sell = abs(quantity - current_quantity)
                    print("short {} stocks of {}".format(to_sell,tic))
                    trade_log.loc[len(trade_log.index)] = [tic,"short",to_sell]
                    sell_stock(app,tic,sectype,exchange,to_sell)
                elif current_quantity < 0:
                    if current_quantity > quantity:
                        to_sell = abs(current_quantity - quantity)
                        print("short {} stocks of {}".format(to_sell,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"short more",to_sell]
                        sell_stock(app,tic,sectype,exchange,to_sell)
                    elif current_quantity < quantity:
                        to_buy = abs(current_quantity - quantity)
                        print("buy to adjust {} stocks of {}".format(to_buy,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",to_buy]
                        buy_stock(app,tic,sectype,exchange,to_buy)

        print(f"Total amount used {total_used}")
        print("Trade Log")
        print(trade_log)
        app.disconnect()
        time.sleep(5)
    
    def close_all_day_trade_positions(self,accountid):
        app = api_connect(demo=self.demo)
        ticker_list = self.ticker_list
        stock_data = get_stock_info(app,ticker_list,self.sec_types,self.exchanges,accountid=accountid,demo=self.demo)
        print(stock_data)
        for i,tic in enumerate(self.ticker_list):
            sectype = self.sec_types[i]
            exchange = self.exchanges[i]
            if sectype == 'STK':
                tic = tic.upper()
                quantity = int(stock_data[tic][1])
            elif sectype == 'FUT':
                tic = tic.upper()
                quantity = int(stock_data[tic[:-2]][1])
            
            print(quantity)
            if quantity < 0:
                buy_stock(app,tic,sectype,exchange,abs(quantity))
            elif quantity > 0:
                sell_stock(app,tic,sectype,exchange,quantity)
            elif quantity == 0:
                print(f"{tic} Position already closed")

        app.disconnect()
        time.sleep(5)

    def train_model(self):
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeEnv2(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.ticker_list = environment.ticker_list
        self.sec_types = environment.sec_types
        self.exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.ticker_list)]
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeEnv2(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.model = model
        self.train_df = environment.df
    
    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs


####################
# Smart DayTrade 3 #
####################
class SmartDayTradeAgent3:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeEnv3(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeEnv3(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeEnv3(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDayTradeEnv3(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        lots = list()
        for a in actions[-1]:
            if a == 0:
                lots.append(-0.1)
            elif a == 1:
                lots.append(0)
            elif a == 2:
                lots.append(0.1)
        
        lots = np.array(lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return lots

    async def make_day_trade(self,actions,account,connection):

        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

#######################################
# Smart DayTrade Forex with SL and TP #
#######################################
class SmartDayTradeForexAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.take_profit = self.env_kwargs['take_profit']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeForexEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeForexEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeForexEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDayTradeForexEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        lots = list()
        for a in actions[-1]:
            if a == 0:
                lots.append(-0.1)
            elif a == 1:
                lots.append(0)
            elif a == 2:
                lots.append(0.1)
        
        lots = np.array(lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)
            take_profit_sell = self.price_dict[tic] * (1 - self.take_profit)
            take_profit_buy = self.price_dict[tic] * (1 + self.take_profit)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs

################
#Daily trading #
################
class SmartTradeAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartTradeEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartTradeEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartTradeEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartTradeEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        lots = list()
        for a in actions[-1]:
            if a == 0:
                lots.append(-0.1)
            elif a == 1:
                lots.append(0)
            elif a == 2:
                lots.append(0.1)
        
        lots = np.array(lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

############################
# Smart Simple Forex Agent #
############################
class SmartSimpleDayTradeSingleForexAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = 0.015
        self.take_profit = 0.015
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=False)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartSimpleForexDayTradeSingleEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartSimpleForexDayTradeSingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(10*len(self.ticker_list))
        environment = SmartSimpleForexDayTradeSingleEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots = actions[:len_ticker_list]
        self.lots = np.array([self.lot_size * int(x) for x in lots])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)
            take_profit_sell = self.price_dict[tic] * (1 - self.take_profit)
            take_profit_buy = self.price_dict[tic] * (1 + self.take_profit)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs


#####################
#Daily Forex Trading#
#####################
class SmartDailyTradeForexAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.take_profit = self.env_kwargs['take_profit']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDailyTradeForexEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        lots = list()
        for a in actions[-1]:
            if a == 0:
                lots.append(-0.1)
            elif a == 1:
                lots.append(0)
            elif a == 2:
                lots.append(0.1)
        
        lots = np.array(lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)
            take_profit_sell = self.price_dict[tic] * (1 - self.take_profit)
            take_profit_buy = self.price_dict[tic] * (1 + self.take_profit)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

###############################################
# Smart DayTrade Forex with dynamic SL and TP #
###############################################
class SmartDayTradeForexDynamicSLTFAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeForexDynamicSLTFEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeForexDynamicSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.new_trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeForexDynamicSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDayTradeForexDynamicSLTFEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]
        self.lots = np.array([self.lot_size * int(x) for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs


############################################
#Daily Forex Trading with dynamic sl and tp#
############################################
class SmartDailyTradeForexDynamicSLTFAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexDynamicSLTFEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexDynamicSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexDynamicSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDailyTradeForexDynamicSLTFEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]       
        self.lots = np.array([self.lot_size * int(x) for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

###############################################
# Smart DayTrade Forex with dynamic SL and TP #
###############################################
class SmartDayTradeForexDynamicSLTFLongOrShortAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.long_or_short = self.env_kwargs['long_or_short']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeForexDynamicSLTFLongOrShortEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeForexDynamicSLTFLongOrShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.new_trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeForexDynamicSLTFLongOrShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDayTradeForexDynamicSLTFLongOrShortEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]
        if self.long_or_short == "long":
            self.lots = np.array([self.lot_size if x >= 0.5 else 0 for x in lots])
        elif self.long_or_short == "short":
            self.lots = np.array([-self.lot_size if x >= 0.5 else 0 for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs

#################################################################
# Smart DayTrade Forex with dynamic SL and TP for single symbol #
#################################################################
class SmartDayTradeForexDynamicSingleSLTFAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.max_vix_fix = self.env_kwargs['max_vix_fix']
        self.min_vix_fix = self.env_kwargs['min_vix_fix']
        self.vix_fix_lag = self.env_kwargs['vix_fix_lag']
        self.lots_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeForexDynamicSingleSLTFEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeForexDynamicSingleSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeForexDynamicSingleSLTFEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(self.vix_fix_lag*len(self.ticker_list))
        environment = SmartDayTradeForexDynamicSingleSLTFEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]
        self.lots = np.array([self.lot_size * int(x) for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs

##############################################################
#Daily Forex Trading with dynamic sl and tp for single symbol#
##############################################################
class SmartDailyTradeForexDynamicSingleSymbolSLTFAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.vix_fix_lag = self.env_kwargs['vix_fix_lag']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexDynamicSLTFSingleSymbolEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexDynamicSLTFSingleSymbolEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexDynamicSLTFSingleSymbolEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(self.vix_fix_lag*len(self.ticker_list))
        environment = SmartDailyTradeForexDynamicSLTFSingleSymbolEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]       
        self.lots = np.array([self.lot_size * int(x) for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs

#######################################################################################
# Smart DayTrade Forex with static SL and TP and dynamic volatility for single symbol #
#######################################################################################
class SmartDayTradeForexStaticSLTFDynamicVolititySingleAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        trades_per_stock,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='5m',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.take_profit = self.env_kwargs['take_profit']
        self.max_vix_fix = self.env_kwargs['max_vix_fix']
        self.min_vix_fix = self.env_kwargs['min_vix_fix']
        self.vix_fix_lag = self.env_kwargs['vix_fix_lag']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.filter_trades_per_stock = environment.trades_per_stock
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['trades_per_stock'] = self.filter_ticker_list
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['trades_per_stock'] = self.filter_trades_per_stock
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.trades_per_stock = self.filter_trades_per_stock
        self.model = model
        self.train_df = environment.df
    
    # For live trading.
    async def get_day_trade_actions(self,time_now,duration,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        tz = pytz.timezone('EST')
        time_now = tz.localize(time_now).astimezone(tz)
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_data()
        print("Downloading Todays Data")
        todays_data = await oa.fetch_todays_data(time_now,duration)
        self.data = self.data.append(todays_data)
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(self.vix_fix_lag*len(self.ticker_list))
        environment = SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots = actions[:len_ticker_list]
        self.lots = np.array([self.lot_size * int(x) for x in lots])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_day_trade(self,actions,account,connection):
        terminal_state = connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)
            take_profit_sell = self.price_dict[tic] * (1 - self.take_profit)
            take_profit_buy = self.price_dict[tic] * (1 + self.take_profit)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await connection.close_positions_by_symbol(symbol=tic)
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))

        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges,
                                     'trades_per_stock':self.trades_per_stock})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.trades_per_stock = self.ext_data['trades_per_stock'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['trades_per_stock'] = self.trades_per_stock
        self.env_kwargs['epochs'] = self.epochs

####################################################################################
#Daily Forex Trading with static sl and tp and dynamic volatility for single symbol#
####################################################################################
class SmartDailyTradeForexStaticSLTFDynamicVolititySingleAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.stop_loss = self.env_kwargs['stop_loss']
        self.take_profit = self.env_kwargs['take_profit']
        self.max_vix_fix = self.env_kwargs['max_vix_fix']
        self.min_vix_fix = self.env_kwargs['min_vix_fix']
        self.vix_fix_lag = self.env_kwargs['vix_fix_lag']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(self.vix_fix_lag*len(self.ticker_list))
        environment = SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots = actions[:len_ticker_list]      
        self.lots = np.array([self.lot_size * int(x) for x in lots])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.stop_loss)
            stop_loss_buy = self.price_dict[tic] * (1 - self.stop_loss)
            take_profit_sell = self.price_dict[tic] * (1 - self.take_profit)
            take_profit_buy = self.price_dict[tic] * (1 + self.take_profit)

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs



##########################################################
#Daily Forex Trading with dynamic sl and tp short or long#
##########################################################
class SmartDailyTradeForexDynamicSLTFLongOrShortAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.long_or_short = self.env_kwargs['long_or_short']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexDynamicSLTFLongOrShortEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexDynamicSLTFLongOrShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexDynamicSLTFLongOrShortEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDailyTradeForexDynamicSLTFLongOrShortEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]       
        if self.long_or_short == "long":
            self.lots = np.array([self.lot_size if x >= 0.5 else 0 for x in lots])
        elif self.long_or_short == "short":
            self.lots = np.array([-self.lot_size if x >= 0.5 else 0 for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs


#################################################
#Daily Forex Trading with dynamic diff sl and tp#
#################################################
class SmartDailyTradeForexDynamicSLTFDiffAgent:

    def __init__(self,
        model_name,
        ticker_list,
        sec_types,
        exchanges,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,
        account,
        time_frame='1d',
        df=None,
        train_period=None,
        test_period=None,
        start_time="09:30:00",
        end_time="15:59:00",
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.start_time = start_time
        self.end_time = end_time
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.account = account
        self.time_frame = time_frame
        self.max_stop_loss = self.env_kwargs['max_stop_loss']
        self.max_take_profit = self.env_kwargs['max_take_profit']
        self.lot_size = self.env_kwargs['lot_size']
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DiffrencedFeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartDailyTradeForexDynamicSLTFDiffEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        self.test_df = environment.df
        self.test_df.to_csv(self.path+'/test_df.csv',index=False)
        self.test_df_sort = self.test_df.sort_values(['tic','date'])
        self.test_df_sort.to_csv(self.path+'/test_sort.csv',index=False)
        return account_memory[0], actions_memory[0]
    
    def train_model(self):
        set_random_seed(42)
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['sec_types'] = self.sec_types
        self.env_kwargs['exchanges'] = self.exchanges
        self.env_kwargs['epochs'] = self.epochs
        environment = SmartDailyTradeForexDynamicSLTFDiffEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.filter_ticker_list = environment.ticker_list
        self.filter_sec_types = environment.sec_types
        self.filter_exchanges = environment.exchanges
        self.model = model
        self.train_df = environment.df
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.filter_ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.filter_ticker_list)]
        self.env_kwargs['ticker_list'] = self.filter_ticker_list
        self.env_kwargs['sec_types'] = self.filter_sec_types
        self.env_kwargs['exchanges'] = self.filter_exchanges
        self.env_kwargs['epochs'] = self.epochs
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps
        environment = SmartDailyTradeForexDynamicSLTFDiffEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.ticker_list = self.filter_ticker_list
        self.sec_types = self.filter_sec_types
        self.exchanges = self.filter_exchanges
        self.model = model
        self.train_df = environment.df  
  
    # For live trading.
    async def get_trade_actions(self,trade_period):
        torch.manual_seed(42)
        print("Downloading Data")
        self.trade_period = trade_period
        oa = OandaDownloader(
                account=self.account,
                time_frame=self.time_frame,
                start_date=self.trade_period[0],
                end_date=self.trade_period[1],
                start_time=self.start_time,
                end_time=self.end_time,
                ticker_list=self.ticker_list)

        self.data = await oa.fetch_daily_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        self.df['date'] =  pd.to_datetime(self.df['date'])
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartDailyTradeForexDynamicSLTFDiffEnv(df=temp,**self.env_kwargs)

        self.price_data = temp.tail(len(self.ticker_list)).loc[:,['tic','close']].values
        self.price_dict = {}
        for tic,close in self.price_data:
            self.price_dict[tic] = close
        
        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        actions_memory = []
        actions = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            actions_memory.append(action)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
                actions = action
                actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break

        actions = actions[-1]
        len_ticker_list = len(self.ticker_list)
        lots,new_stop_loss_per,new_take_profit_per = actions[:len_ticker_list],actions[len_ticker_list:2*len_ticker_list],actions[:-len_ticker_list]       
        self.lots = np.array([self.lot_size * int(x) for x in lots])
        self.new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
        self.new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

        self.lots = np.array(self.lots)
        self.live_df = environment.df
        if os.path.exists(self.path+'/live_df.csv'):
            df_live = pd.read_csv(self.path+'/live_df.csv')
            df_live = df_live.append(self.live_df)
            df_live.to_csv(self.path+'/live_df.csv',index=False)
        else:
            self.live_df.to_csv(self.path+'/live_df.csv',index=False)
        return self.lots

    async def make_trade(self,actions,account,streaming_connection):
        terminal_state = streaming_connection.terminal_state
        stock_data = terminal_state.positions
        ticker_list = [x.upper() for x in self.ticker_list]
        stock_dict = {}
        for s in stock_data:
            if 'SELL' in s['type']:
                stock_dict[s['symbol']] = -s['volume']
            elif 'BUY' in s['type']:
                stock_dict[s['symbol']] = s['volume']
        
        for tic in ticker_list:
            if stock_dict.get(tic) is None:
                stock_dict[tic] = 0
        
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        
        for i,tic in enumerate(ticker_list):
            quantity = actions[i]
            current_quantity = stock_dict[tic]
            stop_loss_sell = self.price_dict[tic] * (1 + self.new_stop_loss_per[i])
            stop_loss_buy = self.price_dict[tic] * (1 - self.new_stop_loss_per[i])
            take_profit_sell = self.price_dict[tic] * (1 - self.new_take_profit_per[i])
            take_profit_buy = self.price_dict[tic] * (1 + self.new_take_profit_per[i])

            print(quantity,current_quantity)
            if quantity == current_quantity:
                print(f"No Action {tic}, current Position {current_quantity}")
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
            
            if quantity == 0:
                if current_quantity > 0:
                    print(f"Closing {tic}, selling {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"selling to close failed",current_quantity]

                elif current_quantity < 0:
                    print(f"Closing {tic}, buying {current_quantity} to close")
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        trade_log.loc[len(trade_log.index)] = [tic,"buying to close",current_quantity]
                    except Exception as err:
                        print(err)
                        print(f"Failed closing {tic}, buying {current_quantity} to close")
                        trade_log.loc[len(trade_log.index)] = [tic,"failed buying to close",current_quantity]
            
            elif quantity > 0:
                if current_quantity < 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("results3",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"long failed",quantity]
                elif current_quantity == 0:
                    print("long {} stocks of {}".format(quantity,tic))
                    try:
                        results = await streaming_connection.create_market_buy_order(symbol=tic,volume=quantity,stop_loss=stop_loss_buy,take_profit=take_profit_buy)
                        trade_log.loc[len(trade_log.index)] = [tic,"long",quantity]
                        print("resuts2",results)
                    except Exception as err:
                        print(err)
                        print("failed long {} stocks of {}".format(quantity,tic))
                        trade_log.loc[len(trade_log.index)] = [tic,"failed long",quantity]


                # elif current_quantity > 0:
                #     if current_quantity > quantity:
                #         print("sell {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"sell to adjust",quantity]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=quantity))
                #     elif current_quantity < quantity:
                #         print("long {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"long more",quantity]
                #         print(await connection.create_market_buy_order(symbol=tic,volume=quantity))
            
            elif quantity < 0:
                if current_quantity > 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try:
                        await streaming_connection.close_positions_by_symbol(symbol=tic)
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results1",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                elif current_quantity == 0:
                    print("short {} stocks of {}".format(abs(quantity),tic))
                    try: 
                        results = await streaming_connection.create_market_sell_order(symbol=tic,volume=abs(quantity),stop_loss=stop_loss_sell,take_profit=take_profit_sell)
                        trade_log.loc[len(trade_log.index)] = [tic,"short",abs(quantity)]
                        print("results",results)
                    except Exception as err:
                        print("failed short {} stocks of {}".format(abs(quantity),tic))
                        print(err)
                        trade_log.loc[len(trade_log.index)] = [tic,"failed short",abs(quantity)]
                        

                # elif current_quantity < 0:
                #     if current_quantity > quantity:
                #         print("short {} stocks of {}".format(abs(quantity),tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"short more",abs(quantity)]
                #         print(await connection.create_market_sell_order(symbol=tic,volume=abs(quantity)))
                #     elif current_quantity < quantity:
                #         print("buy to adjust {} stocks of {}".format(quantity,tic))
                #         trade_log.loc[len(trade_log.index)] = [tic,"buy to adjust",abs(quantity)]
                #         print(await connection.create_limit_buy_order(symbol=tic,volume=quantity))
        
        print("Trade Log")
        print(trade_log)

    def save_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        os.makedirs(self.path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list,
                                     'sec_types':self.sec_types,
                                     'exchanges':self.exchanges})
        self.ext_data.to_csv(self.path+'/ext_data.csv',index=False)
        self.df.to_csv(self.path+'/df.csv',index=False)
        self.train_df.to_csv(self.path+'/train_df.csv',index=False)
        self.train_df_sort = self.train_df.sort_values(['tic','date'])
        self.train_df_sort.to_csv(self.path+'/train_sort.csv',index=False)
        self.model.save(self.path+'/model')

    def load_model(self,path:str):
        self.path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(self.path+'/df.csv')
        self.ext_data = pd.read_csv(self.path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.sec_types = self.ext_data['sec_types'].tolist()
        self.exchanges = self.ext_data['exchanges'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.env_kwargs['epochs'] = self.epochs