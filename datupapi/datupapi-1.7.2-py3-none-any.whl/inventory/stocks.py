import os
import pandas as pd
import re
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import datetime
from datupapi.utils.utils import Utils
from datupapi.configure.config import Config

class Stocks(Config):

    DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
    utls = Utils(config_file=DOCKER_CONFIG_PATH, logfile='data_io', log_path='output/logs')

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path
    
    def extract_sales_history (self, df_prep, df_invopt,date_cols,location=True):
        """
        Return a dataframe with addition the column Sales History in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit
        : param date_cols: Column name of date from df_prep
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : return df_extract: Dataframe with addition the column Sales History in the Inventory's Dataframe

        >>> df_extract = extract_sales_history (df_prep,df_invopt,date_cols='timestamp', location=stks.use_location)
        >>> df_extract =
                                            Item    Location   Inventory   InTransit    SalesHistory
                                idx0          85      905         23            0             200
                                idx1          102     487         95            0             100
        """
        try:
            df_prep_history = df_prep[df_prep[date_cols]== df_prep[date_cols].max()]
            if location:
                dict_names = {'item_id':'Item',
                                'location':'Location',
                                'demand':'SalesHistory'}
                df_prep_history.rename(columns=dict_names,inplace=True)

                df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                df_prep_history['Location'] = df_prep_history['Location'].astype(str)
                df_invopt['Item'] = df_invopt['Item'].astype(str)
                df_invopt['Location'] = df_invopt['Location'].astype(str)

                df_extract = pd.merge(df_invopt,df_prep_history[['Item','Location','SalesHistory']],on=['Item','Location'],how='left')
            else:
                dict_names =  {'item_id':'Item',
                                'demand':'SalesHistory'}
                df_prep_history.rename(columns=dict_names,inplace=True)

                df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                df_invopt['Item'] = df_invopt['Item'].astype(str)

                df_extract = pd.merge(df_invopt,df_prep_history[['Item','SalesHistory']],on=['Item'],how='left')

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_extract
    
    def extract_forecast(self,df_prep,df_fcst,df_invopt,date_cols,location=True,frequency_='W',column_forecast='SuggestedForecast',days_=7):
        """
        Return a dataframe with addition the column Suggested Forecast in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_fcst: Forecast's Dataframe 
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit, SalesHistory
        : param date_cols: Column name of date from df_fcst
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : param frequency_: Target frequency to the dataset
        : return df_extract: Dataframe with addition the column Suggested Forecast  in the Inventory's Dataframe

        >>> df_extract = extract_forecast (df_prep,df_fcst,df_invopt,date_cols='Date', location=stks.use_location, frequency_= stks.dataset_frequency)
        >>> df_extract =
                                            Item    Location   Inventory   InTransit     SuggestedForecast
                                idx0          85      905         23            0             200
                                idx1          102     487         95            0             100
        """
        try:
            if frequency_ == 'M':
                df_fcst_sug = df_fcst[df_fcst[date_cols]== df_fcst[date_cols].max()]
                if location:
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_fcst_sug['Location'] = df_fcst_sug['Location'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location',column_forecast]],on=['Item','Location'],how='left')
                else:
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item',column_forecast]],on=['Item'],how='left')
            
            elif frequency_ == 'W':
                df_fcst_sug = df_fcst[df_fcst[date_cols]== (df_prep['timestamp'].max() + timedelta(days=days_))]
                if location:
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_fcst_sug['Location'] = df_fcst_sug['Location'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location',column_forecast]],on=['Item','Location'],how='left')
                else:
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item',column_forecast]],on=['Item'],how='left')

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_extract

    def extract_avg_daily(self,df_prep, df_invopt,date_cols,location=True,months_=4,frequency_='M'):
        """
        Return a dataframe with addition the column AvgDailyUsage  in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit
        : param date_cols: Column name of date from df_prep
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : param months_: Target Number months 
        : param frequency_: Target frequency to the dataset
        : return df_extract: Dataframe with addition the column AvgDailyUsage  in the Inventory's Dataframe

        >>> df_extract = extract_avg_daily (df_prep, df_invopt, date_cols='timestamp', location=fmt.use_location, months_= 4, frequency_= fmt.dataset_frequency)
        >>> df_extract =
                                            Item    Location   Inventory   InTransit     AvgDailyUsage
                                idx0          85      905         23            0             20
                                idx1          102     487         95            0             10
        """
        try:
            
            if frequency_ == 'M':
                df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(months=months_))) & 
                                    (df_prep[date_cols] <= df_prep[date_cols].max() )]
                if location:
                    df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                        .agg({'demand': sum})\
                                                                                        .reset_index(drop=True)
                    df_prep_avg['demand'] = df_prep_avg['demand']/(30*months_)

                    dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'AvgDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)

                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','AvgDailyUsage']],on=['Item','Location'],how='left')
                else:
                    df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                .agg({'demand': sum})\
                                                                                .reset_index(drop=True)
                    df_prep_avg['demand'] = df_prep_avg['demand']/(30*months_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'AvgDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)

                    df_invopt['Item'] = df_invopt['Item'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','AvgDailyUsage']],on=['Item'],how='left')

            elif frequency_ == 'W':
                week_ = months_*4
                df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(days=7*week_))) & 
                                    (df_prep[date_cols] <= df_prep[date_cols].max() )]
                if location:
                    df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                        .agg({'demand': sum})\
                                                                                        .reset_index(drop=True)
                    df_prep_avg['demand'] = df_prep_avg['demand']/(7*week_)

                    dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'AvgDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)

                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','AvgDailyUsage']],on=['Item','Location'],how='left')

                else:
                    df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                .agg({'demand': sum})\
                                                                                .reset_index(drop=True)
                    df_prep_avg['demand'] = df_prep_avg['demand']/(7*week_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'AvgDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)

                    df_invopt['Item'] = df_invopt['Item'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','AvgDailyUsage']],on=['Item'],how='left')
            
            
            df_extract['AvgDailyUsage'] = round(df_extract['AvgDailyUsage'],3)
            df_extract.loc[(df_extract['AvgDailyUsage']>0)&(df_extract['AvgDailyUsage']<=1),'AvgDailyUsage'] = 1.0

        except:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_extract

    def extract_max_sales(self,df_prep, df_invopt,date_cols,location=True,months_=4,frequency_='M'):
        """
        Return a dataframe with addition the column MaxDailySales in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit
        : param date_cols: Column name of date from df_prep
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : param months_: Target Number months 
        : param frequency_: Target frequency to the dataset
        : return df_extract: Dataframe with addition the column MaxDailySales in the Inventory's Dataframe

        >>> df_extract = extract_max_sales (df_prep, df_invopt, date_cols='timestamp', location=fmt.use_location, months_= 4, frequency_= fmt.dataset_frequency)
        >>> df_extract =
                                            Item    Location   Inventory   InTransit     MaxDailySales
                                idx0          85      905         23            0             20
                                idx1          102     487         95            0             10
        """
        try:
              df_extract = pd.DataFrame()
              if frequency_ == 'M':
                  if location:
                    for a in df_invopt['Location'].unique():
                      df_prep1 = df_prep[df_prep['location']==a]
                      df_invopt1 = df_invopt[df_invopt['Location']==a]
                      for b in df_invopt1['Item'].unique():
                        df_prep2 = df_prep1[df_prep1['item_id']==b]
                        if len(df_prep2)>0: 
                          df_prep_avg = df_prep2[(df_prep2[date_cols] > (df_prep2[date_cols].max() - relativedelta(months=months_))) & 
                                              (df_prep2[date_cols] <= df_prep2[date_cols].max() )]
                          std = (np.std(df_prep_avg['demand']))/(30*months_)
                          df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                              .agg({'demand': sum})\
                                                                                              .reset_index(drop=True)
                          df_prep_avg['demand'] = (df_prep_avg['demand'] / (30*months_)) 
                          df_prep_avg.loc[(df_prep_avg['demand']>0)&(df_prep_avg['demand']<=1),'demand'] = 1.0
                          df_prep_avg['demand'] = df_prep_avg['demand'] + (2*std)
                          dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'MaxDailySales'}
                          df_prep_avg.rename(columns=dict_names,inplace=True)
                          df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                          df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)
                          df_invopt['Item'] = df_invopt['Item'].astype(str)
                          df_invopt['Location'] = df_invopt['Location'].astype(str)

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailySales']],on=['Item','Location'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                        else:
                          df_prep_avg = pd.DataFrame()
                          df_prep_avg['Item'] = [b]
                          df_prep_avg['Location'] = [a]
                          df_prep_avg['MaxDailySales'] = [np.NaN]

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailySales']],on=['Item','Location'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                  else:
                      for b in df_invopt['Item'].unique():
                        week_ = months_*4
                        df_prep2 = df_prep[df_prep['item_id']==b]
                        if len(df_prep2)>0:
                          df_prep_avg = df_prep2[(df_prep2[date_cols] > (df_prep2[date_cols].max() - relativedelta(months=months_))) & 
                                              (df_prep2[date_cols] <= df_prep2[date_cols].max() )]
                          std = (np.std(df_prep_avg['demand']))/ (7*week_)
                          df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                      .agg({'demand': sum})\
                                                                                      .reset_index(drop=True)
                          df_prep_avg['demand'] = (df_prep_avg['demand'] / (30*months_)) 
                          df_prep_avg.loc[(df_prep_avg['demand']>0)&(df_prep_avg['demand']<=1),'demand'] = 1.0

                          df_prep_avg['demand'] = df_prep_avg['demand'] + (2*std)
                          dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'MaxDailySales'}
                          df_prep_avg.rename(columns=dict_names,inplace=True)
                          df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                          df_invopt['Item'] = df_invopt['Item'].astype(str)

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','MaxDailySales']],on=['Item'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                        else:
                          df_prep_avg = pd.DataFrame()
                          df_prep_avg['Item'] = [b]
                          df_prep_avg['MaxDailySales'] = [np.NaN]

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','MaxDailySales']],on=['Item'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])

              elif frequency_ == 'W':
                  if location:
                    for a in df_invopt['Location'].unique():
                      df_prep1 = df_prep[df_prep['location']==a]
                      df_invopt1 = df_invopt[df_invopt['Location']==a]
                      for b in df_invopt1['Item'].unique():
                        df_prep2 = df_prep1[df_prep1['item_id']==b]
                        if len(df_prep2)>0: 
                          week_ = months_*4
                          df_prep_avg = df_prep2[(df_prep2[date_cols] > (df_prep2[date_cols].max() - relativedelta(days=7*week_))) & 
                                              (df_prep2[date_cols] <= df_prep2[date_cols].max() )]
                          std = (np.std(df_prep_avg['demand']))/ (7*week_)
                          
                          df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                              .agg({'demand': sum})\
                                                                                              .reset_index(drop=True)
                          df_prep_avg['demand'] = (df_prep_avg['demand'] / (7*week_)) 
                          df_prep_avg.loc[(df_prep_avg['demand']>0)&(df_prep_avg['demand']<=1),'demand'] = 1.0

                          df_prep_avg['demand'] = df_prep_avg['demand'] + (2*std)

                          dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'MaxDailySales'}
                          df_prep_avg.rename(columns=dict_names,inplace=True)

                          df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                          df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)

                          df_invopt['Item'] = df_invopt['Item'].astype(str)
                          df_invopt['Location'] = df_invopt['Location'].astype(str)

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailySales']],on=['Item','Location'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                        else:
                          df_prep_avg = pd.DataFrame()
                          df_prep_avg['Item'] = [b]
                          df_prep_avg['Location'] = [a]
                          df_prep_avg['MaxDailySales'] = [np.NaN]

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailySales']],on=['Item','Location'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                  else:
                      
                      for b in df_invopt['Item'].unique():
                        df_prep2 = df_prep[df_prep['item_id']==b]
                        if len(df_prep2)>0: 
                          week_ = months_*4
                          df_prep_avg = df_prep2[(df_prep2[date_cols] > (df_prep2[date_cols].max() - relativedelta(days=7*week_))) & 
                                              (df_prep2[date_cols] <= df_prep2[date_cols].max() )]
                          std = (np.std(df_prep_avg['demand']))/ (7*week_)

                          df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                      .agg({'demand': sum})\
                                                                                      .reset_index(drop=True)
                          df_prep_avg['demand'] = (df_prep_avg['demand'] / (7*week_)) 
                          df_prep_avg.loc[(df_prep_avg['demand']>0)&(df_prep_avg['demand']<=1),'demand'] = 1.0
                          df_prep_avg['demand'] = df_prep_avg['demand'] + (2*std)
                          dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'MaxDailySales'}
                          df_prep_avg.rename(columns=dict_names,inplace=True)
                          df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                          df_invopt['Item'] = df_invopt['Item'].astype(str)

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailySales']],on=['Item'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])
                        else:
                          df_prep_avg = pd.DataFrame()
                          df_prep_avg['Item'] = [b]
                          df_prep_avg['MaxDailySales'] = [np.NaN]

                          df_extract1 = pd.merge(df_invopt,df_prep_avg[['Item','MaxDailySales']],on=['Item'],how='inner')
                          df_extract = pd.concat([df_extract,df_extract1])

              df_extract['MaxDailySales'] = round(df_extract['MaxDailySales'],3)
              df_extract.loc[(df_extract['MaxDailySales']>0)&(df_extract['MaxDailySales']<=1),'MaxDailySales'] = 1.0
        
        except:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_extract

    def extract_stockout (self,df_prep, df_invopt):
        """
        Return a dataframe with addition the column StockoutDate in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit,
                                AvgDailyUsage, Availability, SecurityStock
        : return df_invopt: Dataframe with addition the column StockoutDate in the Inventory's Dataframe

        >>> df_invopt = extract_stockout (df_prep, df_invopt)
        >>> df_invopt =
                                            Item    Location   Inventory   ....     StockoutDate
                                idx0          85      905         23         ....      2021-06-01
                                idx1          102     487         95         ....      2021-06-01

        """
        try:
            timestamp = self.utls.set_timestamp()
            year = int(timestamp[0:4])
            month = int(timestamp[4:6])
            day = int(timestamp[6:8])

            df_invopt['StockoutDate'] = datetime.datetime(year, month, day)
            for a in df_invopt.index:
                if (df_invopt['AvgDailyUsage'][a] != 0):
                    b = int ((df_invopt['Availability'][a] - df_invopt['SecurityStock'][a])/(df_invopt['AvgDailyUsage'][a]))
                    if (b < 0):
                        df_invopt['StockoutDate'][a] = datetime.datetime(year, month, day)
                    else:
                        c = datetime.datetime(year, month, day) + timedelta(days=b)
                        df_invopt['StockoutDate'][a] = c
            
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_invopt

    def extract_sug_stockout (self,df_prep, df_invopt):
        """
        Return a dataframe with addition the column SuggestedStockoutDate in the Inventory's Dataframe

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, InTransit,
                                AvgDailyUsage, SuggestedAvailability, SecurityStock
        : return df_invopt: Dataframe with addition the column SuggestedStockoutDate in the Inventory's Dataframe

        >>> df_invopt = extract_sug_stockout (df_prep, df_invopt)
        >>> df_invopt =
                                            Item    Location   Inventory   ....     SuggestedStockoutDate
                                idx0          85      905         23         ....      2021-06-01
                                idx1          102     487         95         ....      2021-06-01

        """
        try:

            timestamp = self.utls.set_timestamp()
            year = int(timestamp[0:4])
            month = int(timestamp[4:6])
            day = int(timestamp[6:8])

            df_invopt['SuggestedStockoutDate'] = datetime.datetime(year, month, day)
            for a in df_invopt.index:
                if (df_invopt['AvgDailyUsage'][a] != 0):
                    b = int ((df_invopt['SuggestedAvailability'][a] - df_invopt['SecurityStock'][a])/(df_invopt['AvgDailyUsage'][a]))
                    if (b < 0):
                        df_invopt['SuggestedStockoutDate'][a] = datetime.datetime(year, month, day)
                    else:
                        c = datetime.datetime(year, month, day) + timedelta(days=b)
                        df_invopt['SuggestedStockoutDate'][a] = c
            
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            raise
        return df_invopt
    