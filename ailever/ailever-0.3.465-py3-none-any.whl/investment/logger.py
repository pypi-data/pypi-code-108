import logging
import logging.config
import os

r"""---------- DEFAULT CONFIG for Logger and UPDATE log ----------"""

update_log = {'ohlcv_1d':'ohlcv_1d.json', 'ohlcv_1m': 'ohlcv_1m', 'fundamentals':'fundamentals.json'}
config = {"version": 1,
            "formatters": {
                "simple": {"format": "[%(name)s] %(message)s"},
                "complex":{"format": "[%(asctime)s]/[%(name)s]/[%(filename)s:%(lineno)d]/[%(levelname)s]/[%(message)s]"},
                },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "level": "DEBUG"},
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "meta.log",
                    "formatter": "complex",
                    "level": "INFO"},
                },
            "root": {"handlers": ["console", "file"], "level": "WARNING"},
            "loggers": {"normal": {"level": "INFO"}, "dev": {"level": "DEBUG"},},}



class Logger():
     
    def __init__(self, config=config):
        
        self.config = config
        
        logging.config.dictConfig(self.config)       
        self.root_logger = logging.getLogger("root")
        self.normal_logger = logging.getLogger("normal")
        self.dev_logger = logging.getLogger("dev") 















def ptest():

    for i in range(10):
        logger.dev_logger.info(i)

def ptest2():

    lst = ['ARE','BXP','SPG', 'SLG']
    for ticker in lst:
        logger.normal_logger.info(ticker)

if __name__=="__main__":
    
    logger = Logger()

    ptest()
    ptest2()
        

