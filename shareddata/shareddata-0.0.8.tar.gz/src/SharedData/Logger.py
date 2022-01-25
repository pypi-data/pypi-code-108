import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import glob
import pandas as pd
from pythonjsonlogger.jsonlogger import JsonFormatter
import boto3

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
            ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',\
            datefmt='%Y-%m-%dT%H:%M:%S%z')
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
        #log to aws kinesis
        kinesishandler = KinesisFirehoseDeliveryStreamHandler()
        kinesishandler.setLevel(loglevel)    
        jsonformatter = JsonFormatter(os.environ['USERNAME']+'@'+os.environ['USERDOMAIN'] + 
            ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',\
            datefmt='%Y-%m-%dT%H:%M:%S%z')
        kinesishandler.setFormatter(jsonformatter)
        self.log.addHandler(kinesishandler)
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
                _df.columns = ['user','datetime','name','type','message']
                _df['source'] = source
                df = df.append(_df)
            except Exception as e:
                print(e)
                pass
        return df


class KinesisFirehoseDeliveryStreamHandler(logging.StreamHandler):

   def __init__(self):
       # By default, logging.StreamHandler uses sys.stderr if stream parameter is not specified
       logging.StreamHandler.__init__(self)

       self.__firehose = None
       self.__stream_buffer = []

       try:
           session = boto3.Session(profile_name='kinesis-logs-write-only')
           self.__firehose = session.client('firehose')
       except Exception:
           print('Firehose client initialization failed.')

       self.__delivery_stream_name = "PUT-S3-Logs"

   def emit(self, record):
       try:
           msg = self.format(record)

           if self.__firehose:
               self.__stream_buffer.append({
                   'Data': msg.encode(encoding="UTF-8", errors="strict")
               })
           else:
               stream = self.stream
               stream.write(msg)
               stream.write(self.terminator)

           self.flush()
       except Exception:
           self.handleError(record)

   def flush(self):
       self.acquire()

       try:
           if self.__firehose and self.__stream_buffer:
               self.__firehose.put_record_batch(
                   DeliveryStreamName=self.__delivery_stream_name,
                   Records=self.__stream_buffer
               )

               self.__stream_buffer.clear()
       except Exception as e:
           print("An error occurred during flush operation.")
           print(f"Exception: {e}")
           print(f"Stream buffer: {self.__stream_buffer}")
       finally:
           if self.stream and hasattr(self.stream, "flush"):
               self.stream.flush()

           self.release()
