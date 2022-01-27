
import os
import sys

import re

import pyodbc

import logging

logger = logging.getLogger('PT3S') 


class Error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class accdb(object):
    """
    create some SIR 3S related Views in an Access-DB
    """

    def __init__(self,accFile):

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             
            if os.path.exists(accFile):  
                if os.access(accFile,os.R_OK):
                    if os.access(accFile,os.W_OK):
                        pass # OK
                    else:
                        logStrFinal="{:s}accFile: {:s}: Not writetable.".format(logStr,accFile) 
                        raise Error(logStrFinal)
            else:                
                logStrFinal="{:s}accFile: {:s}: Not readable!".format(logStr,accFile)     
                raise Error(logStrFinal)  
                                      
            # die MDB existiert und ist lesbar
            logger.debug("{:s}accFile (abspath): {:s} is read- and writetable.".format(logStr,os.path.abspath(accFile))) 
           
            Driver=[x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')]
            if Driver == []:
                logStrFinal="{:s}{:s}: No Microsoft Access Driver!".format(logStr,accFile)     
                raise Error(logStrFinal)  

            # ein Treiber ist installiert
            self.conStr=(
                r'DRIVER={'+Driver[0]+'};'
                r'DBQ='+os.path.abspath(accFile)+';'
                )
            logger.debug("{:s}conStr: {:s}".format(logStr,self.conStr)) 

            # Verbindung ...
            #self.con = pyodbc.connect(self.conStr)
            #self.cur = self.con.cursor()

            ## all Tables in DB
            #tableNames=[table_info.table_name for table_info in cur.tables(tableType='TABLE')]
            #logger.debug("{0:s}tableNames: {1:s}".format(logStr,str(tableNames))) 
            #allTables=set(tableNames)
                     
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise Error(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def executeSQLFile(self,sqlFile):

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:    

            if os.path.exists(sqlFile):  
                if os.access(sqlFile,os.R_OK):
                    pass
                else:
                    logStrFinal="{:s}sqlFile: {:s}: Not readable.".format(logStr,sqlFile)
                    raise Error(logStrFinal)  
            else:
                logStrFinal="{:s}sqlFile: {:s}: Not existing.".format(logStr,sqlFile)
                raise Error(logStrFinal)  

            logger.debug("{:s}sqlFile (abspath): {:s} is readable.".format(logStr,os.path.abspath(sqlFile))) 
           
            con = pyodbc.connect(self.conStr)
            cur = con.cursor()            
            tableNames=[table_info.table_name for table_info in cur.tables(tableType='TABLE')]
            viewNames=[table_info.table_name for table_info in cur.tables(tableType='VIEW')]
            allNames=tableNames+viewNames
            allNames=set(allNames)
            allNames=list(allNames)
            cur.close()
            con.close()

            sqlfile=open(sqlFile, 'r')
            lines=sqlfile.read()
            sqlfile.close()

            for stmt in self._getSQLStmts(lines):

                logger.debug("{:s}stmt: {:s}".format(logStr,stmt))    
                                           
                con = pyodbc.connect(self.conStr)
                cur = con.cursor()

                try:
                    cur.execute(stmt)#+';')   
                    
                except Exception as e:
                    #logger.debug("{:s}ERROR: Stmt: {:s}".format(logStr,stmt))  
                    logger.debug("{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e)))
                    
                finally:
                    con.commit()
                    cur.close()
                    con.close()
                        
                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise Error(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     


    def _getSQLStmts(self,text):
        current = ''
        state = None
        for c in text:
            if state is None:  # default state, outside of special entity
                current += c
                if c in '"\'':
                    # quoted string
                    state = c
                elif c == '-':
                    # probably "--" comment
                    state = '-'
                elif c == '/':
                    # probably '/*' comment
                    state = '/'
                elif c == ';':
                    # remove it from the statement
                    current = current[:-1].strip()
                    ##current = current.strip()
                    # and save current stmt unless empty
                    if current:
                        yield current
                    current = ''
            elif state == '-':
                if c != '-':
                    # not a comment
                    state = None
                    current += c
                    continue
                # remove first minus
                current = current[:-1]
                # comment until end of line
                state = '--'
            elif state == '--':
                if c == '\n':
                    # end of comment
                    # and we do include this newline
                    current += c
                    state = None
                # else just ignore
            elif state == '/':
                if c != '*':
                    state = None
                    current += c
                    continue
                # remove starting slash
                current = current[:-1]
                # multiline comment
                state = '/*'
            elif state == '/*':
                if c == '*':
                    # probably end of comment
                    state = '/**'
            elif state == '/**':
                if c == '/':
                    state = None
                else:
                    # not an end
                    state = '/*'
            elif state[0] in '"\'':
                current += c
                if state.endswith('\\'):
                    # prev was backslash, don't check for ender
                    # just revert to regular state
                    state = state[0]
                    continue
                elif c == '\\':
                    # don't check next char
                    state += '\\'
                    continue
                elif c == state[0]:
                    # end of quoted string
                    state = None
            else:
                raise Exception('Illegal state %s' % state)

        if current:
            current = current.rstrip(';').strip()
            if current:
                yield current