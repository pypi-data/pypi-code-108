import time
import requests
import pandas as pd
import json
import ast
import pymongo
import datetime
from dateutil.relativedelta import relativedelta, FR


class Database:

    def __init__(self,authToken):
        self.authToken = authToken

    def get_hk_stock_ohlc(self, code, start_date, end_date, freq, price_adj=False, vol_adj=False):
        # http://localhost:8000/api/cbbc_dis?sid=0910d3e18c01f86&token=efc220c6c6da52b&date=20210802&database=cbbc_dis
        # http://localhost:8000/data_api?sid=0910d3e18c01f86&token=efc220c6c6da52b&date=20210802&database=cbbc_dis

        check_bool_dict = self.check_hk_stock_ohlc_args(code, start_date, end_date, freq)

        if False not in list(check_bool_dict.values()):
            link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_stock_ohlc'
            code_str = 'code=' + code
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            freq_str = 'freq=' + freq
            price_adj = 'price_adj=0' if price_adj == False else 'price_adj=1'
            vol_adj = 'vol_adj=0' if vol_adj == False else 'vol_adj=1'
            link_str = link_url + code_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str + '&' + freq_str + '&' + price_adj + '&' + vol_adj

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            cols = ['datetime'] + list(df.columns)
            if 'T' in freq:
                df['time'] = df['time'].astype(str)
                df['datetime'] = df['date'] + ' ' + df['time']
                df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H%M%S')
            else:
                df['datetime'] = df['date']
                df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d')

            df = df[cols]

            df = df.set_index(keys='datetime')
            df = df.sort_index()
            df = df[['open', 'high', 'low', 'close', 'volume']]
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)
    def get_us_stock_ohlc(self, code, start_date, end_date):

        check_bool_dict = self.check_us_stock_ohlc_args(code, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            # link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'spx_stock_ohlc'
            code_str = 'code=' + code
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + code_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            cols = ['datetime'] + list(df.columns)
            df['time'] = df['time'].astype(str)
            df['time'] = df['time'].str.zfill(6)
            df['datetime'] = df['date'] + ' ' + df['time']
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H%M%S')

            df = df[cols]

            df = df.set_index(keys='datetime')
            df = df.sort_index()
            df = df[['open', 'high', 'low', 'close', 'volume']]
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_hk_market_cap_hist(self, start_date, end_date):
        
        ### should change name to check_start_end_date ###
        check_bool_dict = self.check_start_end_date(start_date, end_date, 180)

        if False not in list(check_bool_dict.values()):
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_market_cap_hist'
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str

            response = requests.get(link_str)
            json_content = json.loads(response.content)
            json_content = json_content.replace(' nan', '\" nan\"')

            result = ast.literal_eval(json_content)

            df = pd.DataFrame(result)
            df = df[['date', 'code','issued_share_mil','record_date','market_cap_mil','cumulative_market_cap_mil']]
            df = df.sort_values(['date', 'market_cap_mil'], ascending=[True, False])
            df = df.reset_index(drop=True)
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_hk_buyback_by_code(self, code):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'hk_buyback_by_code'
        code_str = 'code=' + code
        link_str = link_url + code_str + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        df = pd.DataFrame(result)
        df['date'] = pd.to_datetime(df['date'], format = '%Y%m%d')
        df = df.set_index(keys='date')
        df = df.sort_index()

        return df

    def get_hk_buyback_by_date(self, start_date, end_date):

        ### should change name to check_start_end_date ###
        check_bool_dict = self.check_start_end_date(start_date, end_date, 2160)

        if False not in list(check_bool_dict.values()):

            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_buyback_by_date'
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str
            
            response = requests.get(link_str)
            json_content = json.loads(response.content)
            json_content = json_content.replace(' nan', '\" nan\"')

            result = ast.literal_eval(json_content)

            df = pd.DataFrame(result)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.set_index(keys='date')
            df = df.sort_index()
            return df
        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_hk_earning_calendar_by_code(self, code):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'hk_earning_calendar_by_code'
        code_str = 'code=' + code
        link_str = link_url + code_str + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        df = pd.DataFrame(result)
        df['datetime'] = pd.to_datetime(df['datetime'], format = '%Y-%m-%d %H:%M:%S')
        df = df.set_index(keys='datetime')
        df = df.sort_index()

        return df
    def get_hk_earning_calendar_by_date(self, start_date, end_date):

        ### should change name to check_start_end_date ###
        check_bool_dict = self.check_start_end_date(start_date, end_date)

        if False not in list(check_bool_dict.values()):
            # link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_earning_calendar_by_date'
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d%H%M%S')

            df = df.set_index(keys='datetime')
            df = df[['code','name','result']]
            df = df.sort_index()
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_us_earning_calendar_by_code(self, code):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'us_earning_calendar_by_code'
        code_str = 'code=' + code
        link_str = link_url + code_str + '&' + token_str + '&' + database_str

        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        date_list = list(result)

        return date_list
    def get_us_earning_calendar_by_date(self, start_date, end_date):
        
        ### should change name to check_start_end_date ###
        check_bool_dict = self.check_start_end_date(start_date, end_date)

        if False not in list(check_bool_dict.values()):
            #link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'us_earning_calendar_by_date'
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

            df = df.set_index(keys='date')
            df = df.sort_index()
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_ccass_by_code(self, code, start_date, end_date):

        check_bool_dict = self.check_ccass_by_code_args(code, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'ccass_by_code'
            code_str = 'code=' + code
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + code_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)
            
            df['date'] = df['date'].astype(str) 
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)
    def get_ccass_holding_rank(self, code, start_date, end_date):

        check_bool_dict = self.check_ccass_holding_rank_args(code, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'ccass_holding_rank'
            code_str = 'code=' + code
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + code_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + end_date_str

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)
            df = df.sort_values(['date', 'share'], ascending=False)
            df = df[['date', 'ccass_id', 'name', 'share', 'percent']]

            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)
    def get_ccass_all_id(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'ccass_all_id'
        link_str = link_url + '&' + token_str + '&' + database_str

        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        name_list = list(result)

        return name_list
    def get_ccass_by_id(self, ccass_id, start_date, end_date):

        check_bool_dict = self.check_ccass_by_id_args(ccass_id, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            # link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'ccass_by_id'
            ccass_id_str = 'ccass_id=' + ccass_id
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + ccass_id_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

            df = df[['date', 'percent', 'code', 'share']]
            df = df.set_index(keys='date')
            df = df.sort_index()

            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)
    def get_ccass_by_id_change(self, ccass_id, start_date, end_date):

        check_bool_dict = self.check_ccass_by_id_args(ccass_id, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            start_date_dt = datetime.datetime.strptime(str(start_date), '%Y%m%d')
            end_date_dt = datetime.datetime.strptime(str(end_date), '%Y%m%d')
            if start_date_dt.weekday() > 4:
                start_date_dt = start_date_dt + relativedelta(weekday=FR(-1))
                start_date = int(start_date_dt.strftime('%Y%m%d'))
            if end_date_dt.weekday() > 4:
                end_date_dt = end_date_dt + relativedelta(weekday=FR(-1))
                end_date = int(end_date_dt.strftime('%Y%m%d'))

            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'ccass_by_id'
            ccass_id_str = 'ccass_id=' + ccass_id
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(start_date)
            link_str = link_url + ccass_id_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df_first = pd.DataFrame(result)

            time.sleep(1)

            start_date_str = 'start_date=' + str(end_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + ccass_id_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str

            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df_last = pd.DataFrame(result)

            df_first = df_first.set_index(keys='code')
            df_last = df_last.set_index(keys='code')

            for col in df_first:
                df_first = df_first.rename(columns={col: col + '_first'})
                df_last = df_last.rename(columns={col: col + '_last'})

            df_first['date_first'] = pd.to_datetime(df_first['date_first'], format='%Y%m%d')
            df_last['date_last'] = pd.to_datetime(df_last['date_last'], format='%Y%m%d')

            df = pd.concat([df_first, df_last], axis=1)
            df['percent_chg'] = df['percent_last'] - df['percent_first']
            df['share_chg'] = df['share_last'] - df['share_first']
            df['date_diff'] = df['date_last'] - df['date_first']
            df = df.dropna()

            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_spx_index_const(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'spx_index_const'
        link_str = link_url + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        df = pd.DataFrame(result)
        df['is_active'] = df['is_active'].astype(bool) 
        df['is_delisted'] = df['is_delisted'].astype(bool) 

        return df
    def get_hk_index_const(self, index_name):
        
        if len(index_name) > 0:

            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_index_const'
            index_name_str = 'index_name=' + index_name
            link_str = link_url + index_name_str + '&' + token_str + '&' + database_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))
    
            df = pd.DataFrame(result)
            df['code'] = df['code'].str.zfill(5)
        
            return df

        else:
            err_msg =  'index_name missing'
            print(err_msg)
    def get_hk_stock_plate_const(self, plate_name):
        
        if len(plate_name) > 0:

            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'hk_stock_plate_const'
            plate_name_str = 'plate_name=' + plate_name
            link_str = link_url + plate_name_str + '&' + token_str + '&' + database_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))
    
            df = pd.DataFrame(result)
            df['code'] = df['code'].str.zfill(5)
        
            return df

        else:
            err_msg =  'index_name missing'
            print(err_msg)
    def get_all_hk_index_name(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'all_hk_index_name'
        link_str = link_url + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        name_list = list(result)

        return name_list
    def get_all_hk_stock_plate_name(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'all_hk_stock_plate_name'
        link_str = link_url + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        name_list = list(result)

        return name_list

    def get_basic_hk_stock_info(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'basic_hk_stock_info'
        link_str = link_url + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        result = ast.literal_eval(json.loads(response.content))

        df = pd.DataFrame(result)
        df['ipo_date'] = pd.to_datetime(df['ipo_date'],format='%Y-%m-%d')
        df['ipo_date'] = df['ipo_date'].astype(str)
        
        return df

    def get_hk_ipo_hist(self):

        link_url = 'http://www.hkfdb.net/data_api?'
        token_str = 'token=' + str(self.authToken)
        database_str = 'database=' + 'hk_ipo_hist'
        link_str = link_url + '&' + token_str + '&' + database_str
        
        response = requests.get(link_str)
        json_content = json.loads(response.content)
        json_content = json_content.replace(' nan', '\" nan\"')

        result = ast.literal_eval(json_content)
        df = pd.DataFrame(result)
        col_list = ['name','sponsors','accountants','valuers']
        #col_list = ['name','sponsors','accountants']
        for col in col_list: 
            df[col] = df[col].str.replace('\n',' ', regex= False)
        for col in col_list:
            for i in range(len(df)):
                content = df.loc[i,col]
                if content[-1] == ' ':
                    df.at[i,col] = content[0:-1]
                if 'Appraisaland' in content:
                    df.at[i,col] = content.replace('Appraisaland','Appraisal and')

        return df

    def get_market_highlight(self, market, start_date, end_date):

        check_bool_dict = self.check_market_highlight_args(market, start_date, end_date)

        if False not in list(check_bool_dict.values()):
            #link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'market_highlight'
            market_str = 'market=' + market
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + market_str + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.drop_duplicates(subset='date',keep='last')
            df = df.set_index(keys='date')
            df = df.sort_index()
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def get_north_water(self, start_date, end_date):

        check_bool_dict = self.check_start_end_date(start_date, end_date)

        if False not in list(check_bool_dict.values()):
            #link_url = 'http://localhost:8000/data_api?'
            link_url = 'http://www.hkfdb.net/data_api?'
            token_str = 'token=' + str(self.authToken)
            database_str = 'database=' + 'north_water'
            start_date_str = 'start_date=' + str(start_date)
            end_date_str = 'end_date=' + str(end_date)
            link_str = link_url + '&' + token_str + '&' + database_str + '&' + start_date_str + '&' + \
                       end_date_str
            
            response = requests.get(link_str)
            result = ast.literal_eval(json.loads(response.content))

            df = pd.DataFrame(result)

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

            df = df.set_index(keys='date')
            df = df.sort_index()
            return df

        else:
            err_msg = 'Error in: '
            for error in check_bool_dict:
                if check_bool_dict[error] == False:
                    err_msg += error + ','
            print(err_msg)

    def check_hk_stock_ohlc_args(self, code, start_date, end_date, freq):
        freq_list = ['1T', '5T', '15T', '30T', '1D']
        freq_valid = True if freq in freq_list else False


        try:
            code_length = len(code) == 5
        except:
            code_length = False
        try:
            code_isdigit = code.isdigit() == True
        except:
            code_isdigit = False
        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),'%Y%m%d').date() >= \
                                   datetime.datetime.strptime(str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False
        
        try:
            day_diff = (datetime.datetime.strptime(str(end_date),'%Y%m%d').date() - \
                                   datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days

            if freq == '1T':
                exceed_max_day_diff = day_diff <= 36
            elif freq == '5T':
                exceed_max_day_diff = day_diff <= 180
            elif freq == '15T':
                exceed_max_day_diff = day_diff <= 540
            elif freq == '30T':
                exceed_max_day_diff = day_diff <= 540
            elif freq == '30T':
                exceed_max_day_diff = day_diff <= 1080
            elif freq == '1D':
                exceed_max_day_diff = day_diff <= 2160
        except:
            exceed_max_day_diff = False
        
        check_bool_dict = {'freq_valid': freq_valid,
                           'code_isdigit': code_isdigit,
                           'code_length': code_length,
                           'start_date_length': start_date_length,
                           'start_date_is_int': start_date_is_int,
                           'start_date_future': start_date_future,
                           'end_date_is_int': end_date_is_int,
                           'end_date_length': end_date_length,
                           'end_date_future': end_date_future,
                           'end_after_start_date': end_after_start_date,
                           'exceed_max_day_diff': exceed_max_day_diff}
        
        return check_bool_dict
    def check_us_stock_ohlc_args(self, code, start_date, end_date):

        try:
            code_length = len(code) > 0
        except:
            code_length = False

        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),
                                                              '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False
            
        try:
            day_diff = (datetime.datetime.strptime(str(end_date), '%Y%m%d').date() - \
                        datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days
            exceed_max_day_diff = day_diff <= 36
        except:
            exceed_max_day_diff = False

        check_bool_dict = {'code_length': code_length,
                           'start_date_length': start_date_length,
                           'start_date_is_int': start_date_is_int,
                           'start_date_future': start_date_future,
                           'end_date_is_int': end_date_is_int,
                           'end_date_length': end_date_length,
                           'end_date_future': end_date_future,
                           'end_after_start_date': end_after_start_date,
                           'exceed_max_day_diff':exceed_max_day_diff}
        return check_bool_dict

    def check_market_highlight_args(self, market, start_date, end_date):
        try:
            market_length = len(market) > 0
        except:
            market_length = False
        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),
                                                              '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False

        check_bool_dict = {'market_length': market_length,
                           'start_date_length': start_date_length,
                           'start_date_is_int': start_date_is_int,
                           'start_date_future': start_date_future,
                           'end_date_is_int': end_date_is_int,
                           'end_date_length': end_date_length,
                           'end_date_future': end_date_future,
                           'end_after_start_date': end_after_start_date}
        return check_bool_dict

    def check_start_end_date(self, start_date, end_date, max_day = 9999):

        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),'%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),
                                                              '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False
        
        if max_day < 9999:
            day_diff = (datetime.datetime.strptime(str(end_date), '%Y%m%d').date() - \
                        datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days
            exceed_max_day_diff = day_diff <= max_day
        else:
            exceed_max_day_diff = True
            
        check_bool_dict = {
            'start_date_length': start_date_length,
            'start_date_is_int': start_date_is_int,
            'start_date_future': start_date_future,
            'end_date_is_int': end_date_is_int,
            'end_date_length': end_date_length,
            'end_date_future': end_date_future,
            'end_after_start_date': end_after_start_date,
            'exceed_max_day_diff':exceed_max_day_diff}
        return check_bool_dict

    def check_ccass_by_id_args(self, ccass_id, start_date, end_date):
        if len(ccass_id) > 0:
            ccass_id_len = True
        else:
            ccass_id_len = False
        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date), '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date), '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False
        
        try:
            day_diff = (datetime.datetime.strptime(str(end_date), '%Y%m%d').date() - \
                        datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days
            exceed_max_day_diff = day_diff <= 360
        except:
            exceed_max_day_diff = False

        
        check_bool_dict = {'ccass_id_len' : ccass_id_len,
                           'start_date_length': start_date_length,
                           'start_date_is_int': start_date_is_int,
                           'start_date_future': start_date_future,
                           'end_date_is_int': end_date_is_int,
                           'end_date_length': end_date_length,
                           'end_date_future': end_date_future,
                           'end_after_start_date': end_after_start_date,
                           'exceed_max_day_diff':exceed_max_day_diff}
        return check_bool_dict
    
    def check_ccass_by_code_args(self, code, start_date, end_date):

        try:
            code_length = len(code) == 5
        except:
            code_length = False
        try:
            code_isdigit = code.isdigit() == True
        except:
            code_isdigit = False
        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False
        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),
                                                              '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False

        try:
            day_diff = (datetime.datetime.strptime(str(end_date), '%Y%m%d').date() - \
                        datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days
            exceed_max_day_diff = day_diff <= 2160
        except:
            exceed_max_day_diff = False

        check_bool_dict = {
            'code_isdigit': code_isdigit,
            'code_length': code_length,
            'start_date_length': start_date_length,
            'start_date_is_int': start_date_is_int,
            'start_date_future': start_date_future,
            'end_date_is_int': end_date_is_int,
            'end_date_length': end_date_length,
            'end_date_future': end_date_future,
            'end_after_start_date': end_after_start_date,
            'exceed_max_day_diff':exceed_max_day_diff}
        
        return check_bool_dict
    def check_ccass_holding_rank_args(self, code, start_date, end_date):

        try:
            code_length = len(code) == 5
        except:
            code_length = False
        try:
            code_isdigit = code.isdigit() == True
        except:
            code_isdigit = False
        try:
            start_date_is_int = isinstance(start_date, int)
        except:
            start_date_is_int = False
        try:
            start_date_length = len(str(start_date)) == 8
        except:
            start_date_length = False
        try:
            start_date_future = datetime.datetime.strptime(str(start_date),
                                                           '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            start_date_future = False

        try:
            end_date_is_int = isinstance(end_date, int)
        except:
            end_date_is_int = False
        try:
            end_date_length = len(str(end_date)) == 8
        except:
            end_date_length = False
        try:
            end_date_future = datetime.datetime.strptime(str(end_date),
                                                         '%Y%m%d').date() <= datetime.datetime.now().date()
        except:
            end_date_future = False
        try:
            end_after_start_date = datetime.datetime.strptime(str(end_date),
                                                              '%Y%m%d').date() >= datetime.datetime.strptime(
                str(start_date), '%Y%m%d').date()
        except:
            end_after_start_date = False

        try:
            day_diff = (datetime.datetime.strptime(str(end_date), '%Y%m%d').date() - \
                        datetime.datetime.strptime(str(start_date), '%Y%m%d').date()).days
            exceed_max_day_diff = day_diff <= 360
        except:
            exceed_max_day_diff = False


        check_bool_dict = {
            'code_isdigit': code_isdigit,
            'code_length': code_length,
            'start_date_length': start_date_length,
            'start_date_is_int': start_date_is_int,
            'start_date_future': start_date_future,
            'end_date_is_int': end_date_is_int,
            'end_date_length': end_date_length,
            'end_date_future': end_date_future,
            'end_after_start_date': end_after_start_date,
            'exceed_max_day_diff':exceed_max_day_diff}

        return check_bool_dict
