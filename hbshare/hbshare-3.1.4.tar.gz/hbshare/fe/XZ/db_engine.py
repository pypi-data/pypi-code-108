import os
import pandas as pd
import datetime
from sqlalchemy import create_engine
import hbshare as hbs
from ..XZ.config import config_pfa

configuration=config_pfa.Config()

class PrvFunDB:

    def __init__(self):

        self.sql_info= configuration.DBconfig
        self.columns_name_trans = configuration.Columns_name_trans
        self.mkr_code_dic = configuration.Mkr_code

        #set up the engine
        self.engine= create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
            self.sql_info['Sql_user'], self.sql_info['Sql_pass'],
            self.sql_info['Sql_ip'], self.sql_info['port'], self.sql_info['Database']))

    def read_files_2_df(self,root_dir,dirs):

        # initial the output table
        value_table = pd.DataFrame()
        fold_dir = root_dir + "\\" + dirs
        for root, dir, files in os.walk(fold_dir, topdown=False):
            file_list = files

        # go through all the fiels in the sub folder
        for files in file_list:

            # read the file and rename the columns
            temp_excel = pd.read_excel(fold_dir + "\\" + files, header=3)

            # check if there is any regular columns missed if yes add those columns
            if (len(list(set(self.columns_name_trans.keys()).difference(set(temp_excel.columns)))) > 0):
                for col in list(set(self.columns_name_trans.keys()).difference(set(temp_excel.columns))):
                    temp_excel[col] = None

            # rename all the chinese column names
            temp_excel.rename(columns=self.columns_name_trans, inplace=True)

            # add the column  stamp date and product name based on the file names,the frequence based on data
            Stamp_date = ''.join(filter(lambda x: x.isdigit(), files.split('_')[2].split('.')[0]))

            temp_excel = temp_excel[~(temp_excel['Code'].isnull())]

            temp_excel['Stamp_date'] = datetime.datetime.strptime(Stamp_date, "%Y%m%d").date()
            temp_excel['Prd_name'] = dirs
            temp_excel['Fre'] = 'Monthly'

            # combine all the tables into one output table
            value_table = pd.concat([value_table, temp_excel], axis=0)

        return value_table

    def create_new_table(engine):

        # generate the sql for creating the table
        sql = """
        CREATE TABLE PrvFund (
                 Code  CHAR(100),
                 Name  CHAR(100),
                 Quant FLOAT,  
                 Unit_cost FLOAT,
                 Cost FLOAT,
                 Cost_weight FLOAT,
                 Price FLOAT,
                 Mkt_value FLOAT,
                 Weight FLOAT,
                 Increased_val FLOAT,
                 Trading_flg CHAR(20),
                 Currency  CHAR(20),
                 Hd_info CHAR(100),
                 Ex_rate FLOAT,
                 Stamp_date timestamp ,
                 Prd_name CHAR(20),
                 Fre CHAR(20)
                 )
                 """

        # delect the will-be-creted table if exist already
        with engine.connect() as con:
            con.execute("DROP TABLE IF EXISTS PrvFund")
            con.execute(sql)

    def delete_table(self):

        # delect the will-be-creted table if exist already
        with self.engine.connect() as con:
            con.execute("DROP TABLE IF EXISTS {}".format(self.table_name))

    def write2DB(self,table_name,fold_dir,increment):

        # self.delete_table()

        # get all the sub fold names in the root folder
        for root, dir, files in os.walk(fold_dir,topdown=False):
            dir_list = dir

        # for each sub folders  go through all the fiels in the it
        for dirs in dir_list:

            # save file data into dataframe
            Input_table = self.read_files_2_df(fold_dir,dirs)

            # if not increment out-dated data need to be deleted first
            if (increment == 0):

                # collect all the stamp_date that need to be deleted
                Date_list = Input_table['Stamp_date'].unique().astype('str')

                # set up the sql to count the number of data for the target stamp date
                count_sql = """ 
                    select count(*) as count from {0} where Prd_name= '{1}' and Stamp_date in ({2}) 
                """.format(table_name, dirs, ','.join(["'%s'" % item for item in Date_list]))
                count = pd.read_sql(sql=count_sql, con=self.engine)['count'][0]

                # if there is out-dated data
                if (count > 0):
                    delete_sql = """ 
                        delete from {0} where Prd_name= '{1}' and Stamp_date in ({2}) 
                    """.format(table_name, dirs, ','.join(["'%s'" % item for item in Date_list]))
                    with self.engine.connect() as con:
                        con.execute(delete_sql)

            # write dataframe into database
            Input_table.to_sql(table_name, self.engine, index=False, if_exists='append')

    def get_trading_date(self,date_list):

        last_date = date_list[-1].strftime('%Y%m%d')
        pre_date = (date_list[-0] - datetime.timedelta(days=30)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, last_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        calander = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        calander['isOpen'] = calander['isOpen'].astype(int).replace({0: 1, 1: 0})
        calander['isWeekEnd'] = calander['isWeekEnd'].fillna(0).astype(int)
        calander['isMonthEnd'] = calander['isMonthEnd'].fillna(0).astype(int)
        #
        trading_day_list = calander[calander['isOpen'] == 1]['calendarDate'].tolist()
        trading_day_list=[ datetime.datetime.strptime(x, "%Y%m%d").date() for x in  trading_day_list]

        return  trading_day_list

    def _shift_df_date(self,df):

        date_list = df['Stamp_date'].dropna().unique()
        trading_day_list=self.get_trading_date(date_list)

        missing_date=set(date_list).difference(set( trading_day_list))
        if(len(missing_date)>0):
            for missed_date in missing_date:
                delta_date=[x-missed_date for x in trading_day_list]
                df.loc[df['Stamp_date'] == missed_date, 'Stamp_date'] = trading_day_list[
                    [abs(x) for x in delta_date] == min([abs(x) for x in delta_date])]

        return df

    def extract_from_db(self,prd_name,columns,tablename):

        #read the table from the temp database
        sql="""
            select {0} from {1} where Prd_name= '{2}'
        """.format(columns,tablename,prd_name)
        df=pd.read_sql(sql,con=self.engine)

        #add a new columd stock_code by translating code
        df['Stock_code'] = None
        for mkr_code in self.mkr_code_dic.values():
            df=self.generate_stockcode_from_code(df,mkr_code)

        #transfor datetime format to string format
        # df['Stamp_date']=[x.strftime("%Y-%m-%d") for x in df['Stamp_date']]

        return self._shift_df_date(df)

    def read_from_db(self,sql):
        df = pd.read_sql(sql, con=self.engine)
        return  df

    def generate_stockcode_from_code(self,df,code):

        df.loc[df['Code'].str.startswith(code), 'Stock_code'] = \
        df[(df['Code'].str.startswith(code)) & (df['Code'] !=code)]['Code'] \
            .apply(lambda x: x.split(code)[1])
        return df

class HBDB:

    def __init__(self):

        self.sql_info = configuration.DBconfig
        self.columns_name_trans = configuration.Columns_name_trans
        self.jy_sql = configuration.Jy_sql

        hbs.set_token("")

    def db2df(self,sql,db='readonly'):

        data = hbs.db_data_query(db, sql, page_size=2000)
        pages=data['pages']
        data = pd.DataFrame(data['data'])
        if(pages>1):
            for page in range(2,pages+1):
                temp_data= hbs.db_data_query(db, sql, page_size=2000,page_num=page)
                data=pd.concat([data,pd.DataFrame(temp_data['data'])],axis=0)
        return data

    def extract_industry(self,sec_code=None):

        if(sec_code is None ):
            #join the table with company stock code and company industry
            #sql1 for normal stock sql2 for kechuang ban stock
            sql1= self.jy_sql['sql_indus_a']['sql'].replace('@@','')
            sql2 = self.jy_sql['sql_indus_b']['sql'].replace('@@','')
        else:
            sql1 = self.jy_sql['sql_indus_a']['sql']\
                .replace('@@', "and A.SecuCode in ("+','.join(["'%s'" % item for item in sec_code])+")")
            sql2 = self.jy_sql['sql_indus_b']['sql']\
                .replace('@@', "and A.SecuCode in (" + ','.join(["'%s'" % item for item in sec_code]) + ")")

        df1 = self.db2df(sql1)
        df2 = self.db2df(sql2)
        data=pd.concat([df1,df2],axis=0)

        #some of the stocks has multiple industries,keep the latest one row
        data = data.sort_values(by='XGRQ', ascending=False)
        data.drop_duplicates(subset=['SECUCODE', 'SECUABBR', 'COMPANYCODE'],inplace=True,keep='first')
        return data[['SECUCODE', 'SECUABBR', 'COMPANYCODE','FIRSTINDUSTRYNAME']]

    def extract_fin_info(self,sec_code=None,date_list=None):

        input_date_list=date_list.copy()
        if(input_date_list is None):
            datalistcon=''
        else:
            # date_list_str = [''.join(str(x).split('-')) for x in input_date_list]
            # sql=self.jy_sql['sql_fin_date']['sql'].format(date_list_str[0],date_list_str[-1])
            #
            # date_df=self.db2df(sql=sql,db='readonly')
            # date_df['TRADINGDAY'] = [datetime.datetime.strptime(x, "%Y-%m-%d").date() for x in
            #                       (date_df['TRADINGDAY'].apply(lambda x: x[0:10]))]
            # missing_date=list( set(input_date_list).difference(set(date_df['TRADINGDAY'])) )
            #
            # for date in missing_date:
            #     date_delta =date_df['TRADINGDAY'] - date
            #     input_date_list[input_date_list==date]=date_df['TRADINGDAY'][date_delta.abs()==date_delta.abs().min()]
            #
            # input_date_list=list(set(input_date_list))
            date_list_str=[''.join(str(x)) for x in input_date_list]
            datalistcon="and a.TradingDay in ({})".format(','.join([ "to_date('"+x+"', 'yyyy-mm-dd')" for x in date_list_str]) )

        if(sec_code is None ):
            #join the table with company stock code and company industry
            sql = self.jy_sql['sql_fin']['sql'].replace('@@','')+datalistcon
        else:
            #filter the sql by security code range
            sql = self.jy_sql['sql_fin']['sql']\
                .replace('@@', "where b.SecuCode in (" + ','.join(["'%s'" % item for item in sec_code])+")")\
                  +datalistcon

        data=self.db2df(sql)

        # transfor tradingday format from yyyy-mm-dd hh-mm-ss to yyyy-mm-dd
        data['TRADINGDAY'] = [datetime.datetime.strptime(x, "%Y-%m-%d").date() for x in
                             (data['TRADINGDAY'].apply(lambda x: x[0:10]))]

        return data

    def extract_benchmark(self,benchmark_dict,sec_code=None,date_list=None):

        input_date_list=date_list.copy()
        if(input_date_list is None):
            datacond=''
        else:
            date_list_str = [''.join(str(x).split('-')) for x in input_date_list]
            datacond=" and ENDDATE>= to_date('{0}','yyyymmdd') and ENDDATE <=to_date('{1}','yyyymmdd') " .format(date_list_str[0], date_list_str[-1])


        if(sec_code is None ):
            sql = self.jy_sql['sql_benchmark']['sql'].replace('@@','')
        else:
            #filter the sql by security code range
            sql =self.jy_sql['sql_benchmark']['sql']\
                .replace('@@', "and b.SecuCode in (" + ','.join(["'%s'" % item for item in sec_code])+")")

        data=pd.DataFrame()
        for benchmarks in benchmark_dict.keys():
            sql2 = "SELECT INNERCODE FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(benchmark_dict[benchmarks])
            innercode = self.db2df(sql2)['INNERCODE'][0]
            tempdata=self.db2df(sql.replace('@IndexCode',str(innercode))+datacond)
            tempdata['Index_type']=benchmarks
            data=pd.concat([data,tempdata],axis=0)

        # transform tradingday format from yyyy-mm-dd hh-mm-ss to yyyy-mm-dd
        data['ENDDATE'] = [datetime.datetime.strptime(x, "%Y-%m-%d").date() for x in
                             (data['ENDDATE'].apply(lambda x: x[0:10]))]

        return data

    def extract_factors(self,sec_code,date_list,industry=False):

        # sql = """
        # select distinct( trade_date ) from st_ashare.r_st_barra_style_factor
        # where trade_date>= '{0}' and trade_date<= '{1}'
        # """.format(date_list[0],date_list[-1])
        #
        # available_date=self.db2df(sql, db='alluser')

        date_list=[''.join(x.split('-')) for x in date_list.astype(str)]
        # miss_date=set( date_list ).difference(set(available_date['trade_date']))
        #
        # for date in miss_date:
        #     date_delta = datetime.date(date_list) - datetime.date(date)
        #     date_list[date_list == date] = date_list[date_delta.abs() == date_delta.abs().min()]

        industry_col=['aerodef','agriforest','auto','bank','builddeco','chem','conmat','commetrade','computer','conglomerates',
                      'eleceqp','electronics','foodbever','health','houseapp','ironsteel','leiservice','lightindus',
                      'machiequip','media','mining','nonbankfinan','nonfermetal',
                    'realestate','telecom','textile','transportation','utilities']

        if(industry==True):
            industry_con=','+','.join(industry_col)
        else:
            industry_con=''

        sql="""
        select ticker,trade_date,size,beta,momentum,resvol,btop,sizenl,liquidity,earnyield,growth,leverage{2}
        from st_ashare.r_st_barra_style_factor where ticker in ({0}) and trade_date in ({1})
        """.format(','.join(sec_code),"'" + "','".join(date_list) + "'",industry_con)
        raw_factors = self.db2df(sql, db='alluser')

        if(industry==True):
            raw_factors[industry_col]=raw_factors[industry_col].astype(float)
            for col in industry_col:
                if(raw_factors[col].sum()==0):
                    raw_factors.drop(col,axis=1,inplace=True)

        return raw_factors

    def extract_benchmark_return(self,date_list,index_list):

        index_con="'"+"','".join(index_list)+"'"

        sql="""
        select ZQDM,TJYF,HB from funddb.T_FU_GG_ZSHB_M   
        where ZQDM in ({1}) and TJYF in ({0})
        """.format(','.join([ x[0:6] for x in [''.join(x.split('-')) for x in date_list.astype(str)]]),index_con)
        factors_benchmark=self.db2df(sql,'readonly')

        return  factors_benchmark