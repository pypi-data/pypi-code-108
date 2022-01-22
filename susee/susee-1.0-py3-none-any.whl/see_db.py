# -*- coding: utf-8 -*-
##############################
##### DATABASE Functions  ####
##############################
# Studio Tecnico Pugliautomazione - Monopoli (BA)
# Copyright (c)
# v2.0 2020-07-03
# v2.1 2020-07-22
# v2.2 2020-09-19
# v2.3 2020-12-27
# v2.4 2020-12-27 fixed exec_sql1
# v2.5 2021-02-15
# v2.6 2021-02-22
# v2.6 2021-02-23 fixed seeAdmin
# v2.7 2021-02-28
# v2.8 2021-05-04
# v3.0 2021-05-12  Table_read
# v3.1 2021-05-15
# v3.2 2021-05-17
# v3.3 2021-06-08
# v3.4 2021-07-05


from datetime import timedelta, datetime
import mysql.connector
import os
import pandas as pd

from susee.see_comm import internet2
from susee.see_dict import message_strings, err_code
from susee.see_functions import time_utc, push_log, utctime_to_tZone, tZone_to_utctime, time_local

# GLobal variables

###########################################################
class seedatadb:
    def __init__(self, configMysql, *args, **kwargs):
        self.configMysql = configMysql

        #Write array
        self.array_sql =[]
        #self.tempdf = pd.DataFrame()  #used to temp store df for .csv file
        #self.dfDevPar = pd.DataFrame()  # used to temp store df for SysRawData

        # check socket if available. 1=ok, -1=none
        self.db_connect = internet2()

    #Tools
    def exec_sql1(self,  sql, _bresult):
        # _bresult : flag used to specify if result are needed from db
        #  2019-10-31  - version with always two outputs used only in svuota_file_array()
        #              - exec_sql() deleted
        # v2.0 2020-08-04 -fixed bugs
        # v2.1 2020-12-02 - declared out_sql
        # v2.2 2020-12-03 - flag output
        # v2.3 2021-02-02 - timeout

        config_mysql = self.configMysql

        flag_db = False
        out_sql = []

        # TImeout [s]
        try:
            mcT_ = config_mysql['maxConnectTime']
        except:
            mcT_ = 1000

        #SQL timeout
        #sql = "SET STATEMENT max_statement_time=" + str(msT_) + ' for ' + sql

        try:
            cnx = mysql.connector.connect(user=config_mysql['user'],
                                          passwd=config_mysql['passwd'],
                                          host=config_mysql['host'],
                                          port=config_mysql['port'],
                                          database=config_mysql['database'],
                                          connect_timeout=mcT_,
                                          )
            cursor = cnx.cursor()
            cursor.execute(sql)
            flag_db = True
        except mysql.connector.Error as err:
            push_log('exec_sql1() - ' + message_strings[9] + '\n err: ' + str(err) + '\n sql: ' + sql)   # 'msg_09 - Database MYSQL non accessibile.'
            print('> exeq_sql1() -  DataBase Error: ',err)
            print('> exeq_sql1() -  sql: ', sql)
            return flag_db, str(err)

        if _bresult == False:
            cnx.commit()
            cnx.close()
            cursor.close()
            return flag_db, '0'
        else:
            out_sql = cursor.fetchall()
            cnx.close()
            cursor.close()
            try:
                len(out_sql)>0
                flag_db = True
            except:
                pass

            return out_sql, '0'

    #Table seeLast (last sampled data)
    def dataDB_seeLast_Clear(self):
        # Delete the last sampled data in the table seeJOBLast
        # v2.0
        # 2020-03-21
        # rename the default tableName
        # v2.1 2020-07-02

        sql = 'DELETE  FROM %s where idNum>0' % (self.configMysql['tableLast'])
        err_ = ''

        if self.db_connect:
            flag_db, _ = self.exec_sql1(sql, 0)
            return flag_db
        else:
            str_ = 'dataDelete_Last() - no web connection'
            push_log(str_)
            return 0
    def dataDB_seeLast_write(self, dataPack, flag_tZone=False or None):
        # Store data in the seeLast Table
        # v1.1 2020-04-02 - do not activate flag_tzone!
        # v1.2 2020-07-02
        # v1.3 2021-01-06

        dataPack_ = dataPack
        # Clear Table
        self.dataDB_seeLast_Clear()

        # Local config table
        # TimeZone
        if flag_tZone:
            tZone = self.configMysql['tZone']  # timezone utctime_to_tZone(date_[0], self.configMysql['tZone'] )
            if tZone != '':
                for xx in range(len(dataPack_)):
                    for ii in range(len(dataPack_[xx])):
                        date_ = [y for x, y in dataPack_[xx][ii].items() if x == 'Date']
                        dataPack_[xx][ii]['Date'] = utctime_to_tZone(date_[0], tZone)

        return self.data_store_pack(dataPack_, self.configMysql['tableLast'] )
    def dataDB_seeLast_read(self, idDevice, idParam):
        #Reads actual data
        # v2.0 2020-07-07

        sql_ = "select date, idDevice, idParam, value,  Code, Delay  from {0}.{1}  where idDevice='{2}' and idParam= '{3}'; ".format(
            self.configMysql['database'],
            self.configMysql['tableLast'],
            idDevice,
            idParam)

        if idDevice == 'All':
            sql_ = sql_.replace('idDevice=', 'idDevice!=')

        if idParam=='All':
            sql_ = sql_.replace('idParam=', 'idParam!=')

        if self.db_connect:
            out_, _ = self.exec_sql1(sql_, True)  # format [(par1, par2,...)]
        else:
            str_ = '[msg] dataDB_seeLast_read() - no web connection'
            push_log(str_)

        db_1 = pd.DataFrame(data=out_,
                            columns=['DateTime', 'idDevice', 'idParam', 'Value', 'Code', 'Delay'],
                            )
        return db_1

    #Tables read
    def dataDB_Table_read(self, tableName):
        # Reads  a generic table data and creates a Dataframe
        # v1.1 2021-05-12

        # sql1 = 'INSERT INTO {0}.{1} {2} '.format(self.configMysql['database'], tableName, tuple(df.columns))
        err = ''

        # Reads Data from the table
        sql_ = 'select * from {0}.{1}'.format(self.configMysql['database'], tableName)
        sql_ = sql_.replace("'", '')
        try:
            data_, err = self.exec_sql1(sql_, True)
        except:
            return [], err

        # Reads Column names from the table
        sql_ = 'show columns from {0}.{1}'.format(self.configMysql['database'], tableName)
        sql_ = sql_.replace("'", '')
        try:
            temp_, err = self.exec_sql1(sql_, True)
            cols_ = [x[0] for x in temp_]
        except:
            return [], err

        # Creates Dataframe
        df = pd.DataFrame(data=data_, columns=cols_)

        # Drop idNum
        try:
            df.drop(columns='idNum', inplace=True)
        except:
            pass
        return df, cols_
    def dataDB_seeRaw_read(self, load_data):
        #
        # Reads Data from RAW Table
        # Input
        #       idDev: str or list of str
        #       idPars: str or list of str
        # returns dataFrame
        # v1.9 2018-08-21
        # v2.0 2021-05-15

        config_mysql = self.configMysql
        if isinstance(load_data['idDev'],list):
            if len(load_data['idDev'])==1:
                load_data['idDev'] = load_data['idDev'][0]

        if isinstance(load_data['idPars'],list):
            if len(load_data['idPars'])==1:
                load_data['idPars'] = load_data['idPars'][0]


        list_idDevs = tuple(load_data['idDev']) if isinstance(load_data['idDev'],list) else "('"+load_data['idDev']+"')"
        list_idParams = tuple(load_data['idPars']) if isinstance(load_data['idPars'],list) else "('"+load_data['idPars']+"')"

        # Translate local dates to utc
        if load_data['tZone']:
            startDate = tZone_to_utctime(load_data['startDate'],load_data['tZone'])
            endDate =   tZone_to_utctime(load_data['endDate'],load_data['tZone'])
        else:
            startDate =  load_data['startDate']
            endDate =  load_data['endDate']

        # SQL
        sql_ = ' Select Date, idDevice, idParam, Value, Code, Delay  '
        sql_ += 'from {}.{} '.format(load_data['database'], load_data['table'])
        sql_ += 'where idDevice in {} and idParam in {} '.format(list_idDevs, list_idParams)
        sql_ += "and Date between '{}' AND '{}' ".format(startDate, endDate)
        #sql_ += 'order by Date asc; '

        try:
            df, err = self.exec_sql1(sql_, True)
            df = pd.DataFrame(data=df,
                                columns=['DateTime', 'idDevice', 'idParam', 'Value', 'Code', 'Delay'],
                                )

            df.set_index('DateTime', inplace=True)
            df.index.name = 'DateTime'
            err+=' ' +sql_
        except:
            db = pd.DataFrame()
            err = '[msg] dataDB_seeRaw_read() - no connection with DB available. sql_:' + sql_

        return df, err

    def dataDB_seeParams_read(self, idParam):
        # Reads Parameters Table data
        # v1.0 2020-07-07

        sql_ = "select  idParam, descrLANG, um, Acronimo from {0}.{1}  " \
               "where idParam='{2}'; ".format(
            self.configMysql['database'],
            self.configMysql['tableParams'],
            idParam)

        sql_ = sql_.replace('descrLANG', 'descr'+self.configMysql['language'])

        if idParam == 'All':
            sql_ = sql_.replace('idParam=', 'idParam!=')

        if self.db_connect:
            out_, _ = self.exec_sql1(sql_, True)  # format [(par1, par2,...)]
        else:
            str_ = '[msg] dataDB_seeParams_read() - no web connection'
            push_log(str_)

        db_1 = pd.DataFrame(data=out_,
                            columns=['idParam', 'paramDescr', 'um','Acronimo'],
                            )

        return db_1
    def dataDB_seeMac_read(self, idMac):
        # Reads MAchine  Table data
        # v1.0 2020-07-07

        sql_ = "select  idMac, descrLANG  from {0}.{1}  " \
               "where idMac= '{2}'; ".format(
            self.configMysql['database'],
            self.configMysql['tableMac'],
            idMac)

        sql_ = sql_.replace('descrLANG', 'descr'+self.configMysql['language'])

        if idMac == 'All':
            sql_ = sql_.replace('idMac=', 'idMac!=' )

        if self.db_connect:
            out_, _ = self.exec_sql1(sql_, True)  # format [(par1, par2,...)]
        else:
            str_ = '[msg] dataDB_seeParams_read() - no web connection'
            push_log(str_)

        db_1 = pd.DataFrame(data=out_,
                            columns=['idMac', 'machDescr'],
                            )
        return db_1
    def dataDB_seeDep_read(self, idDep):
        # Reads Departments  Table data
        # v1.0 2020-07-07

        sql_ = "select  idDep, descrLANG  from {0}.{1}  " \
               "where idDep='{2}'; ".format(
            self.configMysql['database'],
            self.configMysql['tableDeps'],
            idDep)

        sql_ = sql_.replace('descrLANG', 'descr'+self.configMysql['language'])

        if idDep == 'All':
            sql_ = sql_.replace('idDep=', 'idDep!=')

        if self.db_connect:
            out_, _ = self.exec_sql1(sql_, True)  # format [(par1, par2,...)]
        else:
            str_ = '[msg] dataDB_seeDep_read() - no web connection'
            push_log(str_)

        db_1 = pd.DataFrame(data=out_,
                            columns=['idDep', 'depDescr'],
                            )
        return db_1
    def dataDB_seeSysRaw_read(self, type):
        # Reads table System Raw Data
        # v1.0 2020-10-25
        # v2.0 2021-05-12

        if type == 'Raw':
            table_ = self.configMysql['tableSysRaw']

        elif type == 'Prod':
            table_ = self.configMysql['tableSysProdw']

        if self.db_connect:
            db_1, _ = self.dataDB_Table_read(self.configMysql['tableSysRaw'])
        else:
            db_1 = pd.DataFrame([0])
            push_log(str_)

        return db_1

    def pivotRead_RawData(self, load_data):
        # Pivot table from RAW data
        # v1.0 2020-11-06
        # v1.1 2020-11-23
        # v2.0 2021-05-15  tz_localize, dataDB_seeRaw_read

        err= ''
        #Read RAW Data
        df, err = self.dataDB_seeRaw_read(load_data)

        if len(df)==0:
            print(err)
            return pd.DataFrame(), err

        # Creates Field idDev_idParam
        df['idxPar'] = df['idDevice'] + '_' + df['idParam']

        # Adapt DateTime to timezone
        if load_data['tZone']:
            #deltaTime = ((utctime_to_tZone(datetime.now(),load_data['tZone']) - datetime.now()).seconds + 1) // 3600  # deltatime in hours
            #df.index = df.index.to_series().apply(lambda x: x + timedelta(hours=deltaTime))  # update datetime
            #df['DateTime'] = df['DateTime'].apply(lambda x: utctime_to_tZone(x, tZone))  # Pivot Columns names: device_param
            df.index = df.index.tz_localize('utc').tz_convert(load_data['tZone'])
            df.reset_index(inplace=True)
            df['DateTime'] = df['DateTime'].apply(lambda x: x.replace(tzinfo=None))
            df = df.set_index('DateTime')

        #Code for not sampled data
        error_code = err_code['server_off']
        #Todo: include server_off error in Code
        #df.update(df[df['idDevice'].isna()].loc[:, 'idDevice'].fillna(value=load_data['idDev']))
        #df.update(df[df['idParam'].isna()].loc[:, 'idParam'].fillna(value=load_data['idPars']))
        #df.update(df[df['Code'].isna()].loc[:, 'Code'].fillna(value=error_code))


        # Pivot Table
        df1=df
        if load_data['code'] != '':
            df1 = df1[df1['Code'] == load_data['code']]
        # Shift time
        if load_data['shiftStep'] != 0:
            df1.index = df1.index.to_period(load_data['timeStep']) + load_data['shiftStep']
            df1.index = df1.index.to_timestamp(load_data['timeStep'])  # riconversione index in timestamp per plot

        df1 = df1[~df1.index.duplicated(keep='first')]
        pivot_ = df1.reset_index().pivot(
                          index='DateTime',
                          columns='idxPar',
                          values='Value')

        if load_data['timeStep'] != '0t':
            pivot_=pivot_.resample(load_data['timeStep']).max()

        # Drops duplicated  - filter for DST time shifts
        #pivot_ = pivot_[~pivot_.index.duplicated(keep='first')]
        #pivot_.dropna(inplace=True)

        # df index DateTime
        pivot_.index.name = 'DateTime'
        pivot_.columns.name=''

        return pivot_, df1

    #Table Write
    def dataDB_Table_write(self, df, tableName):
        # Writes a Dataframe  to a generic table
        # v1.1 2020-10-20

        # Drop idNum
        try:
            df.drop(columns='idNum', inplace=True)
        except:
            pass

        sql1 = 'INSERT INTO {0}.{1} {2} '.format(self.configMysql['database'], tableName, tuple(df.columns))
        sql1 = sql1.replace("'", '')

        sql2 = 'VALUES {};'.format(tuple(map(tuple,df.to_numpy())))
        sql2 = sql2.replace('((', '(')
        sql2 = sql2.replace('))', ')')
        sql2 = sql2.replace('),);', ');')
        sql2
        sql1 += sql2

        flagdb, err = self.exec_sql1(sql1, 0)

        return flagdb, err
    def dataDB_seeProd_write(self, df, date_format='%d/%m/%Y %H:%M' or None, UTC_flag=False):
        # Writes a Dataframe  to the Production  seetable
        # Options: time utc conversion, date format adjiustment
        # Table fields = ('Date', 'Value', 'idProd', 'idMac', 'idParam', 'Code')
        # v1.0 2020-07-12
        # v1.1 2021-04-23
        # 2021-05-12 - Todo: upgrade

        database_= self.configMysql['database']
        table_   = self.configMysql['tableProd']

        # Drop idNum
        try:
            df.drop(columns='idNum', inplace=True)
        except:
            pass

        if UTC_flag:
            # Date format is 26/03/2020 23:03
            # Convert Datetime from local time string format   to utc Datetime format
            df['Date'] = df['Date'].apply(
                lambda x: tZone_to_utctime(datetime.strptime(x, date_format),self.configMysql['tZone'])
                )
        flag_, err = self.dataDB_Table_write(df, table_)
        return flag_, err
    def dataDB_seeRaw_write(self, df, date_format='%d/%m/%Y %H:%M' or None, time_to_utc=False ):
        # Writes a Dataframe  to the Raw Data  seetable
        # Table fields = ('Date', 'idDevice', 'idParam', 'Code','Delay', 'Value')
        # v1.0 2020-07-12
        # v1.1 2021-05-12

        database_= self.configMysql['database']
        table_   = self.configMysql['tableRaw']
        # Drop idNum
        df.drop(columns='idNum', inplace=True)

        # Date format is 26/03/2020 23:03
        # Convert Datetime from local time string fromat   to utc Datetime format

        if time_to_utc:
            df['Date'] = df['Date'].apply(lambda x: tZone_to_utctime(
                datetime.strptime(x, date_format),
                self.configMysql['tZone']
            ))
        else:
            df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, date_format))

        flagdb, _ = self.dataDB_Table_write(df, table_)

        return flagdb

    #Production Data
    def dataDB_Prod_Article(self):
        # Collects data about production of articles
        # v1.0 2021-05-12
        # v1.1 2021-05-13


        # 1. Extract production resources
        # 2. Filter on article
        config_mysql = self.configMysql
        #Join Table Names
        t_jArtJob = config_mysql['tablejArtJob']
        t_jJobDep = config_mysql['tablejJobDep']
        t_jDepMac = config_mysql['tablejDepMac']
        t_jMacDev = config_mysql['tablejMacDev']
        #t_Articoli = config_mysql['tableArt']   # idArt, idParams, Description


        # METHOD Merge tables 1 - merge tables
        if False:
            # Read table contents
            ArtJob = c001.dataDB_Table_read(t_jArtJob)[0]
            JobDep = c001.dataDB_Table_read(t_jArtJob)[0]
            DepMac = c001.dataDB_Table_read(t_jDepMac)[0]

            tableArt
            df0 = pd.merge(ArtJob, JobDep, how='left', on='idJob')
            df0 = pd.merge(df0, DepMac, how='left', on='idDep')
            df0 = pd.merge(df0, MacDev, how='left', on='idMac')


        # METHOD Merge tables 2 - sql
        cols_ = 'idArt,{0}.idJob,{1}.idDep,DateStart,DateEnd,{2}.idMac,sign,idDevice'.format(t_jJobDep,t_jDepMac, t_jMacDev, t_jArtJob )
        from_ = ' FROM {3} LEFT JOIN ({0}, {1},{2})'.format(t_jJobDep,t_jDepMac, t_jMacDev , t_jArtJob )
        on_ = ' ON ({0}.idJob={3}.idJob AND {1}.idDep={0}.idDep AND {2}.idMac={1}.idMac)'.format(t_jJobDep,t_jDepMac, t_jMacDev , t_jArtJob )
        #where_ = ' where idArt = {}'.format(article)

        sql_ = 'SELECT '+cols_+ from_ + on_ #+ where_
        columns_ = ['idArt', 'idJob', 'idDep', 'DateStart', 'DateEnd', 'idMac', 'sign', 'idDevice']
        dbjArt, _  = self.exec_sql1(sql_, True)
        artTable = pd.DataFrame(data=dbjArt, columns=columns_)

        '''
            artTable 	
            
               idArt  idJob  idDep  DateStart    DateEnd              idMac sign idDevice
            0   Art1   Job1  dep01 2021-04-25 2021-04-30       Forno_Cucina    +      d01
            1   Art1   Job1  dep01 2021-04-25 2021-04-30         Forno_Tunn    +      d09
            2   Art1   Job1  dep01 2021-04-25 2021-04-30          Gen_Forno    -      d07
            3   Art1   Job2  dep02 2021-02-01 2021-02-28  Celle_Evaporatori    +      d03
            4   Art1   Job2  dep02 2021-02-01 2021-02-28        Sala_Motori    +      d02
            5   Art1   Job3  dep03 2021-03-01 2021-03-31          Farcitura    +      d04
            6   Art1   Job3  dep03 2021-03-01 2021-03-31      Gen_Farcitura    +      d08
            7   Art1   Job3  dep03 2021-03-01 2021-03-31         Imballatri    +      d05
            8   Art2   Job4  dep04 2021-04-01 2021-04-10             Uffici    +      d06
            9   Art2   Job5  dep05 2021-04-11 2021-04-20  Celle_Evaporatori    -      d03
            10  Art2   Job5  dep05 2021-04-11 2021-04-20          Farcitura    -      d04
            11  Art2   Job5  dep05 2021-04-11 2021-04-20       Forno_Cucina    -      d01
        '''
        return artTable

    #Pivot from tables
    def pivotTable_rescale_old(self, loadData):
        # read data from db with
        # timestep, shiftvalue NullValue
        # v3.0 2019-01-02 -   timezone conversion from UTC to tZone,
        #                    filter for DST timeshift,
        #                    Code filter
        #                    Columns name: idDev_idParam
        #
        # loadData= format_loadData(load_data)
        #     if loadData['error']:
        #         return loadData['error'], ''
        # v4.0 2020-07-03
        # v4.1 2020-07-19 fixed endDate

        startDate = loadData['startDate']
        endDate =   loadData['endDate']
        timeStep =  loadData['timeStep']
        shiftStep = loadData['shiftStep']
        NullValue = loadData['NullValue']
        tZone =     loadData['tZone'] or None
        code =      loadData['code']


        if tZone != '':
            # one day back to keep around midnight  time
            if isinstance(startDate, str):
                loadData['startDate'] = (datetime.strptime(startDate, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                loadData['startDate'] = startDate - timedelta(days=1)

            if isinstance(endDate, str):
                loadData['endDate'] = (datetime.strptime(endDate, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                loadData['endDate'] = endDate + timedelta(days=1)

        ##### READS DATA  ###
        ck_Prod = loadData['table'] == self.configMysql['tableProd']
        if ck_Prod:
            df = self.dataDB_seeProd_read(loadData)
            df['idxPar'] = df['idMac'] + '_' + df['idParam']
        else:
            df = self.dbRead_pars(loadData)
            df['idxPar'] = df['idDevice'] + '_' + df['idParam']


        # Adapt DateTime to timezone
        df = df.set_index('DateTime')
        if tZone:
            deltaTime = ((utctime_to_tZone(datetime.now(),tZone) - datetime.now()).seconds + 1) // 3600  # deltatime in hours
            df.index = df.index.to_series().apply(lambda x: x + timedelta(hours=deltaTime))  # update datetime
            #df['DateTime'] = df['DateTime'].apply(lambda x: utctime_to_tZone(x, tZone))  # Pivot Columns names: device_param

        DT_Stream = pd.date_range(loadData['startDate'], loadData['endDate'], freq = timeStep)
        DT_Stream = pd.DataFrame(data=DT_Stream, columns=['DateTime'])
        DT_Stream=DT_Stream.set_index('DateTime')

        #Merge
        df = pd.merge(DT_Stream, df, how='left', right_index=True, left_index=True)

        #Code for not sampled data
        error_code = err_code['server_off']
        idDev = loadData['idDev']
        idPar = loadData['idPars']
        error_code = err_code['server_off']
        df.update(df[df['idDevice'].isna()].loc[:, 'idDevice'].fillna(value=idDev))
        df.update(df[df['idParam'].isna()].loc[:, 'idParam'].fillna(value=idPar))
        df.update(df[df['Code'].isna()].loc[:, 'Code'].fillna(value=error_code))


        # Pivot Table
        df1=df
        if code != '':
            df1 = df1[df1['Code'] == code]
        # Shift time
        if shiftStep != 0:
            df1.index = df1.index.to_period(timeStep) + shiftStep
            df1.index = df1.index.to_timestamp(timeStep)  # riconversione index in timestamp per plot

        #df1 = df1[~df1.index.duplicated(keep='first')]
        pivot_ = df1.reset_index().pivot(
                          index='DateTime',
                          columns='idxPar',
                          values='Value')

        # Drops duplicated  - filter for DST time shifts
        #pivot_ = pivot_[~pivot_.index.duplicated(keep='first')]
        # pivot_.dropna(inplace=True)

        # df index DateTime
        pivot_.index.name = 'DateTime'
        pivot_.columns.name=''

        return pivot_, df

    def pivotTable_rescale_old(self, loadData):
        # read data from RAW Table db with
        # timestep, shiftvalue NullValue
        # v3.0 2019-01-02 -   timezone conversion from UTC to tZone,
        #                    filter for DST timeshift,
        #                    Code filter
        #                    Columns name: idDev_idParam
        #
        # loadData= format_loadData(load_data)
        #     if loadData['error']:
        #         return loadData['error'], ''
        # v4.0 2020-07-03
        # v4.1 2020-07-19 fixed endDate
        # v4.2 2021-05-15

        startDate = loadData['startDate']
        endDate =   loadData['endDate']
        timeStep =  loadData['timeStep']
        shiftStep = loadData['shiftStep']
        NullValue = loadData['NullValue']
        tZone =     loadData['tZone'] or None
        code =      loadData['code']

        #if tZone != '':
            # one day back to keep around midnight  time
            #if isinstance(startDate, str):
            #    loadData['startDate'] = (datetime.strptime(startDate, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            #else:
            #    loadData['startDate'] = startDate - timedelta(days=1)

        if isinstance(endDate, str):
            loadData['endDate'] = (datetime.strptime(endDate, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            loadData['endDate'] = endDate + timedelta(days=1)

        ##### READS DATA  ###
        #df = self.dbRead_pars(loadData)
        df, err = self.dataDB_seeRaw_read(loadData)
        df['idxPar'] = df['idDevice'] + '_' + df['idParam']

        if tZone:
            deltaTime = ((utctime_to_tZone(datetime.now(),tZone) - datetime.now()).seconds + 1) // 3600  # deltatime in hours
            df.index = df.index.to_series().apply(lambda x: x + timedelta(hours=deltaTime))  # update datetime
            #df['DateTime'] = df['DateTime'].apply(lambda x: utctime_to_tZone(x, tZone))  # Pivot Columns names: device_param

        DT_Stream = pd.date_range(loadData['startDate'], loadData['endDate'], freq = timeStep)
        DT_Stream = pd.DataFrame(data=DT_Stream, columns=['DateTime'])
        DT_Stream=DT_Stream.set_index('DateTime')

        #Merge
        df = pd.merge(DT_Stream, df, how='left', right_index=True, left_index=True)

        #Code for not sampled data
        error_code = err_code['server_off']

        #Check one device and one param
        ck_Prod = False
        if ck_Prod:
            for x in enumerate([loadData['idMac'], loadData['idPars']]):
                if isinstance(x[1], list):
                    if len(x[1]) == 1:
                        ck_ = True
                    else:
                        ck_ = False
                elif isinstance(x[1], str):
                    ck_ = True
            if ck_:
                idMac = loadData['idMac']
                idPar = loadData['idPars']
                error_code = err_code['server_off']
                df.update(df[df['idMac'].isna()].loc[:, 'idMac'].fillna(value=idMac))
                df.update(df[df['idParam'].isna()].loc[:, 'idParam'].fillna(value=idPar))
                df.update(df[df['Code'].isna()].loc[:, 'Code'].fillna(value=error_code))
        else:
            for x in enumerate([loadData['idDev'], loadData['idPars']]):
                if isinstance(x[1], list):
                    if len(x[1]) == 1:
                        ck_ = True
                    else:
                        ck_ = False
                elif isinstance(x[1], str):
                    ck_ = True
            if ck_:
                idDev = loadData['idDev']
                idPar = loadData['idPars']
                error_code = err_code['server_off']
                df.update(df[df['idDevice'].isna()].loc[:, 'idDevice'].fillna(value=idDev))
                df.update(df[df['idParam'].isna()].loc[:, 'idParam'].fillna(value=idPar))
                df.update(df[df['Code'].isna()].loc[:, 'Code'].fillna(value=error_code))


        # Pivot Table
        df1=df
        if code != '':
            df1 = df1[df1['Code'] == code]
        # Shift time
        if shiftStep != 0:
            df1.index = df1.index.to_period(timeStep) + shiftStep
            df1.index = df1.index.to_timestamp(timeStep)  # riconversione index in timestamp per plot

        #df1 = df1[~df1.index.duplicated(keep='first')]
        pivot_ = df1.reset_index().pivot(
                          index='DateTime',
                          columns='idxPar',
                          values='Value')

        # Drops duplicated  - filter for DST time shifts
        #pivot_ = pivot_[~pivot_.index.duplicated(keep='first')]
        # pivot_.dropna(inplace=True)

        # df index DateTime
        pivot_.index.name = 'DateTime'
        pivot_.columns.name=''

        return pivot_, df


    #Backup mngt
    def reload_filebackup(self , **kwargs):
        # Check and reload data in temp file/array __mysql
        # 2019-07-20  fixed stop connect to DB if first attempt fails
        # 2019-07-20  execute_sql() in place of push_db()
        # 2019-08-27  fixed filename - like push_file()
        # v2.0 2020-07-03
        # v2.1 2020-07-19 fixed configMySql
        # v3.0 2020-09-19 if h>0


        config_mysql_bk = self.configMysql['config_mysql_bk']

        filename = config_mysql_bk['filename']

        try:
            oldText = kwargs['oldText']
            newText = kwargs['newText']
        except:
            oldText=''
            newText=''
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
        except:
            #print('[msg] reload_filebackup() - file {} not available'.format(filename))
            #push_log('[msg] reload_filebackup() - file {} not available'.format(filename))
            pass
        else:
            h = min(config_mysql_bk['max_rows_reload'], len(lines))

            # Svuota file
            msg_file = 'reload_filebackup()'
            idLine = 0

            if h>0:
                for x in range(h):
                    sql_ = lines[idLine]
                    sql_ = sql_.replace(oldText, newText)

                    #print('oldText: ', oldText)
                    #print('newText: ', newText)
                    #print('> sql_: ', sql_[:200])
                    flag_db, err = self.exec_sql1(sql_, False)
                    str_ = str(err + '\n sql: ' + sql_)
                    if flag_db == True:
                        msg_ = "[msg_1] - {3}. Line {0}/{1} stored. {2} remaining".format(
                            str(x), str(h), str(len(lines)),msg_file)
                        print(msg_)
                        push_log(msg_)
                    else:
                        f1 = open(filename + '_error.csv', 'a+')
                        f1.writelines(sql_)
                        f1.close()
                        if 'Duplicate' in  err:
                            msg_ = "[msg_3] - {3}. Line {0}/{1} DELETED as it is a DUPLICATE. {2} remaining".format(
                                str(x), str(h), str(len(lines)), msg_file)
                            print(msg_)
                            push_log(msg_)

                        elif sql_=='\n' or sql_=='':
                            msg_ = "[msg_3.1] - {3}. Line {0}/{1} DELETEDas it is None. {2} remaining".format(
                                str(x), str(h), str(len(lines)), msg_file)
                            print(msg_)
                            push_log(msg_)
                        else:
                            if lines[idLine] != '\n':
                                msg_ = "[msg_4] - {3}. Line {0}/{1} not stored. {2} remaining. MySQL Error: {4}" \
                                    .format(str(x), str(h), str(len(lines)), msg_file, err)
                                print(msg_)
                                push_log(msg_)
                    del lines[idLine]

                # Rewrite remaining lines in file
                f = open(filename, 'w')
                f.writelines(lines)
                f.close()

                msg_ = '[msg_5] - Stored {} lines to file: {}'.format(len(lines), filename)
                print(msg_)
                push_log(msg_)
    def reload_arrayBackup(self):
        # 2019-11-11  svuota array
        # v2.0 2020-07-04
        # v2.11 2020-07-19
        # v2.12 2020-07-26
        # v3.0  2020-09-19  if h>0

        msg_file = 'reload_arrayBackup()'
        config_mysql_bk = self.configMysql['config_mysql_bk']
        filename = config_mysql_bk['filename']
        lines = self.array_sql
        h = min(config_mysql_bk['max_rows_reload'], len(lines))
        idLine = 0

        if h>0:
            for x in range(h):
                sql_ = lines[idLine]
                flag_db, err = self.exec_sql1(sql_, False)
                str_ = str(err + '\n sql: ' + sql_)

                if flag_db == True:
                    msg_ = "[msg_1] reload_arrayBackup() - {3}. Line {0}/{1} stored. {2} remaining".format(
                        str(x), str(h), str(len(lines)), msg_file)
                    print(msg_)
                    push_log(msg_)

                else:

                    f1 = open(filename + '_error.csv', 'a+')
                    f1.writelines(sql_)
                    f1.close()

                    if 'Duplicate' in  err:
                        msg_ = "[msg_3] reload_arrayBackup - {3}. Line {0}/{1} DELETED as it is a DUPLICATE. {2} remaining".format(
                            str(x), str(h), str(len(lines)), msg_file)
                        print(msg_)
                        push_log(msg_)
                    elif sql_ == '\n' or sql_ == '':
                        msg_ = "[msg_3.1] reload_arrayBackup - {3}. Line {0}/{1} DELETEDas it is None. {2} remaining".format(
                            str(x), str(h), str(len(lines)), msg_file)
                        print(msg_)
                        push_log(msg_)

                    else:
                        if lines[idLine] != '\n':
                            msg_ = "[msg_4] reload_arrayBackup - {3}. Line {0}/{1} not stored. {2} remaining. MySQL Error: {4}" \
                                .format(str(x), str(h), str(len(lines)), msg_file, err)
                            print(msg_)
                            push_log(msg_)

                del lines[idLine]

            msg_ = '[msg_5] reload_arrayBackup - Stored {} remaining lines in array_sql'.format(len(lines))
            print(msg_)
            push_log(msg_)
    def data_store_pack(self, dataPack, table_, *args, **kwargs):
        # Memorizza i dati di piu' strumenti
        # v1.0 2020-07-03
        # v2.0 2021-01-06

        len_pack = len(dataPack)
        store_flag = [0] * len_pack

        for i in range(len_pack):
            store_flag[i] = self.data_store(dataPack[i], table_)
        return store_flag
    def data_store_db(self, param_list, table_, **kwargs):
        # Memorizza i dati solo su db
        # v1.0 2020-07-03
        # v2.0 2020-12-27
        # v3.0 2021-01-06

        item = param_list[0]
        keys = [x for x in item.keys()]
        sql1 = 'INSERT INTO %s (%s) ' % (table_, keys)
        sql2 = 'VALUES '

        for xx in range(len(param_list)):
            item = param_list[xx]
            vals = [x for x in item.values()]
            sql2 += '( %s ),' % vals

        sql2 = sql2[:-1]
        sql1 = sql1.replace('[', '')
        sql1 = sql1.replace(']', '')
        sql1 = sql1.replace("'", '')
        sql2 = sql2.replace('[', '')
        sql2 = sql2.replace(']', '')
        sql2 += r';'
        sql = sql1 + sql2

        flagDB,err = self.exec_sql1(sql, False)
        #print('AAA - stored: ', datetime.now())
        return flagDB,err, sql

    #Others
    def data_store(self,  param_list, table_):
        # Memorizza i dati di param_list in
        # 1. mysql DB
        # 2. backup file
        # 3. temp-array

        # v2.7 2019-07-20   pack data
        # v3.0 2020-07-04
        # v3.1 2020-12-03   integrated data_store_db()
        # v3.2 2021-01-06   table

        config_mysql= self.configMysql
        config_mysql_bk = self.configMysql['config_mysql_bk']
        flag_db = 0
        flag_file = 0
        store_flag = 0
        # storage flag
        #     0=none
        #     1=Mysql
        #     2=file
        #     3=array

        db_connect = internet2()
        sql_ = '[msg] see_db.data_store() - error: no internet connection'
        # print('dbconnect', db_connect)

        if db_connect:
            flag_db, _, sql_ = self.data_store_db(param_list, table_)
            #flag_db, _ = self.exec_sql1( sql, 0)

        if flag_db:
            # print('...sql ---->>> db_mysql... ip', config_mysql['host'])
            store_flag = '1'
        else:
            if config_mysql_bk['enable']:
                filename = config_mysql_bk['filename']
                flag_file = self.write_to_file(filename, sql_)
            if flag_file:
                store_flag = '2'
                push_log(message_strings[10] % (filename)) # 'msg_10 - DB inaccessibile ---> backup su %s ',
            else:
                self.write_array(sql_)
                #print('> sql: ', sql[:200])
                push_log(message_strings[13])
                store_flag = '3'
                print('> data_store() - store_flag3: stored sql array to array_sql. Size: ', str(len(self.array_sql)))
        return store_flag
    def write_array(self, sql):
        #v2.0 2020-07-04
        self.array_sql.append(sql)
        items = len(self.array_sql)
        return items
    def write_to_file(self, file_name, stringa):
        # 2019-08-26
        # filname: one each month
        # file backup mysql string
        # v2.0 2020-07-04
        # v2.1 2020-09-19 no "\n"

        stringa += "\n"

        # store in mysql backup file
        if 'INSERT ' in stringa:
            filedatetime = ''  # -> to mysql_bk
        else:
            # store in Backup file
            filedatetime = '{:%Y_%B}'.format(time_utc())

        filename = filedatetime + file_name

        file_ok = True
        if os.path.isfile(filename):
            try:
                f = open(filename, 'a')
            except os.error:  # as err
                file_ok = False
            else:
                f.write(stringa)
                f.close()
        else:
            try:
                f = open(filename, 'w')
            except os.error:  # as err:
                file_ok = False
                print(message_strings[3], filename)
            else:
                f.write(stringa)
                f.close()
        return file_ok
    def dataDB_newTab_y(self, tableName, year_):
        # Creates a new seeTable every year
        # v1.0 2020-04-20
        # v1.1 2020-07-02

        seeDB_ = self.configMysql['database']
        seeTab_ = tableName  # self.configMysql['tableRaw']
        seeTabNew_ = seeTab_ + '_' + str(year_)

        sql_1 = 'ALTER TABLE {0}.{1} RENAME TO {0}.{2} ;'.format(
            seeDB_,
            seeTab_,
            seeTabNew_,
        )

        sql_2 = 'CREATE TABLE {0}.{1} LIKE {0}.{2};'.format(
            seeDB_,
            seeTab_,
            seeTabNew_,
        )

        err1 = '0'
        err2 = '0'
        _, err1 = self.exec_sql1(sql_1, 0)
        _, err2 = self.exec_sql1(sql_2, 0)

        if err1 != '0':
            txt_ = '[msg] - dataDB_seeTab_y: 1. error in renaming  table {0}'.format(seeTab_, )
            print(txt_)
            push_log(txt_)
        else:
            txt_ = '[msg] - dataDB_newseeTab_y: 1. table  {0} renamed to  {1}'.format(seeTab_, seeTabNew_)
            print(txt_)
            push_log(txt_)

        if err2 != '0':
            txt_ = '[msg] - dataDB_newseeTab_y: 2. error in creating the new table err1:{0}.'.format(seeTab_)
            print(txt_)
            push_log(txt_)
        else:
            txt_ = '[msg] - dataDB_seeTab_y: 2. new table {0} created.'.format(seeTab_)
            print(txt_)
            push_log(txt_)

    #
    #
    # OLD
    #
    #
    def dataDB_seeJoin_read_old(self, idDevice='All', idMac='All', idDep='All'):
        # Reads Join Table data
        # v1.0 2020-07-07
        # old 2021-05-14

        sql_ = "select  idDevice, idMac, idDep from {0}.{1}  " \
               "where idDevice='{2}' and idMac= '{3}' and idDep= '{4}'; ".format(
            self.configMysql['database'],
            self.configMysql['tableJoin'],
            idDevice, idMac, idDep
        )

        if idDevice == 'All':
            sql_ = sql_.replace('idDevice=', 'idDevice!=')
        if idMac == 'All':
            sql_ = sql_.replace('idMac=', 'idMac!=')
        if idDep == 'All':
            sql_ = sql_.replace('idDep=', 'idDep!=')

        if self.db_connect:
            out_, _ = self.exec_sql1(sql_, True)  # format [(par1, par2,...)]
        else:
            str_ = '[msg] dataDB_seeJoin_read() - no web connection'
            push_log(str_)

        db_1 = pd.DataFrame(data=out_,
                            columns=['idDevice', 'idMac', 'idDep'],
                            )
        return db_1
    def dataDB_seeAllDevice_read_old(self, dfDevPar):
        # Reads Devices, MAchines, Departments Table
        # Generates a general Table
        # v1.0 2020-07-12
        # old 2021-05-14

        # dfDevPar = c001.init_plot(request, dataparam)
        # dfDevPar = List of Data from local DataBase dataparam

        # List od Divices
        devices_ = sorted(dfDevPar['idDevice'].unique(), reverse=False)
        df0 = pd.DataFrame(data=devices_,
                           columns=['idDevice'],
                           )
        # Reads Join Table
        df1 = self.dataDB_seeJoin_read(idDevice='All', idMac='All', idDep='All')
        df0 = pd.merge(df0, df1, how='left', on='idDevice')

        # Reads Machine Description
        df1 = self.dataDB_seeMac_read(idMac='All')
        df0 = pd.merge(df0, df1, how='left', on='idMac')

        # Reads Departments Description
        df1 = self.dataDB_seeDep_read(idDep='All')
        df0 = pd.merge(df0, df1, how='left', on='idDep')

        columns_ = ['idDevice', 'idMac', 'idDep', 'machDescr', 'depDescr']
        df0 = df0[columns_]
        return df0
    def dataDB_seeAllData_Join_old(self, df):
        # Join to input Dataframe's idDevices:  MAchines, Departments, MAchDescr, DepDesc
        # Generates a general Table
        # v1.0 2020-07-12
        # old 2021-05-14

        # dfDevPar = c001.init_plot(request, dataparam)
        # dfDevPar = List of Data from local DataBase dataparam

        # Reads Join Table
        df1 = self.dataDB_seeJoin_read(idDevice='All', idMac='All', idDep='All')
        df0 = pd.merge(df, df1, how='left', on='idDevice')

        # Reads Machine Description
        df1 = self.dataDB_seeMac_read(idMac='All')
        df0 = pd.merge(df0, df1, how='left', on='idMac')

        # Reads Departments Description
        df1 = self.dataDB_seeDep_read(idDep='All')
        df0 = pd.merge(df0, df1, how='left', on='idDep')

        return df0
    def dataDB_seeAllProd_read_old(self, dfDevPar):
        # Reads Devices, MAchines, Departments Table
        # Generates a general Table
        # v1.0 2020-07-13
        # old 2021-05-14

        # dfDevPar = c001.init_plot(request, dataparam)
        # dfDevPar = List of Data from local DataBase dataparam

        # List od Devices
        devices_ = sorted(dfDevPar['idMac'].unique(), reverse=False)
        df0 = pd.DataFrame(data=devices_,
                           columns=['idMac'],
                           )
        # Reads Join Table
        df1 = self.dataDB_seeJoin_read(idDevice='All', idMac='All', idDep='All')
        df0 = pd.merge(df0, df1, how='left', on='idMac')

        # Reads Machine Description
        df1 = self.dataDB_seeMac_read(idMac='All')
        df0 = pd.merge(df0, df1, how='left', on='idMac')

        # Reads Departments Description
        df1 = self.dataDB_seeDep_read(idDep='All')
        df0 = pd.merge(df0, df1, how='left', on='idDep')

        # columns_ = ['idMac', 'idDep', 'machDescr', 'depDescr', 'idDevice']
        # df0 = df0[columns_]
        return df0
    def dbRead_pars_old(self, load_data):
        # v1.9 2018-08-21
        # Added 'Delay'
        # old 2021-05-14

        config_mysql = self.configMysql
        idDevs = load_data['idDev']
        idParams = load_data['idPars']
        startDate = load_data['startDate']
        endDate = load_data['endDate']

        # DB - Lettura Parametri multipli -
        # idParams,idDevs  list
        db_name = load_data['database']
        tab_name = load_data['table']
        sql_params = 'and ('
        sql_Devs = '('
        iPar = [None] * len(idParams)
        iDev = [None] * len(idDevs)

        if isinstance(idDevs, str):
            sql_Devs += 'idDevice = ' + "'" + idDevs + "')"
        else:
            for x in range(len(idDevs)):
                iDev[x] = 'idDevice = ' + "'" + str(idDevs[x]) + "'"
            sql_Devs += ' OR '.join(iDev) + ')'

        if isinstance(idParams, str):
            sql_params += 'idParam = ' + "'" + idParams + "'" + ')'
        else:
            for x in range(len(idParams)):
                iPar[x] = 'idParam = ' + "'" + str(idParams[x]) + "'"
            sql_params += ' OR '.join(iPar) + ')'

        startDate = str(startDate)
        endDate = str(endDate)
        sql_text = 'select Date, idDevice, idParam, Value, Code, Delay ' + '\n'
        sql_text += 'from ' + db_name + '.' + tab_name + '\n'
        sql_text += 'where ' + sql_Devs + '\n'
        sql_text += sql_params + '\n'
        sql_text += 'and   Date between ' + "'" + startDate + "'" + ' and ' + "'" + endDate + "'" + '\n'
        sql_text += 'order by Date asc; '

        # print('-> dbRead_pars - sql_text: ', sql_text)
        # 0. Estrazione dati da DB
        db_1, _ = self.exec_sql1(sql_text, True)

        # 1. Creazione DataFrame del Database
        db_1 = pd.DataFrame(data=db_1,
                            columns=['DateTime', 'idDevice', 'idParam', 'Value', 'Code', 'Delay'],
                            )
        # 1. Eliminazione DateTime duplicati
        # db_1 =  db_1.loc[[not n for n in db_1[['DateTime','idDevice','idParam']].duplicated()]]

        #     indexList ='DateTime'
        #     db_1.index=db_1[indexList]
        #     db_1.drop(indexList,axis=1,inplace=True)
        return db_1
    def dataDB_seeProd_read_old(self, load_data):
        # Read Production Data from s000Prod
        # v2.0 2020-07-13
        # v.2.1 renamed to from dbProd_read() to dataDB_seeProd_read
        # ---  OLD  ---- 2021-05-12

        config_mysql = self.configMysql
        idMacs = load_data['idMac']
        idParams = load_data['idPars']
        startDate = load_data['startDate']
        endDate = load_data['endDate']

        # DB - Lettura Parametri multipli -
        # idParams,idDevs  list
        db_name = load_data['database']
        tab_name = load_data['table']
        sql_params = 'and ('
        sql_Macs = '('

        iPars = [None] * len(idParams)
        iMacs = [None] * len(idMacs)

        if isinstance(idMacs, str):
            sql_Macs += 'idMac = ' + "'" + idMacs + "')"
        else:
            for x in range(len(idMacs)):
                iMacs[x] = 'idMac = ' + "'" + str(idMacs[x]) + "'"
            sql_Macs += ' OR '.join(iMacs) + ')'

        if isinstance(idParams, str):
            sql_params += 'idParam = ' + "'" + idParams + "'" + ')'
        else:
            for x in range(len(idParams)):
                iPars[x] = 'idParam = ' + "'" + str(idParams[x]) + "'"
            sql_params += ' OR '.join(iPars) + ')'

        startDate = str(startDate)
        endDate = str(endDate)
        sql_text = 'select Date, idMac, idJob, idArt, idParam, Value, Code ' + '\n'
        sql_text += 'from ' + db_name + '.' + tab_name + '\n'
        sql_text += 'where ' + sql_Macs + '\n'
        sql_text += sql_params + '\n'
        sql_text += 'and   Date between ' + "'" + startDate + "'" + ' and ' + "'" + endDate + "'" + '\n'
        sql_text += 'order by Date asc; '

        # 0. Estrazione dati da DB
        db_1, _ = self.exec_sql1(sql_text, True)

        # 1. Creazione DataFrame del Database
        db_1 = pd.DataFrame(data=db_1,
                            columns=['DateTime', 'idMac', 'idJob', 'idArt', 'idParam', 'Value', 'Code'],
                            )
        # 1. Eliminazione DateTime duplicati
        # db_1 =  db_1.loc[[not n for n in db_1[['DateTime','idDevice','idParam']].duplicated()]]

        #     indexList ='DateTime'
        #     db_1.index=db_1[indexList]
        #     db_1.drop(indexList,axis=1,inplace=True)
        return db_1
    def pivotRead_ProdData_old(self, load_data):
        # Read Prod from see000Prod
        # v1.0 2020-11-08

        if load_data['tZone'] != '':
            try:
                load_data['startDate'] = (
                        datetime.strptime(load_data['startDate'], "%Y-%m-%d") - timedelta(days=1)).strftime(
                    "%Y-%m-%d")
                load_data['endDate'] = (
                        datetime.strptime(load_data['endDate'], "%Y-%m-%d") + timedelta(days=1)).strftime(
                    "%Y-%m-%d")
            except:
                load_data['startDate'] = load_data['startDate'] - timedelta(days=1)
                load_data['endDate'] = load_data['endDate'] + timedelta(days=1)

        ##### READS DATA  ###

        sql_ = '''
         Select Date, idMac, idParam, Value, Code 
         FROM DB_.TABLE_ 
         WHERE (Date between startDate_ AND endDate_)  AND (idMac =dev_) AND (idParam = par_);
         '''
        sql_ = sql_.replace('DB_', load_data['database'])
        sql_ = sql_.replace('TABLE_', load_data['table'])
        sql_ = sql_.replace('startDate_', "'" + str(load_data['startDate']) + "'")
        sql_ = sql_.replace('endDate_', "'" + str(load_data['endDate']) + "'")
        sql_ = sql_.replace('dev_', "'" + load_data['idDev'] + "'")
        sql_ = sql_.replace('par_', "'" + load_data['idPars'] + "'")

        print('sql: ', sql_)

        df, _ = self.exec_sql1(sql_, True)
        if len(df) == 0:
            return [0], pd.DataFrame()

        # 1. Creazione DataFrame del Database
        df = pd.DataFrame(data=df,
                          columns=['DateTime', 'idMac', 'idParam', 'Value', 'Code'],
                          )

        df.set_index('DateTime', inplace=True)
        df.index.name = 'DateTime'
        df['idxPar'] = df['idMac'] + '_' + df['idParam']

        # Adapt DateTime to timezone
        if load_data['tZone']:
            deltaTime = ((utctime_to_tZone(datetime.now(), load_data[
                'tZone']) - datetime.now()).seconds + 1) // 3600  # deltatime in hours
            df.index = df.index.to_series().apply(lambda x: x + timedelta(hours=deltaTime))  # update datetime
            # df['DateTime'] = df['DateTime'].apply(lambda x: utctime_to_tZone(x, tZone))  # Pivot Columns names: device_param

        if load_data['timeStep'] != '0t':
            DT_Stream = pd.date_range(load_data['startDate'], load_data['endDate'], freq=load_data['timeStep'])
            DT_Stream = pd.DataFrame(data=DT_Stream, columns=['DateTime'])
            DT_Stream = DT_Stream.set_index('DateTime')
            # Merge
            df = pd.merge(DT_Stream, df, how='left', right_index=True, left_index=True)

        # Code for not sampled data
        error_code = err_code['server_off']
        df.update(df[df['idMac'].isna()].loc[:, 'idMac'].fillna(value=load_data['idDev']))
        df.update(df[df['idParam'].isna()].loc[:, 'idParam'].fillna(value=load_data['idPars']))
        df.update(df[df['Code'].isna()].loc[:, 'Code'].fillna(value=error_code))

        # Pivot Table
        df1 = df
        if load_data['code'] != '':
            df1 = df1[df1['Code'] == load_data['code']]
        # Shift time
        if load_data['shiftStep'] != 0:
            df1.index = df1.index.to_period(load_data['timeStep']) + load_data['shiftStep']
            df1.index = df1.index.to_timestamp(load_data['timeStep'])  # riconversione index in timestamp per plot

        # df1 = df1[~df1.index.duplicated(keep='first')]
        pivot_ = df1.reset_index().pivot(
            index='DateTime',
            columns='idxPar',
            values='Value')

        # Drops duplicated  - filter for DST time shifts
        # pivot_ = pivot_[~pivot_.index.duplicated(keep='first')]
        # pivot_.dropna(inplace=True)

        # df index DateTime
        pivot_.index.name = 'DateTime'
        pivot_.columns.name = ''

        return pivot_, df
    def pivotTable_all_old(self, loadData):
        # read all data for ONE Param from raw data table
        # v1.0 - 2020-07-27
        # -- old -- 2021-05-15

        startDate = loadData['startDate']
        endDate = loadData['endDate']
        #timeStep = loadData['timeStep']
        #shiftStep = loadData['shiftStep']
        NullValue = loadData['NullValue']
        tZone = loadData['tZone'] or None
        code = loadData['code']

        daysBack =0
        if tZone != '':
            # one day back to keep around midnight  time
            if isinstance(startDate, str):
                loadData['startDate'] = (datetime.strptime(startDate, "%Y-%m-%d") - timedelta(days=daysBack)).strftime(
                    "%Y-%m-%d")
            else:
                loadData['startDate'] = startDate - timedelta(days=daysBack)

            if isinstance(endDate, str):
                loadData['endDate'] = (datetime.strptime(endDate, "%Y-%m-%d") + timedelta(days=daysBack)).strftime("%Y-%m-%d")
            else:
                loadData['endDate'] = endDate + timedelta(days=daysBack)

        ##### READS DATA  ###
        df = self.dbRead_pars(loadData)
        df['idxPar'] = df['idDevice'] + '_' + df['idParam']

        # Adapt DateTime to timezone
        df = df.set_index('DateTime')
        if tZone:
            deltaTime = ((utctime_to_tZone(datetime.now(),
                                           tZone) - datetime.now()).seconds + 1) // 3600  # deltatime in hours
            df.index = df.index.to_series().apply(lambda x: x + timedelta(hours=deltaTime))  # update datetime

        # Pivot Table
        df = df[df['Code'] == code]

        pivot_ = df.reset_index().pivot(
            index='DateTime',
            columns='idxPar',
            values='Value', )

        # df index DateTime
        pivot_.index.name = 'DateTime'
        pivot_.columns.name = ''

        return pivot_, df



##################
## FUNCTIONS  OLD  OLD  OLD   ####
##################
def string_to_file_old(diz):
    # Stringa per fileLog
    # 2021-05-21  OLD

    data = str(diz['Date']).replace('.', ',')
    valore = str(diz['Value']).replace('.', ',')
    return str(data) + ';' + str(diz['idDevice']) + ';' + str(diz['idParam']) + ';' + str(valore) + ';' + str(
        diz['Code'])
def push_file_old(config, stringa):
    # 2019-08-26
    # filname: one each month
    # file backup mysql string

    if 'INSERT' in stringa[0:12]:
        # store in mysql backup file
        filedatetime = ''  # -> to mysql_bk
        stringa += '\n'
    else:
        # store in Backup file
        filedatetime = '{:%Y_%B}'.format(time_utc())

    filename = config['path'] + filedatetime + '_' + config['filename']
    stringa += '\n'

    f = []
    file_ok = True

    if os.path.isfile(filename):

        try:
            f = open(filename, 'a')
        except os.error:  # as err
            file_ok = False
        else:
            f.write(stringa)
            f.close()

    else:

        try:
            f = open(filename, 'w')
        except os.error:  # as err:
            file_ok = False
            print(message_strings[3], filename)
        else:
            f.write(stringa)
            f.close()
    return file_ok
def time_array_old(startDate, endDate, timeStep):
    # Genera array di DateTime
    # freq_ = str(step_minutes)+'T'
    # 2021-05-21  OLD
    return pd.date_range(startDate, endDate, freq=timeStep)