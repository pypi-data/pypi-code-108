
import os
import datetime as dt
from pathlib import Path

DEBUG = 0
INFO = 10
WARNING = 20
ERROR = 30
CRITICAL = 40

root_level = DEBUG
capture_logs = False

_logs_dir = None
_log_fname = None
_log_file_path = None

def config_log_capture(logsdir:str, logfile_title:str='', start=True):
    global _logs_dir, _log_fname, _log_file_path
    _logs_dir = logsdir
    if not os.path.exists(Path(_logs_dir).resolve()):
        raise LogError("Log directory specified doesn't exist")
    _log_fname = _generate_logfname(logfile_title)
    _log_file_path = Path(_logs_dir).resolve()/(_log_fname+'.txt')
    if start: start_log_capture()
 
def start_log_capture():
    global capture_logs
    capture_logs = True
    
def stop_log_capture():
    global capture_logs
    capture_logs = False
    
def _generate_logfname(title:str) -> str:
    date = _get_date(path_friendly=True)
    return title + "_" + date

def _get_date(path_friendly:bool=False) -> str:
    datetime = dt.datetime.now()
    if path_friendly:
        date = str(datetime.date())
        time = str(datetime.time()).replace(':', "-").replace('.', '_')
        return date+"_"+time
    else:
        return str(datetime)
    
# -------------------------------------------------------------------
class LogError(Exception):
    pass

class Logger():
    
    capture_logs = True
    
    def __init__(self, module_name:str=None, level=DEBUG, sysout:bool=True) -> None:
        self.module_name = module_name
        self.level = level
        self.sysout = sysout
        
    def capture_logs(self):
        self.capture_logs = True
    
    def free_logs(self):
        self.capture_logs = False
     
    def debug(self, msg:str, nl:bool=False):
        _level = DEBUG; symbol = '[DEBUG]'
        if self._check_level(_level):
            self._process(msg, symbol=symbol, nl=nl)
    
    def info(self, msg:str,nl:bool=False):
        _level = INFO; symbol = '[INFO]'
        if self._check_level(_level):
            self._process(msg, symbol=symbol, nl=nl)
    
    def warning(self, msg:str, nl:bool=False):
        _level = WARNING; symbol = '[WARNING]'
        if self._check_level(_level):
            self._process(msg, symbol=symbol, nl=nl)  
        
    def error(self, msg:str, nl:bool=False):
        _level = ERROR; symbol = '[ERROR]'
        if self._check_level(_level):
            self._process(msg, symbol=symbol, nl=nl)
    
    def critical(self, msg:str, nl:bool=False):
        _level = CRITICAL; symbol = '[CRITICAl]'
        if self._check_level(_level):
            self._process(msg, symbol=symbol, nl=nl)
    
    def log(self, msg:str, nl:bool=False):
        symbol = '[LOG]'
        self._process(msg, symbol=symbol, nl=nl)
            
    def _check_level(self, level:int):
        if not root_level > level and not self.level > level:
            return True
        return False
    
    def _process(self, msg:str, symbol:str='', nl:bool=False):
        log = self._get_log(msg, symbol=symbol, nl=nl)
        self._capture(log)
        self._print(log)
    
    def _get_log(self, msg:str, symbol:str='', nl:bool=False) -> str:
        log = symbol+" "
        if self.module_name is not None:
            log += self.module_name+": "
        log += str(msg)
        if nl: log = "\n"+log
        
        return log
    
    def _capture(self, log:str):
        if not capture_logs or not self.capture_logs: return
        log_date = _get_date()
        with open(_log_file_path, 'ab') as file:
            if log.startswith('\n'):
                log = log[1:]
            final_log = "\n\n"+log_date+"\n"+log
            file.write(final_log.encode('utf-8'))
    
    def _print(self, log:str):
        if not self.sysout: return
        print(log)
        