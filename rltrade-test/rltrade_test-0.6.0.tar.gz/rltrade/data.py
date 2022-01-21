import time
import threading
import numpy as np
import pandas as pd
from pytz import timezone
from scipy.stats import norm
from datetime import datetime
from stockstats import StockDataFrame as Sdf
from rltrade.ibkr import IBapi, api_connect, contfuture_contract,stock_contract,future_contract


def load_csv(path):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

class IBKRDownloader:

    def __init__(self,
        start_date:str,end_date:str,
        ticker_list:list,
        sec_types:list,
        exchanges:list,
        time_frame='1 hour',
        start_time="09:30:00",
        end_time="15:59:00",
        demo=True):
        self.start_date = start_date.replace('-','')
        self.end_date = end_date.replace('-','')
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.time_frame = time_frame
        self.start_date_dt = datetime.strptime(self.start_date,"%Y%m%d")
        self.end_date_dt = datetime.strptime(self.end_date,"%Y%m%d")
        self.date_delta =  (self.end_date_dt-self.start_date_dt)
        self.days = self.date_delta.days
        self.years = int(self.days / 365)
        self.dates = pd.date_range(start=self.start_date_dt,end =self.end_date_dt,freq='2D')
        self.dates = [''.join(str(x).split('-'))[:8] for x in self.dates]
        self.start_time = start_time
        self.end_time = end_time
        self.demo = demo
        self.count = 0
            
    def download_daily_data(self,app:IBapi,id:int,ticker:str,sectype:str,exchange:str):
        def run_loop():
            app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        duration = f"{self.years} Y" if self.years > 0 else f"{self.days} D"
        if sectype == 'STK':
            cnt = stock_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'FUT':
            cnt = future_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'CONTFUT':
            cnt = contfuture_contract(ticker,secType=sectype,exchange=exchange)
        app.reqHistoricalData(id,cnt,"", duration,self.time_frame,'ADJUSTED_LAST',1,2,False,[])
        app.nextorderId += 1
        return app

    def fetch_daily_data(self):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            print("Trying to download: ",tic)
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            try:
                temp_df = self.download_daily_data(app,i,tic,sec,exchange)
                time.sleep(10)
                temp_df = app.get_df()
                temp_df['tic'] = tic
                temp_df['sec'] = sec
                temp_df['exchange'] = exchange
                app.reset_df()
                df = df.append(temp_df)
            except:
                print("Not able to download",tic)
                not_downloaded.append(tic)
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df = df.reset_index()
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d')
        df["day"] = df["date"].dt.dayofweek
        df['only date'] = df['date'].dt.date
        df["date"] = df["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df['market closed'] = False
        return df
    
    def download_data(self,app:IBapi,id:int,ticker:str,sectype:str,exchange:str,end:str):
        def run_loop():
            app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        if sectype == 'STK':
            cnt = stock_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'FUT':
            cnt = future_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'CONTFUT':
            cnt = contfuture_contract(ticker,secType=sectype,exchange=exchange)

        app.reqHistoricalData(id,cnt ,end+" "+ self.end_time + " est","2 D",self.time_frame,'TRADES',1,1,False,[])
        app.nextorderId += 1
        return app
    
    def fetch_data(self):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            print("Trying to download: ",tic)
            sec = self.sec_types[i]
            exchange  = self.exchanges[i]
            for end in self.dates[1:]:
                self.count += 1
                try:
                    app = self.download_data(app,self.count,tic,sec,exchange,end)
                    time.sleep(10)
                    temp_df = app.get_df()
                    temp_df['tic'] = tic
                    temp_df['sec'] = sec
                    temp_df['exchange'] = exchange
                    app.reset_df()
                    df = df.append(temp_df)
                except:
                    print("Not able to download",tic)
                    not_downloaded.append(tic)
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d  %H:%M:%S')
        df['time'] = df['date'].dt.time
        df['only date'] = df['date'].dt.date
        df = df[(df['time']>=datetime.strptime(self.start_time,"%H:%M:%S").time()) & 
                (df['time']<=datetime.strptime(self.end_time,"%H:%M:%S").time())]
        
        df['market closed'] = df.groupby('only date')['time'].transform(lambda x:(x==x.max()))
        df['market closed'] = df['market closed'] | df['market closed'].shift(-1).fillna(True)
        return df
    
    def download_todays_data(self,app:IBapi,id:int,ticker:str,sectype:str,exchange:str,end:str,duration:str):
        def run_loop():
            app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        if sectype == 'STK':
            cnt = stock_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'FUT':
            cnt = future_contract(ticker,secType=sectype,exchange=exchange)
        elif sectype == 'CONTFUT':
            cnt = contfuture_contract(ticker,secType=sectype,exchange=exchange)

        app.reqHistoricalData(id,cnt ,"", duration,self.time_frame,'TRADES',1,1,True,[])
        time.sleep(5)
        app.nextorderId += 1
        return app
    
    def fetch_todays_data(self,end,duration):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            self.count +=1
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            try:
                temp_df = self.download_todays_data(app,self.count,tic,sec,exchange,end,duration)
                time.sleep(1)
                temp_df = app.get_df()
                temp_df['tic'] = tic
                temp_df['sec'] = sec
                temp_df['exchange'] = exchange
                app.reset_df()
                df = df.append(temp_df)
            except:
                print("Not able to download",tic)
                not_downloaded.append(tic)   
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d  %H:%M:%S')
        df['time'] = df['date'].dt.time
        df['only date'] = df['date'].dt.date
        df = df[(df['time']>=datetime.strptime(self.start_time,"%H:%M:%S").time()) & 
                (df['time']<=datetime.strptime(self.end_time,"%H:%M:%S").time())]
        df['market closed'] = False
        return df

class OandaDownloader:
    def __init__(self,
    account,
    time_frame:str,
    start_date:str,
    end_date:str,
    ticker_list:list,
    start_time="09:30:00",
    end_time="15:59:00",
    ):
        self.account = account
        self.time_frame = time_frame
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.ticker_list = ticker_list
        tz = timezone('EST')
        self.start_date_st = tz.localize(datetime.strptime(self.start_date+self.start_time,"%Y-%m-%d%H:%M:%S")).astimezone(tz)
        self.start_date_et = tz.localize(datetime.strptime(self.start_date+self.end_time,"%Y-%m-%d%H:%M:%S")).astimezone(tz)
        self.end_date_st = tz.localize(datetime.strptime(self.end_date+self.start_time,"%Y-%m-%d%H:%M:%S")).astimezone(tz)
        self.end_date_et = tz.localize(datetime.strptime(self.end_date+self.end_time,"%Y-%m-%d%H:%M:%S")).astimezone(tz)
        
        self.time_value = int(self.time_frame[:-1])
        self.time_format = self.time_frame[-1]

        if self.time_format == 'm':
            freq = f'{self.time_value * 1000} min' 
        elif self.time_format == 'h':
            freq = f'{self.time_value * 1000} H'
        elif self.time_format == 'd':
            freq = f'{self.time_value * 1000} D'

        self.date_range = pd.date_range(start=self.start_date_st,end=self.end_date_et,freq=freq)
        self.date_range = [tz.localize(datetime.strptime(str(x)[:-6],"%Y-%m-%d %H:%M:%S")).astimezone(tz) for x in self.date_range]
        self.date_range.append(self.end_date_et)
        self.date_range = self.date_range[1:]
        self.time_delta = (self.start_date_et-self.start_date_st)

        
    async def fetch_data(self):
            
        df = pd.DataFrame()
        for tic in self.ticker_list:
            for date in self.date_range:
                # if date.weekday() < 5:
                new_data = await self.account.get_historical_candles(tic,self.time_frame,date,limit=1000)
                print(f'Downloaded {len(new_data) if new_data else 0} historical data for {tic}')
                temp_df = pd.DataFrame(new_data)
                temp_df.columns = ['date','open','high','low','close','volume']
                temp_df['date'] = temp_df['date'].dt.tz_convert('EST')
                temp_df["date"] = pd.to_datetime(temp_df['date'],format='%Y%m%d  %H:%M:%S')
                temp_df['tic'] = tic
                temp_df['sec'] = '-'
                temp_df['exchange'] = '-'
                # if date.weekday() == 0:
                #     temp_df['time'] = temp_df['date'].dt.time
                #     temp_df = temp_df[(temp_df['time']>=datetime.strptime("01:00:00","%H:%M:%S").time())]
                #     temp_df.drop('time',inplace=True,axis=1)
                # elif date.weekday() == 4:
                #     temp_df['time'] = temp_df['date'].dt.time
                #     temp_df = temp_df[(temp_df['time']<=datetime.strptime("03:30:00","%H:%M:%S").time())]
                #     temp_df.drop('time',inplace=True,axis=1)
                df = df.append(temp_df)
        
        df['only date'] = df['date'].dt.date
        df['time'] = df['date'].dt.time
        df = df[(df['time']>=datetime.strptime(self.start_time,"%H:%M:%S").time()) & 
                (df['time']<=datetime.strptime(self.end_time,"%H:%M:%S").time())]
        df = df[(df['only date']>=datetime.strptime(self.start_date,"%Y-%m-%d").date()) & 
                (df['only date']<=datetime.strptime(self.end_date,"%Y-%m-%d").date())]
        # df['market closed'] = df.groupby('only date')['time'].transform(lambda x:(x==x.max()))
        # df['market closed'] = df['market closed'] | df['market closed'].shift(-1).fillna(True)
        df = df.reset_index(drop=True)
        return df
    
    async def fetch_todays_data(self,time_now,duration):
        df = pd.DataFrame()
        if self.time_format == 'm':
            duration = duration / (60 * self.time_value)
        elif self.time_format == 'h':
            duration = duration / (3600 * self.time_value)

        for tic in self.ticker_list:
            # if time_now.weekday() < 5:
            new_data = await self.account.get_historical_candles(tic,self.time_frame,time_now,limit=duration)
            print(f'Downloaded {len(new_data) if new_data else 0} historical data for {tic}')
            temp_df = pd.DataFrame(new_data)
            temp_df.columns = ['date','open','high','low','close','volume']
            temp_df['date'] = temp_df['date'].dt.tz_convert('EST')
            temp_df["date"] = pd.to_datetime(temp_df['date'],format='%Y%m%d  %H:%M:%S')
            temp_df['tic'] = tic
            temp_df['sec'] = '-'
            temp_df['exchange'] = '-'
            # if time_now.weekday() == 0:
            #     temp_df['time'] = temp_df['date'].dt.time
            #     temp_df = temp_df[(temp_df['time']>=datetime.strptime("01:00:00","%H:%M:%S").time())]
            #     temp_df.drop('time',inplace=True,axis=1)
            # elif time_now.weekday() == 4:
            #     temp_df['time'] = temp_df['date'].dt.time
            #     temp_df = temp_df[(temp_df['time']<=datetime.strptime("03:30:00","%H:%M:%S").time())]
            #     temp_df.drop('time',inplace=True,axis=1)
            df = df.append(temp_df)

        df['only date'] = df['date'].dt.date
        df['time'] = df['date'].dt.time
        df = df[(df['time']>=datetime.strptime(self.start_time,"%H:%M:%S").time()) & 
                (df['time']<=datetime.strptime(self.end_time,"%H:%M:%S").time())]
        # df['market closed'] = False
        df = df.reset_index(drop=True)

        return df

    async def fetch_daily_data(self):
            
        df = pd.DataFrame()
        for tic in self.ticker_list:
            for date in self.date_range:
                # if date.weekday() < 5:
                new_data = await self.account.get_historical_candles(tic,self.time_frame,date,limit=1000)
                print(f'Downloaded {len(new_data) if new_data else 0} historical data for {tic}')
                temp_df = pd.DataFrame(new_data)
                temp_df.columns = ['date','open','high','low','close','volume']
                temp_df['date'] = temp_df['date'].dt.tz_convert('EST')
                temp_df["date"] = pd.to_datetime(temp_df['date'],format='%Y%m%d  %H:%M:%S')
                temp_df['tic'] = tic
                temp_df['sec'] = '-'
                temp_df['exchange'] = '-'
                # if date.weekday() == 0:
                #     temp_df['time'] = temp_df['date'].dt.time
                #     temp_df = temp_df[(temp_df['time']>=datetime.strptime("01:00:00","%H:%M:%S").time())]
                #     temp_df.drop('time',inplace=True,axis=1)
                # elif date.weekday() == 4:
                #     temp_df['time'] = temp_df['date'].dt.time
                #     temp_df = temp_df[(temp_df['time']<=datetime.strptime("03:30:00","%H:%M:%S").time())]
                #     temp_df.drop('time',inplace=True,axis=1)
                df = df.append(temp_df)
        
        df['only date'] = df['date'].dt.date
        df = df[(df['only date']>=datetime.strptime(self.start_date,"%Y-%m-%d").date()) & 
                (df['only date']<=datetime.strptime(self.end_date,"%Y-%m-%d").date())]
        df = df.reset_index(drop=True)
        return df


class FeatureEngineer:

    def __init__(self,
                stock_indicator_list = [],
                additional_indicators = [],
                cov_matrix = False):
        self.stock_indicator_list = stock_indicator_list
        self.additional_indicators = additional_indicators
        self.indicators = self.stock_indicator_list + self.additional_indicators
        self.cov_matrix = cov_matrix
    
    def create_data(self,df):
        df = self.clean_data(df)

        if self.cov_matrix:
            df = self.add_cov_matrix(df)

        if 'hurst_exp' in self.additional_indicators:
            df = self.add_hurst_exponent(df)
        if 'half_hour_time' in self.additional_indicators:
            df = self.add_half_hour_time(df)

        if 'pct_return_5' in self.additional_indicators:
            df = self.add_pct_return(df,5,'pct_return_5','close')
        if 'pct_return_22' in self.additional_indicators:
            df = self.add_pct_return(df,22,'pct_return_22','close')
        if 'pct_return_66' in self.additional_indicators:
            df = self.add_pct_return(df,66,'pct_return_66','close')
        if 'pct_return_1year' in self.additional_indicators:
            df = self.add_pct_return(df,252,'pct_return_1year','close')
        if 'pct_return_3year' in self.additional_indicators:
            df = self.add_pct_return(df,3*252,'pct_return_3year','close')
        if 'pct_return_5year' in self.additional_indicators:
            df = self.add_pct_return(df,5*252,'pct_return_5year','close')
        
        if 'price_diff_5' in self.additional_indicators:
            df = self.add_diff(df,5,'price_diff_5','close')
        if 'price_diff_22' in self.additional_indicators:
            df = self.add_diff(df,22,'price_diff_22','close')
        if 'price_diff_66' in self.additional_indicators:
            df = self.add_diff(df,66,'price_diff_66','close')
        if 'price_diff_1year' in self.additional_indicators:
            df = self.add_diff(df,252,'price_diff_1year','close')
        if 'price_diff_3year' in self.additional_indicators:
            df = self.add_diff(df,3*252,'price_diff_3year','close')
        if 'price_diff_5year' in self.additional_indicators:
            df = self.add_diff(df,5*252,'price_diff_5year','close')
        
        if 'sharpe_diff_5' in self.additional_indicators:
            df = self.add_sharpe(df,5,'sharpe_diff_5')
            df = self.add_diff(df,5,'sharpe_diff_5','sharpe_diff_5')
        if 'sharpe_diff_22' in self.additional_indicators:
            df = self.add_sharpe(df,22,'sharpe_diff_22')
            df = self.add_diff(df,22,'sharpe_diff_22','sharpe_diff_22')
        if 'sharpe_diff_66' in self.additional_indicators:
            df = self.add_sharpe(df,66,'sharpe_diff_66')
            df = self.add_diff(df,66,'sharpe_diff_66','sharpe_diff_66')
        if 'sharpe_diff_1year' in self.additional_indicators:
            df = self.add_sharpe(df,252,'sharpe_diff_1year')
            df = self.add_diff(df,252,'sharpe_diff_1year','sharpe_diff_1year')
        if 'sharpe_diff_3year' in self.additional_indicators:
            df = self.add_sharpe(df,3*252,'sharpe_diff_3year')
            df = self.add_diff(df,3*252,'sharpe_diff_3year','sharpe_diff_3year')
        if 'sharpe_diff_5year' in self.additional_indicators:
            df = self.add_sharpe(df,5*252,'sharpe_diff_5year')
            df = self.add_diff(df,5*252,'sharpe_diff_5year','sharpe_diff_5year')
        
        if 'sortino_diff_5' in self.additional_indicators:
            df = self.add_sortino(df,5,'sortino_diff_5')
            df = self.add_diff(df,5,'sortino_diff_5','sortino_diff_5')
        if 'sortino_diff_22' in self.additional_indicators:
            df = self.add_sortino(df,22,'sortino_diff_22')
            df = self.add_diff(df,22,'sortino_diff_22','sortino_diff_22')
        if 'sortino_diff_66' in self.additional_indicators:
            df = self.add_sortino(df,66,'sortino_diff_66')
            df = self.add_diff(df,66,'sortino_diff_66','sortino_diff_66')
        if 'sortino_diff_1year' in self.additional_indicators:
            df = self.add_sortino(df,252,'sortino_diff_1year')
            df = self.add_diff(df,252,'sortino_diff_1year','sortino_diff_1year')
        if 'sortino_diff_3year' in self.additional_indicators:
            df = self.add_sortino(df,3*252,'sortino_diff_3year')
            df = self.add_diff(df,3*252,'sortino_diff_3year','sortino_diff_3year')
        if 'sortino_diff_5year' in self.additional_indicators:
            df = self.add_sortino(df,5*252,'sortino_diff_5year')
            df = self.add_diff(df,5*252,'sortino_diff_5year','sortino_diff_5year')
        
        if 'calamar_diff_5' in self.additional_indicators:
            df = self.add_clamar(df,5,'calamar_diff_5')
            df = self.add_diff(df,5,'calamar_diff_5','calamar_diff_5')
        if 'calamar_diff_22' in self.additional_indicators:
            df = self.add_clamar(df,22,'calamar_diff_22')
            df = self.add_diff(df,22,'calamar_diff_22','calamar_diff_22')
        if 'calamar_diff_66' in self.additional_indicators:
            df = self.add_clamar(df,66,'calamar_diff_66')
            df = self.add_diff(df,66,'calamar_diff_66','calamar_diff_66')
        if 'calamar_diff_1year' in self.additional_indicators:
            df = self.add_clamar(df,252,'calamar_diff_1year')
            df = self.add_diff(df,252,'calamar_diff_1year','calamar_diff_1year')
        if 'calamar_diff_3year' in self.additional_indicators:
            df = self.add_clamar(df,3*252,'calamar_diff_3year')
            df = self.add_diff(df,3*252,'calamar_diff_3year','calamar_diff_3year')
        if 'calamar_diff_5year' in self.additional_indicators:
            df = self.add_clamar(df,5*252,'calamar_diff_5year')
            df = self.add_diff(df,5*252,'calamar_diff_5year','calamar_diff_5year')
        
        if 'vix_fix_diff_5' in self.additional_indicators:
            df = self.add_vix_fix(df,5,'vix_fix_diff_5')
            df = self.add_diff(df,5,'vix_fix_diff_5','vix_fix_diff_5')
        if 'vix_fix_diff_22' in self.additional_indicators:
            df = self.add_vix_fix(df,22,'vix_fix_diff_22')
            df = self.add_diff(df,22,'vix_fix_diff_22','vix_fix_diff_22')
        if 'vix_fix_diff_66' in self.additional_indicators:
            df = self.add_vix_fix(df,66,'vix_fix_diff_66')
            df = self.add_diff(df,66,'vix_fix_diff_66','vix_fix_diff_66')
        if 'vix_fix_diff_1year' in self.additional_indicators:
            df = self.add_vix_fix(df,252,'vix_fix_diff_1year')
            df = self.add_diff(df,252,'vix_fix_diff_1year','vix_fix_diff_1year')
        if 'vix_fix_diff_3year' in self.additional_indicators:
            df = self.add_vix_fix(df,3*252,'vix_fix_diff_3year')
            df = self.add_diff(df,3*252,'vix_fix_diff_3year','vix_fix_diff_3year')
        if 'vix_fix_diff_5year' in self.additional_indicators:
            df = self.add_vix_fix(df,5*252,'vix_fix_diff_5year')
            df = self.add_diff(df,5*252,'vix_fix_diff_5year','vix_fix_diff_5year')
        
        if 'max_value_price_diff_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_price_diff_5','close')
            df = self.add_diff(df,5,'max_value_price_diff_5','max_value_price_diff_5')
        if 'max_value_price_diff_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_price_diff_22','close')
            df = self.add_diff(df,22,'max_value_price_diff_22','max_value_price_diff_22')
        if 'max_value_price_diff_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_price_diff_66','close')
            df = self.add_diff(df,66,'max_value_price_diff_66','max_value_price_diff_66')
        if 'max_value_price_diff_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_price_diff_1year','close')
            df = self.add_diff(df,252,'max_value_price_diff_1year','max_value_price_diff_1year')
        if 'max_value_price_diff_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_price_diff_3year','close')
            df = self.add_diff(df,3*252,'max_value_price_diff_3year','max_value_price_diff_3year')
        if 'max_value_price_diff_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_price_diff_5year','close')
            df = self.add_diff(df,5*252,'max_value_price_diff_5year','max_value_price_diff_5year')
        
        if 'min_value_price_diff_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_price_diff_5','close')
            df = self.add_diff(df,5,'min_value_price_diff_5','min_value_price_diff_5')
        if 'min_value_price_diff_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_price_diff_22','close')
            df = self.add_diff(df,22,'min_value_price_diff_22','min_value_price_diff_22')
        if 'min_value_price_diff_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_price_diff_66','close')
            df = self.add_diff(df,66,'min_value_price_diff_66','min_value_price_diff_66')
        if 'min_value_price_diff_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_price_diff_1year','close')
            df = self.add_diff(df,252,'min_value_price_diff_1year','min_value_price_diff_1year')
        if 'min_value_price_diff_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_price_diff_3year','close')
            df = self.add_diff(df,3*252,'min_value_price_diff_3year','min_value_price_diff_3year')
        if 'min_value_price_diff_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_price_diff_5year','close')
            df = self.add_diff(df,5*252,'min_value_price_diff_5year','min_value_price_diff_5year')
        

        if 'max_value_volume_diff_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_volume_diff_5','volume')
            df = self.add_diff(df,5,'max_value_volume_diff_5','max_value_volume_diff_5')
        if 'max_value_volume_diff_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_volume_diff_22','volume')
            df = self.add_diff(df,22,'max_value_volume_diff_22','max_value_volume_diff_22')
        if 'max_value_volume_diff_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_volume_diff_66','volume')
            df = self.add_diff(df,66,'max_value_volume_diff_66','max_value_volume_diff_66')
        if 'max_value_volume_diff_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_volume_diff_1year','volume')
            df = self.add_diff(df,252,'max_value_volume_diff_1year','max_value_volume_diff_1year')
        if 'max_value_volume_diff_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_volume_diff_3year','volume')
            df = self.add_diff(df,3*252,'max_value_volume_diff_3year','max_value_volume_diff_3year')
        if 'max_value_volume_diff_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_volume_diff_5year','volume')
            df = self.add_diff(df,5*252,'max_value_volume_diff_5year','max_value_volume_diff_5year')
        
        if 'min_value_volume_diff_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_volume_diff_5','volume')
            df = self.add_diff(df,5,'min_value_volume_diff_5','min_value_volume_diff_5')
        if 'min_value_volume_diff_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_volume_diff_22','volume')
            df = self.add_diff(df,22,'min_value_volume_diff_22','min_value_volume_diff_22')
        if 'min_value_volume_diff_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_volume_diff_66','volume')
            df = self.add_diff(df,66,'min_value_volume_diff_66','min_value_volume_diff_66')
        if 'min_value_volume_diff_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_volume_diff_1year','volume')
            df = self.add_diff(df,252,'min_value_volume_diff_1year','min_value_volume_diff_1year')
        if 'min_value_volume_diff_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_volume_diff_3year','volume')
            df = self.add_diff(df,3*252,'min_value_volume_diff_3year','min_value_volume_diff_3year')
        if 'min_value_volume_diff_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_volume_diff_5year','volume')
            df = self.add_diff(df,5*252,'min_value_volume_diff_5year','min_value_volume_diff_5year')


        if 'vix_fix_5' in self.additional_indicators:
            df = self.add_vix_fix(df,5,'vix_fix_5')
        if 'sharpe_5' in self.additional_indicators:
            df = self.add_sharpe(df,5,'sharpe_5')
        if 'sortino_5' in self.additional_indicators:
            df = self.add_sortino(df,5,'sortino_5')
        if 'calamar_5' in self.additional_indicators:
            df = self.add_clamar(df,5,'calamar_5')
        if 'vpin_5' in self.additional_indicators:
            df = self.add_vpin(df,5,'vpin_5')
        if 'max_value_price_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_price_5','close')
        if 'min_value_price_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_price_5','close')
        if 'max_value_volume_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_volume_5','volume')
        if 'min_value_volume_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_volume_5','volume')
        
        if 'vix_fix_22' in self.additional_indicators:
            df = self.add_vix_fix(df,22,'vix_fix_22')
        if 'sharpe_22' in self.additional_indicators:
            df = self.add_sharpe(df,22,'sharpe_22')
        if 'sortino_22' in self.additional_indicators:
            df = self.add_sortino(df,22,'sortino_22')
        if 'calamar_22' in self.additional_indicators:
            df = self.add_clamar(df,22,'calamar_22')
        if 'vpin_22' in self.additional_indicators:
            df = self.add_vpin(df,22,'vpin_22')
        if 'max_value_price_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_price_22','close')
        if 'min_value_price_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_price_22','close')
        if 'max_value_volume_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_volume_22','volume')
        if 'min_value_volume_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_volume_22','volume')

        if 'vix_fix_66' in self.additional_indicators:
            df = self.add_vix_fix(df,66,'vix_fix_66')
        if 'sharpe_66' in self.additional_indicators:
            df = self.add_sharpe(df,66,'sharpe_66')
        if 'sortino_66' in self.additional_indicators:
            df = self.add_sortino(df,66,'sortino_66')
        if 'calamar_66' in self.additional_indicators:
            df = self.add_clamar(df,66,'calamar_66')
        if 'vpin_66' in self.additional_indicators:
            df = self.add_vpin(df,66,'vpin_66')
        if 'max_value_price_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_price_66','close')
        if 'min_value_price_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_price_66','close')
        if 'max_value_volume_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_volume_66','volume')
        if 'min_value_volume_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_volume_66','volume')

        if 'vix_fix_1year' in self.additional_indicators:
            df = self.add_vix_fix(df,252,'vix_fix_1year')
        if 'sharpe_1year' in self.additional_indicators:
            df = self.add_sharpe(df,252,'sharpe_1year')
        if 'sortino_1year' in self.additional_indicators:
            df = self.add_sortino(df,252,'sortino_1year')
        if 'calamar_1year' in self.additional_indicators:
            df = self.add_clamar(df,252,'calamar_1year')
        if 'vpin_1year' in self.additional_indicators:
            df = self.add_vpin(df,252,'vpin_1year')
        if 'max_value_price_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_price_1year','close')
        if 'min_value_price_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_price_1year','close')
        if 'max_value_volume_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_volume_1year','volume')
        if 'min_value_volume_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_volume_1year','volume')
        
        if 'vix_fix_3year' in self.additional_indicators:
            df = self.add_vix_fix(df,3*252,'vix_fix_3year')
        if 'sharpe_3year' in self.additional_indicators:
            df = self.add_sharpe(df,3*252,'sharpe_3year')
        if 'sortino_3year' in self.additional_indicators:
            df = self.add_sortino(df,3*252,'sortino_3year')
        if 'calamar_3year' in self.additional_indicators:
            df = self.add_clamar(df,3*252,'calamar_3year')
        if 'vpin_3year' in self.additional_indicators:
            df = self.add_vpin(df,3*252,'vpin_3year')
        if 'max_value_price_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_price_3year','close')
        if 'min_value_price_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_price_3year','close')
        if 'max_value_volume_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_volume_3year','volume')
        if 'min_value_volume_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_volume_3year','volume')
        
        if 'vix_fix_5year' in self.additional_indicators:
            df = self.add_vix_fix(df,5*252,'vix_fix_5year')
        if 'sharpe_5year' in self.additional_indicators:
            df = self.add_sharpe(df,5*252,'sharpe_5year')
        if 'sortino_5year' in self.additional_indicators:
            df = self.add_sortino(df,5*252,'sortino_5year')
        if 'calamar_5year' in self.additional_indicators:
            df = self.add_clamar(df,5*252,'calamar_5year')
        if 'vpin_5year' in self.additional_indicators:
            df = self.add_vpin(df,5*252,'vpin_5year')
        if 'max_value_price_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_price_5year','close')
        if 'min_value_price_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_price_5year','close')
        if 'max_value_volume_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_volume_5year','volume')
        if 'min_value_volume_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_volume_5year','volume')

        if len(self.stock_indicator_list)>0:
            df = self.add_stock_indicators(df)

        df.loc[:,self.indicators] = df[self.indicators].replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.fillna(0)
        df = df.sort_values(["date", "tic"], ignore_index=True)
        df.index = df["date"].factorize()[0]
        return df
    
    def time_series_split(self,df, start, end, target_date_col="date"):
        df = df.copy()
        data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
        data.index = data[target_date_col].factorize()[0]
        return data
        
    def train_test_split(self,df,train_period,test_period):
        df = self.create_data(df)
        train = self.time_series_split(df, start = train_period[0], end = train_period[1])
        test = self.time_series_split(df, start = test_period[0], end = test_period[1])
        return train,test
    
    def clean_data(self,data):
        df = data.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.drop_duplicates(subset=['date','tic'])
        df = df.reset_index(drop=True)
        df = self.skip_missing_dates(df)
        df = self.remove_corrupt_ticker(df)
        df.index = df.date.factorize()[0]
        df=df.sort_values(['date','tic'],ignore_index=True)
        return df
    
    def remove_corrupt_ticker(self,df:pd.DataFrame):
        a = df.groupby('tic')['close'].apply(lambda x:sum(x==0))
        invalid_ticker = a[a>0].index.tolist()
        df = df[~df['tic'].isin(invalid_ticker)]
        df = df.reset_index(drop=True)
        print("Tickers with corrupt Data",invalid_ticker)
        print("Remaining ticker",df.tic.unique().tolist())
        return df
    
    def skip_missing_dates(self,df:pd.DataFrame):
        n_ticker = df['tic'].nunique()
        a = df.groupby('date')['tic'].count()
        invalid_dates = a[a<n_ticker].index.tolist()
        print("Deleted Dates",len(invalid_dates))
        df = df[~df['date'].isin(invalid_dates)]
        df = df.reset_index(drop=True)
        return df
    
    def add_half_hour_time(self,df:pd.DataFrame):
        df['half_hour_time'] = [x.hour*2 +2 if int((x.minute//30)*30) else x.hour*2+1 for x in df['date']]
        return df
    
    def add_cov_matrix(self,df,lookback=252):
        df.index = df.date.factorize()[0]

        cov_list = []
        for i in range(lookback,len(df.index.unique())):
            data_lookback = df.loc[i-lookback:i,:]
            price_lookback=data_lookback.pivot_table(index = 'date',columns = 'tic', values = 'close')
            return_lookback = price_lookback.pct_change().dropna()
            return_lookback = return_lookback.replace([np.inf, -np.inf], np.nan)
            return_lookback = return_lookback.fillna(method="ffill").fillna(method="bfill")
            covs = return_lookback.cov().values 
            cov_list.append(covs)
        
        df_cov = pd.DataFrame({'date':df.date.unique()[lookback:],'cov_list':cov_list})
        df = df.merge(df_cov, on='date',how='left')
        return df
    
    def add_hurst_exponent(self,data,max_lag=20):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['hurst_exp'] = temp['close'].rolling(max_lag*2).apply(lambda x:self.get_hurst_exponent(x.values))
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'hurst_exp']], on=["tic", "date"], how="left")
        return df

    def get_hurst_exponent(self,time_series, max_lag=20):
        lags = range(2, max_lag)
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]
    
    def add_pct_return(self,data,interval,name,column):
        df = data.copy()
        df[name] = df.groupby('tic')[column].pct_change(interval)
        return df
    
    def add_diff(self,data,interval,name,column):
        df = data.copy()
        df[name] = df.groupby('tic')[column].diff(interval)
        return df
    
    def add_max_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).max()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_min_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def add_sharpe(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def get_buckets(self,df,bucketSize):
        volumeBuckets = pd.DataFrame(columns=['buy','sell','date'])
        count = 0
        BV = 0
        SV = 0
        for index,row in df.iterrows():
            newVolume = row['volume']
            z = row['z']
            if bucketSize < count + newVolume:
                BV = BV + (bucketSize-count)*z
                SV = SV + (bucketSize-count)*(1-z)
                volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = newVolume - (bucketSize-count)
                if int(count/bucketSize) > 0:
                    for i in range(0,int(count/bucketSize)):
                        BV = (bucketSize)*z
                        SV = (bucketSize)*(1-z)
                        volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = count%bucketSize
                BV = (count)*z
                SV = (count)*(1-z)
            else:
                BV = BV + (newVolume)*z
                SV = SV + (newVolume)*(1-z)
                count = count + newVolume
        
        volumeBuckets = volumeBuckets.drop_duplicates('date',keep='last')
        return volumeBuckets

    def calc_vpin(self,data,bucketSize,window):
        volume = (data['volume'])
        trades = (data['close'])
        trades = trades.diff(1).dropna()
        volume = volume.dropna()
        sigma = trades.std()
        z = trades.apply(lambda x: norm.cdf(x/sigma))
        df = pd.DataFrame({'z':z,'volume':volume}).dropna()
        volumeBuckets = self.get_buckets(df,bucketSize)
        volumeBuckets['vpin'] = abs(volumeBuckets['buy']-volumeBuckets['sell']).rolling(window,min_periods=1).mean()/bucketSize
        return volumeBuckets[['date','vpin']]
    
    def add_vpin(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic']==ticker)].copy()
            temp = temp.set_index('date')
            bucketsize = temp['volume'].mean()
            temp = self.calc_vpin(temp,bucketsize,days)
            temp[name] = temp['vpin']
            temp['tic'] = ticker
            indicator_df = indicator_df.append(temp,ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def add_stock_indicators(self,data):
        df = data.copy()
        stock = Sdf.retype(df.copy())
        unique_ticker = stock.tic.unique()
        for indicator in self.stock_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["date"] = df[df.tic == unique_ticker[i]][
                        "date"
                    ].to_list()
                    indicator_df = indicator_df.append(temp_indicator, ignore_index=True)
                except Exception as e:
                    print(e)
            df = df.merge(indicator_df[["tic", "date", indicator]], on=["tic", "date"], how="left")
        return df

class DayTradeFeatureEngineer:

    def __init__(self,
                stock_indicator_list = [],
                additional_indicators = [],
                cov_matrix = False):
        self.stock_indicator_list = stock_indicator_list
        self.additional_indicators = additional_indicators
        self.indicators = self.stock_indicator_list + self.additional_indicators
        self.cov_matrix = cov_matrix
    
    def create_data(self,df):
        df = self.clean_data(df)

        if self.cov_matrix:
            df = self.add_cov_matrix(df)

        if 'hurst_exp' in self.additional_indicators:
            df = self.add_hurst_exponent(df)
        if 'half_hour_time' in self.additional_indicators:
            df = self.add_half_hour_time(df)
        
        if 'pct_return_10' in self.additional_indicators:
            df = self.add_pct_return(df,10,'pct_return_10','close')
        if 'pct_return_50' in self.additional_indicators:
            df = self.add_pct_return(df,50,'pct_return_50','close')
        if 'pct_return_100' in self.additional_indicators:
            df = self.add_pct_return(df,100,'pct_return_100','close')
        if 'pct_return_500' in self.additional_indicators:
            df = self.add_pct_return(df,500,'pct_return_500','close')
        if 'pct_return_1000' in self.additional_indicators:
            df = self.add_pct_return(df,1000,'pct_return_1000','close')
        
        if 'price_diff_10' in self.additional_indicators:
            df = self.add_diff(df,10,'price_diff_10','close')
        if 'price_diff_50' in self.additional_indicators:
            df = self.add_diff(df,50,'price_diff_50','close')
        if 'price_diff_100' in self.additional_indicators:
            df = self.add_diff(df,100,'price_diff_100','close')
        if 'price_diff_500' in self.additional_indicators:
            df = self.add_diff(df,252,'price_diff_500','close')
        if 'price_diff_1000' in self.additional_indicators:
            df = self.add_diff(df,3*252,'price_diff_1000','close')
        
        if 'sharpe_diff_10' in self.additional_indicators:
            df = self.add_sharpe(df,5,'sharpe_diff_10')
            df = self.add_diff(df,5,'sharpe_diff_10','sharpe_diff_10')
        if 'sharpe_diff_50' in self.additional_indicators:
            df = self.add_sharpe(df,50,'sharpe_diff_50')
            df = self.add_diff(df,50,'sharpe_diff_50','sharpe_diff_50')
        if 'sharpe_diff_100' in self.additional_indicators:
            df = self.add_sharpe(df,100,'sharpe_diff_100')
            df = self.add_diff(df,100,'sharpe_diff_100','sharpe_diff_100')
        if 'sharpe_diff_500' in self.additional_indicators:
            df = self.add_sharpe(df,500,'sharpe_diff_500')
            df = self.add_diff(df,500,'sharpe_diff_500','sharpe_diff_500')
        if 'sharpe_diff_1000' in self.additional_indicators:
            df = self.add_sharpe(df,1000,'sharpe_diff_1000')
            df = self.add_diff(df,1000,'sharpe_diff_1000','sharpe_diff_1000')
        
        if 'sortino_diff_10' in self.additional_indicators:
            df = self.add_sortino(df,10,'sortino_diff_10')
            df = self.add_diff(df,10,'sortino_diff_10','sortino_diff_10')
        if 'sortino_diff_50' in self.additional_indicators:
            df = self.add_sortino(df,50,'sortino_diff_50')
            df = self.add_diff(df,50,'sortino_diff_50','sortino_diff_50')
        if 'sortino_diff_100' in self.additional_indicators:
            df = self.add_sortino(df,100,'sortino_diff_100')
            df = self.add_diff(df,100,'sortino_diff_100','sortino_diff_100')
        if 'sortino_diff_500' in self.additional_indicators:
            df = self.add_sortino(df,500,'sortino_diff_500')
            df = self.add_diff(df,500,'sortino_diff_500','sortino_diff_500')
        if 'sortino_diff_1000' in self.additional_indicators:
            df = self.add_sortino(df,1000,'sortino_diff_1000')
            df = self.add_diff(df,1000,'sortino_diff_1000','sortino_diff_1000')
        
        if 'calamar_diff_10' in self.additional_indicators:
            df = self.add_clamar(df,10,'calamar_diff_10')
            df = self.add_diff(df,10,'calamar_diff_10','calamar_diff_10')
        if 'calamar_diff_50' in self.additional_indicators:
            df = self.add_clamar(df,50,'calamar_diff_50')
            df = self.add_diff(df,50,'calamar_diff_50','calamar_diff_50')
        if 'calamar_diff_100' in self.additional_indicators:
            df = self.add_clamar(df,100,'calamar_diff_100')
            df = self.add_diff(df,100,'calamar_diff_100','calamar_diff_100')
        if 'calamar_diff_500' in self.additional_indicators:
            df = self.add_clamar(df,500,'calamar_diff_500')
            df = self.add_diff(df,500,'calamar_diff_500','calamar_diff_500')
        if 'calamar_diff_1000' in self.additional_indicators:
            df = self.add_clamar(df,1000,'calamar_diff_1000')
            df = self.add_diff(df,1000,'calamar_diff_1000','calamar_diff_1000')

        if 'vix_fix_diff_10' in self.additional_indicators:
            df = self.add_vix_fix(df,10,'vix_fix_diff_10')
            df = self.add_diff(df,10,'vix_fix_diff_10','vix_fix_diff_10')
        if 'vix_fix_diff_50' in self.additional_indicators:
            df = self.add_vix_fix(df,50,'vix_fix_diff_50')
            df = self.add_diff(df,50,'vix_fix_diff_50','vix_fix_diff_50')
        if 'vix_fix_diff_100' in self.additional_indicators:
            df = self.add_vix_fix(df,100,'vix_fix_diff_100')
            df = self.add_diff(df,100,'vix_fix_diff_100','vix_fix_diff_100')
        if 'vix_fix_diff_500' in self.additional_indicators:
            df = self.add_vix_fix(df,500,'vix_fix_diff_500')
            df = self.add_diff(df,500,'vix_fix_diff_500','vix_fix_diff_500')
        if 'vix_fix_diff_1000' in self.additional_indicators:
            df = self.add_vix_fix(df,1000,'vix_fix_diff_1000')
            df = self.add_diff(df,1000,'vix_fix_diff_1000','vix_fix_diff_1000')
        
        if 'max_value_price_diff_10' in self.additional_indicators:
            df = self.add_max_value(df,10,'max_value_price_diff_10','close')
            df = self.add_diff(df,10,'max_value_price_diff_10','max_value_price_diff_10')
        if 'max_value_price_diff_50' in self.additional_indicators:
            df = self.add_max_value(df,50,'max_value_price_diff_50','close')
            df = self.add_diff(df,50,'max_value_price_diff_50','max_value_price_diff_50')
        if 'max_value_price_diff_100' in self.additional_indicators:
            df = self.add_max_value(df,100,'max_value_price_diff_100','close')
            df = self.add_diff(df,100,'max_value_price_diff_100','max_value_price_diff_100')
        if 'max_value_price_diff_500' in self.additional_indicators:
            df = self.add_max_value(df,500,'max_value_price_diff_500','close')
            df = self.add_diff(df,500,'max_value_price_diff_500','max_value_price_diff_500')
        if 'max_value_price_diff_1000' in self.additional_indicators:
            df = self.add_max_value(df,1000,'max_value_price_diff_1000','close')
            df = self.add_diff(df,1000,'max_value_price_diff_1000','max_value_price_diff_1000')
        
        if 'min_value_price_diff_10' in self.additional_indicators:
            df = self.add_min_value(df,10,'min_value_price_diff_10','close')
            df = self.add_diff(df,10,'min_value_price_diff_10','min_value_price_diff_10')
        if 'min_value_price_diff_50' in self.additional_indicators:
            df = self.add_min_value(df,50,'min_value_price_diff_50','close')
            df = self.add_diff(df,50,'min_value_price_diff_50','min_value_price_diff_50')
        if 'min_value_price_diff_100' in self.additional_indicators:
            df = self.add_min_value(df,100,'min_value_price_diff_100','close')
            df = self.add_diff(df,100,'min_value_price_diff_100','min_value_price_diff_100')
        if 'min_value_price_diff_500' in self.additional_indicators:
            df = self.add_min_value(df,500,'min_value_price_diff_500','close')
            df = self.add_diff(df,500,'min_value_price_diff_500','min_value_price_diff_500')
        if 'min_value_price_diff_1000' in self.additional_indicators:
            df = self.add_min_value(df,1000,'min_value_price_diff_1000','close')
            df = self.add_diff(df,1000,'min_value_price_diff_1000','min_value_price_diff_1000')

        if 'max_value_volume_diff_10' in self.additional_indicators:
            df = self.add_max_value(df,10,'max_value_volume_diff_10','volume')
            df = self.add_diff(df,10,'max_value_volume_diff_10','max_value_volume_diff_10')
        if 'max_value_volume_diff_50' in self.additional_indicators:
            df = self.add_max_value(df,50,'max_value_volume_diff_50','volume')
            df = self.add_diff(df,50,'max_value_volume_diff_50','max_value_volume_diff_50')
        if 'max_value_volume_diff_100' in self.additional_indicators:
            df = self.add_max_value(df,100,'max_value_volume_diff_100','volume')
            df = self.add_diff(df,100,'max_value_volume_diff_100','max_value_volume_diff_100')
        if 'max_value_volume_diff_500' in self.additional_indicators:
            df = self.add_max_value(df,500,'max_value_volume_diff_500','volume')
            df = self.add_diff(df,500,'max_value_volume_diff_500','max_value_volume_diff_500')
        if 'max_value_volume_diff_1000' in self.additional_indicators:
            df = self.add_max_value(df,1000,'max_value_volume_diff_1000','volume')
            df = self.add_diff(df,1000,'max_value_volume_diff_1000','max_value_volume_diff_1000')
        
        if 'min_value_volume_diff_10' in self.additional_indicators:
            df = self.add_min_value(df,10,'min_value_volume_diff_10','volume')
            df = self.add_diff(df,10,'min_value_volume_diff_10','min_value_volume_diff_10')
        if 'min_value_volume_diff_50' in self.additional_indicators:
            df = self.add_min_value(df,50,'min_value_volume_diff_50','volume')
            df = self.add_diff(df,50,'min_value_volume_diff_50','min_value_volume_diff_50')
        if 'min_value_volume_diff_100' in self.additional_indicators:
            df = self.add_min_value(df,100,'min_value_volume_diff_100','volume')
            df = self.add_diff(df,100,'min_value_volume_diff_100','min_value_volume_diff_100')
        if 'min_value_volume_diff_500' in self.additional_indicators:
            df = self.add_min_value(df,500,'min_value_volume_diff_500','volume')
            df = self.add_diff(df,500,'min_value_volume_diff_500','min_value_volume_diff_500')
        if 'min_value_volume_diff_1000' in self.additional_indicators:
            df = self.add_min_value(df,1000,'min_value_volume_diff_1000','volume')
            df = self.add_diff(df,1000,'min_value_volume_diff_1000','min_value_volume_diff_1000')

        if 'vix_fix_10' in self.additional_indicators:
            df = self.add_vix_fix(df,10,'vix_fix_10')
        if 'sharpe_10' in self.additional_indicators:
            df = self.add_sharpe(df,10,'sharpe_10')
        if 'sortino_10' in self.additional_indicators:
            df = self.add_sortino(df,10,'sortino_10')
        if 'calamar_10' in self.additional_indicators:
            df = self.add_clamar(df,10,'calamar_10')
        if 'vpin_10' in self.additional_indicators:
            df = self.add_clamar(df,10,'vpin_10')
        if 'max_value_price_10' in self.additional_indicators:
            df = self.add_max_value(df,10,'max_value_price_10','close')
        if 'min_value_price_10' in self.additional_indicators:
            df = self.add_min_value(df,10,'min_value_price_10','close')
        if 'max_value_volume_10' in self.additional_indicators:
            df = self.add_max_value(df,10,'max_value_volume_10','volume')
        if 'min_value_volume_10' in self.additional_indicators:
            df = self.add_min_value(df,10,'min_value_volume_10','volume')
        
        if 'vix_fix_50' in self.additional_indicators:
            df = self.add_vix_fix(df,50,'vix_fix_50')
        if 'sharpe_50' in self.additional_indicators:
            df = self.add_sharpe(df,50,'sharpe_50')
        if 'sortino_50' in self.additional_indicators:
            df = self.add_sortino(df,50,'sortino_50')
        if 'calamar_50' in self.additional_indicators:
            df = self.add_clamar(df,50,'calamar_50')
        if 'vpin_50' in self.additional_indicators:
            df = self.add_clamar(df,50,'vpin_50')
        if 'max_value_price_50' in self.additional_indicators:
            df = self.add_max_value(df,50,'max_value_price_50','close')
        if 'min_value_price_50' in self.additional_indicators:
            df = self.add_min_value(df,50,'min_value_price_50','close')
        if 'max_value_volume_50' in self.additional_indicators:
            df = self.add_max_value(df,50,'max_value_volume_50','volume')
        if 'min_value_volume_50' in self.additional_indicators:
            df = self.add_min_value(df,50,'min_value_volume_50','volume')
        
        if 'vix_fix_100' in self.additional_indicators:
            df = self.add_vix_fix(df,100,'vix_fix_100')
        if 'sharpe_100' in self.additional_indicators:
            df = self.add_sharpe(df,100,'sharpe_100')
        if 'sortino_100' in self.additional_indicators:
            df = self.add_sortino(df,100,'sortino_100')
        if 'calamar_100' in self.additional_indicators:
            df = self.add_clamar(df,100,'calamar_100')
        if 'vpin_100' in self.additional_indicators:
            df = self.add_clamar(df,100,'vpin_100')
        if 'max_value_price_100' in self.additional_indicators:
            df = self.add_max_value(df,100,'max_value_price_100','close')
        if 'min_value_price_100' in self.additional_indicators:
            df = self.add_min_value(df,100,'min_value_price_100','close')
        if 'max_value_volume_100' in self.additional_indicators:
            df = self.add_max_value(df,100,'max_value_volume_100','volume')
        if 'min_value_volume_100' in self.additional_indicators:
            df = self.add_min_value(df,100,'min_value_volume_100','volume')
        
        if 'vix_fix_500' in self.additional_indicators:
            df = self.add_vix_fix(df,500,'vix_fix_500')
        if 'sharpe_500' in self.additional_indicators:
            df = self.add_sharpe(df,500,'sharpe_500')
        if 'sortino_500' in self.additional_indicators:
            df = self.add_sortino(df,500,'sortino_500')
        if 'calamar_500' in self.additional_indicators:
            df = self.add_clamar(df,500,'calamar_500')
        if 'vpin_500' in self.additional_indicators:
            df = self.add_clamar(df,500,'vpin_500')
        if 'max_value_price_500' in self.additional_indicators:
            df = self.add_max_value(df,500,'max_value_price_500','close')
        if 'min_value_price_500' in self.additional_indicators:
            df = self.add_min_value(df,500,'min_value_price_500','close')
        if 'max_value_volume_500' in self.additional_indicators:
            df = self.add_max_value(df,500,'max_value_volume_500','volume')
        if 'min_value_volume_500' in self.additional_indicators:
            df = self.add_min_value(df,500,'min_value_volume_500','volume')
        
        if 'vix_fix_1000' in self.additional_indicators:
            df = self.add_vix_fix(df,1000,'vix_fix_1000')
        if 'sharpe_1000' in self.additional_indicators:
            df = self.add_sharpe(df,1000,'sharpe_1000')
        if 'sortino_1000' in self.additional_indicators:
            df = self.add_sortino(df,1000,'sortino_1000')
        if 'calamar_1000' in self.additional_indicators:
            df = self.add_clamar(df,1000,'calamar_1000')
        if 'vpin_1000' in self.additional_indicators:
            df = self.add_clamar(df,1000,'vpin_1000')
        if 'max_value_price_1000' in self.additional_indicators:
            df = self.add_max_value(df,1000,'max_value_price_1000','close')
        if 'min_value_price_1000' in self.additional_indicators:
            df = self.add_min_value(df,1000,'min_value_price_1000','close')
        if 'max_value_volume_1000' in self.additional_indicators:
            df = self.add_max_value(df,1000,'max_value_volume_1000','volume')
        if 'min_value_volume_1000' in self.additional_indicators:
            df = self.add_min_value(df,1000,'min_value_volume_1000','volume')
        
        if len(self.stock_indicator_list)>0:
            df = self.add_stock_indicators(df)

        df.loc[:,self.indicators] = df[self.indicators].replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.fillna(0)
        df = df.sort_values(["date", "tic"], ignore_index=True)
        df['closing time'] = df.groupby('date')['date'].transform(lambda x:(x==x.max))
        df.index = df["date"].factorize()[0]
        return df
    
    def time_series_split(self,df, start, end, target_date_col="date"):
        df = df.copy()
        data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
        data.index = data[target_date_col].factorize()[0]
        return data
        
    def train_test_split(self,df,train_period,test_period):
        df = self.create_data(df)
        train = self.time_series_split(df, start = train_period[0], end = train_period[1])
        test = self.time_series_split(df, start = test_period[0], end = test_period[1])
        return train,test
    
    def clean_data(self,data):
        df = data.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.drop_duplicates(subset=['date','tic'])
        df = df.reset_index(drop=True)
        df = self.skip_missing_dates(df)
        df = self.remove_corrupt_ticker(df)
        df.index = df.date.factorize()[0]
        df=df.sort_values(['date','tic'],ignore_index=True)
        return df
    
    def remove_corrupt_ticker(self,df:pd.DataFrame):
        a = df.groupby('tic')['close'].apply(lambda x:sum(x==0))
        invalid_ticker = a[a>0].index.tolist()
        df = df[~df['tic'].isin(invalid_ticker)]
        df = df.reset_index(drop=True)
        print("Tickers with corrupt Data",invalid_ticker)
        print("Remaining ticker",df.tic.unique().tolist())
        return df
    
    def skip_missing_dates(self,df:pd.DataFrame):
        n_ticker = df['tic'].nunique()
        a = df.groupby('date')['tic'].count()
        invalid_dates = a[a<n_ticker].index.tolist()
        df = df[~df['date'].isin(invalid_dates)]
        df = df.reset_index(drop=True)
        return df
    
    def add_half_hour_time(self,df:pd.DataFrame):
        df['half_hour_time'] = [x.hour*2 +2 if int((x.minute//30)*30) else x.hour*2+1 for x in df['date']]
        return df
    
    def add_cov_matrix(self,df,lookback=252):
        df.index = df.date.factorize()[0]

        cov_list = []
        for i in range(lookback,len(df.index.unique())):
            data_lookback = df.loc[i-lookback:i,:]
            price_lookback=data_lookback.pivot_table(index = 'date',columns = 'tic', values = 'close')
            return_lookback = price_lookback.pct_change().dropna()
            return_lookback = return_lookback.replace([np.inf, -np.inf], np.nan)
            return_lookback = return_lookback.fillna(method="ffill").fillna(method="bfill")
            covs = return_lookback.cov().values 
            cov_list.append(covs)
        
        df_cov = pd.DataFrame({'date':df.date.unique()[lookback:],'cov_list':cov_list})
        df = df.merge(df_cov, on='date',how='left')
        return df
    
    def add_hurst_exponent(self,data,max_lag=20):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['hurst_exp'] = temp['close'].rolling(max_lag*2).apply(lambda x:self.get_hurst_exponent(x.values))
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'hurst_exp']], on=["tic", "date"], how="left")
        return df

    def get_hurst_exponent(self,time_series, max_lag=20):
        lags = range(2, max_lag)
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]
    
    def add_diff(self,data,interval,name,column):
        df = data.copy()
        df[name] = df.groupby('tic')[column].diff(interval)
        return df
    
    def add_pct_return(self,data,interval,name,column):
        df = data.copy()
        df[name] = df.groupby('tic')[column].pct_change(interval)
        return df
    
    def add_max_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).max()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_min_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

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
    
    def get_buckets(self,df,bucketSize):
        volumeBuckets = pd.DataFrame(columns=['buy','sell','date'])
        count = 0
        BV = 0
        SV = 0
        for index,row in df.iterrows():
            newVolume = row['volume']
            z = row['z']
            if bucketSize < count + newVolume:
                BV = BV + (bucketSize-count)*z
                SV = SV + (bucketSize-count)*(1-z)
                volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = newVolume - (bucketSize-count)
                if int(count/bucketSize) > 0:
                    for i in range(0,int(count/bucketSize)):
                        BV = (bucketSize)*z
                        SV = (bucketSize)*(1-z)
                        volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = count%bucketSize
                BV = (count)*z
                SV = (count)*(1-z)
            else:
                BV = BV + (newVolume)*z
                SV = SV + (newVolume)*(1-z)
                count = count + newVolume
        
        volumeBuckets = volumeBuckets.drop_duplicates('date',keep='last')
        return volumeBuckets

    def calc_vpin(self,data,bucketSize,window):
        volume = (data['volume'])
        trades = (data['close'])
        trades = trades.diff(1).dropna()
        volume = volume.dropna()
        sigma = trades.std()
        z = trades.apply(lambda x: norm.cdf(x/sigma))
        df = pd.DataFrame({'z':z,'volume':volume}).dropna()
        volumeBuckets = self.get_buckets(df,bucketSize)
        volumeBuckets['vpin'] = abs(volumeBuckets['buy']-volumeBuckets['sell']).rolling(window,min_periods=1).mean()/bucketSize
        return volumeBuckets[['date','vpin']]
    
    def add_vpin(self,data,n,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic']==ticker)].copy()
            bucketsize = temp['volume'].mean()
            temp = self.calc_vpin(temp,bucketsize,n)
            temp[name] = temp['vpin']
            temp['tic'] = ticker
            indicator_df = indicator_df.append(temp,ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df


    def add_stock_indicators(self,data):
        df = data.copy()
        stock = Sdf.retype(df.copy())
        unique_ticker = stock.tic.unique()
        for indicator in self.stock_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["date"] = df[df.tic == unique_ticker[i]][
                        "date"
                    ].to_list()
                    indicator_df = indicator_df.append(temp_indicator, ignore_index=True)
                except Exception as e:
                    print(e)
            df = df.merge(indicator_df[["tic", "date", indicator]], on=["tic", "date"], how="left")
        return df


##################################
# Diffrenced Feature Engineering #
##################################
class DiffrencedFeatureEngineer:

    def __init__(self,
                stock_indicator_list = [],
                additional_indicators = [],
                cov_matrix = False):
        self.stock_indicator_list = stock_indicator_list
        self.additional_indicators = additional_indicators
        self.indicators = self.stock_indicator_list + self.additional_indicators
        self.cov_matrix = cov_matrix
    
    def create_data(self,df):
        df = self.clean_data(df)

        df = self.add_diffrenced_data(df)

        if self.cov_matrix:
            df = self.add_cov_matrix(df)

        if 'hurst_exp' in self.additional_indicators:
            df = self.add_hurst_exponent(df)
        if 'half_hour_time' in self.additional_indicators:
            df = self.add_half_hour_time(df)

        if 'vix_fix_5' in self.additional_indicators:
            df = self.add_vix_fix(df,5,'vix_fix_5')
        if 'sharpe_5' in self.additional_indicators:
            df = self.add_sharpe(df,5,'sharpe_5')
        if 'sortino_5' in self.additional_indicators:
            df = self.add_sortino(df,5,'sortino_5')
        if 'calamar_5' in self.additional_indicators:
            df = self.add_clamar(df,5,'calamar_5')
        if 'vpin_5' in self.additional_indicators:
            df = self.add_vpin(df,5,'vpin_5')
        if 'max_value_price_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_price_5','close_diff')
        if 'min_value_price_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_price_5','close_diff')
        if 'max_value_volume_5' in self.additional_indicators:
            df = self.add_max_value(df,5,'max_value_volume_5','volume')
        if 'min_value_volume_5' in self.additional_indicators:
            df = self.add_min_value(df,5,'min_value_volume_5','volume')
        
        if 'vix_fix_22' in self.additional_indicators:
            df = self.add_vix_fix(df,22,'vix_fix_22')
        if 'sharpe_22' in self.additional_indicators:
            df = self.add_sharpe(df,22,'sharpe_22')
        if 'sortino_22' in self.additional_indicators:
            df = self.add_sortino(df,22,'sortino_22')
        if 'calamar_22' in self.additional_indicators:
            df = self.add_clamar(df,22,'calamar_22')
        if 'vpin_22' in self.additional_indicators:
            df = self.add_vpin(df,22,'vpin_22')
        if 'max_value_price_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_price_22','close_diff')
        if 'min_value_price_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_price_22','close_diff')
        if 'max_value_volume_22' in self.additional_indicators:
            df = self.add_max_value(df,22,'max_value_volume_22','volume')
        if 'min_value_volume_22' in self.additional_indicators:
            df = self.add_min_value(df,22,'min_value_volume_22','volume')

        if 'vix_fix_66' in self.additional_indicators:
            df = self.add_vix_fix(df,66,'vix_fix_66')
        if 'sharpe_66' in self.additional_indicators:
            df = self.add_sharpe(df,66,'sharpe_66')
        if 'sortino_66' in self.additional_indicators:
            df = self.add_sortino(df,66,'sortino_66')
        if 'calamar_66' in self.additional_indicators:
            df = self.add_clamar(df,66,'calamar_66')
        if 'vpin_66' in self.additional_indicators:
            df = self.add_vpin(df,66,'vpin_66')
        if 'max_value_price_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_price_66','close_diff')
        if 'min_value_price_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_price_66','close_diff')
        if 'max_value_volume_66' in self.additional_indicators:
            df = self.add_max_value(df,66,'max_value_volume_66','volume')
        if 'min_value_volume_66' in self.additional_indicators:
            df = self.add_min_value(df,66,'min_value_volume_66','volume')

        if 'vix_fix_1year' in self.additional_indicators:
            df = self.add_vix_fix(df,252,'vix_fix_1year')
        if 'sharpe_1year' in self.additional_indicators:
            df = self.add_sharpe(df,252,'sharpe_1year')
        if 'sortino_1year' in self.additional_indicators:
            df = self.add_sortino(df,252,'sortino_1year')
        if 'calamar_1year' in self.additional_indicators:
            df = self.add_clamar(df,252,'calamar_1year')
        if 'vpin_1year' in self.additional_indicators:
            df = self.add_vpin(df,252,'vpin_1year')
        if 'max_value_price_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_price_1year','close_diff')
        if 'min_value_price_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_price_1year','close_diff')
        if 'max_value_volume_1year' in self.additional_indicators:
            df = self.add_max_value(df,252,'max_value_volume_1year','volume')
        if 'min_value_volume_1year' in self.additional_indicators:
            df = self.add_min_value(df,252,'min_value_volume_1year','volume')
        
        if 'vix_fix_3year' in self.additional_indicators:
            df = self.add_vix_fix(df,3*252,'vix_fix_3year')
        if 'sharpe_3year' in self.additional_indicators:
            df = self.add_sharpe(df,3*252,'sharpe_3year')
        if 'sortino_3year' in self.additional_indicators:
            df = self.add_sortino(df,3*252,'sortino_3year')
        if 'calamar_3year' in self.additional_indicators:
            df = self.add_clamar(df,3*252,'calamar_3year')
        if 'vpin_3year' in self.additional_indicators:
            df = self.add_vpin(df,3*252,'vpin_3year')
        if 'max_value_price_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_price_3year','close_diff')
        if 'min_value_price_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_price_3year','close_diff')
        if 'max_value_volume_3year' in self.additional_indicators:
            df = self.add_max_value(df,3*252,'max_value_volume_3year','volume')
        if 'min_value_volume_3year' in self.additional_indicators:
            df = self.add_min_value(df,3*252,'min_value_volume_3year','volume')
        
        if 'vix_fix_5year' in self.additional_indicators:
            df = self.add_vix_fix(df,5*252,'vix_fix_5year')
        if 'sharpe_5year' in self.additional_indicators:
            df = self.add_sharpe(df,5*252,'sharpe_5year')
        if 'sortino_5year' in self.additional_indicators:
            df = self.add_sortino(df,5*252,'sortino_5year')
        if 'calamar_5year' in self.additional_indicators:
            df = self.add_clamar(df,5*252,'calamar_5year')
        if 'vpin_5year' in self.additional_indicators:
            df = self.add_vpin(df,5*252,'vpin_5year')
        if 'max_value_price_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_price_5year','close_diff')
        if 'min_value_price_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_price_5year','close_diff')
        if 'max_value_volume_5year' in self.additional_indicators:
            df = self.add_max_value(df,5*252,'max_value_volume_5year','volume')
        if 'min_value_volume_5year' in self.additional_indicators:
            df = self.add_min_value(df,5*252,'min_value_volume_5year','volume')

        if len(self.stock_indicator_list)>0:
            df = self.add_stock_indicators(df)

        df.loc[:,self.indicators] = df[self.indicators].replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.fillna(0)
        df = df.sort_values(["date", "tic"], ignore_index=True)
        df.index = df["date"].factorize()[0]
        return df
    
    def time_series_split(self,df, start, end, target_date_col="date"):
        df = df.copy()
        data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
        data.index = data[target_date_col].factorize()[0]
        return data
        
    def train_test_split(self,df,train_period,test_period):
        df = self.create_data(df)
        train = self.time_series_split(df, start = train_period[0], end = train_period[1])
        test = self.time_series_split(df, start = test_period[0], end = test_period[1])
        return train,test
    
    def clean_data(self,data):
        df = data.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.drop_duplicates(subset=['date','tic'])
        df = df.reset_index(drop=True)
        df = self.skip_missing_dates(df)
        df = self.remove_corrupt_ticker(df)
        df.index = df.date.factorize()[0]
        df=df.sort_values(['date','tic'],ignore_index=True)
        return df
    
    def remove_corrupt_ticker(self,df:pd.DataFrame):
        a = df.groupby('tic')['close'].apply(lambda x:sum(x==0))
        invalid_ticker = a[a>0].index.tolist()
        df = df[~df['tic'].isin(invalid_ticker)]
        df = df.reset_index(drop=True)
        print("Tickers with corrupt Data",invalid_ticker)
        print("Remaining ticker",df.tic.unique().tolist())
        return df
    
    def skip_missing_dates(self,df:pd.DataFrame):
        n_ticker = df['tic'].nunique()
        a = df.groupby('date')['tic'].count()
        invalid_dates = a[a<n_ticker].index.tolist()
        print("Deleted Dates",len(invalid_dates))
        df = df[~df['date'].isin(invalid_dates)]
        df = df.reset_index(drop=True)
        return df
    
    def add_diffrenced_data(self,data):
        df = data.copy()
        for column in ['open','low','high','close']:
            df[f"{column}_diff"] = df.groupby('tic')[column].diff(1)
        return df
    
    def add_half_hour_time(self,df:pd.DataFrame):
        df['half_hour_time'] = [x.hour*2 +2 if int((x.minute//30)*30) else x.hour*2+1 for x in df['date']]
        return df
    
    def add_cov_matrix(self,df,lookback=252):
        df.index = df.date.factorize()[0]

        cov_list = []
        for i in range(lookback,len(df.index.unique())):
            data_lookback = df.loc[i-lookback:i,:]
            price_lookback=data_lookback.pivot_table(index = 'date',columns = 'tic', values = 'close_diff')
            return_lookback = price_lookback.pct_change().dropna()
            return_lookback = return_lookback.replace([np.inf, -np.inf], np.nan)
            return_lookback = return_lookback.fillna(method="ffill").fillna(method="bfill")
            covs = return_lookback.cov().values 
            cov_list.append(covs)
        
        df_cov = pd.DataFrame({'date':df.date.unique()[lookback:],'cov_list':cov_list})
        df = df.merge(df_cov, on='date',how='left')
        return df
    
    def add_hurst_exponent(self,data,max_lag=20):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['hurst_exp'] = temp['close_diff'].rolling(max_lag*2).apply(lambda x:self.get_hurst_exponent(x.values))
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'hurst_exp']], on=["tic", "date"], how="left")
        return df

    def get_hurst_exponent(self,time_series, max_lag=20):
        lags = range(2, max_lag)
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]
    
    def add_diff(self,data,interval,name,column):
        df = data.copy()
        df[name] = df.groupby('tic')[column].diff(interval)
        return df
    
    def add_max_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).max()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_min_value(self,data,days,name,column):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = temp[column].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def add_sharpe(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close_diff'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close_diff'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[name] = temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close_diff'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[name] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date",name]], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[name] = ((temp['close_diff'].rolling(days,min_periods=1).max() \
                                         - temp['low_diff'])/temp['close_diff'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df
    
    def get_buckets(self,df,bucketSize):
        volumeBuckets = pd.DataFrame(columns=['buy','sell','date'])
        count = 0
        BV = 0
        SV = 0
        for index,row in df.iterrows():
            newVolume = row['volume']
            z = row['z']
            if bucketSize < count + newVolume:
                BV = BV + (bucketSize-count)*z
                SV = SV + (bucketSize-count)*(1-z)
                volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = newVolume - (bucketSize-count)
                if int(count/bucketSize) > 0:
                    for i in range(0,int(count/bucketSize)):
                        BV = (bucketSize)*z
                        SV = (bucketSize)*(1-z)
                        volumeBuckets = volumeBuckets.append({'buy':BV,'sell':SV,'date':index},ignore_index=True)
                count = count%bucketSize
                BV = (count)*z
                SV = (count)*(1-z)
            else:
                BV = BV + (newVolume)*z
                SV = SV + (newVolume)*(1-z)
                count = count + newVolume
        
        volumeBuckets = volumeBuckets.drop_duplicates('date',keep='last')
        return volumeBuckets

    def calc_vpin(self,data,bucketSize,window):
        volume = (data['volume'])
        trades = (data['close_diff'])
        trades = trades.diff(1).dropna()
        volume = volume.dropna()
        sigma = trades.std()
        z = trades.apply(lambda x: norm.cdf(x/sigma))
        df = pd.DataFrame({'z':z,'volume':volume}).dropna()
        volumeBuckets = self.get_buckets(df,bucketSize)
        volumeBuckets['vpin'] = abs(volumeBuckets['buy']-volumeBuckets['sell']).rolling(window,min_periods=1).mean()/bucketSize
        return volumeBuckets[['date','vpin']]
    
    def add_vpin(self,data,days,name):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic']==ticker)].copy()
            temp = temp.set_index('date')
            bucketsize = temp['volume'].mean()
            temp = self.calc_vpin(temp,bucketsize,days)
            temp[name] = temp['vpin']
            temp['tic'] = ticker
            indicator_df = indicator_df.append(temp,ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", name]], on=["tic", "date"], how="left")
        return df

    def add_stock_indicators(self,data):
        df = data.copy()
        df_temp = data.copy()
        for column in ['open','high','low','close']:
            df_temp[column] = df_temp[f"{column}_diff"]
        stock = Sdf.retype(df_temp.copy())
        unique_ticker = stock.tic.unique()
        for indicator in self.stock_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["date"] = df[df.tic == unique_ticker[i]][
                        "date"
                    ].to_list()
                    indicator_df = indicator_df.append(temp_indicator, ignore_index=True)
                except Exception as e:
                    print(e)
            df = df.merge(indicator_df[["tic", "date", indicator]], on=["tic", "date"], how="left")
        return df