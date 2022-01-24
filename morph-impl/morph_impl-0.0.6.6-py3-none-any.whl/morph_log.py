import logging
import sys
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter('%(asctime)s:%(lineno)d:%(module)s:%(funcName)s:%(name)s:%(levelname)s:%(message)s')
LOG_FILE = "morph_impl.log"

def get_console_handler():
   """
   Logging console handler
   """
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   """
   Logging file handler
   """
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   """
   Create the logger - call this function from other scripts. 
   """
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.INFO) # better to have too much log than not enough
   if logger.handlers:
      logger.handlers =[] 
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger