from asyncio.tasks import current_task
import math
import gym
import numpy as np
import pandas as pd
from gym import spaces
from gym.utils import seeding
import matplotlib.pyplot as plt
from scipy.stats import skew,kurtosis
from stable_baselines3.common.vec_env import DummyVecEnv

################################################
# This environment is for portfolio management #
################################################ 
class SmartPortfolioEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(self.stock_dim,))
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(len(self.tech_indicator_list) + 7, self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = []

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            weights = self.softmax_normalization(actions)
            self.actions_memory.append(weights)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values / close_values - 1) * weights
            return_values_per_stock = return_values * self.portfolio_value
            portfolio_return = sum(return_values_per_stock)

            #update stocks in portfolio
            stocks_to_buy = [(x*self.initial_amount)/y for x,y in zip(weights,self.data['close'])]
            adjust_stock = [abs(x-y) for x,y in zip(stocks_to_buy,self.stocks_in_portfolio)]
            self.stocks_in_portfolio = stocks_to_buy
            transaction_cost_per_stock = [self.transaction_cost if x!=0 else 0 for x in adjust_stock]
            total_transaction_cost = sum(transaction_cost_per_stock)

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = self.portfolio_value + portfolio_return - total_transaction_cost
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # print(total_transaction_cost,end_total_asset-begin_total_asset)

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0]
            self.state[:len(self.tech_indicator_list)] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-7,:] = self.data['open'].values
            self.state[-6,:] = self.data['close'].values
            self.state[-5,:] = self.data['high'].values
            self.state[-4,:] = self.data['low'].values
            self.state[-3,:] = weights
            self.state[-2,:] = return_values_per_stock
            self.state[-1,:] = (return_values_per_stock - transaction_cost_per_stock)

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'weights'] = weights
            self.df.loc[self.day-1,'return'] = return_values_per_stock
            self.df.loc[self.day-1,'return with cost'] = return_values_per_stock - transaction_cost_per_stock
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        years = self.day/252
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    

    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = []
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

####################################
# Portfolio environment with short #
####################################
class SmartPortfolioWithShortEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(self.stock_dim,))
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(len(self.tech_indicator_list) + 6, self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = []

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            short_or_long = np.array([-1 if x<0.5 else 1 for x in actions])
            weights = self.softmax_normalization(actions)
            weights = short_or_long * weights
            self.actions_memory.append(weights)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #calculate return
            close_values = last_day_memory.close.values
            close_values[close_values==0] = 0.1
            return_values = (self.data.close.values / close_values - 1) * weights
            return_values_per_stock = return_values * self.portfolio_value
            portfolio_return = sum(return_values_per_stock)

            #update stocks in portfolio
            stocks_to_buy = [(x*self.initial_amount)/y for x,y in zip(weights,self.data['close'])]
            adjust_stock = [abs(x-y) for x,y in zip(stocks_to_buy,self.stocks_in_portfolio)]
            self.stocks_in_portfolio = stocks_to_buy
            transaction_cost_per_stock = [self.transaction_cost if x!=0 else 0 for x in adjust_stock]
            total_transaction_cost = sum(transaction_cost_per_stock)

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = self.portfolio_value + portfolio_return - total_transaction_cost
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # print(total_transaction_cost,end_total_asset-begin_total_asset)

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0]
            self.state[:len(self.tech_indicator_list)] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-6,:] = self.data['close'].values
            self.state[-5,:] = self.data['high'].values
            self.state[-4,:] = self.data['low'].values
            self.state[-3,:] = weights
            self.state[-2,:] = return_values_per_stock
            self.state[-1,:] = (return_values_per_stock - transaction_cost_per_stock)

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'actions'] = weights
            self.df.loc[self.day-1,'return'] = return_values_per_stock
            self.df.loc[self.day-1,'return with cost'] = return_values_per_stock - transaction_cost_per_stock

            # print(self.reward)
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        years = self.day/252
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        # print(reward_metrics)
        # time.sleep(1)

        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    

    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = []
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        # date and close price length must match actions length
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

################################################
# This environment is for portfolio management #
################################################ 
class SmartPortfolioDiffEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(self.stock_dim,))
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(len(self.tech_indicator_list) + 7, self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open_diff'].values,
            self.data['close_diff'].values,
            self.data['high_diff'].values,
            self.data['low_diff'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = []

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            weights = self.softmax_normalization(actions)
            self.actions_memory.append(weights)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values / close_values - 1) * weights
            return_values_per_stock = return_values * self.portfolio_value
            portfolio_return = sum(return_values_per_stock)

            #update stocks in portfolio
            stocks_to_buy = [(x*self.initial_amount)/y for x,y in zip(weights,self.data['close'])]
            adjust_stock = [abs(x-y) for x,y in zip(stocks_to_buy,self.stocks_in_portfolio)]
            self.stocks_in_portfolio = stocks_to_buy
            transaction_cost_per_stock = [self.transaction_cost if x!=0 else 0 for x in adjust_stock]
            total_transaction_cost = sum(transaction_cost_per_stock)

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = self.portfolio_value + portfolio_return - total_transaction_cost
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # print(total_transaction_cost,end_total_asset-begin_total_asset)

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0]
            self.state[:len(self.tech_indicator_list)] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-7,:] = self.data['open_diff'].values
            self.state[-6,:] = self.data['close_diff'].values
            self.state[-5,:] = self.data['high_diff'].values
            self.state[-4,:] = self.data['low_diff'].values
            self.state[-3,:] = weights
            self.state[-2,:] = return_values_per_stock
            self.state[-1,:] = (return_values_per_stock - transaction_cost_per_stock)

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'return'] = return_values_per_stock
            self.df.loc[self.day-1,'return with cost'] = return_values_per_stock - transaction_cost_per_stock
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        years = self.day/252
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    

    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open_diff'].values,
            self.data['close_diff'].values,
            self.data['high_diff'].values,
            self.data['low_diff'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = []
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


###########################################
# This is new environment for day trading #
###########################################
class SmartDayTradeEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        mode='min',
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.mode = mode
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(2*self.stock_dim,))
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.stock_dim + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            actions,weights = actions[:self.stock_dim],actions[self.stock_dim:]
            actions = (actions * 2) -1
            weights = self.softmax_normalization(weights)
            weights = actions * weights
            self.actions_memory.append(actions+weights)
            last_day_memory = self.data
            # print(actions,weights)

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]
            self.covs = self.data["cov_list"].values[0]
            self.state = np.append(
                np.array(self.covs),
                [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
                axis=0,)

            #calculate return
            close_values = last_day_memory.close.values
            close_values[close_values==0] = 0.1
            return_values = (self.data.close.values / close_values - 1) * weights
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            stocks_to_buy = [(x*self.initial_amount)/y for x,y in zip(weights,self.data['close'])]
            adjust_stock = [abs(x-y) for x,y in zip(stocks_to_buy,self.stocks_in_portfolio)]
            self.stocks_in_portfolio = stocks_to_buy
            total_transaction_cost = sum([self.transaction_cost for x in adjust_stock if x!=0])

            # update portfolio value
            begin_total_asset = self.portfolio_value
            if self.mode == 'daily':
                new_portfolio_value = (self.portfolio_value * (1 + portfolio_return) ) - total_transaction_cost
            else:
                new_portfolio_value = (self.portfolio_value * (1 + portfolio_return) ) - total_transaction_cost
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            # print(self.reward)
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric * 0.001

        #cagr calculation
        years = self.day/252
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        # print(reward_metrics)
        # time.sleep(1)

        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    

    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        # date and close price length must match actions length
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

################################
#Day Trading for single future #
################################
class SmartDayTradeSingleEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_vix_fix = 2,
        min_vix_fix = 0.5,
        vix_fix_lag = 22,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_vix_fix = max_vix_fix
        self.min_vix_fix = min_vix_fix
        self.vix_fix_lag = vix_fix_lag
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(9 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.volatality_per_stock = list()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.current_date = self.data['only date']
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.trades_per_stock_memory  = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                pass

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            # total_contracts = 5
            # actions = np.array([int(x*total_contracts) for x in actions])
            # abs_actions = [abs(x) for x in actions]
            # top_actions = np.argsort(abs_actions)[::-1][:total_contracts]
            # contracts = np.zeros(self.stock_dim)

            # for i in top_actions:
            #     if (total_contracts - abs_actions[i]) >=0:
            #         contracts[i] = actions[i]
            #         total_contracts -= abs_actions[i]
            #         total_contracts = np.max([0,total_contracts])
            #     else:
            #         contracts[i] = total_contracts
            # total_contracts = 2
            # contracts = np.array([int(x*total_contracts) for x in actions])
            
            # load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day, :]   

            prev_contracts = self.state[-3,:]
            contracts = list()
            for a in actions:
                if a == 0:
                    contracts.append(-1)
                elif a == 1:
                    contracts.append(0)
                elif a == 2:
                    contracts.append(1)
            contracts = np.array(contracts)

            #check for number of trades left
            last_date= self.current_date
            new_date = last_day_memory['only date']
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-4,:]

            self.actions_memory.append(actions)

            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_contracts)):
                cl = contracts[i]
                pl = prev_contracts[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    contracts[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    contracts[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]


            if last_day_memory['market closed']:
                contracts = np.array([0 for x in range(len(contracts))])  

            self.ticker_memory.append(last_day_memory['tic'])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close']) 

            #check for volatility
            closed_by_volatality = np.zeros(self.stock_dim)
            self.volatality_per_stock = self.get_volatality_per_stock()
            for i in range(self.stock_dim):
                v = self.volatality_per_stock[i]
                if (v <= self.min_vix_fix or v>= self.max_vix_fix) and contracts[i] !=0:
                    contracts[i] = 0
                    closed_by_volatality[i] = 1     

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * np.array(contracts) * 1000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(contracts,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = contracts

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(return_values)
            self.trades_per_stock_memory.append(self.start_trade_per_stock)           

            self.reward = self.get_reward(contracts,prev_contracts,return_values,new_date,last_date)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array([[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-9,:] = self.data['open']
            self.state[-8,:] = self.data['close']
            self.state[-7,:] = self.data['high']
            self.state[-6,:] = self.data['low']
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = new_number_of_trades
            self.state[-3,:] = contracts
            self.state[-2,:] = return_values
            self.state[-1,:] = (return_values - total_transaction_cost_per_stock)
            
            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'contracts'] = contracts
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'closed by volatility'] = closed_by_volatality
            self.df.loc[self.day-1,'volatility'] = self.volatality_per_stock
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,contracts,prev_contracts,return_values,new_date,last_date):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "daily":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if contracts[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #unrealized
                cl = contracts[i]
                pl = prev_contracts[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #daily
                if new_date != last_date:
                    metric_dict['daily'][i] = return_values[i]
                else:
                    metric_dict['daily'][i] += return_values[i]

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric]
        
        return sum(self.reward_per_stock) * self.reward_scaling

    def get_volatality_per_stock(self):
        self.volatality_per_stock = list()
        df_temp = pd.DataFrame({
            "tic":self.ticker_memory,
            "close":self.close_values_memory,
            "low":self.low_values_memory,
        })

        for tic in self.ticker_list:
            df_tic = df_temp.query(f"tic == '{tic}'")
            max_close = df_tic.loc[-self.vix_fix_lag:,'close'].max()
            low = df_tic.iloc[-1,df_tic.columns.get_loc('low')].item()
            self.volatality_per_stock.append((max_close-low)*100/max_close)
        
        return self.volatality_per_stock
    
    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')


        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.volatality_per_stock = list()
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

    
##################
#Day Trade Env 2 #
##################
class SmartDayTradeEnv2(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        mode='min',
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.mode = mode
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.stock_dim + 6 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            (np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("total reward:{}".format(sum(self.reward_memory)))
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            # total_contracts = 5
            # actions = np.array([int(x*total_contracts) for x in actions])
            # abs_actions = [abs(x) for x in actions]
            # top_actions = np.argsort(abs_actions)[::-1][:total_contracts]
            # contracts = np.zeros(self.stock_dim)

            # for i in top_actions:
            #     if (total_contracts - abs_actions[i]) >=0:
            #         contracts[i] = actions[i]
            #         total_contracts -= abs_actions[i]
            #         total_contracts = np.max([0,total_contracts])
            #     else:
            #         contracts[i] = total_contracts
            # total_contracts = 2
            # contracts = np.array([int(x*total_contracts) for x in actions])

            contracts = list()
            for a in actions:
                if a == 0:
                    contracts.append(-1)
                elif a == 1:
                    contracts.append(0)
                elif a == 2:
                    contracts.append(1)
            
            contracts = np.array(contracts)

            self.actions_memory.append(actions)
            last_day_memory = self.data

            if last_day_memory['market closed'].values[0]:
                contracts = np.array([0 for x in range(len(contracts))])

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]           

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * np.array(contracts)
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(contracts,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = contracts

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:self.stock_dim,:] = np.array(self.covs)
            self.state[self.stock_dim:self.stock_dim+len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-6,:] = self.data['close'].values
            self.state[-5,:] = self.data['high'].values
            self.state[-4,:] = self.data['low'].values
            self.state[-3,:] = contracts
            self.state[-2,:] = return_values
            self.state[-1,:] = (return_values - total_transaction_cost_per_stock)

            if contracts[0] == 0 and contracts[1] == 0:
                self.reward = 0
            
            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'contracts'] = contracts
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')


        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            (np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

##################
#Day Trade Env 3 #
##################
class SmartDayTradeEnv3(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        trades_per_stock,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.stop_loss = stop_loss
        self.trades_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(8 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date'].values[0]
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            # load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day, :]

            lots = list()
            prev_lots = self.state[-4,:]
            for i,a in enumerate(actions):
                if a == 0:
                    lots.append(-0.1)
                elif a == 1:
                    lots.append(0)
                elif a == 2:
                    lots.append(0.1)
            lots = np.array(lots)

            #check for number of trades left
            new_date = self.data['only date'].values[0]
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
            else:
                prev_number_of_trades = self.state[-5,:]

            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]
            
            #stop loss logic
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - self.stop_loss)
            
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 100000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-8,:] = self.data['close'].values
            self.state[-7,:] = self.data['high'].values
            self.state[-6,:] = self.data['low'].values
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            
            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'number of trades left'] = prev_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')


        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic","date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

###################################################
# Forex Day trading with stop loss and take profit#
###################################################
class SmartDayTradeForexEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        take_profit= 0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.trades_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(11 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date'].values[0]
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]
                self.trades_per_stock = df_metrics['trades_per_stock'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            # load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day, :]

            lots = list()
            prev_lots = self.state[-4,:]
            for i,a in enumerate(actions):
                if a == 0:
                    lots.append(-0.1)
                elif a == 1:
                    lots.append(0)
                elif a == 2:
                    lots.append(0.1)
            lots = np.array(lots)

            #check for number of trades left
            new_date = last_day_memory['only date'].values[0]
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-5,:]

            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]
            
            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - self.stop_loss)
                    elif cl == 0:
                        new_stop_loss[i] = 0
            
            #take profit logic
            prev_take_profit = self.state[-7,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - self.take_profit)
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + self.take_profit)
                    elif cl == 0:
                        new_take_profit[i] = 0
                    
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 100000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.trades_per_stock_memory.extend(self.trades_per_stock)
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-11,:] = self.data['open'].values
            self.state[-10,:] = self.data['close'].values
            self.state[-9,:] = self.data['high'].values
            self.state[-8,:] = self.data['low'].values
            self.state[-7,:] = new_take_profit
            self.state[-6,:] = self.reward_per_stock
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    def get_delayed_reward(self,lots,prev_lots,return_values):
        reward = 0
        for i in range(len(lots)):
            cl = lots[i]
            pl = prev_lots[i]
            if pl != cl and pl!=0:
                reward += self.reward_per_stock[i]
                self.reward_per_stock[i] = 0
            elif (pl==cl) or (pl != cl and pl==0):
                # reward += self.reward_per_stock[i] * 0.5 + return_values[i] * 0.5
                reward += self.reward_per_stock[i] * 0.8
                # reward += return_values[i]
                self.reward_per_stock[i] += return_values[i]
        return reward
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "trades_per_stock":self.trades_per_stock_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')

        df_temp = df_temp.groupby(["tic","sec","exchange","trades_per_stock"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic","date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs
        
#############################
# Daily Trading environment #
#############################
class SmartTradeEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.stop_loss = stop_loss
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(7 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            lots = list()
            for a in actions:
                if a == 0:
                    lots.append(-0.1)
                elif a == 1:
                    lots.append(0)
                elif a == 2:
                    lots.append(0.1)
                        
            self.actions_memory.append(actions)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #stop loss logic
            lots = np.array(lots)
            prev_stop_loss = self.state[-1,:]
            prev_lots = self.state[-4,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - self.stop_loss)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 100000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-7,:] = self.data['close'].values
            self.state[-6,:] = self.data['high'].values
            self.state[-5,:] = self.data['low'].values
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss
            
            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

###################################################
# Forex Day trading with stop loss and take profit#
###################################################
class SmartDailyTradeForexEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        take_profit=0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.MultiDiscrete([3] * self.stock_dim)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            lots = list()
            prev_lots = self.state[-4,:]
            for a in actions:
                if a == 0:
                    lots.append(-0.1)
                elif a == 1:
                    lots.append(0)
                elif a == 2:
                    lots.append(0.1)
                        
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - self.stop_loss)
                    elif cl == 0:
                        new_stop_loss[i] = 0
            
            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - self.take_profit)
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + self.take_profit)
                    elif cl == 0:
                        new_take_profit[i] = 0
                    
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 100000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open'].values
            self.state[-9,:] = self.data['close'].values
            self.state[-8,:] = self.data['high'].values
            self.state[-7,:] = self.data['low'].values
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

#################################################################
# Day Trading Environment for Dynamic stop loss and take profit #
#################################################################
class SmartDayTradeForexDynamicSLTFEnv(gym.Env):
    
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit= 0.015,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_take_profit = max_take_profit
        self.max_stop_loss = max_stop_loss
        self.lot_size = lot_size
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(11 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date'].values[0]
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)
    
    def step(self,actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]
                self.new_trades_per_stock = df_metrics['trades_per_stock'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}
        
        else:
            #load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day,:]

            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

            #check for number of trades left
            last_date= self.current_date
            new_date = last_day_memory['only date'].values[0]
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-5,:]
            
            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]
            
            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0   

            #take profit logic
            prev_take_profit = self.state[-7,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
            
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(portfolio_return_per_stock.ravel().tolist())
            self.ticker_memory.extend(self.data["tic"].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.trades_per_stock_memory.extend(self.start_trade_per_stock)
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            # self.reward = self.get_reward_old(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,prev_lots,return_values,new_date,last_date)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-11,:] = self.data['open'].values
            self.state[-10,:] = self.data['close'].values
            self.state[-9,:] = self.data['high'].values
            self.state[-8,:] = self.data['low'].values
            self.state[-7,:] = new_take_profit
            self.state[-6,:] = self.reward_per_stock
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    def get_delayed_reward(self,lots,prev_lots,return_values):
        reward = 0
        for i in range(len(lots)):
            cl = lots[i]
            pl = prev_lots[i]
            if pl != cl and pl!=0:
                reward += self.reward_per_stock[i]
                self.reward_per_stock[i] = 0
            elif (pl==cl) or (pl != cl and pl==0):
                reward += self.reward_per_stock[i] * 0.8
                self.reward_per_stock[i] += return_values[i]
        return reward
    
    def get_reward(self,lots,prev_lots,return_values,new_date,last_date):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "daily":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #daily
                if new_date != last_date:
                    metric_dict['daily'][i] = return_values[i]
                else:
                    metric_dict['daily'][i] += return_values[i]

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric]
        
        return sum(self.reward_per_stock) * self.reward_scaling

    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward

    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "trades_per_stock":self.trades_per_stock_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')

        df_temp = df_temp.groupby(["tic","sec","exchange","trades_per_stock"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic","date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


#################################################################
# Day Trading Environment for Dynamic stop loss and take profit #
#################################################################
class SmartDailyTradeForexDynamicSLTFEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        lot_size = 0.1,
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit=0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.lot_size = lot_size
        self.transaction_cost = transaction_cost
        self.max_stop_loss = max_stop_loss
        self.max_take_profit = max_take_profit
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

       # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])
                        
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0  

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
                    
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(portfolio_return_per_stock.ravel().tolist())
            self.ticker_memory.extend(self.data["tic"].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            # self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,prev_lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open'].values
            self.state[-9,:] = self.data['close'].values
            self.state[-8,:] = self.data['high'].values
            self.state[-7,:] = self.data['low'].values
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,lots,prev_lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling
    
    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


#################################
# Simple single forex trading env
#################################
class SmartSimpleForexDayTradeSingleEnv(gym.Env):
    
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.lot_size = lot_size
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(5 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.volatality_per_stock = list()
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date']
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * self.stock_dim
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)
    
    def step(self,actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}
        
        else:
            #load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day,:]

            prev_lots = self.state[-1,:]
            lots = np.array([self.lot_size * int(x) for x in actions])

            # check for number of trades left
            last_date= self.current_date
            new_date = last_day_memory['only date']

            self.ticker_memory.append(last_day_memory["tic"])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close'])
                
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * lots * 1000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(portfolio_return_per_stock)
            self.trades_per_stock_memory.append(self.start_trade_per_stock)           

            self.reward = self.get_reward(lots,prev_lots,return_values,new_date,last_date)
            self.reward_memory.append(self.reward)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array([[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-5,:] = self.data['open']
            self.state[-4,:] = self.data['close']
            self.state[-3,:] = self.data['high']
            self.state[-2,:] = self.data['low']
            self.state[-1,:] = lots

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            
        return self.state, self.reward, self.terminal, {}
    
    
    def get_reward(self,lots,prev_lots,return_values,new_date,last_date):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "daily":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'][i] += return_values[i]

                #daily
                if new_date != last_date:
                    metric_dict['daily'][i] = return_values[i]
                else:
                    metric_dict['daily'][i] += return_values[i]

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling


    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]]for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


######################################################################################
# Day Trading Environment for Dynamic stop loss and take profit with only one Symbol #
######################################################################################
class SmartDayTradeForexDynamicSingleSLTFEnv(gym.Env):
    
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit= 0.015,
        max_vix_fix = 2,
        min_vix_fix = 0.5,
        vix_fix_lag = 22,
        lot_size=0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_take_profit = max_take_profit
        self.max_stop_loss = max_stop_loss
        self.max_vix_fix = max_vix_fix
        self.min_vix_fix = min_vix_fix
        self.vix_fix_lag = vix_fix_lag
        self.lot_size = lot_size
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(11 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.volatality_per_stock = list()
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date']
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * self.stock_dim
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)
    
    def step(self,actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                pass

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}
        
        else:
            #load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day,:]

            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

            #check for number of trades left
            last_date= self.current_date
            new_date = last_day_memory['only date']
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-5,:]
            
            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]

            self.ticker_memory.append(last_day_memory["tic"])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close'])
            
            #check for volatality
            closed_by_volatality = np.zeros(self.stock_dim)
            self.volatality_per_stock = self.get_volatality_per_stock()
            for i in range(self.stock_dim):
                v = self.volatality_per_stock[i]
                if (v <= self.min_vix_fix or v>= self.max_vix_fix) and lots[i] !=0:
                    lots[i] = 0
                    closed_by_volatality[i] = 1
            
            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0   

            #take profit logic
            prev_take_profit = self.state[-7,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0   
                
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(portfolio_return_per_stock)
            self.trades_per_stock_memory.append(self.start_trade_per_stock)           

            # self.reward = self.get_reward_old(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,prev_lots,return_values,new_date,last_date)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array( [[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-11,:] = self.data['open']
            self.state[-10,:] = self.data['close']
            self.state[-9,:] = self.data['high']
            self.state[-8,:] = self.data['low']
            self.state[-7,:] = new_take_profit
            self.state[-6,:] = self.reward_per_stock
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'closed by volatility'] = closed_by_volatality
            self.df.loc[self.day-1,'volatility'] = self.volatality_per_stock
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    
    def get_reward(self,lots,prev_lots,return_values,new_date,last_date):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "daily":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #daily
                if new_date != last_date:
                    metric_dict['daily'][i] = return_values[i]
                else:
                    metric_dict['daily'][i] += return_values[i]

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling

    def get_volatality_per_stock(self):
        self.volatality_per_stock = list()
        df_temp = pd.DataFrame({
            "tic":self.ticker_memory,
            "close":self.close_values_memory,
            "low":self.low_values_memory,
        })

        for tic in self.ticker_list:
            df_tic = df_temp.query(f"tic == '{tic}'")
            max_close = df_tic.loc[-self.vix_fix_lag:,'close'].max()
            low = df_tic.iloc[-1,df_tic.columns.get_loc('low')].item()
            self.volatality_per_stock.append((max_close-low)*100/max_close)
        
        return self.volatality_per_stock

    def get_delayed_reward(self,lots,prev_lots,return_values):
        reward = 0
        for i in range(len(lots)):
            cl = lots[i]
            pl = prev_lots[i]
            if pl != cl and pl!=0:
                reward += self.reward_per_stock[i]
                self.reward_per_stock[i] = 0
            elif (pl==cl) or (pl != cl and pl==0):
                reward += self.reward_per_stock[i] * 0.8
                self.reward_per_stock[i] += return_values[i]
        return reward

    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward

    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "trades_per_stock":self.trades_per_stock_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')

        df_temp = df_temp.groupby(["tic","sec","exchange","trades_per_stock"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic","date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]]for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


####################################
# Daily Trading with single symbol #
####################################
class SmartDailyTradeForexDynamicSLTFSingleSymbolEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit=0.015,
        max_vix_fix = 2,
        min_vix_fix = 0.2,
        vix_fix_lag = 22,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_stop_loss = max_stop_loss
        self.max_take_profit = max_take_profit
        self.max_vix_fix = max_vix_fix
        self.min_vix_fix = min_vix_fix
        self.vix_fix_lag = vix_fix_lag
        self.lot_size = lot_size
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

       # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * self.stock_dim
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                pass

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])
                        
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            self.ticker_memory.append(last_day_memory["tic"])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close'])

            #check for volatality
            closed_by_volatality = np.zeros(self.stock_dim)
            self.volatality_per_stock = self.get_volatality_per_stock()
            for i in range(self.stock_dim):
                v = self.volatality_per_stock[i]
                if (v <= self.min_vix_fix or v>= self.max_vix_fix) and lots[i] !=0:
                    lots[i] = 0
                    closed_by_volatality[i] = 1

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0  

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
        
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(portfolio_return_per_stock)
        
            # self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,prev_lots,return_values)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array( [[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open']
            self.state[-9,:] = self.data['close']
            self.state[-8,:] = self.data['high']
            self.state[-7,:] = self.data['low']
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'volatility'] = self.volatality_per_stock
            self.df.loc[self.day-1,'closed by volatility'] = closed_by_volatality
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,lots,prev_lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling
    
    def get_volatality_per_stock(self):
        self.volatality_per_stock = list()
        df_temp = pd.DataFrame({
            "tic":self.ticker_memory,
            "close":self.close_values_memory,
            "low":self.low_values_memory,
        })

        for tic in self.ticker_list:
            df_tic = df_temp.query(f"tic == '{tic}'")
            max_close = df_tic.loc[-self.vix_fix_lag:,'close'].max()
            low = df_tic.iloc[-1,df_tic.columns.get_loc('low')].item()
            self.volatality_per_stock.append((max_close-low)*100/max_close)
        
        return self.volatality_per_stock
    
    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

######################################################################################
# Day Trading Environment for Dynamic stop loss and take profit with only one Symbol #
######################################################################################
class SmartDayTradeForexStaticSLTFDynamicVolatilitySingleEnv(gym.Env):
    
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        take_profit= 0.015,
        max_vix_fix = 2,
        min_vix_fix = 0.5,
        vix_fix_lag = 22,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.max_vix_fix = max_vix_fix
        self.min_vix_fix = min_vix_fix
        self.vix_fix_lag = vix_fix_lag
        self.lot_size = lot_size
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.volatality_per_stock = list()
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date']
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * self.stock_dim
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)
    
    def step(self,actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                pass

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}
        
        else:
            #load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day,:]

            prev_lots = self.state[-4,:]
            lots,new_max_volatility_per,new_min_volatility_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_max_volatility_per = np.array([abs(x) * self.max_vix_fix for x in new_max_volatility_per])
            new_min_volatility_per = np.array([abs(x) * self.min_vix_fix for x in new_min_volatility_per])

            #check for number of trades left
            last_date= self.current_date
            new_date = last_day_memory['only date']
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-5,:]
            
            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]

            self.ticker_memory.append(last_day_memory["tic"])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close'])
            
            #check for volatality
            closed_by_volatality = np.zeros(self.stock_dim)
            self.volatality_per_stock = self.get_volatality_per_stock()
            for i in range(self.stock_dim):
                v = self.volatality_per_stock[i]
                if (v <= new_min_volatility_per[i] or v>= new_max_volatility_per[i]) and lots[i] !=0:
                    lots[i] = 0
                    closed_by_volatality[i] = 1
            
            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close * (1 - self.stop_loss)
                    elif cl == 0:
                        new_stop_loss[i] = 0   

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close * (1 - self.take_profit)
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close * (1 + self.take_profit)
                    elif cl == 0:
                        new_take_profit[i] = 0   
                
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * lots * 1000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(portfolio_return_per_stock)
            self.trades_per_stock_memory.append(self.start_trade_per_stock)           

            self.reward = self.get_reward(lots,prev_lots,return_values,new_date,last_date)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array( [[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open']
            self.state[-8,:] = self.data['close']
            self.state[-8,:] = self.data['high']
            self.state[-7,:] = self.data['low']
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'closed by volatility'] = closed_by_volatality
            self.df.loc[self.day-1,'volatility'] = self.volatality_per_stock
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    
    def get_reward(self,lots,prev_lots,return_values,new_date,last_date):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "daily":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #daily
                if new_date != last_date:
                    metric_dict['daily'][i] = return_values[i]
                else:
                    metric_dict['daily'][i] += return_values[i]

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] * self.reward_scaling
        
        return sum(self.reward_per_stock) 

    def get_volatality_per_stock(self):
        self.volatality_per_stock = list()
        df_temp = pd.DataFrame({
            "tic":self.ticker_memory,
            "close":self.close_values_memory,
            "low":self.low_values_memory,
        })

        for tic in self.ticker_list:
            df_tic = df_temp.query(f"tic == '{tic}'")
            max_close = df_tic.loc[-self.vix_fix_lag:,'close'].max()
            low = df_tic.iloc[-1,df_tic.columns.get_loc('low')].item()
            self.volatality_per_stock.append((max_close-low)*100/max_close)
        
        return self.volatality_per_stock

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]]for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


####################################
# Daily Trading with single symbol #
####################################
class SmartDailyTradeForexStaticSLTFDynamicVolatilitySingleEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        stop_loss = 0.015,
        take_profit=0.015,
        max_vix_fix = 2,
        min_vix_fix = 0.2,
        vix_fix_lag = 22,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_vix_fix = max_vix_fix
        self.min_vix_fix = min_vix_fix
        self.vix_fix_lag = vix_fix_lag
        self.lot_size = lot_size
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

       # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.stocks_in_portfolio = [0] * self.stock_dim
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                pass

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            prev_lots = self.state[-4,:]
            lots,new_max_volatility_per,new_min_volatility_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_max_volatility_per = np.array([abs(x) * self.max_vix_fix for x in new_max_volatility_per])
            new_min_volatility_per = np.array([abs(x) * self.min_vix_fix for x in new_min_volatility_per])

            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            self.ticker_memory.append(last_day_memory["tic"])
            self.sec_types_memory.append(last_day_memory['sec'])
            self.exchanges_memory.append(last_day_memory['exchange'])
            self.date_memory_per_stock.append(last_day_memory['date'])
            self.low_values_memory.append(last_day_memory['low'])
            self.close_values_memory.append(last_day_memory['close'])

            #check for volatality
            closed_by_volatality = np.zeros(self.stock_dim)
            self.volatality_per_stock = self.get_volatality_per_stock()
            for i in range(self.stock_dim):
                v = self.volatality_per_stock[i]
                if (v <= new_min_volatility_per[i] or v>= new_max_volatility_per[i]) and lots[i] !=0:
                    lots[i] = 0
                    closed_by_volatality[i] = 1

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close * (1 + self.stop_loss)
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close * (1 - self.stop_loss)
                    elif cl == 0:
                        new_stop_loss[i] = 0  

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close * (1 - self.take_profit)
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close * (1 + self.take_profit)
                    elif cl == 0:
                        new_take_profit[i] = 0
        
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close
            return_values = (self.data.close - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data['date'])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.append(portfolio_return_per_stock)
        
            # self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,prev_lots,return_values)

            #update state
            self.state[:len(self.tech_indicator_list),:] = np.array( [[self.data[tech]] for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open']
            self.state[-9,:] = self.data['close']
            self.state[-8,:] = self.data['high']
            self.state[-7,:] = self.data['low']
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'volatility'] = self.volatality_per_stock
            self.df.loc[self.day-1,'closed by volatility'] = closed_by_volatality
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,lots,prev_lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim)
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling
    
    def get_volatality_per_stock(self):
        self.volatality_per_stock = list()
        df_temp = pd.DataFrame({
            "tic":self.ticker_memory,
            "close":self.close_values_memory,
            "low":self.low_values_memory,
        })

        for tic in self.ticker_list:
            df_tic = df_temp.query(f"tic == '{tic}'")
            max_close = df_tic.loc[-self.vix_fix_lag:,'close'].max()
            low = df_tic.iloc[-1,df_tic.columns.get_loc('low')].item()
            self.volatality_per_stock.append((max_close-low)*100/max_close)
        
        return self.volatality_per_stock
    
    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([[self.data[tech]] for tech in self.tech_indicator_list],
            self.data['open'],
            self.data['close'],
            self.data['high'],
            self.data['low'],
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data['date']]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = [self.data.tic]
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs



#########################################################################################
# Day Trading Environment for Dynamic stop loss and take profit with only long or short #
#########################################################################################
class SmartDayTradeForexDynamicSLTFLongOrShortEnv(gym.Env):
    
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        trades_per_stock= [],
        ticker_col_name="tic",
        long_or_short= "long",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit= 0.015,
        lot_size = 0.1,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.long_or_short = long_or_short
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_take_profit = max_take_profit
        self.max_stop_loss = max_stop_loss
        self.lot_size = lot_size
        self.trades_per_stock = trades_per_stock
        self.start_trade_per_stock = trades_per_stock
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(11 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))
        
        self.current_date = self.data['only date'].values[0]
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.trades_per_stock_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)
    
    def step(self,actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]
                self.new_trades_per_stock = df_metrics['trades_per_stock'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}
        
        else:
            #load next state
            last_day_memory = self.data
            self.day += 1
            self.data = self.df.loc[self.day,:]

            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            if self.long_or_short == "long":
                lots = np.array([self.lot_size if x >= 0.5 else 0 for x in lots])
            elif self.long_or_short == "short":
                lots = np.array([-self.lot_size if x >= 0.5 else 0 for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])

            #check for number of trades left
            new_date = last_day_memory['only date'].values[0]
            if new_date != self.current_date:
                prev_number_of_trades = self.trades_per_stock
                self.current_date = new_date
            else:
                prev_number_of_trades = self.state[-5,:]
            
            new_number_of_trades = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                if cl != pl and prev_number_of_trades[i]==0:
                    lots[i] = pl
                elif cl==pl and prev_number_of_trades[i]==0:
                    lots[i] = cl
                elif cl !=pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = (prev_number_of_trades[i]-1)
                elif cl==pl and prev_number_of_trades[i]>0:
                    new_number_of_trades[i] = prev_number_of_trades[i]
            
            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0   

            #take profit logic
            prev_take_profit = self.state[-7,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
            
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(portfolio_return_per_stock.ravel().tolist())
            self.ticker_memory.extend(self.data["tic"].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.trades_per_stock_memory.extend(self.start_trade_per_stock)
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            # self.reward = self.get_reward_old(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-11,:] = self.data['open'].values
            self.state[-10,:] = self.data['close'].values
            self.state[-9,:] = self.data['high'].values
            self.state[-8,:] = self.data['low'].values
            self.state[-7,:] = new_take_profit
            self.state[-6,:] = self.reward_per_stock
            self.state[-5,:] = new_number_of_trades
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            self.df.loc[self.day-1,'number of trades left'] = new_number_of_trades
            
        return self.state, self.reward, self.terminal, {}
    
    def get_delayed_reward(self,lots,prev_lots,return_values):
        reward = 0
        for i in range(len(lots)):
            cl = lots[i]
            pl = prev_lots[i]
            if pl != cl and pl!=0:
                reward += self.reward_per_stock[i]
                self.reward_per_stock[i] = 0
            elif (pl==cl) or (pl != cl and pl==0):
                # reward += self.reward_per_stock[i] * 0.5 + return_values[i] * 0.5
                reward += self.reward_per_stock[i] * 0.8
                # reward += return_values[i]
                self.reward_per_stock[i] += return_values[i]
        return reward
    
    def get_reward(self,lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling

    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward

    def get_reward_per_stock(self):

        metrics_list = ['sortino_1day','sortino_4hour','sortino_1hour','sortino_30min','sortino_15min',
                        'vix_fix_1day','vix_fix_4hour','vix_fix_1hour','vix_fix_30min','vix_fix_15min',
                        'calamar_1day','calamar_4hour','calamar_1hour','calamar_30min','calamar_15min',
                        'sharpe_1day','sharpe_4hour','sharpe_1hour','sharpe_30min','sharpe_15min']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "trades_per_stock":self.trades_per_stock_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_vix_fix(df_temp,86_400,'vix_fix_1day')
        df_temp = self.add_sharpe(df_temp,86_400,'sharpe_1day')
        df_temp = self.add_sortino(df_temp,86_400,'sortino_1day')
        df_temp = self.add_clamar(df_temp,86_400,'calamar_1day')
    
        df_temp = self.add_vix_fix(df_temp,14_400,'vix_fix_4hour')
        df_temp = self.add_sharpe(df_temp,14_400,'sharpe_4hour')
        df_temp = self.add_sortino(df_temp,14_400,'sortino_4hour')
        df_temp = self.add_clamar(df_temp,14_400,'calamar_4hour')
    
        df_temp = self.add_vix_fix(df_temp,3600,'vix_fix_1hour')
        df_temp = self.add_sharpe(df_temp,3600,'sharpe_1hour')
        df_temp = self.add_sortino(df_temp,3600,'sortino_1hour')
        df_temp = self.add_clamar(df_temp,3600,'calamar_1hour')
    
        df_temp = self.add_vix_fix(df_temp,1800,'vix_fix_30min')
        df_temp = self.add_sharpe(df_temp,1800,'sharpe_30min')
        df_temp = self.add_sortino(df_temp,1800,'sortino_30min')
        df_temp = self.add_clamar(df_temp,1800,'calamar_30min')
    
        df_temp = self.add_vix_fix(df_temp,900,'vix_fix_15min')
        df_temp = self.add_sharpe(df_temp,900,'sharpe_15min')
        df_temp = self.add_sortino(df_temp,900,'sortino_15min')
        df_temp = self.add_clamar(df_temp,900,'calamar_15min')

        df_temp = df_temp.groupby(["tic","sec","exchange","trades_per_stock"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    def add_sharpe(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic","date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.array(self.trades_per_stock),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.trades_per_stock_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


#########################################################################################
# Day Trading Environment for Dynamic stop loss and take profit with only short or long #
#########################################################################################
class SmartDailyTradeForexDynamicSLTFLongOrShortEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit=0.015,
        lot_size = 0.1,
        long_or_short= "long",
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_stop_loss = max_stop_loss
        self.max_take_profit = max_take_profit
        self.long_or_short = long_or_short
        self.lot_size = lot_size
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

       # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            if self.long_or_short == "long":
                lots = np.array([self.lot_size if x >= 0.5 else 0 for x in lots])
            elif self.long_or_short == "short":
                lots = np.array([-self.lot_size if x >= 0.5 else 0 for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])
                        
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0  

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
                    
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(portfolio_return_per_stock.ravel().tolist())
            self.ticker_memory.extend(self.data["tic"].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            # self.reward = self.get_reward(begin_total_asset,end_total_asset)
            # self.reward = self.get_delayed_reward(lots,prev_lots,return_values)
            self.reward = self.get_reward(lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open'].values
            self.state[-9,:] = self.data['close'].values
            self.state[-8,:] = self.data['high'].values
            self.state[-7,:] = self.data['low'].values
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling
    
    def get_reward_old(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric

        #cagr calculation
        cagr = (end_total_asset/begin_total_asset) - 1
        reward_metrics['cagr'] = cagr / 24

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 100

        #drawdown 
        drawdown = df_temp['daily_return'].diff(1).sum()
        reward_metrics['drawndown'] = -drawdown
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score
    
        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
                    
        self.reward *= self.reward_scaling
        return self.reward
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open'].values,
            self.data['close'].values,
            self.data['high'].values,
            self.data['low'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

######################################################################
# Day Trading Environment Diff for Dynamic stop loss and take profit #
######################################################################
class SmartDailyTradeForexDynamicSLTFDiffEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        sec_types = [],
        exchanges = [],
        lot_size = 0.1,
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        max_stop_loss = 0.015,
        max_take_profit=0.015,
        epochs = 1,
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.max_stop_loss = max_stop_loss
        self.max_take_profit = max_take_profit
        self.lot_size = lot_size
        self.tech_indicator_list = tech_indicator_list
        self.epochs = epochs
        self.epochs_cnt = 0

       # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=-1,high=1,shape=(3*self.stock_dim,))
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(10 + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open_diff'].values,
            self.data['close_diff'].values,
            self.data['high_diff'].values,
            self.data['low_diff'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            ))

        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.reward_memory = list()

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:
            self.epochs_cnt += 1           
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            if self.epochs_cnt == self.epochs:
                df_metrics = self.get_reward_per_stock()
                top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
                self.ticker_list = df_metrics['tic'].tolist()[:top_n]
                self.sec_types = df_metrics['sec'].tolist()[:top_n]
                self.exchanges = df_metrics['exchange'].tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            prev_lots = self.state[-4,:]
            lots,new_stop_loss_per,new_take_profit_per = actions[:self.stock_dim],actions[self.stock_dim:2*self.stock_dim],actions[:-self.stock_dim]
            lots = np.array([self.lot_size * int(x) for x in lots])
            new_stop_loss_per = np.array([self.max_stop_loss * abs(x) for x in new_stop_loss_per])
            new_take_profit_per = np.array([self.max_take_profit * abs(x) for x in new_take_profit_per])
                        
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]

            #stop loss logic
            orignal_lots = lots
            prev_stop_loss = self.state[-1,:]
            new_stop_loss = np.zeros(self.stock_dim)
            closed_by_stop_loss = np.zeros(self.stock_dim)
            for i in range(len(prev_lots)):
                cl = lots[i]
                pl = prev_lots[i]
                
                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] >= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] <= prev_stop_loss[i]:
                            lots[i] = 0
                            closed_by_stop_loss[i] = 1
                            new_stop_loss[i] = 0
                        else:
                            new_stop_loss[i] = prev_stop_loss[i] 
                    elif cl == 0:
                        new_stop_loss[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 + new_stop_loss_per[i])
                    if cl > 0:
                        new_stop_loss[i] = last_day_memory.close.values[i] * (1 - new_stop_loss_per[i])
                    elif cl == 0:
                        new_stop_loss[i] = 0  

            #take profit logic
            prev_take_profit = self.state[-6,:]
            new_take_profit = np.zeros(self.stock_dim)
            closed_by_take_profit = np.zeros(self.stock_dim)
            for i in range(len(prev_take_profit)):
                cl = lots[i]
                pl = prev_lots[i]

                if pl == cl:
                    if cl < 0:
                        if last_day_memory.close.values[i] <= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i]
                    elif cl > 0:
                        if last_day_memory.close.values[i] >= prev_take_profit[i]:
                            lots[i] = 0
                            closed_by_take_profit[i] = 1
                            new_take_profit[i] = 0
                        else:
                            new_take_profit[i] = prev_take_profit[i] 
                    elif cl == 0:
                        new_take_profit[i] = 0

                elif pl != cl:
                    if cl < 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 - new_take_profit_per[i])
                    if cl > 0:
                        new_take_profit[i] = last_day_memory.close.values[i] * (1 + new_take_profit_per[i])
                    elif cl == 0:
                        new_take_profit[i] = 0
                    
            self.actions_memory.append(lots)

            #calculate return
            close_values = last_day_memory.close.values
            return_values = (self.data.close.values - close_values) * lots * 10000
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            adjust_stock = [abs(x-y) for x,y in zip(lots,self.stocks_in_portfolio)]
            total_transaction_cost_per_stock = np.array([self.transaction_cost if x!=0 else 0 for x in adjust_stock])
            total_transaction_cost = sum(total_transaction_cost_per_stock)
            self.stocks_in_portfolio = lots

            # update portfolio value
            portfolio_return_per_stock = return_values - total_transaction_cost_per_stock + self.portfolio_value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = (self.portfolio_value + portfolio_return - total_transaction_cost)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            percentage_return = (end_total_asset/begin_total_asset -1)
            self.portfolio_return_memory.append(percentage_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(portfolio_return_per_stock.ravel().tolist())
            self.ticker_memory.extend(self.data["tic"].values.tolist())
            self.sec_types_memory.extend(self.data['sec'].values.tolist())
            self.exchanges_memory.extend(self.data['exchange'].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(lots,prev_lots,return_values)

            #update state
            self.covs = self.data["cov_list"].values[0] 
            self.state[:len(self.tech_indicator_list),:] = np.array( [self.data[tech].values.tolist() for tech in self.tech_indicator_list])
            self.state[-10,:] = self.data['open'].values
            self.state[-9,:] = self.data['close'].values
            self.state[-8,:] = self.data['high'].values
            self.state[-7,:] = self.data['low'].values
            self.state[-6,:] = new_take_profit
            self.state[-5,:] = self.reward_per_stock
            self.state[-4,:] = lots
            self.state[-3,:] = return_values
            self.state[-2,:] = (return_values - total_transaction_cost_per_stock)
            self.state[-1,:] = new_stop_loss

            self.reward_memory.append(self.reward)

            self.df.loc[self.day-1,'reward'] = self.reward_per_stock
            self.df.loc[self.day-1,'lots'] = lots
            self.df.loc[self.day-1,'return'] = return_values
            self.df.loc[self.day-1,'return with cost'] = return_values - total_transaction_cost_per_stock
            self.df.loc[self.day-1,'portfolio value'] = new_portfolio_value
            self.df.loc[self.day-1,'orignal lots'] = orignal_lots
            self.df.loc[self.day-1,'stop loss'] = new_stop_loss
            self.df.loc[self.day-1,'take profit'] = new_take_profit
            self.df.loc[self.day-1,'closed by stop loss'] = closed_by_stop_loss
            self.df.loc[self.day-1,'closed by take profit'] = closed_by_take_profit
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward(self,lots,prev_lots,return_values):
        self.reward = 0
        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "account_value":self.portfolio_return_per_stock_memory})
        
        metric_dict = {
            "asset":np.zeros(self.stock_dim),
            "sortino":np.zeros(self.stock_dim),
            "sharpe":np.zeros(self.stock_dim),
            "cagr":np.zeros(self.stock_dim),
            "unrealized":np.zeros(self.stock_dim),
            "calamar":np.zeros(self.stock_dim),
            "skew":np.zeros(self.stock_dim),
            "kurtosis":np.zeros(self.stock_dim),
        }
        self.reward_per_stock = np.zeros(self.stock_dim)

        for i,tic in enumerate(self.ticker_list):
            df_tic = df_temp.loc[df_temp['tic'] == tic,:].copy()
            df_tic['daily_return'] = df_tic.loc[:,'account_value'].pct_change(1)
            df_tic['daily_return'].fillna(0,inplace=True)
            df_tic.fillna(0,inplace=True)

            if lots[i] != 0:
                #asset
                metric_dict["asset"][i] = return_values[i]

                #sortino
                temp = df_tic.query("daily_return <= 0")['daily_return']
                sortino = (252 ** 0.5) * temp.mean()/ (temp.std() + 1e-8)
                sortino = 0 if math.isnan(sortino) else sortino
                metric_dict["sortino"][i] = sortino

                #sharpe
                temp = df_tic['daily_return']
                sharpe = (252 ** 0.5) * temp.mean()/(temp.std()+1e-8)
                sharpe = 0 if math.isnan(sharpe) else sharpe
                metric_dict["sharpe"][i] = sharpe

                #unrealized
                cl = lots[i]
                pl = prev_lots[i]
                if pl != cl and pl!=0:
                    metric_dict['unrealized'][i] = return_values[i]
                elif (pl==cl) or (pl != cl and pl==0):
                    metric_dict['unrealized'] += return_values[i]

                #cagr
                final_value = df_tic['account_value'].values[-1]
                initial_value = df_tic['account_value'].values[0]
                cagr = (final_value/initial_value)**(252/len(df_tic)) - 1
                metric_dict['cagr'][i] = cagr * 100

                #calamar
                avg_return = df_tic['daily_return'].mean()
                max_drawdown = df_tic['daily_return'].diff(1).min()
                calamar = avg_return/ (max_drawdown + 1e-8)
                calamar = 0 if math.isnan(calamar) else calamar
                metric_dict["calamar"][i] = calamar*100

                #skew
                skew_score = skew(df_tic['daily_return'])
                metric_dict["skew"][i] = skew_score

                #kurtosis
                kurtosis_score = kurtosis(df_tic['daily_return'])
                metric_dict["kurtosis"][i] = kurtosis_score
        
        for metric in self.target_metrics:
            self.reward_per_stock += metric_dict[metric] 
        
        return sum(self.reward_per_stock) * self.reward_scaling
    
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "sec":self.sec_types_memory,
                                "exchange":self.exchanges_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby(["tic","sec","exchange"])[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False).reset_index()
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = (days ** 0.5) * temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = (days ** 0.5) * temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.reward_per_stock = np.zeros(self.stock_dim)
        self.state = np.row_stack(
            ([self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            self.data['open_diff'].values,
            self.data['close_diff'].values,
            self.data['high_diff'].values,
            self.data['low_diff'].values,
            np.zeros(self.stock_dim),
            self.reward_per_stock,
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim),
            np.zeros(self.stock_dim)
            ))
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.reward_memory = list()
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.sec_types_memory = list()
        self.exchanges_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        df_account_value = pd.DataFrame(
              {"date": date_list, "account_value": self.asset_memory}
        )
        df_account_value['daily_return'] = df_account_value['account_value'].pct_change(1)
        df_account_value['daily_return'].fillna(0,inplace=True)
        df_account_value.drop('account_value',axis=1,inplace=True)
        return df_account_value

    def save_action_memory(self):
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs


###################################
# Multi-stock trading environment #
###################################

class StockTradingEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self, 
                df, 
                hmax,                
                initial_amount,
                buy_cost_pct,
                sell_cost_pct,
                reward_scaling,
                tech_indicator_list = [],
                tic_col_name="tic",
                target_metrics=['cagr','sortino','calamar'],
                turbulence_threshold=None,
                make_plots = False, 
                print_verbosity = 10,
                day = 0, 
                initial=True,
                previous_state=[],
                model_name = '',
                mode='',
                iteration=''):
        self.day = day
        self.df = df
        self.stock_dim = self.df[tic_col_name].nunique()
        self.target_metrics = target_metrics
        self.all_metrics = ["asset", "cagr", "sortino", "calamar", "skew", "kurtosis" ]
        # assert self.target_metrics in self.all_metrics,f"wrong metrics available options are:{self.all_metrics}"

        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.reward_scaling = reward_scaling
        self.action_space = self.stock_dim
        self.tech_indicator_list = tech_indicator_list
        self.state_space =  1 + 2 * self.stock_dim + len(self.tech_indicator_list)*self.stock_dim
        self.action_space = spaces.Box(low = -1, high = 1,shape = (self.action_space,)) 
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape = (self.state_space,))

        self.data = self.df.loc[self.day,:]
        self.terminal = False     
        self.make_plots = make_plots
        self.print_verbosity = print_verbosity
        self.turbulence_threshold = turbulence_threshold
        self.initial = initial
        self.previous_state = previous_state
        self.model_name=model_name
        self.mode=mode 
        self.iteration=iteration
        # initalize state
        self.state = self._initiate_state()
        
        # initialize reward
        self.reward = 0
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0
        # memorize all the total balance change
        self.asset_memory = [self.initial_amount]
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        #self.reset()
        self._seed()
        


    def _sell_stock(self, index, action):
        def _do_sell_normal():
            if self.state[index+1]>0: 
                # Sell only if the price is > 0 (no missing data in this particular date)
                # perform sell action based on the sign of the action
                if self.state[index+self.stock_dim+1] > 0:
                    # Sell only if current asset is > 0
                    sell_num_shares = min(abs(action),self.state[index+self.stock_dim+1])
                    sell_amount = self.state[index+1] * sell_num_shares * (1- self.sell_cost_pct)
                    #update balance
                    self.state[0] += sell_amount

                    self.state[index+self.stock_dim+1] -= sell_num_shares
                    self.cost +=self.state[index+1] * sell_num_shares * self.sell_cost_pct
                    self.trades+=1
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = 0

            return sell_num_shares
            
        # perform sell action based on the sign of the action
        if self.turbulence_threshold is not None:
            if self.turbulence>=self.turbulence_threshold:
                if self.state[index+1]>0: 
                    # Sell only if the price is > 0 (no missing data in this particular date)
                    # if turbulence goes over threshold, just clear out all positions 
                    if self.state[index+self.stock_dim+1] > 0:
                        # Sell only if current asset is > 0
                        sell_num_shares = self.state[index+self.stock_dim+1]
                        sell_amount = self.state[index+1]*sell_num_shares* (1- self.sell_cost_pct)
                        #update balance
                        self.state[0] += sell_amount
                        self.state[index+self.stock_dim+1] =0
                        self.cost += self.state[index+1]*self.state[index+self.stock_dim+1]* \
                                    self.sell_cost_pct
                        self.trades+=1
                    else:
                        sell_num_shares = 0
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = _do_sell_normal()
        else:
            sell_num_shares = _do_sell_normal()

        return sell_num_shares

    
    def _buy_stock(self, index, action):

        def _do_buy():
            if self.state[index+1]>0: 
                #Buy only if the price is > 0 (no missing data in this particular date)       
                available_amount = self.state[0] // self.state[index+1]
                # print('available_amount:{}'.format(available_amount))
                
                #update balance
                buy_num_shares = min(available_amount, action)
                buy_amount = self.state[index+1] * buy_num_shares * (1+ self.buy_cost_pct)
                self.state[0] -= buy_amount

                self.state[index+self.stock_dim+1] += buy_num_shares
                
                self.cost+=self.state[index+1] * buy_num_shares * self.buy_cost_pct
                self.trades+=1
            else:
                buy_num_shares = 0

            return buy_num_shares

        # perform buy action based on the sign of the action
        if self.turbulence_threshold is None:
            buy_num_shares = _do_buy()
        else:
            if self.turbulence< self.turbulence_threshold:
                buy_num_shares = _do_buy()
            else:
                buy_num_shares = 0
                pass

        return buy_num_shares

    def _make_plot(self):
        plt.plot(self.asset_memory,'r')
        plt.savefig('results/account_value_trade_{}.png'.format(self.episode))
        plt.close()

    def step(self, actions):
        self.terminal = self.day >= len(self.df.index.unique())-1
        if self.terminal:
            # print(f"Episode: {self.episode}")
            # if self.make_plots:
            #     self._make_plot()            
            end_total_asset = self.state[0]+ \
                sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            df_total_value = pd.DataFrame(self.asset_memory)
            tot_reward = self.state[0]+sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))- self.initial_amount 
            df_total_value.columns = ['account_value']
            df_total_value['date'] = self.date_memory
            df_total_value['daily_return']=df_total_value['account_value'].pct_change(1)
            sharpe = (252**0.5)*df_total_value['daily_return'].mean()/ \
                   ( df_total_value['daily_return'].std() + 1e-8)
            df_rewards = pd.DataFrame(self.rewards_memory)
            df_rewards.columns = ['account_rewards']
            df_rewards['date'] = self.date_memory[:-1]
            if self.episode % self.print_verbosity == 0:
                print(f"day: {self.day}, episode: {self.episode}")
                print(f"begin_total_asset: {self.asset_memory[0]:0.2f}")
                print(f"end_total_asset: {end_total_asset:0.2f}")
                print(f"total_reward: {tot_reward:0.2f}")
                print(f"total_cost: {self.cost:0.2f}")
                print(f"total_trades: {self.trades}")
                if df_total_value['daily_return'].std() != 0:
                    print(f"Sharpe: {sharpe:0.3f}")
                print("=================================")

            if (self.model_name!='') and (self.mode!=''):
                df_actions = self.save_action_memory()
                df_actions.to_csv('results/actions_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration))
                df_total_value.to_csv('results/account_value_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration),index=False)
                df_rewards.to_csv('results/account_rewards_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration),index=False)
                plt.plot(self.asset_memory,'r')
                plt.savefig('results/account_value_{}_{}_{}.png'.format(self.mode,self.model_name, self.iteration),index=False)
                plt.close()

            return self.state, self.reward, self.terminal, {}

        else:

            actions = actions * self.hmax #actions initially is scaled between 0 to 1
            actions = (actions.astype(int)) #convert into integer because we can't by fraction of shares
            if self.turbulence_threshold is not None:
                if self.turbulence>=self.turbulence_threshold:
                    actions=np.array([-self.hmax]*self.stock_dim)
            begin_total_asset = self.state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            #print("begin_total_asset:{}".format(begin_total_asset))
            
            argsort_actions = np.argsort(actions)
            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

            for index in sell_index:
                # print(f"Num shares before: {self.state[index+self.stock_dim+1]}")
                # print(f'take sell action before : {actions[index]}')
                actions[index] = self._sell_stock(index, actions[index]) * (-1)
                # print(f'take sell action after : {actions[index]}')
                # print(f"Num shares after: {self.state[index+self.stock_dim+1]}")

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))
                actions[index] = self._buy_stock(index, actions[index])

            self.actions_memory.append(actions)

            self.day += 1
            self.data = self.df.loc[self.day,:]    
            if self.turbulence_threshold is not None:     
                self.turbulence = self.data['turbulence'].values[0]
            self.state =  self._update_state()
                           
            end_total_asset = self.state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            self.asset_memory.append(end_total_asset)
            self.date_memory.append(self._get_date())

            reward_metrics = {}
            self.reward = 0

            #asset metric calculation
            asset_metric = end_total_asset - begin_total_asset 
            reward_metrics['asset'] = asset_metric

            #cagr calculation
            years = self.day/252
            cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
            reward_metrics['cagr'] = cagr

            #daily return
            df_temp = pd.DataFrame(self.asset_memory)
            df_temp.columns = ['account_value']
            df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
            df_temp.fillna(0,inplace=True)

            #sortino calculation
            sortino = np.mean((df_temp['daily_return'] - 0.1)/ \
                (df_temp.query("daily_return <= 0")['daily_return'].std()+1e-8))
            sortino = 0 if math.isnan(sortino) else sortino
            reward_metrics['sortino'] = sortino

            #sharpe calculation
            sharpe = np.mean((df_temp['daily_return'] - 0.1)/ \
                (df_temp['daily_return'].std()+1e-8))
            sharpe = 0 if math.isnan(sharpe) else sharpe
            reward_metrics['sharpe'] = sharpe
            
            #calamar calculation
            avg_return = df_temp['daily_return'].mean()
            max_drawdown = df_temp['daily_return'].diff(1).min()
            calamar = avg_return/ (max_drawdown + 1e-8)
            calamar = 0 if math.isnan(calamar) else calamar
            reward_metrics['calamar'] = calamar
            
            #skew
            skew_score = skew(df_temp['daily_return'])
            reward_metrics['skew'] = skew_score
            
            kurtosis_score = kurtosis(df_temp['daily_return'])
            reward_metrics['kurtosis'] = kurtosis_score

            for metric in self.target_metrics:
                self.reward += reward_metrics[metric]
                
            self.rewards_memory.append(self.reward)
            self.reward *= self.reward_scaling

        return self.state, self.reward, self.terminal, {}

    def reset(self):  
        #initiate state
        self.state = self._initiate_state()
        
        if self.initial:
            self.asset_memory = [self.initial_amount]
        else:
            previous_total_asset = self.previous_state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            self.asset_memory = [previous_total_asset]

        self.day = 0
        self.data = self.df.loc[self.day,:]
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.terminal = False 
        # self.iteration=self.iteration
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        
        self.episode+=1

        return self.state
    
    def render(self, mode='human',close=False):
        return self.state

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = [self.initial_amount] + \
                         self.data.close.values.tolist() + \
                         [0]*self.stock_dim  + \
                         sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
            else:
                # for single stock
                state = [self.initial_amount] + \
                        [self.data.close] + \
                        [0]*self.stock_dim  + \
                        sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
        else:
            #Using Previous State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = [self.previous_state[0]] + \
                         self.data.close.values.tolist() + \
                         self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]  + \
                         sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
            else:
                # for single stock
                state = [self.previous_state[0]] + \
                        [self.data.close] + \
                        self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]  + \
                        sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
        return state

    def _update_state(self):
        if len(self.df.tic.unique())>1:
            # for multiple stock
            state =  [self.state[0]] + \
                      self.data.close.values.tolist() + \
                      list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                      sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])

        else:
            # for single stock
            state =  [self.state[0]] + \
                     [self.data.close] + \
                     list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                     sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
                          
        return state

    def _get_date(self):
        if len(self.df.tic.unique())>1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    def save_asset_memory(self):
        date_list = self.date_memory
        asset_list = self.asset_memory
        #print(len(date_list))
        #print(len(asset_list))
        df_account_value = pd.DataFrame({'date':date_list,'account_value':asset_list})
        return df_account_value

    def save_action_memory(self):
        if len(self.df.tic.unique())>1:
            # date and close price length must match actions length
            date_list = self.date_memory[:-1]
            df_date = pd.DataFrame(date_list)
            df_date.columns = ['date']
            
            action_list = self.actions_memory
            df_actions = pd.DataFrame(action_list)
            df_actions.columns = self.data.tic.values
            df_actions.index = df_date.date
            #df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            date_list = self.date_memory[:-1]
            action_list = self.actions_memory
            df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs