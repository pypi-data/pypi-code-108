import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import glob
import pandas as pd

from dotenv import load_dotenv

class Logger:

    def __init__(self, source):
        self.source = source

        load_dotenv()  # take environment variables from .env.
        
        commompath = os.path.commonpath([source,os.environ['SOURCE_FOLDER']])
        source = source.replace(commompath,'')
        source = source.lstrip('\\').lstrip('/')
        source = source.replace('.py','')

        path = Path(os.environ['DATABASE_FOLDER'])
        path = path / 'Logs'
        path = path / datetime.now().strftime('%Y%m%d')
        path = path / (os.environ['USERNAME']+'@'+os.environ['USERDOMAIN'])        
        path = path / (source+'.log')
        if not path.parents[0].is_dir():
            os.makedirs(path.parents[0])
        os.environ['LOG_PATH'] = str(path)

        if os.environ['LOG_LEVEL']=='DEBUG':
            loglevel = logging.DEBUG
        elif os.environ['LOG_LEVEL']=='INFO':
            loglevel = logging.INFO   

        self.log = logging.getLogger(source)        
        self.log.setLevel(loglevel)    
        formatter = logging.Formatter(os.environ['USERNAME']+'@'+os.environ['USERDOMAIN'] + 
            ';%(levelname)s;%(asctime)s;%(message)s',\
            datefmt='%H:%M:%S')
        #log screen
        handler = logging.StreamHandler()
        handler.setLevel(loglevel)    
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        #log file        
        fhandler = logging.FileHandler(os.environ['LOG_PATH'], mode='a')
        fhandler.setLevel(loglevel)    
        fhandler.setFormatter(formatter)
        self.log.addHandler(fhandler)
        #assign static variable log to be used by modules
        Logger.log = self.log
        
    def readLogs(self):    
        logsdir = Path(os.environ['LOG_PATH']).parents[0]
        lenlogsdir = len(str(logsdir))
        files = glob.glob(str(logsdir) + "/**/*.log", recursive = True)   
        df = pd.DataFrame()
        # f=files[0]
        for f in files:
            source = f[lenlogsdir+1:].replace('.log','.py')
            try:
                _df = pd.read_csv(f,header=None,sep=';')
                _df.columns = ['user','type','hour','message']
                _df['source'] = source
                df = df.append(_df)
            except Exception as e:
                print(e)
                pass
        return df
