"""
# Module Test:
# -q -m 1 --testDir testdata
# all Single Tests:
# -q -m 0 -s Dm  
# ---
# SETUP
# ---
import os
import time
import logging
logger = logging.getLogger('PT3S.Dm')  
# ---
# path
# ---
if __name__ == "__main__":
  try:      
     dummy=__file__
     logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ','path = os.path.dirname(__file__)'," .")) 
     path = os.path.dirname(__file__)
  except NameError:    
     logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ',"path = '.' because __file__ not defined and: "," from Dm import Dm")) 
     path = '.'
     from Dm import Dm
else:
  logger.debug("{0:s}{1:s}{2:s}{3:s}".format('DOCTEST: Not __main__ Context: ','__name__: ',__name__,"path = '.'")) 
  path = '.'
try:
  from PT3S import Am
except ImportError:
  logger.debug("{0:s}{1:s}".format("DOCTEST: ImportError: from PT3S import Am: ","- trying import Am instead ... maybe pip install -e . is active ..."))  
  import Am
# ---
# testDir
# ---
# globs={'testDir':'testdata'}
try:
   dummy= testDir
except NameError:
   testDir='testdata' 
# ---
# Init
# ---
accFile=os.path.join(path,os.path.join(testDir,'DHNetwork.mdb')) 
am=Am.Am(accFile=accFile)
accFile2=r'C:\\3s\\Projekte\\19.137 - Actemium - FBG LDS AP13\\04 - Versionen\\Version80_installiert_IO_20201216\\MDBDOC\\FBG.mdb'
am2=Am.Am(accFile=accFile2)
#accFile3=r'c:\\3s\\Projekte\\20.175 - SWM Geomare\\08 Bearbeitung Freimann\\Freimann.mdb'
#am3=Am.Am(accFile=accFile3)
"""

__version__='90.12.4.18.dev1'



import os
import sys


import re
import pandas as pd
import numpy as np
import warnings
import tables

import h5py
import time

import base64
import struct

import logging

import glob


import math

import argparse
import unittest
import doctest

# ---
# --- PT3S Imports
# ---
logger = logging.getLogger('PT3S')  
if __name__ == "__main__":
    logger.debug("{0:s}{1:s}".format('in MODULEFILE: __main__ Context:','.')) 
else:
    logger.debug("{0:s}{1:s}{2:s}{3:s}".format('in MODULEFILE: Not __main__ Context: ','__name__: ',__name__," .")) 

class DmError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def f_HelperBVBZ(
    con
   ,BV
   ,BZ   
    ):
    """
    Returns:
         df,dfBV,dfBZ
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:   

        df=pd.DataFrame()
            
        sql='select * from '+BV
        try:
            dfBV=pd.read_sql(sql,con)
        except pd.io.sql.DatabaseError as e:
            logStrFinal="{0:s}sql: {1:s}: Fehler?!".format(logStr,sql) 
            raise DmError(logStrFinal)        

        sql='select * from '+BZ
        try:
            dfBZ=pd.read_sql(sql,con)
        except pd.io.sql.DatabaseError as e:
            logStrFinal="{0:s}sql: {1:s}: Fehler?!".format(logStr,sql) 
            raise DmError(logStrFinal) 

        
        df=pd.merge(dfBZ
                        ,dfBV                                                          
                        ,left_on=['fk']
                        ,right_on=['pk']
                        ,suffixes=('_BZ',''))     
            
        newCols=df.columns.to_list()
        df=df.filter(items=[col for col in dfBV.columns.to_list()]+[col for col in newCols if col not in dfBV.columns.to_list()])
                                                                                                                  
    except DmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise DmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return df,dfBV,dfBZ

def f_HelperDECONT(   
    df
   ,dfViewModelle 
   ,dfCONT
    ):
    """
    Returns:
        df
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:   
               
        cols=df.columns.to_list()
        
        if 'fkDE_BZ' in cols:
            df=pd.merge(df
                        ,dfViewModelle                                                        
                        ,left_on=['fkDE_BZ']
                        ,right_on=['fkBZ']
                        ,suffixes=('','_VMBZ'))   
        elif 'fkDE' in cols:
            df=pd.merge(df
                        ,dfViewModelle                                                        
                        ,left_on=['fkDE']
                        ,right_on=['fkBASIS']
                        ,suffixes=('','_VMBASIS')
                        ,how='left')         
            df=pd.merge(df
                        ,dfViewModelle                                                        
                        ,left_on=['fkDE']
                        ,right_on=['fkVARIANTE']
                        ,suffixes=('','_VMVARIANTE')
                        ,how='left')               
        if 'fkCONT' in cols:
            df=pd.merge(df
                        ,dfCONT.add_suffix('_CONT')                                                        
                        ,left_on=['fkCONT']
                        ,right_on=['pk_CONT']
                        #,suffixes=('','_CONT')
                        )   
                                                                                                                          
    except DmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise DmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return df

def f_HelperVKNO(   
    dfKNOT
   ,dfVKNO   
    ):
    """
    Returns:
        df
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 


    logger.debug("{:s}dfKNOT: {!s:s}".format(logStr,dfKNOT.columns.to_list())) 
    logger.debug("{:s}dfVKNO: {!s:s}".format(logStr,dfVKNO.columns.to_list())) 

    try:                          
        df=pd.merge(dfKNOT,dfVKNO.add_suffix('_VKNO'),left_on='pk',right_on='fkKNOT_VKNO',how='left'
                  # ,suffixes=('','_VKNO')
                    )
                                                                                                                          
    except DmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise DmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return df
   

class Dm():
    """Processing Pandas Base Views.

    Args:
        * ...
           
    Attributes:
       
    Raises:
        DmError
    """


               
    def __init__(self):

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        

        try:
            pass
           









           
                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise AmError(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

  
if __name__ == "__main__":
    """
    Run Tests.
    """

    try:      
        
        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
                                      
        # Arguments      
        parser = argparse.ArgumentParser(description='Run Tests.'
        ,epilog='''
        UsageExamples: 



        '''                                 
        )

        group = parser.add_mutually_exclusive_group()                                
        group.add_argument("-v","--verbose", help="Debug Messages On (default)", action="store_true",default=True)      
        group.add_argument("-q","--quiet", help="Debug Messages Off", action="store_true")           

        parser.add_argument('--testDir',type=str,default='testdata',help="value for global 'testDir' i.e. testdata (default)")
    
                                 
        parser.add_argument("-m","--moduleTest", help="execute the Module Doctest On/Off: -m 1 (default)", action="store",default='1')      
        parser.add_argument("-s","--singleTest", help='execute single Doctest: Exp.: -s  "^Dm.": all Doctests in Module Rm are executed - but not the Module Doctest (which is named Dm)'
                            ,action="append"
                            ,default=[])      
        parser.add_argument("-x","--singleTestNO", help='execute NOT single Doctest: Exp.: -s  "^Dm.": NO Doctests in Module Rm are executed - but not the Module Doctest (which is named Dm)'
                            ,action="append"
                            ,default=[])               


        parser.add_argument("-l","--logExternDefined", help="Logging (File etc.) ist extern defined (default: False)", action="store_true",default=False)      


        args = parser.parse_args()


        class LogStart(Exception):
            pass

        try:
            logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
            if args.logExternDefined:  
                logger = logging.getLogger('PT3S')  
                logStr=logStr+" (Logging extern defined) "
            else:                
                logFileName = 'PT3S.log' 
        
                loglevel = logging.INFO
                logging.basicConfig(filename=logFileName
                                    ,filemode='w'
                                    ,level=loglevel
                                    ,format="%(asctime)s ; %(name)-60s ; %(levelname)-7s ; %(message)s")    

                fileHandler = logging.FileHandler(logFileName)        
                logger.addHandler(fileHandler)

                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logging.Formatter("%(levelname)-7s ; %(message)s"))
                consoleHandler.setLevel(logging.INFO)
                logger.addHandler(consoleHandler)
                          
            raise LogStart
        except LogStart:   
            if args.verbose:  # default         
                logger.setLevel(logging.DEBUG)  
            if args.quiet:    # Debug Messages are turned Off
                logger.setLevel(logging.ERROR)  
                args.verbose=False            
            logger.debug("{0:s}{1:s}".format(logStr,'Start.'))             
        else:
            pass
                                            
        logger.debug("{0:s}{1:s}{2:s}".format(logStr,'Argumente:',str(sys.argv))) 
        #logger.debug("{0:s}{1:s}{2:s}".format(logStr,'testDir: ',args.testDir)) 


        if args.moduleTest == '1':            
            logger.info("{0:s}{1:s}{2:s}".format(logStr,'Start unittests (by DocTestSuite...). testDir: ',args.testDir)) 
            dtFinder=doctest.DocTestFinder(recurse=False,verbose=args.verbose) # recurse = False findet nur den Modultest
            suite=doctest.DocTestSuite(test_finder=dtFinder #,setUp=setUpFct
                                   ,globs={'testDir':args.testDir                                           
                                           })   
            unittest.TextTestRunner().run(suite)
          
        if len(args.singleTest)>0:


 
            dtFinder=doctest.DocTestFinder(verbose=args.verbose)
            
            logger.debug("{:s}singleTests suchen in Mx ...".format(logStr)) 
            dTests=dtFinder.find(Dm,globs={'testDir':args.testDir}) 

            
            # gefundene Tests mit geforderten Tests abgleichen
            testsToBeExecuted=[]
            for expr in args.singleTest:
                logger.debug("{0:s}singleTests: {1:s}: {2:s} ...".format(logStr,'Searching in Tests found for Expr     TBD',expr.strip("'")))                
                testsToBeExecuted=testsToBeExecuted+[test for test in dTests if re.search(expr.strip("'"),test.name) != None]     
            logger.debug("{0:s}singleTests: {1:s}: {2:s}".format(logStr,'    TBD',str(sorted([test.name for test in testsToBeExecuted]))))                   

            testsNotToBeExecuted=[]
            for expr in args.singleTestNO:
                logger.debug("{0:s}singleTests: {1:s}: {2:s} ...".format(logStr,'Searching in Tests found for Expr NOT TBD',expr.strip("'")))      
                testsNotToBeExecuted=testsNotToBeExecuted+[test for test in testsToBeExecuted if re.search(expr.strip("'"),test.name) != None]       
            logger.debug("{0:s}singleTests: {1:s}: {2:s}".format(logStr,'NOT TBD',str(sorted([test.name for test in testsNotToBeExecuted]))))    

            # effektiv auszuführende Tests 
            testsToBeExecutedEff=sorted(set(testsToBeExecuted)-set(testsNotToBeExecuted),key=lambda test: test.name)
            
            dtRunner=doctest.DocTestRunner(verbose=args.verbose) 
            for test in testsToBeExecutedEff:                      
                    logger.debug("{0:s}singleTests: {1:s}: {2:s} ...".format(logStr,'Running Test',test.name)) 
                    dtRunner.run(test)                                        



                                
    except SystemExit:
        pass                                              
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise AmError(logStrFinal)   
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 


        sys.exit(0)

