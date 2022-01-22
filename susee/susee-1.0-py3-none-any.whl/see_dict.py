# -*- coding: utf-8 -*-
##############################
##### DATABASE Functions  ####
##############################
#Studio Tecnico Pugliautomazione - Monopoli (BA)
# Copyright (c)
# v2.0 2020-07-22
# v2.1 2021-01-04
# v2.2 2021-01-31
# v2.3 2021-02-21 params_id
# v2.4 2021-05-26
# v2.5 2021-06-09


from datetime import datetime

#Fixed deltatime used to geenerate web reports
# 2021-05-26
d_periods = {
            '0t': ['DateTime', '0s', 0],
            '1t': ['DateTime', '1min', 0],
             '5t': ['DateTime', '5min', 0],
             '15t': ['qH', '15min', 0],
             '1h': ['hour', 'hour', -1],
             '1d': ['Date', 'day', -1],
             '1w': ['DateTime', 'week', -1],
             '1M': ['Month', 'month', -1]
             }

diff_params = ['222','224','226', '228', '208']

config_log = {
        'path'      :   '',
        'filename'  :   'log_file.log',
        'topstring' :   '-----  Start  Datetime_UTC:  ' + str(datetime.utcnow()) + ' ------ '
}
store_mode  = {
        0           : 'None', 
        1           : 'mysql_database',
        2           : 'mysql_backup_file',
        3           : 'array'
}
err_code = {
        'err_connection'    : 1,
        'driver error'      :  2,   #fixed driver error
        'server_off'        :  4,   #2018-08-21
        'err_register'      :     8,
        'value_NaN'         :    16,
        'lenreg_zero'       :    32,
        'driver not found'  :   64,
 }


params_id = {
    'dev_connection': 100,
}

message_strings= {
    1: 'msg 01 - push_db() - array_sql line %s stored in mysql. Linee rimanenti %s  ',
    2: 'msg_02 - push_file() - array line %s stored in file %s. Linee rimanenti %s  ',
    3: 'msg_03 - push_file() - Impossibile creare il file:  ',
    4: 'msg_04 - Svuota file e array. Database MYSQL non accessibile.',
    5: 'msg_05 - svuota_file_array() - FILE line %s stored in mysql. Linee rimanenti %s ',
    6: 'msg_06 - svuota_file_array() - Scrittura su Mysql NON riuscita. FILE line %s stored in mysql, Linee rimanenti %s.\n err.: %s ',
    7: 'msg_07 - array line %s stored in db. Lines remaining %s ',
    8: 'msg_08 - Completata routine svuota_file_array...',
    9: 'msg_09 - Database MYSQL non accessibile.',
    10:'msg_10 - data_store() - DB nok,  backup su file %s ',
    11:'msg_11 - svuota_file_array() - row deleted ',
    12:'msg_12 - data_store() - DB & file nok, backup to array ',
    13:'msg_13 - data_store() - backup to  array.',
    14:'msg_14 - Scan %s - Device %s - time %s - store mode: %s - e_rr1_rr2 %s %s' ,
    15:'msg_15 - push_db - Database MYSQL non accessibile. ErrorCode: %s ',
    16:'msg_16 - push_db - Database MySql data loaded',
    17:'msg_17 - push_db - Data already present in DB. No DB entry. ErrorCode: %s',
    18:'msg_18 - push_db - DB ErrorCode: %s',
    19:'msg_19 - device not found - one time more attempt to read',
    20:'msg_20 - push_mesDATA() - database connection failed',
    21:'msg_21 - push_mesDATA() - MES table updated',
    22:'msg_22 - server check -  %s',
    23:'msg_23 - db check -  %s',
    24:'msg_24 - Completata routine svuota_tempArray...',
    }



