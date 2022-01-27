"""

"""

__version__='90.12.4.23.dev1'

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

import pyodbc

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

try:
    from PT3S import Dm
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Dm - trying import Dm instead ... maybe pip install -e . is active ...')) 
    import Dm

try:
    from PT3S import Xm
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Xm - trying import Xm instead ... maybe pip install -e . is active ...')) 
    import Xm
   
class AmError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Am():
    """SIR 3S AccessDB to pandas DataFrames.

    Args:
        * accFile (str): SIR 3S AccessDB
           
    Attributes:
        * dataFrames: enthaelt alle gelesenen Tabellen und konstruierten Views

        * viewSets: fasst View- bzw. Tabellennamen zu Kategorien zusammen; dient zur Uebersicht bei Bedarf

        * zu den Spaltennamen der Views:
            * grundsaetzlich die Originalnamen - aber ...
                * bei den _BVZ_ Views:
                    * :_BZ, wenn Spalten Namensgleich
                * Datenebenen:
                    * _VMBZ,_VMVARIANTE,_VMBASIS, wenn Spalten Namensgleich
                * CONT:
                    * immer _CONT
                * VKNO:
                    * immer _VKNO
                * VBEL:
                    * immer _i und _k fuer die Knotendaten

        * V3-Views i.e. dataFrames['V3_KNOT']
            * V3_SWVT
                * 1 Zeile pro ZEIT und W; cols sind NAMEn der SWVT 
            * V3_RSLW_SWVT
                * 1 Zeile pro RSLW der aktiv eine SWVT referenziert
            * V3_KNOT: Knoten: "alle" Knotendaten                
            * V3_VBEL: Kanten: "alle" Verbindungselementdaten des hydr. Prozessmodells
                * Multiindex:
                    * OBJTYPE
                    * OBJID (pk)
            * V3_DPKT: ausgewaehlte Daten von Datenpunkten
            * V3_RKNOT: Knotendaten des Signalmodells
                * Kn: Knotenname
                * OBJTYPE: der Typname des Elementes des Signalmodells z.B. RADD
            * V3_RRUES: 
                * wie V_BVZ_RUES - mit folgenden zusaetzlichen Spalten:

                    * pk_DEF	
                    * IDUE_DEF	
                    * OBJTYPE_SRC:      RXXX-Objekttyp der das Signal definiert welches die Ue repraesentiert	
                    * OBJID_SRC:        ID des RXXX der das Signal definiert welches die Ue repraesentiert	
                    * Kn_SRC:           Signal fuer das die Ue ein Alias ist (KA des RXXX)
                    * NAME_CONT_SRC:    Block in dem das Signal definiert wird (das RXXX-Element liegt)

            * V3_RVBEL: Kantendaten des Signalmodells
                * Multiindex:
                    * OBJTYPE_i
                    * OBJTYPE_k
                * RUES-RUES fehlen
                * RUES-RXXX sind in den Spalten 'OBJTYPE_i','OBJID_i','Kn_i','KnExt_i','NAME_CONT_i' durch die RUES-Quelle ersetzt
                * G=nx.from_pandas_edgelist(df=V3_RVBEL.reset_index(), source='Kn_i', target='Kn_k', edge_attr=True)

        * viewSets['pairViews_BZ']:
            * ['V_BVZ_ALLG'
            *, 'V_BVZ_BEVE', 'V_BVZ_BEWI', 'V_BVZ_BZAG'
            *, 'V_BVZ_DPGR', 'V_BVZ_DPRG'
            *, 'V_BVZ_EBES'
            *, 'V_BVZ_FKNL', 'V_BVZ_FQPS', 'V_BVZ_FWEA', 'V_BVZ_FWES', 'V_BVZ_FWVB', 'V_BVZ_FWWU'
            *, 'V_BVZ_GVWK'
            *, 'V_BVZ_HYDR'
            *, 'V_BVZ_KLAP', 'V_BVZ_KNOT', 'V_BVZ_KOMP'
            *, 'V_BVZ_LFAL'
            *, 'V_BVZ_MREG'
            *, 'V_BVZ_NSCH'
            *, 'V_BVZ_OBEH'
            *, 'V_BVZ_PARI', 'V_BVZ_PARZ', 'V_BVZ_PGRP', 'V_BVZ_PGRP_PUMP', 'V_BVZ_PHTR', 'V_BVZ_PREG', 'V_BVZ_PUMP', 'V_BVZ_PZVR'
            *, 'V_BVZ_RADD', 'V_BVZ_RART', 'V_BVZ_RDIV', 'V_BVZ_REGV', 'V_BVZ_RFKT', 'V_BVZ_RHYS', 'V_BVZ_RINT', 'V_BVZ_RLSR', 'V_BVZ_RLVG', 'V_BVZ_RMES', 'V_BVZ_RMMA', 'V_BVZ_RMUL'
            *, 'V_BVZ_ROHR'
                * erweitert um folgende DTRO-Daten: ['NAME_DTRO','DN', 'DI', 'DA', 'S', 'KT', 'PN']
            *, 'V_BVZ_RPID', 'V_BVZ_RPT1', 'V_BVZ_RSLW', 'V_BVZ_RSTE', 'V_BVZ_RSTN', 'V_BVZ_RTOT', 'V_BVZ_RUES'
            *, 'V_BVZ_SIVE', 'V_BVZ_SLNK', 'V_BVZ_SNDE', 'V_BVZ_STRO'
            *, 'V_BVZ_VENT'
            *, 'V_BVZ_WIND']
        * viewSets['pairViews_ROWS']:
            * ['V_BVZ_ANTE', 'V_BVZ_ANTP', 'V_BVZ_AVOS', 'V_BVZ_DPGR', 'V_BVZ_ETAM', 'V_BVZ_ETAR', 'V_BVZ_ETAU', 'V_BVZ_KOMK', 'V_BVZ_MAPG'
            *, 'V_BVZ_PHI2', 'V_BVZ_PHIV', 'V_BVZ_PUMK', 'V_BVZ_RPLAN', 'V_BVZ_SRAT', 'V_BVZ_STOF', 'V_BVZ_TFKT', 'V_BVZ_TRFT', 'V_BVZ_ZEP1', 'V_BVZ_ZEP2']
        * viewSets['pairViews_ROWT']:
            * ['V_BVZ_LFKT', 'V_BVZ_PHI1', 'V_BVZ_PUMD', 'V_BVZ_PVAR', 'V_BVZ_QVAR'
            *, 'V_BVZ_RCPL' # da RCPL_ROWT existiert "landet" RCPL bei den ROWTs; es handelt sich aber bei RCPL_ROWT um gar keine Zeittabelle
            *, 'V_BVZ_SWVT', 'V_BVZ_TEVT', 'V_BVZ_WEVT', 'V_BVZ_WTTR']
            * enthalten alle Zeiten
            * Spalte lfdNrZEIT beginnt mit 1 fuer die chronologisch 1. Zeit
        * viewSets['pairViews_ROWD']:
            * ['V_BVZ_DTRO']
        * viewSets['notPairViews']:
            * ['V_AB_DEF', 'V_AGSN', 'V_ARRW', 'V_ATMO'
            *, 'V_BENUTZER', 'V_BREF'
            *, 'V_CIRC', 'V_CONT', 'V_CRGL'
            *, 'V_DATENEBENE', 'V_DPGR_DPKT', 'V_DPKT', 'V_DRNP'
            *, 'V_ELEMENTQUERY'
            *, 'V_FSTF', 'V_FWBZ'
            *, 'V_GKMP', 'V_GMIX', 'V_GRAV', 'V_GTXT'
            *, 'V_HAUS'
            *, 'V_LAYR', 'V_LTGR'
            *, 'V_MODELL', 'V_MWKA'
            *, 'V_NRCV'
            *, 'V_OVAL'
            *, 'V_PARV', 'V_PGPR', 'V_PLYG', 'V_POLY', 'V_PROZESSE', 'V_PZON'
            *, 'V_RCON', 'V_RECT', 'V_REGP', 'V_RMES_DPTS', 'V_ROHR_VRTX', 'V_RPFL', 'V_RRCT'
            *, 'V_SIRGRAF', 'V_SOKO', 'V_SPLZ', 'V_STRASSE', 'V_SYSTEMKONFIG'
            *, 'V_TIMD', 'V_TRVA'
            *, 'V_UTMP'
            *, 'V_VARA', 'V_VARA_CSIT', 'V_VARA_WSIT', 'V_VERB', 'V_VKNO', 'V_VRCT'
            *, 'V_WBLZ']

    Raises:
        AmError
    """

               
    def __init__(self,accFile):

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             
            if os.path.exists(accFile):  
                if os.access(accFile,os.W_OK):
                    pass
                else:
                    logger.debug("{:s}accFile: {:s}: Not writable.".format(logStr,accFile)) 
                    if os.access(accFile,os.R_OK):
                        pass
                    else:
                        logStrFinal="{:s}accFile: {:s}: Not readable!".format(logStr,accFile)     
                        raise AmError(logStrFinal)  
            else:
                logStrFinal="{:s}accFile: {:s}: Not existing!".format(logStr,accFile)     
                raise AmError(logStrFinal)  
          
            # die MDB existiert und ist lesbar
            logger.debug("{:s}accFile (abspath): {:s}".format(logStr,os.path.abspath(accFile))) 
           
            Driver=[x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')]
            if Driver == []:
                logStrFinal="{:s}{:s}: No Microsoft Access Driver!".format(logStr,accFile)     
                raise AmError(logStrFinal)  

            # ein Treiber ist installiert
            conStr=(
                r'DRIVER={'+Driver[0]+'};'
                r'DBQ='+accFile+';'
                )
            logger.debug("{0:s}conStr: {1:s}".format(logStr,conStr)) 

            # Verbindung ...
            con = pyodbc.connect(conStr)
            cur = con.cursor()

            # all Tables in DB
            tableNames=[table_info.table_name for table_info in cur.tables(tableType='TABLE')]
            logger.debug("{0:s}tableNames: {1:s}".format(logStr,str(tableNames))) 
            allTables=set(tableNames)
          
            # pandas DataFrames
            self.dataFrames={}

            # Mengen von Typen von Tabellen und Views
            pairTables=set()
            pairViews=set()
            pairViews_BZ=set()
            pairViews_ROWS=set()
            pairViews_ROWT=set()
            pairViews_ROWD=set()

            # SIR 3S Grundtabellen und -views lesen
            try:
                dfViewModelle=pd.read_sql('select * from VIEW_MODELLE',con)
            except pd.io.sql.DatabaseError as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.error(logStrFinal) 
                raise AmError(logStrFinal)
            
            try:
                dfCONT=pd.read_sql('select * from CONT',con)
            except pd.io.sql.DatabaseError as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.error(logStrFinal) 
                raise AmError(logStrFinal)   

            try:
                dfKNOT=pd.read_sql('select * from KNOT',con)
            except pd.io.sql.DatabaseError as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.error(logStrFinal) 
                raise AmError(logStrFinal)   

            # Paare
            for pairType in ['_BZ','_ROWS','_ROWT','_ROWD']:
                logger.debug("{0:s}pairType: {1:s}: ####".format(logStr,pairType)) 
                tablePairsBVBZ=[(re.search('(?P<BV>[A-Z,1,2]+)('+pairType+')$',table_info.table_name).group('BV'),table_info.table_name) for table_info in cur.tables(tableType='TABLE') if re.search('(?P<BV>[A-Z,1,2]+)('+pairType+')$',table_info.table_name) != None]
                for (BV,BZ) in tablePairsBVBZ:

                    if BV not in tableNames:
                        logger.debug("{0:s}BV: {1:s}: Tabelle gibt es nicht. Falsche Paar-Ermittlung? Weiter. ".format(logStr,BV)) 
                        continue
                    if BZ not in tableNames:
                        logger.debug("{0:s}BZ: {1:s}: Tabelle gibt es nicht. Falsche Paar-Ermittlung? Weiter. ".format(logStr,BZ)) 
                        continue
                    
                    if BZ == 'PGRP_PUMP_BZ': # BV: PUMP BVZ: PGRP_PUMP_BZ V: V_PUMP - Falsch!; wird unten ergaenzt
                        continue

                    # TabellenNamen in entspr. Mengen abspeichern
                    pairTables.add(BV)
                    pairTables.add(BZ)      

                    # VName
                    VName='V_BVZ_'+BV                    
                    logger.debug("{0:s}BV: {1:s} BVZ: {2:s} V: {3:s} ...".format(logStr,BV,BZ,VName))   
                                        
                    df,dfBV,dfBZ=Dm.f_HelperBVBZ(
                                    con
                                   ,BV
                                   ,BZ                                 
                                    )
                    self.dataFrames[BV]=dfBV
                    self.dataFrames[BZ]=dfBZ

                    df=Dm.f_HelperDECONT(
                        df
                       ,dfViewModelle 
                       ,dfCONT
                        )
                    
                    if pairType=='_ROWT':                             
                        if 'ZEIT' in df.columns.to_list():
                            df['lfdNrZEIT']=df.sort_values(['pk','ZEIT'],ascending=True).groupby(['pk'])['ZEIT'].cumcount(ascending=True)+1
                        else:
                            logger.debug("{0:s}ROWT: {1:s} hat keine Spalte ZEIT?!".format(logStr,VName))   

                    # View abspeichern                    
                    self.dataFrames[VName]=df                    

                    # ViewName in entspr. Menge abspeichern                
                    pairViews.add(VName)
                    if pairType=='_BZ':
                        pairViews_BZ.add(VName)
                    elif pairType=='_ROWS':
                        pairViews_ROWS.add(VName)
                    elif pairType=='_ROWT':                        
                        pairViews_ROWT.add(VName)
                    elif pairType=='_ROWD':
                        pairViews_ROWD.add(VName)

            # BVZ-Paare Nachzuegler
            for (BV,BZ) in [('PGRP_PUMP','PGRP_PUMP_BZ')]:
                                       
                    df,dfBV,dfBZ=Dm.f_HelperBVBZ(
                                    con
                                   ,BV
                                   ,BZ                              
                                    )      
                    self.dataFrames[BV]=dfBV
                    self.dataFrames[BZ]=dfBZ                    

                    df=Dm.f_HelperDECONT(
                        df
                       ,dfViewModelle 
                       ,dfCONT
                        )
                                                   
                    VName='V_BVZ_'+BV                    
                    self.dataFrames[VName]=df
                    logger.debug("{0:s}BV: {1:s} BVZ: {2:s} V: {3:s}".format(logStr,BV,BZ,VName)) 

                    pairTables.add(BV)
                    pairTables.add(BZ)

                    pairViews.add(VName)
                    pairViews_BZ.add(VName)

            # Nicht-Paare             
            notInPairTables=sorted(allTables-pairTables)           
            notInPairTablesW=[ # W: "Sollwert"; erwartete SIR 3S Tabellen, die nicht Paare sind
                'AB_DEF', 'AGSN', 'ARRW', 'ATMO'
               ,'BENUTZER', 'BREF'
               ,'CIRC', 'CONT', 'CRGL'
               ,'DATENEBENE'
               ,'DPGR_DPKT'
               ,'DPKT' # 90-12 ein Paar
               ,'DRNP'
               ,'ELEMENTQUERY'
               ,'FSTF', 'FWBZ'
               ,'GEOMETRY_COLUMNS' # 90-12
               ,'GKMP', 'GMIX', 'GRAV', 'GTXT'
               ,'HAUS'
               ,'LAYR', 'LTGR'
               ,'MODELL'
               ,'MWKA' # nicht 90-12
               ,'NRCV'
               ,'OVAL'
               ,'PARV', 'PGPR', 'PLYG', 'POLY', 'PROZESSE', 'PZON'
               ,'RCON', 'RECT', 'REGP'
               ,'RMES_DPTS'#, 'RMES_DPTS_BZ'
               ,'ROHR_VRTX', 'RPFL', 'RRCT'
               ,'SIRGRAF', 'SOKO', 'SPLZ', 'STRASSE', 'SYSTEMKONFIG'
               ,'TIMD', 'TRVA'
               ,'UTMP'
               ,'VARA', 'VARA_CSIT', 'VARA_WSIT', 'VERB', 'VKNO', 'VRCT'
               ,'WBLZ']
            
            # erwartete SIR 3S Tabellen, die nicht Paare sind
            notPairTables=set()        
            notPairViews=set()            
            for tableName in  notInPairTablesW: 


                 if tableName not in tableNames:
                        logger.debug("{0:s}tableName: {1:s}: Tabelle gibt es nicht - falsche Annahme in diesem Modul bzgl. der existierenden SIR 3S Tabellen? Weiter. ".format(logStr,tableName)) 
                        continue

                 sql='select * from '+tableName 
                 try:
                        df=pd.read_sql(sql,con)
                        self.dataFrames[tableName]=df
                        notPairTables.add(tableName)
                 except pd.io.sql.DatabaseError as e:
                        logger.info("{0:s}sql: {1:s}: Fehler?! Weiter. ".format(logStr,sql)) 
                        continue

                 df=Dm.f_HelperDECONT(
                    df
                   ,dfViewModelle 
                   ,dfCONT
                    )
              
                 VName='V_'+tableName
                 logger.debug("{0:s}V: {1:s}".format(logStr,VName)) 
                 self.dataFrames[VName]=df
                 notPairViews.add(VName)

            # unerwartete Tabellen
            notPairViewsProbablyNotSir3sTables=set()       
            notPairTablesProbablyNotSir3sTables=set()       
            for tableName in  set(notInPairTables)-set(notInPairTablesW):

                 logger.debug("{0:s}tableName: {1:s}: Tabelle keine SIR 3S Tabelle aus Sicht dieses Moduls. Trotzdem lesen. ".format(logStr,tableName)) 

                 sql='select * from '+tableName 
                 try:
                        df=pd.read_sql(sql,con)
                        self.dataFrames[tableName]=df
                        notPairTablesProbablyNotSir3sTables.add(tableName)
                 except pd.io.sql.DatabaseError as e:
                        logger.debug("{0:s}sql: {1:s}: Fehler?! Weiter. ".format(logStr,sql)) 
                        continue

                 df=Dm.f_HelperDECONT(
                    df
                   ,dfViewModelle 
                   ,dfCONT
                    )
                 
                 VName='V_'+tableName
                 logger.debug("{0:s}V: {1:s}".format(logStr,VName)) 
                 self.dataFrames[VName]=df
                 notPairViewsProbablyNotSir3sTables.add(VName)

            self.viewSets={}

            self.viewSets['allTables']=sorted(allTables)
            self.viewSets['pairTables']=sorted(pairTables)
            
            self.viewSets['pairViews']=sorted(pairViews)
            self.viewSets['pairViews_BZ']=sorted(pairViews_BZ)
            self.viewSets['pairViews_ROWS']=sorted(pairViews_ROWS)
            self.viewSets['pairViews_ROWT']=sorted(pairViews_ROWT)
            self.viewSets['pairViews_ROWD']=sorted(pairViews_ROWD)
            
            self.viewSets['notPairTables']=sorted(notPairTables)
            self.viewSets['notPairTablesProbablyNotSir3sTables']=sorted(notPairTablesProbablyNotSir3sTables)
            self.viewSets['notPairViews']=sorted(notPairViews)
            self.viewSets['notPairViewsProbablyNotSir3sTables']=sorted(notPairViewsProbablyNotSir3sTables)

            # ROHR um u.a. DN erweitern           
            df=pd.merge(self.dataFrames['V_BVZ_ROHR'],self.dataFrames['V_BVZ_DTRO'],left_on='fkDTRO_ROWD',right_on='pk_BZ',suffixes=('','_DTRO'))
            df=df.filter(items=self.dataFrames['V_BVZ_ROHR'].columns.to_list()+['NAME','DN', 'DI', 'DA', 'S', 'KT', 'PN'])
            df.rename(columns={'NAME':'NAME_DTRO'},inplace=True)
            self.dataFrames['V_BVZ_ROHR']=df

            # V3_SWVT, V3_RSLW_SWVT
            logger.debug("{0:s}{1:s} ...".format(logStr,'V3_RSLW_SWVT'))     

            # 1 Zeile pro RSLW der aktiv eine SWVT referenziert
            # NAME_SWVT_Nr gibt an, um die wie-vielte Referenz derselben SWVT es sich handelt
            # NAME_SWVT_NrMax gibt die max. Anzahl der Referenzierungen an; typischerwweise sollte NAME_SWVT_NrMax=1 sein für alle SWVT
            # (ZEIT, count)	... (W, max) sind Aggregate der referenzierten SWVT

            vRSLW=self.dataFrames['V_BVZ_RSLW']
            vSWVT=self.dataFrames['V_BVZ_SWVT'].sort_values(by=['pk','NAME','ZEIT'])

            V3_SWVT=vSWVT.pivot_table(index='ZEIT', columns='NAME', values='W',aggfunc='last')
            self.dataFrames['V3_SWVT']=V3_SWVT

            # Sollwertgeber ...
            vRSLW_SWVTAll=pd.merge(vRSLW,vSWVT.add_suffix('_SWVT'),left_on='fkSWVT',right_on='pk_SWVT')
            vRSLW_SWVTAll=vRSLW_SWVTAll[vRSLW_SWVTAll['INDSLW'].isin([1])] # die aktiv eine Sollwerttabelle referenzieren ...   
            vRSLW_SWVT=vRSLW_SWVTAll[vRSLW_SWVTAll['lfdNrZEIT_SWVT'].isin([1])]#.copy(deep=True) #  nur 1 Zeile pro Sollwerttabelle
            
            vRSLW_SWVT=vRSLW_SWVT.copy(deep=True)


            vRSLW_SWVT['NAME_SWVT_Nr']=vRSLW_SWVT.groupby(by=['NAME_SWVT'])['NAME_SWVT'].cumcount()+1
            vRSLW_SWVT['NAME_SWVT_NrMax']=vRSLW_SWVT.groupby(by=['NAME_SWVT'])['NAME_SWVT_Nr'].transform(pd.Series.max)

            #  Aggregate einer SWVT
            df=vSWVT.groupby(by=['NAME']).agg(
            {'ZEIT':['count','first', 'min','last','max']
            ,'W':['count','first', 'min','last','max']
            }   
            )
            df.columns = df.columns.to_flat_index()
            
            # diese Aggregate verfuegbar machen
            self.dataFrames['V3_RSLW_SWVT']=pd.merge(vRSLW_SWVT,df,left_on='NAME_SWVT',right_on='NAME')

            logger.debug("{0:s}{1:s} ...".format(logStr,'V3_KNOT'))     
            # KNOT (V3_KNOT) - "alle" Knotendaten
            vKNOT=Dm.f_HelperVKNO(
                    self.dataFrames['V_BVZ_KNOT']
                   ,self.dataFrames['V_VKNO']                   
                    )            
            self.dataFrames['V3_KNOT']=vKNOT

            logger.debug("{0:s}{1:s} ...".format(logStr,'V3_VBEL'))     
            # VBEL (V3_VBEL) - "alle" Verbindungselementdaten des hydr. Prozessmodells; Knotendaten mit _i und _k             
            vVBEL_UnionList=[]
            for vName in self.viewSets['pairViews_BZ']:                
                dfVBEL=self.dataFrames[vName]
                if 'fkKI' in dfVBEL.columns.to_list():
                    df=pd.merge(dfVBEL,vKNOT.add_suffix('_i'),left_on='fkKI',right_on='pk_i'                                
                                )           
                    if 'fkKK' in df.columns.to_list():
                        df=pd.merge(df,vKNOT.add_suffix('_k'),left_on='fkKK',right_on='pk_k'                                    
                                    )
                        m=re.search('^(V_BVZ_)(\w+)',vName)         
                        OBJTYPE=m.group(2)
                        df=df.assign(OBJTYPE=lambda x: OBJTYPE)

                        logger.debug("{0:s}{1:s} in VBEL-View ...".format(logStr,OBJTYPE))     
                        vVBEL_UnionList.append(df)
                    elif 'KNOTK' in df.columns.to_list():
                        # Nebenschlusselement
                        pass
                        df=pd.merge(df,vKNOT.add_suffix('_k'),left_on='fkKI',right_on='pk_k'                                    
                                    )
                        m=re.search('^(V_BVZ_)(\w+)',vName)         
                        OBJTYPE=m.group(2)
                        df=df.assign(OBJTYPE=lambda x: OBJTYPE)

                        logger.debug("{0:s}{1:s} (Nebenschluss) in VBEL-View ...".format(logStr,OBJTYPE))     
                        vVBEL_UnionList.append(df)

            vVBEL=pd.concat(vVBEL_UnionList)
            vVBEL=Xm.Xm.constructNewMultiindexFromCols(df=vVBEL,mColNames=['OBJTYPE','pk'],mIdxNames=['OBJTYPE','OBJID'])
            vVBEL.sort_index(level=0,inplace=True)
            self.dataFrames['V3_VBEL']=vVBEL

            logger.debug("{0:s}{1:s} ...".format(logStr,'V3_DPKT'))     
            # DPKT (V3_DPKT) - relevante Datenpunktdaten   
            if 'V_DPKT' in self.dataFrames.keys():
                vDPKT=self.dataFrames['V_DPKT']                
            elif 'V_BVZ_DPKT' in self.dataFrames.keys():
                vDPKT=self.dataFrames['V_BVZ_DPKT']            
            vDPKT_DPGR1=pd.merge(vDPKT,self.dataFrames['V_DPGR_DPKT'],left_on='pk',right_on='fkDPKT',suffixes=('','_DPGR1')) # fk der DPGR ermitteln
            vDPKT_DPGR=pd.merge(vDPKT_DPGR1,self.dataFrames['V_BVZ_DPGR'],left_on='fkDPGR',right_on='pk',suffixes=('','_DPGR')) # Daten der DPGR (vor allem der NAME der DPGR)
            try:
                self.dataFrames['V3_DPKT']=vDPKT_DPGR[[
                  'pk'
                 ,'OBJTYPE'
                 ,'fkOBJTYPE'
                 ,'ATTRTYPE'
                 ,'EPKZ'
                 ,'TITLE'
                 ,'UNIT'
                 ,'FLAGS'             
                 ,'CLIENT_ID'
                 ,'OPCITEM_ID'
                 ,'DESCRIPTION'
                 # ---
                 ,'pk_DPGR'
                 ,'NAME'
                ]].drop_duplicates().reset_index(drop=True)
            except  Exception as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrFinal) 

                self.dataFrames['V3_DPKT']=vDPKT_DPGR[[
                  'pk'
                 ,'OBJTYPE'
                 #,'fkOBJTYPE'
                 ,'ATTRTYPE'
                 ,'EPKZ'
                 ,'TITLE'
                 ,'UNIT'
                 ,'FLAGS'             
                 #,'CLIENT_ID'
                 #,'OPCITEM_ID'
                 ,'DESCRIPTION'
                 # ---
                 ,'pk_DPGR'
                 ,'NAME'
                ]].drop_duplicates().reset_index(drop=True)

            # RXXX ########################################

   

            try:

                logger.debug("{0:s}{1:s} ...".format(logStr,'V3_RKNOT'))  

                # RXXX-Nodes but RUES-Nodes
                vRXXX_nodes =['RSLW','RMES','RHYS','RLVG','RLSR','RMMA','RADD','RMUL','RDIV','RTOT','RPT1','RINT','RPID','RFKT','RSTN']
                vRXXX_UnionList=[]
                for NODE in vRXXX_nodes:
                    vName='V_BVZ_'+NODE
                    if vName in self.dataFrames:
                        vRXXX=self.dataFrames[vName]
                        if vRXXX is None:
                            pass
                        else:
                            vRXXX['OBJTYPE']=NODE
                            vRXXX_UnionList.append(vRXXX)
                vRXXX=pd.concat(vRXXX_UnionList)
                vRXXX=vRXXX.rename(columns={'KA':'Kn'})

                # all RXXX-Nodes
                V3_RKNOT_UnionList=[]
                V3_RKNOT_UnionList.append(vRXXX)#[['OBJTYPE','BESCHREIBUNG','Kn','NAME','pk']])               
                V3_RKNOT=pd.concat(V3_RKNOT_UnionList)
                self.dataFrames['V3_RKNOT']=V3_RKNOT
            
                # RUES
                logger.debug("{0:s}{1:s} ...".format(logStr,'V3_RRUES'))  
                # wahre Quelle (wahre SRC) ermitteln
                #  Ues sind nur Aliase fuer Signale (fuer Knoten)
                #  fuer jede Alias-Definition den wahren Signalnamen (Knotennamen) ermitteln

                # alle Ues 
                vRUES=self.dataFrames['V_BVZ_RUES']
                # alle Kanten (alle Signalverbindungen)
                vCRGL=self.dataFrames['V_CRGL']
                # Ue-Definitionen per Kante (per Signal): 
                vRUESDefs=pd.merge(vRUES,vCRGL,left_on='pk',right_on='fkKk',suffixes=('','_Edge'))

                def get_UE_SRC(UeName # Name der Ue deren SRC gesucht wird             
                              ,dfUes # alle Ues (Defs und Refs)
                              ,dfUesDefs # alle Signalverbindungen die Ues definieren  
                              ):
                    """
                    gibt per df diejenige Zeile von dfUesDefs zurueck die schlussendlich UeName definiert
                    fkKi ist dann die wahre Quelle von UeName
                    fkKi verweist dabei _nicht auf eine andere Ue, d.h. verkettete Referenzen werden bis zur wahren Quelle aufgeloest
                    """

                    df=dfUesDefs[dfUesDefs['IDUE']==UeName]
    
                    if df['fkKi'].iloc[0] in dfUes['pk'].to_list():
                        pass
                        # die SRC der Ue ist eine Ue
                        #print("Die SRC der Ue {:s} ist eine Ue - die Ue-Def:\n{:s}".format(UeName, str(df[['IDUE','pk'
                        #                                                                      ,'rkRUES'
                        #                                                                      ,'fkKi','fkKk']].iloc[0])))    

                        df=dfUes[dfUes['pk']==df['fkKi'].iloc[0]] # die Referenz
                        df=dfUes[dfUes['pk']==df['rkRUES'].iloc[0]] # die SRC 
        
                        #print("{:s}".format((str(df[['IDUE','pk'
                        #                                                                      ,'rkRUES'
                        #                            #                                          ,'fkKi','fkKk'
                        #                            ]].iloc[0]))))    
                
                        # Rekursion bis zur wahren Quelle
                        df=get_UE_SRC( df['IDUE'].iloc[0]
                                   ,dfUes
                                   ,dfUesDefs
                                  )
                    else:
                        pass
                        #print("Die SRC der Ue {:s} gefunden -die Ue-Def:\n{:s}".format(UeName, str(df[['IDUE','pk'
                        #                                                                   ,'rkRUES'
                        #                                                                   ,'fkKi','fkKk']].iloc[0])))    
    
                    return df
            
                # fuer jede Ue-Definition die SRC bestimmen

                dcts=[]
                for index, row in vRUESDefs.iterrows():
    
                    if row['IDUE'] not in ['6-EL1-pVPATL','6KHV_01_P_01']:
                        #continue
                        pass
    
                    df=get_UE_SRC(row['IDUE'] # Name der Ue deren SRC gesucht wird
                              ,vRUES # Ues
                              ,vRUESDefs # Ue-Definitionen per Kante        
                              )
                    # df['fkKi'] ist die SRC
                    df=V3_RKNOT[V3_RKNOT['pk']==df['fkKi'].iloc[0]]
    
    
                    #print("{:12s} {:s} {:s}".format(row['IDUE'],row['NAME_CONT'],df[['OBJTYPE','BESCHREIBUNG','Kn']].to_string()))
    
                    dct={ 'pk_DEF':row['pk'] 
                         ,'IDUE_DEF':row['IDUE'] 
                         # 
                         ,'OBJTYPE_SRC':df['OBJTYPE'].iloc[0]
                         ,'OBJID_SRC':df['pk'].iloc[0]
                         ,'Kn_SRC':df['Kn'].iloc[0]
                         ,'NAME_CONT_SRC':df['NAME_CONT'].iloc[0]
                        }
                    dcts.append(dct)
    
                    #brea
                vRUESDefsSRCs=pd.DataFrame.from_dict(dcts)

                # fuer alle Defs die wahre Quelle angeben
                V3_RUES=pd.merge(vRUES.copy(deep=True),vRUESDefsSRCs,left_on='IDUE',right_on='IDUE_DEF'
                                ,how='left'
                                )
                
                # fuer alle Refs ebenfalls die wahre Quelle angeben
                for index, row in V3_RUES.iterrows():
                    if pd.isnull(row['IDUE_DEF']):
                        pass
                        rkRUES=row['rkRUES']
                        #print(rkRUES)
                        s=vRUESDefsSRCs[vRUESDefsSRCs['pk_DEF']==rkRUES].iloc[0]
                       # print(s)
                       # print(s['Kn_SRC'])
        
                        V3_RUES.loc[index,'pk_DEF']=s['pk_DEF']
                        V3_RUES.loc[index,'IDUE_DEF']=s['IDUE_DEF']
                        V3_RUES.loc[index,'OBJTYPE_SRC']=s['OBJTYPE_SRC']
                        V3_RUES.loc[index,'Kn_SRC']=s['Kn_SRC']
                        V3_RUES.loc[index,'NAME_CONT_SRC']=s['NAME_CONT_SRC']
                self.dataFrames['V3_RRUES']=V3_RUES

                # alle RXXX-Kanten
                logger.debug("{0:s}{1:s} ...".format(logStr,'V3_RVBEL'))  

                V3_RKNOT=self.dataFrames['V3_RKNOT']
                vRUES=self.dataFrames['V_BVZ_RUES']
                vRUES=pd.merge(vRUES,vRUES,how='left',left_on='rkRUES',right_on='pk',suffixes=('','_rkRUES'))
                vRUES['Kn'] = vRUES.apply(lambda row: row.IDUE if row.IOTYP=='1' else row.IDUE_rkRUES, axis=1)             
                vRUES['OBJTYPE']='RUES'
                vRUES['BESCHREIBUNG']=None
                V3_RKNOT=pd.concat([V3_RKNOT,vRUES[['OBJTYPE','Kn','BESCHREIBUNG','pk','NAME_CONT','IDUE','IOTYP']]])

                howMode='left'
                V_CRGL=self.dataFrames['V_CRGL']
                V3_RVBEL=pd.merge(V_CRGL,V3_RKNOT.add_suffix('_i'),left_on='fkKi',right_on='pk_i'                        
                                                  ,how=howMode)                
                V3_RVBEL['KnExt_i']=V3_RVBEL['Kn_i']+'_'+V3_RVBEL['OBJTYPE_i'] 
                V3_RVBEL=pd.merge(V3_RVBEL,V3_RKNOT.add_suffix('_k'),left_on='fkKk',right_on='pk_k'                            
                                                  ,how=howMode)
                V3_RVBEL['KnExt_k']=V3_RVBEL['Kn_k']+'_'+V3_RVBEL['OBJTYPE_k'] 

                V3_RVBEL=Xm.Xm.constructNewMultiindexFromCols(df=V3_RVBEL,mColNames=['OBJTYPE_i','OBJTYPE_k','pk'],mIdxNames=['OBJTYPE_i','OBJTYPE_k','OBJID'])

                V3_RVBEL=V3_RVBEL[~V3_RVBEL.index.get_level_values('OBJTYPE_k').isin(['RUES'])]

                V3_RVBEL=V3_RVBEL[~
                         (
                         (V3_RVBEL.index.get_level_values('OBJTYPE_i').isin(['RUES']))
                          &
                         (V3_RVBEL.index.get_level_values('OBJTYPE_k').isin(['RUES'])) 
                         )
                          ]

                V3_RVBEL=V3_RVBEL.reset_index()
                V3_RRUES=self.dataFrames['V3_RRUES']
                for index, row in V3_RVBEL[V3_RVBEL['OBJTYPE_i'].isin(['RUES'])].iterrows():
                  
                    s=V3_RRUES[V3_RRUES['pk']==row['fkKi']].iloc[0]

                    V3_RVBEL.loc[index,'OBJTYPE_i']=s['OBJTYPE_SRC']
                    #V3_RVBEL.loc[index,'OBJID_i']=s['OBJID_SRC']
                    V3_RVBEL.loc[index,'Kn_i']=s['Kn_SRC']
                    V3_RVBEL.loc[index,'KnExt_i']=s['Kn_SRC']+'_'+s['OBJTYPE_SRC'] 
                    V3_RVBEL.loc[index,'NAME_CONT_i']=s['NAME_CONT_SRC']

                V3_RVBEL=Xm.Xm.constructNewMultiindexFromCols(df=V3_RVBEL,mColNames=['OBJTYPE_i','OBJTYPE_k','OBJID'],mIdxNames=['OBJTYPE_i','OBJTYPE_k','OBJID'])
                self.dataFrames['V3_RVBEL']=V3_RVBEL

            except  Exception as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrFinal) 
                                                                     
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise AmError(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

  



