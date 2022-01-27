"""DB utilities (pyodbc based).

ODBC mit Access funktioniert nur mit 32-bit 
    solange/wenn kein 64-bit Access Treiber vorhanden.
ODBC mit Access funktioniert unter Windows 10 nur mit 2003er .mdb s 
    solange der neuere Treiber {Microsoft Access Driver (*.mdb, *.accdb)}
    unter Windows 10 nicht instanziert werden kann. 
    Der neuere Treiber wird zwar angezeigt im ODBC-Datenquellen-Administrator (32-Bit),
    man kann den Treiber dort aber auch fuer DSNs nicht instanzieren:
    "Das Betriebssystem ist momentan nicht zum Ausfuehren dieser Anwendung konfiguriert."

-v --sqlFile .\VSICS\V_VSICS.sql --mdbFile C:\3S\Modelle\FBG.mdb
"""

# Code in English.
# Beschreibungen und Kommentare (zumeist) in Deutsch.
import os
import shutil
import sys
import logging

logger = logging.getLogger('PT3S.UTILS')     
import argparse
import unittest
import doctest

import traceback

import re

import csv

import pyodbc 
# ...\Anaconda3_32\Scripts\conda.exe install -c anaconda pyodbc=3.0.10
# Ergebnis: ...\Anaconda3_32\Lib\site-packages\pyodbc-3.0.10-py3.5.egg-info

import pandas as pd

class DbError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



def getMdbConStr(mdbFile):
    mdbFile = os.path.normpath(mdbFile)
    mdbFile = os.path.abspath(mdbFile)         
    

    Driver=[x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')]
    if Driver == []:
                logStrFinal="{:s}{:s}: No Microsoft Access Driver!".format(logStr,accFile)     
                raise DbError(logStrFinal)  

    # ein Treiber ist installiert
    conStr=(
                r'DRIVER={'+Driver[0]+'};'
                r'DBQ='+mdbFile+';'
                )







    return conStr #'DRIVER={Microsoft Access Driver (*.mdb)}' + ';' + 'DBQ=' + mdbFile + ';' 

class Db:
    """DB utilities (pyodbc based).
    .
    """

    def __init__(self,conStr):
        """Datenbankverbindung herstellen.
        
        Arguments:
        conStr: Connection String
        Bsp. fuer conStr: 
            r"DRIVER={Microsoft Access Driver (*.mdb)};DBQ=.\Db.mdb;" 
            "DSN=xyz"
                Wenn DSN xyz eingerichtet ist.
        .
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            self.conStr=conStr
            logger.debug("{0:s}conStr: {1:s}.".format(logStr,self.conStr)) 
            self.open()     
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))                         
        except:
            logging.exception('')  
        finally:
            pass
            
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def close(self):
        """Datenbankverbindung schliessen.
        .
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            self.con.close()   
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))                         
        except:
            logging.exception('')  
        finally:
            pass
            
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def open(self):
        """Datenbankverbindung oeffnen.
        .
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            self.con = pyodbc.connect(self.conStr)            
            self.cur = self.con.cursor()        
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))                         
        except:
            logging.exception('')  
        finally:
            pass
            
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def executeSqlCmd(self,sqlCmd):
        """Fuehrt SQL-Befehl aus.

        Arguments:
        sqlCmd: SQL-Befehl
        Bsp. fuer sqlCmd: 
            r"CREATE TABLE TDbTest(Col1 VARCHAR(254), Col2 VARCHAR(254))" 
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            #logger.debug("{0:s}SQL:{1:s} Ausfuehrung ...".format(logStr,sqlCmd))  
            self.cur.execute(sqlCmd)
            self.con.commit()
 
        except pyodbc.Error as e:  
            logger.debug("{0:s}SQL:{1:s} Error bei Ausfuehrung ...".format(logStr,sqlCmd))  
            raise pyodbc.Error(str(e))      
        
        except Exception as e:
            logger.debug("{0:s}SQL:{1:s} Error bei Ausfuehrung ...".format(logStr,sqlCmd))  
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise DbError(logStrFinal)     
        
        finally:
            pass
            #logger.debug("{0:s}... erfolgreich!".format(logStr))
                       
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    

    def testIfExists(self,Name):
        """Prueft ob Tabelle/View Name existiert.
           
        Arguments:         
        Name: Name der Tabelle / des Views
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            nameExists=None
            tableNames = [row.table_name for row in self.cur.tables()] # VIEWS sind auch TABLES hier
            if Name in tableNames:
                nameExists=True
            else:
                nameExists=False
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))     
        except:
            logging.exception('')  
        finally:
            #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     
            return nameExists 
            
    def dropIfExists(self,Name):
        """Loescht Tabelle/View Name wenn diese existiert.
           
        Arguments:         
        Name: Name der Tabelle / des Views
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            if self.testIfExists(Name):
                dropSQL = "DROP TABLE {0:s}".format(Name) # VIEWS sind auch TABLES hier
                self.executeSqlCmd(dropSQL)

        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))     
        except:
            logging.exception('')  
        finally:
            pass
            
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def dropIfExistsFromRegExp(self,regExp):
        """Loescht alle Tabellen/Views deren Name regExp matched.
           
        Arguments:       
        regExp: Regulaerer Ausdruck
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:           
            for tableName in [row.table_name for row in self.cur.tables()]: # VIEWS sind auch TABLES hier
                if re.search(regExp,tableName) != None:
                    self.dropIfExists(tableName)
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))        
        except:
            logging.exception('')  
        finally:
            pass
            
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    

    def executeFromSqlFile(self,sqlFile,sep=';',commentPattern='--.*'):
        """Fuehrt SQL-Befehle in sqlFile aus.
        
        Mehrere SQL-Befehle muessen mit sep in sqlFile voneinander getrennt werden.    
        sep muss (abgesehen von nachfolgenden Blanks und Kommentaren) wenn das letzte Zeichen einer Zeile sein       
        Arguments:
        sqlFile: Datei mit einem oder mehreren SQL-Befehlen.
        sep: 1 Zeichen mit dem die SQL-Befehle in sqlFile voneinander getrennt sind.
        commentPattern: regExp mit der die Kommentare erkannt werden sollen.

        SQL-Befehle mit CREATE ...:
             existieren die zu erzeugenden Tabellen/Views, dann werden sie zuvor geloescht.
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:            
            # sqlFile pruefen
            sqlFile = os.path.normpath(sqlFile) # frei von Redundanzen etc.
            if not os.path.isfile(sqlFile):
                logger.error("{0:s}{1:s} ist keine Datei oder die Datei existiert nicht.".format(logStr,sqlFile))   
                sys.exit()                        
            if not os.path.isabs(sqlFile):
                 sqlFile = os.path.abspath(sqlFile) # mit absolutem Pfad
            logger.debug("{0:s}SQL-Datei:{1:s}.".format(logStr,sqlFile)) 

            # sqlFile lesen
            with open(sqlFile,'r') as f:
                sqlFileLines = f.readlines()
            logger.debug("{0:s}SQL-Datei:{1:s} gelesen.".format(logStr,sqlFile)) 

            # Bereinigungen 
            sqlFileLinesStripped=[]
            for idx,line in enumerate(sqlFileLines):
                lineStripped=line

                lineStripped = lineStripped.lstrip() # fuehrende Leerzeichen loeschen
                lineStripped = lineStripped.rstrip() # endende Leerzeichen loeschen

                #logger.debug("{0:s}lineStripped 01:{1:s}.".format(logStr,lineStripped)) 

                regExpObj = re.compile(commentPattern)
                m = regExpObj.search(lineStripped)
                if m == None:
                    pass
                else:
                    lineStripped = lineStripped.replace(m.group(0),'')   # Kommentare loeschen
                    lineStripped = lineStripped.rstrip() # ggf. neu entstandene endende Leerzeichen loeschen

                if lineStripped == '' or lineStripped == '\n':
                    continue # keine reinen Leerzeilen weiter behandeln

                # Zeilen die jetzt nicht mit sep enden (== mehrzeilge Befehle) um 1 Blank ergaenzen
                # andernfalls koennten beim Verketten Syntaxfehler entstehen
                # sowie
                # Zeilen die mit sep enden mit sepExtension enden lassen
                # andernfalls koennte beim Splitten der Verkettung nach nur sep z.B. auch hier ';' faelschlicher eine Befehlstrennung vorgenommen werden
                sepExtension = '@'+'#'+sep # 
                regExpObj = re.compile(sep+'$')
                m = regExpObj.search(lineStripped)
                if m == None:
                    lineStripped=lineStripped+' '
                else:
                    lineStripped = lineStripped.replace(m.group(0),sepExtension) 
                #logger.debug("{0:s}lineStripped 02:{1:s}.".format(logStr,lineStripped)) 
                  
                sqlFileLinesStripped.append(lineStripped)

            # Bereinigungen fertig 
            for idx,lineStripped in enumerate(sqlFileLinesStripped):
                pass
                #logger.debug("{0:s}lineStripped Nr. {1:d}:{2:s}.".format(logStr,idx,lineStripped)) 
            
            # sqlFile in 1 string um diesen dann in SQL-Befehle zu splitten
            sqlCommandsAsOneString = ''
            for line in sqlFileLinesStripped:
                sqlCommandsAsOneString+=line
            #logger.debug("{0:s}sqlCommandsAsOneString:{1:s}.".format(logStr,sqlCommandsAsOneString)) 
            sqlCommandLst = sqlCommandsAsOneString.split(sepExtension)
            if sqlCommandLst[-1] == '':
                # der letzte Befehl ist "leer" weil auch die letzte Befehlssequenz mit sep abgeschlossen wurde 
                del sqlCommandLst[-1]

            # SQL-Befehle fertig
            for idx,sqlCommand in enumerate(sqlCommandLst):
                pass
                #logger.debug("{0:s}sqlCommand Nr. {1:d}:{2:s}.".format(logStr,idx,sqlCommand))                 
         
            # DROPs ermitteln
            regExpObj = re.compile('^CREATE(\s+)(\w+)(\s+)(\w+)')     
            dropCommandLst = ['DROP' + ' ' + regExpObj.search(sqlCommand.upper()).group(2) + ' ' + regExpObj.search(sqlCommand).group(4) 
                                 for sqlCommand in sqlCommandLst if regExpObj.search(sqlCommand.upper()) != None]
            for idx,dropCommand in enumerate(dropCommandLst):
                pass
                #logger.debug("{0:s}dropCommand Nr. {1:d}:{2:s}.".format(logStr,idx,dropCommand))    
          
            # DROPs absetzen
            regExpObj = re.compile('^DROP (\w+) (\w+)')     
            for sqlCommand in dropCommandLst:
                Name = regExpObj.search(sqlCommand).group(2)
                self.dropIfExists(Name)

            # SQL-Befehle absetzen
            for idx,sqlCommand in enumerate(sqlCommandLst):
                #logger.debug("{0:s}SQL Nr. {1:d}:{2:s}.".format(logStr,idx+1,sqlCommand))  
                self.cur.execute(sqlCommand)
                self.con.commit()
        
        except SystemExit:
            logger.error('{0:s}SytemExit Exeption.'.format(logStr))
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))        
        except:
            logging.exception('')  
        finally:
            pass
            
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))             

    def selectSmart(self,vt_Name):
        """Gibt den Inhalt von vt_Name wie folgt zurueck:
        rows [][]
        ,colNames []
        ,colTypes []
        ,colSizes []
        ,dicts [{}]
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:            
            rows=None   
            colNames=None
            colTypes=None
            colSizes=None
            dicts=None        

            if self.testIfExists(vt_Name) != True:
                logger.error("{0:s}Tabelle/View {1:s} existiert nicht.".format(logStr,vt_Name))         
                sys.exit(0)
               
            # Spalteninformationen auslesen
            rowsDef=self.cur.columns(vt_Name)
            colNames = [row.column_name for row in rowsDef]#self.cur.columns(vt_Name)]
            colTypes = [row.type_name   for row in rowsDef]#self.cur.columns(vt_Name)]
            colSizes = [row.column_size for row in rowsDef]#self.cur.columns(vt_Name)]
            selectStmt = "SELECT * FROM "+vt_Name
            #logger.debug("Execute {0}...".format(selectStmt))
            self.cur.execute(selectStmt)
            #logger.debug("Executed {0}.".format(selectStmt))
            
            rows = self.cur.fetchall()
            #logger.debug("{0:s} Fetched {1} rows with {2} columns.".format(logStr,len(rows), len(colNames)))
            dicts=[]
            for row in rows:
                dict={}
                for col,colName in zip(row,colNames):
                    dict[colName]=col
                dicts.append(dict)

        except SystemExit:
            logger.error('{0:s}SytemExit Exeption.'.format(logStr))
        except pyodbc.Error as e:
            logging.exception('{0:s} {1:s} {2:s}'.format(logStr, vt_Name, str(e)))
            raise pyodbc.Error('{0:s} {1:s} {2:s}'.format(logStr, vt_Name, str(e)))
        except Exception as e:
            logging.exception('{0:s} {1:s} {2:s}'.format(logStr, vt_Name, str(e)))  
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return rows,colNames,colTypes,colSizes,dicts

    def exportToCsvFile(self,Name,csvFile,csvFileMode='w',csvFileDelimiter=';',csvFileHeader=True, withPandas=True):
        """Exportiert den Inhalt von Tabelle/View Name in csvFile.
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:            
            # csvFile pruefen
            csvFile = os.path.normpath(csvFile) # frei von Redundanzen etc.
            if not os.path.isfile(csvFile):
                logger.info("{0:s}{1:s} ist keine Datei oder die Datei existiert nicht.".format(logStr,csvFile))                    
            if not os.path.isabs(csvFile):
                 csvFile = os.path.abspath(csvFile) # mit absolutem Pfad

            # Quelle pruefen
            if self.testIfExists(Name) != True:
                logger.error("{0:s}Tabelle/View {1:s} existiert nicht.".format(logStr,Name))         
                sys.exit(0)

            head,tail=os.path.split(csvFile)
            logger.debug("{0:s}csv-Datei: {1:s}: Tabelle/View {2:s} lesen und schreiben ....".format(logStr,tail,Name)) 

            if not withPandas:
                # Daten lesen
                #logger.debug("{0:s}Tabelle/View {1:s} lesen ...".format(logStr,Name))      
                rows,colNames,colTypes,colSizes,dicts = self.selectSmart(Name)

                # csvFile schreiben
                #logger.debug("{0:s}Tabelle/View {1:s} schreiben ...".format(logStr,Name))      
                with open(csvFile,csvFileMode) as f:
                    csv.register_dialect('exportToCsvFile','excel',delimiter=csvFileDelimiter,lineterminator='\n')
                    writer = csv.DictWriter(f,fieldnames=colNames,dialect='exportToCsvFile')
                    if csvFileHeader:
                        writer.writeheader()
                    writer.writerows(dicts)
            else:
                #logger.debug("{0:s}Tabelle/View {1:s} schreiben ...".format(logStr,Name))      
                df=pd.read_sql("select * from {:s}".format(Name),self.con)                
                df.to_csv(csvFile,sep=csvFileDelimiter,header=csvFileHeader,mode=csvFileMode,index=False)


        except SystemExit:
            logger.error('{0:s}SytemExit Exeption.'.format(logStr))
        except pyodbc.Error as e:  
            raise pyodbc.Error(str(e))        
        except Exception as e:
            logging.exception('{0:s} {1:s} {2:s}'.format(logStr, Name, str(e)))  
        finally:
            pass
            
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))            
        
    def readFromCsvFileWithHeader(self,csvFile,csvFileDelimiter=';'):
        """Liest den Inhalt von csvFile. Interpretiert die 1. Zeile als Spaltennamen. Gibt den Inhalt wie folgt zurueck:
        dicts [{}]
        ,rows [][] - Spalten in csvFile-Reihenfolge
        ,colNames  - SpaltenNamen in csvFile-Reihenfolge
        ,idxDct {} - Key: SpaltenName Value: SpaltenIndex im csvFile beginnend mit 0
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:            
            # csvFile pruefen
            csvFile = os.path.normpath(csvFile) # frei von Redundanzen etc.
            if not os.path.isfile(csvFile):
                logger.error("{0:s}{1:s} ist keine Datei oder die Datei existiert nicht.".format(logStr,csvFile))     
                sys.exit(0)               
            if not os.path.isabs(csvFile):
                 csvFile = os.path.abspath(csvFile) # mit absolutem Pfad
            logger.debug("{0:s}csv-Datei:{1:s}.".format(logStr,csvFile)) 

            #dicts
            csv.register_dialect('readFromCsvFile','excel',delimiter=csvFileDelimiter,lineterminator='\n')
            with open(csvFile) as f:
                reader=csv.DictReader(f,dialect='readFromCsvFile')

                # Spaltennummern von Spaltennamen
                colNames=reader.fieldnames
                #logger.debug('{0:s}Spaltennamen:{1:s}.'.format(logStr,str(colNames)))    
                idxDct={}
                for idx,colName in enumerate(colNames):
                    idxDct[colName]=idx

                dicts=[]
                for idx,dict in enumerate(reader): 
                    #logger.debug('{0:s}Dict von Zeile {1:d}:{2:s}.'.format(logStr,idx,str(dict)))    
                    dicts.append(dict)
            
            #rows - Spalten in csvFile-Reihenfolge
            rows=[]
            for idxRow,dict in enumerate(dicts):
                row=[]
                for idx,colName in enumerate(colNames):
                    row.append(dict[colName])
                rows.append(row)

        except SystemExit:
            logger.error('{0:s}SytemExit Exeption.'.format(logStr))     
        except:
            logging.exception('')  
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return dicts,rows,colNames,idxDct

    def importCsvFileWithHeaderToTable(self,tableName,csvFile,csvFileDelimiter=';'):
        """Liest den Inhalt von csvFile. Interpretiert die 1. Zeile als Spaltennamen. 
        Speichert den Inhalt in tableName.
        Wenn tableName nicht existiert wird tableName mit den erf. Spalten erzeugt.
        Wenn tableName existiert und Spalten fehlen !oder existierende Spalten nicht passen 
        wird tableName entsprechend um Spalten erweitert !oder die Spalten werden geaendert.  
        Existiert tableName muessen die existierenden _und referenzierten Spalten vom Typ Varchar sein 
        !sonst gehen die Daten dieser Spalten verloren.
        .
        """

        logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:            
            # csvFile pruefen
            csvFile = os.path.normpath(csvFile) # frei von Redundanzen etc.
            if not os.path.isfile(csvFile):
                logger.error("{0:s}{1:s} ist keine Datei oder die Datei existiert nicht.".format(logStr,csvFile))     
                sys.exit(0)               
            if not os.path.isabs(csvFile):
                 csvFile = os.path.abspath(csvFile) # mit absolutem Pfad
            logger.debug("{0:s}csv-Datei:{1:s}.".format(logStr,csvFile)) 

            # Daten lesen 
            dicts,rows,colNames,idxDct=self.readFromCsvFileWithHeader(csvFile,csvFileDelimiter=csvFileDelimiter)

            # benoetigte Spaltenbreiten feststellen
            colLengthNeeded={}
            # ueber alle Spalten
            for idx,colName in enumerate(colNames):
                colLengthNeeded[colName]=0
                for idxRow,row in enumerate(rows): # ueber alle Zeilen
                    cell=row[idx]
                    if len(cell)>colLengthNeeded[colName]:
                        colLengthNeeded[colName]=len(cell)

            # 
            self.dropIfExists(tableName)

            if self.testIfExists(tableName) != True:
                # Tabelle erzeugen
                logger.debug("{0:s}Tabelle {1:s} existiert nicht.".format(logStr,tableName))     
                createTableSQL = ",\n".join(["{0:s} VARCHAR({1:d})".format(colName,colLengthNeeded[colName]) for colName in colNames])
                createTableSQL = "CREATE TABLE {0:s} ({1:s})".format(tableName,createTableSQL)
                self.executeSqlCmd(createTableSQL)
            else:
                # Tabelle pruefen und ggf. anpassen
                pass

            # Daten importieren per INSERT
            wo = ",".join(["{0:s}".format(colName) for colName in colNames])
            for idxRow,dict in enumerate(dicts):
                was = ",".join(["'{0:s}'".format(dict[colName]) for colName in colNames])   
                insertSQL="INSERT INTO {0:s} \n({1:s}) \nVALUES({2:s})".format(tableName,wo,was)   
                self.executeSqlCmd(insertSQL)
              
        except SystemExit:
            logger.error('{0:s}SytemExit Exeption.'.format(logStr))     
        except:
            logging.exception('')  
        finally:
            pass

        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))        
            
class  test_Db(unittest.TestCase):        
        """Test von Db.
        .
        """
        def setUp(self):
            """Test von Db vorbereiten.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                                     
                # mdb
                self.mdbFile = None
                for dirpath, dirnames, filenames in os.walk('.'):
                    for filename in filenames:
                        if filename.endswith("Db.mdb"): # eine mdb-Datei suchen und verwenden
                            self.mdbFile = os.path.join(dirpath,filename)
                            break
                    if self.mdbFile != None:
                        break
                if self.mdbFile == None:
                    logger.error("{0:s}Die gewuenschte .mdb-Datei konnte nicht gefunden werden.".format(logStr)) 
                    sys.exit()
                else:
                    self.mdbFile = os.path.normpath(self.mdbFile)
                    self.mdbFile = os.path.abspath(self.mdbFile)
                    logger.debug("{0:s}Mdb-Datei: {1:s}.".format(logStr,self.mdbFile))                                                                                  
                    self.conStr = getMdbConStr(self.mdbFile)                                       
                    logger.debug("{0:s}conStr: {1:s}.".format(logStr,self.conStr))            
               
                # sql
                self.sqlFile = None
                for dirpath, dirnames, filenames in os.walk('.'):
                    for filename in filenames:
                        if filename.endswith("Db.sql"): # eine sql-Datei suchen und verwenden
                            self.sqlFile = os.path.join(dirpath,filename)
                            break
                    if self.sqlFile != None:
                        break
                if self.sqlFile == None:
                    logger.error("{0:s}Die gewuenschte .sql-Datei konnte nicht gefunden werden.".format(logStr)) 
                    sys.exit()
                else:
                    self.sqlFile = os.path.normpath(self.sqlFile)
                    self.sqlFile = os.path.abspath(self.sqlFile)
                    logger.debug("{0:s}Sql-Datei: {1:s}.".format(logStr,self.sqlFile))   

                # csv (Export)
                (root,ext) = os.path.splitext(self.sqlFile)
                self.csvFile = root+'.csv'
                logger.debug("{0:s}Csv-Datei: {1:s}.".format(logStr,self.csvFile))   

                # csv (Import)
                self.csvFileImport=self.csvFile.replace('Db.csv','DbImport.csv')
                logger.debug("{0:s}Csv-Datei Import: {1:s}.".format(logStr,self.csvFileImport))   

                # Name der Testtabelle
                self.tableName='T_Db'
                                
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                pass
           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))           

        #@unittest.skip(".")
        def test_01_InitDbNichtda(self):
            """Test von InitDbNichtda.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
               
            self.assertRaisesRegex(pyodbc.Error,'nicht gefunden',Db,self.conStr.replace('Db.mdb','DbNichtda.mdb'))

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        #@unittest.skip(".")
        def test_02_InitDb2016(self):
            """Test von InitDb2016.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            self.assertRaisesRegex(pyodbc.Error,'nicht von Ihrer Anwendung erkannt',Db,self.conStr.replace('Db.mdb','Db2016.mdb'))

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 
 
        #@unittest.skip(".")
        def test_03_Init(self):
            """Test von Init.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                self.assertIsInstance(obj.con,pyodbc.Connection,msg='con nicht vom Typ pyodbc.Connection')    
                self.assertIsInstance(obj.cur,pyodbc.Cursor,msg='cur nicht vom Typ pyodbc.Cursor')                              
            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))  
                raise pyodbc.Error                                
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 
 
        #@unittest.skip(".")
        def test_04_DropIfExists(self):
            """Test von DropIfExists.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                obj.dropIfExists(self.tableName)      
            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))     
                raise pyodbc.Error                                       
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        #@unittest.skip(".")
        def test_05_DropIfExistsFromRegExp(self):
            """Test von DropIfExistsFromRegExp.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                obj.dropIfExistsFromRegExp('^'+self.tableName)      
            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))     
                raise pyodbc.Error                                       
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        #unittest.skip(".")
        def test_06_ExecuteSqlCommand(self):
            """Test von ExecuteSqlCommand.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                obj.dropIfExists(self.tableName)      
                obj.executeSqlCmd("CREATE TABLE "+self.tableName+"(Col1 VARCHAR(254), Col2 VARCHAR(254))")

                obj.executeSqlCmd("INSERT INTO "+self.tableName+"(Col1, Col2) VALUES ('11','12')")
                obj.executeSqlCmd("INSERT INTO "+self.tableName+"(Col1, Col2) VALUES ('21','Bug')")
                obj.executeSqlCmd("UPDATE      "+self.tableName+" SET Col2='22' WHERE Col2='Bug'")

                obj.executeSqlCmd("INSERT INTO "+self.tableName+"(Col1) VALUES ('Bug')")
                obj.executeSqlCmd("DELETE FROM "+self.tableName+" WHERE Col1='Bug'")
                
                obj.cur.execute("SELECT * FROM "+self.tableName)
                rows = obj.cur.fetchall()
                for idxRow,row in enumerate(rows):
                    for idxCol, cell in enumerate(row):
                         logger.debug("{0:s}{1:s}".format(logStr,cell))
                
                self.assertEqual(rows[0][0],'11')
                self.assertEqual(rows[0][1],'12')
                self.assertEqual(rows[1][0],'21')
                self.assertEqual(rows[1][1],'22')

            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))     
                raise pyodbc.Error                                                                  
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        def test_07_ExecuteFromSqlFile(self):
            """Test von ExecuteFromSqlFile.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

          
            try:
                obj=Db(self.conStr)
                # Testtabelle T_Db existiert noch 2x2 aus vorherigen Tests
                obj.executeFromSqlFile(self.sqlFile)

                obj.cur.execute("SELECT * FROM "+self.tableName)
                rows = obj.cur.fetchall()
                for idxRow,row in enumerate(rows):
                    for idxCol, cell in enumerate(row):
                         logger.debug("{0:s}{1:s}".format(logStr,cell))
                
                self.assertEqual(rows[0][0],'11')
                self.assertEqual(rows[0][1],'12')
                self.assertEqual(rows[1][0],'21')
                self.assertEqual(rows[1][1],'22FileDb.sql')

            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))    
                raise pyodbc.Error                                                                   
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        def test_08_ExportToCsvFile(self):
            """Test von ExportToCsvFile und ReadFromCsvFile.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                # Testtabelle T_Db existiert noch 2x2 aus vorherigen Tests
                obj.exportToCsvFile(self.tableName,self.csvFile,csvFileDelimiter=';')
                obj.exportToCsvFile(self.tableName,self.csvFile,csvFileMode='a',csvFileHeader=None)

                dicts,rows,colNames,idxDct=obj.readFromCsvFileWithHeader(self.csvFile,csvFileDelimiter=';')
               
                self.assertEqual(dicts[0],dicts[2])
                self.assertEqual(dicts[1],dicts[3])
                self.assertEqual('22FileDb.sql',dicts[1]['Col2'])

                self.assertEqual(rows[0],rows[2])
                self.assertEqual(rows[1],rows[3])
                self.assertEqual('22FileDb.sql',rows[1][1])
                
            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))    
                raise pyodbc.Error                                                                   
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 

        def test_09_ImportCsvFileWithHeaderToTable(self):
            """Test von ImportCsvFileWithHeaderToTable.
            .
            """

            logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:
                obj=Db(self.conStr)
                obj.importCsvFileWithHeaderToTable(self.tableName,self.csvFileImport,csvFileDelimiter=';')
                rows,colNames,colTypes,colSizes,dicts=obj.selectSmart(self.tableName)
                self.assertEqual('22FileDbImport.csv',rows[1][1])
                
            except pyodbc.Error as e:
                logger.error('{0:s}Unerwartete Exception:{1:s} erhalten:{2:s}.'.format(logStr,'pyodbc.Error',str(e)))    
                raise pyodbc.Error                                                                   
            finally:
                pass

            logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 
              
if __name__ == "__main__":
    """.
    .
    """

    try:              
        # Logfile
        head,tail = os.path.split(__file__)
        file,ext = os.path.splitext(tail)
        logFileName = os.path.normpath(os.path.join(head,os.path.normpath('./Test'))) # Ablage des Logfiles auf Unterverzeichnis Test
        logFileName = os.path.join(logFileName,file + '.log') # Dateiname des Logfiles wie diese Datei - nur mit .log statt .py
        
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

        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
                                      
        # Argumente parsen      
        parser = argparse.ArgumentParser()
        parser.add_argument("--sqlFile",type=str, help="file with SQL-Commands (.sql-File) to be executed in Access Database")    
        parser.add_argument("--mdbFile",type=str, help="Access Database (.mdb-File)")                
        parser.add_argument("-v","--verbose", help="Debug Messages On", action="store_true")               
        args = parser.parse_args()

        if args.verbose:           
            logger.setLevel(logging.DEBUG)                   
        logger.debug("{0:s}{1:s}{2:s}".format(logStr,'Start. Argumente:',str(sys.argv))) 

        if args.sqlFile and args.mdbFile:
            # Scripting-Einsatz
            sqlFile = args.sqlFile 
            mdbFile = args.mdbFile
            conStr=getMdbConStr(mdbFile)
            obj = Db(conStr)
            obj.executeFromSqlFile(sqlFile)
            obj.close()
            
        else:
            # Selbsttest
            # WD: .\UTILS
            # Arguments: -v
            unittest.main(verbosity=2)
                                                     
    except:
        logger.error("{0:s}{1:s}".format(logStr,'logging.exception!')) 
        logging.exception('')  
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 
        sys.exit(0)



