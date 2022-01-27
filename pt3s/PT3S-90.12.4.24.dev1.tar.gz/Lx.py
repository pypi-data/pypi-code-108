"""
SIR 3S Logfile Utilities (short: Lx)
"""

__version__='90.12.4.23.dev1'

import os
import sys
import logging
logger = logging.getLogger(__name__)     
import argparse
import unittest
import doctest

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

import timeit

import xml.etree.ElementTree as ET
import re
import struct
import collections
import zipfile
import py7zr
import pandas as pd
import h5py

import subprocess

import csv

import glob

import warnings 
#warnings.simplefilter(action='ignore', category=PerformanceWarning)


# pd.set_option("max_rows", None)
# pd.set_option("max_columns", None)

# pd.reset_option('max_rows')
# ...

class LxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def fTCCast(x):
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    v=x
    try:
        if x in ['true','True']:
            v=1
        elif x in ['false','False','']:
            v=0
        else:
            try:
                v = float(x) 
            except Exception as e:
                #logStrTmp="{:s}{!s:s}: Konvertierung zu float schlaegt fehl! - Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,x,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                #logger.debug(logStrTmp)            
                
                try:
                    v = pd.to_numeric(x,errors='raise',downcast='float') 
                    #logStrTmp="{:s}{!s:s}: Konvertierung mit pd.to_numeric liefert: {!s:s}".format(logStr,x,v)
                    #logger.debug(logStrTmp)                                             
                except Exception as e:
                    #logStrTmp="{:s}{!s:s}: Konvertierung zu float mit pd.to_numeric schlaegt auch fehl! - Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,x,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    #logger.debug(logStrTmp)  

                    #x='2021-04-20 10:56:12.000'
                    #t = pd.Timestamp(x)
                    #t # Timestamp('2021-04-20 10:56:12')

                    #i=int(t.to_datetime64())/1000000000
                    #i # 1618916172.0
                    #pd.to_datetime(i,unit='s',errors='coerce'): Timestamp('2021-04-20 10:56:12')

                    try:
                        t = pd.Timestamp(x)
                        i=int(t.to_datetime64())/1000000000                   
                        v=pd.to_numeric(i,errors='raise',downcast='float') 

                    except Exception as e:
                        logStrTmp="{:s}{!s:s}: Konvertierung zu float (mit pd.to_numeric) schlaegt (auch nach Annahme vaulue=Zeitstring) fehl! - Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,x,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                        logger.debug(logStrTmp)  

    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise LxError(logStrFinal)     

    finally:           
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return v

def getTCsOPCDerivative(TCsOPC,col,shiftSize,windowSize,fct=None):
    """
    returns a df
    index: ProcessTime
    cols:
        col
        dt
        dValue
        dValueDt
        dValueDtRollingMean
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    mDf=pd.DataFrame()

    try:    
        s=TCsOPC[col].dropna()        
        mDf=pd.DataFrame(s)        
        dt=mDf.index.to_series().diff(periods=shiftSize)
        mDf['dt']=dt
        mDf['dValue']=mDf[col].diff(periods=shiftSize)
        mDf=mDf.iloc[shiftSize:]
        mDf['dValueDt']=mDf.apply(lambda row: row['dValue']/row['dt'].total_seconds(),axis=1)       
        if fct != None:
            mDf['dValueDt']=mDf['dValueDt'].apply(fct)            
        mDf['dValueDtRollingMean']=mDf['dValueDt'].rolling(window=windowSize).mean()
        mDf=mDf.iloc[windowSize-1:]               
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise LxError(logStrFinal)                       
    finally:           
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return mDf

logFilenamePattern='([0-9]+)(_)+([0-9]+)(\.log)' # group(3) ist Postfix und Nr.
logFilenameHeadPattern='([0-9,_]+)(\.log)' # group(1) ist Head und H5-Key

# nicht alle IDs werden von RE pID erfasst
# diese werden mit pID2, getDfFromODIHelper und in getDfFromODI "nachbehandelt"

pID=re.compile('(?P<Prae>IMDI\.)?(?P<A>[a-z,A-Z,0-9,_]+)\.(?P<B>[a-z,A-Z,0-9,_]+)\.(?P<C1>[a-z,A-Z,0-9]+)_(?P<C2>[a-z,A-Z,0-9]+)_(?P<C3>[a-z,A-Z,0-9]+)_(?P<C4>[a-z,A-Z,0-9]+)_(?P<C5>[a-z,A-Z,0-9]+)(?P<C6>_[a-z,A-Z,0-9]+)?(?P<C7>_[a-z,A-Z,0-9]+)?\.(?P<D>[a-z,A-Z,0-9,_]+)\.(?P<E>[a-z,A-Z,0-9,_]+)(?P<Post>\.[a-z,A-Z,0-9,_]+)?') 
pID2='(?P<Prae>IMDI\.)?(?P<A>[a-z,A-Z,0-9,_]+)(?P<Post>\.[a-z,A-Z,0-9,_]+)?'

def getDfFromODIHelper(row,col,colCheck,pID2=pID2):

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    try:
        if not pd.isnull(row[colCheck]):            
            res= row[col]
            resStr='ColCheckOk'
        elif pd.isnull(row[col]):            
            res=re.search(pID2,row['ID']).group(col)  
            if res != None:
                resStr='ColNowOk'
            else:
                resStr='ColStillNotOk'
        else:
            res = row[col]        
            resStr='ColWasOk'
    except:        
        res = row[col]
        resStr='ERROR'
    finally:
        if resStr not in ['ColCheckOk','ColNowOk']:
            logger.debug("{:s}col: {:s} resStr: {:s} row['ID']: {:s} res: {:s}".format(logStr,col, resStr,row['ID'],str(res)))
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return res

def getDfFromODI(ODIFile,pID=pID):
    """
    returns a defined df from ODIFile
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    dfID=None

    try:          
        df=pd.read_csv(ODIFile,delimiter=';')
        s = pd.Series(df['ID'].unique()) 
        dfID=s.str.extract(pID.pattern,expand=True)

        dfID['ID']=s

        dfC=dfID['C1']+'_'+dfID['C2']+'_'+dfID['C3']+'_'+dfID['C4']+'_'+dfID['C5']+'_'+dfID['C6']#+'_'+dfID['C7']
        dfID.loc[:,'C']=dfC.values
        dfID['C']=dfID.apply(lambda row: row['C']+'_'+row['C7'] if not pd.isnull(row['C7']) else row['C'],axis=1)

        dfID=dfID[['ID','Prae','A','B','C','C1','C2','C3','C4','C5','C6','C7','D','E','Post']]

        for col in ['Prae','Post','A']:    
            dfID[col]=dfID.apply(lambda row: getDfFromODIHelper(row,col,'A'),axis=1)

        dfID.sort_values(by=['ID'], axis=0,ignore_index=True,inplace=True)
        dfID.set_index('ID',verify_integrity=True,inplace=True)

        dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN','Post']='.EIN'
        dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN','A']='Objects'
        dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN','B']='3S_XYZ_PUMPE'
        dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN','C']='3S_XYZ_GSI_01'
        dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN','D']='Out'
        #dfID.loc['Objects.3S_XYZ_PUMPE.3S_XYZ_GSI_01.Out.EIN',:]


        dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW','Post']='.SOLLW'
        dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW','A']='Objects'
        dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW','B']='3S_XYZ_RSCHIEBER'
        dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW','C']='3S_XYZ_PCV_01'
        dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW','D']='Out'
        #dfID.loc['Objects.3S_XYZ_RSCHIEBER.3S_XYZ_PCV_01.Out.SOLLW',:]

        dfID['yUnit']=dfID.apply(lambda row: getDfFromODIHelperyUnit(row),axis=1)
        dfID['yDesc']=dfID.apply(lambda row: getDfFromODIHelperyDesc(row),axis=1)

        dfID=dfID[['yUnit','yDesc','Prae','A','B','C','C1','C2','C3','C4','C5','C6','C7','D','E','Post']]

    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise LxError(logStrFinal)                       
    finally:           
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return dfID

def addInitvalueToDfFromODI(INITFile,dfID):
    """
    returns dfID extended with new Cols Initvalue and NumOfInits
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    dfIDext=dfID

    try:         
        df=pd.read_csv(INITFile,delimiter=';',header=None,names=['ID','Value'])#,index_col=0)
        dfGrped=df.groupby(by=['ID'])['Value'].agg(['count','min','max','mean','last'])
        dfIDext=dfID.merge(dfGrped,left_index=True,right_index=True,how='left').filter(items=dfID.columns.to_list()+['last','count']).rename(columns={'last':'Initvalue','count':'NumOfInits'})

    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise LxError(logStrFinal)                       
    finally:           
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return dfIDext

def fODIMatch(dfODI,TYPE=None,OBJTYPE=None,NAME1=None,NAME2=None):    
    df=dfODI
    
    if TYPE != None:
        df=df[df['TYPE']==TYPE]
    if OBJTYPE != None:
        df=df[df['OBJTYPE']==OBJTYPE]        
    if NAME1 != None:
        df=df[df['NAME1']==NAME1]           
    if NAME2 != None:
        df=df[df['NAME2']==NAME2]          
    
    return df

def fODIFindAllSchieberSteuerungsIDs(dfODI,NAME1=None,NAME2=None):    # dfODI: pd.read_csv(ODI,delimiter=';')
    df=fODIMatch(dfODI,TYPE='OL_2',OBJTYPE='VENT',NAME1=NAME1,NAME2=NAME2)
    return sorted(list(df['ID'].unique())+[ID for ID in df['REF_ID'].unique() if not pd.isnull(ID)])


def fODIFindAllZeilenWithIDs(dfODI,IDs):
    return dfODI[dfODI['ID'].isin(IDs) | dfODI['REF_ID'].isin(IDs)]


def getDfFromODIHelperyUnit(row):
    """
    returns Unit
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    unit=None
    try:
        if row['E'] in ['AL_S','SB_S']:       
            unit='[-]'
        elif row['E'] in ['LR_AV','LP_AV','QD_AV','SD_AV','AM_AV','FZ_AV','MZ_AV','NG_AV']:
            unit='[Nm³/h]'
        elif row['E'] in ['AC_AV','LR_AV']:
            unit='[mm/s²]'
        else:
            unit='TBD in Lx'                  
    except:        
        unit='ERROR'
    finally:
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return unit

def getDfFromODIHelperyDesc(row):
    """
    returns Desc
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    desc=None
    try:
        if row['E'] in ['AL_S','SB_S']:       
            desc='Status'
        elif row['E'] in ['LR_AV','LP_AV','QD_AV','SD_AV','AM_AV','FZ_AV','MZ_AV','NG_AV']:
            desc='Fluss'
        elif row['E'] in ['AC_AV','LR_AV']:
            desc='Beschleunigung'
        else:
            desc='TBD in Lx'                  
    except:        
        desc='ERROR'
    finally:
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return desc

def getDfIDUniqueCols(dfID):
    """
    returns df with uniques  
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfIDUniqueCols=pd.DataFrame()
    try:
        # Spalte mit der groessten Anzahl von Auspraegungen feststellen
        lenMax=0
        colMax=''
        # ueber alle Spalten
        for idx,col in enumerate(dfID):           
            s=pd.Series(dfID[col].unique())
            if len(s) > lenMax:
                lenMax=len(s)
                colMax=col

        s=pd.Series(dfID[colMax].unique(),name=colMax)
        s.sort_values(inplace=True)
        s=pd.Series(s.values,name=colMax)
        dfIDUniqueCols=pd.DataFrame(s)
               
        # ueber alle weiteren Spalten
        for idx,col in enumerate([col for col in dfID.columns if col != colMax]):
            # s unique erzeugen
            s=pd.Series(dfID[col].unique(),name=col)
            # s sortieren
            s.sort_values(inplace=True)
            s=pd.Series(s.values,name=col)
            dfIDUniqueCols=pd.concat([dfIDUniqueCols,s],axis=1)
        
        dfIDUniqueCols=dfIDUniqueCols[dfID.columns]


    except:        
        logger.error("{0:s}".format(logStr))  
        
    finally:

        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return dfIDUniqueCols

def getIDsFromID(ID='Objects.3S_XYZ_SEG_INFO.3S_L_6_KED_39_EL1.In.AL_S',dfID=None,matchCols=['B','C1','C2','C3','C4','C5','D'],any=False):
    """
    returns IDs matching ID  
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
       
    try:
        IDsMatching=[]   
        s=dfID.loc[ID,:]        
    
        for ID,row in dfID.iterrows():            
            match=True
            for col in [col for col in row.index.values if col in matchCols]:            
                #if str(row[col])!=str(s[col]):
                if row[col]!=s[col]:
                    match=False                
                    break                
                else:
                    if any:
                        break                   
            if match:
                    IDsMatching.append(ID)
    
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 

    #except:        
    #    logger.error("{0:s}".format(logStr))  
        
    finally:
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return sorted(IDsMatching)

def getLDSResVecDf(
     ID # ResVec-Defining-Channel; i.e. for Segs Objects.3S_XYZ_SEG_INFO.3S_L_6_EL1_39_TUD.In.AL_S / i.e. for Drks Objects.3S_XYZ_DRUCK.3S_6_EL1_39_PTI_02_E.In.AL_S 
    ,dfID
    ,TCsLDSResDf 
    ,matchCols # i.e. ['B','C1','C2','C3','C4','C5','C6','D'] for Segs; i.e. ['B','C','D'] for Drks
    ):
    """
    returns a df with LDSResChannels as columns (AL_S, ...); derived by Filtering columns from TCsLDSResDf and renaming them
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfResVec=pd.DataFrame()
    try:
        IDs=getIDsFromID(ID=ID,dfID=dfID,matchCols=matchCols)
        dfFiltered=TCsLDSResDf.filter(items=IDs)
       
        colDct={}
        for col in dfFiltered.columns:            
            m=re.search(pID,col)
            colDct[col]=m.group('E')
        dfResVec=dfFiltered.rename(columns=colDct)        

    except:        
        logger.error("{0:s}".format(logStr))  
        
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return dfResVec


def fGetFirstAndLastValidIdx(df):
    """
    returns (tFirst,tLast)
    """
    
    for idx,col in enumerate(df.columns):
        tF=df[col].first_valid_index()
        tL=df[col].last_valid_index()
        if idx==0:        
            tFirst=tF
            tLast=tL
        else:
            if tF < tFirst:
                tFirst=tF
            if tL > tLast:
                tLast=tL     
    return (tFirst,tLast)
    
def fGetIDSets(
    dfID
   ,divNr #'7'
   ,pipelineNrLst #['43','44']
   ,fctIn=None # Funktion von ID die Falsch heraus gibt, wenn ID (doch) nicht in Menge sein soll
):
    # returns Dct: key: Bezeichner einer ID-Menge; value: zugeh. IDs
    
    IDSets={}
    
    IDs=[]
    for ID in sorted(dfID.index.unique()):
        m=re.search(pID,ID)
        if m != None:
            C1= m.group('C1')        
            C2= m.group('C2')
            C3= m.group('C3')
            C4= m.group('C4')
            C5= m.group('C5')

            if   C1 in [divNr] and C3 in pipelineNrLst: # u.a. SEG ErgVecs
                IDs.append(ID)        

            elif C2 in [divNr] and C4 in pipelineNrLst:
                IDs.append(ID)

            elif C3 in [divNr] and C5 in pipelineNrLst: # FT, PTI, etc.
                IDs.append(ID)     
         
    if fctIn != None:
        IDs=[ID for ID in IDs if fctIn(ID)]

    IDSets['IDs']=IDs
    
    IDsAlarm=[ID for ID in IDs if re.search(pID,ID).group('E') == 'AL_S']
    IDSets['IDsAlarm']=IDsAlarm
    
    IDsAlarmSEG=[ID for ID in IDsAlarm if re.search(pID,ID).group('C5') != 'PTI']    
    IDSets['IDsAlarmSEG']=IDsAlarmSEG
    IDsAlarmDruck=[ID for ID in IDsAlarm if re.search(pID,ID).group('C5') == 'PTI']
    IDSets['IDsAlarmDruck']=IDsAlarmDruck
    
    IDsStat=[ID for ID in IDs if re.search(pID,ID).group('E') == 'STAT_S']
    IDSets['IDsStat']=IDsStat

    IDsStatSEG=[ID for ID in IDsStat if re.search(pID,ID).group('C5') != 'PTI']    
    IDSets['IDsStatSEG']=IDsStatSEG
    IDsStatDruck=[ID for ID in IDsStat if re.search(pID,ID).group('C5') == 'PTI']
    IDSets['IDsStatDruck']=IDsStatDruck

    ###

    IDsSb=[ID for ID in IDs if re.search(pID,ID).group('E') == 'SB_S']
    IDSets['IDsSb']=IDsSb

    IDsSbSEG=[ID for ID in IDsSb if re.search(pID,ID).group('C5') != 'PTI']    
    IDSets['IDsSbSEG']=IDsSbSEG
    IDsSbDruck=[ID for ID in IDsSb if re.search(pID,ID).group('C5') == 'PTI']
    IDSets['IDsSbDruck']=IDsSbDruck

    ###

    IDsZHK=[ID for ID in IDs if re.search(pID,ID).group('E') == 'ZHKNR_S']
    IDSets['IDsZHK']=IDsZHK

    IDsZHKSEG=[ID for ID in IDsZHK if re.search(pID,ID).group('C5') != 'PTI']    
    IDSets['IDsZHKSEG']=IDsZHKSEG
    IDsZHKDruck=[ID for ID in IDsZHK if re.search(pID,ID).group('C5') == 'PTI']
    IDSets['IDsZHKDruck']=IDsZHKDruck
    
    IDsFT=[ID for ID in IDs if re.search(pID,ID).group('C4') == 'FT']
    IDSets['IDsFT']=IDsFT
    
    IDsPT=[ID for ID in IDs if re.search(pID,ID).group('C4') == 'PTI']
    IDSets['IDsPT']=IDsPT

    IDsPT_BCIND=[ID for ID in IDs if re.search(pID,ID).group('C5') == 'PTI' and re.search(pID,ID).group('E') == 'BCIND_S' ]
    IDSets['IDsPT_BCIND']=IDsPT_BCIND

    ### Schieber
    
    IDsZUST=[ID for ID in IDs if re.search(pID,ID).group('E') == 'ZUST']
    IDsZUST=sorted(IDsZUST,key=lambda x: re.match(pID,x).group('C5'))   
    IDSets['IDsZUST']=IDsZUST
    
    IDs_3S_XYZ_ESCHIEBER=[ID for ID in IDs if re.search(pID,ID).group('B') == '3S_FBG_ESCHIEBER']
    IDs_3S_XYZ_ESCHIEBER=sorted(IDs_3S_XYZ_ESCHIEBER,key=lambda x: re.match(pID,x).group('C6'))    
    IDSets['IDs_3S_XYZ_ESCHIEBER']=IDs_3S_XYZ_ESCHIEBER
    
    IDs_XYZ_ESCHIEBER=[ID for ID in IDs if re.search(pID,ID).group('B') == 'FBG_ESCHIEBER']
    IDs_XYZ_ESCHIEBER=sorted(IDs_XYZ_ESCHIEBER,key=lambda x: re.match(pID,x).group('C5'))    #
    IDSets['IDs_XYZ_ESCHIEBER']=IDs_XYZ_ESCHIEBER    
        
    IDs_XYZ_ESCHIEBER_Ohne_ZUST=[ID for ID in IDs_XYZ_ESCHIEBER if re.search(pID,ID).group('E') != 'ZUST']
    IDs_XYZ_ESCHIEBER_Ohne_ZUST=sorted(IDs_XYZ_ESCHIEBER_Ohne_ZUST,key=lambda x: re.match(pID,x).group('C5'))    
    IDSets['IDs_XYZ_ESCHIEBER_Ohne_ZUST']=IDs_XYZ_ESCHIEBER_Ohne_ZUST



    
    IDsSchieberAlle=IDsZUST+IDs_XYZ_ESCHIEBER_Ohne_ZUST+IDs_3S_XYZ_ESCHIEBER  
    IDSets['IDsSchieberAlle']=IDsSchieberAlle
    
    IDsSchieberAlleOhneLAEUFT=[ID for ID in IDsSchieberAlle if re.search('LAEUFT$',ID) == None]
    IDsSchieberAlleOhneLAEUFT=[ID for ID in IDsSchieberAlleOhneLAEUFT if re.search('LAEUFT_NICHT$',ID) == None]    
    IDSets['IDsSchieberAlleOhneLAEUFT']=IDsSchieberAlleOhneLAEUFT
    
    
    return IDSets   


h5KeySep='/'

def fValueFct(x):        
    return pd.to_numeric(x,errors='ignore',downcast='float')

class AppLog():
    """
    SIR 3S App Log (SQC Log)

    Maintains a H5-File.   
    Existing H5-File will be deleted (if not initialized with h5File=...).

    H5-Keys are:
    * init
    * lookUpDf
    * lookUpDfZips (if initialized with zip7Files=...)
    * Logfilenames praefixed by Log without extension 
    
    Attributes:  
    * h5File
    * lookUpDf
        zipName
        logName
        FirstTime (ScenTime - not #LogTime)
        LastTime  (ScenTime - mot #LogTime)
    * lookUpDfZips
    """

    TCsdfOPCFill=False # wenn Wahr, werden in TCsdfOPCFill die NULLen aufgefuellt; default: Falsch

    @classmethod
    def getTCsFromDf(cls,df,dfID=pd.DataFrame(),TCsdfOPCFill=TCsdfOPCFill):
        """
        returns several TC-dfs from df

        Verarbeitung von dfs gemaess extractTCsToH5s; siehe dort
      
        Args:
            * df: a df with Log-Data
                * columns: ['ID','ProcessTime','ScenTime','SubSystem','Value','Direction']
            * dfID
                * index: ID
                * erf. nur, wenn IDs nach Res1 und Res2 aufgeteilt werden sollen
            * TCsdfOPCFill: if True (default): fill NaNs in this df
        
        Time curve dfs: cols:
            * Time (TCsdfOPC: ProcessTime, other: ScenTime)
            * ID 
            * Value 

        Time curve dfs:
            * TCsdfOPC
            * TCsSirCalc
            * TCsLDSIn
            * TCsLDSRes (dfID empty) or TCsLDSRes1, TCsLDSRes2            
            
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
       
        try:                                      

            TCsdfOPC=pd.DataFrame()
            TCsdfSirCalc=pd.DataFrame()
            TCsdfLDSIn=pd.DataFrame()
            if not dfID.empty:
                TCsdfLDSRes1=pd.DataFrame()
                TCsdfLDSRes2=pd.DataFrame()
            else:
                TCsdfLDSRes=pd.DataFrame()           

            if not dfID.empty:
                df=df.merge(dfID,how='left',left_on='ID',right_index=True,suffixes=('','_r'))             
                                                           
            logger.debug("{0:s}{1:s}".format(logStr,'TCsdfOPC ...'))     
            TCsdfOPC=df[(df['SubSystem'].str.contains('^OPC')) 
                        ### & ~(df['Value'].isnull()) # ueberfluessig, wenn df dies bereits erfuellt
                        ][['ProcessTime','ID','Value']].pivot_table(index='ProcessTime', columns='ID', values='Value',aggfunc='last')
            if TCsdfOPCFill:
                for col in TCsdfOPC.columns:    
                    TCsdfOPC[col]=TCsdfOPC[col].fillna(method='ffill')
                    TCsdfOPC[col]=TCsdfOPC[col].fillna(method='bfill')
            
            logger.debug("{0:s}{1:s}".format(logStr,'TCsdfSirCalc ...'))                           
            TCsdfSirCalc=df[(df['SubSystem'].str.contains('^SirCalc')) | (df['SubSystem'].str.contains('^RTTM')) ][['ScenTime','ID','Value']].pivot_table(index='ScenTime', columns='ID', values='Value',aggfunc='last')       
            
            logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSIn ...'))      
            TCsdfLDSIn=df[(df['SubSystem'].str.contains('^LDS')) & (df['Direction'].str.contains('^<-'))][['ScenTime','ID','Value']].pivot_table(index='ScenTime', columns='ID', values='Value',aggfunc='last')
           
            if not dfID.empty:
                logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes1 ...'))  
                TCsdfLDSRes1=df[(df['SubSystem'].str.contains('^LDS')) & (df['Direction'].str.contains('^->')) & (df['B'].str.contains('^3S_FBG_SEG_INFO'))][['ScenTime','ID','Value']].pivot_table(index='ScenTime', columns='ID', values='Value',aggfunc='last')               

                logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes2 ...'))  
                TCsdfLDSRes2=df[(df['SubSystem'].str.contains('^LDS')) & (df['Direction'].str.contains('^->')) & (df['B'].str.contains('^3S_FBG_DRUCK'))][['ScenTime','ID','Value']].pivot_table(index='ScenTime', columns='ID', values='Value',aggfunc='last')                      
            else:                   
                logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes ...'))  
                TCsdfLDSRes=df[(df['SubSystem'].str.contains('^LDS')) & (df['Direction'].str.contains('^->'))][['ScenTime','ID','Value']].pivot_table(index='ScenTime', columns='ID', values='Value',aggfunc='last')  
                                                         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            if not dfID.empty:
                return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2
            else:
                return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes

    def __init__(self,logFile=None,zip7File=None,h5File=None,h5FileName=None,readWithDictReader=False,nRows=None,readWindowsLog=False):
        """
        (re-)initialize

        logFile: 
            wird gelesen und in H5 abgelegt
            addZip7File(zip7File) liest alle Logs eines zipFiles und legt diese in H5 ab

        zipFile: 
            1. logFile wird gelesen und in H5 abgelegt
            addZip7File(zip7File) liest alle Logs eines zipFiles und legt diese in H5 ab
            die Initialisierung mit zipFile ist identisch mit der Initialisierung mit logFile wenn logFile das 1. logFile des Zips ist 

            nach addZip7File(zip7File) - ggf. mehrfach fuer mehrere Zips:
                koennen Daten mit self.get(...) gelesen werden (liefert 1 df)
                koennen Daten mit self.getTCs(...) gelesen werden (liefert mehrere dfs in TC-Form)
                koennen Daten mit self.getTCsSpecified(...) gelesen werden (liefert 1 df in TC-Form)

                koennen Daten in TC-Form mit self.extractTCsToH5s(...) in separate H5s gelesen werden
                mit self.getTCsFromH5s(...) koennen die TCs wieder gelesen werden

                === addZip7File(zip7File) - ggf. mehrfach - und extractTCsToH5s(...) sind Bestandteil einer 7Zip-Verarbeitung vor der eigentlichen Analyse ===

        h5File:
            die lookUp-Dfs vom H5-File werden gelesen
            die zum H5-File zugehoerigen TC-H5-Filenamen werden belegt
            die TC-H5-Files werden nicht auf Existenz geprüft oder gar gelesen            

        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        self.lookUpDf=pd.DataFrame() 
        self.lookUpDfZips=pd.DataFrame() 

        try:     
             if logFile != None and zip7File != None and h5File != None:
                logger.debug("{0:s}{1:s}".format(logStr,'3 Files (logFile and zip7File and h5File) specified.'))             
             elif logFile != None and zip7File != None:
                logger.debug("{0:s}{1:s}".format(logStr,'2 Files (logFile and zip7File) specified.')) 
             elif logFile != None and h5File != None:
                logger.debug("{0:s}{1:s}".format(logStr,'2 Files (logFile and h5File) specified.')) 
             elif h5File != None and zip7File != None:
                logger.debug("{0:s}{1:s}".format(logStr,'2 Files (h5File and zip7File) specified.')) 
             elif  logFile != None:                 
                 self.__initlogFile(logFile,h5FileName=h5FileName,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog)
             elif zip7File != None:
                 self.__initzip7File(zip7File,h5FileName=h5FileName,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog)            
             elif h5File != None:
                 self.__initWithH5File(h5File)
             else:                 
                 logger.debug("{0:s}{1:s}".format(logStr,'No File (logFile XOR zip7File XOR h5File) specified.')) 

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
             
    def __initlogFile(self,logFile,h5FileName=None,readWithDictReader=False,readWindowsLog=False):
        """
        (re-)initialize with logFile
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:                 
             # wenn logFile nicht existiert ...
             if not os.path.exists(logFile):                                      
                logger.debug("{0:s}logFile {1:s} not existing.".format(logStr,logFile))    
             else:
                df = self.__processALogFile(logFile=logFile,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog)    
                self.__initH5File(logFile,df,h5FileName=h5FileName)
         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def __initH5File(self,h5File,df,h5FileName=None):
        """
        creates self.h5File and writes 'init'-Key Logfile df to it

        Args:
        * h5File: name of logFile or zip7File; the Dir is the Dir of the H5-File
        * df
        * h5FileName: the H5-FileName without Dir and Extension; if None (default), "Log ab ..." is used
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:                                              
             (h5FileHead,h5FileTail)=os.path.split(h5File)
             
             # H5-File
             if h5FileName==None:
                h5FileTail="Log ab {0:s}.h5".format(str(df['#LogTime'].min())).replace(':',' ').replace('-',' ')           
             else:
                h5FileTail=h5FileName+'.h5'
             self.h5File=os.path.join(h5FileHead,h5FileTail)

             # wenn H5 existiert wird es geloescht
             if os.path.exists(self.h5File):                                         
                os.remove(self.h5File)
                logger.debug("{0:s}Existing H5-File {1:s} deleted.".format(logStr,h5FileTail))    

             # init-Logfile schreiben
             self.__toH5('init',df) 
             logger.debug("{0:s}'init'-Key Logfile done.".format(logStr))    

         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def __initWithH5File(self,h5File,useRawHdfAPI=False):
        """       
        self.h5File=h5File

        self.lookUpDf     
        self.lookUpDfZips 
        die lookUp-Dfs werden gelesen vom H5-File

        die zum H5-File zugehoerigen TC-H5-Filenamen werden belegt, wenn diese H5-Files existieren
        die TC-H5-Files werden nicht gelesen

        der zum H5-File zugehoerige CVD-Filename wird belegt, wenn das H5-File existiert
        das H5-File wird nicht gelesen
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:  
            # H5 existiert 
            if os.path.exists(h5File):
                self.h5File=h5File

                # Keys available
                with pd.HDFStore(self.h5File) as h5Store:
                     h5Keys=sorted(h5Store.keys())                                     
                     logger.debug("{0:s}h5Keys available: {1:s}".format(logStr,str(h5Keys))) 
                     
                h5KeysStripped=[item.replace(h5KeySep,'') for item in h5Keys]

                if useRawHdfAPI:
                    with pd.HDFStore(self.h5File) as h5Store:
                        if 'lookUpDf' in h5KeysStripped:
                            self.lookUpDf=h5Store['lookUpDf']
                        if 'lookUpDfZips' in h5KeysStripped:
                            self.lookUpDfZips=h5Store['lookUpDfZips']
                else:
                    if 'lookUpDf' in h5KeysStripped:
                        self.lookUpDf=pd.read_hdf(self.h5File, key='lookUpDf')        
                    if 'lookUpDfZips' in h5KeysStripped:
                        self.lookUpDfZips=pd.read_hdf(self.h5File, key='lookUpDfZips')     

            else:
                logStrFinal="{0:s}h5File {1:s} not existing.".format(logStr,h5File) 
                logger.debug(logStrFinal)    
                raise LxError(logStrFinal)        
                                     
            #TC-H5s
            (name,ext)=os.path.splitext(self.h5File)
            TCPost='_TC'

            h5FileOPC=name+TCPost+'OPC'+ext
            h5FileSirCalc=name+TCPost+'SirCalc'+ext
            h5FileLDSIn=name+TCPost+'LDSIn'+ext

            h5FileLDSRes1=name+TCPost+'LDSRes1'+ext
            h5FileLDSRes2=name+TCPost+'LDSRes2'+ext
            h5FileLDSRes=name+TCPost+'LDSRes'+ext
               
            if os.path.exists(h5FileOPC):                                         
                self.h5FileOPC=h5FileOPC                       
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileOPC))    
            if os.path.exists(h5FileSirCalc):                                         
                self.h5FileSirCalc=h5FileSirCalc
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileSirCalc))  
            if os.path.exists(h5FileLDSIn):                                         
                self.h5FileLDSIn=h5FileLDSIn
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileLDSIn))  

            if os.path.exists(h5FileLDSRes):                                         
                self.h5FileLDSRes=h5FileLDSRes                      
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileLDSRes))    
            if os.path.exists(h5FileLDSRes1):                                         
                self.h5FileLDSRes1=h5FileLDSRes1
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileLDSRes1))    
            if os.path.exists(h5FileLDSRes2):                                         
                self.h5FileLDSRes2=h5FileLDSRes2
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileLDSRes2))    


            h5FileCVD=name+'_'+'CVD'+ext
            if os.path.exists(h5FileCVD):                                         
                self.h5FileCVD=h5FileCVD
                logger.debug("{0:s}Existing H5-File {1:s}.".format(logStr,self.h5FileCVD))    
                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def getInitDf(self,useRawHdfAPI=False):
        """       
        returns InitDf from H5-File 
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:
            
            df=pd.DataFrame()

            # H5 existiert 
            if os.path.exists(self.h5File):
               

                # Keys available
                with pd.HDFStore(self.h5File) as h5Store:
                     h5Keys=sorted(h5Store.keys())                                     
                     logger.debug("{0:s}h5Keys available: {1:s}".format(logStr,str(h5Keys))) 
                     
                h5KeysStripped=[item.replace(h5KeySep,'') for item in h5Keys]

                if useRawHdfAPI:
                    with pd.HDFStore(self.h5File) as h5Store:
                        if 'init' in h5KeysStripped:
                            df=h5Store['init']
                else:
                    if 'init' in h5KeysStripped:
                        df=pd.read_hdf(self.h5File, key='init')        
            else:
                logStrFinal="{0:s}h5File {1:s} not existing.".format(logStr,h5File) 
                logger.debug(logStrFinal)    
                raise LxError(logStrFinal)      
            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            return df

    def __initzip7File(self,zip7File,h5FileName=None,nRows=None,readWithDictReader=False,readWindowsLog=False):
        """
        (re-)initialize with zip7File
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:                                             
                # wenn zip7File nicht existiert ...
                if not os.path.exists(zip7File):                     
                   logStrFinal="{0:s}zip7File {1:s} not existing.".format(logStr,zip7File) 
                   logger.debug(logStrFinal)    
                   raise LxError(logStrFinal)    
                else:
                   (zip7FileHead, zip7FileTail)=os.path.split(zip7File)
                
                zipFileDirname=os.path.dirname(zip7File)
                logger.debug("{0:s}zipFileDirname: {1:s}".format(logStr,zipFileDirname))   

                aDfRead=False
                with py7zr.SevenZipFile(zip7File, 'r') as zip7FileObj:                
                    allLogFiles = zip7FileObj.getnames()

                    logger.debug("{0:s}{1:s}: len(getnames()): {2:d}.".format(logStr,zip7FileTail,len(allLogFiles)))  
                    logger.debug("{0:s}getnames(): {1:s}.".format(logStr,str(allLogFiles)))  

                    extDirLstTBDeleted=[]
                    extDirLstExistingLogged=[]                    

                    for idx,logFileNameInZip in enumerate(allLogFiles):

                        logger.debug("{0:s}idx: {1:d} logFileNameInZip: {2:s}".format(logStr,idx,logFileNameInZip))   

                        # die Datei die 7Zip bei extract erzeugen wird
                        logFile=os.path.join(zipFileDirname,logFileNameInZip)

                        (logFileHead, logFileTail)=os.path.split(logFile) # logFileHead == dirname()
                        logger.debug("{0:s}idx: {1:d} logFileHead: {2:s} logFileTail: {3:s}".format(logStr,idx,logFileHead,logFileTail))   

                        (name, ext)=os.path.splitext(logFile)
                        logger.debug("{0:s}idx: {1:d} name: {2:s} ext: {3:s}".format(logStr,idx,name,ext))   

                        if logFileHead!='': # logFileHead == dirname()
                            if os.path.exists(logFileHead) and logFileHead not in extDirLstExistingLogged:
                                logger.debug("{0:s}idx: {1:d} Verz. logFileHead: {2:s} existiert bereits.".format(logStr,idx,logFileHead))  
                                extDirLstExistingLogged.append(logFileHead)
                            elif not os.path.exists(logFileHead):
                                logger.debug("{0:s}idx: {1:d} Verz. logFileHead: {2:s} existiert noch nicht.".format(logStr,idx,logFileHead))                      
                                extDirLstTBDeleted.append(logFileHead)
                        
                        # kein Logfile zu prozessieren ...
                        if ext == '':
                            continue

                        # Logfile prozessieren ...
                        if os.path.exists(logFile):
                            isFile = os.path.isfile(logFile)
                            if isFile:
                                logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert bereits. Wird durch Extrakt ueberschrieben werden.".format(logStr,idx,logFileTail))  
                                logFileTBDeleted=False
                            else:
                                logFileTBDeleted=False
                        else:
                            logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert nicht. Wird extrahiert, dann prozessiert und dann wieder geloescht.".format(logStr,idx,logFileTail))                      
                            logFileTBDeleted=True
                  
                        # extrahieren 
                        zip7FileObj.extract(path=zipFileDirname,targets=logFileNameInZip)
                    
                        if os.path.exists(logFile):
                            pass                       
                        else:
                            logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT extracted?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                            # nichts zu prozessieren ...
                            continue

                        # ...
                        if os.path.isfile(logFile):                                                  
                            df = self.__processALogFile(logFile=logFile,nRows=nRows,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog) 
                            if df is None:      
                                logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT processed?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                                # nichts zu prozessieren ...
                                continue
                            else:
                                aDfRead=True
                        # ...

                        # gleich wieder loeschen
                        if os.path.exists(logFile) and logFileTBDeleted:
                            if os.path.isfile(logFile):
                                os.remove(logFile)
                                logger.debug("{0:s}idx: {1:d} Log: {2:s} wieder geloescht.".format(logStr,idx,logFileTail))         
                                
                        # wir wollen nur das 1. File lesen ...
                        if aDfRead:                           
                           break;

                for dirName in extDirLstTBDeleted:
                    if os.path.exists(dirName):
                        if os.path.isdir(dirName):
                            (dirNameHead, dirNameTail)=os.path.split(dirName)
                            if len(os.listdir(dirName)) == 0:
                                os.rmdir(dirName)                                    
                                logger.debug("{0:s}dirName: {1:s} existierte nicht und wurde wieder geloescht.".format(logStr,dirNameTail))     
                            else:
                                logger.info("{0:s}dirName: {1:s} existiert mit nicht leerem Inhalt?!".format(logStr,dirNameTail))    
                            
                
                self.__initH5File(zip7File,df,h5FileName=h5FileName)
         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def __toH5(self,key,df,useRawHdfAPI=False,updLookUpDf=False,logName='',zipName='',noDfStorage=False):
        """
        write df with key to H5-File (if not noDfStorage)

        Args:
        * updLookUpDf: if True, self.lookUpDf is updated with 
            * zipName (the Zip of logFile)
            * logName (the name of the logFile i.e. 20201113_0000004.log)
            * FirstTime (the first ScenTime in df)
            * LastTime (the last ScenTime in df)
            self.lookUpDf is not wriiten to H5
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:   
            
             (h5FileHead,h5FileTail)=os.path.split(self.h5File)

             if not noDfStorage:
                 if useRawHdfAPI:
                     with pd.HDFStore(self.h5File) as h5Store:                 
                        try:
                            h5Store.put(key,df)
                        except Exception as e:
                            logger.error("{0:s}Writing df with h5Key={1:s} to {2:s} FAILED!".format(logStr,key,h5FileTail))    
                            raise e
                 else:
                     df.to_hdf(self.h5File, key=key)
                 logger.debug("{0:s}Writing df with h5Key={1:s} to {2:s} done.".format(logStr,key,h5FileTail))    

             if updLookUpDf:
                 s=df['ScenTime']#['#LogTime']
                 FirstTime=s.iloc[0]
                 LastTime=s.iloc[-1]
                 if self.lookUpDf.empty:
                     data={ 'zipName': [zipName]
                           ,'logName': [logName]
                           ,'FirstTime' : [FirstTime]
                           ,'LastTime' : [LastTime]
                          }
                     self.lookUpDf = pd.DataFrame (data, columns = ['zipName','logName','FirstTime','LastTime'])
                     self.lookUpDf['zipName']=self.lookUpDf['zipName'].astype(str)
                     self.lookUpDf['logName']=self.lookUpDf['logName'].astype(str)
                 else:
                     data={ 'zipName': zipName
                           ,'logName': logName
                           ,'FirstTime' : FirstTime
                           ,'LastTime' : LastTime
                          }
                     self.lookUpDf=self.lookUpDf.append(data,ignore_index=True)                                       
                   
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
          
    def __processALogFile(self,logFile=None,delimiter='\t',nRows=None,readWithDictReader=False,fValueFct=fValueFct,readWindowsLog=False):
        """
        process logFile

        Args:
            * logFile: logFile to be processed        
            * nRows: number of logFile rows to be processed; default: None (:= all rows are processed); if readWithDictReader: last row is also processed
            * readWithDictReader: if True, csv.DictReader is used; default: None (:= pd.read_csv is used)                

        Returns:
            * df: logFile processed to df

                *  converted:
                    * #LogTime:                                      to datetime
                    * ProcessTime:                                   to datetime
                    * Value:                                         to float64        
                    * ID,Direction,SubSystem,LogLevel,State,Remark:  to str
                *  new:
                    * ScenTime                                          datetime
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        df=None
        try: 
             with open(logFile,'r') as f: 
                pass

             (logFileHead,logFileTail)=os.path.split(logFile)

             if readWithDictReader:
                restkey='+' 
                with open(logFile,"r") as csvFile: # 1. Zeile enthaelt die Ueberschrift 
                     reader = csv.DictReader(csvFile,delimiter=delimiter,restkey=restkey) 
                     logger.debug("{0:s}{1:s} csv.DictReader reader processed.".format(logStr,logFileTail)) 
             
                     # If a row has more fields than fieldnames, the remaining data is put in a list and stored with the fieldname specified by restkey. 
                     colNames=reader.fieldnames
                     
                     dcts = [dct for dct in reader] # alle Zeilen lesen  

                logger.debug("{0:s}{1:s} csv.DictReader-Ergebnis processed.".format(logStr,logFileTail)) 
                if nRows!=None:
                    dcts=dcts[0:nRows]+[dcts[-1]]
             
                # nur die Spaltennamen werden als row-Spalten erzeugt
                rows = [[dct[colName] for colName in colNames] for dct in dcts]
                logger.debug("{0:s}{1:s} rows processed.".format(logStr,logFileTail)) 

                # die "ueberfluessigen" Spalten an die letzte Spalte dranhaengen             
                for i, dct in enumerate(dcts):                    
                    if restkey in dct:
                        restValue=dct[restkey]
                        restValueStr = delimiter.join(restValue)
                        newValue=rows[i][-1]+delimiter+restValueStr
                        #logger.debug("{0:s}{1:s} restValueStr: {2:s} - Zeile {3:10d}: {4:s} - neuer Wert letzte Spalte: {5:s}.".format(logStr,logFileTail,restValueStr,i,str(rows[i]),newValue)) 
                        rows[i][-1]=rows[i][-1]+newValue
                logger.debug("{0:s}{1:s} restkey processed.".format(logStr,logFileTail)) 

                index=range(len(rows))
                df = pd.DataFrame(rows,columns=colNames,index=index)
             else:
                if nRows==None:
                    df=pd.read_csv(logFile,delimiter=delimiter,error_bad_lines=False,warn_bad_lines=True,low_memory=False)
                else:
                    df=pd.read_csv(logFile,delimiter=delimiter,error_bad_lines=False,warn_bad_lines=True,low_memory=False,nrows=nRows)                
                
             logger.debug("{0:s}{1:s} pd.DataFrame processed.".format(logStr,logFileTail)) 
             #logger.debug("{0:s}df: {1:s}".format(logStr,str(df))) 

             #LogTime
             df['#LogTime']=pd.to_datetime(df['#LogTime'],unit='ms',errors='coerce') # NaT     
             
             #ProcessTime
             df['ProcessTime']=pd.to_datetime(df['ProcessTime'],unit='ms',errors='coerce') # NaT

             logger.debug("{0:s}{1:s} col ProcessTime processed.".format(logStr,logFileTail)) 
             
             #Value
             df['Value']=df.Value.str.replace(',', '.') # Exception: Line: 1137: <class 'AttributeError'>: Can only use .str accessor with string values!
             df['Value']=fValueFct(df['Value'].values) # df['ValueProcessed'].apply(fValueFct)
             logger.debug("{0:s}{1:s} col Value processed.".format(logStr,logFileTail)) 

             #Strings             
             for col in ['ID','Direction','SubSystem','LogLevel','State','Remark']: 
                df[col]=df[col].astype(str)

             logger.debug("{0:s}{1:s} String-cols processed.".format(logStr,logFileTail)) 

             #1618249551621	STD	CVD		1615442324000	p-p			BEGIN_OF_NEW_CONTROL_VOLUME	6-10-SV1-RB~6-10-BID-RB	NULL	NULL # String in beiden Faellen (Linux und Windows) gleich?
             #1618249551621	STD	CVD	<-			156		CV_ID

             ##ScenTime       
             ##                      SubSystem   Direction   ProcessTime     ID                  Value   State   Remark                              
             ## Linux ---
             ## 1615029280000	INF	SQC		    			                                                    Starting cycle for 2021-03-06 12:14:38.000
             ## 1615029280000	STD	LDS MCL		            1615029278000	Main cycle loop			            06.03.2021	12:14:38.000 (ScenTime: Tag und Zeit in Klartext; Spalte ProcessTime ScenTime!)
             ## Windows ---
             ## 1618256150711	STD	SQC		                1615457121000	Main cycle loop			            11:05:21.000 (ScenTime-Zeit in Klartext; Spalte ProcessTime ScenTime!)
                                    
             dfScenTime=df[df['ID']=='Main cycle loop'][['ProcessTime']]
             dfScenTime.rename(columns={'ProcessTime':'ScenTime'},inplace=True)
             df=df.join(dfScenTime) 
             df['ScenTime']=df['ScenTime'].fillna(method='ffill')
             df['ScenTime']=df['ScenTime'].fillna(method='bfill')
             if df['ScenTime'].isnull().values.all():
                logger.debug("{0:s}Keine Zeile mit ID=='Main cycle loop' gefunden. ScenTime zu #LogTime gesetzt.".format(logStr))     
                df['ScenTime']=df['#LogTime'] # wenn keine Zeile mit ID=='Main cycle loop' gefunden wurde, wird ScenTime zu #LogTime gesetzt
            
             # finalisieren           
             df=df[['#LogTime','LogLevel','SubSystem','Direction','ProcessTime','ID','Value','ScenTime','State','Remark']]            
             logger.debug("{0:s}{1:s} processed with nRows: {2:s} (None if all).".format(logStr,logFileTail,str(nRows)))     
                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))                    
            return df

    def rebuildLookUpDfZips(self,zip7Files,readWithDictReader=True,readWindowsLog=False):
        """
        (re-)initialize with zip7Files

        only persistent outcome is lookUpDfZips (Attribute and H5-Persistence)
        lookUpdf is changed but not H5-stored   
        (Re-)Init with AppLog(h5File=...) after using rebuildLookUpDfZips to obtain old lookUpdf   

        main Usage of rebuildLookUpDfZips is to determine which zip7Files to add by i.e.:
        zip7FilesToAdd=lx.lookUpDfZips[~(lx.lookUpDfZips['LastTime']<timeStartAusschnitt) & ~(lx.lookUpDfZips['FirstTime']>timeEndAusschnitt)].index.to_list()
        """ 


        #noDfStorage=False
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:                                                             
                #self.__initzip7File(zip7File=zip7Files[0],h5FileName=h5FileName,nRows=1,readWithDictReader=True)
            
                for zip7File in zip7Files:                    
                    logger.info("{0:s}addZip7File: {1:s}".format(logStr,zip7File))   
                    self.addZip7File(zip7File,firstsAndLastsLogsOnly=True,nRows=1,readWithDictReader=readWithDictReader,noDfStorage=True,readWindowsLog=readWindowsLog)

                logger.debug("{0:s}lookUpDf: {1:s}".format(logStr,self.lookUpDf.to_string()))  
                df=self.lookUpDf.groupby(by='zipName').agg(['min', 'max'])
                logger.debug("{0:s}df: {1:s}".format(logStr,df.to_string()))   

                minTime=df.loc[:,('FirstTime','min')]
                maxTime=df.loc[:,('LastTime','max')]

                minFileNr=df.loc[:,('logName','min')].apply(lambda x: int(re.search(logFilenamePattern,x).group(3)))
                maxFileNr=df.loc[:,('logName','max')].apply(lambda x: int(re.search(logFilenamePattern,x).group(3)))

                s=(maxTime-minTime)/(maxFileNr-minFileNr)
                lookUpDfZips=s.to_frame().rename(columns={0:'TimespanPerLog'})
                lookUpDfZips['NumOfFiles']=maxFileNr-minFileNr
                lookUpDfZips['FirstTime']=minTime
                lookUpDfZips['LastTime']=maxTime
                lookUpDfZips['minFileNr']=minFileNr
                lookUpDfZips['maxFileNr']=maxFileNr

                lookUpDfZips=lookUpDfZips[['FirstTime','LastTime','TimespanPerLog','NumOfFiles','minFileNr','maxFileNr']]

                # lookUpDfZips schreiben
                self.lookUpDfZips=lookUpDfZips
                self.__toH5('lookUpDfZips',self.lookUpDfZips)
                                                             
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def addZip7File(self,zip7File,firstsAndLastsLogsOnly=False,nRows=None,readWithDictReader=False,noDfStorage=False,readWindowsLog=False):
        """
        add zip7File

        Args:
        * zipFile: zipFile which LogFiles shall be added

        * Args for internal Usage: 
            * firstsAndLastsLogsOnly (True dann)
            * nRows (1 dann)
            * readWithDictReader (True dann)
            d.h. es werden nur die ersten und letzten Logs pro Zip angelesen und dort auch nur die 1. und letzte Zeile und das mit DictReader
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:                                             
                # wenn zip7File nicht existiert ...
                if not os.path.exists(zip7File):                     
                   logStrFinal="{0:s}zip7File {1:s} not existing.".format(logStr,zip7File) 
                   logger.debug(logStrFinal)    
                   raise LxError(logStrFinal)    
                else:
                   (zip7FileHead, zip7FileTail)=os.path.split(zip7File)
                   logger.debug("{0:s}zip7FileHead (leer wenn zip7 im selben Verz.): {1:s} zip7FileTail: {2:s}.".format(logStr,zip7FileHead,zip7FileTail))  

                logger.info("{0:s}zip7File: {1:s} ...".format(logStr,zip7File))  
                
                tmpDir=os.path.dirname(zip7File)
                tmpDirContent=glob.glob(tmpDir)
              
                with py7zr.SevenZipFile(zip7File, 'r') as zip7FileObj:                
                    allLogFiles = zip7FileObj.getnames()
                    allLogFilesLen=len(allLogFiles)
                    logger.debug("{0:s}{1:s}: len(getnames()): {2:d}.".format(logStr,zip7FileTail,allLogFilesLen))  

                    extDirLstTBDeleted=[]
                    extDirLstExistingLogged=[]                    

                    for idx,logFileNameInZip in enumerate(allLogFiles):

                        if firstsAndLastsLogsOnly:
                            if idx not in [0,1,allLogFilesLen-2,allLogFilesLen-1]:
                                #logger.debug("{0:s}idx: {1:d} item: {2:s} NOT processed ...".format(logStr,idx,logFileNameInZip))   
                                continue

                        logger.info("{0:s}idx: {1:d} item: {2:s} ...".format(logStr,idx,logFileNameInZip))   

                        # die Datei die 7Zip bei extract erzeugen wird
                        logFile=os.path.join(tmpDir,logFileNameInZip)
                        (logFileHead, logFileTail)=os.path.split(logFile)

                        # evtl. bezeichnet logFileNameInZip keine Datei sondern ein Verzeichnis
                        (name, ext)=os.path.splitext(logFileNameInZip)
                        if ext == '':
                            # Verzeichnis!                        
                            extDir=os.path.join(tmpDir,logFileNameInZip)                       
                            (extDirHead, extDirTail)=os.path.split(extDir)
                            if os.path.exists(extDir) and extDir in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) bereits.".format(logStr,idx,extDirTail))  
                                        extDirLstExistingLogged.append(extDir)
                            elif os.path.exists(extDir) and extDir not in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) noch nicht.".format(logStr,idx,extDirTail))                      
                                        extDirLstTBDeleted.append(extDir)
                            elif not os.path.exists(extDir) and extDir not in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) noch nicht.".format(logStr,idx,extDirTail))                      
                                        extDirLstTBDeleted.append(extDir)
                            # kein Logfile zu prozessieren ...
                            continue

                        # logFileNameInZip bezeichnet eine Datei       
                        if os.path.exists(logFile):
                            isFile = os.path.isfile(logFile)
                            if isFile:
                                logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert bereits. Wird durch Extrakt ueberschrieben werden.".format(logStr,idx,logFileTail))  
                                logFileTBDeleted=False
                            else:
                                logFileTBDeleted=False
                        else:
                            logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert nicht. Wird extrahiert, dann prozessiert und dann wieder geloescht.".format(logStr,idx,logFileTail))                      
                            logFileTBDeleted=True
                  
                        # extrahieren 
                        logger.debug("{0:s}Log: {1:s} wird extrahiert ... ".format(logStr,logFileTail))   
                        import lzma
                        try:
                            zip7FileObj.extract(path=tmpDir,targets=logFileNameInZip)
                        except lzma.LZMAError as e:
                            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                            logger.info(logStrFinal) 
                            logger.warning("{0:s}Log: {1:s} nicht erfolgreich extrahiert - continue ... ".format(logStr,logFileTail))   
                            continue
                        except Exception as e:
                            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                            logger.error(logStrFinal) 
                            raise LxError(logStrFinal)    

                        logger.debug("{0:s}Log: {1:s} wurde extrahiert. ".format(logStr,logFileTail))   
                    
                        if os.path.exists(logFile):
                            pass                       
                        else:
                            logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT extracted?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                            # nichts zu prozessieren ...
                            continue

                        # ...
                        if os.path.isfile(logFile):                                                  
                            df = self.__processALogFile(logFile=logFile,nRows=nRows,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog) 
                            if df is None:      
                                logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT processed?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                                # nichts zu prozessieren ...
                                continue                        
                        # ...

                        # gleich wieder loeschen
                        if os.path.exists(logFile) and logFileTBDeleted:
                            if os.path.isfile(logFile):
                                os.remove(logFile)
                                logger.debug("{0:s}idx: {1:d} Log: {2:s} wieder geloescht.".format(logStr,idx,logFileTail))         

                        #  ...
                        (name, ext)=os.path.splitext(logFileTail)
                        key='Log'+name

                        if zip7FileHead != '':
                            zipName=os.path.join(os.path.relpath(zip7FileHead),zip7FileTail)
                        else:
                            zipName=zip7FileTail
                        # df schreiben
                        self.__toH5(key,df,updLookUpDf=True,logName=logFileTail,zipName=zipName,noDfStorage=noDfStorage)#os.path.join(os.path.relpath(zip7FileHead),zip7FileTail))
                        # danach gleich lookUpDf schreiben ...
                        self.__toH5('lookUpDf',self.lookUpDf,noDfStorage=noDfStorage)
                                
                for dirName in extDirLstTBDeleted:
                    if os.path.exists(dirName):
                        if os.path.isdir(dirName):
                            (dirNameHead, dirNameTail)=os.path.split(dirName)
                            if len(os.listdir(dirName)) == 0:
                                os.rmdir(dirName)                                    
                                logger.debug("{0:s}dirName: {1:s} existierte nicht und wurde wieder geloescht.".format(logStr,dirNameTail))     
                            else:
                                logger.info("{0:s}dirName: {1:s} existiert mit nicht leerem Inhalt?!".format(logStr,dirNameTail))                                                                    
         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def getTotalLogTime(self):
        """       
        Returns Tuple: firstTime,lastTime,tdTotalGross,tdTotal,tdBetweenFilesTotal # Brutto-Logzeit, Netto-Logzeit, Summe aller Zeiten zwischen 2 Logdateien (sollte = Brutto-Netto sein)
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:  

            # Inhalt der Logs
            tdTotal=pd.Timedelta('0 Seconds')
            tdBetweenFilesTotal=pd.Timedelta('0 Seconds')
            for idx,(index,row) in enumerate(self.lookUpDf.iterrows()):               
                if idx > 0:
        
                    tdBetweenFiles=row["FirstTime"]-lastTime
                    tdBetweenFilesTotal=tdBetweenFilesTotal+tdBetweenFiles
        
                    if tdBetweenFiles > pd.Timedelta('0 second'):
                        if tdBetweenFiles > pd.Timedelta('1 second'):
                            logger.info("{:s}Zeitdifferenz: {!s:s} zwischen {:s} ({:s}) und {:s} ({:s})".format(logStr,
                                str(tdBetweenFiles).replace('days','Tage')
                                ,lastFile,lastZip
                                ,row["logName"],row["zipName"]
                            ))    
                        pass
                    if tdBetweenFiles < pd.Timedelta('0 second'):            
                        if tdBetweenFiles < -pd.Timedelta('1 second'):
                            pass
                            logger.info("{:s}Zeitueberlappung > 1s: {!s:s} zwischen {:s} ({:s}) und {:s} ({:s})".format(logStr,
                                str(tdBetweenFiles).replace('days','Tage')
                                ,lastFile,lastZip
                                ,row["logName"],row["zipName"]     
                            ))
            
                td=row["LastTime"]-row["FirstTime"]
                if type(td) == pd.Timedelta:    
                    tdTotal=tdTotal+td
                else:
                    print(index)# Fehler!
                lastTime=row["LastTime"]
                lastFile=row["logName"]
                lastZip=row["zipName"]      
                
            firstTime=self.lookUpDf.iloc[0]["FirstTime"]    
            lastTime=self.lookUpDf.iloc[-1]["LastTime"]
            tdTotalGross=lastTime-firstTime
            tdTotalGross,tdTotal,tdBetweenFilesTotal

                            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            return firstTime,lastTime,tdTotalGross,tdTotal,tdBetweenFilesTotal

    def extractTCsToH5s(self,dfID=pd.DataFrame(),timeStart=None,timeEnd=None,TCsdfOPCFill=TCsdfOPCFill):
        """
        extracts TC-Data (and CVD-Data) from H5 to seperate H5-Files (Postfixe: _TCxxx.h5 and _CVD.h5)

        TCsdfOPCFill: wenn Wahr, werden in TCsdfOPCFill die NULLen aufgefuellt; default: Falsch

        wenn timeStart != None: es wird an exisitierende .h5s angehaengt; sonst werden diese ueberschrieben
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                        
        try:   

            # _TCxxx.h5 anlegen (OPC, SirCalc, LDSIn, LDSRes1, LDSRes2 (,LDSRes)) and _CVD.h5

            # ueber alle dfs in H5 (unter Berücksichtigung von timeStart und timeEnd)
                # lesen
                # TC-Teilmenge ermitteln: 'ID','ProcessTime','ScenTime','SubSystem','Value','Direction'
                    # Zeilen mit 'Value' isnull() werden NICHT gelesen
                    # d.h. bei einer Logfile-Semantik welche durch NULL-Zeilen einen Wert auf (was auch immer) zuruecksetzt wuerde der Wert bei einer Stop-Plot-Ausgabe auf dem letzten Nicht-NULL Wert verharren ...
                    # ... zunaechst ...                    
                # Untermengen bilden: ['TCsdfOPC','TCsdfSirCalc','TCsdfLDSIn','TCsdfLDSRes1','TCsdfLDSRes2' (,'TCsdfLDSRes')]
                    # ... NULLen (NaNs) entstehen durch die Pivotierung mit Index = Time: nicht fuer alles Times (Obermenge) gibt es fuer jede ID Values
                # speichern

            (name,ext)=os.path.splitext(self.h5File)

            TCPost='_TC'
            self.h5FileOPC=name+TCPost+'OPC'+ext
            self.h5FileSirCalc=name+TCPost+'SirCalc'+ext
            self.h5FileLDSIn=name+TCPost+'LDSIn'+ext
            if not dfID.empty:
                # Attribute
                self.h5FileLDSRes1=name+TCPost+'LDSRes1'+ext
                self.h5FileLDSRes2=name+TCPost+'LDSRes2'+ext

                # Komplement wird geloescht
                h5FileLDSRes=name+TCPost+'LDSRes'+ext
                try:
                    # wenn TC-H5 existiert wird es geloescht
                    if os.path.exists(h5FileLDSRes):                                         
                        os.remove(h5FileLDSRes)
                        logger.debug("{0:s}Existing H5-File {1:s} deleted.".format(logStr,h5FileLDSRes))    
                    del self.h5FileLDSRes
                except:
                    pass
            else:
                # Attribut
                self.h5FileLDSRes=name+TCPost+'LDSRes'+ext

                # Komplemente werden geloescht
                h5FileLDSRes1=name+TCPost+'LDSRes1'+ext
                h5FileLDSRes2=name+TCPost+'LDSRes2'+ext
                try:
                    # wenn TC-H5 existiert wird es geloescht
                    if os.path.exists(h5FileLDSRes1):                                         
                        os.remove(h5FileLDSRes1)
                        logger.debug("{0:s}Existing H5-File {1:s} deleted.".format(logStr,h5FileLDSRes1))     
                    # wenn TC-H5 existiert wird es geloescht
                    if os.path.exists(h5FileLDSRes2):                                         
                        os.remove(h5FileLDSRes2)
                        logger.debug("{0:s}Existing H5-File {1:s} deleted.".format(logStr,h5FileLDSRes2))                              
                    del self.h5FileLDSRes1
                    del self.h5FileLDSRes2
                except:
                    pass
            self.h5FileCVD=name+'_'+'CVD'+ext

            h5Keys,h5KeysPost=self.__getH5Keys(timeStart=timeStart,timeEnd=timeEnd)

            h5KeysOPC=['TCsOPC'+x for x in h5KeysPost]
            h5KeysSirCalc=['TCsSirCalc'+x for x in h5KeysPost]
            h5KeysLDSIn=['TCsLDSIn'+x for x in h5KeysPost]
            h5KeysLDSRes1=['TCsLDSRes1'+x for x in h5KeysPost]
            h5KeysLDSRes2=['TCsLDSRes2'+x for x in h5KeysPost]
            h5KeysLDSRes=['TCsLDSRes'+x for x in h5KeysPost]

            h5KeysCVD=['CVDRes'+x for x in h5KeysPost]

            h5KeysAll=zip(h5Keys,h5KeysOPC,h5KeysSirCalc,h5KeysLDSIn,h5KeysLDSRes1,h5KeysLDSRes2,h5KeysLDSRes,h5KeysCVD)
            
            for idx,(h5Key,h5KeyOPC,h5KeySirCalc,h5KeyLDSIn,h5KeyLDSRes1,h5KeyLDSRes2,h5KeyLDSRes,h5KeyCVD) in enumerate(h5KeysAll):

                #H5-Write-Modus
                if idx==0:
                    if timeStart!=None:
                        mode='a'
                    else:
                        mode='w'
                else:
                    mode='a'

                logger.info("{0:s}Get (read_hdf) df with h5Key: {1:s} ...".format(logStr,h5Key)) 
                df=pd.read_hdf(self.h5File, key=h5Key)                   

                # CVD -------------------------------------------------------------------------------------------------
                dfCVD=df[df['SubSystem']=='CVD']

                df=df[['ID','ProcessTime','ScenTime','SubSystem','Value','Direction']]

                df['Value']=df['Value'].apply(lambda x: fTCCast(x))
                df=df[~(df['Value'].isnull())]                

                if not dfID.empty:
                    TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2=self.getTCsFromDf(df,dfID=dfID,TCsdfOPCFill=TCsdfOPCFill)
                else:
                    TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes=self.getTCsFromDf(df,dfID=dfID,TCsdfOPCFill=TCsdfOPCFill)
                                                                                                     
                logger.debug("{0:s}{1:s}".format(logStr,'Write ...'))     

                TCsdfOPC.to_hdf(self.h5FileOPC,h5KeyOPC, mode=mode)               
                TCsdfSirCalc.to_hdf(self.h5FileSirCalc,h5KeySirCalc, mode=mode)               
                TCsdfLDSIn.to_hdf(self.h5FileLDSIn,h5KeyLDSIn, mode=mode)

                if not dfID.empty:                   
                    TCsdfLDSRes1.to_hdf(self.h5FileLDSRes1,h5KeyLDSRes1, mode=mode)                    
                    TCsdfLDSRes2.to_hdf(self.h5FileLDSRes2,h5KeyLDSRes2, mode=mode)
                else:                                       
                    TCsdfLDSRes.to_hdf(self.h5FileLDSRes,h5KeyLDSRes, mode=mode)
                # ---
                dfCVD.to_hdf(self.h5FileCVD,h5KeyCVD, mode=mode)
                                                                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return

    def shrinkH5File(self):
        """       
        die dfs werden geloescht im H5-File
        extract TCs to H5s ### MUSS ### vorher gelaufen sein
        nach shrinkH5File stehen im Master-H5 die eigentlichen Daten nicht mehr zur Verfuegung               
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:  
            # H5 existiert 
            if os.path.exists(self.h5File):
                
                # Keys available
                with pd.HDFStore(self.h5File) as h5Store:
                     h5Keys=sorted(h5Store.keys())         # /Log20201216_0000001                            
                     logger.debug("{0:s}h5Keys available: {1:s}".format(logStr,str(h5Keys))) 

                     for key in h5Keys:
                        if re.match('(^/Log)',key):                            
                            logger.debug("{0:s}key removed: {1:s}".format(logStr,str(key))) 
                            h5Store.remove(key.replace(h5KeySep,''))
                        else:
                            logger.debug("{0:s}key NOT removed: {1:s}".format(logStr,str(key))) 
                
                with pd.HDFStore(self.h5File) as h5Store:
                    pass
                
                shrinkCmd="ptrepack --chunkshape=auto --propindexes --complib=blosc "+self.h5File+" "+self.h5File+".Shrinked"
                logger.debug("{0:s}shrinkCmd: {1:s}".format(logStr,shrinkCmd)) 
                if os.path.exists(self.h5File+".Shrinked"):
                    os.remove(self.h5File+".Shrinked")
                os.system(shrinkCmd)
                os.remove(self.h5File)
                os.rename(self.h5File+".Shrinked",self.h5File)                
                            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

    def get(self,timeStart=None,timeEnd=None,filter_fct=None,filterAfter=True,useRawHdfAPI=False):
        """
        returns df with filter_fct applied
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                
        dfRet=None
        try:   
            dfLst=[]

            dfLookUpTimes=self.lookUpDf
            if timeStart!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende
            dfLookUpTimesIdx=dfLookUpTimes.set_index('logName')
            dfLookUpTimesIdx.filter(regex='\.log$',axis=0)
            h5Keys=['Log'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5Keys used: {1:s}".format(logStr,str(h5Keys))) 
                         
            if useRawHdfAPI:
                with pd.HDFStore(self.h5File) as h5Store:                   
                    for h5Key in h5Keys:
                        logger.debug("{0:s}Get (pd.HDFStore) df with h5Key: {1:s} ...".format(logStr,h5Key)) 
                        df=h5Store[h5Key]
                        if not filterAfter and filter_fct != None:
                            logger.debug("{0:s}Apply Filter ...".format(logStr)) 
                            df=pd.DataFrame(df[df.apply(filter_fct,axis=1)].values,columns=df.columns)                                                     
                        dfLst.append(df)
            else:
                    for h5Key in h5Keys:
                        logger.debug("{0:s}Get (read_hdf) df with h5Key: {1:s} ...".format(logStr,h5Key)) 
                        df=pd.read_hdf(self.h5File, key=h5Key)
                        if not filterAfter and filter_fct != None:
                            logger.debug("{0:s}Apply Filter ...".format(logStr)) 
                            df=pd.DataFrame(df[df.apply(filter_fct,axis=1)].values,columns=df.columns)    
                        dfLst.append(df)     
                        
            logger.debug("{0:s}{1:s}".format(logStr,'Extraction finished. Concat ...')) 
            dfRet=pd.concat(dfLst)
            del dfLst
            if filterAfter and filter_fct != None:
                logger.debug("{0:s}Apply Filter ...".format(logStr)) 
                dfRet=pd.DataFrame(dfRet[dfRet.apply(filter_fct,axis=1)].values,columns=dfRet.columns)   
                               
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            return dfRet

    def getFromZips(self,timeStart=None,timeEnd=None,filter_fct=None,filterAfter=True,readWithDictReader=False,readWindowsLog=False):
        """
        returns df from Zips

        die Daten werden von den Zips gelesen: Log extrahieren, parsen, wieder loeschen
        die Initalisierung muss mit AppLog(zip7Files=...) erfolgt sein da nur dann self.lookUpDfZips existiert
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                
        dfRet=None
        try:   
            dfLst=[]


            timeStart=pd.Timestamp(timeStart)
            timeEnd=pd.Timestamp(timeEnd)

            # zips die prozessiert werden muessen 
            dfLookUpZips=self.lookUpDfZips
            if timeStart!=None:
                dfLookUpZips=dfLookUpZips[dfLookUpZips['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpZips=dfLookUpZips[dfLookUpZips['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende

            for index, row in dfLookUpZips.iterrows():
                
                zip7File=index
                (zip7FileHead, zip7FileTail)=os.path.split(zip7File)
                
               
                dTime=timeStart-row['FirstTime']
                nStart = int(dTime.total_seconds()/row['TimespanPerLog'].total_seconds())
                dTime=timeEnd-timeStart
                nDelta = int(dTime.total_seconds()/row['TimespanPerLog'].total_seconds())+1
                nEnd=nStart+nDelta

                logger.debug("{0:s}zip7File: {1:s}: Start: {2:d}/{3:07d} End: {4:d}/{5:07d}".format(logStr,zip7FileTail
                                                                                                   ,nStart,nStart+row['minFileNr']
                                                                                                   ,nStart+nDelta,nStart+row['minFileNr']+nDelta)) 
            
                try:                                             
                        # wenn zip7File nicht existiert ...
                        if not os.path.exists(zip7File):                     
                           logStrFinal="{0:s}zip7File {1:s} not existing.".format(logStr,zip7File) 
                           logger.debug(logStrFinal)    
                           raise LxError(logStrFinal)    
                
                        tmpDir=os.path.dirname(zip7File)
                        tmpDirContent=glob.glob(tmpDir)
              
                        with py7zr.SevenZipFile(zip7File, 'r') as zip7FileObj:                
                            allLogFiles = zip7FileObj.getnames()
                            allLogFilesLen=len(allLogFiles)
                            logger.debug("{0:s}{1:s}: len(getnames()): {2:d}.".format(logStr,zip7FileTail,allLogFilesLen))  

                            extDirLstTBDeleted=[]
                            extDirLstExistingLogged=[]                    

                            idxEff=0
                            for idx,logFileNameInZip in enumerate(allLogFiles):
                             
                                if idx < nStart-idxEff or idx > nEnd+idxEff: 
                                        continue

                                logger.debug("{0:s}idx: {1:d} item: {2:s} ...".format(logStr,idx,logFileNameInZip))   

                                # die Datei die 7Zip bei extract erzeugen wird
                                logFile=os.path.join(tmpDir,logFileNameInZip)
                                (logFileHead, logFileTail)=os.path.split(logFile)

                                # evtl. bezeichnet logFileNameInZip keine Datei sondern ein Verzeichnis
                                (name, ext)=os.path.splitext(logFileNameInZip)
                                if ext == '':
                                    # Verzeichnis!                        
                                    extDir=os.path.join(tmpDir,logFileNameInZip)                       
                                    (extDirHead, extDirTail)=os.path.split(extDir)
                                    if os.path.exists(extDir) and extDir in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) bereits.".format(logStr,idx,extDirTail))  
                                        extDirLstExistingLogged.append(extDir)
                                    elif os.path.exists(extDir) and extDir not in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) noch nicht.".format(logStr,idx,extDirTail))                      
                                        extDirLstTBDeleted.append(extDir)
                                    elif not os.path.exists(extDir) and extDir not in tmpDirContent:
                                        logger.debug("{0:s}idx: {1:d} extDir: {2:s} existiert(e) noch nicht.".format(logStr,idx,extDirTail))                      
                                        extDirLstTBDeleted.append(extDir)
                                    # kein Logfile zu prozessieren ...
                                    idxEff+=1
                                    continue

                                # logFileNameInZip bezeichnet eine Datei       
                                if os.path.exists(logFile):
                                    isFile = os.path.isfile(logFile)
                                    if isFile:
                                        logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert bereits. Wird durch Extrakt ueberschrieben werden.".format(logStr,idx,logFileTail))  
                                        logFileTBDeleted=False
                                    else:
                                        logFileTBDeleted=False
                                else:
                                    logger.debug("{0:s}idx: {1:d} Log: {2:s} existiert nicht. Wird extrahiert, dann prozessiert und dann wieder geloescht.".format(logStr,idx,logFileTail))                      
                                    logFileTBDeleted=True
                  
                                # extrahieren 
                                zip7FileObj.extract(path=tmpDir,targets=logFileNameInZip)
                    
                                if os.path.exists(logFile):
                                    pass                       
                                else:
                                    logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT extracted?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                                    # nichts zu prozessieren ...
                                    continue

                                # ...
                                if os.path.isfile(logFile):                                                  
                                    df = self.__processALogFile(logFile=logFile,readWithDictReader=readWithDictReader,readWindowsLog=readWindowsLog) 
                                    if df is None:      
                                        logger.warning("{0:s}idx: {1:d} Log: {2:s} NOT processed?! Continue with next Name in 7Zip.".format(logStr,idx,logFileTail))  
                                        # nichts zu prozessieren ...
                                        continue    
                                    else:
                                        if not filterAfter and filter_fct != None:
                                            logger.debug("{0:s}Apply Filter ...".format(logStr)) 
                                            df=pd.DataFrame(df[df.apply(filter_fct,axis=1)].values,columns=df.columns)                
                                        dfLst.append(df)
                                # ...

                                # gleich wieder loeschen
                                if os.path.exists(logFile) and logFileTBDeleted:
                                    if os.path.isfile(logFile):
                                        os.remove(logFile)
                                        logger.debug("{0:s}idx: {1:d} Log: {2:s} wieder geloescht.".format(logStr,idx,logFileTail))         


                                
                        for dirName in extDirLstTBDeleted:
                            if os.path.exists(dirName):
                                if os.path.isdir(dirName):
                                    (dirNameHead, dirNameTail)=os.path.split(dirName)
                                    if len(os.listdir(dirName)) == 0:
                                        os.rmdir(dirName)                                            
                                        logger.debug("{0:s}dirName: {1:s} existierte nicht und wurde wieder geloescht.".format(logStr,dirNameTail))     
                                    else:
                                        logger.info("{0:s}dirName: {1:s} existiert mit nicht leerem Inhalt?!".format(logStr,dirNameTail))                                                                   
         
                except Exception as e:
                    logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.error(logStrFinal) 
                    raise LxError(logStrFinal)                       

            logger.debug("{0:s}{1:s}".format(logStr,'Extraction finished. Concat ...')) 
            dfRet=pd.concat(dfLst)
            del dfLst

            if filterAfter and filter_fct != None:
                logger.debug("{0:s}Apply Filter ...".format(logStr)) 
                dfRet=pd.DataFrame(dfRet[dfRet.apply(filter_fct,axis=1)].values,columns=dfRet.columns)   
                                
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            return dfRet

    def getTCs(self,dfID=pd.DataFrame(),timeStart=None,timeEnd=None,TCsdfOPCFill=TCsdfOPCFill,persistent=False,overwrite=True):
        """
        returns TCs-dfs
        Verarbeitung von dfs gemaess extractTCsToH5s; siehe dort
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                        
        try:   

            TCKeys=['TCsdfOPC','TCsdfSirCalc','TCsdfLDSIn','TCsdfLDSRes1','TCsdfLDSRes2a','TCsdfLDSRes2b','TCsdfLDSRes2c']

            if persistent:        
                 with pd.HDFStore(self.h5File) as h5Store:
                    h5Keys=sorted(h5Store.keys())                                     
                    #logger.debug("{0:s}h5Keys available: {1:s}".format(logStr,str(h5Keys)))                      
                    h5KeysStripped=[item.replace(h5KeySep,'') for item in h5Keys]                   

                 if set(TCKeys) & set(h5KeysStripped) == set(TCKeys):
                    if not overwrite:
                        logger.debug("{0:s}persistent: TCKeys {1:s} existieren alle bereits - return aus H5-File ...".format(logStr,str(TCKeys))) 

                        TCsdfOPC=pd.read_hdf(self.h5File,key='TCsdfOPC')
                        TCsdfSirCalc=pd.read_hdf(self.h5File,key='TCsdfSirCalc')
                        TCsdfLDSIn=pd.read_hdf(self.h5File,key='TCsdfLDSIn')
                        TCsdfLDSRes1=pd.read_hdf(self.h5File,key='TCsdfLDSRes1')
                        TCsdfLDSRes2a=pd.read_hdf(self.h5File,key='TCsdfLDSRes2a')
                        TCsdfLDSRes2b=pd.read_hdf(self.h5File,key='TCsdfLDSRes2b')
                        TCsdfLDSRes2c=pd.read_hdf(self.h5File,key='TCsdfLDSRes2c')
                       
                        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
                        return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2a,TCsdfLDSRes2b,TCsdfLDSRes2c
                    else:
                        logger.debug("{0:s}persistent: TCKeys {1:s} existieren alle bereits - sollen aber ueberschrieben werden ...".format(logStr,str(TCKeys))) 
                        
                 else:                    
                    logger.debug("{0:s}persistent: TCKeys {1:s} existieren nicht (alle) ...".format(logStr,str(TCKeys))) 
                       
            dfLookUpTimes=self.lookUpDf
            if timeStart!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende
            dfLookUpTimesIdx=dfLookUpTimes.set_index('logName')
            dfLookUpTimesIdx.filter(regex='\.log$',axis=0)
            h5Keys=['Log'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5Keys used: {1:s}".format(logStr,str(h5Keys))) 

            dfLst=[]
            for h5Key in h5Keys:
                logger.debug("{0:s}Get (read_hdf) df with h5Key: {1:s} ...".format(logStr,h5Key)) 
                dfSingle=pd.read_hdf(self.h5File, key=h5Key)
                   
                dfSingle=dfSingle[['ID','ProcessTime','ScenTime','SubSystem','Value','Direction']]
                dfSingle=dfSingle[~(dfSingle['Value'].isnull())]

                dfLst.append(dfSingle) 
                                              
            logger.debug("{0:s}{1:s}".format(logStr,'Extraction finished. Concat ...')) 
            df=pd.concat(dfLst)
            del dfLst

            logger.debug("{0:s}{1:s}".format(logStr,'Concat finished. Filter & Pivot ...'))      
            
            if not dfID.empty:
                TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2=self.getTCsFromDf(df,dfID=dfID,TCsdfOPCFill=TCsdfOPCFill)
            else:
                TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes=self.getTCsFromDf(df,dfID=dfID,TCsdfOPCFill=TCsdfOPCFill)
               
            if persistent:                 
                    logger.debug("{0:s}peristent: TCKeys {1:s} nach H5-File ...".format(logStr,str(TCKeys))) 
                    TCsdfOPC.to_hdf(self.h5File,key='TCsdfOPC')
                    TCsdfSirCalc.to_hdf(self.h5File,key='TCsdfSirCalc')
                    TCsdfLDSIn.to_hdf(self.h5File,key='TCsdfLDSIn')
                    TCsdfLDSRes1.to_hdf(self.h5File,key='TCsdfLDSRes1')
                    TCsdfLDSRes2a.to_hdf(self.h5File,key='TCsdfLDSRes2a')
                    TCsdfLDSRes2b.to_hdf(self.h5File,key='TCsdfLDSRes2b')
                    TCsdfLDSRes2c.to_hdf(self.h5File,key='TCsdfLDSRes2c')
                    
                                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            if not dfID.empty:
                return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2#a,TCsdfLDSRes2b,TCsdfLDSRes2c
            else:                
                return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1

    def getTCsFromH5s(self,timeStart=None,timeEnd=None, LDSResOnly=False, LDSResColsSpecified=None, LDSResTypeSpecified=None, timeShiftPair=None):
        """
        returns several TC-dfs from TC-H5s:
            TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2
            or
            TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes        

            LDSResOnly:
            TCsdfLDSRes1,TCsdfLDSRes2
            or
            TCsdfLDSRes       
            
                LDSResColsSpecified:
                return in LDSRes df(s) only the specified cols
                all cols are returned otherwise

                LDSResTypeSpecified:
                return TCsdfLDSRes1 (SEG) for 'SEG' or TCsdfLDSRes2 (Druck) for 'Druck'
                both are returned otherwise

            timeShiftPair: (preriod,freq): i.e. (1,'H'); if not None index is shifted
        """ 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                        
        try:   

            try:
                self.h5FileLDSRes1                
                Res2=True
            except:                
                Res2=False

            TCsdfOPC=pd.DataFrame()
            TCsdfSirCalc=pd.DataFrame()
            TCsdfLDSIn=pd.DataFrame()
            if Res2:                
                TCsdfLDSRes1=pd.DataFrame()
                TCsdfLDSRes2=pd.DataFrame()
            else:
                TCsdfLDSRes=pd.DataFrame()

            dfLookUpTimes=self.lookUpDf
            if timeStart!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende
            dfLookUpTimesIdx=dfLookUpTimes.set_index('logName')
            dfLookUpTimesIdx.filter(regex='\.log$',axis=0)
            h5Keys=['Log'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5Keys used: {1:s}".format(logStr,str(h5Keys))) 


            h5KeysOPC=['TCsOPC'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            h5KeysSirCalc=['TCsSirCalc'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            h5KeysLDSIn=['TCsLDSIn'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            h5KeysLDSRes1=['TCsLDSRes1'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            h5KeysLDSRes2=['TCsLDSRes2'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            h5KeysLDSRes=['TCsLDSRes'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]

            h5KeysAll=zip(h5Keys,h5KeysOPC,h5KeysSirCalc,h5KeysLDSIn,h5KeysLDSRes1,h5KeysLDSRes2,h5KeysLDSRes)
            
            for idx,(h5Key,h5KeyOPC,h5KeySirCalc,h5KeyLDSIn,h5KeyLDSRes1,h5KeyLDSRes2,h5KeyLDSRes) in enumerate(h5KeysAll):

                if not LDSResOnly:
                                                           
                    #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfOPC ...'))                    
                    TCsdfOPC=pd.read_hdf(self.h5FileOPC,h5KeyOPC)

                    #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfSirCalc ...'))                                           
                    TCsdfSirCalc=pd.read_hdf(self.h5FileSirCalc,h5KeySirCalc)

                    #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSIn ...'))                      
                    TCsdfLDSIn=pd.read_hdf(self.h5FileLDSIn,h5KeyLDSIn)

                if Res2:
                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':
                        #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes1 ...'))                      
                        TCsdfLDSRes1=pd.read_hdf(self.h5FileLDSRes1,h5KeyLDSRes1)
                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                        #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes2 ...'))                      
                        TCsdfLDSRes2=pd.read_hdf(self.h5FileLDSRes2,h5KeyLDSRes2)
                else:                   
                    #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes ...'))                    
                    TCsdfLDSRes=pd.read_hdf(self.h5FileLDSRes,h5KeyLDSRes)

                if LDSResColsSpecified != None:                    
                    if Res2:
                        if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':
                            #logger.debug("{0:s}{1:s} {2:s}".format(logStr,'TCsdfLDSRes1 Filter ...',str(LDSResColsSpecified)))                      
                            TCsdfLDSRes1=TCsdfLDSRes1.filter(items=LDSResColsSpecified)
                        if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                            #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes2 Filter ...'))                      
                            TCsdfLDSRes2=TCsdfLDSRes2.filter(items=LDSResColsSpecified)
                    else:                   
                        #logger.debug("{0:s}{1:s}".format(logStr,'TCsdfLDSRes Filter ...'))                    
                        TCsdfLDSRes=TCsdfLDSRes.filter(items=LDSResColsSpecified)

                if idx==0:
                    if not LDSResOnly:
                        TCsdfOPCLst=[]
                        TCsdfSirCalcLst=[]
                        TCsdfLDSInLst=[]
                    if Res2:
                        if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':
                            TCsdfLDSRes1Lst=[]
                        if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                            TCsdfLDSRes2Lst=[]
                    else:
                        TCsdfLDSResLst=[]
                    
                #logger.debug("{0:s}Append ...".format(logStr)) 

                if not LDSResOnly:
                    TCsdfOPCLst.append(TCsdfOPC)
                    TCsdfSirCalcLst.append(TCsdfSirCalc)
                    TCsdfLDSInLst.append(TCsdfLDSIn)
                if Res2:
                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':
                        TCsdfLDSRes1Lst.append(TCsdfLDSRes1)
                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                        TCsdfLDSRes2Lst.append(TCsdfLDSRes2)
                else:
                    TCsdfLDSResLst.append(TCsdfLDSRes)

            logger.debug("{0:s}Concat ...".format(logStr)) 

            if not LDSResOnly:
                TCsdfOPC=pd.concat(TCsdfOPCLst)
                TCsdfSirCalc=pd.concat(TCsdfSirCalcLst)
                TCsdfLDSIn=pd.concat(TCsdfLDSInLst)
                
                if timeShiftPair != None:
                    (period,freq)=timeShiftPair
                    logger.debug("{0:s}timeShift TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn by {1:d} {2:s} ...".format(logStr,period,freq)) 
                    for df in TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn:
                        df.index=df.index.shift(period,freq=freq)

            if Res2:
                if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':
                    TCsdfLDSRes1=pd.concat(TCsdfLDSRes1Lst)
                if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                    TCsdfLDSRes2=pd.concat(TCsdfLDSRes2Lst)

                if timeShiftPair != None:
                    (period,freq)=timeShiftPair

                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='SEG':                    
                        #for df in TCsdfLDSRes1:
                        logger.debug("{:s}timeShift LDSRes1 by {:d} {:s} Ist: {!s:s} {!s:s}  ...".format(logStr,period,freq,TCsdfLDSRes1.index[0],TCsdfLDSRes1.index[-1])) 
                        TCsdfLDSRes1.index=TCsdfLDSRes1.index.shift(period,freq=freq)

                    if LDSResTypeSpecified == None or LDSResTypeSpecified=='Druck':
                        #for df in TCsdfLDSRes2:
                        logger.debug("{:s}timeShift LDSRes2 by {:d} {:s} Ist: {!s:s} {!s:s}  ...".format(logStr,period,freq,TCsdfLDSRes2.index[0],TCsdfLDSRes2.index[-1])) 
                        TCsdfLDSRes2.index=TCsdfLDSRes2.index.shift(period,freq=freq)

            else:
                TCsdfLDSRes=pd.concat(TCsdfLDSResLst)

                if timeShiftPair != None:
                    (period,freq)=timeShiftPair
                    logger.debug("{0:s}timeShift LDSRes by {1:d} {2:s} ...".format(logStr,period,freq)) 
                    for df in TCsdfLDSRes:
                        df.index=df.index.shift(period,freq=freq)
                                                                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            if not LDSResOnly:
                if Res2:
                    return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes1,TCsdfLDSRes2
                else:
                    return TCsdfOPC,TCsdfSirCalc,TCsdfLDSIn,TCsdfLDSRes
            else:
                if Res2:
                    if LDSResTypeSpecified == None:
                        return TCsdfLDSRes1,TCsdfLDSRes2
                    elif LDSResTypeSpecified=='SEG':
                        return TCsdfLDSRes1
                    elif LDSResTypeSpecified=='Druck':
                        return TCsdfLDSRes2
                else:
                    return TCsdfLDSRes

    def __getH5Keys(self,timeStart=None,timeEnd=None):
        """
        returns h5Keys (keys fuer Logfiles in h5File), h5KeysPost (key Postfixe fuer dfs in allen anderen h5Files)  
        """ 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                        
        try:   

            dfLookUpTimes=self.lookUpDf
            if timeStart!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende
            dfLookUpTimesIdx=dfLookUpTimes.set_index('logName')
            #dfLookUpTimesIdx.filter(regex='\.log$',axis=0)

            h5Keys=['Log'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5Keys: {1:s}".format(logStr,str(h5Keys))) 

            h5KeysPost=[re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5KeysPost: {1:s}".format(logStr,str(h5KeysPost))) 
                                                                               
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return h5Keys,h5KeysPost

    def getCVDFromH5(self,timeStart=None,timeEnd=None,timeDelta=None,returnDfCVDataOnly=False):
        """
        returns dfCVD, dfCVDataOnly 
        dfCVD:          all rows with Subsystem CVD 
        dfCVDataOnly:   CVs from dfCVD

        timeDelta: i.e. pd.Timedelta('1 Hour'); if not None ScenTime is shifted by + timeDelta

        returns dfCVDataOnly only, if returnDfCVDataOnly
        """ 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        dfCVD=pd.DataFrame()
        dfCVDataOnly=pd.DataFrame()
                        
        try:   

            h5Keys,h5KeysPost=self.__getH5Keys(timeStart=timeStart,timeEnd=timeEnd)

            h5KeysCVD=['CVDRes'+x for x in h5KeysPost]
            
            if timeDelta != None:                
                    logger.debug("{0:s}timeShift ScenTime by + {1:s} ...".format(logStr,str(timeDelta))) 
                        
            for idx,h5KeyCVD in enumerate(h5KeysCVD):
                                                                                        
                dfCVD=pd.read_hdf(self.h5FileCVD,h5KeyCVD)

                if timeDelta != None:                
                    #logger.debug("{0:s}timeShift ScenTime by + {1:s} ...".format(logStr,str(timeDelta))) 
                    dfCVD['ScenTime']=dfCVD['ScenTime']+timeDelta

                dfCVDataOnly=pd.DataFrame()
                dfCVDBEGIN=dfCVD[dfCVD['Remark'].str.contains('^BEGIN_OF_NEW_CONTROL_VOLUME')].copy(deep=True)
                
                if not dfCVDBEGIN.empty:
                    try:
                        dfCVDBEGIN['ZHKNR']=dfCVDBEGIN['Value'].astype('int64')
                    except:
                        logger.debug("{:s}Parsen von Value nach ZHKNR in Zeile mit BEGIN_OF_NEW_CONTROL_VOLUME schlaegt fehlt. Vmtl. aeltere App-Log Version.".format(logStr)) 
                        dfCVDBEGIN['ZHKNR']=-1

                    dfCVDBEGIN_Remarks=dfCVDBEGIN['Remark'].str.split(pat=';',expand=True)
                    #logger.debug("{:s}dfCVDBEGIN_Remarks: {:s}".format(logStr,dfCVDBEGIN_Remarks.to_string())) 
                    try:
                        dfCVDNames=dfCVDBEGIN_Remarks[dfCVDBEGIN_Remarks[0].str.contains('^BEGIN_OF_NEW_CONTROL_VOLUME')][[1]][1].str.replace('NULL','')
                    except:
                        logger.debug("{:s}Split von Remark mit ; schlug vmtl. fehl. Vmtl. aeltere App-Log Version.".format(logStr)) 
                        dfCVDBEGIN_Remarks=dfCVDBEGIN['Remark'].str.split(pat='\t',expand=True)
                        #logger.debug("{:s}dfCVDBEGIN_Remarks: {:s}".format(logStr,dfCVDBEGIN_Remarks.to_string())) 
                        dfCVDNames=dfCVDBEGIN_Remarks[dfCVDBEGIN_Remarks[0].str.contains('^BEGIN_OF_NEW_CONTROL_VOLUME')][[1]][1].str.replace('NULL','')

                    dfCVDBEGIN=dfCVDBEGIN.join(dfCVDNames).rename(columns={1:'Name'})                                   
                    dfCVDataOnly=dfCVDBEGIN[['ScenTime','ZHKNR','ID','Name']].rename(columns={'ID':'Type'}).reset_index(drop=True)

                if idx==0:
                    if not returnDfCVDataOnly:
                        dfCVDLst=[]
                    dfCVDataOnlyLst=[]

                # Liste ergaenzen
                if not returnDfCVDataOnly:
                    dfCVDLst.append(dfCVD)
                if not dfCVDataOnly.empty:
                    dfCVDataOnlyLst.append(dfCVDataOnly)
                               
            # Listen verketten und Nachbereitung
            if not returnDfCVDataOnly:
                dfCVD=pd.concat(dfCVDLst)
                dfCVD=dfCVD.reset_index(drop=True)

            dfCVDataOnly=pd.concat(dfCVDataOnlyLst)
            dfCVDataOnly=dfCVDataOnly.reset_index(drop=True)
                                                                                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            if returnDfCVDataOnly:
                return dfCVDataOnly
            else:
                return dfCVD,dfCVDataOnly

    def getTCsSpecified(self,dfID=pd.DataFrame(),timeStart=None,timeEnd=None,f=lambda row: True if row['E'] == 'AL_S' else False):
        """
        returns specified IDs as 1 TCs-df (with ScenTime as Index)
        """ 
 
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                        
        try:   
                                   
            dfLookUpTimes=self.lookUpDf
            if timeStart!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['LastTime']>=timeStart] # endet nach dem Anfang oder EndeFile ist Anfang
            if timeEnd!=None:
                dfLookUpTimes=dfLookUpTimes[dfLookUpTimes['FirstTime']<=timeEnd] # beginnt vor dem Ende oder AnfangFile ist Ende
            dfLookUpTimesIdx=dfLookUpTimes.set_index('logName')
            dfLookUpTimesIdx.filter(regex='\.log$',axis=0)
            h5Keys=['Log'+re.search(logFilenameHeadPattern,logFile).group(1) for logFile in dfLookUpTimesIdx.index]
            logger.debug("{0:s}h5Keys used: {1:s}".format(logStr,str(h5Keys))) 

          
            dfLst=[]
            for h5Key in h5Keys:
                logger.debug("{0:s}Get (read_hdf) df with h5Key: {1:s} ...".format(logStr,h5Key)) 
                dfSingle=pd.read_hdf(self.h5File, key=h5Key)
                   
                dfSingle=dfSingle[['ID','ScenTime','Value']]
                dfSingle=dfSingle[~(dfSingle['Value'].isnull())]

                if not dfID.empty:
                    dfSingle=dfSingle.merge(dfID,how='left',left_on='ID',right_index=True,suffixes=('','_r'))       
                    dfSingle=dfSingle[dfSingle.apply(f,axis=1)]

                dfLst.append(dfSingle[['ID','ScenTime','Value']]) 
                del dfSingle
                                              
            logger.debug("{0:s}{1:s}".format(logStr,'Extraction finished. Concat ...')) 
            df=pd.concat(dfLst)
            del dfLst
            df=df.pivot_table(index='ScenTime', columns='ID', values='Value', aggfunc='last')  
                                                       
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise LxError(logStrFinal)                       
        finally:           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
            return df

if __name__ == "__main__":
    """
    Run Lx-Stuff or/and perform Lx-Unittests.
    """

    try:              
        # Logfile
        head,tail = os.path.split(__file__)
        file,ext = os.path.splitext(tail)
        logFileName = os.path.normpath(os.path.join(head,os.path.normpath('./testresults'))) 
        logFileName = os.path.join(logFileName,file + '.log') 
        
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
                                      
        # Arguments      
        parser = argparse.ArgumentParser(description='Run Lx-Stuff or/and perform Lx-Unittests.'
        ,epilog='''
        UsageExample#1: (without parameter): -v --x ./testdata/20171103__000001.log   
        '''                                 
        )
        parser.add_argument('--x','--logFile',type=str, help='.log File (default: ./testdata/Lx/20201113_0000003.log)',default='./testdata/Lx/20201113_0000003.log')  

        group = parser.add_mutually_exclusive_group()                                
        group.add_argument("-v","--verbose", help="Debug Messages On", action="store_true",default=True)      
        group.add_argument("-q","--quiet", help="Debug Messages Off", action="store_true")                  
        args = parser.parse_args()

        if args.verbose:           
            logger.setLevel(logging.DEBUG)     
        else:            
            logger.setLevel(logging.ERROR)  
                      
        logger.debug("{0:s}{1:s}{2:s}".format(logStr,'Start. Argumente:',str(sys.argv))) 

        lx=AppLog(logFile=args.x)

    except SystemExit:
        pass                                              
    except:
        logger.error("{0:s}{1:s}".format(logStr,'logging.exception!')) 
        logging.exception('')  
    else:
        logger.debug("{0:s}{1:s}".format(logStr,'No Exception.')) 
        sys.exit(0)
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.')) 
        sys.exit(0)

