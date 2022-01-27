
import warnings

import os
import sys
import logging
import pandas as pd

import re

__version__='90.12.3.0.dev1'

try:              
    
    # -------------------------------------- 
    logger = logging.getLogger('PT3S')
    logger.addHandler(logging.NullHandler())      
    # -------------------------------------- 
    
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)

    logger.debug("{0:s}{1:s}".format(logStr,'Start.'))     

    #H5
    warnings.filterwarnings('ignore',category=pd.io.pytables.PerformanceWarning) #your performance may suffer as PyTables will pickle object types that it cannot map directly to c-types 
    #warnings.filterwarnings('ignore',category=tables.exceptions.NaturalNameWarning) #\lib\site-packages\tables\path.py:100: NaturalNameWarning: object name is not a valid Python identifier: '3S'; it does not match the pattern ``^[a-zA-Z_][a-zA-Z0-9_]*$``; you will not be able to use natural naming to access this object; using ``getattr()`` will still work, though)
                                                                                 
except Exception as e:
    logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
    logger.error(logStrFinal)
    logger.error("{0:s}{1:s}".format(logStr,"the call to logging.exception('') follows ...")) 
    logging.exception('')  

finally:
    logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))

