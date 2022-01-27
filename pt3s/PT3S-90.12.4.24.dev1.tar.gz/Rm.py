"""
"""
"""
>>> # ---
>>> # SETUP
>>> # ---
>>> import os
>>> import logging
>>> logger = logging.getLogger('PT3S.Rm')
>>> # ---
>>> # path
>>> # ---
>>> if __name__ == "__main__":
...   try:
...      dummy=__file__
...      logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ','path = os.path.dirname(__file__)'," .")) 
...      path = os.path.dirname(__file__)
...   except NameError:    
...      logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ',"path = '.' because __file__ not defined and: "," from Rm import Rm")) 
...      path = '.'
...      from Rm import Rm 
... else:
...    path = '.'
...    logger.debug("{0:s}{1:s}".format('Not __main__ Context: ',"path = '.' .")) 
>>> try:
...    from PT3S import Mx
... except ImportError:
...    logger.debug("{0:s}{1:s}".format("DOCTEST: from PT3S import Mx: ImportError: ","trying import Mx instead ... maybe pip install -e . is active ..."))  
...    import Mx
>>> try:
...    from PT3S import Xm
... except ImportError:
...    logger.debug("{0:s}{1:s}".format("DOCTEST: from PT3S import Xm: ImportError: ","trying import Xm instead ... maybe pip install -e . is active ..."))  
...    import Xm
>>> # ---
>>> # testDir
>>> # ---
>>> # globs={'testDir':'testdata'}
>>> try:
...    dummy= testDir
... except NameError:
...    testDir='testdata' 
>>> # ---
>>> # dotResolution
>>> # ---
>>> # globs={'dotResolution':''}
>>> try:
...     dummy= dotResolution
... except NameError:
...     dotResolution='' 
>>> import pandas as pd
>>> import matplotlib.pyplot as plt
>>> pd.set_option('display.max_columns',None)
>>> pd.set_option('display.width',666666666)
>>> # ---
>>> # LocalHeatingNetwork SETUP
>>> # ---
>>> xmlFile=os.path.join(os.path.join(path,testDir),'LocalHeatingNetwork.XML')
>>> xm=Xm.Xm(xmlFile=xmlFile)
>>> mx1File=os.path.join(path,os.path.join(testDir,'WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1'+dotResolution+'.MX1')) 
>>> mx=Mx.Mx(mx1File=mx1File,NoH5Read=True,NoMxsRead=True)
>>> mx.setResultsToMxsFile(NewH5Vec=True)
5
>>> xm.MxSync(mx=mx)
>>> rm=Rm(xm=xm,mx=mx)
>>> # ---
>>> # Plot 3Classes False
>>> # ---
>>> plt.close('all')
>>> ppi=72 # matplotlib default
>>> dpi_screen=2*ppi
>>> fig=plt.figure(dpi=dpi_screen,linewidth=1.)
>>> timeDeltaToT=mx.df.index[2]-mx.df.index[0]
>>> # 3Classes und FixedLimits sind standardmaessig Falsch; RefPerc ist standardmaessig Wahr
>>> # die Belegung von MCategory gemaess FixedLimitsHigh/Low erfolgt immer ... 
>>> pFWVB=rm.pltNetDHUS(timeDeltaToT=timeDeltaToT,pFWVBMeasureCBFixedLimitHigh=0.80,pFWVBMeasureCBFixedLimitLow=0.66,pFWVBGCategory=['BLNZ1u5u7'],pVICsDf=pd.DataFrame({'Kundenname': ['VIC1'],'Knotenname': ['V-K007']}))
>>> # ---
>>> # Check pFWVB Return
>>> # ---
>>> f=lambda x: "{0:8.5f}".format(x) 
>>> print(pFWVB[['Measure','MCategory','GCategory','VIC']].round(2).to_string(formatters={'Measure':f}))
   Measure MCategory  GCategory   VIC
0  0.81000       Top  BLNZ1u5u7   NaN
1  0.67000    Middle              NaN
2  0.66000    Middle  BLNZ1u5u7   NaN
3  0.66000    Bottom  BLNZ1u5u7  VIC1
4  0.69000    Middle              NaN
>>> # ---
>>> # Print 
>>> # ---
>>> (wD,fileName)=os.path.split(xm.xmlFile)
>>> (base,ext)=os.path.splitext(fileName)
>>> plotFileName=wD+os.path.sep+base+'.'+'pdf'
>>> if os.path.exists(plotFileName):                        
...    os.remove(plotFileName)
>>> plt.savefig(plotFileName,dpi=2*dpi_screen)
>>> os.path.exists(plotFileName)
True
>>> # ---
>>> # Plot 3Classes True
>>> # ---
>>> plt.close('all')
>>> # FixedLimits wird automatisch auf Wahr gesetzt wenn 3Classes Wahr ... 
>>> pFWVB=rm.pltNetDHUS(timeDeltaToT=timeDeltaToT,pFWVBMeasure3Classes=True,pFWVBMeasureCBFixedLimitHigh=0.80,pFWVBMeasureCBFixedLimitLow=0.66)
>>> # ---
>>> # LocalHeatingNetwork Clean Up
>>> # ---
>>> if os.path.exists(mx.h5File):                        
...    os.remove(mx.h5File)
>>> if os.path.exists(mx.mxsZipFile):                        
...    os.remove(mx.mxsZipFile)
>>> if os.path.exists(mx.h5FileVecs):                        
...    os.remove(mx.h5FileVecs)
>>> if os.path.exists(plotFileName):                        
...    os.remove(plotFileName)
"""

__version__='90.12.4.23.dev1'

import warnings # 3.6
#...\Anaconda3\lib\site-packages\h5py\__init__.py:36: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated. In future, it will be treated as `np.float64 == np.dtype(float).type`.
#   from ._conv import register_converters as _register_converters
warnings.simplefilter(action='ignore', category=FutureWarning)

#C:\Users\Wolters\Anaconda3\lib\site-packages\matplotlib\cbook\deprecation.py:107: MatplotlibDeprecationWarning: Adding an axes using the same arguments as a previous axes currently reuses the earlier instance.  In a future version, a new instance will always be created and returned.  Meanwhile, this warning can be suppressed, and the future behavior ensured, by passing a unique label to each axes instance.
#  warnings.warn(message, mplDeprecation, stacklevel=1)
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
warnings.filterwarnings("ignore", 'This pattern has match groups')

import os
import sys

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

import timeit

import xml.etree.ElementTree as ET
import re
import struct
import collections
import zipfile
import pandas as pd
import h5py

from collections import namedtuple
from operator import attrgetter

import subprocess

import warnings
import tables
import math

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.colorbar import make_axes

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from matplotlib import markers
from matplotlib.path import Path

from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib.backends.backend_pdf import PdfPages

import numpy as np
import scipy
import networkx as nx
from itertools import chain
import math
import sys

from copy import deepcopy

from itertools import chain 

import scipy
from scipy.signal import savgol_filter

from collections import Counter


import logging
# ---
# --- PT3S Imports
# ---
logger = logging.getLogger('PT3S')  
if __name__ == "__main__":
    logger.debug("{0:s}{1:s}".format('in MODULEFILE: __main__ Context','.')) 
else:
    logger.debug("{0:s}{1:s}{2:s}{3:s}".format('in MODULEFILE: Not __main__ Context: ','__name__: ',__name__," .")) 

try:
    from PT3S import Mx
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Mx - trying import Mx instead ... maybe pip install -e . is active ...')) 
    import Mx

try:
    from PT3S import Xm
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Xm - trying import Xm instead ... maybe pip install -e . is active ...')) 
    import Xm

try:
    from PT3S import Am
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Am - trying import Am instead ... maybe pip install -e . is active ...')) 
    import Am

try:
    from PT3S import Lx
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Lx - trying import Lx instead ... maybe pip install -e . is active ...')) 
    import Lx

# ---
# --- main Imports
# ---
import argparse
import unittest
import doctest

import math

from itertools import tee

# --- Parameter Allgemein
# -----------------------

DINA6 =  (4.13 ,  5.83)
DINA5 =  (5.83 ,  8.27)
DINA4 =  (8.27 , 11.69)
DINA3 = (11.69 , 16.54)
DINA2 = (16.54 , 23.39)
DINA1 = (23.39 , 33.11)
DINA0 = (33.11 , 46.81)

DINA6q =  (  5.83, 4.13)
DINA5q =  (  8.27, 5.83)
DINA4q =  ( 11.69, 8.27)
DINA3q =  ( 16.54,11.69)
DINA2q =  ( 23.39,16.54)
DINA1q =  ( 33.11,23.39)
DINA0q =  ( 46.81,33.11)

dpiSize=72

DINA4_x=8.2677165354
DINA4_y=11.6929133858

DINA3_x=DINA4_x*math.sqrt(2)
DINA3_y=DINA4_y*math.sqrt(2)

linestyle_tuple = [
     ('loosely dotted',        (0, (1, 10))),
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('loosely dashed',        (0, (5, 10))),
     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]

ylimpD=(-5,70)
ylimpDmlc=(600,1350) #(300,1050)  

ylimQD=(-75,300)
ylim3rdD=(0,3)
yticks3rdD=[0,1,2,3]
yGridStepsD=30

yticksALD=[0,3,4,10,20,30,40]
ylimALD=(yticksALD[0],yticksALD[-1])

yticksRD=[0,2,4,10,15,30,45] 
ylimRD=(-yticksRD[-1],yticksRD[-1])

ylimACD=(-5,5)
yticksACD=[-5,0,5] 

yticksTVD=[0,100,135,180,200,300]  
ylimTVD=(yticksTVD[0],yticksTVD[-1])
plotTVAmLabelD='TIMER u. AM [Sek. u. (N)m3]'

def getDerivative(df,col,shiftSize=1,windowSize=60,fct=None,savgol_polyorder=None):
    """
    returns a df

    df: the df
    col: the col of df to be derived
    shiftsize: the Difference between 2 indices for dValue and dt
    windowSize: size for rolling mean or window_length of savgol_filter; choosen filtertechnique is applied after fct
                windowsSize must be an even number
                for savgol_filter windowsSize-1 is used 
    fct: function to be applied on dValue/dt 
    savgol_polyorder: if not None savgol_filter is applied; pandas' rolling.mean() is applied otherwise

    new cols:
            dt (with shiftSize)
            dValue (from col)
            dValueDt (from col); fct applied
            dValueDtFiltered; choosen filtertechnique is applied
    """

    
    mDf=df.dropna().copy(deep=True)

    try:    
        
      
        dt=mDf.index.to_series().diff(periods=shiftSize)
        mDf['dt']=dt
        mDf['dValue']=mDf[col].diff(periods=shiftSize)
        mDf=mDf.iloc[shiftSize:]
        mDf['dValueDt']=mDf.apply(lambda row: row['dValue']/row['dt'].total_seconds(),axis=1)       

        if fct != None:
            mDf['dValueDt']=mDf['dValueDt'].apply(fct)            

        if savgol_polyorder == None:
            mDf['dValueDtFiltered']=mDf['dValueDt'].rolling(window=windowSize).mean()
            mDf=mDf.iloc[windowSize-1:]
        else:           
            mDf['dValueDtFiltered']=savgol_filter(mDf['dValueDt'].values,windowSize-1, savgol_polyorder)
            mDf=mDf.iloc[windowSize/2+1+savgol_polyorder-1:]

        #mDf=mDf.iloc[windowSize-1:]               
    except Exception as e:        
        raise e            
    finally:                   
        return mDf



def fCVDNodesFromName(x):
    Nodes=x.replace('Â°','~')
    Nodes=Nodes.split('~')
    
    Nodes =[Node.lstrip().rstrip() for Node in Nodes if len(Node)>0]
    return Nodes

def fgetMaxpMinFromName(CVDName,dfSegsNodesNDataDpkt):
    """
    returns max. pMin for alle NODEs in CVDName
    """
    
    nodeLst=fCVDNodesFromName(CVDName)
    df=dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['NODEsName'].isin(nodeLst)][['pMin','pMinMlc']]
    s=df.max()
    return s.pMin

# --- Funktionen Allgemein
# -----------------------

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def genTimespans(timeStart
     ,timeEnd
     ,timeSpan=pd.Timedelta('12 Minutes')
     ,timeOverlap=pd.Timedelta('0 Seconds')
     ,timeStartPraefix=pd.Timedelta('0 Seconds')
     ,timeEndPostfix=pd.Timedelta('0 Seconds')
    ):
    
    # generates timeSpan-Sections 

    # if timeStart is 
    #     an int, it is considered as the number of desired Sections before timeEnd; timeEnd must be a time
    #     a time, it is considered as timeStart      
    
    # if timeEnd is 
    #     an int, it is considered as the number of desired Sections after timeStart; timeStart must be a time
    #     a time, it is considered as timeEnd 
    
    # if timeSpan is 
    #     an int, it is considered as the number of desired Sections 
    #     a time, it is considered as timeSpan
    
    # returns an array of tuples

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    xlims=[]

    try:
 
        if type(timeStart) == int:    
            numOfDesiredSections=timeStart                
            timeStartEff=timeEnd+timeEndPostfix-numOfDesiredSections*timeSpan+(numOfDesiredSections-1)*timeOverlap-timeStartPraefix
        else:        
            timeStartEff=timeStart-timeStartPraefix
        logger.debug("{0:s}timeStartEff: {1:s}".format(logStr,str(timeStartEff))) 
    
        if type(timeEnd) == int:    
            numOfDesiredSections=timeEnd
            timeEndEff=timeStart-timeStartPraefix+numOfDesiredSections*timeSpan-(numOfDesiredSections-1)*timeOverlap+timeEndPostfix        
        else:        
            timeEndEff=timeEnd+timeEndPostfix
        logger.debug("{0:s}timeEndEff: {1:s}".format(logStr,str(timeEndEff))) 
    
        if type(timeSpan) == int:    
            numOfDesiredSections=timeSpan  
            dt=timeEndEff-timeStartEff
            timeSpanEff=dt/numOfDesiredSections+(numOfDesiredSections-1)*timeOverlap        
        else:        
            timeSpanEff=timeSpan
        logger.debug("{0:s}timeSpanEff: {1:s}".format(logStr,str(timeSpanEff))) 
    
        logger.debug("{0:s}timeOverlap: {1:s}".format(logStr,str(timeOverlap)))  
        
        timeStartAct = timeStartEff           
        while timeStartAct < timeEndEff: 
            logger.debug("{0:s}timeStartAct: {1:s}".format(logStr,str(timeStartAct)))  
            timeEndAct=timeStartAct+timeSpanEff
            xlim=(timeStartAct,timeEndAct)
            xlims.append(xlim)        
            timeStartAct = timeEndAct - timeOverlap         
    
   

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return xlims

def gen2Timespans(
      timeStart # Anfang eines "Prozesses"
     ,timeEnd # Ende eines "Prozesses"
     ,timeSpan=pd.Timedelta('12 Minutes')     
     ,timeStartPraefix=pd.Timedelta('0 Seconds')
     ,timeEndPostfix=pd.Timedelta('0 Seconds')
     ,roundStr=None # i.e. '5min': timeStart.round(roundStr) und timeEnd dito
    ):

    """
    erzeugt 2 gleich lange Zeitbereiche
    1 um timeStart herum
    1 um timeEnd   herum
    """
      
    #print("timeStartPraefix: {:s}".format(str(timeStartPraefix)))
    #print("timeEndPostfix: {:s}".format(str(timeEndPostfix)))
    
    xlims=[]

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:

        if roundStr != None:
            timeStart=timeStart.round(roundStr)
            timeEnd=timeEnd.round(roundStr)

        xlims.append((timeStart-timeStartPraefix,timeStart-timeStartPraefix+timeSpan))
        xlims.append((timeEnd+timeEndPostfix-timeSpan,timeEnd+timeEndPostfix))
     
        return xlims

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return xlims

def fTotalTimeFromPairs(
     x
    ,denominator=None # i.e. pd.Timedelta('1 minute') for totalTime in Minutes
    ,roundToInt=True # round to and return as int if denominator is specified; else td is rounded by 2
):
    tdTotal=pd.Timedelta('0 seconds')
    for idx,tPairs in enumerate(x):

        t1,t2=tPairs
        if idx==0:
            tLast=t2                
        else:
            if t1 <= tLast:
                print("Zeitpaar überlappt?!")        
        td=t2-t1
        if td < pd.Timedelta('1 seconds'):
            pass
            #print("Zeitpaar < als 1 Sekunde?!")     
        
        
        tdTotal=tdTotal+td
    if denominator==None:
        return tdTotal
    else:
        td=tdTotal / denominator
        if roundToInt:
            td=int(round(td,0))
        else:
            td=round(td,2)
        return td

def findAllTimeIntervalls(
 df
,fct=lambda row: True if row['col'] == 46 else False
,tdAllowed=None 
):

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    tPairs=[]

    try:

        rows,cols=df.shape

        if df.empty:            
            logger.debug("{:s}df ist leer".format(logStr)) 

        elif rows == 1:            
            logger.debug("{:s}df hat nur 1 Zeile: {:s}".format(logStr,df.to_string()))       
                                   
            rowValue=fct(df.iloc[0])
            if rowValue:
                tPair=(df.index[0],df.index[0])
                tPairs.append(tPair)    
            else:
                pass                
            
        else:


            tEin=None
            # paarweise über alle Zeilen
            for (i1, row1), (i2, row2) in pairwise(df.iterrows()):    
                row1Value=fct(row1)
                row2Value=fct(row2)

                # wenn 1 nicht x und 2       x tEin=t2 "geht Ein"
                if not row1Value and row2Value:
                    tEin=i2

                # wenn 1       x und 2 nicht x tAus=t2 "geht Aus"
                elif row1Value and not row2Value:
                    if tEin != None:
                        # Paar speichern                    
                        tPair=(tEin,i1)
                        tPairs.append(tPair)            
                    else:
                        pass # sonst: Bed. ist jetzt Aus und war nicht Ein
                        # Bed. kann nur im ersten Fall Ein gehen

                # wenn 1       x und 2       x
                elif row1Value and row2Value: 
                    if tEin != None:
                        pass
                    else:
                        # im ersten Wertepaar ist der Bereich Ein
                        tEin=i1

            # letztes Paar
            if row1Value and row2Value: 
                    if tEin != None:
                        tPair=(tEin,i2)
                        tPairs.append(tPair)    

            if tdAllowed != None:            
                tPairs=fCombineSubsequenttPairs(tPairs,tdAllowed)

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return tPairs

def findAllTimeIntervallsSeries(
 s=pd.Series()
,fct=lambda x: True if x == 46 else False
,tdAllowed=None # if not None all subsequent TimePairs with TimeDifference <= tdAllowed are combined to one TimePair
,debugOutput=True
):
    """
    # if fct: 
    #       alle [Zeitbereiche] finden fuer die fct Wahr ist; diese Zeitbereiche werden geliefert; es werden nur Paare geliefert; Wahr-Solitäre gehen nicht verloren sondern werden als Paar (t,t)  geliefert
    #       Wahr-Solitäre sind NUR dann enthalten, wenn s nur 1 Wert enthält und dieser Wahr ist; das 1 gelieferte Paar enthaelt dann den Solitär-Zeitstempel für beide Zeiten
    #       tdAllowed can be be specified
    #       dann im Anschluss in Zeitbereiche zusammenfassen, die nicht mehr als tdAllowed auseinander liegen; diese Zeitbereiche werden dann geliefert

    # if fct None: 
    #       tdAllowed must be specified
    #       in Zeitbereiche zerlegen, die nicht mehr als Schwellwert tdAllowed auseinander liegen; diese Zeitbereiche werden geliefert
    #       generell hat jeder gelieferte Zeitbereich Anfang und Ende (d.h. 2 Zeiten), auch dann, wenn dadurch ein- oder mehrfach der Schwellwert ignoriert werden muss
    #       denn es soll kein Zeitbereich verloren gehen, der in s enthalten ist
    #       wenn s nur 1 Wert enthält, wird 1 Zeitpaar mit demselben Zeitstempel für beide Zeiten geliefert, wenn Wert nicht Null

    # returns array of Time-Pair-Tuples    
    >>> import pandas as pd
    >>> t=pd.Timestamp('2021-03-19 01:02:00')
    >>> t1=t +pd.Timedelta('1 second')
    >>> t2=t1+pd.Timedelta('1 second')
    >>> t3=t2+pd.Timedelta('1 second')
    >>> t4=t3+pd.Timedelta('1 second')
    >>> t5=t4+pd.Timedelta('1 second')
    >>> t6=t5+pd.Timedelta('1 second')
    >>> t7=t6+pd.Timedelta('1 second')
    >>> d = {t1: 46, t2: 0} # geht aus - kein Paar
    >>> s1PaarGehtAus=pd.Series(data=d, index=[t1, t2])
    >>> d = {t1: 0, t2: 46} # geht ein - kein Paar
    >>> s1PaarGehtEin=pd.Series(data=d, index=[t1, t2])
    >>> d = {t5: 46, t6: 0} # geht ausE - kein Paar
    >>> s1PaarGehtAusE=pd.Series(data=d, index=[t5, t6])
    >>> d = {t5: 0, t6: 46} # geht einE - kein Paar
    >>> s1PaarGehtEinE=pd.Series(data=d, index=[t5, t6])
    >>> d = {t1: 46, t2: 46} # geht aus - ein Paar
    >>> s1PaarEin=pd.Series(data=d, index=[t1, t2])
    >>> d = {t1: 0, t2: 0} # geht aus - kein Paar
    >>> s1PaarAus=pd.Series(data=d, index=[t1, t2])
    >>> s2PaarAus=pd.concat([s1PaarGehtAus,s1PaarGehtAusE])
    >>> s2PaarEin=pd.concat([s1PaarGehtEin,s1PaarGehtEinE])
    >>> s2PaarAusEin=pd.concat([s1PaarGehtAus,s1PaarGehtEinE])
    >>> s2PaarEinAus=pd.concat([s1PaarGehtEin,s1PaarGehtAusE])
    >>> # 1 Wert
    >>> d = {t1: 46} # 1 Wert - Wahr
    >>> s1WertWahr=pd.Series(data=d, index=[t1])
    >>> d = {t1: 44} # 1 Wert - Falsch
    >>> s1WertFalsch=pd.Series(data=d, index=[t1])
    >>> d = {t1: None} # 1 Wert - None
    >>> s1WertNone=pd.Series(data=d, index=[t1])
    >>> ###
    >>> # 46  0
    >>> # 0  46
    >>> # 0   0
    >>> # 46 46 !1 Paar
    >>> # 46  0  46  0
    >>> # 46  0   0 46
    >>> # 0  46   0 46
    >>> # 0  46  46  0 !1 Paar
    >>> ###
    >>> findAllTimeIntervallsSeries(s1PaarGehtAus)
    []
    >>> findAllTimeIntervallsSeries(s1PaarGehtEin)
    []
    >>> findAllTimeIntervallsSeries(s1PaarEin)
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02'))]
    >>> findAllTimeIntervallsSeries(s1PaarAus)
    []
    >>> findAllTimeIntervallsSeries(s2PaarAus)
    []
    >>> findAllTimeIntervallsSeries(s2PaarEin)
    []
    >>> findAllTimeIntervallsSeries(s2PaarAusEin)
    []
    >>> findAllTimeIntervallsSeries(s2PaarEinAus)
    [(Timestamp('2021-03-19 01:02:02'), Timestamp('2021-03-19 01:02:05'))]
    >>> # 1 Wert
    >>> findAllTimeIntervallsSeries(s1WertWahr)
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:01'))]
    >>> findAllTimeIntervallsSeries(s1WertFalsch)
    []
    >>> ###
    >>> # 46  0 !1 Paar
    >>> # 0  46 !1 Paar
    >>> # 0   0 !1 Paar
    >>> # 46 46 !1 Paar
    >>> # 46  0  46  0 !2 Paare
    >>> # 46  0   0 46 !2 Paare
    >>> # 0  46   0 46 !2 Paare
    >>> # 0  46  46  0 !2 Paare
    >>> ###
    >>> findAllTimeIntervallsSeries(s1PaarGehtAus,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02'))]
    >>> findAllTimeIntervallsSeries(s1PaarGehtEin,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02'))]
    >>> findAllTimeIntervallsSeries(s1PaarEin,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02'))]
    >>> findAllTimeIntervallsSeries(s1PaarAus,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02'))]
    >>> findAllTimeIntervallsSeries(s2PaarAus,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02')), (Timestamp('2021-03-19 01:02:05'), Timestamp('2021-03-19 01:02:06'))]
    >>> findAllTimeIntervallsSeries(s2PaarEin,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02')), (Timestamp('2021-03-19 01:02:05'), Timestamp('2021-03-19 01:02:06'))]
    >>> findAllTimeIntervallsSeries(s2PaarAusEin,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02')), (Timestamp('2021-03-19 01:02:05'), Timestamp('2021-03-19 01:02:06'))]
    >>> findAllTimeIntervallsSeries(s2PaarEinAus,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02')), (Timestamp('2021-03-19 01:02:05'), Timestamp('2021-03-19 01:02:06'))]
    >>> # 1 Wert
    >>> findAllTimeIntervallsSeries(s1WertWahr,fct=None)
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:01'))]
    >>> findAllTimeIntervallsSeries(s1WertNone,fct=None)
    []
    >>> ###
    >>> d = {t1: 0, t3: 0} 
    >>> s1PaarmZ=pd.Series(data=d, index=[t1, t3])
    >>> findAllTimeIntervallsSeries(s1PaarmZ,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:03'))]
    >>> d = {t4: 0, t5: 0} 
    >>> s1PaaroZ=pd.Series(data=d, index=[t4, t5])
    >>> s2PaarmZoZ=pd.concat([s1PaarmZ,s1PaaroZ])
    >>> findAllTimeIntervallsSeries(s2PaarmZoZ,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:05'))]
    >>> ###
    >>> d = {t1: 0, t2: 0} 
    >>> s1PaaroZ=pd.Series(data=d, index=[t1, t2])
    >>> d = {t3: 0, t5: 0} 
    >>> s1PaarmZ=pd.Series(data=d, index=[t3, t5])
    >>> s2PaaroZmZ=pd.concat([s1PaaroZ,s1PaarmZ])
    >>> findAllTimeIntervallsSeries(s2PaaroZmZ,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:05'))]
    >>> ###
    >>> d = {t6: 0, t7: 0} 
    >>> s1PaaroZ2=pd.Series(data=d, index=[t6, t7])
    >>> d = {t4: 0} 
    >>> solitaer=pd.Series(data=d, index=[t4])
    >>> s5er=pd.concat([s1PaaroZ,solitaer,s1PaaroZ2])
    >>> findAllTimeIntervallsSeries(s5er,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:02')), (Timestamp('2021-03-19 01:02:04'), Timestamp('2021-03-19 01:02:07'))]
    >>> s3er=pd.concat([s1PaaroZ,solitaer])
    >>> findAllTimeIntervallsSeries(s3er,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:01'), Timestamp('2021-03-19 01:02:04'))]
    >>> s3er=pd.concat([solitaer,s1PaaroZ2])
    >>> findAllTimeIntervallsSeries(s3er,fct=None,tdAllowed=pd.Timedelta('1 second'))
    [(Timestamp('2021-03-19 01:02:04'), Timestamp('2021-03-19 01:02:07'))]
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    tPairs=[]

    try:

        if s.empty:            
            logger.debug("{:s}Series {!s:s} ist leer".format(logStr,s.name)) 

        elif s.size == 1:            
            logger.debug("{:s}Series {!s:s} hat nur 1 Element: {:s}".format(logStr,s.name,s.to_string()))       

           
           
            if fct != None:
                 # 1 Paar mit selben Zeiten wenn das 1 Element Wahr

                sValue=fct(s.iloc[0]) 
                if sValue:
                    tPair=(s.index[0],s.index[0])
                    tPairs.append(tPair)    
                else:
                    pass                
            else:
                # 1 Paar mit selben Zeiten wenn das 1 Element nicht None

                sValue=s.iloc[0]
                if sValue != None:               
                    tPair=(s.index[0],s.index[0])
                    tPairs.append(tPair) 
                else:
                    pass                
        else:
            tEin=None
        
            if fct != None:
                # paarweise über alle Zeiten
                for idx,((i1, s1), (i2, s2)) in enumerate(pairwise(s.iteritems())):    
                    s1Value=fct(s1)
                    s2Value=fct(s2)

                    # wenn 1 nicht x und 2       x tEin=t2 "geht Ein"
                    if not s1Value and s2Value:
                        tEin=i2
                        if idx > 0: # Info
                                pass
                        else:
                                # beim ersten Paar "geht Ein"
                                pass                               

                    # wenn 1       x und 2 nicht x tAus=t2 "geht Aus"
                    elif s1Value and not s2Value:
                        if tEin != None:
                            if tEin<i1:
                                # Paar speichern                                                
                                tPair=(tEin,i1)
                                tPairs.append(tPair)            
                            else:
                                # singulaeres Ereignis
                                # Paar mit selben Zeiten
                                tPair=(tEin,i1)
                                tPairs.append(tPair)  
                                pass                                
                        else: # geht Aus ohne Ein zu sein
                            if idx > 0: # Info
                                pass                             
                            else:
                                # im ersten Paar 
                                pass 
                           
                    # wenn 1       x und 2       x
                    elif s1Value and s2Value: 
                        if tEin != None:
                            pass
                        else:
                            # im ersten Wertepaar ist der Bereich Ein
                            tEin=i1
                

                # Behandlung letztes Paar

                # bleibt Ein am Ende der Series: Paar speichern
                if s1Value and s2Value: 
                    if tEin != None:
                        tPair=(tEin,i2)
                        tPairs.append(tPair)      

                # Behandlung tdAllowed
                if tdAllowed != None:   
                    if debugOutput:
                        logger.debug("{:s}Series {!s:s}: Intervalle werden mit {!s:s} zusammengefasst ...".format(logStr,s.name,tdAllowed))
                        tPairsOld=tPairs.copy()

                    tPairs=fCombineSubsequenttPairs(tPairs,tdAllowed,debugOutput=debugOutput)
                    
                    if debugOutput:
                        tPairsZusammengefasst=sorted(list(set(tPairsOld) - set(tPairs)))
                        if len(tPairsZusammengefasst)>0:
                            logger.debug("{:s}Series {!s:s}: Intervalle wurden wg. {!s:s} zusammengefasst. Nachfolgend die zusgefassten Intervalle: {!s:s}. Sowie die entsprechenden neuen: {!s:s}".format(
                                logStr
                               ,s.name
                               ,tdAllowed
                               ,tPairsZusammengefasst
                               ,sorted(list(set(tPairs) - set(tPairsOld)))
                               ))       

            else:            
                # paarweise über alle Zeiten
                # neues Paar beginnen
                anzInPair=1 # Anzahl der Zeiten in aktueller Zeitspanne
                for (i1, s1), (i2, s2) in pairwise(s.iteritems()):    
                    td=i2-i1
                    if td > tdAllowed: # Zeit zwischen 2 Zeiten  > als Schwelle: Zeitspanne ist abgeschlossen
                        if tEin==None:
                            # erstes Paar liegt bereits > als Schwelle auseinander
                            # Zeitspannenabschluss wird ignoriert, denn sonst Zeitspanne mit nur 1 Wert
                            # aktuelle Zeitspanne beginnt beim 1. Wert und geht über Schwellwert
                            tEin=i1
                            anzInPair=2
                        else:                    
                            if anzInPair>=2:
                                # Zeitspanne abschließen                            
                                tPair=(tEin,i1)
                                tPairs.append(tPair)      
                                # neue Zeitspanne beginnen
                                tEin=i2
                                anzInPair=1
                            else:
                                # Zeitspannenabschluss wird ignoriert, denn sonst Zeitspanne mit nur 1 Wert
                                anzInPair=2
                    else: # Zeitspanne zugelassen, weiter ...
                        if tEin==None:
                            tEin=i1
                        anzInPair=anzInPair+1
                    
                # letztes Zeitpaar behandeln

                if anzInPair>=2:
                    tPair=(tEin,i2)
                    tPairs.append(tPair)                                  
                else:                
                    # ein letzter Wert wuerde ueber bleiben, letzte Zeitspanne verlängern ... 
                    tPair=tPairs[-1]
                    tPair=(tPair[0],i2)
                    tPairs[-1]=tPair  
                
            

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return tPairs

def fCombineSubsequenttPairs(
 tPairs
,tdAllowed=pd.Timedelta('1 second') # all subsequent TimePairs with TimeDifference <= tdAllowed are combined to one TimePair
,debugOutput=False
):
# returns tPairs 

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:

        for idx,(tp1,tp2) in enumerate(pairwise(tPairs)):            
            
            t1Ende=tp1[1]
            t2Start=tp2[0]

            if t2Start-t1Ende <= tdAllowed:
                
                if debugOutput:
                    logger.debug("{:s} t1Ende: {!s:s} t2Start: {!s:s} Gap: {!s:s}".format(logStr,t1Ende,t2Start,t2Start-t1Ende)) 

                tPairs[idx]=(tp1[0],tp2[1]) # Folgepaar in vorheriges Paar integrieren
                tPairs.remove(tp2) # Folgepaar löschen
                tPairs=fCombineSubsequenttPairs(tPairs,tdAllowed) # Rekursion       

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return tPairs

class RmError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

alarmEvent = namedtuple('alarmEvent','tA,tE,ZHKNR,LDSResBaseType')

# --- Parameter und Funktionen LDS Reports
# ----------------------------------------

def pltMakeCategoricalColors(color,nOfSubColorsReq=3,reversedOrder=False):
    """
    Returns an array of rgb colors derived from color.

    Parameter:
        color:             a rgb color                       
        nOfSubColorsReq:   number of SubColors requested
        
    Raises:
        RmError

    >>> import matplotlib
    >>> color='red'
    >>> c=list(matplotlib.colors.to_rgb(color))
    >>> import Rm    
    >>> Rm.pltMakeCategoricalColors(c)
    array([[1.   , 0.   , 0.   ],
           [1.   , 0.375, 0.375],
           [1.   , 0.75 , 0.75 ]])
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    rgb=None

    try:             
        chsv = matplotlib.colors.rgb_to_hsv(color[:3])
        arhsv = np.tile(chsv,nOfSubColorsReq).reshape(nOfSubColorsReq,3)
        arhsv[:,1] = np.linspace(chsv[1],0.25,nOfSubColorsReq)
        arhsv[:,2] = np.linspace(chsv[2],1,nOfSubColorsReq)
        rgb = matplotlib.colors.hsv_to_rgb(arhsv)
        if reversedOrder:
            rgb=list(reversed(rgb))                                                                                                                    
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return rgb

# Farben fuer Druecke
SrcColorp='green'
SrcColorsp=pltMakeCategoricalColors(list(matplotlib.colors.to_rgb(SrcColorp)),nOfSubColorsReq=4,reversedOrder=False)
# erste Farbe ist Original-Farbe

SnkColorp='blue'
SnkColorsp=pltMakeCategoricalColors(list(matplotlib.colors.to_rgb(SnkColorp)),nOfSubColorsReq=4,reversedOrder=True)
# letzte Farbe ist Original-Farbe

# Farben fuer Fluesse
SrcColorQ='red'
SrcColorsQ=pltMakeCategoricalColors(list(matplotlib.colors.to_rgb(SrcColorQ)),nOfSubColorsReq=4,reversedOrder=False)
# erste Farbe ist Original-Farbe

SnkColorQ='orange'
SnkColorsQ=pltMakeCategoricalColors(list(matplotlib.colors.to_rgb(SnkColorQ)),nOfSubColorsReq=4,reversedOrder=True)
# letzte Farbe ist Original-Farbe

lwBig=4.5
lwSmall=2.5

attrsDct={   'p Src':{'color':SrcColorp,'lw':lwBig,'where':'post'}
            ,'p Snk':{'color':SnkColorp,'lw':lwSmall+1.,'where':'post'}
            ,'p Snk 2':{'color':'mediumorchid','where':'post'}
            ,'p Snk 3':{'color':'darkviolet','where':'post'}
            ,'p Snk 4':{'color':'plum','where':'post'}
                                             
            ,'Q Src':{'color':SrcColorQ,'lw':lwBig,'where':'post'}
            ,'Q Snk':{'color':SnkColorQ,'lw':lwSmall+1.,'where':'post'}
            ,'Q Snk 2':{'color':'indianred','where':'post'}
            ,'Q Snk 3':{'color':'coral','where':'post'}
            ,'Q Snk 4':{'color':'salmon','where':'post'}
            ,'Q Snk 5':{'color':'firebrick','where':'post'}
                    
            ,'Q Src RTTM':{'color':SrcColorQ,'lw':matplotlib.rcParams['lines.linewidth']+1.,'ls':'dotted','where':'post'}
            ,'Q Snk RTTM':{'color':SnkColorQ,'lw':matplotlib.rcParams['lines.linewidth']   ,'ls':'dotted','where':'post'}        
            ,'Q Snk 2 RTTM':{'color':'indianred','ls':'dotted','where':'post'}        
            ,'Q Snk 3 RTTM':{'color':'coral','ls':'dotted','where':'post'}       
            ,'Q Snk 4 RTTM':{'color':'salmon','ls':'dotted','where':'post'}    
            ,'Q Snk 5 RTTM':{'color':'firebrick','ls':'dotted','where':'post'}                
                    
            ,'p ISrc 1':{'color':SrcColorsp[-1],'ls':'dashdot','where':'post'}          
            ,'p ISrc 2':{'color':SrcColorsp[-2],'ls':'dashdot','where':'post'}     
            ,'p ISrc 3':{'color':SrcColorsp[-2],'ls':'dashdot','where':'post'}     # ab hier selbe Farbe
            ,'p ISrc 4':{'color':SrcColorsp[-2],'ls':'dashdot','where':'post'}     
            ,'p ISrc 5':{'color':SrcColorsp[-2],'ls':'dashdot','where':'post'}     
            ,'p ISrc 6':{'color':SrcColorsp[-2],'ls':'dashdot','where':'post'}     
          
            ,'p ISnk 1':{'color':SnkColorsp[0],'ls':'dashdot','where':'post'}          
            ,'p ISnk 2':{'color':SnkColorsp[1],'ls':'dashdot','where':'post'}        
            ,'p ISnk 3':{'color':SnkColorsp[1],'ls':'dashdot','where':'post'}     # ab hier selbe Farbe   
            ,'p ISnk 4':{'color':SnkColorsp[1],'ls':'dashdot','where':'post'}        
            ,'p ISnk 5':{'color':SnkColorsp[1],'ls':'dashdot','where':'post'}        
            ,'p ISnk 6':{'color':SnkColorsp[1],'ls':'dashdot','where':'post'}        
          
            ,'Q xSrc 1':{'color':SrcColorsQ[-1],'ls':'dashdot','where':'post'}          
            ,'Q xSrc 2':{'color':SrcColorsQ[-2],'ls':'dashdot','where':'post'}     
            ,'Q xSrc 3':{'color':SrcColorsQ[-3],'ls':'dashdot','where':'post'}     
          
            ,'Q xSnk 1':{'color':SnkColorsQ[0],'ls':'dashdot','where':'post'}          
            ,'Q xSnk 2':{'color':SnkColorsQ[1],'ls':'dashdot','where':'post'}        
            ,'Q xSnk 3':{'color':SnkColorsQ[2],'ls':'dashdot','where':'post'}           

            ,'Q (DE) Me':{'color': 'indigo','ls': 'dashdot','where': 'post','lw':1.5}
            ,'Q (DE) Re':{'color': 'cyan','ls': 'dashdot','where': 'post','lw':3.5}

            ,'p (DE) SS Me':{'color': 'magenta','ls': 'dashdot','where': 'post'}
            ,'p (DE) DS Me':{'color': 'darkviolet','ls': 'dashdot','where': 'post'}

            ,'p (DE) SS Re':{'color': 'magenta','ls': 'dotted','where': 'post'}
            ,'p (DE) DS Re':{'color': 'darkviolet','ls': 'dotted','where': 'post'}

            ,'p OPC LDSErgV':{'color':'olive'
                          ,'lw':lwSmall-.5
                          ,'ms':matplotlib.rcParams['lines.markersize']
                          ,'marker':'x'
                          ,'mec':'olive'
                          ,'mfc':'olive'
                          ,'where':'post'}   

            ,'p OPC Src':{'color':SrcColorp
                       ,'lw':0.05+2
                       ,'ms':matplotlib.rcParams['lines.markersize']/2
                       ,'marker':'D'
                       ,'mec':SrcColorp
                       ,'mfc':SrcColorQ
                       ,'where':'post'}    

            ,'p OPC Snk':{'color':SnkColorp
                       ,'lw':0.05+2
                       ,'ms':matplotlib.rcParams['lines.markersize']/2
                       ,'marker':'D'
                       ,'mec':SnkColorp
                       ,'mfc':SnkColorQ
                       ,'where':'post'}   


            ,'Q OPC Src':{'color':SrcColorQ
                       ,'lw':0.05+2
                       ,'ms':matplotlib.rcParams['lines.markersize']/2
                       ,'marker':'D'
                       ,'mec':SrcColorQ
                       ,'mfc':SrcColorp
                       ,'where':'post'}            

            ,'Q OPC Snk':{'color':SnkColorQ
                       ,'lw':0.05+2
                       ,'ms':matplotlib.rcParams['lines.markersize']/2
                       ,'marker':'D'
                       ,'mec':SnkColorQ
                       ,'mfc':SnkColorp
                       ,'where':'post'}    

          }

attrsDctLDS={
     'Seg_AL_S_Attrs':{'color':'blue','lw':3.,'where':'post'}
    ,'Druck_AL_S_Attrs':{'color':'blue','lw':3.,'ls':'dashed','where':'post'}
    
    #R1
    ,'Seg_MZ_AV_Attrs':{'color':'orange','zorder':1,'lw':2.50,'where':'post'}    
    ,'Druck_MZ_AV_Attrs':{'color':'orange','zorder':1,'lw':2.50,'ls':'dashed','where':'post'}    
    
    #R2
    ,'Seg_LR_AV_Attrs':{'color':'green','zorder':3,'where':'post'}
    ,'Druck_LR_AV_Attrs':{'color':'green','zorder':3,'ls':'dashed','where':'post'}
    
    ,'Seg_LP_AV_Attrs':{'color':'turquoise','zorder':2,'lw':1.0,'where':'post'}
    ,'Druck_LP_AV_Attrs':{'color':'turquoise','zorder':2,'lw':1.0,'ls':'dashed','where':'post'}
    
    ,'Seg_NG_AV_Attrs':{'color':'red','zorder':2,'where':'post'}
    ,'Druck_NG_AV_Attrs':{'color':'red','zorder':2,'ls':'dashed','where':'post'}
    
    ,'Seg_SB_S_Attrs':{'color':'black','alpha':.5,'where':'post'}
    ,'Druck_SB_S_Attrs':{'color':'black','ls':'dashed','alpha':.75,'where':'post','lw':1.0}    
    
    ,'Seg_AC_AV_Attrs':{'color':'indigo','where':'post'}
    ,'Druck_AC_AV_Attrs':{'color':'indigo','ls':'dashed','where':'post'}       

    ,'Seg_ACF_AV_Attrs':{'color':'blueviolet','where':'post','lw':1.0}
    ,'Druck_ACF_AV_Attrs':{'color':'blueviolet','ls':'dashed','where':'post','lw':1.0}       

    ,'Seg_ACC_Limits_Attrs':{'color':'indigo','ls':linestyle_tuple[2][1]} # 'densely dotted'
    ,'Druck_ACC_Limits_Attrs':{'color':'indigo','ls':linestyle_tuple[8][1]} # 'densely dashdotted'

    ,'Seg_TIMER_AV_Attrs':{'color':'chartreuse','where':'post'}
    ,'Druck_TIMER_AV_Attrs':{'color':'chartreuse','ls':'dashed','where':'post'}      

    ,'Seg_AM_AV_Attrs':{'color':'chocolate','where':'post'}
    ,'Druck_AM_AV_Attrs':{'color':'chocolate','ls':'dashed','where':'post'}      
    #
    ,'Seg_DPDT_REF_Attrs':{'color':'violet','ls':linestyle_tuple[2][1]} # 'densely dotted'
    ,'Druck_DPDT_REF_Attrs':{'color':'violet','ls':linestyle_tuple[8][1]} # 'densely dashdotted'

    ,'Seg_DPDT_AV_Attrs':{'color':'orchid'
                          ,'where':'post'
                          ,'lw':1.5}
    ,'Druck_DPDT_AV_Attrs':{'color':'orchid','ls':'dashed'
                            ,'where':'post'
                            ,'lw':1.5}       

    ,'Seg_DP2DT2_AV_Attrs':{'color':'plum'
                          ,'where':'post'
                          ,'lw':0.5}
    ,'Druck_DP2DT2_AV_Attrs':{'color':'plum','ls':'dashed'
                            ,'where':'post'
                            ,'lw':0.5}   

    ,'Seg_QM_AV_Attrs':{'color':'sandybrown','ls':linestyle_tuple[6][1],'where':'post','lw':1.0}        # 'loosely dashdotted'
    ,'Druck_QM_AV_Attrs':{'color':'sandybrown','ls':linestyle_tuple[10][1],'where':'post','lw':1.0}     # 'loosely dashdotdotted'

    }

pSIDEvents=re.compile('(?P<Prae>IMDI\.)?Objects\.(?P<colRegExMiddle>3S_FBG_ESCHIEBER|FBG_ESCHIEBER{1})\.(3S_)?(?P<colRegExSchieberID>[a-z,A-Z,0-9,_]+)\.(?P<colRegExEventID>(In\.ZUST|In\.LAEUFT|In\.LAEUFT_NICHT|In\.STOER|Out\.AUF|Out\.HALT|Out\.ZU)$)')
# ausgewertet werden: colRegExSchieberID (um welchen Schieber geht es), colRegExMiddle (Befehl oder Zustand) und colRegExEventID (welcher Befehl bzw. Zustand) 
# die Befehle bzw. Zustaende (die Auspraegungen von colRegExEventID) muessen nachf. def. sein um den Marker (des Befehls bzw. des Zustandes) zu definieren

eventCCmds={ 'Out.AUF':0
                 ,'Out.ZU':1
                 ,'Out.HALT':2}
eventCStats={'In.LAEUFT':3
                 ,'In.LAEUFT_NICHT':4
                 ,'In.ZUST':5
                 ,'Out.AUF':6
                 ,'Out.ZU':7
                 ,'Out.HALT':8            
                 ,'In.STOER':9}

valRegExMiddleCmds='3S_FBG_ESCHIEBER' # colRegExMiddle-Auspraegung fuer Befehle (==> eventCCmds)

LDSParameter=[
        'ACC_SLOWTRANSIENT'
        ,'ACC_TRANSIENT'
        ,'DESIGNFLOW'
        ,'DT'
        ,'FILTERWINDOW'

        #,'L_PERCENT'   
        ,'L_PERCENT_STDY'
        ,'L_PERCENT_STRAN'
        ,'L_PERCENT_TRANS'
        
        ,'L_SHUTOFF'
        ,'L_SLOWTRANSIENT'
        ,'L_SLOWTRANSIENTQP'
        ,'L_STANDSTILL'
        ,'L_STANDSTILLQP'
        ,'L_TRANSIENT'
        ,'L_TRANSIENTQP'
        ,'L_TRANSIENTVBIGF'
        ,'L_TRANSIENTPDNTF'
        ,'MEAN'
        ,'NAME'
        ,'ORDER'
        ,'TIMER'
        ,'TTIMERTOALARM'
        ,'TIMERTOLISS'
        ,'TIMERTOLIST'
        
        ]

LDSParameterDataD={
         'ACC_SLOWTRANSIENT':0.1
        ,'ACC_TRANSIENT':0.8
        ,'DESIGNFLOW':250.
        ,'DT':1
        ,'FILTERWINDOW':180

        #,'L_PERCENT':1.6
        ,'L_PERCENT_STDY':1.6
        ,'L_PERCENT_STRAN':1.6
        ,'L_PERCENT_TRANS':1.6

        ,'L_SHUTOFF':2.
        ,'L_SLOWTRANSIENT':4.
        ,'L_SLOWTRANSIENTQP':4.
        ,'L_STANDSTILL':2.
        ,'L_STANDSTILLQP':2.
        ,'L_TRANSIENT':10.
        ,'L_TRANSIENTQP':10.
        ,'L_TRANSIENTVBIGF':3.
        ,'L_TRANSIENTPDNTF':1.5
        ,'MEAN':1
       
        ,'ORDER':1
        ,'TIMER':180
        ,'TTIMERTOALARM':45 # TIMER/4
        ,'TIMERTOLISS':180
        ,'TIMERTOLIST':180

        ,'NAME':''
        }

def getNamesFromSEGResIDBase(dfSegsNodesNDataDpkt
                            ,SEGResIDBase):
    """
    Returns tuple (DIVPipelineName,SEGName) from SEGResIDBase
    """    
    df=dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['SEGResIDBase']==SEGResIDBase]
    if not df.empty:
        return (df['DIVPipelineName'].iloc[0],df['SEGName'].iloc[0])

def getNamesFromDruckResIDBase(dfSegsNodesNDataDpkt
                            ,DruckResIDBase):
    """
    Returns tuple (DIVPipelineName,SEGName,SEGResIDBase,SEGOnlyInLDSPara) from DruckResIDBase
    """    
    df=dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['DruckResIDBase']==DruckResIDBase]
    if not df.empty:
        #return (df['DIVPipelineName'].iloc[0],df['SEGName'].iloc[0],df['SEGResIDBase'].iloc[0])
        tupleLst=[]
        for index,row in df.iterrows():
            tupleItem=(row['DIVPipelineName'],row['SEGName'],row['SEGResIDBase'],row['SEGOnlyInLDSPara'])
            tupleLst.append(tupleItem)    
        return tupleLst
    else:
        return []


def fGetErgIDsFromBaseID(
    baseID='Objects.3S_FBG_SEG_INFO.3S_L_6_BUV_01_BUA.In.'
   ,dfODI=pd.DataFrame() # df mit ODI Parametrierungsdaten
   ,strSep=' '
   ,patternPat='^IMDI.' # 
   ,pattern=True # nur ergIDs, fuer die 2ndPatternPat zutrifft liefern
):
    """
    returns string 
    mit strSep getrennten IDs aus dfODI, welche baseID enthalten (und bei pattern WAHR patternPat matchen)
    baseID (und group(0) von patternPat bei pattern WAHR) sind in den IDs entfernt
    """

    if baseID in [None,'']:
        return None
    
    df=dfODI[dfODI.index.str.contains(baseID)]
    
    if df.empty:
        return None

    if pattern:
        ergIDs=''.join([e.replace(baseID,'').replace(re.search(patternPat,e).group(0),'')+' ' for e in df.index if re.search(patternPat,e) !=  None])    
    else:
        ergIDs=''.join([e.replace(baseID,'')+' ' for e in df.index if re.search(patternPat,e) ==  None])   
    
    return ergIDs


def dfSegsNodesNDataDpkt(
     VersionsDir=r"C:\3s\Projekte\Projekt\04 - Versionen\Version82.3"
    ,Model=r"MDBDOC\FBG.mdb" #  relativ zu VersionsDir; unverwendet, wenn am angegeben ist
    ,am=None # a Access Model already processed

    ,SEGsDefPattern='(?P<SEG_Ki>\S+)~(?P<SEG_Kk>\S+)$' # RSLW-Beschreibung: liefert die Knotennamen der Segmentdefinition
    ,RIDefPattern='(?P<Prae>\S+)\.(?P<Post>RICHT.S)$' # SWVT-Beschreibung (RICHT-DP)
    ,LODefPattern='(?P<Prae>\S+)\.(?P<Post>LO)$'  # SWVT-Beschreibung (LO-DP)
    ,SIDefPattern='(?P<Prae>\S+)\.(?P<Post>SIMSTAT)$'  # SWVT-Beschreibung (SIMSTAT-DP)

    ,fSEGNameFromPV_RICHT=lambda x: x # Funktion, die von PV-Name SEGName liefert
    ,fSEGNameFromPV_LO_SIMSTAT=lambda x: x # Funktion, die von PV-Name SEGName liefert
    ,fDIVNameFromSEGName=lambda x: x # Funktion, die DIVName von SEGName liefert

    ,fGetBaseIDFromResID=lambda x: x # Funktion, die von OPCITEM-ID des PH-Kanals eines KNOTens den Wortstamm der Knotenergebnisse liefert
    ,fGetSEGBaseIDFromSEGName=lambda x: x # Funktion, die aus SEGName den Wortstamm der Segmentergebnisse liefert
    ,fCheckFT_NODEsName=lambda x: x # Funktion, die den zu einer Flussmessung gehoerenden Druckmessknoten prueft; x ist der topologisch ermittelte Knoten

    # optional; wenn die Dateien vorhanden sind, werden die Daten als Spalten eingepflegt
    ,LDSPara=r"App LDS\Modelle\WDFBG\B1\V0\BZ1\LDS_Para.xml" #  relativ zu VersionsDir
    ,LDSParaPT=r"App LDS\SirOPC\AppLDS_DPDTParams.csv" #  relativ zu VersionsDir
    ,ODI=r"App LDS\SirOPC\AppLDS_ODI.csv" #  relativ zu VersionsDir
    # wird fuer Check der LDSPara-Daten benoetigt
    ,LDSParameter=LDSParameter
    ,LDSParameterDataD=LDSParameterDataD
    
    ):
    """
    alle Segmente (mit Segmantdaten) und mit Pfaddaten (Kantenzuege) mit Kanten- und Knotendaten sowie Parametrierungsdaten
    
    returns df:

        DIVPipelineName
        SEGName
        SEGNr
        ... siehe Ende der Funktion
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfSegsNodesNDataDpkt=pd.DataFrame()

    try:      
        
        ###### --- LDSPara
        
        LDSParaFile=os.path.join(VersionsDir,LDSPara)

        if os.path.exists(LDSParaFile):
            
            logger.info("{:s}###### {:10s}: {:s}: Lesen und prüfen ...".format(logStr,'LDSPara',LDSPara))

            with open(LDSParaFile) as f:
                xml = f.read()
                xmlWellFormed='<root>'+xml+'</root>'
            root=ET.fromstring(xmlWellFormed)

            LDSParameterData={}
            for key in LDSParameterDataD.keys():
                LDSParameterData[key]=[]

            logger.debug("{:s}LDSParameter: {!s:s}.".format(logStr,LDSParameter))

            for idx,element in enumerate(root.iter(tag='LDSI')):
    
                attribKeysMute=[]
                for key,value in element.attrib.items():
                    if key not in LDSParameter:
                        logger.warning("{:s}{:s}: Parameter: {:s} undefiniert.".format(logStr,element.attrib['NAME'],key))

                        attribKeysMute.append(key)
            
                keysIst=element.attrib.keys()
                keysSoll=set(LDSParameter)    
                keysExplizitFehlend=keysSoll-keysIst        
    
                LDSIParaDct=element.attrib    
                for key in keysExplizitFehlend:  
                    if key=='ORDER':
                        LDSIParaDct[key]=LDSParameterDataD[key]
                        logger.debug("{:s}{:25s}: explizit fehlender Parameter: {:20s} ({!s:s}).".format(logStr,element.attrib['NAME'],key,LDSIParaDct[key]))
                    elif key=='TTIMERTOALARM':
                        LDSIParaDct[key]=int(LDSIParaDct['TIMER'])/4
                        logger.debug("{:s}{:25s}: explizit fehlender Parameter: {:20s} ({!s:s}).".format(logStr,element.attrib['NAME'],key,LDSIParaDct[key]))
                    else:                                            
                        LDSIParaDct[key]=LDSParameterDataD[key]
                        logger.debug("{:s}{:25s}: explizit fehlender Parameter: {:20s} ({!s:s}).".format(logStr,element.attrib['NAME'],key,LDSIParaDct[key]))

                keyListToProcess=[key for key in LDSIParaDct.keys() if key not in attribKeysMute]
                for key in keyListToProcess:        
                    LDSParameterData[key].append(LDSIParaDct[key])

            df=pd.DataFrame.from_dict(LDSParameterData)
            df=df.set_index('NAME').sort_index()
            df.index.rename('SEGMENT', inplace=True)
            df=df[sorted(df.columns.to_list())]
            df = df.apply(pd.to_numeric)       
            #logger.debug("{:s}df: {:s}".format(logStr,df.to_string()))      

            logger.debug("{:s}Parameter, die nicht auf Standardwerten sind:".format(logStr))
            for index, row in df.iterrows():    
                for colName, colValue in zip(df.columns.to_list(),row):
                    if colValue != LDSParameterDataD[colName]:
                        logger.debug("Segment: {:30s}: Parameter: {:20s} Wert: {:10s} (Standard: {:s})".format(index,colName,str(colValue),str(LDSParameterDataD[colName])))

            dfPara=df
        else:
            logger.debug("{:s}###### {:10s}: {:s}: Datei existiert nicht".format(logStr,'LDSPara',LDSPara))

        # --- Einlesen Modell    
        if am == None:
            accFile=os.path.join(VersionsDir,Model)        
            logger.info("{:s}###### {:10s}: {:s}: Lesen und verarbeiten ...".format(logStr,'Modell',Model))
            am=Am.Am(accFile=accFile)

        V_BVZ_RSLW=am.dataFrames['V_BVZ_RSLW']
        V_BVZ_SWVT=am.dataFrames['V_BVZ_SWVT']
        V3_KNOT=am.dataFrames['V3_KNOT']
        V3_VBEL=am.dataFrames['V3_VBEL']
        V3_DPKT=am.dataFrames['V3_DPKT']
        
        V3_RSLW_SWVT=am.dataFrames['V3_RSLW_SWVT']

        # --- Segmente ermitteln        

        # --- per Modell
        SEGsDefinesPerRICHT=V3_RSLW_SWVT[
        (V3_RSLW_SWVT['BESCHREIBUNG'].str.match(SEGsDefPattern).isin([True])) # Muster Ki~Kk ...
        & #!
        (V3_RSLW_SWVT['BESCHREIBUNG_SWVT'].str.match(RIDefPattern).isin([True])) # Muster Förderrichtungs-PV ...
        ].copy(deep=True)
        SEGsDefinesPerRICHT=SEGsDefinesPerRICHT[['BESCHREIBUNG','BESCHREIBUNG_SWVT']]

        if os.path.exists(LDSParaFile):
            # --- nur per LDS Para?!
            lSEGOnlyInLDSPara=[str(SEGNodes) for SEGNodes in dfPara.index if str(SEGNodes) not in SEGsDefinesPerRICHT['BESCHREIBUNG'].values]
            for SEGNodes in lSEGOnlyInLDSPara:
                logger.info("{:s}LDSPara SEG {:s} ist nicht Modell-definiert!".format(logStr,SEGNodes)) 

            # --- zusammenfassen
            SEGsDefines=pd.concat([SEGsDefinesPerRICHT,pd.DataFrame(lSEGOnlyInLDSPara,columns=['BESCHREIBUNG'])])
        else:
            SEGsDefines=pd.concat([SEGsDefinesPerRICHT])

        # Knotennamen der SEGDef ergänzen        
        df=SEGsDefines['BESCHREIBUNG'].str.extract(SEGsDefPattern,expand=True)
        dfCols=df.columns.to_list()
        SEGsDefines=pd.concat([SEGsDefines,df],axis=1)
        # ausduennen
        SEGsDefines=SEGsDefines[dfCols+['BESCHREIBUNG_SWVT','BESCHREIBUNG']]
        # sortieren
        SEGsDefines=SEGsDefines.sort_values(by=['BESCHREIBUNG_SWVT','BESCHREIBUNG']).reset_index(drop=True)
        # SEGName
        SEGsDefines['BESCHREIBUNG_SWVT']=SEGsDefines.apply(lambda row: row['BESCHREIBUNG_SWVT'] if not pd.isnull(row['BESCHREIBUNG_SWVT']) else row['BESCHREIBUNG']+' (undef.)' ,axis=1)
        #print(SEGsDefines)
        SEGsDefines['SEGName']=SEGsDefines['BESCHREIBUNG_SWVT'].apply(lambda x: fSEGNameFromPV_RICHT(x))
        
        # --- Segmentkantenzuege ermitteln
        dfSegsNodeLst={} # nur zu Kontrollzwecken
        dfSegsNode=[]
        for index,row in SEGsDefines[~SEGsDefines[dfCols[-1]].isnull()].iterrows():        
            df=Xm.Xm.constructShortestPathFromNodeList(df=V3_VBEL.reset_index()
                                                    ,sourceCol='NAME_i'
                                                    ,targetCol='NAME_k'
                                                    ,nl=[row[dfCols[0]],row[dfCols[-1]]]
                                                    ,weight=None,query=None,fmask=None,filterNonQ0Rows=True)    
    
            s=pd.concat([pd.Series([row[dfCols[0]]]),df['nextNODE']])
            s.name=row['SEGName']
    
            dfSegsNodeLst[row['SEGName']]=s.reset_index(drop=True)
    
            df2=pd.DataFrame(s.reset_index(drop=True)).rename(columns={s.name:'NODEs'})
            df2['SEGName']=s.name
            df2=df2[['SEGName','NODEs']]
    
            sObj=pd.concat([pd.Series(['None']),df['OBJTYPE']])
            sObj.name='OBJTYPE'    
    
            df3=pd.concat([df2,pd.DataFrame(sObj.reset_index(drop=True))],axis=1)

            sObjID=pd.concat([pd.Series(['None']),df['OBJID']])
            sObjID.name='OBJID'   
            df3b=pd.concat([df3,pd.DataFrame(sObjID.reset_index(drop=True))],axis=1)
    
            df4=df3b.reset_index().rename(columns={'index':'NODEsLfdNr','NODEs':'NODEsName'})[['SEGName','NODEsLfdNr','NODEsName','OBJTYPE'
                                                                                               ,'OBJID'
                                                                                               ]]
            df4['NODEsType']=df4.apply(lambda row: row['NODEsLfdNr'] if row['NODEsLfdNr'] < df4.index[-1] else -1, axis=1)
            df4=df4[['SEGName','NODEsLfdNr','NODEsType','NODEsName','OBJTYPE'
                     ,'OBJID'
                     ]]
            df4['SEGNodes']=row[dfCols[0]]+'~'+row[dfCols[-1]]
    
            dfSegsNode.append(df4)        
        dfSegsNodes=pd.concat(dfSegsNode).reset_index(drop=True)

        # ---
        if os.path.exists(LDSParaFile):
            dfSegsNodes['SEGOnlyInLDSPara']=dfSegsNodes.apply(lambda row: True if row['SEGNodes'] in lSEGOnlyInLDSPara else False,axis=1)
        else:           
            dfSegsNodes['SEGOnlyInLDSPara']=False

        dfSegsNodes['NODEsRef']=dfSegsNodes.sort_values(
            by=['NODEsName','SEGOnlyInLDSPara','NODEsType','SEGName']
            ,ascending=[True,True,False,True]).groupby(['NODEsName']).cumcount() + 1
        dfSegsNodes=pd.merge(dfSegsNodes,dfSegsNodes.groupby(['NODEsName']).max(),left_on='NODEsName',right_index=True,suffixes=('','_max'))
        dfSegsNodes=dfSegsNodes[['SEGName','SEGNodes','SEGOnlyInLDSPara'
                                 ,'NODEsRef'
                                 ,'NODEsRef_max'
                                 ,'NODEsLfdNr','NODEsType','NODEsName','OBJTYPE'
                                 ,'OBJID'
                                 ]]
        dfSegsNodes=dfSegsNodes.rename(columns={'NODEsLfdNr':'NODEsSEGLfdNr','NODEsType':'NODEsSEGLfdNrType'})

        dfSegsNodes=dfSegsNodes[['SEGName','SEGNodes','SEGOnlyInLDSPara'
                                 ,'NODEsRef'
                                 ,'NODEsRef_max'
                                 ,'NODEsSEGLfdNr','NODEsSEGLfdNrType','NODEsName','OBJTYPE'
                                 ,'OBJID'
                                 ]]


        dfSegsNodes=dfSegsNodes.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodes vor 3 PVs', dfSegsNodes.to_string()))

        # Förderrichtungs-PV
        dfSegsNodes=pd.merge(dfSegsNodes,SEGsDefines,left_on='SEGName',right_on='SEGName',how='left').filter(items=dfSegsNodes.columns.to_list()+['BESCHREIBUNG_SWVT'])
        dfSegsNodes=dfSegsNodes.rename(columns={'BESCHREIBUNG_SWVT':'Förderrichtungs-PV'})

        # Leckort-PV
        SEGsDefinesPerLO=V3_RSLW_SWVT[V3_RSLW_SWVT['BESCHREIBUNG_SWVT'].str.match(LODefPattern).isin([True])].copy(deep=True)
        # eff. zu behaltene Spalten 
        SEGsDefinesPerLO=SEGsDefinesPerLO[['BESCHREIBUNG_SWVT','NAME_CONT']].copy(deep=True) 
        SEGsDefinesPerLO.rename(columns={'BESCHREIBUNG_SWVT':'Leckort-PV','NAME_CONT':'RSLW_LO_CONT'},inplace=True)
        SEGsDefinesPerLO['SEGName']=\
        SEGsDefinesPerLO['Leckort-PV'].apply(lambda x: fSEGNameFromPV_LO_SIMSTAT(x))
        dfSegsNodes=pd.merge(dfSegsNodes,SEGsDefinesPerLO,left_on='SEGName',right_on='SEGName',how='left').filter(items=dfSegsNodes.columns.to_list()+['Leckort-PV'])
        dfSegsNodes=dfSegsNodes.rename(columns={'BESCHREIBUNG_SWVT':'Leckort-PV'})

        # Simstat-PV
        SEGsDefinesPerSI=V3_RSLW_SWVT[V3_RSLW_SWVT['BESCHREIBUNG_SWVT'].str.match(SIDefPattern).isin([True])].copy(deep=True)
        # eff. zu behaltene Spalten 
        SEGsDefinesPerSI=SEGsDefinesPerSI[['BESCHREIBUNG_SWVT','NAME_CONT','KA']].copy(deep=True) 
        SEGsDefinesPerSI.rename(columns={'BESCHREIBUNG_SWVT':'Simstat-PV','NAME_CONT':'RSLW_SI_CONT'},inplace=True)
        SEGsDefinesPerSI['SEGName']=\
        SEGsDefinesPerSI['Simstat-PV'].apply(lambda x:  fSEGNameFromPV_LO_SIMSTAT(x))
        dfSegsNodes=pd.merge(dfSegsNodes,SEGsDefinesPerSI,left_on='SEGName',right_on='SEGName',how='left').filter(items=dfSegsNodes.columns.to_list()+['Simstat-PV'])

        # dieselbe RI-, LO-, SIM-PV kann fuer mehrere Segmente definiert sein; daher hier evtl. Duplikate entfernen
        dfSegsNodes.drop_duplicates(keep='first', inplace=True)        
        dfSegsNodes=dfSegsNodes.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodes nach 3 PVs', dfSegsNodes.to_string()))
        
        # --- Knotendaten ergaenzen
        dfSegsNodesNData=pd.merge(dfSegsNodes,V3_KNOT, left_on='NODEsName',right_on='NAME',suffixes=('','KNOT'))
        dfSegsNodesNData=dfSegsNodesNData.filter(items=dfSegsNodes.columns.to_list()+['ZKOR','NAME_CONT','pk'])
        dfSegsNodesNData=dfSegsNodesNData.rename(columns={'NAME_CONT':'Blockname'})

        # --- Knotendatenpunktdaten ergänzen
        V3_DPKT_KNOT=pd.merge(V3_DPKT,V3_KNOT,left_on='fkOBJTYPE',right_on='pk',suffixes=('','_KNOT'))
        V3_DPKT_KNOT_PH=V3_DPKT_KNOT[V3_DPKT_KNOT['ATTRTYPE'].isin(['PH'])]
        
        df=pd.merge(dfSegsNodesNData,V3_DPKT_KNOT_PH,left_on='pk',right_on='fkOBJTYPE',suffixes=('','_DPKT'),how='left')
        cols=dfSegsNodesNData.columns.to_list()
        #cols.remove('pk')
        df=df.filter(items=cols+[
                                 #'ATTRTYPE',
                                 'CLIENT_ID','OPCITEM_ID','NAME'
                                 ,'DESCRIPTION'
                                 ])
        df.rename(columns={'pk':'NODEsOBJID','DESCRIPTION':'BESCHREIBUNG'},inplace=True)
        dfSegsNodesNDataDpkt=df
       
        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodesNDataDpkt nach Knotendatenpunktdaten ergänzen',dfSegsNodesNDataDpkt.to_string()))

        # --- VBELdatenpunktdaten VENT QM ergänzen
        V3_DPKT_QM=V3_DPKT[V3_DPKT['ATTRTYPE'].isin(['QM']) & V3_DPKT['OBJTYPE'].isin(['VENT'])]
        df=pd.merge(dfSegsNodesNDataDpkt,V3_DPKT_QM,left_on='OBJID',right_on='fkOBJTYPE',how='left',suffixes=('','_QM'))
        DPKT_FT_Cols=['CLIENT_ID_QM','OPCITEM_ID_QM','NAME_QM','DESCRIPTION']

        dfSegsNodesNDataDpkt=df.filter(dfSegsNodesNDataDpkt.columns.to_list()                
                +DPKT_FT_Cols
                )
        dfSegsNodesNDataDpkt.rename(columns={'DESCRIPTION':'BESCHREIBUNG_QM'},inplace=True)

        DPKT_FT_Cols=['CLIENT_ID_QM','OPCITEM_ID_QM','NAME_QM','BESCHREIBUNG_QM']

        # --- VBELdatenpunktdaten ROHR LINEPACKRATE ergänzen
        V3_DPKT_LP=V3_DPKT[V3_DPKT['ATTRTYPE'].isin(['LINEPACKRATE']) & V3_DPKT['OBJTYPE'].isin(['ROHR'])]
        df=pd.merge(dfSegsNodesNDataDpkt,V3_DPKT_LP,left_on='OBJID',right_on='fkOBJTYPE',how='left',suffixes=('','_LP'))
        DPKT_LP_Cols=['CLIENT_ID_LP','OPCITEM_ID_LP','NAME_LP','DESCRIPTION']
        dfSegsNodesNDataDpkt=df.filter(dfSegsNodesNDataDpkt.columns.to_list()                
                        +DPKT_LP_Cols
                        )
        dfSegsNodesNDataDpkt.rename(columns={'DESCRIPTION':'BESCHREIBUNG_LP'},inplace=True)
        DPKT_LP_Cols=['CLIENT_ID_LP','OPCITEM_ID_LP','NAME_LP','BESCHREIBUNG_LP']

        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodesNDataDpkt nach VBELdatenpunktdaten ergänzen',dfSegsNodesNDataDpkt.to_string()))


        # --- FT und PT: Messstellen klassifizieren
        # Avise der nachfolgend eränzten Spalten 
        XT_Cols=[ 'NODEsNamePrev' # Name des vorherigen Knotens (Hilfreich fuer die Generierung von ODI-VBEL-Zeilen aus einer row)
         ,'FT_ind'        # Indikator für Flussmessstellen
         ,'FT_NODEsName'  # Names des Knotens der fuer diese Flussmessstelle der Randknoten ist        
         ,'FT_NODEsPT'    # Druckmessstellen-PV welche für diese Flussmessstelle Druckmesswerte liefert 
         ,'PT_ind'        # Indikator für Druckmessstellen
        ##  ,'PT_NODEsFT'  # FlussmessstellenPV des Randknotennamens        
        ]
        dfSegsNodesNDataDpkt['NODEsNamePrev']=dfSegsNodesNDataDpkt['NODEsName'].shift(1)
        dfSegsNodesNDataDpkt['NODEsNamePrev']\
        =dfSegsNodesNDataDpkt.apply(lambda row: row['NODEsNamePrev'] if row['NODEsSEGLfdNrType']!= 0 else None,axis=1)
        #dfSegsNodesNDataDpkt['CLIENT_IDPrev']=dfSegsNodesNDataDpkt['CLIENT_ID'].shift(1)

        dfSegsNodesNDataDpkt['FT_ind']=~dfSegsNodesNDataDpkt['CLIENT_ID_QM'].str.strip().isin(['',None,pd.np.nan])

        # FT_ind:
        # True: Flussmessstelle
        # False: keine Flussmessstelle

        # 0: Fehler
        # 'Src': am Anfang der SEGDef (d.h. NODEsName ist pBC)
        # 'Snk': am Ende der SEGDef (d.h. NODEsNamePrev ist pBC)
        # None: keine Flussmessstelle

        def fGetFT_indFromRow(row):
    
            if row['FT_ind']:
                if row['NODEsSEGLfdNrType']==1:
                    # am Anfang der SEGDef (d.h. NODEsName ist pBC)
                    return 'Src' #1
                elif row['NODEsSEGLfdNrType']==-1:
                    # am Ende der SEGDef (d.h. NODEsNamePrev ist pBC)
                    return 'Snk' #-1
                else:
                    return 0 # Fehler
            else:
                return None
        dfSegsNodesNDataDpkt['FT_ind']=dfSegsNodesNDataDpkt.apply(lambda row: fGetFT_indFromRow(row),axis=1)
        # FT_NODEsName:
        # Names des Knotens der fuer diese Flussmessstelle topologisch der Randknoten ist
        # None: keine Flussmessstelle

        def fGetFT_NODEsNameFromRow(row):
    
            if row['FT_ind']=='Src': #1:
                return row['NODEsName']
            elif row['FT_ind']=='Snk': #-1:
                return row['NODEsNamePrev']    
            else:
                return None
        dfSegsNodesNDataDpkt['FT_NODEsName']=dfSegsNodesNDataDpkt.apply(lambda row: fGetFT_NODEsNameFromRow(row),axis=1)
        dfSegsNodesNDataDpkt['FT_NODEsNameTopo']=dfSegsNodesNDataDpkt['FT_NODEsName']
        dfSegsNodesNDataDpkt['FT_NODEsName']=dfSegsNodesNDataDpkt.apply(lambda row: fCheckFT_NODEsName(row['FT_NODEsName']),axis=1)

        # FT_NODEsPT:
        # Druckmess-PV der Flussmessstelle
        def fGetFT_NODEsPTFromRow(row):       
            FT_NODEsPT=None
            try:
                s=dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['NODEsName']==row['FT_NODEsName']].iloc[0]
                FT_NODEsPT=s.CLIENT_ID
            except:
                pass
            finally:
                return FT_NODEsPT
        dfSegsNodesNDataDpkt['FT_NODEsPT']=dfSegsNodesNDataDpkt.apply(lambda row: fGetFT_NODEsPTFromRow(row),axis=1)

        # PT_ind:
        # 'Src': Knoten ist topologischer Quellrandknoten eines Flow-Meters (kk des Meters)
        # 'Snk': Knoten ist topologischer Senkrandknoten eines Flow-Meters (ki des Meters)        
        # Nr.:   NODEsType: 0 beim Anfangsknoten der SEGDef; -1 beim Endknoten der SEGDef
        dfSegsNodesNDataDpkt['FT_indSm1']=dfSegsNodesNDataDpkt['FT_ind'].shift(-1)
        def fGetPT_indFromRow(row):                   
            if row['FT_ind']=='Src': #1:
                    # am Anfang der SEGDef (d.h. NODEsName ist pBC)
                    return 'Src'
            elif row['FT_indSm1']=='Snk': #-1:
                    # am Ende der SEGDef (d.h. NODEsNamePrev ist pBC)
                    return 'Snk'
            else:
                    return row['NODEsSEGLfdNrType']    
        dfSegsNodesNDataDpkt['PT_ind']=dfSegsNodesNDataDpkt.apply(lambda row: fGetPT_indFromRow(row),axis=1)
        dfSegsNodesNDataDpkt.drop(columns=['FT_indSm1'],inplace=True)

        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodesNDataDpkt nach XT Klassifizierung',dfSegsNodesNDataDpkt.to_string()))

        # Schieber-PVs (ZU,SCHLIESST,OEFFNET,AUF sowie _Base und _Exts)
        for ATTTRTYPE in ['ZU','SCHLIESST','OEFFNET','AUF']:
    
            ATTTRTYPE_Post='_'+ATTTRTYPE
    
            V3_DPKT_tmp=V3_DPKT[V3_DPKT['ATTRTYPE'].isin([ATTTRTYPE]) & V3_DPKT['OBJTYPE'].isin(['VENT'])]
    
            df=pd.merge(dfSegsNodesNDataDpkt,V3_DPKT_tmp,left_on='OBJID',right_on='fkOBJTYPE',how='left',suffixes=('',ATTTRTYPE_Post))

            dfSegsNodesNDataDpkt=df.filter(items=dfSegsNodesNDataDpkt.columns.to_list()
                        +
                        [                         
                         'OPCITEM_ID'+ATTTRTYPE_Post,'NAME'+ATTTRTYPE_Post
                        ]
                        )            
        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['SEGName','NODEsSEGLfdNr']).reset_index(drop=True)
        logger.debug("{:s}{:s}:\n{:s}".format(logStr,'dfSegsNodesNDataDpkt nach ZU,SCHLIESST,OEFFNET,AUF',dfSegsNodesNDataDpkt.to_string()))

        def fGetMaxCommonPatternInVENTPVs(row
                                            ,cols=['OPCITEM_ID_ZU','OPCITEM_ID_SCHLIESST','OPCITEM_ID_OEFFNET','OPCITEM_ID_AUF']
                                            ,sep='.'):
    
            sList=[row[col] for col in cols]
            sList=[item for item in sList if not pd.isnull(item)]
            sList=[item for item in sList if len(item) > 0]
    
            if len(sList)==4:
                # Liste aller Bestandteile
                l = sep.join(sList).split(sep)
                # zaehlen, wie oft die Bestandteile jeweils vorkommen
                d = Counter(l)
                # die max. Zahl, mit der Bestandteile vorkommen (1: jeder Bestandteil erscheint nur 1x)
                maxCount=max(d.values())
                s=''
                for string, count in d.most_common()[0:maxCount]: # ueber alle Bestandteile, die am Haeufigsten vorkommen
                    if s=='':
                        s=string
                    else:
                        s=s+sep+string   
                # string aus den am Haeufigsten vorkommenden Bestandteilen
                return s
            else:
                return None
        dfSegsNodesNDataDpkt['VENT_ID_Base']=dfSegsNodesNDataDpkt.apply(lambda row: fGetMaxCommonPatternInVENTPVs(row),axis=1)

        def fGetDifferentPatternInVENTPVs(row
                                            ,cols=['OPCITEM_ID_ZU','OPCITEM_ID_SCHLIESST','OPCITEM_ID_OEFFNET','OPCITEM_ID_AUF']
                                            ,commonPattern='VENT_ID_Base'):
    
            sList=[row[col] for col in cols]
            sList=[item for item in sList if not pd.isnull(item)]
            sList=[item for item in sList if len(item) > 0]
    

    
            if len(sList)==4:
        
                s=''

                for idx,item in enumerate(sList):
                    string=item.replace(row[commonPattern],'')

                    if s=='':
                            s=string
                    else:
                            s=s+string  
                    if idx<len(sList)-1:
                        s=s+'/'  
                return s
            else:
                return None
        dfSegsNodesNDataDpkt['VENT_ID_Exts']=dfSegsNodesNDataDpkt.apply(lambda row: fGetDifferentPatternInVENTPVs(row),axis=1)



        # DN etc.
        V3_VBEL_tmp = V3_VBEL.copy(deep=True)
        V3_VBEL_tmp['OBJID'] = V3_VBEL_tmp.index.get_level_values('OBJID')
        V3_VBEL_tmp.reset_index(inplace = True, drop = True)
        dfSegsNodesNDataDpkt = pd.merge(dfSegsNodesNDataDpkt, V3_VBEL_tmp[['OBJID', 'DN','DI','L']], how = 'left', on = 'OBJID')
        dfSegsNodesNDataDpkt['V']=dfSegsNodesNDataDpkt.apply(lambda row: math.pi*math.pow(row['DI'],2)/4*10**-6*row['L'],axis=1)
        dfSegsNodesNDataDpkt['L']=dfSegsNodesNDataDpkt['L'].fillna(0.)
        dfSegsNodesNDataDpkt['V']=dfSegsNodesNDataDpkt['V'].fillna(0.)
        dfSegsNodesNDataDpkt['L']=dfSegsNodesNDataDpkt['L'].round(2)
        dfSegsNodesNDataDpkt['V']=dfSegsNodesNDataDpkt['V'].round(2)
        dfSegsNodesNDataDpkt['LSum']=dfSegsNodesNDataDpkt.groupby('SEGName')['L'].transform(pd.Series.cumsum)
        dfSegsNodesNDataDpkt['VSum']=dfSegsNodesNDataDpkt.groupby('SEGName')['V'].transform(pd.Series.cumsum)
        dfSegsNodesNDataDpkt['LSum']=dfSegsNodesNDataDpkt['LSum'].round(2)
        dfSegsNodesNDataDpkt['VSum']=dfSegsNodesNDataDpkt['VSum'].round(2)
        dfSegsNodesNDataDpkt['D']=dfSegsNodesNDataDpkt.apply(lambda row: row.DI if not pd.isnull(row.DI) else row.DN ,axis=1)
        dfSegsNodesNDataDpkt['D']=dfSegsNodesNDataDpkt['D'].round(2)

        g=dfSegsNodesNDataDpkt.groupby(by='SEGName')
        df=g.sum()[['L','V']]
        df.rename(columns={'L':'LGes','V':'VGes'},inplace=True)
        df['LGes']=df['LGes'].round(2)
        df['VGes']=df['VGes'].round(2)
        dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt,df,left_on='SEGName', right_index=True,how='left')

        # ---
        colList=dfSegsNodesNDataDpkt.columns.to_list()
        dfSegsNodesNDataDpkt['DIVPipelineName']=dfSegsNodesNDataDpkt['SEGName'].apply(lambda x: fDIVNameFromSEGName(x))
        ### dfSegsNodesNDataDpkt['DIVPipelineName']=dfSegsNodesNDataDpkt['SEGName'].apply(lambda x: re.search('(\d+)_(\w+)_(\w+)_(\w+)',x).group(1)+'_'+re.search('(\d+)_(\w+)_(\w+)_(\w+)',x).group(3) )
        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.filter(items=['DIVPipelineName']+colList)

        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['DIVPipelineName','SEGName','SEGNodes','NODEsSEGLfdNr']).reset_index(drop=True)

        # SEGNr
        dfSegs=dfSegsNodesNDataDpkt[['DIVPipelineName','SEGName','SEGNodes']].drop_duplicates()
        dfSegs=dfSegs.sort_values(by=['DIVPipelineName','SEGName', 'SEGNodes']).reset_index(drop=True)
        dfSegs['SEGNr']=dfSegs.index+1
        dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt,dfSegs,left_on='SEGName',right_on='SEGName',how='left',suffixes=('','_')).filter(items=dfSegsNodesNDataDpkt.columns.to_list()+['SEGNr'])

        dfSegsNodesNDataDpkt['DruckResIDBase']=dfSegsNodesNDataDpkt['OPCITEM_ID'].apply(lambda x: fGetBaseIDFromResID(x) )
        dfSegsNodesNDataDpkt['SEGResIDBase']=dfSegsNodesNDataDpkt['SEGName'].apply(lambda x: fGetSEGBaseIDFromSEGName(x) ) 

        # --- lfd. Nr. der Druckmessstelle im Segment ermitteln 
        df=dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['DruckResIDBase'].notnull()].copy()
        df['NODEsSEGDruckErgLfdNr']=df.groupby('SEGName').cumcount() + 1
        df['NODEsSEGDruckErgLfdNr']=df['NODEsSEGDruckErgLfdNr'].astype(int)
        cols=dfSegsNodesNDataDpkt.columns.to_list()
        cols.append('NODEsSEGDruckErgLfdNr')
        dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt
                                          ,df
                                          ,left_index=True
                                          ,right_index=True
                                          ,how='left'
                                          ,suffixes=('','_df')
                                          ).filter(items=cols)
        dfSegsNodesNDataDpkt['NODEsSEGDruckErgLfdNr']=dfSegsNodesNDataDpkt['NODEsSEGDruckErgLfdNr'].astype(int,errors='ignore')

        ###### --- ODI        
        ODIFile=os.path.join(VersionsDir,ODI)
        if os.path.exists(ODIFile):
            
            logger.info("{:s}###### {:10s}: {:s}: Lesen und prüfen ...".format(logStr,'ODI',ODI))

            dfODI=Lx.getDfFromODI(ODIFile) 

            dfSegsNodesNDataDpkt['SEGResIDs']=dfSegsNodesNDataDpkt['SEGResIDBase'].apply(lambda x:  fGetErgIDsFromBaseID(baseID=x,dfODI=dfODI,pattern=False))
            dfSegsNodesNDataDpkt['SEGResIDsIMDI']=dfSegsNodesNDataDpkt['SEGResIDBase'].apply(lambda x:  fGetErgIDsFromBaseID(baseID=x,dfODI=dfODI,pattern=True))

            dfSegsNodesNDataDpkt['DruckResIDs']=dfSegsNodesNDataDpkt['DruckResIDBase'].apply(lambda x:  fGetErgIDsFromBaseID(baseID=x,dfODI=dfODI,pattern=False))
            dfSegsNodesNDataDpkt['DruckResIDsIMDI']=dfSegsNodesNDataDpkt['DruckResIDBase'].apply(lambda x:  fGetErgIDsFromBaseID(baseID=x,dfODI=dfODI,pattern=True))
        else:
            pass
            logger.debug("{:s}###### {:10s}: {:s}: Datei existiert nicht.".format(logStr,'ODI',ODI))

        # LDSPara Daten ergaenzen
        if os.path.exists(LDSParaFile):
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape vorher:  {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape)) 
            dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt,dfPara,left_on='SEGNodes',right_index=True,suffixes=('','_LDSPara'),how='left')
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape nachher: {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape))     

        ###### --- LDSParaPT
        LDSParaPTFile=os.path.join(VersionsDir,LDSParaPT)
        if os.path.exists(LDSParaPTFile):

            logger.info("{:s}###### {:10s}: {:s}: Lesen und prüfen ...".format(logStr,'LDSParaPT',LDSParaPT))

            dfDPDTParams=pd.read_csv(LDSParaPTFile,delimiter=';',error_bad_lines=False,warn_bad_lines=True)

            dfMehrfach=dfDPDTParams.groupby(by='#ID').filter(lambda x: len(x) > 1)
            rows,cols=dfMehrfach.shape
            if rows > 0:            
                logger.warning("{:s}Mehrfachkonfigurationen:".format(logStr))    
                logger.warning("{:s}".format(dfMehrfach.to_string()))   
                dfDPDTParams=dfDPDTParams.groupby(by='#ID').first()

            # LDSParaPT ergaenzen
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape vorher:  {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape))     
            dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt,dfDPDTParams,left_on='CLIENT_ID',right_on='#ID',how='left')
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape nachher:  {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape))     

            dfOhne=dfSegsNodesNDataDpkt[(~pd.isnull(dfSegsNodesNDataDpkt['CLIENT_ID']) & dfSegsNodesNDataDpkt['CLIENT_ID'].str.len()>0 ) & (pd.isnull(dfSegsNodesNDataDpkt['pMin'])) ][['DIVPipelineName','SEGName','NODEsName','ZKOR','CLIENT_ID']].reset_index(drop=True)
            rows,cols=dfOhne.shape
            if rows > 0:            
                logger.debug("{:s}Druckmessstellen ohne Mindestdruck:".format(logStr))     
                logger.debug("{:s}".format(dfOhne.to_string()))     
            dfSegsNodesNDataDpkt['pMinMlc']=dfSegsNodesNDataDpkt.apply(lambda row: row['ZKOR']+row['pMin']*100000/(794.*9.81),axis=1)

            g=dfSegsNodesNDataDpkt.groupby(by='SEGName')
            df=g.pMinMlc.agg(pMinMlcMinSEG=np.min,pMinMlcMaxSEG=np.max)

            # pMinMlcMinSEG, pMinMlcMaxSEG ergaenzen
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape vorher:  {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape))     
            dfSegsNodesNDataDpkt=pd.merge(dfSegsNodesNDataDpkt,df,left_on='SEGName',right_index=True,how='left')
            logger.debug("{:s}dfSegsNodesNDataDpkt: shape nachher:  {!s:s}".format(logStr,dfSegsNodesNDataDpkt.shape))    

            # Segmente ohne Mindestdruecke ausgeben
            df=dfSegsNodesNDataDpkt.groupby(['SEGName']).first()
            df=df[pd.isnull(df['pMinMlcMinSEG'])][['DIVPipelineName','SEGNodes']]
            rows,cols=df.shape
            if rows > 0:            
                logger.debug("{:s}ganze Segmente ohne Mindestdruck:".format(logStr))    
                logger.debug("{:s}".format(df.to_string()))    

            # Mindestdruecke ausgeben
            df=dfSegsNodesNDataDpkt[(~pd.isnull(dfSegsNodesNDataDpkt['CLIENT_ID']) & dfSegsNodesNDataDpkt['CLIENT_ID'].str.len()>0 ) & (~pd.isnull(dfSegsNodesNDataDpkt['pMin'])) ][['DIVPipelineName','SEGName','NODEsName','ZKOR','CLIENT_ID','pMin']].reset_index(drop=True)
            logger.debug("{:s}dfSegsNodesNDataDpkt: Mindestdrücke: {!s:s}".format(logStr,df.to_string()))    
        else:
            logger.debug("{:s}###### {:10s}: {:s}: Datei existiert nicht.".format(logStr,'LDSParaPT',LDSParaPT))
        
        cols=[
        'DIVPipelineName'
        ,'SEGName'        
        ,'SEGNodes'# (Ki~Kk; Schluessel in LDSPara)
        ,'SEGNr'
        ,'SEGOnlyInLDSPara'

        ,'Förderrichtungs-PV'
        ,'Leckort-PV'
        ,'Simstat-PV'

        ,'NODEsRef'
        ,'NODEsRef_max'
        ,'NODEsSEGLfdNr'
        ,'NODEsSEGLfdNrType'
        ,'NODEsName'
        ,'OBJTYPE' # (des den Knoten anschliessenden VBELs)
        ,'OBJID' # (pk des den Knoten anschliessenden VBELs)

        ,'ZKOR'
        ,'Blockname'
        ,'NODEsOBJID' # (pk des Knotens)
        
        ,'CLIENT_ID'
        ,'OPCITEM_ID'
        ,'NAME' # (der DPKT-Gruppe des PH-Kanals des Knotens)
        ,'BESCHREIBUNG' # (des PH-Kanals des Knotens)

        ,'CLIENT_ID_QM'
        ,'OPCITEM_ID_QM'
        ,'NAME_QM' # (der DPKT-Gruppe des QM-Kanals des VENT-VBELs)
        ,'BESCHREIBUNG_QM' # (des QM-Kanals des VENT-VBELs)

        ,'CLIENT_ID_LP'
        ,'OPCITEM_ID_LP'
        ,'NAME_LP' # (der DPKT-Gruppe des LINEPACKRATE-Kanals des ROHR-VBELs)
        ,'BESCHREIBUNG_LP' # (des LINEPACKRATE-Kanals des ROHR-VBELs)

        ,'NODEsNamePrev' # hilfreich bei Generierungen

        ,'FT_ind'
        ,'FT_NODEsName'
        ,'FT_NODEsNameTopo'
        ,'FT_NODEsPT'
        ,'PT_ind'

        # Ventil-Steuerung PVs:
        ,'OPCITEM_ID_ZU'
        ,'NAME_ZU' # (Name der DPKT-Gruppe)
        ,'OPCITEM_ID_SCHLIESST'
        ,'NAME_SCHLIESST' # (Name der DPKT-Gruppe)
        ,'OPCITEM_ID_OEFFNET'
        ,'NAME_OEFFNET' # (Name der DPKT-Gruppe)
        ,'OPCITEM_ID_AUF'
        ,'NAME_AUF' # (Name der DPKT-Gruppe)

        ,'VENT_ID_Base' # (Basisname (GGN) aller 4 PVs)
        ,'VENT_ID_Exts' # PrePost zum Basisnamen 
       
        ,'DN'
        ,'DI'
        ,'L'
        ,'V'
        ,'LSum'
        ,'VSum'
        ,'D'
        ,'LGes'
        ,'VGes'

        ,'DruckResIDBase'
        ,'SEGResIDBase'

        ,'NODEsSEGDruckErgLfdNr'
        ]

        colsODI=[

        # ODI (die einzigen Spalten die vom ODI abhaengig sind)

        'SEGResIDs' # configured Extensions to Base
        ,'SEGResIDsIMDI' # configured Extensions to Base (IMDI. ...)

        ,'DruckResIDs' # configured Extensions to Base
        ,'DruckResIDsIMDI' # configured Extensions to Base (IMDI. ...)
        ]
       
        colsRest=[
        
        # LDSPara Daten

        'ACC_SLOWTRANSIENT'
        ,'ACC_TRANSIENT'
        ,'DESIGNFLOW'
        ,'DT'
        ,'FILTERWINDOW'
        ,'L_PERCENT_STDY'
        ,'L_PERCENT_STRAN'
        ,'L_PERCENT_TRANS'
        ,'L_SHUTOFF'
        ,'L_SLOWTRANSIENT'
        ,'L_SLOWTRANSIENTQP'
        ,'L_STANDSTILL'
        ,'L_STANDSTILLQP'
        ,'L_TRANSIENT'
        ,'L_TRANSIENTPDNTF'
        ,'L_TRANSIENTQP'
        ,'L_TRANSIENTVBIGF'
        ,'MEAN'
        ,'ORDER'
        ,'TIMER'
        ,'TIMERTOLISS'
        ,'TIMERTOLIST'
        ,'TTIMERTOALARM'

        # LDSParaPT

        ,'#ID'
        ,'pMin'
        ,'DT_Vorhaltemass'
        ,'TTimer_PMin'
        ,'Faktor_PMin'
        ,'MaxL_PMin'

        ,'pMinMlc'
        ,'pMinMlcMinSEG'
        ,'pMinMlcMaxSEG'

        ]

        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.filter(items=cols+colsODI+colsRest)
     
        dfSegsNodesNDataDpkt.drop_duplicates(keep='first', inplace=True)        
        dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt.sort_values(by=['DIVPipelineName','SEGName','SEGNodes','NODEsSEGLfdNr']).reset_index(drop=True)

                                                                                                                   
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return dfSegsNodesNDataDpkt

def fResValidSeriesSTAT_S(x): # STAT_S    
    if pd.isnull(x)==False:     
        if x >=0:
            return True
        else:
            return False
    else:
        return False

def fResValidSeriesSTAT_S601(x): # STAT_S
    if pd.isnull(x)==False:
        if x>=601:
            return True
        else:
            return False
    else:
        return False

def fResValidSeriesAL_S(x,value=20): # AL_S
    if pd.isnull(x)==False:
        if x==value:
            return True
        else:
            return False
    else:
        return False

def fResValidSeriesAL_S10(x): 
    return fResValidSeriesAL_S(x,value=10)
def fResValidSeriesAL_S4(x): 
    return fResValidSeriesAL_S(x,value=4)
def fResValidSeriesAL_S3(x): 
    return fResValidSeriesAL_S(x,value=3)
    

ResChannelFunctions=[fResValidSeriesSTAT_S,fResValidSeriesAL_S,fResValidSeriesSTAT_S601]
ResChannelResultNames=['Zustaendig','Alarm','Stoerung']
ResChannelTypes=['STAT_S','AL_S','STAT_S'] 

# (fast) alle verfuegbaren Erg-Kanaele
ResChannelTypesAll=['AL_S','STAT_S','SB_S','MZ_AV','LR_AV','NG_AV','LP_AV','AC_AV','ACCST_AV','ACCTR_AV','ACF_AV','TIMER_AV','AM_AV','DNTD_AV','DNTP_AV','DPDT_AV'
                    ,'DPDT_REF_AV'
                    ,'DPDT_REF' # Workaround
                    ,'DP2DT2_REF_AV'
                    ,'DP2DT2_AV'
                    ,'QM_AV','ZHKNR_S']

baseColorsSchieber=[ # Schieberfarben   
                                         'g'        #                           1
                                        ,'b'        #                           2
                                        ,'m'        #                           3                                      
                                        ,'r'        #                           4
                                        ,'c'        #                           5
                                        # alle Basisfarben außer y gelb
                                        ,'tab:blue' #                           6
                                        ,'tab:orange' #                         7 
                                        ,'tab:green' #                          8
                                        ,'tab:red' #                            9
                                        ,'tab:purple' #                         10
                                        ,'tab:brown' #                          11
                                        ,'tab:pink'  #                          12                                    
                                        ,'gold'     #                           13
                                        ,'fuchsia'  #                           14                                       
                                        ,'coral'    #                           15                                                     
                    ]   
markerDefSchieber=[ # Schiebersymobole                      
                                         '^'        # 0 Auf
                                        ,'v'        # 1 Zu
                                        ,'>'        # 2 Halt
                                        # ab hier Zustaende
                                        ,'4'        # 3 Laeuft
                                        ,'3'        # 4 Laeuft nicht
                                        ,'P'        # 5 Zust
                                        ,'1'        # 6 Auf
                                        ,'2'        # 7 Zu
                                        ,'+'        # 8 Halt
                                        ,'x'        # 9 Stoer
                    ]          

# --- Reports LDS: Funktionen und Hilfsfunktionen
# -----------------------------------------------

def getLDSResVecDf(
     ResIDBase='ID.' # i.e. for Segs Objects.3S_XYZ_SEG_INFO.3S_L_6_EL1_39_TUD.In. / i.e. for Drks Objects.3S_XYZ_DRUCK.3S_6_EL1_39_PTI_02_E.In.
    ,LDSResBaseType='SEG' # or Druck
    ,lx=None
    ,timeStart=None,timeEnd=None
    ,ResChannelTypes=ResChannelTypesAll
    ,timeShiftPair=None
    ):
    """
    returns a df: the specified LDSResChannels (AL_S, ...) for an ResIDBase 
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfResVec=pd.DataFrame()
    try:

        # zu lesende IDs basierend auf ResIDBase bestimmen 
        ErgIDs=[ResIDBase+ext for ext in ResChannelTypes]
        IMDIErgIDs=['IMDI.'+ID for ID in ErgIDs]
        ErgIDsAll=[*ErgIDs,*IMDIErgIDs]
        
        # Daten lesen von TC-H5s       
        dfFiltered=lx.getTCsFromH5s(timeStart=timeStart,timeEnd=timeEnd,LDSResOnly=True,LDSResColsSpecified=ErgIDsAll,LDSResTypeSpecified=LDSResBaseType,timeShiftPair=timeShiftPair) 
        
        # Spalten umbenennen
        colDct={}
        for col in dfFiltered.columns:            
            m=re.search(Lx.pID,col)
            colDct[col]=m.group('E')
        dfResVec=dfFiltered.rename(columns=colDct)        

    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)     
        
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return dfResVec

def fGetResTimes(
    ResIDBases=[] # Liste der Wortstaemme der Ergebnisvektoren
   ,df=pd.DataFrame() # TCsLDSRes...
   ,ResChannelTypes=ResChannelTypes # ['STAT_S','AL_S','STAT_S'] # Liste der Ergebnisvektoren Postfixe
   ,ResChannelFunctions=ResChannelFunctions # [fResValidSeriesSTAT_S,ResValidSeriesAL_S,fResValidSeriesSTAT_S601] # Liste der Ergebnisvektoren Funktionen
   ,ResChannelResultNames=ResChannelResultNames # ['Zustaendig','Alarm','Stoerung'] # Liste der key-Namen der Ergebnisse
   ,tdAllowed=pd.Timedelta('1 second') # erlaubte Zeitspanne zwischen geht und kommt (die beiden an diese Zeitspanne angrenzenden Zeitbereiche werden als 1 Zeit gewertet)
):
    """
    Return: dct 
            key:   ResIDBase
            value: dct:
                        key:    ResChannelResultName
                        Value:  Liste mit Zeitpaaren (oder leere Liste)
    """
    resTimesDct={}
    for ResIDBase in ResIDBases:
        tPairsDct={}

        for idx,ext in enumerate(ResChannelTypes):

            ID=ResIDBase+ext
            if ext == 'AL_S':
                debugOutput=True
            else:
                debugOutput=False

            if ID in df:     
                #print("{:s} in Ergliste".format(ID))
                tPairs=findAllTimeIntervallsSeries(
                            s=df[ID].dropna()  #!                             
                           ,fct=ResChannelFunctions[idx]                       
                           ,tdAllowed=tdAllowed#pd.Timedelta('1 second')
                           ,debugOutput=debugOutput
                                        )                            
            else:
                #print("{:s} nicht in Ergliste".format(ID))
                tPairs=[]
            tPairsDct[ResChannelResultNames[idx]]=tPairs

        resTimesDct[ResIDBase]=tPairsDct
    return resTimesDct

def getAlarmStatistikData(    
     h5File='a.h5'   
    ,dfSegsNodesNDataDpkt=pd.DataFrame()    
    ,timeShiftPair=None # z.B. (1,'H') bei Replay     
    ):
    """
    Returns TCsLDSRes1,TCsLDSRes2,dfCVDataOnly
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    TCsLDSRes1=pd.DataFrame()
    TCsLDSRes2=pd.DataFrame()

    try:             
        # "connect" to the App Logs  
        lx=Lx.AppLog(h5File=h5File) 

        if hasattr(lx, 'h5FileLDSRes'):
            logger.error("{0:s}{1:s}".format(logStr,'In den TCs nur Res und nicht Res1 und Res2?!')) 
            raise RmError
       
        # zu lesende Daten ermitteln
        l=dfSegsNodesNDataDpkt['DruckResIDBase'].unique()
        l = l[~pd.isnull(l)]
        DruckErgIDs=[*[ID+'AL_S' for ID in l],*[ID+'STAT_S' for ID in l],*[ID+'SB_S' for ID in l],*[ID+'ZHKNR_S' for ID in l]]
        #
        l=dfSegsNodesNDataDpkt['SEGResIDBase'].unique()
        l = l[~pd.isnull(l)]
        SEGErgIDs=[*[ID+'AL_S' for ID in l],*[ID+'STAT_S' for ID in l],*[ID+'SB_S' for ID in l],*[ID+'ZHKNR_S' for ID in l]]
        ErgIDs=[*DruckErgIDs,*SEGErgIDs]
        
        # Daten lesen
        TCsLDSRes1,TCsLDSRes2=lx.getTCsFromH5s(LDSResOnly=True,LDSResColsSpecified=ErgIDs,timeShiftPair=timeShiftPair) 

        (preriod,freq)=timeShiftPair
        timeDeltaStr="{:d} {:s}".format(preriod,freq)        
        timeDelta=pd.Timedelta(timeDeltaStr)
        dfCVDataOnly=lx.getCVDFromH5(timeDelta=timeDelta,returnDfCVDataOnly=True) 


    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return TCsLDSRes1,TCsLDSRes2,dfCVDataOnly

def processAlarmStatistikData(    
     TCsLDSRes1=pd.DataFrame()
    ,TCsLDSRes2=pd.DataFrame()
    ,dfSegsNodesNDataDpkt=pd.DataFrame()    
    ,tdAllowed=None # pd.Timedelta('1 second')

        # Alarm geht ... Alarm kommt (wieder): wenn Zeitspanne ... <= tdAllowed, dann wird dies _gewertet als dieselbe Alarmzeitspanne
        # d.h. es handelt sich _gewertet inhaltlich um denselben Alarm
        # None zählt die Alarme strikt getrennt    
    ):
    """

    Returns: SEGResDct,DruckResDct            

    ResDct:
        key: baseID (i.e. Objects.3S_FBG_SEG_INFO.3S_L_6_BUV_01_SPV.In.
        value: dct
            key: Zustaendig:    value: Zeitbereiche, in denen der Ergebnisvektor zustaendig ist     (Liste von Zeitstempelpaaren)
            key: Alarm:         value: Zeitbereiche, in denen der Ergebnisvektor in Alarm war       (Liste von Zeitstempelpaaren)
            key: Stoerung:      value: Zeitbereiche, in denen der Ergebnisvektor in Stoerung war    (Liste von Zeitstempelpaaren)
            key: AL_S_SB_S:     value: Liste mit Listen (den verschiedenen SB_S    pro Alarm in der zeitlichen Reihenfolge ihres Auftretens) (Länge der Liste == Länge der Liste von Alarm)
            key: AL_S_ZHKNR_S:  value: Liste mit Listen (den verschiedenen ZHKNR_S pro Alarm in der zeitlichen Reihenfolge ihres Auftretens) (Länge der Liste == Länge der Liste von Alarm)

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:            
              
        # Zeiten SEGErgs mit zustaendig und Alarm ...       
        l=[baseID for baseID in dfSegsNodesNDataDpkt[~dfSegsNodesNDataDpkt['SEGOnlyInLDSPara']]['SEGResIDBase'].unique() if not pd.isnull(baseID)] 
        SEGResDct=fGetResTimes(ResIDBases=l,df=TCsLDSRes1,tdAllowed=tdAllowed)
        logger.debug("{:s}SEGResDct: {!s:s}".format(logStr,SEGResDct))

        # Zeiten DruckErgs mit zustaendig und Alarm ...       
        l=[baseID for baseID in dfSegsNodesNDataDpkt[~dfSegsNodesNDataDpkt['SEGOnlyInLDSPara']]['DruckResIDBase'].unique() if not pd.isnull(baseID)] 
        DruckResDct=fGetResTimes(ResIDBases=l,df=TCsLDSRes2,tdAllowed=tdAllowed)
        logger.debug("{:s}DruckResDct: {!s:s}".format(logStr,DruckResDct))

        # verschiedene Auspraegungen pro Alarmzeit ermitteln
        for ResDct, ResSrc, LDSResBaseType in zip([SEGResDct, DruckResDct],[TCsLDSRes1,TCsLDSRes2],['SEG','Druck']):
            for idxID,(ID,IDDct) in enumerate(ResDct.items()):         
                # IDDct: das zu erweiternde Dct

                # Alarme
                tPairs=IDDct['Alarm']

                for keyStr, colExt in zip(['AL_S_SB_S','AL_S_ZHKNR_S'],['SB_S','ZHKNR_S']):
                    lGes=[]           
                    if tPairs != []:        
                        for tPair in tPairs:                    
                            col=ID+colExt                    
                            lSingle=ResSrc.loc[tPair[0]:tPair[1],col]
                            lSingle=[int(x) for x in lSingle if pd.isnull(x)==False]
                            lSingle=[lSingle[0]]+[lSingle[i] for i in range(1,len(lSingle)) if lSingle[i]!=lSingle[i-1]]
                            lGes.append(lSingle)
                    IDDct[keyStr]=lGes
                      
                # das erweiterte Dct zuweisen    
                ResDct[ID]=IDDct
                                                                                                             
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return SEGResDct,DruckResDct


def addNrToAlarmStatistikData(    
     SEGResDct={}
    ,DruckResDct={}  
    ,dfAlarmEreignisse=pd.DataFrame()   
    ):
    """

    Returns: SEGResDct,DruckResDct added with key AL_S_NR

    ResDct:
        key: baseID (i.e. Objects.3S_FBG_SEG_INFO.3S_L_6_BUV_01_SPV.In.
        value: dct
            key: Zustaendig:    value: Zeitbereiche, in denen der Ergebnisvektor zustaendig ist     (Liste von Zeitstempelpaaren)
            key: Alarm:         value: Zeitbereiche, in denen der Ergebnisvektor in Alarm war       (Liste von Zeitstempelpaaren)
            key: Stoerung:      value: Zeitbereiche, in denen der Ergebnisvektor in Stoerung war    (Liste von Zeitstempelpaaren)
            key: AL_S_SB_S:     value: Liste mit Listen (den verschiedenen SB_S    pro Alarm in der zeitlichen Reihenfolge ihres Auftretens) (Länge der Liste == Länge der Liste von Alarm)
            key: AL_S_ZHKNR_S:  value: Liste mit Listen (den verschiedenen ZHKNR_S pro Alarm in der zeitlichen Reihenfolge ihres Auftretens) (Länge der Liste == Länge der Liste von Alarm)
            # ergänzt:
            key: AL_S_NR:       value: Liste mit der Nr. (aus dfAlarmEreignisse) pro Alarm  (Länge der Liste == Länge der Liste von Alarm)

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:             
      
        # 
        for ResDct, LDSResBaseType in zip([SEGResDct, DruckResDct],['SEG','Druck']):
            for idxID,(ID,IDDct) in enumerate(ResDct.items()):         
                # IDDct: das zu erweiternde Dct

                # Alarme
                tPairs=IDDct['Alarm']

               
                lNr=[]           
                if tPairs != []:     


                    ZHKNRnListen=IDDct['AL_S_ZHKNR_S']
                    
                    for idxAlarm,tPair in enumerate(tPairs):     
                        
                        ZHKNRnListe=ZHKNRnListen[idxAlarm]
                        ZHKNR=ZHKNRnListe[0]
                       
                        ae=alarmEvent(tPair[0],tPair[1],ZHKNR,LDSResBaseType)

                        Nr=dfAlarmEreignisse[dfAlarmEreignisse['AlarmEvent']==ae]['Nr'].iloc[0]

                        lNr.append(Nr)

                IDDct['AL_S_NR']=lNr
                      
                # das erweiterte Dct zuweisen    
                ResDct[ID]=IDDct

            

                                                                                                             
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return SEGResDct,DruckResDct

def processAlarmStatistikData2(    
     DruckResDct=pd.DataFrame()
    ,TCsLDSRes2=pd.DataFrame()
    ,dfSegsNodesNDataDpkt=pd.DataFrame()    
    ):
    """
    Druckergebnisaussagen auf Segmentergebnisaussagen geeignet verdichtet

    Returns: SEGDruckResDct        
    
    ResDct:
        key: baseID 
        value: dct
            sortiert und direkt angrenzende oder gar ueberlappende Zeiten aus Druckergebnissen zusammenfasst
                key: Zustaendig:    value: Zeitbereiche, in denen ein Druckergebnisvektor zustaendig ist     (Liste von Zeitstempelpaaren)
                key: Alarm:         value: Zeitbereiche, in denen ein Druckergebnisvektor in Alarm war       (Liste von Zeitstempelpaaren)
                key: Stoerung:      value: Zeitbereiche, in denen ein Druckergebnisvektor in Stoerung war    (Liste von Zeitstempelpaaren)
            voneiander verschiedene Ausprägungen (sortiert) aus Druckergebnissen
                key: AL_S_SB_S:     Liste 
                key: AL_S_ZHKNR_S:  Liste 
                key: AL_S_NR:       Liste 

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:             
      
        # Druckergebnisaussagen auf Segmentergebnisaussagen geeignet verdichtet       

        SEGDruckResDct={}

        # merken, ob eine ID bereits bei einem SEG gezählt wurde; die Alarme einer ID sollen nur bei einem SEG gezaehlt werden
        IDBereitsGezaehlt={}

        # über alle DruckErgs
        for idx,(ID,tPairsDct) in enumerate(DruckResDct.items()):
    
            # SEG ermitteln
    
            # ein DruckErg kann zu mehreren SEGs gehoeren z.B. gehoert ein Verzweigungsknoten i.d.R. zu 3 versch. SEGs
            tupleLst=getNamesFromDruckResIDBase(dfSegsNodesNDataDpkt,ID)            
     
            for idxTuple,(DIVPipelineName,SEGName,SEGResIDBase,SEGOnlyInLDSPara) in enumerate(tupleLst):   
                

                # wenn internes SEG 
                if SEGOnlyInLDSPara:                    
                    logger.debug("{:s}ID {:35s} wird bei SEGName {:s} nicht gezaehlt da dieses SEG intern.".format(logStr,ID,SEGName))
                    continue

                # ID wurde bereits gezählt
                if ID in IDBereitsGezaehlt.keys():
                    logger.debug("{:s}ID {:35s} wird bei SEGName {:s} nicht gezaehlt sondern wurde bereits bei SEGName {:s} gezaehlt.".format(logStr,ID,SEGName,IDBereitsGezaehlt[ID]))
                    continue
                else:
                    # ID wurde noch nicht gezaehlt
                    IDBereitsGezaehlt[ID]=SEGName

                #if idxTuple>0:
                #    logger.debug("{:s}ID {:35s} wird bei SEGName {:s} nicht gezaehlt sondern nur bei SEGName {:s}.".format(logStr,ID,SEGName,tupleLst[0][1]))
                #    continue

                if len(tPairsDct['Alarm'])>0:                   
                    logger.debug("{:s}SEGName {:20s}: durch ID {:40s} mit Alarm. Nr des Verweises von ID auf ein Segment: {:d}".format(logStr,SEGName,ID, idxTuple+1))

                if SEGResIDBase not in SEGDruckResDct.keys():
                    # auf dieses SEG wurde noch nie verwiesen
                    SEGDruckResDct[SEGResIDBase]=deepcopy(tPairsDct) # das Segment erhält die Ergebnisse des ersten Druckvektors der zum Segment gehört
                else:
                    # ergaenzen

                    # Zeitlisten ergänzen
                    for idx2,ext in enumerate(ResChannelTypes):
                        tPairs=tPairsDct[ResChannelResultNames[idx2]]
                        for idx3,tPair in enumerate(tPairs):                                    
                            if True: #tPair not in SEGDruckResDct[SEGResIDBase][ResChannelResultNames[idx2]]: #  keine identischen Zeiten mehrfach zaehlen
                                # die Ueberlappung von Zeiten wird weiter unten behandelt
                                SEGDruckResDct[SEGResIDBase][ResChannelResultNames[idx2]].append(tPair)

                    # weitere Listen ergaenzen             
                    for ext in ['AL_S_SB_S','AL_S_ZHKNR_S','AL_S_NR']:
                        SEGDruckResDct[SEGResIDBase][ext]=SEGDruckResDct[SEGResIDBase][ext]+tPairsDct[ext]


        # Ergebnis: sortieren und dann direkt angrenzende oder gar ueberlappende Zeiten zusammenfassen
        for idx,(ID,tPairsDct) in enumerate(SEGDruckResDct.items()):
            for idx2,ext in enumerate(tPairsDct.keys()):        
                if ext in ['AL_S_SB_S','AL_S_ZHKNR_S','AL_S_NR']:     # keine Zeiten              
                    pass
                else:
                    
                    tPairs=tPairsDct[ResChannelResultNames[idx2]]
                    tPairs=sorted(tPairs,key=lambda tup: tup[0])
                    tPairs=fCombineSubsequenttPairs(tPairs)
                    SEGDruckResDct[ID][ResChannelResultNames[idx2]]=tPairs

        # voneiander verschiedene Ausprägungen (sortiert)
        for idx,(ID,tPairsDct) in enumerate(SEGDruckResDct.items()):            
            for idx2,ext in enumerate(tPairsDct.keys()):        
                v=tPairsDct[ext]
                if ext in ['AL_S_SB_S','AL_S_ZHKNR_S']: # Liste von Listen
                    l=[*{*chain.from_iterable(v)}]
                    l=sorted(pd.unique(l))

                    SEGDruckResDct[ID][ext]=l
                    
                elif ext in ['AL_S_NR']:  # Liste   
                    l=sorted(pd.unique(v))
                    SEGDruckResDct[ID][ext]=l
                else:
                    pass
                    



        logger.debug("{:s}SEGDruckResDct: {!s:s}".format(logStr,SEGDruckResDct))



                                                                                                                   
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return SEGDruckResDct

def buildAlarmDataframes(    
     TCsLDSRes1=pd.DataFrame()
    ,TCsLDSRes2=pd.DataFrame()
    ,dfSegsNodesNDataDpkt=pd.DataFrame() 

    ,dfCVDataOnly=pd.DataFrame() 

    ,SEGResDct={}
    ,DruckResDct={}

    ,replaceTup=('2021-','')
    ,NrBy=['LDSResBaseType','SEGName','Ort','tA','ZHKNR']
    ,NrAsc=[False]+4*[True]

    ):
    """
    Returns dfAlarmStatistik,dfAlarmEreignisse,SEGDruckResDct
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfAlarmStatistik=pd.DataFrame()
    dfAlarmEreignisse=pd.DataFrame()

    try:             

        # Ereignisse
        dfAlarmEreignisse=buildDfAlarmEreignisse( 
            SEGResDct=SEGResDct
           ,DruckResDct=DruckResDct
           ,TCsLDSRes1=TCsLDSRes1
           ,TCsLDSRes2=TCsLDSRes2
           ,dfCVDataOnly=dfCVDataOnly
           ,dfSegsNodesNDataDpkt=dfSegsNodesNDataDpkt
           ,replaceTup=replaceTup
           ,NrBy=NrBy
           ,NrAsc=NrAsc
        )

        # in dfAlarmEreignisse erzeugte Alarm-Nr. an Dct merken
        SEGResDct,DruckResDct=addNrToAlarmStatistikData(    
             SEGResDct
            ,DruckResDct
            ,dfAlarmEreignisse   
        )

        # BZKat der Alarme      
        def fGetAlarmKat(row):
            """
            """

            

            # baseID des Alarms
            baseID=row['OrteIDs'][0]    
    
            # dct des Alarms
            if row['LDSResBaseType']=='SEG':
                dct=SEGResDct[baseID]
            else:
                dct=DruckResDct[baseID]
            
            # Nrn der baseID
            Nrn=dct['AL_S_NR']
        
            # idx dieses Alarms innerhalb der Alarme der baseID
            idxAl=Nrn.index(row['Nr'])       

            # Zustaende dieses alarms
            SB_S=dct['AL_S_SB_S'][idxAl]
    
            kat=''
    
            if 3 in SB_S:
                        kat='instationär'
            else:
                        if 2 in SB_S:
                            kat = 'schw. instat.'
                        else:
                            if 1 in SB_S:
                                kat = 'stat. Fluss'
                            elif 4 in SB_S:
                                kat = 'stat. Ruhe'    
                                    
            return kat

        dfAlarmEreignisse['BZKat']=dfAlarmEreignisse.apply(lambda row: fGetAlarmKat(row),axis=1)

        # Segment-verdichtete Druckergebnisse
        SEGDruckResDct=processAlarmStatistikData2(    
         DruckResDct
        ,TCsLDSRes2
        ,dfSegsNodesNDataDpkt    
        )

        # Alarmstatistik bilden
        dfAlarmStatistik=dfSegsNodesNDataDpkt[~dfSegsNodesNDataDpkt['SEGOnlyInLDSPara']]

        dfAlarmStatistik=dfAlarmStatistik[['DIVPipelineName','SEGName','SEGNodes','SEGResIDBase']].drop_duplicates(keep='first').reset_index(drop=True)
        dfAlarmStatistik['Nr']=dfAlarmStatistik.apply(lambda row: "{:2d}".format(int(row.name)),axis=1)
    
        # SEG
        dfAlarmStatistik['FörderZeiten']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGResDct[x]['Zustaendig'])
        dfAlarmStatistik['FörderZeitenAl']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGResDct[x]['Alarm'])
        dfAlarmStatistik['FörderZeitenSt']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGResDct[x]['Stoerung'])

        dfAlarmStatistik['FörderZeitenAlAnz']=dfAlarmStatistik['FörderZeitenAl'].apply(lambda x: len(x))
        dfAlarmStatistik['FörderZeitenAlSbs']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGResDct[x]['AL_S_SB_S'])

        dfAlarmStatistik['FörderZeitenAlNrn']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGResDct[x]['AL_S_NR'])

        # Druck (SEG-verdichtet)
        dfAlarmStatistik['RuheZeiten']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGDruckResDct[x]['Zustaendig'] if x in SEGDruckResDct.keys() else [])
        dfAlarmStatistik['RuheZeitenAl']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGDruckResDct[x]['Alarm'] if x in SEGDruckResDct.keys() else [])
        dfAlarmStatistik['RuheZeitenSt']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGDruckResDct[x]['Stoerung'] if x in SEGDruckResDct.keys() else [])

        
        dfAlarmStatistik['RuheZeitenAlSbs']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGDruckResDct[x]['AL_S_SB_S'] if x in SEGDruckResDct.keys() else [])

        dfAlarmStatistik['RuheZeitenAlNrn']=dfAlarmStatistik['SEGResIDBase'].apply(lambda x: SEGDruckResDct[x]['AL_S_NR'] if x in SEGDruckResDct.keys() else [])

        #dfAlarmStatistik['RuheZeitenAlAnz']=dfAlarmStatistik['RuheZeitenAl'].apply(lambda x: len(x))
        dfAlarmStatistik['RuheZeitenAlAnz']=dfAlarmStatistik['RuheZeitenAlNrn'].apply(lambda x: len(x))

        # je 3 Zeiten bearbeitet
        dfAlarmStatistik['FörderZeit']=dfAlarmStatistik['FörderZeiten'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))
        dfAlarmStatistik['RuheZeit']=dfAlarmStatistik['RuheZeiten'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))
        dfAlarmStatistik['FörderZeitAl']=dfAlarmStatistik['FörderZeitenAl'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))
        dfAlarmStatistik['RuheZeitAl']=dfAlarmStatistik['RuheZeitenAl'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))        
        dfAlarmStatistik['FörderZeitSt']=dfAlarmStatistik['FörderZeitenSt'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))
        dfAlarmStatistik['RuheZeitSt']=dfAlarmStatistik['RuheZeitenSt'].apply(lambda x: fTotalTimeFromPairs(x,pd.Timedelta('1 minute'),False))        
                                                                                                                   
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return dfAlarmEreignisse, dfAlarmStatistik,SEGDruckResDct

def plotDfAlarmStatistik(    
     dfAlarmStatistik=pd.DataFrame()    
    ):
    """
    Returns the plt.table and the df behind it
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 



    
    df=dfAlarmStatistik[[
        'Nr'
       ,'DIVPipelineName'
       ,'SEGName'

       ,'FörderZeit'
       ,'FörderZeitenAlAnz'
       ,'FörderZeitAl'
       ,'FörderZeitSt'

       ,'RuheZeit'
       ,'RuheZeitenAlAnz'
       ,'RuheZeitAl'     
       ,'RuheZeitSt'            
        ]].copy()

    # diese Zeiten um (Störzeiten) annotieren
    df['FörderZeit']=df.apply(lambda row: "{!s:s} ({!s:s})".format(row['FörderZeit'],row['FörderZeitSt']) if row['FörderZeitSt'] > 0. else row['FörderZeit'] ,axis=1)
    df['RuheZeit']=df.apply(lambda row: "{!s:s} ({!s:s})".format(row['RuheZeit'],row['RuheZeitSt']) if row['RuheZeitSt'] > 0. else row['RuheZeit'],axis=1)

    # LfdNr. annotieren
    df['LfdNr']=df.apply(lambda row: "{:2d} - {:s}".format(int(row.Nr)+1,str(row.DIVPipelineName)),axis=1)

    # Zeiten Alarm um Alarm-Nrn annotieren

    def fAddZeitMitNrn(zeit,lAlNr):
        

        if len(lAlNr) > 0:  
            
            if len(lAlNr) <= 3:                
                return "{!s:s} (Nrn.: {!s:s})".format(zeit,lAlNr)
            else:
                # mehr als 3 Alarme...
                return "{!s:s} (Nrn.: {!s:s}, ...)".format(zeit,lAlNr[0])
        else:
            return zeit

    df['FörderZeitAl']=dfAlarmStatistik.apply(lambda row:  fAddZeitMitNrn(row['FörderZeitAl'],row['FörderZeitenAlNrn']),axis=1)
    df['RuheZeitAl']=dfAlarmStatistik.apply(lambda row:  fAddZeitMitNrn(row['RuheZeitAl'],row['RuheZeitenAlNrn']),axis=1)

    df=df[[
        'LfdNr'
       ,'SEGName'

       ,'FörderZeit'
       ,'FörderZeitenAlAnz'
       ,'FörderZeitAl'

       ,'RuheZeit'
       ,'RuheZeitenAlAnz'
       ,'RuheZeitAl'       
        ]]

    try:             
      
        t=plt.table(cellText=df.values, colLabels=df.columns, loc='center')    

        cols=df.columns.to_list()

        colIdxLfdNr=cols.index('LfdNr')

        colIdxFoerderZeit=cols.index('FörderZeit')
        colIdxFoerderZeitenAlAnz=cols.index('FörderZeitenAlAnz')
        colIdxFoerderZeitAl=cols.index('FörderZeitAl')

        colIdxRuheZeit=cols.index('RuheZeit')
        colIdxRuheZeitenAlAnz=cols.index('RuheZeitenAlAnz')
        colIdxRuheZeitAl=cols.index('RuheZeitAl')


        cells = t.properties()["celld"]
        for cellTup,cellObj in cells.items():
            cellObj.set_text_props(ha='left')
    
            row,col=cellTup # row: 0 fuer Ueberschrift bei Ueberschrift; col mit 0

            if row == 0:
                if col in [colIdxRuheZeit,colIdxRuheZeitenAlAnz,colIdxRuheZeitAl]:
                    pass
                    cellObj.set_text_props(backgroundcolor='plum') 
                elif col in [colIdxFoerderZeit,colIdxFoerderZeitenAlAnz,colIdxFoerderZeitAl]:
                    pass
                    cellObj.set_text_props(backgroundcolor='lightsteelblue') 

            if col == colIdxLfdNr:
        
                if row==0:
                    continue

                if 'color' in dfAlarmStatistik.columns.to_list():
                    color=dfAlarmStatistik['color'].iloc[row-1]
                    cellObj.set_text_props(backgroundcolor=color) 

    
            if col == colIdxFoerderZeit:
        
                if row==0:
                    continue
        
                if dfAlarmStatistik.loc[row-1,'FörderZeit']==0:
                    pass                    
                else:
                    if dfAlarmStatistik.loc[row-1,'FörderZeitSt']/ dfAlarmStatistik.loc[row-1,'FörderZeit']*100>1:
                        cellObj.set_text_props(backgroundcolor='goldenrod') 
                
            if col == colIdxFoerderZeitenAlAnz:
        
                if row==0:
                    continue
        
                if dfAlarmStatistik.loc[row-1,'FörderZeit']==0:
                    cellObj.set_text_props(backgroundcolor='lightgrey')               
                else: # hat Förderzeit
                    if df.loc[row-1,'FörderZeitenAlAnz']==0:
                        cellObj.set_text_props(backgroundcolor='springgreen')       
                    else:                        
                        cellObj.set_text_props(ha='center')
                        cellObj.set_text_props(backgroundcolor='navajowhite')   # palegoldenrod
                        #if df.loc[row-1,'FörderZeitAl']/ dfAlarmStatistik.loc[row-1,'FörderZeit']*100>1:
                        if dfAlarmStatistik.loc[row-1,'FörderZeitAl']/ dfAlarmStatistik.loc[row-1,'FörderZeit']*100>1:
                            cellObj.set_text_props(backgroundcolor='tomato') 
                
            if col == colIdxRuheZeit:
        
                if row==0:
                    continue
        
                if dfAlarmStatistik.loc[row-1,'RuheZeit']==0:
                    pass                    
                else:
                    if dfAlarmStatistik.loc[row-1,'RuheZeitSt']/ dfAlarmStatistik.loc[row-1,'RuheZeit']*100>1:
                        cellObj.set_text_props(backgroundcolor='goldenrod')             

            if col == colIdxRuheZeitenAlAnz:
        
                if row==0:
                    continue
        
                if dfAlarmStatistik.loc[row-1,'RuheZeit']==0:
                    cellObj.set_text_props(backgroundcolor='lightgrey')               
                else: # hat Ruhezeit
                    if df.loc[row-1,'RuheZeitenAlAnz']==0:
                        cellObj.set_text_props(backgroundcolor='springgreen')       
                    else:
                        pass
                        cellObj.set_text_props(ha='center')
                        cellObj.set_text_props(backgroundcolor='navajowhite')  #  # palegoldenrod                            
                        #if df.loc[row-1,'RuheZeitAl']/ dfAlarmStatistik.loc[row-1,'RuheZeit']*100>1:
                        if dfAlarmStatistik.loc[row-1,'RuheZeitAl']/ dfAlarmStatistik.loc[row-1,'RuheZeit']*100>1:
                            cellObj.set_text_props(backgroundcolor='tomato') 
                
            
    
    

        plt.axis('off')   
                                                                                                                           
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return t, df

def fOrteStripped(LDSResBaseType,OrteIDs):
    """
    returns Orte stripped
    """    
    if LDSResBaseType == 'SEG': # 'Objects.3S_FBG_SEG_INFO.3S_L_6_MHV_02_FUD.In.']
        orteStripped=[]
        for OrtID in OrteIDs:
            pass
            m=re.search(Lx.pID,OrtID+'dummy')
            ortStripped=m.group('C3')+'_'+m.group('C4')+'_'+m.group('C5')+'_'+m.group('C6')
            orteStripped.append(ortStripped)
        return orteStripped
                
    elif LDSResBaseType == 'Druck': # Objects.3S_FBG_DRUCK.3S_6_BNV_01_PTI_01.In
        orteStripped=[]
        for OrtID in OrteIDs:
            pass
            m=re.search(Lx.pID,OrtID+'dummy')
            ortStripped=m.group('C2')+'_'+m.group('C3')+'_'+m.group('C4')+'_'+m.group('C5')+m.group('C6')
            orteStripped.append(ortStripped)
        return orteStripped        
    
    else:
        return None

def fCVDTime(row,dfSEG,dfDruck,replaceTup=('2021-','')):

    """
    in:
        dfSEG/dfDruck: TCsLDSRes1/TCsLDSRes2
        row: Zeile aus dfAlarmEreignisse
            von row verwendet:
                LDSResBaseType: SEG (dfSEG) oder nicht (dfDruck)
                OrteIDs:        ==> ID von ZHKNR_S in dfSEG/dfDruck
                ZHKNR:          ZHKNR

    returns:
        string: xZeitA - ZeitEx

            ZeitA: erste  Zeit in der ZHKNR_S in dfSEG/dfDruck den Wert von ZHKNR trägt
            ZeitE: letzte Zeit in der ZHKNR_S in dfSEG/dfDruck den Wert von ZHKNR trägt
            xZeitA, wenn ZeitA die erste Zeit  in dfSEG/dfDruck ist mit einem von Null verschiedenen Wert
            xZeitE, wenn ZeitE die letzte Zeit in dfSEG/dfDruck ist mit einem von Null verschiedenen Wert

            in Zeit wurde replaceTup angewendet

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:

        Time=""
    
        ID=row['OrteIDs'][0]+'ZHKNR_S'
        ZHKNR=row['ZHKNR']
    
        if row['LDSResBaseType']=='SEG':
            df=dfSEG
        else:
            df=dfDruck
    
        s=df[df[ID]==ZHKNR][ID] # eine Spalte; Zeilen in denen ZHKNR_S den Wert von ZHKNR trägt
        tA=s.index[0] # 1. Zeit
        tE=s.index[-1] # letzte Zeit
    
        Time=" {!s:s} - {!s:s} ".format(tA,tE)
    
        try:
            if tA==df[ID].dropna().index[0]:        
                Time='x'+Time.lstrip()
        except:
            logger.debug("{0:s}Time: {1:s}: x-tA Annotation Fehler; keine Annotation".format(logStr,Time)) 

        try:
            if tE==df[ID].dropna().index[-1]:
                Time=Time.rstrip()+'x'       
        except:
            logger.debug("{0:s}Time: {1:s}: x-tE Annotation Fehler; keine Annotation".format(logStr,Time)) 
        
        Time=Time.replace(replaceTup[0],replaceTup[1])

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))                 
        return Time

def buildDfAlarmEreignisse( 
    SEGResDct={}
   ,DruckResDct={}
   ,TCsLDSRes1=pd.DataFrame()
   ,TCsLDSRes2=pd.DataFrame()
   ,dfCVDataOnly=pd.DataFrame() 

   ,dfSegsNodesNDataDpkt=pd.DataFrame() 

   ,replaceTup=('2021-','')
   ,NrBy=['LDSResBaseType','SEGName','Ort','tA','ZHKNR'] # Sortierspalten für die Nr. der Ereignisse
   ,NrAsc=[False]+4*[True] # aufsteigend j/n für die o.g. Sortierspalten  
    ):
    """
    Returns dfAlarmEreignisse:
        Nr:                 lfd. Nr (gebildet gem. NrBy und NrAsc)
        tA:                 Anfangszeit
        tE:                 Endezeit
        tD:                 Dauer des Alarms
        ZHKNR:              ZHKNR (die zeitlich 1., wenn der Alarm sich über mehrere ZHKNRn erstreckt)
        tD_ZHKNR:           Lebenszeit der ZHKNR; x-Annotationen am Anfang/Ende, wenn ZHK beginnt bei Res12-Anfang / andauert bei Res12-Ende; '-1', wenn Lebenszeit nicht ermittelt werden konnte
        ZHKNRn:             sortierte Liste der ZHKNRn des Alarms; eine davon ist ZHKNR; typischerweise die 1. der Liste
        LDSResBaseType:     SEG oder Druck
        OrteIDs:            OrteIDs des Alarms
        Orte:               Kurzform von OrteIDs des Alarms
        Ort:                der 1. Ort von Orte        
        SEGName:            Segment zu dem der 1. Ort des Alarms gehört
        DIVPipelineName:
        Voralarm:           ermittelter Vorlalarm des Alarms; -1, wenn kein Voralarm in Res12 gefunden werden konnte
        Type:               Typ des Kontrollraumns; z.B. p-p für vollständige Flussbilanzen; '', wenn kein Typ gefunden werden konnte
        Name:               Name des Bilanzraumes 
        NrSD:               lfd. Nr Alarm BaseType
        NrName:             lfd. Nr Alarm Name
        NrSEGName:          lfd. Nr Alarm SEGName
        AlarmEvent:         alarmEvent-Objekt        
        ###BZKat:           Betriebszustandskategorie des Alarms
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    dfAlarmEreignisse=pd.DataFrame()

    try:       
       
        AlarmEvents=[] # Liste von AlarmEvent
        AlarmEventsOrte={} # dct der Orte, die diesen (key) AlarmEvent melden
        AlarmEventsZHKNRn={} # dct der ZHKNRn, die zu diesem (key) gehoeren


        # über SEG- und Druck-Ergebnisvektoren
        for ResDct, ResSrc, LDSResBaseType in zip([SEGResDct, DruckResDct],[TCsLDSRes1,TCsLDSRes2],['SEG','Druck']):
           
            for ResIDBase,dct in ResDct.items():
                AL_S=dct['Alarm']
                if len(AL_S) > 0:       
                    # eine Erg-ID weist Alarme [(tA,tE),...] auf

                    # korrespondiernede Liste der ZHKs: [(999,1111),...]
                    ZHKNRnListen=dct['AL_S_ZHKNR_S']

                    ID=ResIDBase+'ZHKNR_S' # fuer nachfolgende Ausgabe
                      
                    # ueber alle Alarme der Erg-ID
                    for idx,AL_S_Timepair in enumerate(AL_S):            
                        (t1,t2)=AL_S_Timepair # tA, tE

                        ZHKNR_S_Lst=ZHKNRnListen[idx] # Liste der ZHKs in dieser Zeit
                        
                        if len(ZHKNR_S_Lst) != 1:                
                            logger.warning(("{:s}ID:\n\t {:s}: Alarm {:d} der ID\n\t Zeit von {!s:s} bis {!s:s}:\n\t Anzahl verschiedener ZHKNRn !=1: {:d} {:s}:\n\t ZHKNR eines Alarms wechselt waehrend eines Alarms. Alarm wird identifiziert mit 1. ZHKNR.".format(logStr,ID
                           ,idx
                           ,t1
                           ,t2
                           ,len(ZHKNR_S_Lst)
                           ,str(ZHKNR_S_Lst)
                           )))     
                            
                        # die erste wird verwendet
                        ZHKNR=int(ZHKNR_S_Lst[0])            

                        # AlarmEvent erzeugen
                        ae=alarmEvent(t1,t2,ZHKNR,LDSResBaseType)
                        
                        if ae not in AlarmEvents:                            
                            # diesen Alarm gibt es noch nicht in der Ereignisliste ...
                            AlarmEvents.append(ae)   
                            AlarmEventsOrte[ae]=[]    
                            AlarmEventsZHKNRn[ae]=[]  
                        else:                            
                            pass 

                        # Ort ergaenzen (derselbe Alarm wird erst ab V83.5.3 nur an einem Ort - dem lexikalisch kleinsten des Bilanzraumes - ausgegeben; zuvor konnte derselbe Alarm an mehreren Orten auftreten)
                        AlarmEventsOrte[ae].append(ResIDBase)
                        # ZHKNR(n) ergaenzen (ein Alarm wird unter 1 ZHKNR geführt)
                        AlarmEventsZHKNRn[ae].append(ZHKNR_S_Lst)
         
        # df erzeugen
        dfAlarmEreignisse=pd.DataFrame.from_records(
           [ae for ae in AlarmEvents],
           columns=alarmEvent._fields
        )

        # Liste der EventOrte erstellen, zuweisen
        l=[]
        for idx,ae in enumerate(AlarmEvents):           
            l.append(AlarmEventsOrte[ae])
        dfAlarmEreignisse['OrteIDs']=l
        # abgekuerzte Orte
        dfAlarmEreignisse['Orte']=dfAlarmEreignisse.apply(lambda row: fOrteStripped(row.LDSResBaseType,row.OrteIDs),axis=1)
        dfAlarmEreignisse['Ort']=dfAlarmEreignisse['Orte'].apply(lambda x: x[0])

        # Liste der ZHKNRn erstellen, zuweisen
        l=[]
        for idx,ae in enumerate(AlarmEvents):           
            lOfZl=AlarmEventsZHKNRn[ae]

            lOfZ=[*{*chain.from_iterable(lOfZl)}]
            lOfZ=sorted(pd.unique(lOfZ))
            l.append(lOfZ)
        dfAlarmEreignisse['ZHKNRn']=l

        # Segmentname eines Ereignisses
        dfAlarmEreignisse['SEGName']=dfAlarmEreignisse.apply(lambda row: 
                                                             dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['SEGResIDBase']==row['OrteIDs'][0]]['SEGName'].iloc[0] if row['LDSResBaseType']=='SEG' 
                                                             else [tuple for tuple in getNamesFromDruckResIDBase(dfSegsNodesNDataDpkt,row['OrteIDs'][0]) if not tuple[-1]][0][1],axis=1)

       # DIVPipelineName eines Ereignisses
        dfAlarmEreignisse['DIVPipelineName']=dfAlarmEreignisse.apply(lambda row: 
                                                                   dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['SEGName']==row['SEGName']]['DIVPipelineName'].iloc[0]                                                              
                                                             ,axis=1)

        # Alarm: ---
        #tA:                 Anfangszeit
        #tE:                 Endezeit
        #ZHKNR:              ZHKNR (1. bei mehreren Alarmen)
        #LDSResBaseType:     SEG oder Druck
        # Orte: ---
        #OrteIDs:            OrteIDs des Alarms
        #Orte:               Kurzform von OrteIDs des Alarms
        #ZHKNRn:
        #SEGName:            Segmentname
        #DIVPipelineName

        ## Nr.                 
        dfAlarmEreignisse.sort_values(by=NrBy,ascending=NrAsc,inplace=True)                 
        dfAlarmEreignisse['Nr']=dfAlarmEreignisse.index+1
        #dfAlarmEreignisse['Nr']=dfAlarmEreignisse['Nr']+1
        logger.debug("{0:s}{1:s}: {2:s}".format(logStr,'dfAlarmEreignisse',dfAlarmEreignisse.to_string()))    

        # Voralarm
        VoralarmTypen=[]
        for index, row in dfAlarmEreignisse.iterrows():      

            # zur Information bei Ausgaben
            OrteIDs=row['OrteIDs']
            OrtID=OrteIDs[0]
            
            VoralarmTyp=None
            try:
                if row['LDSResBaseType']=='SEG':
                    VoralarmTyp=TCsLDSRes1.loc[:row['tA']-pd.Timedelta('1 second'),OrtID+'AL_S'].iloc[-1]               
                elif row['LDSResBaseType']=='Druck':
                    VoralarmTyp=TCsLDSRes2.loc[:row['tA']-pd.Timedelta('1 second'),OrtID+'AL_S'].iloc[-1]                
            except:
                pass

            if pd.isnull(VoralarmTyp): # == None: #?! - ggf. Nachfolger eines neutralen Bilanzraumwechsels
                VoralarmTyp=-1      
                logger.warning("{:s}PV: {:40s} Alarm Nr. {:d} ZHKNR {:d}\n\t tA {!s:s}: kein (isnull) Vorlalarm gefunden?! (ggf. neutraler BRWechsel) - Voralarm gesetzt auf: {:d}".format(logStr
                          ,row['OrteIDs'][0]
                          ,int(row['Nr'])
                          ,row['ZHKNR']
                          ,row['tA'],int(VoralarmTyp)))    

            if int(VoralarmTyp)==0: # == 0: #?! - ggf. Nachfolger eines neutralen Bilanzraumwechsels                 
                VoralarmTyp=0  
                logger.warning("{:s}PV: {:40s} Alarm Nr. {:d} ZHKNR {:d}\n\t tA {!s:s}: Vorlalarm 0?! (ggf. war Bilanz in Stoerung)".format(logStr
                          ,row['OrteIDs'][0]
                          ,int(row['Nr'])
                          ,row['ZHKNR']
                          ,row['tA']))                          
            if int(VoralarmTyp) not in [-1,0,3,4,10]:                
                logger.warning("{:s}PV: {:s} Alarm Nr. {:d} {:d} tA {!s:s}: unbekannter Vorlalarm gefunden: {:d}".format(logStr,row['OrteIDs'][0],int(row['Nr']),row['ZHKNR'],row['tA'],int(VoralarmTyp)))                          
                
            logger.debug("{:s}{:d} {!s:s} VoralarmTyp:{:d}".format(logStr,int(row['Nr']),row['tA'],int(VoralarmTyp)))           
            VoralarmTypen.append(VoralarmTyp)
        dfAlarmEreignisse['Voralarm']=[int(x) for x in VoralarmTypen]

        # Type (aus dfCVDataOnly) und Erzeugungszeit (aus dfCVDataOnly) und Name (aus dfCVDataOnly)
        dfAlarmEreignisse['ZHKNR']=dfAlarmEreignisse['ZHKNR'].astype('int64')
        dfAlarmEreignisse['ZHKNRStr']=dfAlarmEreignisse['ZHKNR'].astype('string')
        dfCVDataOnly['ZHKNRStr']=dfCVDataOnly['ZHKNR'].astype('string')

        #                                                                                            wg. aelteren App-Log Versionen in denen ZHKNR in dfCVDataOnly nicht ermittelt werden konnte 
        #                                                                                            Type,ScenTime,Name sind dann undefiniert
        dfAlarmEreignisse=pd.merge(dfAlarmEreignisse,dfCVDataOnly,on='ZHKNRStr',suffixes=('','_CVD'),how='left').filter(items=dfAlarmEreignisse.columns.to_list()+['Type'
                                                                                                                                                                   #,'ScenTime'
                                                                                                                                                                   ,'Name'])       
        dfAlarmEreignisse=dfAlarmEreignisse.drop(['ZHKNRStr'],axis=1)
        dfAlarmEreignisse=dfAlarmEreignisse.fillna(value='')

     
        # lfd. Nummern
        dfAlarmEreignisse['NrSD']=dfAlarmEreignisse.groupby(['LDSResBaseType']).cumcount() + 1        
        dfAlarmEreignisse['NrName']=dfAlarmEreignisse.groupby(['Name']).cumcount() + 1
        dfAlarmEreignisse['NrSEGName']=dfAlarmEreignisse.groupby(['SEGName']).cumcount() + 1

        # Lebenszeit der ZHKNR
        try:
            dfAlarmEreignisse['tD_ZHKNR']=dfAlarmEreignisse.apply(lambda row: fCVDTime(row,TCsLDSRes1,TCsLDSRes2,replaceTup),axis=1)
        except:
            logger.debug("{:s}Spalte tD_ZHKNR (Lebenszeit einer ZHKNR) konnte nicht ermittelt werden. Vmtl. aeltere App-Log Version.".format(logStr))        
            dfAlarmEreignisse['tD_ZHKNR']='-1'

        # Dauer des Alarms
        dfAlarmEreignisse['tD']=dfAlarmEreignisse.apply(lambda row: row['tE']-row['tA'],axis=1)
        dfAlarmEreignisse['tD']= dfAlarmEreignisse['tD'].apply(lambda x: "{!s:s}".format(x).replace('days','Tage').replace('0 Tage','').replace('Tage','T'))
        
        dfAlarmEreignisse=dfAlarmEreignisse[['Nr','tA', 'tE','tD','ZHKNR','tD_ZHKNR','ZHKNRn','LDSResBaseType'
                    ,'OrteIDs', 'Orte', 'Ort', 'SEGName','DIVPipelineName'
                    ,'Voralarm', 'Type', 'Name'
                    ,'NrSD', 'NrName', 'NrSEGName'
                    ]]
        dfAlarmEreignisse['AlarmEvent']=dfAlarmEreignisse.apply(lambda row: alarmEvent(row['tA'],row['tE'],row['ZHKNR'],row['LDSResBaseType']),axis=1)

        # unklar, warum erforderlich
        dfAlarmEreignisse['Nr']=dfAlarmEreignisse.index+1
                                                                                                                       
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return dfAlarmEreignisse


def fCVDName(Name
):
    """
    """
    
    
    lName=len(Name)

    if len(Name)==0:
        Name='ZHKName vmtl. nicht in Log'

    lNameMaxH=20
    if lName > 2*lNameMaxH:
                
        Name=Name[:lNameMaxH-2]+'....'+Name[lName-lNameMaxH+2:]
        
    Name=Name.replace('Â°','|')
    return Name

def plotDfAlarmEreignisse(    
     dfAlarmEreignisse=pd.DataFrame()    
    ,sortBy=[]
    ,replaceTup=('2021-','')
    ,replaceTuptD=('0 days','')
    ):
    """
    Returns the plt.table
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    


    try:                     
     
        df=dfAlarmEreignisse[['Nr','LDSResBaseType','Voralarm','Type','NrSD','tA','tE','tD','ZHKNR','Name','Orte','tD_ZHKNR','NrName','NrSEGName','SEGName','BZKat']].copy()

        df['tA']=df['tA'].apply(lambda x: str(x).replace(replaceTup[0],replaceTup[1]))
        df['tE']=df['tE'].apply(lambda x: str(x).replace(replaceTup[0],replaceTup[1]))       

        ###df['Anz']=df['Orte'].apply(lambda x: len(x))

        ##df['Orte']=df['Orte'].apply(lambda x: str(x).replace('[','').replace(']','').replace("'",""))
        df['Orte']=df['Orte'].apply(lambda x: str(x[0]))
        
        df['LDSResBaseType']=df.apply(lambda row: "{:s} {:s} - {:d}".format(row['LDSResBaseType'],row['Type'],row['Voralarm']),axis=1)
        df=df[['Nr','LDSResBaseType','NrSD','tA','tE','tD','ZHKNR','Name','NrName','NrSEGName','SEGName','tD_ZHKNR','Orte','BZKat']]
        df.rename(columns={'LDSResBaseType':'ResTyp - Voralarm'},inplace=True)
        df.rename(columns={'tD_ZHKNR':'ZHKZeit','Name':'ZHKName'},inplace=True)       

        ###df['ZHKName']=df['ZHKName'].apply(lambda x: fCVDName(x))
        ####df['ZHKName']=df['Orte'].apply(lambda x: x[0])


        df['NrSEGName (SEGName)']=df.apply(lambda row: "{!s:2s} ({!s:s})".format(row['NrSEGName'],row['SEGName']),axis=1)

        df=df[['Nr','ResTyp - Voralarm','NrSD','tA','tD','ZHKNR'
               ,'Orte' #'ZHKName'
               ,'BZKat'
               ,'NrName','NrSEGName (SEGName)','ZHKZeit']]

        df.rename(columns={'Orte':'ID'},inplace=True)       


        df['tD']=df['tD'].apply(lambda x: str(x).replace(replaceTuptD[0],replaceTuptD[1]))


        def fGetZHKNRStr(row,dfOrig):
            """
            returns:
                ZHKNStr in Abhängigkeit der aktuellen Zeile und dfOrig
            """
            s=dfOrig[dfOrig['Nr']==row['Nr']].iloc[0]

            if len(s.ZHKNRn)>1:
                if len(s.ZHKNRn)==2:
                    return "{:d} ({!s:s})".format(row['ZHKNR'],s.ZHKNRn[1:])
                else:
                    return "{:d} (+{:d})".format(row['ZHKNR'],len(s.ZHKNRn)-1)
            else:
                return "{:d}".format(row['ZHKNR'])

        df['ZHKNR']=df.apply(lambda row: fGetZHKNRStr(row,dfAlarmEreignisse),axis=1)
            

        if sortBy!=[]:
            df=df.sort_values(by=sortBy)
       

        t=plt.table(cellText=df.values, colLabels=df.columns

                    ,colWidths=[.03,.1 # Nr ResTyp-Voralarm
                                ,.04 # NrSD
                                ,.08,.08 # tA tD
                                ,.085 # ZHKNR
                                ,.1125,.07 #.1125 # ID BZKat
                                ,.04 # NrName
                                ,.14  # NrSEGName (SEGName)
                                ,.2125] # ZHKZeit
                   
                    , cellLoc='left'
                    , loc='center')    

        t.auto_set_font_size(False)
        t.set_fontsize(10)
        
        
        cols=df.columns.to_list()
        #colIdxOrte=cols.index('Orte')
        #colIdxName=cols.index('ZHKName')

        colIdxNrSD=cols.index('NrSD')

        colIdxNrSEG=cols.index('NrSEGName (SEGName)')

        #                          ResTyp - Voralarm
        colIdxResTypVA=cols.index('ResTyp - Voralarm')

        cells = t.properties()["celld"]
        for cellTup,cellObj in cells.items():
             cellObj.set_text_props(ha='left')


             row,col=cellTup # row: 0 fuer Ueberschrift bei Ueberschrift; col mit 0
    
             #if col == colIdxName:                 
             #    cellObj.set_text_props(ha='left')
             if col == colIdxNrSD:
                 if row > 0:
                    if dfAlarmEreignisse.loc[row-1,'LDSResBaseType']=='SEG':
                        cellObj.set_text_props(backgroundcolor='lightsteelblue') 
                    else:
                        cellObj.set_text_props(backgroundcolor='plum') 

             elif col == colIdxNrSEG:
        
                if row==0:
                    continue

                if 'color' in dfAlarmEreignisse.columns.to_list():
                    color=dfAlarmEreignisse['color'].iloc[row-1]
                    cellObj.set_text_props(backgroundcolor=color)                       


             elif col == colIdxResTypVA and row > 0:
                pass


                        
                if dfAlarmEreignisse.loc[row-1,'Voralarm'] in [10]:
                        cellObj.set_text_props(backgroundcolor='sandybrown')  

                elif dfAlarmEreignisse.loc[row-1,'Voralarm'] in [4]:
                        cellObj.set_text_props(backgroundcolor='pink')   

                elif dfAlarmEreignisse.loc[row-1,'Voralarm'] in [3]:
                        cellObj.set_text_props(backgroundcolor='lightcoral')   


             else:
                 pass
                 #cellObj.set_text_props(fontsize=16)
           
       
            
    

        plt.axis('off')       
                                                                                                                   
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return t

def plotDfAlarmStatistikReportsSEGErgs( 
     h5File='a.h5'   
    ,dfAlarmStatistik=pd.DataFrame()    
    ,SEGResDct={}
    ,timeStart=None,timeEnd=None
    ,SEGErgsFile='SEGErgs.pdf'
    ,stopAtSEGNr=None
    ,dateFormat='%y.%m.%d: %H:%M:%S'
    ,byhour=[0,3,6,9,12,15,18,21]
    ,byminute=None
    ,bysecond=None  
    ,timeFloorCeilStr=None  
    ,timeFloorCeilStrDetailPre='6T' 
    ,timeFloorCeilStrDetailPost='3T'
    ,timeShiftPair=None
    ):
    """
    Creates PDF for all SEGs with 'AL_S':     
    1 Base Plot 
    + (for all SEGs with FörderZeitenAlAnz>0) Detail Plots for the Alarms 

    Creates corresponding Single-PNGs 

    Returns xlimsDct:
        key: BaseID
        value: list of Timepairs of the Detail Plots for the Alarms
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    try:   
        
        lx=Lx.AppLog(h5File=h5File)  

        firstTime,lastTime,tdTotalGross,tdTotal,tdBetweenFilesTotal=lx.getTotalLogTime()
                       
        if timeStart==None:
            if timeFloorCeilStr != None:
                timeStart = firstTime.floor(freq=timeFloorCeilStr) 
            else:
                timeStart = firstTime
        if timeEnd==None:
            if timeFloorCeilStr != None:
                timeEnd = lastTime.ceil(freq=timeFloorCeilStr) 
            else:
                timeEnd = lastTime

        logger.debug("{0:s}timeStart (ohne timeShift): {1:s} timeEnd (ohne timeShift): {2:s}".format(logStr,str(timeStart),str(timeEnd)))       
        
        xlimsDct={}
       
        pdf=PdfPages(SEGErgsFile)
        (fileNameBase,ext)= os.path.splitext(SEGErgsFile)

        if timeShiftPair != None:
            (preriod,freq)=timeShiftPair
            timeDeltaStr="{:d} {:s}".format(preriod,freq)        
            timeDelta=pd.Timedelta(timeDeltaStr)    
        else:
            timeDelta=pd.Timedelta('0 Seconds')               
    
        idxSEGPlotted=0 
        for idx,(index,row) in enumerate(dfAlarmStatistik.iterrows()):

            if stopAtSEGNr != None:
                if idxSEGPlotted>=stopAtSEGNr:                        
                    break

            titleStr="LfdNr {:2d} - {:s}: {:15s}: {:50s}".format(
                             int(row.Nr)+1         
                            ,str(row.DIVPipelineName)
                           # ,row['SEGNodes']                           
                            ,row['SEGName']                                   
                            ,row['SEGResIDBase'])  
         
#            if row['FörderZeitenAlAnz']==0: # and row['RuheZeitenAlAnz']==0:
#                logger.info("{:s}: FörderZeitenAlAnz: 0".format(titleStr))     
#                continue # keine SEGs ohne Alarme drucken
          
            # Erg lesen
            ResIDBase=row['SEGResIDBase']               
            dfSegReprVec=getLDSResVecDf(ResIDBase=ResIDBase,LDSResBaseType='SEG',lx=lx,timeStart=timeStart,timeEnd=timeEnd,timeShiftPair=timeShiftPair)

            ID='AL_S'
            if ID not in dfSegReprVec.keys():
                logger.info("{:s}: keine AL_S-Eintraege (SEG vmtl. nur im Ruhebetrieb)".format(titleStr))     
                continue 

            idxSEGPlotted=idxSEGPlotted+1

            xlimsDct[ResIDBase]=[]

            logger.debug("{:s}ResIDBase: {:s} dfSegReprVec: Spalten: {!s:s}".format(logStr,ResIDBase,dfSegReprVec.columns.to_list()))    

            # Plot Basis ###########################################################
            
            fig=plt.figure(figsize=DINA4q,dpi=dpiSize)             

            ax=fig.gca()          

            pltLDSErgVec(
             ax
            ,dfSegReprVec=dfSegReprVec # Ergebnisvektor SEG; pass empty Df if Druck only    
            ,dfDruckReprVec=pd.DataFrame() # Ergebnisvektor DRUCK; pass empty Df if Seg only    

            ,xlim=(timeStart+timeDelta,timeEnd+timeDelta)   
            
            ,dateFormat=dateFormat
            ,byhour=byhour 
            ,byminute=byminute
            ,bysecond=bysecond

       

            ,plotLegend=True    
    
            )    
                       
            backgroundcolor='white'
            if row['FörderZeit']==0:
                backgroundcolor='lightgrey'               
            else: # hat Förderzeit
                if row['FörderZeitenAlAnz']==0:
                    backgroundcolor='springgreen'       
                else:                                           
                    backgroundcolor='navajowhite'
                    if row['FörderZeitAl']/row['FörderZeit']*100>1:
                        backgroundcolor='tomato' 
            
            txt="SEG: {:s}: FörderZeit: {:8.2f} FörderZeitenAlAnz: {:d}".format(row['SEGNodes'],row['FörderZeit'],row['FörderZeitenAlAnz'])      
            if row['FörderZeitenAlAnz'] > 0:
                if row['FörderZeitenAlAnz'] <= 3:
                    txtNr=" Nrn.: {!s:s}".format(row['FörderZeitenAlNrn'])        
                else:                    
                    txtNr=" Nrn.: {!s:s} u.w.".format(row['FörderZeitenAlNrn'][0])       
                txt=txt+txtNr      
            else:
                txtNr=''

            ax.text(.98, .1,txt,
            horizontalalignment='right',
            verticalalignment='center',
            backgroundcolor=backgroundcolor,
            transform=ax.transAxes)

            if row['FörderZeitSt']>0:
                backgroundcolor='white'
                if row['FörderZeitSt']/row['FörderZeit']*100>1:
                    backgroundcolor='goldenrod'    
                txt="(SEG: FörderZeitSt: {:8.2f})".format(row['FörderZeitSt'])        
                ax.text(.98, .05,txt,
                horizontalalignment='right',
                verticalalignment='center',
                backgroundcolor=backgroundcolor,
                transform=ax.transAxes)
                   
            ax.set_title( titleStr,loc='left') 

            fig.tight_layout(pad=2.) 

            # PDF
            pdf.savefig(fig)  
                 
            # png            
            fileName="{:s} {:2d} - {:s} {:s} {:s}.png".format(fileNameBase
                              ,int(row.Nr)+1
                              ,str(row.DIVPipelineName)
                              ,row['SEGName']
                              ,txtNr.replace('Nrn.: ','Nrn ').replace(',','').replace('[','').replace(']','').replace('u.w.','u w'))
            plt.savefig(fileName)  

            plt.show()
                                 
            ###plt.clf()
            plt.close()     
                    
            if row['FörderZeitenAlAnz']==0: # and row['RuheZeitenAlAnz']==0:
                #logger.info("{:s}: FörderZeitenAlAnz: 0".format(titleStr))     
                continue # fuer SEGs ohne Alarme keine Alarmdetails drucken

            # Plot Alarme ###########################################################

            dct=SEGResDct[row['SEGResIDBase']]

            timeFirstAlarmStarts,dummy=dct['Alarm'][0]
            dummy,timeLastAlarmEnds=dct['Alarm'][-1]
            
            for idxAl,AlNr in enumerate(row['FörderZeitenAlNrn']):                
                timeAlarmStarts,timeAlarmEnds=dct['Alarm'][idxAl]


                timeStartDetail = timeAlarmStarts.floor(freq=timeFloorCeilStrDetailPre)
 
                timeEndDetail = timeAlarmEnds.ceil(freq=timeFloorCeilStrDetailPost)

                # wenn AlarmRand - PlotRand < 3 Minuten: um 3 Minuten erweitern

                if timeAlarmStarts-timeStartDetail<pd.Timedelta('3 Minutes'):
                    timeStartDetail=timeStartDetail-pd.Timedelta('3 Minutes')
                if timeEndDetail-timeAlarmEnds<pd.Timedelta('3 Minutes'):
                    timeEndDetail=timeEndDetail+pd.Timedelta('3 Minutes')

                logger.debug("{0:s}timeStartDetail: {1:s} timeEndDetail: {2:s}".format(logStr,str(timeStartDetail),str(timeEndDetail)))       

                xlimsDct[ResIDBase].append((timeStartDetail,timeEndDetail))

                fig=plt.figure(figsize=DINA4q,dpi=dpiSize)             

                ax=fig.gca()          

                pltLDSErgVec(
                 ax
                ,dfSegReprVec=dfSegReprVec # Ergebnisvektor SEG; pass empty Df if Druck only    
                ,dfDruckReprVec=pd.DataFrame() # Ergebnisvektor DRUCK; pass empty Df if Seg only    

                ,xlim=(timeStartDetail,timeEndDetail)    # wenn die dct-Zeiten time-geshifted sind ist das korrekt 
            
                ,dateFormat=dateFormat
                ,byhour=None#byhour 
                ,byminute=list(np.arange(0,60))#byminute
                ,bysecond=None#bysecond

  


                )    
                       
                backgroundcolor='white'
                if row['FörderZeit']==0:
                    backgroundcolor='lightgrey'               
                else: # hat Förderzeit
                    if row['FörderZeitenAlAnz']==0:
                        backgroundcolor='springgreen'       
                    else:                                           
                        backgroundcolor='navajowhite'
                        if row['FörderZeitAl']/row['FörderZeit']*100>1:
                            backgroundcolor='tomato' 
            
                txt="SEG: {:s}: FörderZeit: {:8.2f} FörderZeitenAlAnz: {:d}".format(row['SEGNodes'],row['FörderZeit'],row['FörderZeitenAlAnz'])      
                txtNr=" Nr.: {!s:s}".format(AlNr)       
                txt=txt+txtNr 

                ax.text(.98, .1,txt,
                horizontalalignment='right',
                verticalalignment='center',
                backgroundcolor=backgroundcolor,
                transform=ax.transAxes)

                if row['FörderZeitSt']>0:
                    backgroundcolor='white'
                    if row['FörderZeitSt']/row['FörderZeit']*100>1:
                        backgroundcolor='goldenrod'    
                    txt="(SEG: FörderZeitSt: {:8.2f})".format(row['FörderZeitSt'])        
                    ax.text(.98, .05,txt,
                    horizontalalignment='right',
                    verticalalignment='center',
                    backgroundcolor=backgroundcolor,
                    transform=ax.transAxes)
                   
                ax.set_title( titleStr,loc='left') 
                #logger.info("{:s}".format(titleStr))       

                fig.tight_layout(pad=2.) 

                # PDF
                pdf.savefig(fig)  
                 
                # png
                #(fileName,ext)= os.path.splitext(SEGErgsFile)
                fileNameAlarm="{:s} {:s}.png".format(fileName.replace('.png','')
                                                 ,txtNr.replace('Nr.: ','Nr ').replace(',','').replace('[','').replace(']',''))

                plt.savefig(fileNameAlarm)  

                plt.show()
                                 
                ###plt.clf()
                plt.close()     

                       
        ###plt.close()  
        pdf.close()  
      
       
                                                                                                                   
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return xlimsDct

def plotDfAlarmStatistikReportsDruckErgs( 
     h5File='a.h5'   
    ,dfAlarmStatistik=pd.DataFrame()     
    ,dfSegsNodesNDataDpkt=pd.DataFrame()    
    ,DruckResDct={}
    ,timeStart=None,timeEnd=None
    ,DruckErgsFile='DruckErgs.pdf'
    ,stopAtSEGNr=None
    ,dateFormat='%y.%m.%d: %H:%M:%S'
    ,byhour=[0,3,6,9,12,15,18,21]
    ,byminute=None
    ,bysecond=None  
    ,timeFloorCeilStr=None #'1H'
    ,timeFloorCeilStrDetailPre='6T' # Runden (3 Minuten)
    ,timeFloorCeilStrDetailPost='3T'
    ,timeShiftPair=None
    ):
    """
    Creates PDF for all SEGs with RuheZeitenAlAnz>0
    1 Base Plot for a Druck with an Alarm and Detail Plots for the Alarms 
    Creates corresponding Single-PNGs 

    Returns xlimsDct:
        key: BaseID
        value: list of Timepairs of the Detail Plots for the Alarms
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    try:   
       
        lx=Lx.AppLog(h5File=h5File)  

        firstTime,lastTime,tdTotalGross,tdTotal,tdBetweenFilesTotal=lx.getTotalLogTime()

        logger.debug("{0:s}firstTime (ohne TimeShift): {1:s} lastTime (ohne TimeShift): {2:s}".format(logStr,str(firstTime),str(lastTime)))    

        if timeStart==None:
            if timeFloorCeilStr != None:
                timeStart = firstTime.floor(freq=timeFloorCeilStr) # https://stackoverflow.com/questions/35339139/where-is-the-documentation-on-pandas-freq-tags
            else:
                timeStart = firstTime
        if timeEnd==None:
            if timeFloorCeilStr != None:
                timeEnd = lastTime.ceil(freq=timeFloorCeilStr) 
            else:
                timeEnd = lastTime

        if timeShiftPair != None:
            (preriod,freq)=timeShiftPair
            timeDeltaStr="{:d} {:s}".format(preriod,freq)        
            timeDelta=pd.Timedelta(timeDeltaStr)    
        else:
            timeDelta=pd.Timedelta('0 Seconds')   

        logger.debug("{0:s}timeStart abgerundet (ohne TimeShift): {1:s} timeEnd aufgerundet (ohne TimeShift): {2:s} TimeShift: {3:s}".format(logStr
               ,str(timeStart)
               ,str(timeEnd)
               ,str(timeDelta)))          
        
        xlimsDct={}

        pdf=PdfPages(DruckErgsFile)
        (fileNameBase,ext)= os.path.splitext(DruckErgsFile)

        # über alle Segmente der Alarmstatistik (die DruckIDs sollen in der Reihenfolge der Alarmstatistik abgearbeitet werden)
        idxSEGPlotted=0
        for idx,(index,row) in enumerate(dfAlarmStatistik.iterrows()):        

            if row['RuheZeitenAlAnz']==0: # and row['RuheZeitenAlAnz']==0:             
                logger.info("LfdNr {:2d} - {:s}: {:15s}: RuheZeitenAlAnz: 0".format(
                             int(row.Nr)+1         
                            ,str(row.DIVPipelineName)
                           # ,row['SEGNodes']                           
                            ,row['SEGName']))  
                continue # keine SEGs ohne Alarme drucken
            
            if stopAtSEGNr != None:
                if idxSEGPlotted>=stopAtSEGNr:                        
                    break
            idxSEGPlotted=idxSEGPlotted+1

            # DruckIDs eines Segmentes
            DruckIDs=sorted([ID for ID in dfSegsNodesNDataDpkt[dfSegsNodesNDataDpkt['SEGName']==row['SEGName']]['DruckResIDBase'].unique() if not pd.isnull(ID)])

            for idxDruckID,DruckResIDBase in enumerate(DruckIDs):                

                dct=DruckResDct[DruckResIDBase]

                if len(dct['Alarm'])==0:
                    # nur DruckIDs mit Alarmen plotten
                    logger.info("LfdNr {:2d} - {:s}: {:15s}: RuheZeitenAlAnz des SEGs: {:d} - diese Druck-ID: {:s} ohne Alarm".format(
                             int(row.Nr)+1         
                            ,str(row.DIVPipelineName)                                        
                            ,row['SEGName']
                            ,row['RuheZeitenAlAnz'] 
                            ,DruckResIDBase
                            ))  
                    continue

                fig=plt.figure(figsize=DINA4q,dpi=dpiSize)     

                # Erg lesen
                ResIDBase=DruckResIDBase         
                dfDruckReprVec=getLDSResVecDf(ResIDBase=ResIDBase,LDSResBaseType='Druck',lx=lx,timeStart=timeStart,timeEnd=timeEnd,timeShiftPair=timeShiftPair)

                logger.debug("{:s}ResIDBase: {:s} dfDruckReprVec: Spalten: {!s:s}".format(logStr,ResIDBase,dfDruckReprVec.columns.to_list()))    

                logger.debug("{:s}ID: {:s}: timeStart (mit TimeShift): {:s} timeEnd (mit TimeShift): {:s}".format(logStr
                ,DruckResIDBase
                ,str(dfDruckReprVec.index[0])
                ,str(dfDruckReprVec.index[-1])
                ))       

                ID='AL_S'
                if ID not in dfDruckReprVec.keys():
                    continue 

                xlimsDct[ResIDBase]=[]

                ax=fig.gca()          

                pltLDSErgVec(
                    ax
                ,dfSegReprVec=pd.DataFrame() # Ergebnisvektor SEG; pass empty Df if Druck only    
                ,dfDruckReprVec=dfDruckReprVec  # Ergebnisvektor DRUCK; pass empty Df if Seg only    

                ,xlim=(timeStart+timeDelta,timeEnd+timeDelta)   
            
                ,dateFormat=dateFormat
                ,byhour=byhour 
                ,byminute=byminute
                ,bysecond=bysecond






                )    

                backgroundcolor='white'
                if row['RuheZeit']==0:
                    backgroundcolor='lightgrey'               
                else: # hat Ruhezeit
                    if row['RuheZeitenAlAnz']==0:
                        backgroundcolor='springgreen'       
                    else:                                           
                        backgroundcolor='navajowhite'
                        if row['RuheZeitAl']/row['RuheZeit']*100>1:
                            backgroundcolor='tomato' 
        
                txt="SEG: {:s}: LfdNr {:2d}: RuheZeit: {:8.2f} RuheZeitenAlAnz: {:d}".format(
                        row['SEGNodes']  
                       ,int(row.Nr)+1                            
                       ,row['RuheZeit']
                       ,row['RuheZeitenAlAnz'])        

                ax.text(.98, .1,txt,
                horizontalalignment='right',
                verticalalignment='center',
                backgroundcolor=backgroundcolor,
                transform=ax.transAxes)

                if row['RuheZeitSt']>0:
                    backgroundcolor='white'
                    if row['RuheZeitSt']/row['RuheZeit']*100>1:
                        backgroundcolor='goldenrod'    
                    txt="(SEG: RuheZeitSt: {:8.2f})".format(row['RuheZeitSt'])        
                    ax.text(.98, .05,txt,
                    horizontalalignment='right',
                    verticalalignment='center',
                    backgroundcolor=backgroundcolor,
                    transform=ax.transAxes)

                RuheZeiten=DruckResDct[DruckResIDBase]['Zustaendig']
                RuheZeit=fTotalTimeFromPairs(RuheZeiten,pd.Timedelta('1 minute'),False)

                AlarmZeiten=DruckResDct[DruckResIDBase]['Alarm']
                AlarmZeit=fTotalTimeFromPairs(AlarmZeiten,pd.Timedelta('1 minute'),False)

                RuheZeitenSt=DruckResDct[DruckResIDBase]['Stoerung']
                RuheZeitSt=fTotalTimeFromPairs(RuheZeitenSt,pd.Timedelta('1 minute'),False)

                txt="Druck: RuheZeit: {:8.2f} (davon St: {:8.2f}) RuheZeitenAlAnz: {:3d}".format(                  
                        RuheZeit
                       ,RuheZeitSt
                       ,len(AlarmZeiten))        

                ax.text(.98, .15,txt,
                horizontalalignment='right',
                verticalalignment='center',
                backgroundcolor='white',
                transform=ax.transAxes)

                titleStr="LfdNr {:2d} - {:s}: {:s}: {:s}".format(
                             int(row.Nr)+1         
                            ,str(row.DIVPipelineName)
                           # ,row['SEGNodes']                           
                            ,row['SEGName']                                   
                            ,DruckResIDBase)  
        
                ax.set_title( titleStr,loc='left')                 
       
                fig.tight_layout(pad=2.) 

                # png                
                fileName="{:s} {:2d} - {:s} {:s} {:s}.png".format(fileNameBase
                                                             ,int(row.Nr)+1
                                                             ,str(row.DIVPipelineName)
                                                             ,row['SEGName']
                                                             ,fOrteStripped('Druck',[DruckResIDBase])[0]
                                                             )
                plt.savefig(fileName)  
                plt.show()
                pdf.savefig(fig)            
                plt.close()     


                # Plot Alarme ###########################################################

                dct=DruckResDct[DruckResIDBase]


                logger.debug("{:s}ID: {:s}: dct: {!s:s} AlNrn des Segmentes: {!s:s}".format(logStr
                ,DruckResIDBase
                ,dct
                ,row['RuheZeitenAlNrn'] # die AlNrn des Segmentes
                ))       

                timeFirstAlarmStarts,dummy=dct['Alarm'][0]
                dummy,timeLastAlarmEnds=dct['Alarm'][-1]        
                
                for idxAl,AlNr in enumerate(row['RuheZeitenAlNrn']):       
                    try:
                        idxAlPV=dct['AL_S_NR'].index(AlNr)
                    except ValueError:
                        # der Alarm AlNr des Segmentes tritt an dieser PV des Segmentes nicht auf
                        continue

                    timeAlarmStarts,timeAlarmEnds=dct['Alarm'][idxAlPV]

                    timeStartDetail = timeAlarmStarts.floor(freq=timeFloorCeilStrDetailPre) 
                    timeEndDetail = timeAlarmEnds.ceil(freq=timeFloorCeilStrDetailPost)

                    if timeAlarmStarts-timeStartDetail<pd.Timedelta('3 Minutes'):
                        timeStartDetail=timeStartDetail-pd.Timedelta('3 Minutes')
                    if timeEndDetail-timeAlarmEnds<pd.Timedelta('3 Minutes'):
                        timeEndDetail=timeEndDetail+pd.Timedelta('3 Minutes')


                    xlimsDct[ResIDBase].append((timeStartDetail,timeEndDetail))

                    fig=plt.figure(figsize=DINA4q,dpi=dpiSize)             

                    ax=fig.gca()                      

                    pltLDSErgVec(
                        ax
                    ,dfSegReprVec=pd.DataFrame() # Ergebnisvektor SEG; pass empty Df if Druck only    
                    ,dfDruckReprVec=dfDruckReprVec  # Ergebnisvektor DRUCK; pass empty Df if Seg only    

                    ,xlim=(timeStartDetail,timeEndDetail)   # wenn die dct-Zeiten time-geshifted sind ist das korrekt 
            
                    ,dateFormat=dateFormat
                    ,byhour=None#byhour 
                    ,byminute=list(np.arange(0,60))#byminute
                    ,bysecond=None#bysecond


      

 
                    )    

                    backgroundcolor='white'
                    if row['RuheZeit']==0:
                        backgroundcolor='lightgrey'               
                    else: # hat Ruhezeit
                        if row['RuheZeitenAlAnz']==0:
                            backgroundcolor='springgreen'       
                        else:                                           
                            backgroundcolor='navajowhite'
                            if row['RuheZeitAl']/row['RuheZeit']*100>1:
                                backgroundcolor='tomato' 
        
                    txt="SEG: {:s}: LfdNr {:2d}: RuheZeit: {:8.2f} RuheZeitenAlAnz: {:d}".format(
                            row['SEGNodes']  
                           ,int(row.Nr)+1                            
                           ,row['RuheZeit']
                           ,row['RuheZeitenAlAnz'])        

                    ax.text(.98, .1,txt,
                    horizontalalignment='right',
                    verticalalignment='center',
                    backgroundcolor=backgroundcolor,
                    transform=ax.transAxes)

                    if row['RuheZeitSt']>0:
                        backgroundcolor='white'
                        if row['RuheZeitSt']/row['RuheZeit']*100>1:
                            backgroundcolor='goldenrod'    
                        txt="(SEG: RuheZeitSt: {:8.2f})".format(row['RuheZeitSt'])        
                        ax.text(.98, .05,txt,
                        horizontalalignment='right',
                        verticalalignment='center',
                        backgroundcolor=backgroundcolor,
                        transform=ax.transAxes)

                    RuheZeiten=DruckResDct[DruckResIDBase]['Zustaendig']
                    RuheZeit=fTotalTimeFromPairs(RuheZeiten,pd.Timedelta('1 minute'),False)

                    AlarmZeiten=DruckResDct[DruckResIDBase]['Alarm']
                    AlarmZeit=fTotalTimeFromPairs(AlarmZeiten,pd.Timedelta('1 minute'),False)

                    RuheZeitenSt=DruckResDct[DruckResIDBase]['Stoerung']
                    RuheZeitSt=fTotalTimeFromPairs(RuheZeitenSt,pd.Timedelta('1 minute'),False)

                    txt="Druck: RuheZeit: {:8.2f} (davon St: {:8.2f}) RuheZeitenAlAnz: {:3d} Nr. {:4d}".format(                  
                            RuheZeit
                           ,RuheZeitSt
                           ,len(AlarmZeiten)
                           ,AlNr)        

                    ax.text(.98, .15,txt,
                    horizontalalignment='right',
                    verticalalignment='center',
                    backgroundcolor='white',
                    transform=ax.transAxes)

                    titleStr="LfdNr {:2d} - {:s}: {:s}: {:s}".format(
                                 int(row.Nr)+1         
                                ,str(row.DIVPipelineName)
                               # ,row['SEGNodes']                           
                                ,row['SEGName']                                   
                                ,DruckResIDBase)  
        
                    ax.set_title( titleStr,loc='left') 
                   
                    fig.tight_layout(pad=2.) 

                    # PDF
                    pdf.savefig(fig)  
                 
                    # png                    
                    fileNameAlarm="{:s} Nr {:d}.png".format(fileName.replace('.png',''),AlNr)                   
                    plt.savefig(fileNameAlarm)  

                    plt.show()                                           
                    plt.close()     


            
        #plt.close()  
        pdf.close()        
                                                                                                                          
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return xlimsDct

def plotTimespans(
     
    xlims # list of sections 
   ,orientation='landscape' # oben HYD unten LDS; 'portrait': # links HYD rechts LDS

   ,pad=3.5 # tight_layout() can take keyword arguments of pad, w_pad and h_pad. These control the extra padding around the figure border and between subplots. The pads are specified in fraction of fontsize.
   ,w_pad=0.5
   ,h_pad=0.5

   # 'portrait'  # links HYD rechts LDS
   ,rectSpalteLinks=[0, 0, 0.5, 1]
   ,rectSpalteRechts=[0.325, 0, 1, 1] 
   # 'landscape': # oben HYD unten LDS
   ,rectZeileOben=[0, .5, 1, 1] 
   ,rectZeileUnten=[0, 0, 1, .5]
    
   ,dateFormat='%y.%m.%d: %H:%M:%S' # can be a list
   ,bysecond=None #[0,15,30,45] # can be a list
   ,byminute=None # can be a list    
   ,byhour=None

   ,figTitle='' #!
   ,figSave=False #!
    
   ,sectionTitles=[] #  list of section titles to be used    
   ,sectionTexts=[] #  list of section texts to be used    
   ,sectionTitlesLDS=None #  list of section titles to be used    
   ,sectionTextsLDS=None #  list of section texts to be used    

   ,vLinesX=[] # plotted in each HYD section if X-time fits
   ,hLinesY=[] # plotted in each HYD section 
   ,vAreasX=[] # for each HYD section a list of areas to highlight i.e. [[(timeStartAusschnittDruck,timeEndAusschnittDruck),...],...]
   ,vLinesXLDS=None # plotted in each LDS section if X-time fits   
   ,vAreasXLDS=None # for each LDS section a list of areas to highlight i.e. [[(timeStartAusschnittDruck,timeEndAusschnittDruck),...],...]
   ,vLinesXColor='gray'
   ,vAreasXColor='whitesmoke'
   ,vLinesXColorLDS=None
   ,vAreasXColorLDS=None

   ,yTwinedAxesPosDeltaHPStart=-0.0125 #: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche
   ,yTwinedAxesPosDeltaHP=-0.0875 #: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche    
    
   ,ySpanMin=0.9     
    
   ,plotLegend=True # interpretiert fuer diese Funktion; Inverse gilt fuer pltLDSErgVec selbst
   ,plotLegend1stOnly=True

   ,legendLoc='best'
   ,legendFramealpha=.2
   ,legendFacecolor='white'     
        
   # --- Args Fct. HYD ---:
   ,TCsLDSIn=pd.DataFrame() # es werden nur die aDct-definierten geplottet
   ,TCsOPC=pd.DataFrame() # es werden nur die aDctOPC-definierten geplottet
   # der Schluessel in den vorstehenden Dcts ist die ID (der Spaltenname) in den TCs
   ,TCsOPCScenTimeShift=pd.Timedelta('1 hour') 
   ,TCsSIDEvents=pd.DataFrame() # es werden alle Schieberevents geplottet    
   ,TCsSIDEventsTimeShift=pd.Timedelta('1 hour') 
   ,TCsSIDEventsInXlimOnly=True # es werden nur die Spalten geplottet, die in xlim vorkommen und dort mindestens 1x nicht Null sind (sonst sind alle (zumindest in der Legende) dargestellt)
   ,TCsSIDEventsyOffset=.05 # die y-Werte werden ab dem 1. Schieber um je dfTCsSIDEventsyOffset erhöht (damit zeitgleiche Events besser sichtbar werden)
   
   ,QDct={}    
   ,pDct={} 
   ,QDctOPC={} 
   ,pDctOPC={}    
   ,IDPltKey='IDPlt' # Schluesselbezeichner in den vorstehenden 4 Dcts; Wert ist Referenz auf das folgende Layout-Dct und das folgende Fcts-Dct; Werte muessen eindeutig sein
   
   ,attrsDct=attrsDct
   
   ,fctsDct={} 
         
   ,plotRTTM=True

   # p y-Achse
   ,ylimp=ylimpD  #wenn undef., dann min/max 
   ,ylimpxlim=False #wenn Wahr und ylim undef., dann wird xlim beruecksichtigt bei min/max 
   ,yticksp=None #[0,50,100] #wenn undef., dann aus ylimp
   ,ylabelp='[bar]'
   
   # Q y-Achse
   ,ylimQ=ylimQD 
   ,ylimQxlim=False 
   ,yticksQ=None 
   ,ylabelQ='[Nm³/h]'

    # 3. Achse
   ,ylim3rd=ylim3rdD
   ,yticks3rd=yticks3rdD
   
   ,yGridSteps=yGridStepsD     

   # SchieberEvents

   ,pSIDEvents=pSIDEvents
   # ausgewertet werden: colRegExSchieberID (um welchen Schieber geht es), colRegExMiddle (Befehl oder Zustand) und colRegExEventID (welcher Befehl bzw. Zustand) 
   # die Befehle bzw. Zustaende (die Auspraegungen von colRegExEventID) muessen nachf. def. sein um den Marker (des Befehls bzw. des Zustandes) zu definieren
   ,eventCCmds=eventCCmds
   ,eventCStats=eventCStats
   ,valRegExMiddleCmds=valRegExMiddleCmds
  
   # es muessen soviele Farben definiert sein wie Schieber
   ,baseColorsDef=baseColorsSchieber                                                             
   ,markerDef=markerDefSchieber     
    
   # --- Args Fct. LDS ---:    
    
   ,dfSegReprVec=pd.DataFrame() 
   ,dfDruckReprVec=pd.DataFrame() 
        
   ,ylimAL=ylimALD
   ,yticksAL=yticksALD 

   ,ylimR=ylimRD  #can be a list #None #(-10,10) #wenn undef., dann min/max dfSegReprVec 
   ,ylimRxlim=False # can be a list #wenn Wahr und ylimR undef. (None), dann wird xlim beruecksichtigt bei min/max dfSegReprVec
   ,yticksR=yticksRD  # can be a list of lists #[0,2,4,10,15,30,40]  #wenn undef. (None), dann aus ylimR; matplotlib "vergrößert" mit dem Setzen von yTicks ein ebenfalls gesetztes ylim wenn die Ticks außerhalb des ylims liegen

    # dito Beschl.
   ,ylimAC=ylimACD 
   ,ylimACxlim=False 
   ,yticksAC=yticksACD 

   ,attrsDctLDS=attrsDctLDS

   ,plotLPRate=True
   ,plotR2FillSeg=True 
   ,plotR2FillDruck=True 
   ,plotAC=True
   ,plotACCLimits=True

   ,highlightAreas=True 

   ,Seg_Highlight_Color='cyan'
   ,Seg_Highlight_Alpha=.1     
   ,Seg_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False      
   ,Seg_HighlightError_Color='peru'
   ,Seg_Highlight_Alpha_Error=.3     
   ,Seg_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False   

   ,Druck_Highlight_Color='cyan'
   ,Druck_Highlight_Alpha=.1
   ,Druck_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False  
   ,Druck_HighlightError_Color='peru'
   ,Druck_Highlight_Alpha_Error=.3
   ,Druck_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False      
   
   # fcts to apply
   ,fcts={'QM_AV':lambda x: x*1.6/100.
          #,'TIMER_AV':lambda x: x*10
          ,'AM_AV':lambda x: x*100
           }
   
   ,plotTV=True
   #,plotTVTimerFct=None 
   #,plotTVAmFct=lambda x: x*100 
   ,plotTVAmLabel=plotTVAmLabelD
   ,ylimTV=ylimTVD
   ,yticksTV=yticksTVD  

   ,plotDPDT=True
   ,plotSB_S=True
    
):
    
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:

        fig=plt.gcf()

        if orientation=='landscape':
            # oben HYD unten LDS
            gsHYD = gridspec.GridSpec(1,len(xlims),figure=fig)
            axLstHYD=[fig.add_subplot(gsHYD[idx]) for idx in np.arange(gsHYD.ncols)]    
        
            gsLDS = gridspec.GridSpec(1,len(xlims),figure=fig)
            axLstLDS=[fig.add_subplot(gsLDS[idx]) for idx in np.arange(gsLDS.ncols)]            
        
        else:
            # links HYD rechts LDS
            gsHYD = gridspec.GridSpec(len(xlims),1,figure=fig)
            axLstHYD=[fig.add_subplot(gsHYD[idx]) for idx in np.arange(gsHYD.nrows)]     
        
            gsLDS = gridspec.GridSpec(len(xlims),1,figure=fig)
            axLstLDS=[fig.add_subplot(gsLDS[idx]) for idx in np.arange(gsLDS.nrows)]     

        pltLDSpQAndEventsResults=plotTimespansHYD(               
                axLst=axLstHYD
               ,xlims=xlims

               ,figTitle=figTitle # ''
               ,figSave=figSave # False     

               ,sectionTitles=sectionTitles
               ,sectionTexts=sectionTexts

               ,vLinesX=vLinesX 
               ,hLinesY=hLinesY     
               ,vAreasX=vAreasX
               ,vLinesXColor=vLinesXColor
               ,vAreasXColor=vAreasXColor

               ,plotLegend=plotLegend
               ,plotLegend1stOnly=plotLegend1stOnly

               # --- Args Fct. ---:

               ,dfTCsLDSIn=TCsLDSIn
               ,dfTCsOPC=TCsOPC
               ,dfTCsOPCScenTimeShift=TCsOPCScenTimeShift

               ,dfTCsSIDEvents=TCsSIDEvents
               ,dfTCsSIDEventsTimeShift=TCsSIDEventsTimeShift
               ,dfTCsSIDEventsInXlimOnly=TCsSIDEventsInXlimOnly

               ,QDct=QDct
               ,pDct=pDct
               ,QDctOPC=QDctOPC
               ,pDctOPC=pDctOPC 
               ,attrsDct=attrsDct  

               ,fctsDct=fctsDct

               ,dateFormat=dateFormat
               ,bysecond=bysecond
               ,byminute=byminute
               ,byhour=byhour

               ,plotRTTM=plotRTTM

               ,ylimp=ylimp
               ,ylabelp=ylabelp
               ,yticksp=yticksp

               ,ylimQ=ylimQ
               ,yticksQ=yticksQ

               ,yGridSteps=yGridSteps

               ,ylim3rd=ylim3rd
               ,yticks3rd=yticks3rd

            )
    
        if orientation=='landscape':
            # oben HYD unten LDS
            gsHYD.tight_layout(fig, pad=pad,h_pad=h_pad,w_pad=w_pad, rect=rectZeileOben)
        else:
            # links HYD rechts LDS
            gsHYD.tight_layout(fig, pad=pad,h_pad=h_pad,w_pad=w_pad, rect=rectSpalteLinks)
    
        if sectionTitlesLDS==None:
            sectionTitlesLDS=sectionTitles
        if sectionTextsLDS==None:
            sectionTextsLDS=sectionTexts

        if vLinesXLDS==None:
            vLinesXLDS=vLinesX
        if vAreasXLDS==None:
            vAreasXLDS=vAreasX

        if vLinesXColorLDS==None:
            vLinesXColorLDS=vLinesXColor
        if vAreasXColorLDS==None:            
            vAreasXColorLDS=vAreasXColor

        pltLDSErgVecResults=plotTimespansLDS(    
            
                axLst=axLstLDS         
               ,xlims=xlims

               ,figTitle=figTitle # ''
               ,figSave=figSave # False     

               ,sectionTitles=sectionTitlesLDS
               ,sectionTexts=sectionTextsLDS

               ,vLinesX=vLinesXLDS        
               ,vAreasX=vAreasXLDS
               ,vLinesXColor=vLinesXColorLDS
               ,vAreasXColor=vAreasXColorLDS

               ,plotLegend=plotLegend
               ,plotLegend1stOnly=plotLegend1stOnly

               # --- Args Fct. ---:

               ,dfSegReprVec=dfSegReprVec 
               ,dfDruckReprVec=dfDruckReprVec   

               ,dateFormat=dateFormat
               ,bysecond=bysecond
               ,byminute=byminute
               ,byhour=byhour

               ,ylimR=ylimR 
               ,ylimRxlim=ylimRxlim
               ,yticksR=yticksR

               ,plotLPRate=plotLPRate
               ,plotR2FillSeg=plotR2FillSeg
               ,plotR2FillDruck=plotR2FillDruck

               # fcts to apply
               ,fcts=fcts

               ,plotAC=plotAC
               ,ylimAC=ylimAC 
               ,ylimACxlim=ylimACxlim
               ,yticksAC=yticksAC 

               ,plotTV=plotTV
               #,plotTVTimerFct=plotTVTimerFct 
               #,plotTVAmFct=plotTVAmFct 
               ,plotTVAmLabel=plotTVAmLabel
               ,ylimTV=ylimTV
               ,yticksTV=yticksTV    

               ,plotDPDT=plotDPDT
               ,plotSB_S=plotSB_S

        )  
    

        # wenn weniger als 5 Achsen geplottet werden stimmt der erste Wert von rectSpalteRechts nicht
        #(axes,lines)=pltLDSErgVecResults[0]
#
#        numOfYAxes=len(axes)
        #corFac=5-numOfYAxes
        #rectSpalteRechtsCor=rectSpalteRechts #[0.325, 0, 1, 1] 
        #rectSpalteRechtsCor[0]=rectSpalteRechtsCor[0]+0.06*corFac


        if orientation=='landscape':
            # oben HYD unten LDS
            gsLDS.tight_layout(fig, pad=pad,h_pad=h_pad,w_pad=w_pad, rect=rectZeileUnten)
        else:
            # links HYD rechts LDS
            gsLDS.tight_layout(fig, pad=pad,h_pad=h_pad,w_pad=w_pad, rect=rectSpalteRechts)
        
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return gsHYD,gsLDS,pltLDSpQAndEventsResults,pltLDSErgVecResults

def plotTimespansHYD(    
    axLst # list of axes to be used    
   ,xlims # list of sections    

   ,figTitle='' # the title of the plot; will be extended by min. and max. time calculated over all sections; will be also the pdf and png fileName
   ,figSave=False #True # creates pdf and png
   ,sectionTitles=[] #  list of section titles to be used    
   ,sectionTexts=[] #  list of section texts to be used    
   ,vLinesX=[] # plotted in each section if X-time fits
   ,hLinesY=[] # plotted in each section 
   ,vAreasX=[] # for each section a list of areas to highlight i.e. [[(timeStartAusschnittDruck,timeEndAusschnittDruck),...],...]
   ,vLinesXColor='gray'
   ,vAreasXColor='whitesmoke'

   # --- Args Fct. ---:

   ,dfTCsLDSIn=pd.DataFrame() # es werden nur die aDct-definierten geplottet
   ,dfTCsOPC=pd.DataFrame() # es werden nur die aDctOPC-definierten geplottet
   # der Schluessel in den vorstehenden Dcts ist die ID (der Spaltenname) in den TCs
   ,dfTCsOPCScenTimeShift=pd.Timedelta('1 hour') 
   ,dfTCsSIDEvents=pd.DataFrame() # es werden alle Schieberevents geplottet    
   ,dfTCsSIDEventsTimeShift=pd.Timedelta('1 hour') 
   ,dfTCsSIDEventsInXlimOnly=True # es werden nur die Spalten geplottet, die in xlim vorkommen und dort mindestens 1x nicht Null sind (sonst sind alle (zumindest in der Legende) dargestellt)
   ,dfTCsSIDEventsyOffset=.05 # die y-Werte werden ab dem 1. Schieber um je dfTCsSIDEventsyOffset erhöht (damit zeitgleiche Events besser sichtbar werden)
   
   ,QDct={ # Exanple
       'Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value':{'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
       ,'Objects.FBG_MESSW.6_TUD_39_FT_01.In.MW.value':{'IDPlt':'Q Snk','RTTM':'IMDI.Objects.FBG_MESSW.6_TUD_39_FT_01.In.MW.value'}
    }
   
   ,pDct={ # Example
       'Objects.FBG_HPS_M.6_KED_39_PTI_01_E.In.MW.value':{'IDPlt':'p Src'}
       ,'Objects.FBG_HPS_M.6_TUD_39_PTI_01_E.In.MW.value':{'IDPlt':'p Snk'}
       ,'Objects.FBG_HPS_M.6_EL1_39_PTI_01_E.In.MW.value':{'IDPlt':'p ISrc 1'}
       ,'Objects.FBG_HPS_M.6_EL1_39_PTI_02_E.In.MW.value':{'IDPlt':'p ISnk 2'}    
    }

   ,QDctOPC={ # Exanple
       'Objects.FBG_MESSW.6_EL1_39_FT_01.In.MW.value':{'IDPlt':'Q xSrc 1'}       
    }

   ,pDctOPC={} 
   
   ,IDPltKey='IDPlt' # Schluesselbezeichner in den vorstehenden 4 Dcts; Wert ist Referenz auf das folgende Layout-Dct und das folgende Fcts-Dct; Werte muessen eindeutig sein
   
   ,attrsDct=attrsDct 
   
   ,fctsDct={} # a Dct with Fcts
          
   ,dateFormat='%y.%m.%d: %H:%M:%S' # can be a list
   ,bysecond=None#[0,15,30,45] # can be a list
   ,byminute=None # can be a list
   ,byhour=None
   
   ,yTwinedAxesPosDeltaHPStart=-0.0125 #: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche
   ,yTwinedAxesPosDeltaHP=-0.0875 #: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche
   
   ,plotRTTM=True 

   # p y-Achse
   ,ylimp=ylimpD   #wenn undef., dann min/max 
   ,ylimpxlim=False #wenn Wahr und ylim undef., dann wird xlim beruecksichtigt bei min/max 
   ,yticksp=None #[0,50,100] #wenn undef., dann aus ylimp
   ,ylabelp='[bar]'
   
   # Q y-Achse
   ,ylimQ=ylimQD
   ,ylimQxlim=False 
   ,yticksQ=None 
   ,ylabelQ='[Nm³/h]'

    # 3. Achse
    ,ylim3rd=ylim3rdD
    ,yticks3rd=yticks3rdD
   
    ,yGridSteps=yGridStepsD      
    ,ySpanMin=0.9 # wenn ylim undef. vermeidet dieses Maß eine y-Achse mit einer zu kleinen Differenz zwischen min/max

    ,plotLegend=True # interpretiert fuer diese Funktion; Inverse gilt fuer pltLDSpQAndEvents selbst
    ,plotLegend1stOnly=True # diese Funktion plottet wenn plotLegend=True die Legende nur im ersten Plot
    ,legendLoc='best'
    ,legendFramealpha=.2
    ,legendFacecolor='white' 

    # SchieberEvents

    ,pSIDEvents=pSIDEvents
    # ausgewertet werden: colRegExSchieberID (um welchen Schieber geht es), colRegExMiddle (Befehl oder Zustand) und colRegExEventID (welcher Befehl bzw. Zustand) 
    # die Befehle bzw. Zustaende (die Auspraegungen von colRegExEventID) muessen nachf. def. sein um den Marker (des Befehls bzw. des Zustandes) zu definieren
    ,eventCCmds=eventCCmds
    ,eventCStats=eventCStats
    ,valRegExMiddleCmds=valRegExMiddleCmds # colRegExMiddle-Auspraegung fuer Befehle (==> eventCCmds)
    # es muessen soviele Farben definiert sein wie Schieber
    ,baseColorsDef=baseColorsSchieber                                                             
    ,markerDef=markerDefSchieber    
   ):

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    
    # plots pltLDSpQAndEvents-Sections 
    
    # returns a Lst of pltLDSpQAndEvents-Results, a Lst of (axes,lines,scatters)

    try:
    
        if sectionTitles==[] or sectionTitles==None:
            sectionTitles=len(xlims)*['a plotTimespansHYD sectionTitle Praefix']

        if not isinstance(sectionTitles, list):            
            logger.warning("{0:s}sectionTitles muss eine Liste von strings sein.".format(logStr)) 
            sectionTitles=len(xlims)*['a plotTimespansHYD sectionTitle Praefix']

        if len(sectionTitles)!=len(xlims):            
            logger.debug("{0:s}sectionTitles muss dieselbe Laenge haben wie xlims.".format(logStr)) 
            if len(sectionTitles) == 1:
                sectionTitles=len(xlims)*[sectionTitles[0]]
            else:
                sectionTitles=len(xlims)*['a plotTimespansHYD sectionTitle Praefix']

        if sectionTexts==[] or sectionTexts==None:
            sectionTexts=len(xlims)*['']

        if not isinstance(sectionTexts, list):            
            logger.warning("{0:s}sectionTexts muss eine Liste von strings sein.".format(logStr)) 
            sectionTexts=len(xlims)*['']

        if len(sectionTexts)!=len(xlims):            
            logger.warning("{0:s}sectionTexts muss dieselbe Laenge haben wie xlims.".format(logStr)) 
            sectionTexts=len(xlims)*['']

        if plotLegend:
            plotLegendFct=False
        else:
            plotLegendFct=True
             
        pltLDSpQAndEventsResults=[]
        for idx,xlim in enumerate(xlims):   
                             
            ax = axLst[idx]

            if isinstance(dateFormat, list):
                dateFormatIdx=dateFormat[idx]
            else:
                dateFormatIdx=dateFormat

            bysecondIdx=bysecond
            if isinstance(bysecond, list):
                if any(isinstance(el, list) for el in bysecond):               
                    bysecondIdx=bysecond[idx]                        

            byminuteIdx=byminute
            if isinstance(byminute, list):
                if any(isinstance(el, list) for el in byminute):              
                    byminuteIdx=byminute[idx]     

            byhourIdx=byhour
            if isinstance(byhour, list):
                if any(isinstance(el, list) for el in byhour):              
                    byhourIdx=byhour[idx]    

            (axes,lines,scatters)=pltLDSpQAndEvents(
                 ax
            
                ,dfTCsLDSIn=dfTCsLDSIn
                ,dfTCsOPC=dfTCsOPC
                ,dfTCsOPCScenTimeShift=dfTCsOPCScenTimeShift
            
                ,dfTCsSIDEvents=dfTCsSIDEvents    
                ,dfTCsSIDEventsTimeShift=dfTCsSIDEventsTimeShift
                ,dfTCsSIDEventsInXlimOnly=dfTCsSIDEventsInXlimOnly
                ,dfTCsSIDEventsyOffset=dfTCsSIDEventsyOffset
                        
                ,QDct=QDct
                ,pDct=pDct
                ,QDctOPC=QDctOPC
                ,pDctOPC=pDctOPC
                ,attrsDct=attrsDct    
            
                ,fctsDct=fctsDct

                ,xlim=xlim

                ,dateFormat=dateFormatIdx
                ,bysecond=bysecondIdx
                ,byminute=byminuteIdx
                ,byhour=byhourIdx

                ,plotRTTM=plotRTTM

                ,ylimp=ylimp
                ,ylabelp=ylabelp
                ,yticksp=yticksp

                ,ylimQ=ylimQ
                ,yticksQ=yticksQ    

                # 3. Achse
                ,ylim3rd=ylim3rd
                ,yticks3rd=yticks3rd

                ,yGridSteps=yGridSteps

                ,plotLegend=plotLegendFct
            
                ,baseColorsDef=baseColorsDef
                )
            pltLDSpQAndEventsResults.append((axes,lines,scatters))     
            
            sectionText=sectionTexts[idx]
            ax.text(  
                0.5, 0.5,
                sectionText,
                ha='center', va='top',
                transform=ax.transAxes
            )

            (timeStart,timeEnd)=xlim
            sectionTitleSingle="{:s}: Plot Nr. {:d} - Zeitspanne: {:s}".format(sectionTitles[idx],idx+1,str(timeEnd-timeStart)).replace('days','Tage')  
            ax.set_title(sectionTitleSingle) 

            for vLineX in vLinesX:        
                if vLineX >= timeStart and vLineX <= timeEnd:
                    ax.axvline(x=vLineX,ymin=0, ymax=1, color=vLinesXColor,ls=linestyle_tuple[11][1])
                
            for hLineY in hLinesY:      
                ax.axhline(y=hLineY,xmin=0, xmax=1,color='gray',ls=linestyle_tuple[11][1])         

            if len(vAreasX) == len(xlims):
                vAreasXSection=vAreasX[idx]
                if vAreasXSection==[] or vAreasXSection==None:
                    pass
                else:
                    for vArea in vAreasXSection:
                        ax.axvspan(vArea[0], vArea[1], alpha=0.6, color=vAreasXColor)
            else:
                if len(vAreasX)>0:
                    logger.warning("{0:s}vAreasX muss dieselbe Laenge haben wie xlims.".format(logStr)) 
           
            # Legend
            if plotLegend:
                legendHorizontalPos='center'
                if len(xlims)>1:
                    if idx in [0,2,4]: # Anfahren ...
                        legendHorizontalPos='right'
                    elif idx in [1,3,5]: # Abfahren ...
                        legendHorizontalPos='left'   

                if plotLegend1stOnly:
                    legendHorizontalPos='center' # wenn nur 1x Legende dann Mitte

                if plotLegend1stOnly and idx>0:
                    pass
                else:   
                    patterBCp='^p S[rc|nk]'
                    patterBCQ='^Q S[rc|nk]'
                    patterBCpQ='^[p|Q] S[rc|nk]'

                    linesp=[line for line in lines if re.search(patterBCp,line) != None]
                    linesQ=[line for line in lines if re.search(patterBCQ,line) != None]

                    linespTxt=tuple([lines[line] for line in linesp])                                                            
                    linesQTxt=tuple([lines[line] for line in linesQ])
                    
                    moreLines=[line for line in lines if re.search(patterBCpQ,line) == None]

                    moreLinesp=[line for line in moreLines if re.search('^p',line) != None]
                    moreLinesQ=[line for line in moreLines if re.search('^Q',line) != None]

                    moreLinespTxt=tuple([lines[line] for line in moreLinesp])                                                            
                    moreLinesQTxt=tuple([lines[line] for line in moreLinesQ])

                    axes['p'].add_artist(axes['p'].legend(
                                     linespTxt+moreLinespTxt
                                    ,linesp+moreLinesp
                                    ,loc='upper '+legendHorizontalPos
                                    ,framealpha=legendFramealpha
                                    ,facecolor=legendFacecolor
                                    ))
                    axes['Q'].add_artist(axes['Q'].legend(
                                     linesQTxt+moreLinesQTxt
                                    ,linesQ+moreLinesQ
                                    ,loc='lower '+legendHorizontalPos
                                    ,framealpha=legendFramealpha
                                    ,facecolor=legendFacecolor
                                    ))

                    if 'SID' in axes.keys() and len(scatters)>0:
                            if legendHorizontalPos == 'center':
                                legendHorizontalPosAct=''
                            else:
                                legendHorizontalPosAct=' '+legendHorizontalPos
                            axes['SID'].legend(loc='center'+legendHorizontalPosAct
                                    ,framealpha=legendFramealpha
                                    ,facecolor=legendFacecolor)        
                        
        # Titel
        tMin=xlims[0][0]
        tMax=xlims[-1][1]
        for tPair in xlims:
            (t1,t2)=tPair
            if t1 < tMin:
                tMin=t1
            if t2>tMax:
                tMax=t2

        if figTitle not in ['',None]:                      
            figTitle="{:s} - {:s} - {:s}".format(figTitle,str(tMin),str(tMax)).replace(':',' ')
            fig=plt.gcf()
            fig.suptitle(figTitle)   

        # speichern?!
        if figSave:
            fig.tight_layout(pad=2.) # gs.tight_layout(fig,pad=2.)

            plt.savefig(figTitle+'.png')
            plt.savefig(figTitle+'.pdf') 

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return pltLDSpQAndEventsResults


def plotTimespansLDS(    
     axLst # list of axes to be used      
    ,xlims # list of sections    

    ,figTitle='' # the title of the plot; will be extended by min. and max. time calculated over all sections; will be also the pdf and png fileName
    ,figSave=False #True # creates pdf and png
    ,sectionTitles=[] #  list of section titles to be used    
    ,sectionTexts=[] #  list of section texts to be used    
    ,vLinesX=[] # plotted in each section if X-time fits    
    ,vAreasX=[] # for each section a list of areas to highlight i.e. [[(timeStartAusschnittDruck,timeEndAusschnittDruck),...],...]
    ,vLinesXColor='gray'
    ,vAreasXColor='whitesmoke'

   # --- Args Fct. ---:     
    ,dfSegReprVec=pd.DataFrame() 
    ,dfDruckReprVec=pd.DataFrame() 
    
    #,xlim=None    
    ,dateFormat='%y.%m.%d: %H:%M:%S'  # can be a list
    ,bysecond=None #[0,15,30,45]  # can be a list
    ,byminute=None  # can be a list
    ,byhour=None
    
    ,ylimAL=ylimALD
    ,yticksAL=yticksALD 

    ,yTwinedAxesPosDeltaHPStart=-0.0125 
    ,yTwinedAxesPosDeltaHP=-0.0875 

    ,ylimR=ylimRD # can be a list
    ,ylimRxlim=False # can be a list
    ,yticksR=yticksRD # can be a list

    # dito Beschl.
    ,ylimAC=ylimACD
    ,ylimACxlim=False 
    ,yticksAC=yticksACD     

    ,ySpanMin=0.9 

    ,plotLegend=True # interpretiert fuer diese Funktion; Inverse gilt fuer pltLDSErgVec selbst
    ,plotLegend1stOnly=True # diese Funktion plottet wenn plotLegend=True die Legende nur im ersten Plot

    ,legendLoc='best'
    ,legendFramealpha=.2
    ,legendFacecolor='white' 

    ,attrsDctLDS=attrsDctLDS

    ,plotLPRate=True
    ,plotR2FillSeg=True 
    ,plotR2FillDruck=True 
    ,plotAC=True
    ,plotACCLimits=True

    ,highlightAreas=True 

    ,Seg_Highlight_Color='cyan'
    ,Seg_Highlight_Alpha=.1     
    ,Seg_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False      
    ,Seg_HighlightError_Color='peru'
    ,Seg_Highlight_Alpha_Error=.3     
    ,Seg_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False   

    ,Druck_Highlight_Color='cyan'
    ,Druck_Highlight_Alpha=.1
    ,Druck_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False  
    ,Druck_HighlightError_Color='peru'
    ,Druck_Highlight_Alpha_Error=.3
    ,Druck_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False     
    
     # fcts to apply
    ,fcts={'QM_AV':lambda x: x*1.6/100.
          #,'TIMER_AV':lambda x: x*10
          ,'AM_AV':lambda x: x*100
           }    

    ,plotTV=True
    #,plotTVTimerFct=None 
    #,plotTVAmFct=lambda x: x*100 
    ,plotTVAmLabel=plotTVAmLabelD
    ,ylimTV=ylimTVD
    ,yticksTV=yticksTVD     

    ,plotDPDT=True
    ,plotSB_S=True
):

    # plots pltLDSErgVec-Sections 
    
    # returns a Lst of pltLDSErgVec-Results, a Lst of (axes,lines)

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:    

        if sectionTitles==[] or sectionTitles ==None:
            sectionTitles=len(xlims)*['a plotTimespansLDS sectionTitle Praefix']

        if not isinstance(sectionTitles, list):            
            logger.warning("{0:s}sectionTitles muss eine Liste von strings sein.".format(logStr)) 
            sectionTitles=len(xlims)*['a plotTimespansLDS sectionTitle Praefix']

        if len(sectionTitles)!=len(xlims):            
            logger.debug("{0:s}sectionTitles muss dieselbe Laenge haben wie xlims.".format(logStr)) 
            if len(sectionTitles) == 1:
                sectionTitles=len(xlims)*[sectionTitles[0]]
            else:
                sectionTitles=len(xlims)*['a plotTimespansLDS sectionTitle Praefix']

        if sectionTexts==[] or sectionTexts==None:
            sectionTexts=len(xlims)*['']

        if not isinstance(sectionTexts, list):            
            logger.warning("{0:s}sectionTexts muss eine Liste von strings sein.".format(logStr)) 
            sectionTexts=len(xlims)*['']

        if len(sectionTexts)!=len(xlims):            
            logger.warning("{0:s}sectionTexts muss dieselbe Laenge haben wie xlims.".format(logStr)) 
            sectionTexts=len(xlims)*['']
        
        if plotLegend:
           plotLegendFct=False
        else:
           plotLegendFct=True

        pltLDSErgVecResults=[]
        for idx,xlim in enumerate(xlims):   
                             
            ax = axLst[idx]

            if isinstance(dateFormat, list):
                dateFormatIdx=dateFormat[idx]
            else:
                dateFormatIdx=dateFormat

            bysecondIdx=bysecond
            if isinstance(bysecond, list):
                if any(isinstance(el, list) for el in bysecond):               
                    bysecondIdx=bysecond[idx]                        

            byminuteIdx=byminute
            if isinstance(byminute, list):
                if any(isinstance(el, list) for el in byminute):              
                    byminuteIdx=byminute[idx]   
                    
            byhourIdx=byhour
            if isinstance(byhour, list):
                if any(isinstance(el, list) for el in byhour):              
                    byhourIdx=byhour[idx]    
            
            ylimRIdx=ylimR
            if isinstance(ylimR, list):
                ylimRIdx=ylimR[idx]

            ylimRxlimIdx=ylimRxlim
            if isinstance(ylimRxlim, list):
                ylimRxlimIdx=ylimRxlim[idx]

            yticksRIdx=yticksR
            if isinstance(yticksR, list):
                if any(isinstance(el, list) for el in yticksR):               
                    yticksRIdx=yticksR[idx]                  

        
            (axes,lines)=pltLDSErgVec(
                     ax
                    ,dfSegReprVec=dfSegReprVec
                    ,dfDruckReprVec=dfDruckReprVec
                    ,xlim=xlims[idx]    
                      
                    ,dateFormat=dateFormatIdx
                    ,bysecond=bysecondIdx
                    ,byminute=byminuteIdx
                    ,byhour=byhourIdx

                    ,ylimAL=ylimAL
                    ,yticksAL=yticksAL

                    ,yTwinedAxesPosDeltaHPStart=yTwinedAxesPosDeltaHPStart
                    ,yTwinedAxesPosDeltaHP=yTwinedAxesPosDeltaHP

                    ,ylimR=ylimRIdx
                    ,ylimRxlim=ylimRxlimIdx
                    ,yticksR=yticksRIdx
                
                    ,ylimAC=ylimAC 
                    ,ylimACxlim=ylimACxlim 
                    ,yticksAC=yticksAC 

                    ,ySpanMin=ySpanMin

                    ,plotLegend=plotLegendFct
                    ,legendLoc=legendLoc
                    ,legendFramealpha=legendFramealpha
                    ,legendFacecolor=legendFacecolor 

                    ,attrsDctLDS=attrsDctLDS         
                    
                    ,plotLPRate=plotLPRate                  
                    ,plotR2FillSeg=plotR2FillSeg
                    ,plotR2FillDruck=plotR2FillDruck                   
                    ,plotAC=plotAC     
                    ,plotACCLimits=plotACCLimits

                    ,highlightAreas=highlightAreas 

                    ,Seg_Highlight_Color=Seg_Highlight_Color
                    ,Seg_Highlight_Alpha=Seg_Highlight_Alpha     
                    ,Seg_Highlight_Fct=Seg_Highlight_Fct   
                    ,Seg_HighlightError_Color=Seg_HighlightError_Color
                    ,Seg_Highlight_Alpha_Error=Seg_Highlight_Alpha_Error #     
                    ,Seg_HighlightError_Fct=Seg_HighlightError_Fct   

                    ,Druck_Highlight_Color=Druck_Highlight_Color
                    ,Druck_Highlight_Alpha=Druck_Highlight_Alpha
                    ,Druck_Highlight_Fct=Druck_Highlight_Fct  
                    ,Druck_HighlightError_Color=Druck_HighlightError_Color
                    ,Druck_Highlight_Alpha_Error=Druck_Highlight_Alpha_Error #     
                    ,Druck_HighlightError_Fct=Druck_HighlightError_Fct       
                    
                    # fcts to apply
                    ,fcts=fcts
                    
                    ,plotTV=plotTV
                    #,plotTVTimerFct=plotTVTimerFct 
                    #,plotTVAmFct=plotTVAmFct 
                    ,plotTVAmLabel=plotTVAmLabel
                    ,ylimTV=ylimTV
                    ,yticksTV=yticksTV            

                    ,plotDPDT=plotDPDT
                    ,plotSB_S=plotSB_S
                    )    
            pltLDSErgVecResults.append((axes,lines))

            sectionText=sectionTexts[idx]
            ax.text(  
                0.5, 0.5,
                sectionText,
                ha='center', va='top',
                transform=ax.transAxes
            )
        
            (timeStart,timeEnd)=xlim                
            sectionTitleSingle="{:s}: Plot Nr. {:d} - Zeitspanne: {:s}".format(sectionTitles[idx],idx+1,str(timeEnd-timeStart)).replace('days','Tage')  
            ax.set_title(sectionTitleSingle)         
        
            for vLineX in vLinesX:        
                if vLineX >= timeStart and vLineX <= timeEnd:
                    ax.axvline(x=vLineX,ymin=0, ymax=1, color=vLinesXColor,ls=linestyle_tuple[11][1])     
                
            if len(vAreasX) == len(xlims):
                vAreasXSection=vAreasX[idx]
                if vAreasXSection==[] or vAreasXSection==None:
                    pass
                else:
                    for vArea in vAreasXSection:
                        ax.axvspan(vArea[0], vArea[1], alpha=0.6, color=vAreasXColor)
            else:
                if len(vAreasX)>0:
                    logger.warning("{0:s}vAreasX muss dieselbe Laenge haben wie xlims.".format(logStr))                
                                
            # Legend
            if plotLegend:
                legendHorizontalPos='center'
                if len(xlims)>1:
                    if idx in [0,2,4]: # Anfahren ...
                        legendHorizontalPos='right'
                    elif idx in [1,3,5]: # Abfahren ...
                        legendHorizontalPos='left'                    

                if plotLegend1stOnly and idx>0:
                    pass
                else:                
                    if not dfSegReprVec.empty:
                        patternSeg='Seg$'
                        axes['A'].add_artist(axes['A'].legend(
                                    tuple([lines[line] for line in lines if re.search(patternSeg,line) != None]) 
                                   ,tuple([line for line in lines if re.search(patternSeg,line) != None]) 
                                   ,loc='upper '+legendHorizontalPos
                                   ,framealpha=legendFramealpha
                                   ,facecolor=legendFacecolor
                                    ))         
                    if not dfDruckReprVec.empty:
                        patternDruck='Drk$'
                        axes['A'].add_artist(axes['A'].legend(
                                    tuple([lines[line] for line in lines if re.search(patternDruck,line) != None]) 
                                   ,tuple([line for line in lines if re.search(patternDruck,line) != None]) 
                                   ,loc='lower '+legendHorizontalPos
                                   ,framealpha=legendFramealpha
                                   ,facecolor=legendFacecolor
                                    ))                   
        
        # Titel
        tMin=xlims[0][0]
        tMax=xlims[-1][1]
        for tPair in xlims:
            (t1,t2)=tPair
            if t1 < tMin:
                tMin=t1
            if t2>tMax:
                tMax=t2

        if figTitle not in ['',None]:                     
            figTitle="{:s} - {:s} - {:s}".format(figTitle,str(tMin),str(tMax)).replace(':',' ')
            fig=plt.gcf()
            fig.suptitle(figTitle)   

        # speichern?!
        if figSave:
            fig.tight_layout(pad=2.) # gs.tight_layout(fig,pad=2.)

            plt.savefig(figTitle+'.png')
            plt.savefig(figTitle+'.pdf') 
                     
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return pltLDSErgVecResults    


def pltLDSpQAndEvents(
     ax
    ,dfTCsLDSIn # es werden nur die aDct-definierten geplottet
    ,dfTCsOPC=pd.DataFrame() # es werden nur die aDctOPC-definierten geplottet
    # der Schluessel in den vorgenannten Dcts ist die ID (der Spaltenname) in den TCs
    ,dfTCsOPCScenTimeShift=pd.Timedelta('1 hour') 

    ,dfTCsSIDEvents=pd.DataFrame() 
    ,dfTCsSIDEventsTimeShift=pd.Timedelta('1 hour') 
    ,dfTCsSIDEventsInXlimOnly=True # es werden nur die Spalten geplottet, die in xlim vorkommen und dort mindestens 1x nicht Null sind (sonst sind alle (zumindest in der Legende) dargestellt)
    ,dfTCsSIDEventsyOffset=.05 # die y-Werte werden ab dem 1. Schieber um je dfTCsSIDEventsyOffset erhöht (damit zeitgleiche Events besser sichtbar werden)
    
    ,QDct={ # Exanple
        'Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value':{'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
        ,'Objects.FBG_MESSW.6_TUD_39_FT_01.In.MW.value':{'IDPlt':'Q Snk','RTTM':'IMDI.Objects.FBG_MESSW.6_TUD_39_FT_01.In.MW.value'}
     }
    
    ,pDct={# Example
       'Objects.FBG_HPS_M.6_KED_39_PTI_01_E.In.MW.value':{'IDPlt':'p Src'}
       ,'Objects.FBG_HPS_M.6_TUD_39_PTI_01_E.In.MW.value':{'IDPlt':'p Snk'}
       ,'Objects.FBG_HPS_M.6_EL1_39_PTI_01_E.In.MW.value':{'IDPlt':'p ISrc 1'}
       ,'Objects.FBG_HPS_M.6_EL1_39_PTI_02_E.In.MW.value':{'IDPlt':'p ISnk 2'}    
    }
    ,QDctOPC={ # Exanple
        'Objects.FBG_MESSW.6_EL1_39_FT_01.In.MW.value':{'IDPlt':'Q xSnk 1'}       
     }

    ,pDctOPC={} 
    
    ,IDPltKey='IDPlt' # Schluesselbezeichner in den vorstehenden 4 Dcts; Wert ist Referenz auf das folgende Layout-Dct und das folgende Fcts-Dct; Werte muessen eindeutig sein
    
    ,attrsDct=attrsDct 
     
    ,fctsDct={} # a Dct with Fcts
        
    ,xlim=None    
    ,dateFormat='%y.%m.%d: %H:%M:%S'
    ,bysecond=None #[0,15,30,45]
    ,byminute=None
    ,byhour=None
    
    ,yTwinedAxesPosDeltaHPStart=-0.0125 #: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche
    ,yTwinedAxesPosDeltaHP=-0.0875 #: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche
    
    ,plotRTTM=True # plot RTTM-Echoes; if =='Filter': plot with Filter

    # p y-Achse
    ,ylimp=ylimpD  #wenn undef., dann min/max 
    ,ylimpxlim=False #wenn Wahr und ylim undef., dann wird xlim beruecksichtigt bei min/max 
    ,yticksp=None #wenn undef., dann aus ylimp
    ,ylabelp='[bar]'
    
    # Q y-Achse
    ,ylimQ=ylimQD 
    ,ylimQxlim=False 
    ,yticksQ=None #wenn undef., dann aus ylimQ
    ,ylabelQ='[Nm³/h]'

    # 3. Achse
    ,ylim3rd=ylim3rdD
    ,yticks3rd=yticks3rdD
    
    ,ylabel3rd='Schieber (ZUSTände 0,1,2 jew. + x; Befehle)'

    ,yGridSteps=30 # 0: das y-Gitter besteht dann bei ylimp=ylimQ=yticksp=yticksQ None nur aus min/max (also 1 Gitterabschnitt)     
    ,ySpanMin=0.9 # wenn ylim undef. vermeidet dieses Maß eine y-Achse mit einer zu kleinen Differenz zwischen min/max

    ,plotLegend=True
    ,legendLoc='best'
    ,legendFramealpha=.2
    ,legendFacecolor='white' 

    # SchieberEvents

    ,pSIDEvents=pSIDEvents
    # ausgewertet werden: colRegExSchieberID (um welchen Schieber geht es), colRegExMiddle (Befehl oder Zustand) und colRegExEventID (welcher Befehl bzw. Zustand) 
    # die Befehle bzw. Zustaende (die Auspraegungen von colRegExEventID) muessen nachf. def. sein um den Marker (des Befehls bzw. des Zustandes) zu definieren

    ,eventCCmds=eventCCmds
    ,eventCStats=eventCStats
    ,valRegExMiddleCmds=valRegExMiddleCmds # colRegExMiddle-Auspraegung fuer Befehle (==> eventCCmds)

    # es muessen soviele Farben definiert sein wie Schieber
    ,baseColorsDef=baseColorsSchieber                                                             
    ,markerDef=markerDefSchieber 
    ):
    """
    zeichnet pq-Zeitkurven - ggf. ergaenzt durch Events

    Returns:
        * axes (Dct of axes)
        * lines (Dct of lines)
        * scatters (List of ax.scatter-Results)
    """
   
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    axes={}
    lines={}
    scatters=[]

    try:    
        
            if type(plotRTTM) == str:
                plotRTTMlocal=True
            elif type(plotRTTM) == bool:
                 plotRTTMlocal=plotRTTM

            axes['p']=ax

            # x-Achse ----------------
            if xlim == None:            
                xlimMin=dfTCsLDSIn.index[0]
                xlimMax=dfTCsLDSIn.index[-1]                                
                xlim=(xlimMin,xlimMax)
            (xlimMin,xlimMax)=xlim

            ax.set_xlim(xlim)

            logger.debug("{0:s}dfTCsOPCScenTimeShift: {1:s}".format(logStr,str(dfTCsOPCScenTimeShift))) 

            logger.debug("{0:s}bysecond: {1:s}".format(logStr,str(bysecond))) 
            logger.debug("{0:s}byminute: {1:s}".format(logStr,str(byminute))) 
            logger.debug("{0:s}byhour: {1:s}".format(logStr,str(byhour))) 
                           
            pltHelperX(
             ax
            ,dateFormat=dateFormat
            ,bysecond=bysecond
            ,byminute=byminute
            ,byhour=byhour
            ,yPos=yTwinedAxesPosDeltaHPStart
            )  
                      
            # Eindeutigkeit der IDPlts pruefen
            keys=[]
            keysUneindeutig=[]
            for dct in [QDct,pDct,QDctOPC,pDctOPC]:
                for key, value in dct.items():
                    if IDPltKey in value.keys():
                        IDPltValue=value[IDPltKey]
                        if IDPltValue in keys:                
                            print("IDPlt {:s} bereits vergeben".format(IDPltValue))
                            keysUneindeutig.append(IDPltValue)
                        else:
                            keys.append(IDPltValue)

            # 1. Achse p -----------------------    
            logger.debug("{0:s}{1:s}".format(logStr,'# 1. Achse p'))   
        
            for key, value in pDct.items(): # nur die konfigurierten IDs plotten          
                if key in dfTCsLDSIn.columns: # nur dann, wenn ID als Spalte enthalten 
                    label, linesAct = pltLDSpQHelper(
                        ax
                       ,TCdf=dfTCsLDSIn
                       ,ID=key # Spaltenname
                       ,xDctValue=value # a Dct - i.e. {'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
                       ,xDctAttrs=attrsDct # a Dct with - i.e. {'Q Src':{'color':'red'},...}
                       ,IDPltKey=IDPltKey # Schluesselbezeichner in value   
                       ,IDPltValuePostfix=None
                       ,xDctFcts=fctsDct
                       #,timeShift=pd.Timedelta('1 hour') # pd.Timedelta('0 seconds')
                        )                    
                    lines[label]=linesAct[0]               
                else:
                    logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,key))   

                if 'RTTM' in value.keys():       
                    if value['RTTM'] in dfTCsLDSIn.columns:
                        
                        label, linesAct = pltLDSpQHelper(
                        ax
                       ,TCdf=dfTCsLDSIn
                       ,ID=value['RTTM'] 
                       ,xDctValue=value # a Dct - i.e. {'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
                       ,xDctAttrs=attrsDct 
                       ,IDPltKey=IDPltKey 
                       ,IDPltValuePostfix=' RTTM' 
                       ,xDctFcts=fctsDct
                       #,timeShift=pd.Timedelta('0 hour') #pd.Timedelta('0 seconds')
                        )                    
                        lines[label]=linesAct[0]  

                    else:
                        logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,value['RTTM']))   

            if not dfTCsOPC.empty:   
                logger.debug("{0:s}{1:s}".format(logStr,'# 1. Achse p OPC'))   
                for key, value in pDctOPC.items():   
                    if key in dfTCsOPC.columns:

                        label, linesAct = pltLDSpQHelper(
                        ax  
                       ,TCdf=dfTCsOPC
                       ,ID=key 
                       ,xDctValue=value 
                       ,xDctAttrs=attrsDct
                       ,IDPltKey=IDPltKey 
                       ,IDPltValuePostfix=None
                       ,xDctFcts=fctsDct
                       ,timeShift=dfTCsOPCScenTimeShift
                        )                    
                        lines[label]=linesAct[0]   

                    else:
                        logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,key))                                        
                                                                                                           
            ylimp,yticksp=pltLDSpQHelperYLimAndTicks(
             dfTCsLDSIn
            ,pDct.keys()
            ,ylim=ylimp
            ,yticks=yticksp     
            ,ylimxlim=ylimpxlim 
            ,xlim=xlim      
            ,ySpanMin=ySpanMin
            ,yGridSteps=yGridSteps
            )       
    
            ax.set_ylim(ylimp)
            ax.set_yticks(yticksp)
                            
            ax.grid() 
    
            ax.set_zorder(10)
            ax.patch.set_visible(False)      
    
            ax.set_ylabel(ylabelp)
    
            # 2. y-Achse Q ----------------------------------------
            logger.debug("{0:s}{1:s}".format(logStr,'# 2. Achse Q'))   
            ax2 = ax.twinx()
            axes['Q']=ax2            
    
            pltHelperX(
             ax2
            ,dateFormat=dateFormat
            ,bysecond=bysecond
            ,byminute=byminute
            ,byhour=byhour
            ,yPos=yTwinedAxesPosDeltaHPStart+yTwinedAxesPosDeltaHP
            )         
           
            for key, value in QDct.items():   
                if key in dfTCsLDSIn.columns:
                   
                    label, linesAct = pltLDSpQHelper(
                    ax2    
                    ,TCdf=dfTCsLDSIn
                    ,ID=key 
                    ,xDctValue=value # a Dct - i.e. {'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
                    ,xDctAttrs=attrsDct 
                    ,IDPltKey=IDPltKey 
                    ,IDPltValuePostfix=None
                    ,xDctFcts=fctsDct
                    # ,timeShift=pd.Timedelta('0 hour') # pd.Timedelta('0 seconds')
                    )    
                    lines[label]=linesAct[0]  
                else:
                    logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,key))       
                       
                if 'RTTM' in value.keys() and plotRTTMlocal:       
                    if value['RTTM'] in dfTCsLDSIn.columns:      
                        
                        plotDf=dfTCsLDSIn.filter(items=[value['RTTM']])
                        if plotRTTM == 'Filter180_1':                            
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,180-1,1)
                            plotDf=plotDf.dropna()       
                        elif plotRTTM == 'Filter60_1':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,60-1,1)
                            plotDf=plotDf.dropna()     
                        elif plotRTTM == 'Filter60_2':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,60-1,2)
                            plotDf=plotDf.dropna()               
                        elif plotRTTM == 'Filter60_3':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,60-1,3)
                            plotDf=plotDf.dropna()       
                        elif plotRTTM == 'Filter30_1':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,1)
                            plotDf=plotDf.dropna()     
                        elif plotRTTM == 'Filter30_2':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,2)
                            plotDf=plotDf.dropna()               
                        elif plotRTTM == 'Filter30_3':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,3)
                            plotDf=plotDf.dropna()          
                        elif plotRTTM == 'Filter30_4':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,4)
                            plotDf=plotDf.dropna()                                      
                        elif plotRTTM == 'Filter30_5':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,5)
                            plotDf=plotDf.dropna()          
                        elif plotRTTM == 'Filter30_6':                           
                            plotDf[value['RTTM']]=savgol_filter(plotDf[value['RTTM']].values,30-1,6)
                            plotDf=plotDf.dropna()                                      
                        else:
                            plotDf=dfTCsLDSIn
                        
                        label, linesAct = pltLDSpQHelper(
                        ax2    
                       ,TCdf=plotDf #dfTCsLDSIn
                       ,ID=value['RTTM'] 
                       ,xDctValue=value # a Dct - i.e. {'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
                       ,xDctAttrs=attrsDct 
                       ,IDPltKey=IDPltKey 
                       ,IDPltValuePostfix=' RTTM' 
                       ,xDctFcts=fctsDct
                       #,timeShift=pd.Timedelta('0 hour') #pd.Timedelta('0 seconds')
                        )                    
                        lines[label]=linesAct[0]  

                    else:
                        logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,value['RTTM']))   

            if not dfTCsOPC.empty:   
                logger.debug("{0:s}{1:s}".format(logStr,'# 2. Achse Q OPC'))   
                for key, value in QDctOPC.items():   
                    if key in dfTCsOPC.columns:                       
                        label, linesAct = pltLDSpQHelper(
                        ax2    
                       ,TCdf=dfTCsOPC
                       ,ID=key 
                       ,xDctValue=value
                       ,xDctAttrs=attrsDct 
                       ,IDPltKey=IDPltKey    
                       ,IDPltValuePostfix=None
                       ,xDctFcts=fctsDct
                       ,timeShift=dfTCsOPCScenTimeShift
                        )                    
                        lines[label]=linesAct[0]                                              
                    else:
                        logger.debug("{0:s}Spalte {1:s} gibt es nicht. Weiter.".format(logStr,key))               
 
                                
            pltLDSHelperY(ax2)
                     
            ylimQ,yticksQ=pltLDSpQHelperYLimAndTicks(
             dfTCsLDSIn
            ,QDct.keys()
            ,ylim=ylimQ
            ,yticks=yticksQ     
            ,ylimxlim=ylimQxlim 
            ,xlim=xlim      
            ,ySpanMin=ySpanMin
            ,yGridSteps=yGridSteps                
            )                               

            ax2.set_ylim(ylimQ)
            ax2.set_yticks(yticksQ)
                                         
            ax2.grid()  
    
            ax2.set_ylabel(ylabelQ)

            # ggf. 3. Achse

            if not dfTCsSIDEvents.empty:       
                

                logger.debug("{0:s}{1:s}".format(logStr,'# 3. Achse SID'))   


                ax3 = ax.twinx()                
                axes['SID']=ax3
    
                pltHelperX(
                 ax3
                ,dateFormat=dateFormat
                ,bysecond=bysecond
                ,byminute=byminute
                ,byhour=byhour
                ,yPos=yTwinedAxesPosDeltaHPStart+2*yTwinedAxesPosDeltaHP
                )         

                if dfTCsSIDEventsInXlimOnly:                    
                    # auf xlim beschränken                
                    dfTCsSIDEventsPlot=dfTCsSIDEvents[
                        (dfTCsSIDEvents.index-dfTCsSIDEventsTimeShift>=xlim[0]) 
                        &#:
                        (dfTCsSIDEvents.index-dfTCsSIDEventsTimeShift<=xlim[1])
                        ]
                    # weiter beschränken auf die, die in xlim mind. 1 Eintrag haben
                    dfTCsSIDEventsPlot=dfTCsSIDEventsPlot.dropna(axis=1,how='all')
                else:
                    dfTCsSIDEventsPlot=dfTCsSIDEvents

                # doppelte bzw. mehrfache Spaltennamen eliminieren (das waere ein Aufruf-Fehler)
                dfTCsSIDEventsPlot = dfTCsSIDEventsPlot.loc[:,~dfTCsSIDEventsPlot.columns.duplicated()]

                #logger.debug("{:s}dfTCsSIDEventsPlot.dropna(how='all'): {:s}".format(logStr,dfTCsSIDEventsPlot.dropna(how='all').to_string()))   

                if not dfTCsSIDEventsPlot.dropna(how='all').empty: # mind. 1 Ereignis in irgendeiner Spalte muss ueberbleiben

                    # aus Performanzgruenden wird nur zum Plot gegeben, was in xlim auch zu sehen sein wird
                    dfTCsSIDEventsPlot2=dfTCsSIDEventsPlot[
                        ( dfTCsSIDEventsPlot.index-dfTCsSIDEventsTimeShift>=xlim[0]) 
                        &#:
                        ( dfTCsSIDEventsPlot.index-dfTCsSIDEventsTimeShift<=xlim[1])
                        ]
            
                    labelsOneCall,scattersOneCall=pltLDSSIDHelper(
                    ax3 
                   ,dfTCsSIDEventsPlot2
                   ,dfTCsSIDEventsTimeShift   
                   ,dfTCsSIDEventsyOffset
                   ,pSIDEvents
                   ,valRegExMiddleCmds
                   ,eventCCmds
                   ,eventCStats
                   ,markerDef
                   ,baseColorsDef                   
                    )                
                    scatters=scatters+scattersOneCall
                            
                pltLDSHelperY(ax3)             
                ax3.set_ylim(ylim3rd)
                ax3.set_yticks(yticks3rd)

                ax3.set_ylabel(ylabel3rd)
    
            if plotLegend:
                legendHorizontalPos='center'

                patterBCp='^p S[rc|nk]'
                patterBCQ='^Q S[rc|nk]'
                patterBCpQ='^[p|Q] S[rc|nk]'

                linesp=[line for line in lines if re.search(patterBCp,line) != None]
                linesQ=[line for line in lines if re.search(patterBCQ,line) != None]

                linespTxt=tuple([lines[line] for line in linesp])                                                            
                linesQTxt=tuple([lines[line] for line in linesQ])
                    
                moreLines=[line for line in lines if re.search(patterBCpQ,line) == None]

                moreLinesp=[line for line in moreLines if re.search('^p',line) != None]
                moreLinesQ=[line for line in moreLines if re.search('^Q',line) != None]

                moreLinespTxt=tuple([lines[line] for line in moreLinesp])                                                            
                moreLinesQTxt=tuple([lines[line] for line in moreLinesQ])

                axes['p'].add_artist(axes['p'].legend(
                                    linespTxt+moreLinespTxt
                                ,linesp+moreLinesp
                                ,loc='upper '+legendHorizontalPos
                                ,framealpha=legendFramealpha
                                ,facecolor=legendFacecolor
                                ))
                axes['Q'].add_artist(axes['Q'].legend(
                                    linesQTxt+moreLinesQTxt
                                ,linesQ+moreLinesQ
                                ,loc='lower '+legendHorizontalPos
                                ,framealpha=legendFramealpha
                                ,facecolor=legendFacecolor
                                ))

                if 'SID' in axes.keys() and len(scatters)>0:
                        if legendHorizontalPos == 'center':
                            legendHorizontalPosAct=''
                        else:
                            legendHorizontalPosAct=' '+legendHorizontalPos
                        axes['SID'].legend(loc='center'+legendHorizontalPosAct
                                ,framealpha=legendFramealpha
                                ,facecolor=legendFacecolor)                                                                                                                        
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return axes,lines,scatters


def pltLDSErgVec(
     ax=None # Axes auf die geplottet werden soll (und aus der neue axes ge-twinx-ed werden; plt.gcf().gca() wenn undef.
    ,dfSegReprVec=pd.DataFrame() # Ergebnisvektor SEG; pass empty Df if Druck only    
    ,dfDruckReprVec=pd.DataFrame() # Ergebnisvektor DRUCK; pass empty Df if Seg only    

    ,xlim=None # tuple (xmin,xmax); wenn undef. gelten min/max aus vorgenannten Daten als xlim; wenn Seg angegeben, gilt Seg   

    ,dateFormat='%y.%m.%d: %H:%M:%S'
    ,bysecond=None #[0,15,30,45]
    ,byminute=None
    ,byhour=None
    
    ,ylimAL=ylimALD
    ,yticksAL=yticksALD #[0,10,20,30,40]

    ,yTwinedAxesPosDeltaHPStart=-0.0125 #: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche
    ,yTwinedAxesPosDeltaHP=-0.0875 #: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche

    ,ylimR=ylimRD #None #(-10,10) #wenn undef., dann min/max dfSegReprVec 
    ,ylimRxlim=False #wenn Wahr und ylimR undef. (None), dann wird xlim beruecksichtigt bei min/max dfSegReprVec
    ,yticksR=yticksRD  #[0,2,4,10,15,30,40]  #wenn undef. (None), dann aus ylimR; matplotlib "vergrößert" mit dem Setzen von yTicks ein ebenfalls gesetztes ylim wenn die Ticks außerhalb des ylims liegen

    # dito Beschl.
    ,ylimAC=ylimACD 
    ,ylimACxlim=False 
    ,yticksAC=yticksACD 

    ,ySpanMin=0.9 # wenn ylim R/AC undef. vermeidet dieses Maß eine y-Achse mit einer zu kleinen Differenz zwischen min/max

    ,plotLegend=True    
    ,legendLoc='best'
    ,legendFramealpha=.2
    ,legendFacecolor='white' 

    ,attrsDctLDS=attrsDctLDS         
                    
    ,plotLPRate=True
    ,plotR2FillSeg=True 
    ,plotR2FillDruck=True         

    ,plotAC=True      
    ,plotACCLimits=True

    ,highlightAreas=True 
    ,Seg_Highlight_Color='cyan'
    ,Seg_Highlight_Alpha=.1     
    ,Seg_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False      
    ,Seg_HighlightError_Color='peru'
    ,Seg_Highlight_Alpha_Error=.3     
    ,Seg_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False   

    ,Druck_Highlight_Color='cyan'
    ,Druck_Highlight_Alpha=.1
    ,Druck_Highlight_Fct=lambda row: True if row['STAT_S']==101 else False  
    ,Druck_HighlightError_Color='peru'
    ,Druck_Highlight_Alpha_Error=.3
    ,Druck_HighlightError_Fct=lambda row: True if row['STAT_S']>=601 else False      

     # fcts to apply
    ,fcts={'QM_AV':lambda x: x*1.6/100.
          #,'TIMER_AV':lambda x: x*10
          ,'AM_AV':lambda x: x*100
           }

    ,plotTV=True
    #,plotTVTimerFct=None 
    #,plotTVAmFct=lambda x: x*100 
    ,plotTVAmLabel=plotTVAmLabelD
    ,ylimTV=ylimTVD
    ,yticksTV=yticksTVD    
    
    ,plotDPDT=True
    ,plotSB_S=True
    ):
    """
    zeichnet Zeitkurven von App LDS Ergebnisvektoren auf ax

    return: axes (Dct der Achsen), yLines (Dct der Linien) 
    Dct der Achsen: 'A': Alarm etc.; 'R': m3/h; 'a': ACC; 'TV': Timer und Leckvolumen

    #! Lücken (nicht plotten) wenn keine Zeiten
    """
   
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    axes={}
    yLines={}

    try:    
        
            if dfSegReprVec.empty and dfDruckReprVec.empty:                
                logger.error("{0:s}{1:s}".format(logStr,'dfSegReprVec UND dfDruckReprVec leer?! Return.')) 
                return

            if not dfSegReprVec.empty: 
                # keine komplett leeren Zeilen
                dfSegReprVec=dfSegReprVec[~dfSegReprVec.isnull().all(1)]
                # keine doppelten Indices
                dfSegReprVec=dfSegReprVec[~dfSegReprVec.index.duplicated(keep='last')] # dfSegReprVec.groupby(dfSegReprVec.index).last() # df[~df.index.duplicated(keep='last')]

            if not dfDruckReprVec.empty: 
                # keine komplett leeren Zeilen
                dfDruckReprVec=dfDruckReprVec[~dfDruckReprVec.isnull().all(1)]
                # keine doppelten Indices
                dfDruckReprVec=dfDruckReprVec[~dfDruckReprVec.index.duplicated(keep='last')] # dfDruckReprVec.groupby(dfDruckReprVec.index).last() # df[~df.index.duplicated(keep='last')]

            if ax==None:
                ax=plt.gcf().gca()
            axes['A']=ax 

            # x-Achse ----------------
            if xlim == None:
                if not dfSegReprVec.empty:
                    xlimMin=dfSegReprVec.index[0]
                    xlimMax=dfSegReprVec.index[-1]
                elif not dfDruckReprVec.empty:
                    xlimMin=dfDruckReprVec.index[0]
                    xlimMax=dfDruckReprVec.index[-1]
                xlim=(xlimMin,xlimMax)

            (xlimMin,xlimMax)=xlim

            ax.set_xlim(xlim)

            logger.debug("{0:s}bysecond: {1:s}".format(logStr,str(bysecond))) 
            logger.debug("{0:s}byminute: {1:s}".format(logStr,str(byminute))) 
            logger.debug("{0:s}byhour: {1:s}".format(logStr,str(byhour))) 
            logger.debug("{0:s}dateFormat: {1:s}".format(logStr,dateFormat)) 
    
            pltHelperX(
             ax
            ,dateFormat=dateFormat
            ,bysecond=bysecond
            ,byminute=byminute
            ,byhour=byhour
            ,yPos=yTwinedAxesPosDeltaHPStart
            )      
    
            # 1. Achse Alarm -----------------------    

            if not dfSegReprVec.empty and highlightAreas:
                tPairs=findAllTimeIntervalls(dfSegReprVec,Seg_Highlight_Fct)
                for t1,t2 in tPairs:                    
                    ax.axvspan(t1, t2, alpha=Seg_Highlight_Alpha, color=Seg_Highlight_Color)
                tPairs=findAllTimeIntervalls(dfSegReprVec,Seg_HighlightError_Fct)
                for t1,t2 in tPairs:                    
                    ax.axvspan(t1, t2, alpha=Seg_Highlight_Alpha_Error, color=Seg_HighlightError_Color)

            if not dfDruckReprVec.empty and highlightAreas:
                tPairs=findAllTimeIntervalls(dfDruckReprVec,Druck_Highlight_Fct)
                for t1,t2 in tPairs:                    
                    ax.axvspan(t1, t2, alpha=Druck_Highlight_Alpha, color=Druck_Highlight_Color)
                tPairs=findAllTimeIntervalls(dfDruckReprVec,Druck_HighlightError_Fct)
                for t1,t2 in tPairs:                    
                    ax.axvspan(t1, t2, alpha=Druck_Highlight_Alpha_Error, color=Druck_HighlightError_Color)

            if not dfSegReprVec.empty:
                lines = pltLDSErgVecHelper(ax,dfSegReprVec,'AL_S',attrsDctLDS['Seg_AL_S_Attrs'])              
                yLines['AL_S Seg']=lines[0]

                
            if not dfDruckReprVec.empty:
                lines = pltLDSErgVecHelper(ax,dfDruckReprVec,'AL_S',attrsDctLDS['Druck_AL_S_Attrs'])                
                yLines['AL_S Drk']=lines[0]
    
                    
            if not dfSegReprVec.empty and plotSB_S:
                lines = pltLDSErgVecHelper(ax,dfSegReprVec,'SB_S',attrsDctLDS['Seg_SB_S_Attrs'],fct=lambda x: x*10)                
                yLines['SB_S Seg']=lines[0]


            if not dfDruckReprVec.empty and plotSB_S:    
                lines = pltLDSErgVecHelper(ax,dfDruckReprVec,'SB_S',attrsDctLDS['Druck_SB_S_Attrs'],fct=lambda x: x*10)                
                yLines['SB_S Drk']=lines[0]
   
        
            ax.set_ylim(ylimAL)
            ax.set_yticks(yticksAL)
    
            ax.grid() 
    
            ax.set_zorder(10)
            ax.patch.set_visible(False)      
    
            ax.set_ylabel('A [0/10/20] u. 10x B [0/1/2/3/4]')
    
            # 2. y-Achse Fluss ----------------------------------------
            ax2 = ax.twinx()
            axes['R']=ax2            
    
            pltHelperX(
             ax2
            ,dateFormat=dateFormat
            ,bysecond=bysecond
            ,byminute=byminute
            ,byhour=byhour
            ,yPos=yTwinedAxesPosDeltaHPStart+yTwinedAxesPosDeltaHP
            )         
           
            pltLDSHelperY(ax2)
            
            if not dfSegReprVec.empty:

                lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'MZ_AV',attrsDctLDS['Seg_MZ_AV_Attrs'])                
                yLines['MZ_AV (R1) Seg']=lines[0]
         
        
                lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'LR_AV',attrsDctLDS['Seg_LR_AV_Attrs'])                
                yLines['LR_AV (R2) Seg']=lines[0]
 
    
                lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'NG_AV',attrsDctLDS['Seg_NG_AV_Attrs'])                            
                yLines['NG_AV Seg']=lines[0]

                if 'QM_AV' in fcts.keys():
                    lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'QM_AV',attrsDctLDS['Seg_QM_AV_Attrs'],fct=fcts['QM_AV'])
                else:                    
                    lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'QM_AV',attrsDctLDS['Seg_QM_AV_Attrs'])
                yLines['QM_AV Seg']=lines[0]

    
                if plotLPRate:        
                    # R2 = R1 - LP
                    # R2 - R1 = -LP
                    # LP = R1 - R2
                    lines = pltLDSErgVecHelper(ax2,dfSegReprVec,'LP_AV',attrsDctLDS['Seg_LP_AV_Attrs'])                   
                    yLines['LP_AV Seg']=lines[0]
         
                                  
                if plotR2FillSeg: 
                    df=dfSegReprVec
                    df=df.reindex(pd.date_range(start=df.index[0], end=df.index[-1], freq='1s'))
                    df=df.fillna(method='ffill').fillna(method='bfill')

                    # R2 unter 0
                    dummy=ax2.fill_between(df.index, df['LR_AV'],0
                                           ,where=df['LR_AV']<0,color='grey',alpha=.2)

                    # zwischen R2 und 0   
                    dummy=ax2.fill_between(df.index, 0, df['LR_AV']
                                           ,where=df['LR_AV']>0
                                           #,color='yellow',alpha=.1
                                           ,color='red',alpha=.1
                                           )


                    # R2 über 0 aber unter NG  
                    dummy=ax2.fill_between(df.index, df['LR_AV'], df['NG_AV']
                                           ,where=(df['LR_AV']>0) & (df['LR_AV']<df['NG_AV']) 
                                           #,color='red',alpha=.1
                                           ,color='yellow',alpha=.1
                                           )

                    # R2 über NG
                    dummy=ax2.fill_between(df.index, df['LR_AV'], df['NG_AV']
                                           ,where=df['LR_AV']>df['NG_AV']
                                           ,color='red',alpha=.2)
    
            if not dfDruckReprVec.empty:

                lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'MZ_AV',attrsDctLDS['Druck_MZ_AV_Attrs'])                
                yLines['MZ_AV (R1) Drk']=lines[0]


                lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'LR_AV',attrsDctLDS['Druck_LR_AV_Attrs'])                
                yLines['LR_AV (R2) Drk']=lines[0]
   
    
                lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'NG_AV',attrsDctLDS['Druck_NG_AV_Attrs'])                
                yLines['NG_AV Drk']=lines[0]


                if plotLPRate:        
                    lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'LP_AV',attrsDctLDS['Druck_LP_AV_Attrs'])                    
                    yLines['LP_AV Drk']=lines[0]

                if 'QM_AV' in fcts.keys():
                    lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'QM_AV',attrsDctLDS['Druck_QM_AV_Attrs'],fct=fcts['QM_AV'])      
                else:                                       
                    lines = pltLDSErgVecHelper(ax2,dfDruckReprVec,'QM_AV',attrsDctLDS['Druck_QM_AV_Attrs'])
                yLines['QM_AV Drk']=lines[0]
  
                if plotR2FillDruck: 
                    df=dfDruckReprVec
                    df=df.reindex(pd.date_range(start=df.index[0], end=df.index[-1], freq='1s'))
                    df=df.fillna(method='ffill').fillna(method='bfill')

                    # R2 unter 0
                    dummy=ax2.fill_between(df.index, df['LR_AV'],0
                                           ,where=df['LR_AV']<0,color='grey',alpha=.4)

                    # zwischen R2 und 0   
                    dummy=ax2.fill_between(df.index, 0, df['LR_AV']
                                           ,where=df['LR_AV']>0
                                           #,color='yellow',alpha=.1
                                           ,color='red',alpha=.1
                                           )


                    # R2 über 0 aber unter NG  
                    dummy=ax2.fill_between(df.index, df['LR_AV'], df['NG_AV']
                                           ,where=(df['LR_AV']>0) & (df['LR_AV']<df['NG_AV']) 
                                           #,color='red',alpha=.1
                                           ,color='yellow',alpha=.1
                                           )

                    # R2 über NG
                    dummy=ax2.fill_between(df.index, df['LR_AV'], df['NG_AV']
                                           ,where=df['LR_AV']>df['NG_AV']
                                           ,color='red',alpha=.2)

        

            ylimSeg,yticksSeg=pltLDSErgVecHelperYLimAndTicks(
             dfSegReprVec
            ,'LR_AV'
            ,ylim=ylimR   
            ,yticks=yticksR 
            ,ylimxlim=ylimRxlim 

            ,xlim=xlim      
            ,ySpanMin=ySpanMin
            )   
            logger.debug("{0:s}ylimRSeg: {1:s} yticksRSeg: {2:s}".format(logStr,str(ylimSeg),str(yticksSeg)))   

            ylimDrk,yticksDrk=pltLDSErgVecHelperYLimAndTicks(
             dfDruckReprVec
            ,'LR_AV'
            ,ylim=ylimR   
            ,yticks=yticksR 
            ,ylimxlim=ylimRxlim
            
            ,xlim=xlim      
            ,ySpanMin=ySpanMin
            ) 
            logger.debug("{0:s}ylimRDrk: {1:s} yticksRDrk: {2:s}".format(logStr,str(ylimDrk),str(yticksDrk)))   

            if ylimSeg[1]>=ylimDrk[1]:
                ylimR=ylimSeg
                yticksR=yticksSeg
            else:
                ylimR=ylimDrk
                yticksR=yticksDrk
            logger.debug("{0:s}ylimR: {1:s} yticksR: {2:s}".format(logStr,str(ylimR),str(yticksR)))   
            
            ax2.set_ylim(ylimR)
            ax2.set_yticks(yticksR)
        
            ax2.grid()  
    
            ax2.set_ylabel('R1, R2, NG, LP (R1-R2), QM [Nm³/h]')

            # 3. y-Achse Beschleunigung ----------------------------------------    
            if plotAC:
    
                # 3. y-Achse Beschleunigung -------------------------------------------------
                ax3 = ax.twinx()
                axes['a']=ax3               
    
                pltHelperX(
                 ax3
                ,dateFormat=dateFormat
                ,bysecond=bysecond
                ,byminute=byminute
                ,byhour=byhour
                ,yPos=yTwinedAxesPosDeltaHPStart+2*yTwinedAxesPosDeltaHP
                )           
                pltLDSHelperY(ax3)
        
                if not dfSegReprVec.empty:
                    lines = pltLDSErgVecHelper(ax3,dfSegReprVec,'AC_AV',attrsDctLDS['Seg_AC_AV_Attrs'])                    
                    yLines['AC_AV Seg']=lines[0]              
                    
                    lines = pltLDSErgVecHelper(ax3,dfSegReprVec,'ACF_AV',attrsDctLDS['Seg_ACF_AV_Attrs'])                    
                    yLines['ACF_AV Seg']=lines[0]    
    
                if not dfDruckReprVec.empty:
                    lines = pltLDSErgVecHelper(ax3,dfDruckReprVec,'AC_AV',attrsDctLDS['Druck_AC_AV_Attrs'])                   
                    yLines['AC_AV Drk']=lines[0]             
                    
                    lines = pltLDSErgVecHelper(ax3,dfDruckReprVec,'ACF_AV',attrsDctLDS['Druck_ACF_AV_Attrs'])                   
                    yLines['ACF_AV Drk']=lines[0]    

                # ACC Limits
                if plotACCLimits:

                    if not dfSegReprVec.empty:
                        # +
                        line=ax3.axhline(y=dfSegReprVec['ACCST_AV'].max())
                        for prop,value in attrsDctLDS['Seg_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   
                        line=ax3.axhline(y=dfSegReprVec['ACCTR_AV'].max())
                        for prop,value in attrsDctLDS['Seg_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)  
                    
                    if not dfDruckReprVec.empty:
                        # +
                        line=ax3.axhline(y=dfDruckReprVec['ACCST_AV'].max())
                        for prop,value in attrsDctLDS['Druck_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   
                        line=ax3.axhline(y=dfDruckReprVec['ACCTR_AV'].max())
                        for prop,value in attrsDctLDS['Druck_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   

                    if not dfSegReprVec.empty:
                        # -
                        line=ax3.axhline(y=-dfSegReprVec['ACCST_AV'].max())
                        for prop,value in attrsDctLDS['Seg_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   
                        line=ax3.axhline(y=-dfSegReprVec['ACCTR_AV'].max())
                        for prop,value in attrsDctLDS['Seg_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   

                    if not dfDruckReprVec.empty:
                        # -
                        line=ax3.axhline(y=-dfDruckReprVec['ACCST_AV'].max())
                        for prop,value in attrsDctLDS['Druck_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   
                        line=ax3.axhline(y=-dfDruckReprVec['ACCTR_AV'].max())
                        for prop,value in attrsDctLDS['Druck_ACC_Limits_Attrs'].items():               
                            plt.setp(line,"{:s}".format(prop),value)   


                ylimSeg,yticksSeg=pltLDSErgVecHelperYLimAndTicks(
                 dfSegReprVec

                ,'AC_AV'
                ,ylim=ylimAC   
                ,yticks=yticksAC    
                ,ylimxlim=ylimACxlim 

                ,xlim=xlim       
                ,ySpanMin=ySpanMin
                )   
                logger.debug("{0:s}ylimACSeg: {1:s} yticksACSeg: {2:s}".format(logStr,str(ylimSeg),str(yticksSeg)))   

                ylimDrk,yticksDrk=pltLDSErgVecHelperYLimAndTicks(
                 dfDruckReprVec              

                ,'AC_AV'
                ,ylim=ylimAC   
                ,yticks=yticksAC    
                ,ylimxlim=ylimACxlim 

                ,xlim=xlim       
                ,ySpanMin=ySpanMin
                ) 
                logger.debug("{0:s}ylimACDrk: {1:s} yticksACDrk: {2:s}".format(logStr,str(ylimDrk),str(yticksDrk)))   

                if ylimSeg[1]>=ylimDrk[1]:
                    ylimAC=ylimSeg
                    yticksAC=yticksSeg
                else:
                    ylimAC=ylimDrk
                    yticksAC=yticksDrk
                logger.debug("{0:s}ylimAC: {1:s} yticksAC: {2:s}".format(logStr,str(ylimAC),str(yticksAC)))   

                ax3.set_ylim(ylimAC)
                ax3.set_yticks(yticksAC)    
    
                ax3.set_ylabel('a [mm/s²]')    

            # 4. y-Achse Timer und Volumen  ----------------------------------------    
            if plotTV:
    
                # 4. y-Achse Timer und Volumen  ----------------------------------------    
                ax4 = ax.twinx()
                axes['TV']=ax4               
    
                yPos=yTwinedAxesPosDeltaHPStart+2*yTwinedAxesPosDeltaHP
                if plotAC:
                    yPos=yPos+yTwinedAxesPosDeltaHP
                                 
                pltHelperX(
                 ax4
                ,dateFormat=dateFormat
                ,bysecond=bysecond
                ,byminute=byminute
                ,byhour=byhour
                ,yPos=yPos
                )           
                pltLDSHelperY(ax4)
        
                if not dfSegReprVec.empty:

                    # TIMER_AV	
                    ###lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'TIMER_AV',attrsDctLDS['Seg_TIMER_AV_Attrs'],fct=plotTVTimerFct)                    

                    if 'TIMER_AV' in fcts.keys():
                        lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'TIMER_AV',attrsDctLDS['Seg_TIMER_AV_Attrs'],fct=fcts['TIMER_AV'])    
                    else:                                       
                        lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'TIMER_AV',attrsDctLDS['Seg_TIMER_AV_Attrs'])    

                    yLines['TIMER_AV Seg']=lines[0]      
                    
                    # AM_AV
                    ###lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'AM_AV',attrsDctLDS['Seg_AM_AV_Attrs'])###,fct=plotTVAmFct)            
                    
                    if 'AM_AV' in fcts.keys():
                        lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'AM_AV',attrsDctLDS['Seg_AM_AV_Attrs'],fct=fcts['AM_AV'])    
                    else:                                       
                        lines = pltLDSErgVecHelper(ax4,dfSegReprVec,'AM_AV',attrsDctLDS['Seg_AM_AV_Attrs'])


                    yLines['AM_AV Seg']=lines[0]      
    
                if not dfDruckReprVec.empty:

                    # TIMER_AV	
                    ###lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'TIMER_AV',attrsDctLDS['Druck_TIMER_AV_Attrs'],fct=plotTVTimerFct)                    

                    if 'TIMER_AV' in fcts.keys():
                        lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'TIMER_AV',attrsDctLDS['Druck_TIMER_AV_Attrs'],fct=fcts['TIMER_AV'])    
                    else:                                       
                        lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'TIMER_AV',attrsDctLDS['Druck_TIMER_AV_Attrs'])    

                    yLines['TIMER_AV Drk']=lines[0]      
                    
                    # AM_AV
                    ###lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'AM_AV',attrsDctLDS['Druck_AM_AV_Attrs'])###,fct=plotTVAmFct)         
                    
                    if 'AM_AV' in fcts.keys():
                        lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'AM_AV',attrsDctLDS['Druck_AM_AV_Attrs'],fct=fcts['AM_AV'])    
                    else:                                       
                        lines = pltLDSErgVecHelper(ax4,dfDruckReprVec,'AM_AV',attrsDctLDS['Druck_AM_AV_Attrs'])

                    yLines['AM_AV Drk']=lines[0]      

                if not dfSegReprVec.empty or not dfDruckReprVec.empty:
                    ax4.set_ylim(ylimTV)
                    ax4.set_yticks(yticksTV)        
                    ax4.set_ylabel(plotTVAmLabel)  
                    ax4.grid() 


            # 5. y-Achse DPDT  ----------------------------------------    
            if plotDPDT and (not dfSegReprVec.empty or not dfDruckReprVec.empty):

                #logger.debug("{:s}plotDPDT: {!s:s} dfSegReprVec.shape: {!s:s} dfDruckReprVec.shape: {!s:s}".format(logStr,plotDPDT,dfSegReprVec.shape,dfDruckReprVec.shape))   

                DPDT_REF_Channel=''

                # Min. ermitteln                
                DPDT_REF_MinSEG=0
                if not dfSegReprVec.empty:
                    if 'DPDT_REF' in dfSegReprVec.columns.to_list():
                        DPDT_REF_Channel='DPDT_REF'
                        s=dfSegReprVec.loc[xlim[0]:xlim[1],'DPDT_REF'].dropna()
                    if 'DPDT_REF_AV' in dfSegReprVec.columns.to_list():
                        DPDT_REF_Channel='DPDT_REF_AV'
                        s=dfSegReprVec.loc[xlim[0]:xlim[1],'DPDT_REF_AV'].dropna()
                        if not s.empty:
                            DPDT_REF_MinSEG=s.min()               

                DPDT_REF_MinDruck=0
                if not dfDruckReprVec.empty:
                    logger.debug("{:s}plotDPDT: dfDruckReprVec: {!s:s}".format(logStr,dfDruckReprVec.columns.to_list()))   
                    if 'DPDT_REF' in dfDruckReprVec.columns.to_list():
                        DPDT_REF_Channel='DPDT_REF'
                        s=dfDruckReprVec.loc[xlim[0]:xlim[1],'DPDT_REF'].dropna()
                    if 'DPDT_REF_AV' in dfDruckReprVec.columns.to_list():
                        DPDT_REF_Channel='DPDT_REF_AV'
                        s=dfDruckReprVec.loc[xlim[0]:xlim[1],'DPDT_REF_AV'].dropna()
                        if not s.empty:
                            DPDT_REF_MinDruck=s.min()             

                DPDT_REF_Min=min(DPDT_REF_MinSEG,DPDT_REF_MinDruck)

                #logger.debug("{:s}plotDPDT: dfSegReprVec: {!s:s} dfDruckReprVec: {!s:s}".format(logStr,plotDPDT,DPDT_REF_MinSEG,DPDT_REF_MinDruck))   

                if DPDT_REF_Min >= 0:
                    pass # es gibt nichts zu plotten
                else:

                    # Max ermitteln
                    maxSeg=DPDT_REF_Min
                    if not dfSegReprVec.empty:
                        if DPDT_REF_Channel in dfSegReprVec.columns.to_list():
                            s=dfSegReprVec.loc[xlim[0]:xlim[1],DPDT_REF_Channel].dropna()
                            s=s[s<0]
                            if not s.empty:
                                DPDT_REF_MinSEG=s.max()         

                    maxDruck=DPDT_REF_Min
                    if not dfDruckReprVec.empty:
                        if DPDT_REF_Channel in dfDruckReprVec.columns.to_list():
                            s=dfDruckReprVec.loc[xlim[0]:xlim[1],DPDT_REF_Channel].dropna()
                            s=s[s<0]
                            if not s.empty:
                                DPDT_REF_MinDruck=s.max()               

                    DPDT_REF_Max=max(maxSeg,maxDruck)


                    # 5. y-Achse DPDT  ---------------------------------------- 
                    ax5 = ax.twinx()
                    axes['DPDT']=ax5               
    
                    yPos=yTwinedAxesPosDeltaHPStart+2*yTwinedAxesPosDeltaHP
                    if plotAC:
                        yPos=yPos+yTwinedAxesPosDeltaHP
                    if plotTV:
                        yPos=yPos+yTwinedAxesPosDeltaHP
                                 
                    pltHelperX(
                     ax5
                    ,dateFormat=dateFormat
                    ,bysecond=bysecond
                    ,byminute=byminute
                    ,byhour=byhour
                    ,yPos=yPos
                    )           
                    pltLDSHelperY(ax5)
                    
                    if not dfSegReprVec.empty:
                        if DPDT_REF_Channel in dfSegReprVec.columns.to_list():            
                            
                            df=dfSegReprVec[(~pd.isnull(dfSegReprVec['DPDT_AV']))
                                           &
                                           (~pd.isnull(dfSegReprVec[DPDT_REF_Channel]))
                                           &
                                           (dfSegReprVec['DPDT_AV']<0)               
                                          ]
                            df=dfSegReprVec

                            lines = pltLDSErgVecHelper(ax5,df,DPDT_REF_Channel,attrsDctLDS['Seg_DPDT_REF_Attrs'],fct=None)                    
                            yLines['DPDT_REF Seg']=lines[0]    

                            #df=dfSegReprVec.loc[xlim[0]:xlim[1],:].query('DPDT_AV < 0') 
                            #logger.debug("{0:s}df (neg. DPDT): {1:s}".format(logStr,df.to_string()))   
                            lines = pltLDSErgVecHelper(ax5,df,'DPDT_AV',attrsDctLDS['Seg_DPDT_AV_Attrs'],fct=None)                    
                            yLines['DPDT_AV Seg']=lines[0]    

                            lines = pltLDSErgVecHelper(ax5,df,'DP2DT2_AV',attrsDctLDS['Seg_DP2DT2_AV_Attrs'],fct=None)                    
                            yLines['DP2DT2_AV Seg']=lines[0]    

                    if not dfDruckReprVec.empty:
                        if DPDT_REF_Channel in dfDruckReprVec.columns.to_list():     
                            
                            df=dfDruckReprVec[(~pd.isnull(dfDruckReprVec['DPDT_AV']))
                                           &
                                           (~pd.isnull(dfDruckReprVec[DPDT_REF_Channel]))
                                           &
                                           (dfDruckReprVec['DPDT_AV']<0)               
                                          ]
                            df=dfDruckReprVec

                            lines = pltLDSErgVecHelper(ax5,df,DPDT_REF_Channel,attrsDctLDS['Druck_DPDT_REF_Attrs'],fct=None)                    
                            yLines['DPDT_REF Drk']=lines[0]    

                            #df=dfDruckReprVec.loc[xlim[0]:xlim[1],:].query('DPDT_AV < 0') 
                            #logger.debug("{0:s}df (neg. DPDT): {1:s}".format(logStr,df.to_string()))   
                            lines = pltLDSErgVecHelper(ax5,df,'DPDT_AV',attrsDctLDS['Druck_DPDT_AV_Attrs'],fct=None)                    
                            yLines['DPDT_AV Drk']=lines[0]   

                            lines = pltLDSErgVecHelper(ax5,df,'DP2DT2_AV',attrsDctLDS['Druck_DP2DT2_AV_Attrs'],fct=None)                    
                            yLines['DP2DT2_AV Drk']=lines[0]   
                                                    
                    yTickList=[DPDT_REF_Min*10 
                               ,DPDT_REF_Min/0.9 # bei einem Vorhaltemass von 0.9 steht hier x; 0.9 X x kann man an den anderen beiden Ticks ablesen
                               #,DPDT_REF_Min
                               ,0
                               ,DPDT_REF_Min*-1
                               ]               
                    ax5.set_ylim(yTickList[0],yTickList[-1])
                    ax5.set_yticks([round(yTick,2) for yTick in yTickList])        
                    if DPDT_REF_Max > DPDT_REF_Min:                       
                        ax5.set_ylabel("bar/Minute (max. Wert: {:6.3f})".format(DPDT_REF_Max))  
                    else:
                        ax5.set_ylabel('bar/Minute')  
                    ax5.grid() 

            if plotLegend:
                legendHorizontalPos='center'
                                               
                if not dfSegReprVec.empty:
                    if dfDruckReprVec.empty:
                        loc=legendLoc # Vorgabe                  
                    else:
                        loc='upper '+legendHorizontalPos  # beide: fix   
                    patternSeg='Seg$'
                    axes['A'].add_artist(axes['A'].legend(
                                tuple([yLines[line] for line in yLines if re.search(patternSeg,line) != None]) 
                                ,tuple([line for line in yLines if re.search(patternSeg,line) != None]) 
                                ,loc=loc #'upper '+legendHorizontalPos
                                ,framealpha=legendFramealpha
                                ,facecolor=legendFacecolor
                                ))         
                if not dfDruckReprVec.empty:
                    if dfSegReprVec.empty:
                        loc=legendLoc # Vorgabe                  
                    else:
                        loc='lower '+legendHorizontalPos  # beide: fix   
                    patternDruck='Drk$'
                    axes['A'].add_artist(axes['A'].legend(
                                tuple([yLines[line] for line in yLines if re.search(patternDruck,line) != None]) 
                                ,tuple([line for line in yLines if re.search(patternDruck,line) != None]) 
                                ,loc=loc #'lower '+legendHorizontalPos
                                ,framealpha=legendFramealpha
                                ,facecolor=legendFacecolor
                                ))                   

                                                                                                                      
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return axes,yLines


def pltHelperX(
     ax
    ,dateFormat='%d.%m.%y: %H:%M:%S'
    ,bysecond=None # [0,15,30,45]
    ,byminute=None 
    ,byhour=None 
    ,yPos=-0.0125 #: (i.d.R. negativer) Abstand der y-Achse von der Zeichenfläche; default: -0.0125
    ):

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:

        logger.debug("{0:s}bysecond: {1:s}".format(logStr,str(bysecond))) 
        logger.debug("{0:s}byminute: {1:s}".format(logStr,str(byminute))) 
        logger.debug("{0:s}byhour: {1:s}".format(logStr,str(byhour))) 
        logger.debug("{0:s}dateFormat: {1:s}".format(logStr,dateFormat)) 
    
        if bysecond != None:
            majLocatorTmp=mdates.SecondLocator(bysecond=bysecond)
        elif byminute != None:
            majLocatorTmp=mdates.MinuteLocator(byminute=byminute)
        elif byhour != None:
            majLocatorTmp=mdates.HourLocator(byhour=byhour)
        else:
            majLocatorTmp=mdates.HourLocator(byhour=[0,12])

        majFormatterTmp=mdates.DateFormatter(dateFormat)   
    

        logger.debug("{0:s}ax.xaxis.set_major_locator ...".format(logStr)) 
        ax.xaxis.set_major_locator(majLocatorTmp)

        logger.debug("{0:s}ax.xaxis.set_major_formatter ...".format(logStr)) 
        ax.xaxis.set_major_formatter(majFormatterTmp)  
  
        #logger.debug("{0:s}ax.get_xticks(): {1:s}".format(logStr,str(ax.get_xticks())))     

        logger.debug("{0:s}setp(ax.xaxis.get_majorticklabels() ...".format(logStr))     
        dummy=plt.setp(ax.xaxis.get_majorticklabels(),rotation='vertical',ha='center')
        ax.spines["left"].set_position(("axes",yPos)) 

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
       
    
def pltLDSHelperY(
     ax
    ):
    
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    #logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    pltMakePatchSpinesInvisible(ax)
    ax.spines['left'].set_visible(True)  
    ax.yaxis.set_label_position('left')
    ax.yaxis.set_ticks_position('left')    

    #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
    
def pltLDSErgVecHelperYLimAndTicks(
     dfReprVec
    ,dfReprVecCol
    ,ylim=None #(-10,10) # wenn undef., dann min/max dfReprVec    
    ,yticks=None #[-10,0,10] # wenn undef., dann aus dem Ergebnis von ylim
    
    ,ylimxlim=False #wenn Wahr und ylim undef., dann wird nachf. xlim beruecksichtigt bei min/max dfReprVec    
    ,xlim=None     
    ,ySpanMin=0.1 # wenn ylim undef. vermeidet dieses Maß eine y-Achse mit einer zu kleinen Differenz zwischen min/max
    ):
    """
    Returns: ylim,yticks
             Der y-Werte-Bereich ylim wird zur x-Achse symmetrisch ermittelt.
                yticks spielt dabei keine Rolle.
             Sind ylim bzw. yticks definiert, erfahren sie keine Änderung.
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
  
    if ylim != None:
        # der y-Wertebereich ist explizit definiert
        pass
    else:                    
        if not dfReprVec.empty and not dfReprVec.loc[:,dfReprVecCol].isnull().all().all():
            if not ylimxlim:
                ylimmin=dfReprVec.loc[:,dfReprVecCol].min()
                ylimmax=dfReprVec.loc[:,dfReprVecCol].max()
            else:       
                (xlimMin,xlimMax)=xlim
                if not dfReprVec.loc[xlimMin:xlimMax,dfReprVecCol].isnull().all().all():                    
                    ylimmin=dfReprVec.loc[xlimMin:xlimMax,dfReprVecCol].min()
                    ylimmax=dfReprVec.loc[xlimMin:xlimMax,dfReprVecCol].max()       
                else:
                    ylimmin=0
                    ylimmax=0

            ylimminR=round(ylimmin,0)
            ylimmaxR=round(ylimmax,0)

            if ylimminR > ylimmin:                
                ylimminR=ylimminR-1
            if ylimmaxR < ylimmax:                
                ylimmaxR=ylimmaxR+1

            ylimminAbsR=math.fabs(ylimminR)
        
            # B auf den extremaleren Wert
            ylimB=max(ylimminAbsR,ylimmaxR)
            if ylimB < ySpanMin:
                # B auf Mindestwert
                ylimB=ySpanMin
        
            ## Differenz < Mindestwert: B+ 
            #if math.fabs(ylimmax-ylimmin) < ySpanMin:
            #    ylimB=.5*(ylimminAbs+ylimmax)+ySpanMin
             
            ylim=(-ylimB,ylimB)
        else:
            ylim=(-ySpanMin,ySpanMin)

    
    if yticks != None:
        # die y-Ticks sind explizit definiert
        pass        
    else:
        # aus Wertebereich
        (ylimMin,ylimMax)=ylim
        yticks=[ylimMin,0,ylimMax] 
    
    #logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
    return ylim,yticks


def pltLDSpQHelperYLimAndTicks(
     dfReprVec
    ,dfReprVecCols
    ,ylim=None  # wenn undef., dann min/max dfReprVec    
    ,yticks=None # wenn undef., dann aus ylimR
    
    ,ylimxlim=False # wenn Wahr und ylim undef., dann wird nachf. xlim beruecksichtigt bei min/max dfReprVec    
    ,xlim=None  # x-Wertebereich   
    ,ySpanMin=0.1 # wenn ylim undef. vermeidet dieses Maß eine y-Achse mit einer zu kleinen Differenz zwischen min/max
    
    ,yGridSteps=yGridStepsD  
    ):
    """
    Returns: ylim,yticks             
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
        
        if ylim != None:
            # der y-Wertebereich ist explizit definiert
            pass
        else:       
            df=dfReprVec.loc[:,[col for col in dfReprVecCols]]
            if not ylimxlim:
                # Extremalwerte Analysebereich
                ylimmin=df.min().min()
                ylimmax=df.max().max()                                                                                                             
            else:    
                if xlim == None:                    
                    logger.error("{0:s} xlim muss angegeben sein wenn ylimxlim Wahr gesetzt wird. Weiter mit ylimxlim Falsch.".format(logStr)) 
                    ylimmin=df.min().min()
                    ylimmax=df.max().max()    
                else:
                    # Extremalwerte x-Wertebereich 
                    (xlimMin,xlimMax)=xlim
                    # Extremalwerte Analysebereich
                    ylimmin=df.loc[xlimMin:xlimMax,:].min().min()
                    ylimmax=df.loc[xlimMin:xlimMax,:].max().max()  

            logger.debug("{0:s} ylimmin={1:10.2f} ylimmax={2:10.2f}.".format(logStr,ylimmin,ylimmax))         
        
            if math.fabs(ylimmax-ylimmin) < ySpanMin:
                ylimmax=ylimmin+ySpanMin
                logger.debug("{0:s} ylimmin={1:10.2f} ylimmax={2:10.2f}.".format(logStr,ylimmin,ylimmax))        
                
            ylimMinR=round(ylimmin,0)
            ylimMaxR=round(ylimmax,0)
            if ylimMinR>ylimmin:
                    ylimMinR=ylimMinR-1
            if ylimMaxR<ylimmax:
                ylimMaxR=ylimMaxR+1     
            
            logger.debug("{0:s} ylimMinR={1:10.2f} ylimMaxR={2:10.2f}.".format(logStr,ylimMinR,ylimMaxR))        
                
            ylim=(ylimMinR,ylimMaxR)
            
        if yticks != None:
            # die y-Ticks sind explizit definiert
            pass        
        else:
            # aus Wertebereich
            (ylimMin,ylimMax)=ylim
            if yGridSteps==0:
                yticks=[ylimMin,ylimMax]             
            else:                        
                dYGrid=(ylimMax-ylimMin)/yGridSteps
                y=np.arange(ylimMin,ylimMax,dYGrid)
                if y[-1]<ylimMax:
                    y=np.append(y,y[-1]+dYGrid)                                                                
                yticks=y
        logger.debug("{0:s} yticks={1:s}.".format(logStr,str(yticks)))      

    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return ylim,yticks
                                            

def pltLDSErgVecHelper(
    ax    
   ,dfReprVec=pd.DataFrame()
   ,ID='AL_S' # Spaltenname in dfReprVec
   ,attrs={}
   ,fct=None # Function
    ):

    """
    Helper

    Returns:    
    lines: ax.plot-Ergebnis
    """
   
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:    

        lines=[]
            
        label=ID

        x=dfReprVec.index.values

        if ID in dfReprVec.columns.to_list():

            if fct==None:
                y=dfReprVec[ID].values
            else:
                y=dfReprVec[ID].apply(fct).values

            if 'where' in attrs.keys():
                logger.debug("{0:s}ID: {1:s}: step-Plot".format(logStr,ID))                    
                lines = ax.step(x,y,label=label
                                ,where=attrs['where'])                                                                                                           
            else:
                lines = ax.plot(x,y,label=label
                                )
            for prop,propValue in [(prop,value) for (prop, value) in attrs.items() if prop not in ['where']]:               
                plt.setp(lines[0],"{:s}".format(prop),propValue)     
        else:
            logger.warning("{0:s}Spalte: {1:s}: nicht vorhanden?!".format(logStr,ID)) 
                                  
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return lines
        
def pltLDSpQHelper(
    ax    
   ,TCdf=pd.DataFrame()
   ,ID='' # Spaltenname
   ,xDctValue={} # a Dct - i.e. {'IDPlt':'Q Src','RTTM':'IMDI.Objects.FBG_MESSW.6_KED_39_FT_01.In.MW.value'}
   ,xDctAttrs={} # a Dct with - i.e. {'Q Src':{'color':'red'},...}
   ,IDPltKey='IDPlt' # Schluesselbezeichner in xDctValue (Key in xDctAttrs und xDctFcts)
   ,IDPltValuePostfix=None # SchluesselPostfix in xDctAttrs und xDctFcts - i.e. ' RTTM'
   ,xDctFcts={} # a Dct with Fcts - i.e. {'p Src':  lambda x: 134.969 + x*10^5/(794.*9.81)}
   ,timeShift=pd.Timedelta('0 seconds')
    ):

    """
    Helper

    Returns:
    label: Bezeichner
    lines: ax.plot-Ergebnis
    """
   
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:    
            
        logger.debug("{:s}Echo der Parameter: xDctFcts: {!s:s}".format(logStr,xDctFcts)) 

        label=''
        lines=[]

        # nur Not Null plotten
        s=TCdf[ID][TCdf[ID].notnull()]

        logger.debug("{0:s}timeShift: {1:s}".format(logStr,str(timeShift)))      
        x=s.index.values+timeShift #TCdf.index.values+timeShift
       
        IDPltValue=None
        if IDPltKey in xDctValue.keys():
            # es liegt ein Schluessel fuer eine Layout-Informationen vor
            IDPltValue=xDctValue[IDPltKey]  # koennte auch None sein ...  {'IDPlt':None}    
            if IDPltValue != None and IDPltValuePostfix != None:
                IDPltValue=IDPltValue+IDPltValuePostfix
        
        if IDPltValue in xDctFcts.keys():     
            logger.debug("{:s}Fcts fuer: {:s}".format(logStr,IDPltValue)) 
            fct=xDctFcts[IDPltValue]
            y=s.apply(fct).values#TCdf[ID].apply(fct).values
        else:           
            y=s.values #TCdf[ID].values

        if  IDPltValue != None: 
            label=IDPltValue+' '+ID
            if IDPltValue in xDctAttrs.keys():     
                if 'where' in xDctAttrs[IDPltValue].keys():
                    logger.debug("{0:s}ID: {1:s}: step-Plot".format(logStr,ID))                    
                    lines = ax.step(x,y
                                    ,label=label
                                    ,where=xDctAttrs[IDPltValue]['where'])                                                                                                           
                else:
                    lines = ax.plot(x,y
                                   ,label=label
                                    )
                for prop,propValue in [(prop,value) for (prop, value) in xDctAttrs[IDPltValue].items() if prop not in ['where']]:               
                    plt.setp(lines[0],"{:s}".format(prop),propValue)                        
            else:
                # es ist kein Layout definiert - einfach plotten                
                logger.debug("{0:s}IDPltValue: {1:s}: es ist kein Layout definiert - einfach plotten ...".format(logStr,IDPltValue))     
                lines = ax.plot(x,y
                               ,label=label
                                )
        else:
            # es liegt kein Schluessel (oder Wert None) fuer eine Layout-Informationen vor - einfach plotten
            label=ID
            logger.debug("{0:s}ID: {1:s}: es liegt kein Schluessel (oder kein Wert) fuer eine Layout-Informationen vor - einfach plotten ...".format(logStr,ID))     
            lines = ax.plot(x,y)            

        logger.debug("{0:s}label: '{1:s}' len(lines): {2:d}".format(logStr,label,len(lines))) 
                                      
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return label, lines


def pltLDSSIDHelper(
    ax 
   ,dfTCsSIDEvents
   ,dfTCsScenTimeShift   
   ,dfTCsSIDEventsyOffset # die y-Werte werden ab dem 1. Schieber um je dfTCsSIDEventsyOffset erhöht (damit zeitgleiche Events besser sichtbar werden); max. Erhöhung: 0.9   
   ,pSIDEvents
   ,valRegExMiddleCmds
   ,eventCCmds
   ,eventCStats
   ,markerDef
   ,baseColorsDef   
    ):


    """
    Helper

    Returns:
    labels: Bezeichner
    scatters: ax.scatter-Ergebnisse

    eventCCmds={ 'Out.AUF':0
                     ,'Out.ZU':1
                     ,'Out.HALT':2}
    eventCStats={'In.LAEUFT':3
                     ,'In.LAEUFT_NICHT':4
                     ,'In.ZUST':5
                     ,'Out.AUF':6
                     ,'Out.ZU':7
                     ,'Out.HALT':8            
                     ,'In.STOER':9}


    markerDefSchieber=[ # Schiebersymobole                      
                                             '^'        # 0 Auf
                                            ,'v'        # 1 Zu
                                            ,'>'        # 2 Halt
                                            # ab hier Zustaende
                                            ,'4'        # 3 Laeuft
                                            ,'3'        # 4 Laeuft nicht
                                            ,'P'        # 5 Zust (gefülltes "dickes" Kreuz)
                                            ,'1'        # 6 Auf
                                            ,'2'        # 7 Zu
                                            ,'+'        # 8 Halt
                                            ,'x'        # 9 Stoer


    """
   
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:    
        
        labels=[]
        scatters=[]
               
        # Anzahl der verschiedenen Schieber ermitteln 
        idxKat={}
        idxSchieberLfd=0    
        for col in dfTCsSIDEvents.columns:    
            m=re.search(pSIDEvents,col)
            valRegExSchieberID=m.group('colRegExSchieberID')
                            
            if valRegExSchieberID not in idxKat.keys():
                idxKat[valRegExSchieberID]=idxSchieberLfd
                idxSchieberLfd=idxSchieberLfd+1          
                        
        logger.debug("{0:s}Dct idxKat: keys (versch. Schieber - meint versch. Kategorien): {1:s}: values (Index der jeweiligen Kategorie): {2:s}".format(logStr,str(idxKat.keys()),str(idxKat.values())))

        dfTCsSIDEventsPlot = dfTCsSIDEvents # hier keine Veränderungen mehr
        
        for col in dfTCsSIDEventsPlot.columns:               
                       
            m=re.search(pSIDEvents,col)
        
            valRegExSchieberID=m.group('colRegExSchieberID')
            idxSchieberLfd=idxKat[valRegExSchieberID]        
            valRegExEventID=m.group('colRegExEventID')        
            valRegExMiddle=m.group('colRegExMiddle')
        
            # Markersize
            s=plt.rcParams['lines.markersize']**2 

            # Marker
            if valRegExMiddle == valRegExMiddleCmds:
                idxMarker=eventCCmds[valRegExEventID]
            else:
                idxMarker=eventCStats[valRegExEventID]
                if valRegExEventID in ['In.ZUST']:
                    s=s*2.5

            if idxMarker < len(markerDef):
                m=markerDef[idxMarker]
            else:
                m=markerDef[-1]
                logger.debug("{0:s}{1:s}: idxMarker: Soll: {2:d} MarkerIdx gewählt: {3:d}".format(logStr,col,idxMarker,len(markerDef)-1))   

            if idxSchieberLfd < len(baseColorsDef):
                c=baseColorsDef[idxSchieberLfd]
            else:
                c=baseColorsDef[-1]
                logger.debug("{0:s}{1:s}: idxSchieberLfd: Ist: {2:d} FarbenIdx gewählt: {3:d}".format(logStr,col,idxSchieberLfd,len(baseColorsDef)-1))   
                            
            colors=[c for idx in range(len(dfTCsSIDEventsPlot.index))] # alle Ereignisse (der Spalte) haben dieselbe Farbe
            label=col   # alle Ereignisse (der Spalte) haben dasselbe Label
            #sDefault=plt.rcParams['lines.markersize']**2 
                        
            x=dfTCsSIDEventsPlot.index.values+dfTCsScenTimeShift
            y=dfTCsSIDEventsPlot[col].values+min(idxSchieberLfd*dfTCsSIDEventsyOffset,.9)

            logger.debug("{:s}{:s}: erste und letzte Werte: x:{!s:s} y:{!s:s}...".format(logStr,col,x[::len(x)-1],y[::len(y)-1]))  

            scatter = ax.scatter(
                         x
                        ,y
                        ,c=colors
                        ,marker=m
                        ,label=label
                        ,s=s#Default
                        )     
            # scatter ist eine PathCollection; Attribut u.a. get_label(): Return the label used for this artist in the legend
            # auch wenn y durchgehend Null wird ein scatter zurueckgegeben (d.h. ist ein Legendeneintrag vorhanden)
            labels.append(label)
            scatters.append(scatter)
                                      
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   
        return labels, scatters
        

# --- PLOT: Funktionen und Hilfsfunktionen
# -----------------------------------------------

def pltMakeCategoricalCmap(baseColorsDef="tab10",catagoryColors=None,nOfSubCatsReq=3,reversedSubCatOrder=False):
    """
    Returns a cmap with nOfCatsReq * nOfSubCatsReq discrete colors.

    Parameter:
        baseColorsDef:    a (discrete) cmap defining the "base"colors
                         default: tab10

                         if baseColorsDef is not via get_cmap a matplotlib.colors.ListedColormap, baseColorsDef is interpreted via to_rgb as a list of colors
                         in this case catagoryColors is ignored 

        catagoryColors:  a list of "base"colors indices for this cmap
                         the length of the list is the number of Categories requested: nOfCatsReq
                         apparently cmap's nOfColors must be ge than nOfCatsReq
                         default: None (==> nOfCatsReq = cmap's nOfColors)
                         i.e. [2,8,3] for tab10 is green, yellow (ocher), red

        nOfSubCatsReq:   number of Subcategories requested

        reversedSubCatOrder: False (default): if True, the last color of a category is from baseColorsDef
        reversedSubCatOrder can be a list
        
    Returns:
        cmap with nOfCatsReq * nOfSubCatsReq discrete colors; None if an error occurs
        one "base"color per category
        nOfSubCatsReq "sub"colors per category
        so each category consists of nOfSubCatsReq colors

    Raises:
        RmError

    >>> import matplotlib
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> import Rm    
    >>> Rm.pltMakeCategoricalCmap().N
    30
    >>> Rm.pltMakeCategoricalCmap(catagoryColors=[2,8,3]).N # 2 8 3 in tab10: grün gelb rot
    9
    >>> baseColorsDef="tab10"
    >>> catagoryColors=[2,8,3]
    >>> nOfSubCatsReq=4
    >>> # grün gelb rot mit je 4 Farben von hell nach dunkel
    >>> cm=Rm.pltMakeCategoricalCmap(baseColorsDef=baseColorsDef,catagoryColors=catagoryColors,nOfSubCatsReq=nOfSubCatsReq,reversedSubCatOrder=True)
    >>> cm.colors
    array([[0.75      , 1.        , 0.75      ],
           [0.51819172, 0.87581699, 0.51819172],
           [0.32570806, 0.75163399, 0.32570806],
           [0.17254902, 0.62745098, 0.17254902],
           [0.9983871 , 1.        , 0.75      ],
           [0.91113148, 0.91372549, 0.51165404],
           [0.82408742, 0.82745098, 0.30609849],
           [0.7372549 , 0.74117647, 0.13333333],
           [1.        , 0.75      , 0.75142857],
           [0.94640523, 0.53069452, 0.53307001],
           [0.89281046, 0.33167491, 0.3348814 ],
           [0.83921569, 0.15294118, 0.15686275]])
    >>> cm2=Rm.pltMakeCategoricalCmap(baseColorsDef=baseColorsDef,catagoryColors=catagoryColors,nOfSubCatsReq=nOfSubCatsReq,reversedSubCatOrder=[False]+2*[True])
    >>> cm.colors[nOfSubCatsReq-1]==cm2.colors[0]
    array([ True,  True,  True])
    >>> plt.close()
    >>> size_DINA6quer=(5.8,4.1)    
    >>> fig, ax = plt.subplots(figsize=size_DINA6quer)
    >>> fig.subplots_adjust(bottom=0.5)
    >>> norm=matplotlib.colors.Normalize(vmin=0, vmax=100)
    >>> cb=matplotlib.colorbar.ColorbarBase(ax, cmap=cm2,norm=norm,orientation='horizontal')
    >>> cb.set_label('baseColorsDef was (via get_cmap) a matplotlib.colors.ListedColormap')    
    >>> #plt.show()
    >>> cm3=Rm.pltMakeCategoricalCmap(baseColorsDef=['b','c','m'],nOfSubCatsReq=nOfSubCatsReq,reversedSubCatOrder=True)   
    >>> cm3.colors
    array([[0.75      , 0.75      , 1.        ],
           [0.5       , 0.5       , 1.        ],
           [0.25      , 0.25      , 1.        ],
           [0.        , 0.        , 1.        ],
           [0.75      , 1.        , 1.        ],
           [0.45833333, 0.91666667, 0.91666667],
           [0.20833333, 0.83333333, 0.83333333],
           [0.        , 0.75      , 0.75      ],
           [1.        , 0.75      , 1.        ],
           [0.91666667, 0.45833333, 0.91666667],
           [0.83333333, 0.20833333, 0.83333333],
           [0.75      , 0.        , 0.75      ]])
    >>> plt.close()     
    >>> fig, ax = plt.subplots(figsize=size_DINA6quer)
    >>> fig.subplots_adjust(bottom=0.5)
    >>> norm=matplotlib.colors.Normalize(vmin=0, vmax=100)
    >>> cb=matplotlib.colorbar.ColorbarBase(ax, cmap=cm3,norm=norm,orientation='horizontal')
    >>> cb.set_label('baseColorsDef was (via to_rgb) a list of colors')   
    >>> #plt.show()
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    cmap=None

    try:  

        try:
            # Farben, "base"colors, welche die cmap hat
            nOfColors=plt.get_cmap(baseColorsDef).N

            if catagoryColors==None:            
                catagoryColors=np.arange(nOfColors,dtype=int)

            # verlangte Kategorien
            nOfCatsReq=len(catagoryColors)
        
            if nOfCatsReq > nOfColors:
                logStrFinal="{0:s}: nOfCatsReq: {1:d} > cmap's nOfColors: {2:d}!".format(logStr,nOfCatsReq,nOfColors)                                 
                raise RmError(logStrFinal)          
                        
            if max(catagoryColors) > nOfColors-1:
                logStrFinal="{0:s}: max. Idx of catsReq: {1:d} > cmap's nOfColors-1: {2:d}!".format(logStr,max(catagoryColors),nOfColors-1)                                 
                raise RmError(logStrFinal)      

            # alle Farben holen, welche die cmap hat
            ccolors = plt.get_cmap(baseColorsDef)(np.arange(nOfColors,dtype=int))
            # die gewuenschten Kategorie"Basis"farben extrahieren        
            ccolors=[ccolors[idx] for idx in catagoryColors]
           
        except:
            listOfColors=baseColorsDef
            nOfColors=len(listOfColors)
            nOfCatsReq=nOfColors

            ccolors=[]
            for color in listOfColors:                
                ccolors.append(list(matplotlib.colors.to_rgb(color)))

        finally:
            pass
    
        logger.debug("{0:s}ccolors: {1:s}".format(logStr,str(ccolors))) 
        logger.debug("{0:s}nOfCatsReq: {1:s}".format(logStr,str((nOfCatsReq)))) 
        logger.debug("{0:s}nOfSubCatsReq: {1:s}".format(logStr,str((nOfSubCatsReq)))) 

        # Farben bauen  -------------------------------------

        # resultierende Farben vorbelegen
        cols = np.zeros((nOfCatsReq*nOfSubCatsReq, 3))

        # ueber alle Kategoriefarben
        if type(reversedSubCatOrder) is not list:
            reversedSubCatOrderLst=nOfCatsReq*[reversedSubCatOrder]
        else:
            reversedSubCatOrderLst=reversedSubCatOrder

        logger.debug("{0:s}reversedSubCatOrderLst: {1:s}".format(logStr,str((reversedSubCatOrderLst)))) 

        for i, c in enumerate(ccolors):
            rgb=pltMakeCategoricalColors(c,nOfSubColorsReq=nOfSubCatsReq,reversedOrder=reversedSubCatOrderLst[i])               
            cols[i*nOfSubCatsReq:(i+1)*nOfSubCatsReq,:] = rgb
            
        cmap = matplotlib.colors.ListedColormap(cols)                
                                                                                          
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return cmap

def pltMakePatchSpinesInvisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def pltHlpAlignMarker(marker,halign='center',valign='middle'):
    """
    create markers with specified alignment.

    Parameters
    ----------

    marker : a valid marker specification.
      See mpl.markers

    halign : string, float {'left', 'center', 'right'}
      Specifies the horizontal alignment of the marker. *float* values
      specify the alignment in units of the markersize/2 (0 is 'center',
      -1 is 'right', 1 is 'left').

    valign : string, float {'top', 'middle', 'bottom'}
      Specifies the vertical alignment of the marker. *float* values
      specify the alignment in units of the markersize/2 (0 is 'middle',
      -1 is 'top', 1 is 'bottom').

    Returns
    -------

    marker_array : numpy.ndarray
      A Nx2 array that specifies the marker path relative to the
      plot target point at (0, 0).

    Notes
    -----
    The mark_array can be passed directly to ax.plot and ax.scatter, e.g.::

        ax.plot(1, 1, marker=align_marker('>', 'left'))

    """

    if isinstance(halign,str):
        halign = {'right': -1.,
                  'middle': 0.,
                  'center': 0.,
                  'left': 1.,
                  }[halign]

    if isinstance(valign,str):
        valign = {'top': -1.,
                  'middle': 0.,
                  'center': 0.,
                  'bottom': 1.,
                  }[valign]

    # Define the base marker
    bm = markers.MarkerStyle(marker)

    # Get the marker path and apply the marker transform to get the
    # actual marker vertices (they should all be in a unit-square
    # centered at (0, 0))
    m_arr = bm.get_path().transformed(bm.get_transform()).vertices

    # Shift the marker vertices for the specified alignment.
    m_arr[:, 0] += halign / 2
    m_arr[:, 1] += valign / 2

    return Path(m_arr, bm.get_path().codes)

def pltNetFigAx(pDf,**kwds):
    """
    Erzeugt eine für die Netzdarstellung verzerrungsfreie Axes-Instanz.

        * verwendet gcf() (will return an existing figure if one is open, or it will make a new one if there is no active figure)
        * an already existing figure might be created this way: fig=plt.figure(dpi=2*72,linewidth=1.) 
        * errechnet die verzerrungsfreie Darstellung unter Berücksichtigung einer zukünftigen horizontalen Farblegende
        * erzeugt eine Axes-Instanz
        * setzt Attribute der Axes-Instanz
        * setzt Attribute der Figure-Instanz

    Args:
        pDf: dataFrame

        Coordinates:
            * pXCor_i: colName in pDf (default: 'pXCor_i'): x-Start Coordinate of all Edges to be plotted  
            * pYCor_i: colName in pDf (default: 'pYCor_i'): y-Start Coordinate of all Edges to be plotted  
            * pXCor_k: colName in pDf (default: 'pXCor_k'): x-End   Coordinate of all Edges to be plotted  
            * pYCor_k: colName in pDf (default: 'pYCor_k'): y-End   Coordinate of all Edges to be plotted  

        Colorlegend:
            * CBFraction: fraction of original axes to use for colorbar (default: 0.05)
            * CBHpad: fraction of original axes between colorbar and new image axes (default: 0.0275)

        Figure:
            * pltTitle: title [not suptitle] (default: 'pltNetFigAx') 
            * figFrameon: figure frame (background): displayed or invisible (default: True)
            * figEdgecolor: edge color of the Figure rectangle (default: 'black')
            * figFacecolor: face color of the Figure rectangle (default: 'white')
    """
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
        keys = sorted(kwds.keys())

        # Coordinates
        if 'pXCor_i' not in keys:
            kwds['pXCor_i']='pXCor_i'
        if 'pYCor_i' not in keys:
            kwds['pYCor_i']='pYCor_i'
        if 'pXCor_k' not in keys:
            kwds['pXCor_k']='pXCor_k'
        if 'pYCor_k' not in keys:
            kwds['pYCor_k']='pYCor_k'

        # Colorlegend
        if 'CBFraction' not in keys:
            kwds['CBFraction']=0.05
        if 'CBHpad' not in keys:
            kwds['CBHpad']=0.0275

        # Figure
        if 'pltTitle' not in keys:
            kwds['pltTitle']='pltNetFigAx'
        if 'figFrameon' not in keys:
            kwds['figFrameon']=True
        if 'figEdgecolor' not in keys:
            kwds['figEdgecolor']='black'
        if 'figFacecolor' not in keys:
            kwds['figFacecolor']='white'

    except:
        pass
    
    try:         
        dx=max(pDf[kwds['pXCor_i']].max(),pDf[kwds['pXCor_k']].max())
        dy=max(pDf[kwds['pYCor_i']].max(),pDf[kwds['pYCor_k']].max())

        # erf. Verhältnis bei verzerrungsfreier Darstellung
        dydx=dy/dx 

        if(dydx>=1):
            dxInch=DINA4_x # Hochformat
        else:
            dxInch=DINA4_y # Querformat
    
        figwidth=dxInch

        #verzerrungsfrei: Blattkoordinatenverhaeltnis = Weltkoordinatenverhaeltnis
        factor=1-(kwds['CBFraction']+kwds['CBHpad'])
        # verzerrungsfreie Darstellung sicherstellen
        figheight=figwidth*dydx*factor

        # Weltkoordinatenbereich
        xlimLeft=0
        ylimBottom=0
        xlimRight=dx
        ylimTop=dy
        
        # plt.figure(dpi=, facecolor=, edgecolor=, linewidth=, frameon=True)
        fig = plt.gcf()  # This will return an existing figure if one is open, or it will make a new one if there is no active figure.



        fig.set_figwidth(figwidth)
        fig.set_figheight(figheight)

        logger.debug("{:s}dx={:10.2f} dy={:10.2f}".format(logStr,dx,dy))     
        logger.debug("{:s}figwidth={:10.2f} figheight={:10.2f}".format(logStr,figwidth,figheight))   

        ax=plt.subplot()
        ax.set_xlim(left=xlimLeft)
        ax.set_ylim(bottom=ylimBottom)
        ax.set_xlim(right=xlimRight)
        ax.set_ylim(top=ylimTop)

        xTicks=ax.get_xticks()
        dxTick = xTicks[1]-xTicks[0]
        yTicks=ax.set_yticks([idx*dxTick for idx in range(math.floor(dy/dxTick)+1)])

        plt.title(kwds['pltTitle'])              
        fig.set_frameon(kwds['figFrameon']) 
        fig.set_edgecolor(kwds['figEdgecolor'])
        fig.set_facecolor(kwds['figFacecolor'])


        # https://stackoverflow.com/questions/14827650/pyplot-scatter-plot-marker-size

        # Size in pts:
        # the argument markersize in plot    denotes the markersize (i.e. diameter) in points
        # the argument s          in scatter denotes the markersize**2              in points^2
        # so a given plot-marker with markersize=x needs a scatter-marker with s=x**2 if the scatter-marker shall cover the same "area" in points^2
        # the "area" of the scatter-marker is proportional to the s param

        # What are points - pts:
        # the standard size of points in matplotlib is 72 ppi
        # 1 point is hence 1/72 inches (1 inch = 1 Zoll = 2.54 cm)
        # 1 point = 0.352777.... mm

        # points and pixels - px:
        # 1 point = dpi/ppi
        # the standard dpi in matplotlib is 100
        # a scatter-marker whos "area" covers always 10 pixel:
        # s=(10*ppi/dpi)**2       
                                                                                          
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))               

def pltNetNodes(pDf,**kwds):
    """
    Scatters NODEs on gca().

    Args:
            pDf: dataFrame

            NODE: Size (Attribute)
                * pAttribute: colName (default: 'Attribute') in pDf  
                * pSizeFactor: (deafault: 1.)
                * scatter Sy-Area in pts^2 = pSizeFactor * Attribute   

            NODE: Color (Measure)
                * pMeasure: colName (default: 'Measure') in pDf  
                * pMeasureColorMap (default: plt.cm.autumn)
                * pMeasureAlpha (default: 0.9)
                * pMeasureClip (default: False)

                * CBFixedLimits (default: True)
                * CBFixedLimitLow (default: 0.) 
                * CBFixedLimitHigh (default: 1.) 

            NODE: 3Classes
                * pMeasure3Classes (default: True) 

                * pMCategory: colName (default: 'MCategory') in pDf                    
                * pMCatTopTxt (default: 'Top')     
                * pMCatMidTxt (default: 'Middle')             
                * pMCatBotTxt (default: 'Bottom')    

                * pMCatTopColor (default: 'palegreen')
                * pMCatTopAlpha (default: 0.9) 
                * pMCatTopClip (default: False)            

                * pMCatMidColorMap (default: plt.cm.autumn) 
                * pMCatMidAlpha (default: 0.9) 
                * pMCatMidClip (default: False)  
                                                                        
                * pMCatBotColor (default: 'violet') 
                * pMCatBotAlpha (default: 0.9) 
                * pMCatBotClip (default: False)     
            
            NODE:
                * pXCor: colName (default: 'pXCor_i') in pDf 
                * pYCor: colName (default: 'pYCor_i') in pDf 

    Returns:
            (pcN, vmin, vmax)

                * pcN: die mit Farbskala gezeichneten Symbole
                * vmin/vmax: die für die Farbskala verwendeten Extremalwerte
    """
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())

            # NODE: Size (Attribute)
            if 'pAttribute' not in keys:
                kwds['pAttribute']='Attribute'
            if 'pSizeFactor' not in keys:
                kwds['pSizeFactor']=1.

            # NODE: Color (Measure)
            if 'pMeasure' not in keys:
                kwds['pMeasure']='Measure'
            if 'pMeasureColorMap' not in keys:
                kwds['pMeasureColorMap']=plt.cm.autumn
            if 'pMeasureAlpha' not in keys:
                kwds['pMeasureAlpha']=0.9
            if 'pMeasureClip' not in keys:
                kwds['pMeasureClip']=False

            if 'CBFixedLimits' not in keys:
                kwds['CBFixedLimits']=True
            if 'CBFixedLimitLow' not in keys:
                kwds['CBFixedLimitLow']=0.
            if 'CBFixedLimitHigh' not in keys:
                kwds['CBFixedLimitHigh']=1.

            # NODE: 3Classes
            if 'pMeasure3Classes' not in keys:
                kwds['pMeasure3Classes']=True

            if 'pMCategory' not in keys:
                kwds['pMCategory']='MCategory'
            if 'pMCatTopTxt' not in keys:
                kwds['pMCatTopTxt']='Top'
            if 'pMCatMidTxt' not in keys:
                kwds['pMCatMidTxt']='Middle'
            if 'pMCatBotTxt' not in keys:
                kwds['pMCatBotTxt']='Bottom'

            if 'pMCatTopColor' not in keys:
                kwds['pMCatTopColor']='palegreen'
            if 'pMCatTopAlpha' not in keys:
                kwds['pMCatTopAlpha']=0.9
            if 'pMCatTopClip' not in keys:
                kwds['pMCatTopClip']=False

            if 'pMCatMidColorMap' not in keys:
                kwds['pMCatMidColorMap']=plt.cm.autumn
            if 'pMCatMidAlpha' not in keys:
                kwds['pMCatMidAlpha']=0.9
            if 'pMCatMidClip' not in keys:
                kwds['pMCatMidClip']=False

            if 'pMCatBotColor' not in keys:
                kwds['pMCatBotColor']='violet'
            if 'pMCatBotAlpha' not in keys:
                kwds['pMCatBotAlpha']=0.9
            if 'pMCatBotClip' not in keys:
                kwds['pMCatBotClip']=False

            # NODE:
            if 'pXCor' not in keys:
                kwds['pXCor']='pXCor_i'
            if 'pYCor' not in keys:
                kwds['pYCor']='pYCor_i'

    except:
        pass 
        
    try: 


 
        ax=plt.gca()
                     
        if kwds['pMeasure3Classes']:

            pN_top=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatTopTxt'])] 
            pN_mid=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatMidTxt'])]     
            pN_bot=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatBotTxt'])] 

            pN_top_Anz,col=pN_top.shape
            pN_mid_Anz,col=pN_mid.shape
            pN_bot_Anz,col=pN_bot.shape

            pcN_top=ax.scatter(    
                    pN_top[kwds['pXCor']],pN_top[kwds['pYCor']]                 
                ,s=kwds['pSizeFactor']*pN_top[kwds['pAttribute']]
                ,color=kwds['pMCatTopColor']
                ,alpha=kwds['pMCatTopAlpha']
                ,edgecolors='face'             
                ,clip_on=kwds['pMCatTopClip'])        
            logger.debug("{:s}Anzahl mit fester Farbe Top gezeichneter Symbole={:d}".format(logStr,pN_top_Anz))                        

            if not kwds['CBFixedLimits']:
                vmin=pN_mid[kwds['pMeasure']].min()
                vmax=pN_mid[kwds['pMeasure']].max()
            else:
                vmin=kwds['CBFixedLimitLow']
                vmax=kwds['CBFixedLimitHigh']

            pcN=ax.scatter(    
                    pN_mid[kwds['pXCor']],pN_mid[kwds['pYCor']]       
                ,s=kwds['pSizeFactor']*pN_mid[kwds['pAttribute']]
                # Farbskala
                ,cmap=kwds['pMCatMidColorMap']
                # Normierung Farbe
                ,vmin=vmin
                ,vmax=vmax
                # Farbwert
                ,c=pN_mid[kwds['pMeasure']] 
                ,alpha=kwds['pMCatMidAlpha']
                ,edgecolors='face'
                ,clip_on=kwds['pMCatMidClip']
                )
            logger.debug("{:s}Anzahl mit Farbskala gezeichneter Symbole={:d}".format(logStr,pN_mid_Anz))    

            pcN_bot=ax.scatter(    
                    pN_bot[kwds['pXCor']],pN_bot[kwds['pYCor']]                 
                ,s=kwds['pSizeFactor']*pN_bot[kwds['pAttribute']]
                ,color=kwds['pMCatBotColor']
                ,alpha=kwds['pMCatBotAlpha']
                ,edgecolors='face'             
                ,clip_on=kwds['pMCatBotClip'])              
            logger.debug("{:s}Anzahl mit fester Farbe Bot gezeichneter Symbole={:d}".format(logStr,pN_bot_Anz))     
                          
        else:

            pN_Anz,col=pDf.shape

            if not kwds['CBFixedLimits']:
                vmin=pDf[kwds['pMeasure']].min()
                vmax=pDf[kwds['pMeasure']].max()
            else:
                vmin=kwds['CBFixedLimitLow']
                vmax=kwds['CBFixedLimitHigh']
                                         
            pcN=ax.scatter(    
                    pDf[kwds['pXCor']],pDf[kwds['pYCor']]       
                ,s=kwds['pSizeFactor']*pDf[kwds['pAttribute']]
                # Farbskala
                ,cmap=kwds['pMeasureColorMap']
                # Normierung Farbe
                ,vmin=vmin
                ,vmax=vmax
                # Farbwert
                ,c=pDf[kwds['pMeasure']] 
                ,alpha=kwds['pMeasureAlpha']
                ,edgecolors='face'
                ,clip_on=kwds['pMeasureClip']
                )            
            logger.debug("{:s}Anzahl mit Farbskala gezeichneter Symbole={:d}".format(logStr,pN_Anz))                           
        
        logger.debug("{:s}Farbskala vmin={:10.3f} Farbskala vmax={:10.3f}".format(logStr,vmin,vmax)) 
                                                                                          
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))            
        return (pcN, vmin, vmax)

def pltNetPipes(pDf,**kwds):
    """
    Plots Lines with Marker on gca().

    Args:
            pDf: dataFrame

            PIPE-Line:
                * pAttribute: column in pDf (default: 'Attribute')                                                       
                * pAttributeLs (default: '-')
                * pAttributeSizeFactor: plot linewidth in pts = pAttributeSizeFactor (default: 1.0) * Attribute       
                * pAttributeSizeMin (default: None): if set: use pAttributeSizeMin-Value as Attribute for LineSize if Attribute < pAttributeSizeMin

                * pAttributeColorMap (default: plt.cm.binary)    
                * pAttributeColorMapUsageStart (default: 1./3; Wertebereich: [0,1])   
                     
                    * Farbskala nach vorh. min./max. Wert
                    * die Farbskala wird nur ab UsageStart genutzt
                    * d.h. Werte die eine "kleinere" Farbe hätten, bekommen die Farbe von UsageStart

            PIPE-Marker:
                * pMeasure: column in pDf  (default: 'Measure')                                  
                * pMeasureMarker (default: '.')
                * pMeasureSizeFactor: plot markersize in pts = pMeasureSizeFactor (default: 1.0) * Measure     
                * pMeasureSizeMin (default: None): if set: use pMeasureSizeMin-Value as Measure for MarkerSize if Measure < pMeasureSizeMin

                * pMeasureColorMap (default: plt.cm.cool) 
                * pMeasureColorMapUsageStart (default: 0.; Wertebereich: [0,1])        

                    * Farbskala nach vorh. min./max. Wert
                    * die Farbskala wird nur ab UsageStart genutzt
                    * d.h. Werte die eine "kleinere" Farbe hätten, bekommen die Farbe von UsageStart

            PIPE:
                * pWAYPXCors: column in pDf (default: 'pWAYPXCors')     
                * pWAYPYCors: column in pDf (default: 'pWAYPYCors')     
                * pClip (default: False)
    """
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())

            # PIPE-Line
            if 'pAttribute' not in keys:
                kwds['pAttribute']='Attribute'
            if 'pAttributeSizeFactor' not in keys:
                kwds['pAttributeSizeFactor']=1.      
                
            if 'pAttributeSizeMin' not in keys:
                kwds['pAttributeSizeMin']=None     

            if 'pAttributeLs' not in keys:
                kwds['pAttributeLs']='-'           
            if 'pAttributeColorMap' not in keys:
                kwds['pAttributeColorMap']=plt.cm.binary
            if 'pAttributeColorMapUsageStart' not in keys:
                kwds['pAttributeColorMapUsageStart']=1./3.                  

            # PIPE-Marker
            if 'pMeasure' not in keys:
                kwds['pMeasure']='Measure'
            if 'pMeasureSizeFactor' not in keys:
                kwds['pMeasureSizeFactor']=1.

            if 'pMeasureSizeMin' not in keys:
                kwds['pMeasureSizeMin']=None  

            if 'pMeasureMarker' not in keys:
                kwds['pMeasureMarker']='.'
            if 'pMeasureColorMap' not in keys:
                kwds['pMeasureColorMap']=plt.cm.cool
            if 'pMeasureColorMapUsageStart' not in keys:
                kwds['pMeasureColorMapUsageStart']=0.

            # PIPE
            if 'pWAYPXCors' not in keys:
                kwds['pWAYPXCors']='pWAYPXCors'
            if 'pWAYPYCors' not in keys:
                kwds['pWAYPYCors']='pWAYPYCors'
            if 'pClip' not in keys:
                kwds['pClip']=False

    except:
        pass 
        
    try: 
       
        # Line
        minLine=pDf[kwds['pAttribute']].min()
        maxLine=pDf[kwds['pAttribute']].max()
        logger.debug("{:s}minLine (Attribute): {:6.2f}".format(logStr,minLine))
        logger.debug("{:s}maxLine (Attribute): {:6.2f}".format(logStr,maxLine))
        normLine=colors.Normalize(minLine,maxLine)
        usageLineValue=minLine+kwds['pAttributeColorMapUsageStart']*(maxLine-minLine)
        usageLineColor=kwds['pAttributeColorMap'](normLine(usageLineValue)) 

        # Marker
        minMarker=pDf[kwds['pMeasure']].min()
        maxMarker=pDf[kwds['pMeasure']].max()
        logger.debug("{:s}minMarker (Measure): {:6.2f}".format(logStr,minMarker))
        logger.debug("{:s}maxMarker (Measure): {:6.2f}".format(logStr,maxMarker))
        normMarker=colors.Normalize(minMarker,maxMarker)
        usageMarkerValue=minMarker+kwds['pMeasureColorMapUsageStart']*(maxMarker-minMarker)
        usageMarkerColor=kwds['pMeasureColorMap'](normMarker(usageMarkerValue)) 

        ax=plt.gca()
        for xs,ys,vLine,vMarker in zip(pDf[kwds['pWAYPXCors']],pDf[kwds['pWAYPYCors']],pDf[kwds['pAttribute']],pDf[kwds['pMeasure']]):        

            if vLine >= usageLineValue:
                colorLine=kwds['pAttributeColorMap'](normLine(vLine)) 
            else:
                colorLine=usageLineColor

            if vMarker >= usageMarkerValue:
                colorMarker=kwds['pMeasureColorMap'](normMarker(vMarker))
            else:
                colorMarker=usageMarkerColor

            linewidth=kwds['pAttributeSizeFactor']*vLine 
            if kwds['pAttributeSizeMin'] != None:
               if vLine <  kwds['pAttributeSizeMin']:
                    linewidth=kwds['pAttributeSizeFactor']*kwds['pAttributeSizeMin']     
                    
            mSize=kwds['pMeasureSizeFactor']*vMarker
            if kwds['pMeasureSizeMin'] != None:
               if vMarker <  kwds['pMeasureSizeMin']:
                    mSize=kwds['pMeasureSizeFactor']*kwds['pMeasureSizeMin']  

            pcLines=ax.plot(xs,ys
                            ,color=colorLine
                            ,linewidth=linewidth
                            ,ls=kwds['pAttributeLs']
                            ,marker=kwds['pMeasureMarker']
                            ,mfc=colorMarker 
                            ,mec=colorMarker  
                            ,mfcalt=colorMarker  
                            ,mew=0
                            ,ms=mSize #kwds['pMeasureSizeFactor']*vMarker                                                    
                            ,markevery=[0,len(xs)-1]
                            ,aa=True
                            ,clip_on=kwds['pClip']
                           )            
                                                        
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))                   

def pltNetLegendColorbar(pc,pDf,**kwds): 
    """
    Erzeugt eine Axes cax für den Legendenbereich aus ax (=gca()) und zeichnet auf cax die Farblegende (die Farbskala mit allen Eigenschaften).

        Args:
            pc: (eingefaerbte) PathCollection (aus pltNetNodes); wird für die Erzeugung der Farbskala zwingend benoetigt  
            pDf: dataFrame (default: None)

            Measure:
                * pMeasure: colName in pDf (default: 'Measure') 
                * pMeasureInPerc: Measure wird interpretiert in Prozent [0-1] (default: True)
                * pMeasure3Classes (default: False d.h. Measure wird nicht in 3 Klassen dargestellt)

            CBFixedLimits (Ticks):
                * CBFixedLimits (default: False d.h. Farbskala nach vorh. min./max. Wert)
                * CBFixedLimitLow (default: .10) 
                * CBFixedLimitHigh (default: .95) 

            Label:
                * pMeasureUNIT (default: '[]')
                * pMeasureTYPE (default: '')

            CB
                * CBFraction: fraction of original axes to use for colorbar (default: 0.05)
                * CBHpad: fraction of original axes between colorbar and new image axes (default: 0.0275)               
                * CBLabelPad (default: -50)         
                * CBTicklabelsHPad (default: 0.)      
                * CBAspect: ratio of long to short dimension (default: 10.)
                * CBShrink: fraction by which to shrink the colorbar (default: 0.3)
                * CBAnchorHorizontal: horizontaler Fußpunkt der colorbar in Plot-% (default: 0.)
                * CBAnchorVertical: vertikaler Fußpunkt der colorbar in Plot-% (default: 0.2)     

        Return:
            cax
                  
    """
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())

            # Measure
            if 'pMeasure' not in keys:
                kwds['pMeasure']='Measure'
            if 'pMeasureInPerc' not in keys:
                kwds['pMeasureInPerc']=True
            if 'pMeasure3Classes' not in keys:
                kwds['pMeasure3Classes']=False

            # Label
            if 'pMeasureUNIT' not in keys:
                kwds['pMeasureUNIT']='[]'
            if 'pMeasureTYPE' not in keys:
                kwds['pMeasureTYPE']=''

            # CBFixedLimits 
            if 'CBFixedLimits' not in keys:
                kwds['CBFixedLimits']=False
            if 'CBFixedLimitLow' not in keys:
                kwds['CBFixedLimitLow']=.10
            if 'CBFixedLimitHigh' not in keys:
                kwds['CBFixedLimitHigh']=.95

            # CB
            if 'CBFraction' not in keys:
                kwds['CBFraction']=0.05
            if 'CBHpad' not in keys:
                kwds['CBHpad']=0.0275
            if 'CBLabelPad' not in keys:
                kwds['CBLabelPad']=-50
            if 'CBTicklabelsHPad' not in keys:
                kwds['CBTicklabelsHPad']=0
            if 'CBAspect' not in keys:
                kwds['CBAspect']=10.
            if 'CBShrink' not in keys:
                kwds['CBShrink']=0.3
            if 'CBAnchorHorizontal' not in keys:
                kwds['CBAnchorHorizontal']=0.
            if 'CBAnchorVertical' not in keys:
                kwds['CBAnchorVertical']=0.2


    except:
            pass

        
    try: 
          
        ax=plt.gca()
        fig=plt.gcf()   

        # cax   
        cax=None           
        cax,kw=make_axes(ax
                        ,location='right'
                        ,fraction=kwds['CBFraction'] # fraction of original axes to use for colorbar
                        ,pad=kwds['CBHpad'] # fraction of original axes between colorbar and new image axes
                        ,anchor=(kwds['CBAnchorHorizontal'],kwds['CBAnchorVertical']) # the anchor point of the colorbar axes
                        ,aspect=kwds['CBAspect'] # ratio of long to short dimension
                        ,shrink=kwds['CBShrink'] # fraction by which to shrink the colorbar
                        )         

        # colorbar
        colorBar=fig.colorbar(pc
                    ,cax=cax
                    ,**kw
                    )        

        # tick Values  
        if kwds['pMeasure3Classes']: # FixedLimits should be True and FixedLimitHigh/Low should be set ...
            minCBtickValue=kwds['CBFixedLimitLow']
            maxCBtickValue=kwds['CBFixedLimitHigh']             
        else:
            if kwds['CBFixedLimits'] and isinstance(kwds['CBFixedLimitHigh'],float) and isinstance(kwds['CBFixedLimitLow'],float):
                minCBtickValue=kwds['CBFixedLimitLow']
                maxCBtickValue=kwds['CBFixedLimitHigh']                      
            else:
                minCBtickValue=pDf[kwds['pMeasure']].min()
                maxCBtickValue=pDf[kwds['pMeasure']].max()           
        colorBar.set_ticks([minCBtickValue,minCBtickValue+.5*(maxCBtickValue-minCBtickValue),maxCBtickValue])  

        # tick Labels
        if kwds['pMeasureInPerc']:
            if kwds['pMeasure3Classes']:
                minCBtickLabel=">{:3.0f}%".format(minCBtickValue*100)
                maxCBtickLabel="<{:3.0f}%".format(maxCBtickValue*100)                             
            else:
                minCBtickLabel="{:6.2f}%".format(minCBtickValue*100)
                maxCBtickLabel="{:6.2f}%".format(maxCBtickValue*100) 
        else:
            if kwds['pMeasure3Classes']:
                minCBtickLabel=">{:6.2f}".format(minCBtickValue)
                maxCBtickLabel="<{:6.2f}".format(maxCBtickValue)    
            else:
                minCBtickLabel="{:6.2f}".format(minCBtickValue)
                maxCBtickLabel="{:6.2f}".format(maxCBtickValue)    
        logger.debug("{:s}minCBtickLabel={:s} maxCBtickLabel={:s}".format(logStr,minCBtickLabel,maxCBtickLabel))    
        colorBar.set_ticklabels([minCBtickLabel,'',maxCBtickLabel])        
        colorBar.ax.yaxis.set_tick_params(pad=kwds['CBTicklabelsHPad'])     
                                 
        # Label
        if kwds['pMeasureInPerc']:
                CBLabelText="{:s} in [%]".format(kwds['pMeasureTYPE'])                                                                
        else:
                CBLabelText="{:s} in {:s}".format(kwds['pMeasureTYPE'],kwds['pMeasureUNIT'])
         
        colorBar.set_label(CBLabelText,labelpad=kwds['CBLabelPad'])
                                                                                                                
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
        return cax

def pltNetLegendColorbar3Classes(pDf,**kwds):               
    """
    Zeichnet auf gca() die ergaenzenden Legendeninformationen bei 3 Klassen.  

    * scatters the Top-Symbol
    * scatters the Bot-Symbol
    * the "Mid-Symbol" is the (already existing) colorbar with (already existing) ticks and ticklabels 

    Args:

            pDf: dataFrame

            Category:
                * pMCategory: colName in pDf (default: 'MCategory')
                * pMCatTopText
                * pMCatMidText
                * pMCatBotText

            CBLegend (3Classes) - Parameterization of the representative Symbols
                * CBLe3cTopVPad (default: 1+1*1/4)
                * CBLe3cMidVPad (default: .5)                                                                         
                * CBLe3cBotVPad (default: 0-1*1/4)
                
                    * "1" is the height of the Colorbar                                                                   
                    * the VPads (the vertical Sy-Positions) are defined in cax.transAxes Coordinates    
                    * cax is the Colorbar Axes               

                * CBLe3cSySize=10**2 (Sy-Area in pts^2)
                * CBLe3cSyType='o' 

            Color:
                * pMCatBotColor='violet' 
                * pMCatTopColor='palegreen'    

    Returns:
            (bbTop, bbMid, bbBot): the boundingBoxes of the 3Classes-Symbols  

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())

            # Cats
            if 'pMCategory' not in keys:
                kwds['pMCategory']='MCategory'

            if 'pMCatTopText' not in keys:
                kwds['pMCatTopText']='Top'
            if 'pMCatMidText' not in keys:
                kwds['pMCatMidText']='Middle'
            if 'pMCatBotText' not in keys:
                kwds['pMCatBotText']='Bottom'

            # CBLegend3Cats 
            if 'CBLe3cTopVPad' not in keys:
                kwds['CBLe3cTopVPad']=1+1*1/4  
            if 'CBLe3cMidVPad' not in keys:
                kwds['CBLe3cMidVPad']=.5    
            if 'CBLe3cBotVPad' not in keys:
                kwds['CBLe3cBotVPad']=0-1*1/4    
            if 'CBLe3cSySize' not in keys:
                kwds['CBLe3cSySize']=10**2
            if 'CBLe3cSyType' not in keys:
                kwds['CBLe3cSyType']='o'

            # CatAttribs 
            if 'pMCatTopColor' not in keys:
                kwds['pMCatTopColor']='palegreen'
            if 'pMCatBotColor' not in keys:
                kwds['pMCatBotColor']='violet'

    except:
            pass
        
    try: 
        cax=plt.gca()
        
        pDf_top=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatTopTxt'])] 
        pDf_mid=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatMidTxt'])]     
        pDf_bot=pDf[(pDf[kwds['pMCategory']]==kwds['pMCatBotTxt'])] 

        pDf_top_Anz,col=pDf_top.shape
        pDf_mid_Anz,col=pDf_mid.shape
        pDf_bot_Anz,col=pDf_bot.shape

        logger.debug("{:s} pDf_bot_Anz={:d}  pDf_mid_Anz={:d} pDf_top_Anz={:d}".format(logStr,pDf_bot_Anz,pDf_mid_Anz,pDf_top_Anz))
        logger.debug("{:s} CBLe3cBotVPad={:f}  CBLe3cMidVPad={:f} CBLe3cTopVPad={:f}".format(logStr,kwds['CBLe3cBotVPad'],kwds['CBLe3cMidVPad'],kwds['CBLe3cTopVPad']))

        bbBot=None
        bbMid=None
        bbTop=None

        if pDf_bot_Anz >= 0:
            po=cax.scatter( 0.,kwds['CBLe3cBotVPad']                   
                            ,s=kwds['CBLe3cSySize']
                            ,c=kwds['pMCatBotColor']
                            ,alpha=0.9
                            ,edgecolors='face'             
                            ,clip_on=False
                            ,marker=pltHlpAlignMarker(kwds['CBLe3cSyType'], halign='left')                                     
                            )
            # Text dazu
            o=po.findobj(match=None) 
            p=o[0]           
            bbBot=p.get_datalim(cax.transAxes)      
            logger.debug("{:s} bbBot={!s:s}".format(logStr,bbBot))                         

        #    a=plt.annotate(pMCatBotText                                     
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad+CBLe3cTextSpaceFactor*(bb.x1-bb.x0),CBLe3cBotVpad)
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'  
        #                    ,color=pMCatBotColor 
        #                    )
        #    # weiterer Text dazu
        #    a=plt.annotate("Anz HA: {:6d}".format(pDf_bot_Anz)                                
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad+CBLe3cTextSpaceFactor*(bb.x1-bb.x0)+.5,CBLe3cBotVpad)
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'  
        #                    ,color=pMCatBotColor 
        #                    )

        if pDf_top_Anz >= 0:
            po=cax.scatter( 0.,kwds['CBLe3cTopVPad']                          
                            ,s=kwds['CBLe3cSySize']
                            ,c=kwds['pMCatTopColor']
                            ,alpha=0.9
                            ,edgecolors='face'             
                            ,clip_on=False     
                            ,marker=pltHlpAlignMarker(kwds['CBLe3cSyType'], halign='left')                                      
                            )
           
            o=po.findobj(match=None) 
            p=o[0]           
            bbTop=p.get_datalim(cax.transAxes)      


        #        #Text dazu
        #    o=po.findobj(match=None) 
        #    p=o[0]           
        #    bb=p.get_datalim(cax.transAxes)     
        #    bbTop=bb      
        #    a=plt.annotate(pMCatTopText                                
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad+CBLe3cTextSpaceFactor*(bb.x1-bb.x0),CBLe3cTopVpad)
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'    
        #                    ,color=pMCatTopColor                            
        #                    )

        #        #weiterer Text dazu                  
        #    a=plt.annotate("Anz HA: {:6d}".format(pDf_top_Anz)                                       
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad++CBLe3cTextSpaceFactor*(bb.x1-bb.x0)+.5,CBLe3cTopVpad)
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'    
        #                    ,color=pMCatTopColor                            
        #                    )


        if pDf_mid_Anz >= 0:           
            po=cax.scatter( 0.,kwds['CBLe3cMidVPad']                                    
                            ,s=kwds['CBLe3cSySize']
                            ,c='lightgrey'
                            ,alpha=0.9
                            ,edgecolors='face'             
                            ,clip_on=False
                            ,visible=False # es erden nur die Koordinaten benoetigt
                            ,marker=pltHlpAlignMarker(kwds['CBLe3cSyType'], halign='left')             

                            )
           
            o=po.findobj(match=None) 
            p=o[0]           
            bbMid=p.get_datalim(cax.transAxes)  


        #        #Text dazu
        #    o=po.findobj(match=None) 
        #    p=o[0]
        #    bb=p.get_datalim(cax.transAxes)
        #    a=plt.annotate(pMCatMidText                                    
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad+CBLe3cTextSpaceFactor*(bb.x1-bb.x0),CBLe3cMidVpad)                                                                                 
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'
        #                    ,color=pMCatMidColor   
        #                        ,visible=False
        #    )
        #        #weiterer Text dazu                
        #    a=plt.annotate("Anz HA: {:6d}".format(pDf_mid_Anz)                                              
        #                    ,xy=(CBHpad+CBLe3cHpadSymbol+CBLe3cHpad+CBLe3cTextSpaceFactor*(bb.x1-bb.x0)+.5,CBLe3cMidVpad)                                                                                 
        #                    ,xycoords=cax.transAxes 
        #                    ,rotation='vertical' #90
        #                    ,va='center'
        #                    ,ha='center'
        #                    ,color=pMCatMidColor   
        #                        ,visible=False
        #    )        
      
      
                                                                                                                
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return (bbTop, bbMid, bbBot)  

def pltNetLegendTitleblock(text='',**kwds):
    """
    Zeichnet auf gca() ergaenzende Schriftfeldinformationen.    

    Args:

        text    
        
        Parametrierung:
            * anchorVertical
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())
            
            if 'anchorVertical' not in keys:
                kwds['anchorVertical']=1.
    except:
            pass

    cax=plt.gca()
    try:         
        a=plt.text( 0.
                   ,kwds['anchorVertical']
                   ,text
                   ,transform=cax.transAxes
                   ,family='monospace'
                   ,size='smaller'                    
                   ,rotation='vertical'
                   ,va='bottom'
                   ,ha='left'
                  )                                                                                                                      
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

def pltNetTextblock(text='',**kwds):
    """
    Zeichnet einen Textblock auf gca().      
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:
            keys = sorted(kwds.keys())
            
            if 'x' not in keys:
                kwds['x']=0.
            if 'y' not in keys:
                kwds['y']=1.


    except:
            pass

    ax=plt.gca()
    try:         
        a=plt.text( kwds['x']
                   ,kwds['y']
                   ,text
                   ,transform=ax.transAxes
                   ,family='monospace'
                   ,size='smaller'                    
                   ,rotation='horizontal'
                   ,va='bottom'
                   ,ha='left'
                  )                                                                                                                      
    except RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise RmError(logStrFinal)                       
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

class Rm():

    @classmethod
    def pltNetPipes(cls,pDf,**kwds):
        """
        Plots colored PIPES.
        
        Args:
                DATA:
                    pDf: dataFrame
                        * query: query to filter pDf; default: None; Exp.: ="CONT_ID == '1001'"
                        * fmask: function to filter pDf; default: None; Exp.: =lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False   
                        * query and fmask are used both (query 1st) if not None
                        * sort_values_by: list of colNames defining the plot order; default: None (d.h. die Plotreihenfolge - und damit die z-Order - ist dann die pDF-Reihenfolge)
                        * sort_values_ascending; default: False (d.h. kleine zuletzt und damit (wenn pAttrLineSize = pAttribute/pAttributeFunc) auch dünne über dicke); nur relevant bei sort_values_by

                AXES:
                    pAx: Axes to be plotted on; if not specified: gca() is used

                Colorlegend:
                        * CBFraction in % (default: 5)
                        * CBHpad (default: 0.05)
                        * CBLabel (default: pAttribute/pAttributeFunc)  
                        * CBBinTicks (default: None, d.h. keine Vorgabe von Außen); Vorgabe N: N yTicks; bei diskreten CM gemeint im Sinne von N-1 diskreten Kategorien

                        * CBBinDiscrete (default: False, d.h. eine gegebene (kontinuierliche) CM wird nicht in eine diskrete gewandelt)
                        * wenn CBBinDiscrete, dann gilt N aus CBBinTicks fuer die Ticks (bzw. Kategorien); ist CBBinTicks undef. gilt 4 (also 3 Kategorien)
                        * bei den vorgenannten Kategorien handelt es sich um eine gleichmäßige Unterteilung des definierten Wertebereiches
                        * CBBinBounds (default: None): wenn die CM eine diskrete ist, dann wird eine vorgegebene BoundaryNorm angewandt; CBBinTicks hat dann keine Bedeutung
                      
                        * CBTicks: individuell vorgegebene Ticks; wird am Schluss prozessiert, d.h. vorh. (ggf. auch durch CBBinTicks bzw. <=/>= u. v=/^= bereits manipulierte) ...
                        * ... Ticks werden überschrieben; kann ohne CBTickLabels verwendet werden
                        * CBTickLabels: individuell vorgegebene Ticklabels; wird danach prozessiert; Länge muss zu dann existierenden Ticks passen; kann auch ohne CBTicks verwendet werden
                        
                PIPE-Attribute:
                    * pAttribute: column in pDf (default: 'Attribute')     
                    * pAttributeFunc: 
                        * function to be used to construct a new col to be plotted
                        * if pAttributeFunc is not None pAttribute is not used: pAttribute is set to 'pAttributeFunc'
                        * the new constructed col is named 'pAttributeFunc'; this name can be used in sort_values_by        
                        
                PIPE-Color:
                    * pAttributeColorMap (default: plt.cm.cool)   
                    * Farbskalamapping:
                    * ------------------
                    * pAttributeColorMapMin (default: pAttribute.min()); ordnet der kleinsten   Farbe einen Wert zu; CM: wenn angegeben _und unterschritten: <=    
                    * pAttributeColorMapMax (default: pAttribute.max()); ordnet der größten     Farbe einen Wert zu; CM: wenn angegeben _und überschritten:  >=   
                    * Standard: Farbskala wird voll ausgenutzt; d.h. der (ggf. mit Min/Max) eingegrenzte Wertebereich wird den Randfarben der Skala zugeordnet
                    * wenn ein anderer, kleinerer, Wertebereich mit derselben Farbskala geplottet wird, dann sind die Farben in den Plots nicht vergleichbar ...
                    * ... wenn eine Farbvergleichbarkeit erzielt werden soll, darf dieselbe Farbskala nicht voll ausgenutzt werden  

                    * pAttributeColorMapUsageStart (default: 0.; Wertebereich: [0,1[)                          
                        * hier: die Farbskala wird unten nur ab UsageStart genutzt ...
                        * ... d.h. Werte die eine "kleinere" Farbe hätten, bekommen die Farbe von UsageStart; CM: v=
                    * pAttributeColorMapUsageEnd (default: 1.; Wertebereich: ]0,1])                           
                        * hier: die Farbskala wird oben nur bis UsageEnd genutzt ...
                        * ... d.h. Werte die eine "größere" Farbe hätten, bekommen die Farbe von UsageEnd; CM: ^=
                        
                    * etwas anderes ist es, wenn man eine Farbskala an den Rändern nicht voll ausnutzen möchte weil einem die Farben dort nicht gefallen ...
                                     
                PIPE-Color 2nd:
                    * um "unwichtige" Bereiche zu "dimmen": Beispiele:                    
                    * räumlich: nicht-Schnitt Bereiche; Bestand (2nd) vs. Ausbau; Zonen unwichtig (2nd) vs. Zonen wichtig; Ok (2nd) von NOK
                    * es werden erst die 2nd-Color Pipes gezeichnet; die (1st-)Color Pipes werden danach gezeichnet, liegen also "über" den "unwichtigen"

                    * es wird dieselbe Spalte pAttribute/pAttributeFunc für die 2. Farbskala verwendet
                    * es wird derselbe Linienstil (pAttributeLs) für die 2. Farbskala verwendet
                    * es wird dieselbe Dicke pAttrLineSize (pAttribute/pAttributeFunc) für die 2. Farbskala verwendet

                    * nur die Farbskala ist anders sowie ggf. das Farbskalamapping

                    * pAttributeColorMapFmask: function to filter pDf to decide to plot with colorMap; default: =lambda row: True       
                    * pAttributeColorMap2ndFmask: function to filter pDf to decide to plot with colorMap2nd; default: =lambda row: False     
                                        
                    * mit den beiden Funktionsmasken kann eine Filterung zusätzlich zu query und fmask realisiert werden
                    * die Funktionsmasken sollten schnittmengenfrei sein; wenn nicht: 2nd überschreibt 

                    * pAttributeColorMap2nd (default: plt.cm.binary)    
                    * Farbskalamapping:
                    * ------------------
                    * pAttributeColorMap2ndMin (default: pAttributeColorMapMin)    
                    * pAttributeColorMap2ndMax (default: pAttributeColorMapMax)    

                    * die Farbskala wird an den Rändern nicht voll ausgenutzt wenn die Farben dort ggf. nicht gefallen:
                    * pAttributeColorMap2ndUsageStart (default: 0.; Wertebereich: [0,1[)                                                
                    * pAttributeColorMap2ndUsageEnd (default: 1.; Wertebereich: ]0,1])                                              
                
                PIPE-Linestyle:
                    * pAttributeLs (default: '-')
                    * same for all colors if mutliple colors are specified

                PIPE-Linesize:
                    * pAttrLineSize: column in pDf; if not specified: pAttribute/pAttributeFunc                
                    * pAttrLineSizeFactor (>0): plot linewidth in pts = pAttrLineSizeFactor (default: =...) * fabs(pAttrLineSize) 
                    * ...: 1./(pDf[pAttrLineSize].std()*2.)      
                    * same for all colors if mutliple colors are specified

                PIPE-Geometry:
                    * pWAYPXCors: column in pDf (default: 'pWAYPXCors')     
                    * pWAYPYCors: column in pDf (default: 'pWAYPYCors')     
                    * pClip (default: True)

                >>> import pandas as pd
                >>> import matplotlib
                >>> import matplotlib.pyplot as plt
                >>> import matplotlib.gridspec as gridspec
                >>> import math
                >>> # ---
                >>> try:
                ...   import Rm
                ... except ImportError:                   
                ...   from PT3S import Rm
                >>> # ---
                >>> xm=xms['DHNetwork']
                >>> #mx=mxs['DHNetwork']                  
                >>> # ---
                >>> plt.close()
                >>> size_DINA3quer=(16.5, 11.7) 
                >>> dpiSize=72
                >>> fig=plt.figure(figsize=size_DINA3quer,dpi=dpiSize)         
                >>> gs = gridspec.GridSpec(4, 2)
                >>> # ---
                >>> vROHR=xm.dataFrames['vROHR']                 
                >>> # ---                               
                >>> # Attribute (with neg. Values)
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[0])              
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttribute='ROHR~*~*~*~QMAV'
                ...     )     
                >>> txt=axNfd.set_title('RL QMAV')
                >>> # ---
                >>> # Function as Attribute
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[1])              
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     )
                >>> txt=axNfd.set_title('RL QMAV Abs')
                >>> # --------------------------
                >>> # ---
                >>> # Mi/MaD zS auf
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[2])              
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     ,pAttributeColorMapMin=0.
                ...     ,pAttributeColorMapMax=1600.
                ...     ,CBLabel='Q [t/h]'            
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True                 
                ...     )
                >>> txt=axNfd.set_title('Mi/MaD zS auf')
                >>> # --------------------------
                >>> # ---
                >>> # ind. Kategorien 
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[3])           
                >>> cm = matplotlib.colors.ListedColormap(['cyan', 'royalblue', 'magenta', 'coral'])
                >>> cm.set_over('0.25')
                >>> cm.set_under('0.75')
                >>> bounds = [10.,100.,200.,800.,1600.]
                >>> norm = matplotlib.colors.BoundaryNorm(bounds, cm.N)
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])     
                ...     ,pAttributeColorMap=cm
                ...     ,CBBinBounds=bounds                              
                ...     ,CBLabel='Q [t/h]'    
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True                   
                ...     )              
                >>> txt=axNfd.set_title('ind. Kategorien')
                >>> # --------------------------
                >>> # ---
                >>> # Unwichtiges ausblenden über 2nd Color
                >>> # --------------------------
                >>> vAGSN=xm.dataFrames['vAGSN']    
                >>> hpRL=vAGSN[(vAGSN['LFDNR']=='1') & (vAGSN['Layer']==2)]               
                >>> pDf=pd.merge(vROHR
                ...     ,hpRL[hpRL.IptIdx=='S'] # wg. Innenpunkte 
                ...     ,how='left'
                ...     ,left_on='pk'
                ...     ,right_on='OBJID'
                ...     ,suffixes=('','_AGSN')).filter(items=vROHR.columns.tolist()+['OBJID'])
                >>> axNfd = fig.add_subplot(gs[4])              
                >>> Rm.Rm.pltNetPipes(pDf
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     ,pAttributeColorMapMin=0.
                ...     ,pAttributeColorMapMax=1500.
                ...     ,CBBinTicks=7 
                ...     ,CBLabel='Q [t/h]'    
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True       
                ...     ,pAttributeColorMapFmask=lambda row: True if not pd.isnull(row.OBJID) else False 
                ...     ,pAttributeColorMap2ndFmask=lambda row: True if pd.isnull(row.OBJID) else False                 
                ...     )
                >>> txt=axNfd.set_title('Unwichtiges ausblenden über 2nd Color')
                >>> # --------------------------
                >>> # ---
                >>> # Farbskalen an den Rändern abschneiden
                >>> # --------------------------              
                >>> axNfd = fig.add_subplot(gs[5])              
                >>> Rm.Rm.pltNetPipes(pDf
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])                
                ...     ,pAttributeColorMapMin=0.
                ...     ,pAttributeColorMapMax=1500.
                ...     ,CBLabel='Q [t/h]'    
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True       
                ...     ,pAttributeColorMapFmask=lambda row: True if not pd.isnull(row.OBJID) else False 
                ...     ,pAttributeColorMap2ndFmask=lambda row: True if pd.isnull(row.OBJID) else False 
                ...     ,pAttributeColorMap2ndUsageStart=.5/5. # nicht zu weiß 
                ...     ,pAttributeColorMap2ndUsageEnd=2.5/5. # nicht zu schwarz
                ...     ,pAttributeColorMapUsageStart=3/15.
                ...     ,pAttributeColorMapUsageEnd=12/15.                
                ...     )
                >>> txt=axNfd.set_title('Farbskalen an den Rändern abschneiden')
                >>> # --------------------------
                >>> # ---
                >>> # Farbskala diskretisieren
                >>> # --------------------------              
                >>> axNfd = fig.add_subplot(gs[6])              
                >>> Rm.Rm.pltNetPipes(pDf
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])                
                ...     ,pAttributeColorMapMin=0.
                ...     ,pAttributeColorMapMax=1500.
                ...     ,CBBinDiscrete=True 
                ...     ,CBLabel='Q [t/h]'    
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True       
                ...     ,pAttributeColorMapFmask=lambda row: True if not pd.isnull(row.OBJID) else False 
                ...     ,pAttributeColorMap2ndFmask=lambda row: True if pd.isnull(row.OBJID) else False        
                ...     ,pAttributeColorMap2ndUsageStart=.5/5. # nicht zu weiß 
                ...     ,pAttributeColorMap2ndUsageEnd=2.5/5. # nicht zu schwarz      
                ...     ,CBTicks=[250,750,1250]
                ...     ,CBTickLabels=['klein','mittel','groß']
                ...     )
                >>> txt=axNfd.set_title('Farbskala diskretisieren')
                >>> # --------------------------
                >>> # ---
                >>> # Unterkategorien
                >>> # --------------------------              
                >>> baseColorsDef="tab10"
                >>> catagoryColors=[9,6,1]
                >>> nOfSubCatsReq=4
                >>> cm=Rm.pltMakeCategoricalCmap(baseColorsDef=baseColorsDef,catagoryColors=catagoryColors,nOfSubCatsReq=nOfSubCatsReq,reversedSubCatOrder=True)
                >>> axNfd = fig.add_subplot(gs[7])              
                >>> Rm.Rm.pltNetPipes(pDf
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     ,pAttributeColorMap=cm
                ...     ,pAttributeColorMapMin=0.
                ...     ,pAttributeColorMapMax=1500.
                ...     ,CBBinTicks=16
                ...     ,CBLabel='Q [t/h]'    
                ...     ,sort_values_by=['pAttributeFunc'] 
                ...     ,sort_values_ascending=True       
                ...     ,pAttributeColorMapFmask=lambda row: True if not pd.isnull(row.OBJID) else False 
                ...     ,pAttributeColorMap2ndFmask=lambda row: True if pd.isnull(row.OBJID) else False     
                ...     ,pAttributeColorMap2ndUsageStart=.5/5. # nicht zu weiß 
                ...     ,pAttributeColorMap2ndUsageEnd=2.5/5. # nicht zu schwarz                
                ...     )
                >>> txt=axNfd.set_title('Unterkategorien')
                >>> # --------------------------
                >>> gs.tight_layout(fig)
                >>> plt.show()
                >>> plt.savefig('pltNetPipes.pdf',format='pdf',dpi=dpiSize*2)
                >>> # -----
                >>> plt.close()
                >>> fig=plt.figure(figsize=Rm.DINA3q,dpi=dpiSize)         
                >>> gs = gridspec.GridSpec(1, 1)
                >>> # ---
                >>> # 
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[0])  
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' and row.LTGR_NAME=='NWDUF2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     )
                >>> txt=axNfd.set_title('RL QMAV Abs (Ausschnitt)')      
                >>> gs.tight_layout(fig)
                >>> plt.show()               
                >>> # -----
                >>> plt.close()
                >>> fig=plt.figure(figsize=Rm.DINA3,dpi=dpiSize)         
                >>> gs = gridspec.GridSpec(1, 1)
                >>> # ---
                >>> # 
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[0])  
                >>> Rm.Rm.pltNetPipes(vROHR
                ...     ,query="CONT_ID == '1001'"
                ...     ,fmask=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' and row.LTGR_NAME=='NWDUF2' else False 
                ...     ,pAx=axNfd
                ...     ,pAttributeFunc=lambda row: math.fabs(row['ROHR~*~*~*~QMAV'])
                ...     )
                >>> txt=axNfd.set_title('RL QMAV Abs (Ausschnitt)')      
                >>> gs.tight_layout(fig)
                >>> plt.show()                                
        """
        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
                keys = sorted(kwds.keys())
                
                # AXES
                if 'pAx' not in keys:
                    kwds['pAx']=plt.gca()
                
                # CB
                if 'CBFraction' not in keys:
                    kwds['CBFraction']=5 # in %
                if 'CBHpad' not in keys:
                    kwds['CBHpad']=0.05         
                if 'CBLabel' not in keys:
                    kwds['CBLabel']=None       
                # CB / Farbskala
                if 'CBBinTicks' not in keys:
                    kwds['CBBinTicks']=None         
                if 'CBBinDiscrete' not in keys:
                    kwds['CBBinDiscrete']=False     
                if  kwds['CBBinDiscrete']:
                    if kwds['CBBinTicks']==None:                                           
                        kwds['CBBinTicks']=4 # (d.h. 3 Kategorien)
                if 'CBBinBounds' not in keys:
                    kwds['CBBinBounds']=None

                # customized yTicks
                if 'CBTicks' not in keys:
                    kwds['CBTicks'] = None           
                if 'CBTickLabels' not in keys:
                    kwds['CBTickLabels'] = None 
            
                # DATA
                if 'query' not in keys:
                    kwds['query']=None # Exp.: = "KVR_i=='2' & KVR_k=='2'"
                if 'fmask' not in keys:
                    kwds['fmask']=None # Exp.: =lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False                    
                if 'sort_values_by' not in keys:
                    kwds['sort_values_by']=None  
                if 'sort_values_ascending' not in keys:
                    kwds['sort_values_ascending']=False                   

                # PIPE-Attribute
                if 'pAttribute' not in keys:                   
                    kwds['pAttribute']='Attribute'
                    if 'pAttributeFunc' not in keys:            
                        logger.debug("{:s}pAttribute: not specified?! 'Attribute' will be used. pAttributeFunc is also not specified?!".format(logStr))                  
                if 'pAttributeFunc' not in keys:                    
                    kwds['pAttributeFunc']=None     
                    
                # PIPE-Color
                if 'pAttributeColorMap' not in keys:
                    kwds['pAttributeColorMap']=plt.cm.cool                        
                if 'pAttributeColorMapMin' not in keys:           
                    kwds['pAttributeColorMapMin']=None
                if 'pAttributeColorMapMax' not in keys:
                    kwds['pAttributeColorMapMax']=None

                # Trunc Cmap
                if 'pAttributeColorMapUsageStart' not in keys and 'pAttributeColorMapUsageEnd' not in keys:
                    kwds['pAttributeColorMapTrunc']=False
                else:
                    kwds['pAttributeColorMapTrunc']=True
                if 'pAttributeColorMapUsageStart' not in keys:
                    kwds['pAttributeColorMapUsageStart']=0.     
                if 'pAttributeColorMapUsageEnd' not in keys:
                    kwds['pAttributeColorMapUsageEnd']=1.     

                # PIPE-Color 1st/2nd - FMasks
                if 'pAttributeColorMapFmask' not in keys:                    
                    kwds['pAttributeColorMapFmask']=lambda row: True           
                else:
                     logger.debug("{:s}Color 1st-PIPEs are filtered with fmask: {:s} ...".format(logStr,str(kwds['pAttributeColorMapFmask'])))   
                if 'pAttributeColorMap2ndFmask' not in keys:
                    kwds['pAttributeColorMap2ndFmask']=lambda row: False    
                else:
                    logger.debug("{:s}Color 2nd-PIPEs are filtered with fmask: {:s} ...".format(logStr,str(kwds['pAttributeColorMap2ndFmask'])))   
                    
                # PIPE-Color 2nd
                if 'pAttributeColorMap2nd' not in keys:
                    kwds['pAttributeColorMap2nd']=plt.cm.binary                        
                if 'pAttributeColorMap2ndMin' not in keys:
                    kwds['pAttributeColorMap2ndMin']=kwds['pAttributeColorMapMin']
                if 'pAttributeColorMap2ndMax' not in keys:
                    kwds['pAttributeColorMap2ndMax']=kwds['pAttributeColorMapMax']

                # Trunc Cmap
                if 'pAttributeColorMap2ndUsageStart' not in keys and 'pAttributeColorMap2ndUsageEnd' not in keys:
                    kwds['pAttributeColorMap2ndTrunc']=False
                else:
                    kwds['pAttributeColorMap2ndTrunc']=True

                if 'pAttributeColorMap2ndUsageStart' not in keys:
                    kwds['pAttributeColorMap2ndUsageStart']=0.  
                if 'pAttributeColorMap2ndUsageEnd' not in keys:
                    kwds['pAttributeColorMap2ndUsageEnd']=1.  

                # PIPE-Linestyle
                if 'pAttributeLs' not in keys:
                    kwds['pAttributeLs']='-'           

                # PIPE-Linesize
                if 'pAttrLineSize' not in keys:                    
                    kwds['pAttrLineSize']=None       
                if 'pAttrLineSizeFactor' not in keys:
                    kwds['pAttrLineSizeFactor']=None  

                # PIPE-Geometry
                if 'pWAYPXCors' not in keys:
                    kwds['pWAYPXCors']='pWAYPXCors'
                if 'pWAYPYCors' not in keys:
                    kwds['pWAYPYCors']='pWAYPYCors'
                if 'pClip' not in keys:
                    kwds['pClip']=True

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                     
        
        try: 
                               
            # ggf. filtern
            if kwds['query'] != None:                    
                logger.debug("{:s}pDf is filtered with query: {:s} ...".format(logStr,str(kwds['query'])))   
                pDf=pd.DataFrame(pDf.query(kwds['query']).values,columns=pDf.columns)
            if kwds['fmask'] != None:
                logger.debug("{:s}pDf is filtered with fmask: {:s} ...".format(logStr,str(kwds['fmask'])))   
                pDf=pd.DataFrame(pDf[pDf.apply(kwds['fmask'],axis=1)].values,columns=pDf.columns)         
                              
            # ggf. zu plottende Spalte(n) neu ausrechnen bzw. Plotreihenfolge ändern: Kopie erstellen
            if kwds['pAttributeFunc'] != None or kwds['sort_values_by'] != None:
                # Kopie!
                logger.debug("{:s}pDf is copied ...".format(logStr))   
                pDf=pDf.copy(deep=True)              
        
            # ggf. zu plottende Spalte(n) neu ausrechnen
            if kwds['pAttributeFunc'] != None:                 
                logger.debug("{:s}pAttribute: col '{:s}' is not used: ...".format(logStr,kwds['pAttribute']))  
                logger.debug("{:s}... pAttributeFunc {:s} is used to calculate a new col named 'pAttributeFunc'".format(logStr,str(kwds['pAttributeFunc'])))               
                pDf['pAttributeFunc']=pDf.apply(kwds['pAttributeFunc'],axis=1)
                kwds['pAttribute']='pAttributeFunc'
            logger.debug("{:s}col '{:s}' is used as Attribute.".format(logStr,kwds['pAttribute']))  
            
            # Label für CB
            if kwds['CBLabel'] == None:
                kwds['CBLabel']=kwds['pAttribute']

            # Spalte für Liniendicke ermitteln
            if kwds['pAttrLineSize'] == None:
                kwds['pAttrLineSize']=kwds['pAttribute']
            logger.debug("{:s}col '{:s}' is used as  LineSize.".format(logStr,kwds['pAttrLineSize']))  
            # Liniendicke skalieren  
            if kwds['pAttrLineSizeFactor']==None:
                kwds['pAttrLineSizeFactor']=1./(pDf[kwds['pAttrLineSize']].std()*2.)    
            logger.debug("{:s}Faktor Liniendicke: {:12.6f} - eine Linie mit Attributwert {:6.2f} wird in {:6.2f} Pts Dicke geplottet.".format(logStr
                                                                                                                                       ,kwds['pAttrLineSizeFactor']
                                                                                                                                       ,pDf[kwds['pAttrLineSize']].std()*2.
                                                                                                                                       ,kwds['pAttrLineSizeFactor']*pDf[kwds['pAttrLineSize']].std()*2.
                                                                                                                                       ))  
            logger.debug("{:s}min. Liniendicke: Attributwert {:9.2f} Pts: {:6.2f}.".format(logStr
                                                                                   ,math.fabs(pDf[kwds['pAttrLineSize']].min())
                                                                                   ,kwds['pAttrLineSizeFactor']*math.fabs(pDf[kwds['pAttrLineSize']].min()))
                                                                                   )
            logger.debug("{:s}max. Liniendicke: Attributwert {:9.2f} Pts: {:6.2f}.".format(logStr
                                                                                   ,math.fabs(pDf[kwds['pAttrLineSize']].max())
                                                                                   ,kwds['pAttrLineSizeFactor']*math.fabs(pDf[kwds['pAttrLineSize']].max()))
                                                                                   )
                                                                               
            # ggf. Plotreihenfolge ändern
            if kwds['sort_values_by'] != None:            
                logger.debug("{:s}pDf is sorted (=Plotreihenfolge) by {:s} ascending={:s}.".format(logStr,str(kwds['sort_values_by']),str(kwds['sort_values_ascending'])))  
                pDf.sort_values(by=kwds['sort_values_by'],ascending=kwds['sort_values_ascending'],inplace=True)
                
            # ----------------------------------------------------------------------------------------------------------------------------------------
            # x,y-Achsen: Lims ermitteln und setzen  (das Setzen beeinflusst Ticks und data_ratio; ohne dieses Setzen wären diese auf Standardwerten)      
            # ----------------------------------------------------------------------------------------------------------------------------------------                                                        
            xMin=923456789          
            yMin=923456789  
            xMax=0          
            yMax=0
            for xs,ys in zip(pDf[kwds['pWAYPXCors']],pDf[kwds['pWAYPYCors']]):
                xMin=min(xMin,min(xs))
                yMin=min(yMin,min(ys))
                xMax=max(xMax,max(xs))
                yMax=max(yMax,max(ys))                                                 
            logger.debug("{:s}pWAYPXCors: {:s} Min: {:6.2f} Max: {:6.2f}".format(logStr,kwds['pWAYPXCors'],xMin,xMax))   
            logger.debug("{:s}pWAYPYCors: {:s} Min: {:6.2f} Max: {:6.2f}".format(logStr,kwds['pWAYPYCors'],yMin,yMax))  
            dx=xMax-xMin
            dy=yMax-yMin
            dxdy=dx/dy
            dydx=1./dxdy

            # i.d.R. "krumme" Grenzen (die Ticks werden von mpl i.d.R. trotzdem "glatt" ermittelt)
            kwds['pAx'].set_xlim(xMin,xMax)
            kwds['pAx'].set_ylim(yMin,yMax)         
                          
            # ----------------------------------------------------------------------------------------------------------------------------------------
            # x,y-Achsen: Ticks ermitteln aber NICHT verändern   -----------------------------------------------------------------
            # auch bei "krummen" Grenzen setzt matplotlib i.d.R. "glatte" Ticks
            # ----------------------------------------------------------------------------------------------------------------------------------------
            
            # Ticks ermitteln
            xTicks=kwds['pAx'].get_xticks()
            yTicks=kwds['pAx'].get_yticks()
            dxTick = xTicks[1]-xTicks[0]
            xTickSpan=xTicks[-1]-xTicks[0]
            dyTick = yTicks[1]-yTicks[0]
            yTickSpan=yTicks[-1]-yTicks[0]

            logger.debug("{:s}xTicks    : {:s} dx: {:6.2f}".format(logStr,str(xTicks),dxTick))   
            logger.debug("{:s}yTicks    : {:s} dy: {:6.2f}".format(logStr,str(yTicks),dyTick))  

            # dTick gleich setzen (deaktiviert)
            if dyTick == dxTick:
                pass # nichts zu tun
            elif dyTick > dxTick:
                # dyTick zu dxTick (kleinere) setzen
                dTickW=dxTick
                # erf. Anzahl
                numOfTicksErf=math.floor(dy/dTickW)+1
                newTicks=[idx*dTickW+yTicks[0] for idx in range(numOfTicksErf)]
                #kwds['pAx'].set_yticks(newTicks)  
                #yTicks=kwds['pAx'].get_yticks()               
                #dyTick = yTicks[1]-yTicks[0]
                #logger.debug("{:s}yTicks NEU: {:s} dy: {:6.2f}".format(logStr,str(yTicks),dyTick))  
            else:
                # dxTick zu dyTick (kleinere) setzen
                dTickW=dyTick
                # erf. Anzahl
                numOfTicksErf=math.floor(dx/dTickW)+1
                newTicks=[idx*dTickW+xTicks[0] for idx in range(numOfTicksErf)]
                #kwds['pAx'].set_xticks(newTicks)    
                #xTicks=kwds['pAx'].get_xticks()               
                #dxTick = xTicks[1]-xTicks[0]               
                #logger.debug("{:s}xTicks NEU: {:s} dx: {:6.2f}".format(logStr,str(xTicks),dxTick)) 
            
            # ----------------------------------------------------------------------------------------------------------------------------------------
            # Grid und Aspect            
            # ----------------------------------------------------------------------------------------------------------------------------------------            
            kwds['pAx'].grid()
            kwds['pAx'].set_aspect(aspect='equal') # zur Sicherheit; andere als verzerrungsfreie Darstellungen machen im Netz kaum Sinn
            kwds['pAx'].set_adjustable('box')
            kwds['pAx'].set_anchor('SW')

            ## x,y-Seitenverhältnisse ermitteln ---------------------------------------------------------------------------   
            ## total figure size
            #figW, figH = kwds['pAx'].get_figure().get_size_inches()
            ## Axis pos. on figure
            #x0, y0, w, h = kwds['pAx'].get_position().bounds
            ## Ratio of display units
            #disp_ratio = (figH * h) / (figW * w)
            #disp_ratioA = (figH) / (figW )
            #disp_ratioB = (h) / (w)
            ## Ratio of data units
            #data_ratio=kwds['pAx'].get_data_ratio()
            #logger.debug("{:s}figW: {:6.2f} figH: {:6.2f}".format(logStr,figW,figH))  
            #logger.debug("{:s}x0: {:6.2f} y0: {:6.2f} w: {:6.2f} h: {:6.2f}".format(logStr,x0,y0,w,h))  
            #logger.debug("{:s}pWAYPCors: Y/X: {:6.2f}".format(logStr,dydx))  
            #logger.debug("{:s}Ticks:     Y/X: {:6.2f}".format(logStr,yTickSpan/xTickSpan))  
            #logger.debug("{:s}disp_ratio:     {:6.2f} data_ratio:  {:6.2f}".format(logStr,disp_ratio,data_ratio))  
            #logger.debug("{:s}disp_ratioA:    {:6.2f} disp_ratioB: {:6.2f}".format(logStr,disp_ratioA,disp_ratioB))  
                                 
            # PIPE-Color: Farbskalamapping:
            cMap=plt.cm.get_cmap(kwds['pAttributeColorMap'])
            if kwds['CBBinDiscrete'] and hasattr(cMap,'from_list'): # diskrete Farbskala aus kontinuierlicher erzeugen                                
                N=kwds['CBBinTicks']-1
                color_list = cMap(np.linspace(0, 1, N))
                cmap_name = cMap.name + str(N)
                kwds['pAttributeColorMap']=cMap.from_list(cmap_name, color_list, N)            
            
            minAttr=pDf[kwds['pAttribute']].min()      
            maxAttr=pDf[kwds['pAttribute']].max()  
            if kwds['pAttributeColorMapMin'] != None:
                minLine=kwds['pAttributeColorMapMin']
            else:
                minLine=minAttr
            if kwds['pAttributeColorMapMax'] != None:
                maxLine=kwds['pAttributeColorMapMax']
            else:
                maxLine=maxAttr                  
            logger.debug("{:s}Attribute: minLine (used for CM-Scaling): {:8.2f} min (Data): {:8.2f}".format(logStr,minLine,minAttr))
            logger.debug("{:s}Attribute: maxLine (used for CM-Scaling): {:8.2f} max (Data): {:8.2f}".format(logStr,maxLine,maxAttr))

            # Norm
            normLine=colors.Normalize(minLine,maxLine)

            # kont. Farbskala truncated: Farbskala und Norm anpassen
            cMap=plt.cm.get_cmap(kwds['pAttributeColorMap'])   
            if kwds['pAttributeColorMapTrunc'] and hasattr(cMap,'from_list'):   

                #
                usageStartLineValue=minLine+kwds['pAttributeColorMapUsageStart']*(maxLine-minLine)
                usageStartLineColor=kwds['pAttributeColorMap'](normLine(usageStartLineValue)) 
                logger.debug("{:s}pAttributeColorMapUsageStart: {:6.2f} ==> usageStartLineValue: {:8.2f} (minLine: {:8.2f}) color: {:s}".format(logStr
                                                                                                                                    ,kwds['pAttributeColorMapUsageStart']
                                                                                                                                    ,usageStartLineValue,minLine,str(usageStartLineColor)))
                #
                usageEndLineValue=maxLine-(1.-kwds['pAttributeColorMapUsageEnd'])*(maxLine-minLine)
                usageEndLineColor=kwds['pAttributeColorMap'](normLine(usageEndLineValue)) 
                logger.debug("{:s}pAttributeColorMapUsageEnd:   {:6.2f} ==> usageEndLineValue:   {:8.2f} (maxLine: {:8.2f}) color: {:s}".format(logStr
                                                                                                                                    ,kwds['pAttributeColorMapUsageEnd']                                          
                                                                                                                                    ,usageEndLineValue,maxLine,str(usageEndLineColor)))
            
                nColors=100
                kwds['pAttributeColorMap'] = colors.LinearSegmentedColormap.from_list(
                'trunc({n},{a:.2f},{b:.2f})'.format(n=cMap.name, a=kwds['pAttributeColorMapUsageStart'], b=kwds['pAttributeColorMapUsageEnd'])
                ,cMap(np.linspace(kwds['pAttributeColorMapUsageStart'],kwds['pAttributeColorMapUsageEnd'],nColors)))
                
                normLine=colors.Normalize(max(minLine,usageStartLineValue),min(maxLine,usageEndLineValue))
            
            # diskrete Farbskala mit individuellen Kategorien: Norm anpassen
            
            cMap=plt.cm.get_cmap(kwds['pAttributeColorMap'])   
            if kwds['CBBinBounds'] != None and not hasattr(cMap,'from_list'): # diskrete Farbskala liegt vor und Bounds sind vorgegeben
                normLine = colors.BoundaryNorm(kwds['CBBinBounds'],cMap.N)
                #CBPropExtend='both'
                CBPropExtend='neither'
            else:
                CBPropExtend='neither'
                
            # PIPE-Color 2nd: Farbskalamapping:        
            if kwds['pAttributeColorMap2ndMin'] != None:
                minLine2nd=kwds['pAttributeColorMap2ndMin']
            else:
                minLine2nd=minAttr
            if kwds['pAttributeColorMap2ndMax'] != None:
                maxLine2nd=kwds['pAttributeColorMap2ndMax']
            else:
                maxLine2nd=maxAttr                  
            logger.debug("{:s}Attribute: minLine2nd (used for CM-Scaling): {:8.2f} min (Data): {:8.2f}".format(logStr,minLine2nd,minAttr))
            logger.debug("{:s}Attribute: maxLine2nd (used for CM-Scaling): {:8.2f} max (Data): {:8.2f}".format(logStr,maxLine2nd,maxAttr))

            # Norm
            normLine2nd=colors.Normalize(minLine2nd,maxLine2nd)

            # kont. Farbskala truncated: Farbskala anpassen
            cMap=plt.cm.get_cmap(kwds['pAttributeColorMap2nd'])   
            if kwds['pAttributeColorMap2ndTrunc'] and hasattr(cMap,'from_list'):   

                #
                usageStartLineValue2nd=minLine2nd+kwds['pAttributeColorMap2ndUsageStart']*(maxLine2nd-minLine2nd)
                logger.debug("{:s}pAttributeColorMap2ndUsageStart: {:8.2f} ==> usageStartLineValue2nd: {:8.2f} (minLine2nd: {:8.2f})".format(logStr,kwds['pAttributeColorMap2ndUsageStart'],usageStartLineValue2nd,minLine2nd))
                usageStartLineColor2nd=kwds['pAttributeColorMap2nd'](normLine2nd(usageStartLineValue2nd))      
                #
                usageEndLineValue2nd=maxLine2nd-(1.-kwds['pAttributeColorMap2ndUsageEnd'])*(maxLine2nd-minLine2nd)
                logger.debug("{:s}pAttributeColorMap2ndUsageEnd:   {:8.2f} ==> usageEndLineValue2nd:   {:8.2f} (maxLine2nd: {:8.2f})".format(logStr,kwds['pAttributeColorMap2ndUsageEnd'],usageEndLineValue2nd,maxLine2nd))
                usageEndLineColor2nd=kwds['pAttributeColorMap2nd'](normLine2nd(usageEndLineValue2nd))      


                nColors=100
                kwds['pAttributeColorMap2nd'] = colors.LinearSegmentedColormap.from_list(
                'trunc({n},{a:.2f},{b:.2f})'.format(n=cMap.name, a=kwds['pAttributeColorMap2ndUsageStart'], b=kwds['pAttributeColorMap2ndUsageEnd'])
                ,cMap(np.linspace(kwds['pAttributeColorMap2ndUsageStart'],kwds['pAttributeColorMap2ndUsageEnd'],nColors)))
          
            # PIPE-Color 2nd: PLOT           
            pDfColorMap2nd=pDf[pDf.apply(kwds['pAttributeColorMap2ndFmask'],axis=1)]
            (rows   ,cols)=pDf.shape
            (rows2nd,cols)=pDfColorMap2nd.shape
            logger.debug("{:s}Color 2nd-PIPEs: {:d} von {:d}".format(logStr,rows2nd,rows))   
            for xs,ys,vLine,tLine in zip(pDfColorMap2nd[kwds['pWAYPXCors']],pDfColorMap2nd[kwds['pWAYPYCors']],pDfColorMap2nd[kwds['pAttribute']],pDfColorMap2nd[kwds['pAttrLineSize']]):        


                #if vLine >= usageStartLineValue2nd and vLine <= usageEndLineValue2nd:
                #    colorLine=kwds['pAttributeColorMap2nd'](normLine2nd(vLine))                     
                #elif vLine > usageEndLineValue2nd:
                #    colorLine=usageEndLineColor2nd                   
                #else:
                #    colorLine=usageStartLineColor2nd        
                    
                colorLine=kwds['pAttributeColorMap2nd'](normLine2nd(vLine))     

                pcLines=kwds['pAx'].plot(xs,ys
                                ,color=colorLine
                                ,linewidth=kwds['pAttrLineSizeFactor']*math.fabs(tLine)#(vLine) 
                                ,ls=kwds['pAttributeLs']
                                ,solid_capstyle='round'                             
                                ,aa=True
                                ,clip_on=kwds['pClip']
                               )  
                  
            # PIPE-Color: PLOT            
            pDfColorMap=pDf[pDf.apply(kwds['pAttributeColorMapFmask'],axis=1)]  
            (rows   ,cols)=pDf.shape
            (rows1st,cols)=pDfColorMap.shape
            colorsCBValues=[]
            logger.debug("{:s}Color 1st-PIPEs: {:d} von {:d}".format(logStr,rows1st,rows))               
            for xs,ys,vLine,tLine in zip(pDfColorMap[kwds['pWAYPXCors']],pDfColorMap[kwds['pWAYPYCors']],pDfColorMap[kwds['pAttribute']],pDfColorMap[kwds['pAttrLineSize']]):        

                #if vLine >= usageStartLineValue and vLine <= usageEndLineValue:
                #    colorLine=kwds['pAttributeColorMap'](normLine(vLine))      
                #    value=vLine
                #elif vLine > usageEndLineValue:
                #    colorLine=usageEndLineColor   
                #    value=usageEndLineValue
                #else:
                #    colorLine=usageStartLineColor   
                #    value=usageStartLineValue
                               
                colorLine=kwds['pAttributeColorMap'](normLine(vLine))                      
                colorsCBValues.append(vLine)           
                
                pcLines=kwds['pAx'].plot(xs,ys
                                ,color=colorLine
                                ,linewidth=kwds['pAttrLineSizeFactor']*math.fabs(tLine)#(vLine) 
                                ,ls=kwds['pAttributeLs']
                                ,solid_capstyle='round'                             
                                ,aa=True
                                ,clip_on=kwds['pClip']
                               )   
            

            # PIPE-Color: PLOT der PIPE-Anfänge um Farbskala konstruieren zu koennen  
            xScatter=[]
            yScatter=[]
            for xs,ys in zip(pDfColorMap[kwds['pWAYPXCors']],pDfColorMap[kwds['pWAYPYCors']]):
                xScatter.append(xs[0])
                yScatter.append(ys[0])
            s=kwds['pAttrLineSizeFactor']*pDfColorMap[kwds['pAttrLineSize']].apply(lambda x: math.fabs(x))     
            s=s.apply(lambda x: math.pow(x,2))  # https://stackoverflow.com/questions/14827650/pyplot-scatter-plot-marker-size   
            #pcN=kwds['pAx'].scatter(pDfColorMap['pXCor_i'],pDfColorMap['pYCor_i']         
            pcN=kwds['pAx'].scatter(xScatter,yScatter                                             
                    ,s=s
                    ,linewidth=0 # the linewidth of the marker edges
                    # Farbskala
                    ,cmap=kwds['pAttributeColorMap']
                    # Normierung Farbe                
                    ,norm=normLine
                    # Werte
                    ,c=colorsCBValues                                       
                    ,edgecolors='none'
                    ,clip_on=kwds['pClip']
                    )        
        
            # CB: Axes         
            divider = make_axes_locatable(kwds['pAx'])
            cax = divider.append_axes('right',size="{:f}%".format(kwds['CBFraction']),pad=kwds['CBHpad'])
            x0, y0, w, h = kwds['pAx'].get_position().bounds
            #logger.debug("{:s}ohne Änderung?!: x0: {:6.2f} y0: {:6.2f} w: {:6.2f} h: {:6.2f}".format(logStr,x0,y0,w,h))  
            kwds['pAx'].set_aspect(1.) #!
            x0, y0, w, h = kwds['pAx'].get_position().bounds
            #logger.debug("{:s}ohne Änderung?!: x0: {:6.2f} y0: {:6.2f} w: {:6.2f} h: {:6.2f}".format(logStr,x0,y0,w,h))  
                      
            # CB
            cB=plt.gcf().colorbar(pcN, cax=cax, orientation='vertical',extend=CBPropExtend,spacing='proportional') 

            # Label
            cB.set_label(kwds['CBLabel'])

            # CB Ticks
            if kwds['CBBinTicks'] != None:
                cB.set_ticks(np.linspace(minLine,maxLine,kwds['CBBinTicks']))
                
            ticks=cB.get_ticks()     
            try:
                ticks=np.unique(np.append(ticks,[usageStartLineValue,usageEndLineValue]))
            except:
                pass
            cB.set_ticks(ticks)  

            # CB Ticklabels
            labels=cB.ax.get_yticklabels()

            if kwds['pAttributeColorMapUsageStart'] > 0:
                idx=np.where(ticks == usageStartLineValue)
                labels[idx[0][0]].set_text(labels[idx[0][0]].get_text()+" v=")
            if kwds['pAttributeColorMapUsageEnd'] < 1:
                idx=np.where(ticks == usageEndLineValue)
                labels[idx[0][0]].set_text(labels[idx[0][0]].get_text()+" ^=")

           
            if kwds['pAttributeColorMapMax'] != None and maxLine<maxAttr:
                labels[-1].set_text(labels[-1].get_text()+" >=")
            if kwds['pAttributeColorMapMin'] != None and minLine>minAttr:
                labels[0].set_text(labels[0].get_text()+" <=")

            cB.ax.set_yticklabels(labels)  

            # customized yTicks --------------------

            if kwds['CBTicks'] != None:                                
                cB.set_ticks(kwds['CBTicks'])  
            if kwds['CBTickLabels'] != None:              
                labels=cB.ax.get_yticklabels()
                if len(labels)==len(kwds['CBTickLabels']):
                    for label,labelNew in zip(labels,kwds['CBTickLabels']):
                        label.set_text(labelNew)
                    cB.ax.set_yticklabels(labels)  
                else:
                    logStrFinal="{:s}Error: Anz. CB Ticklabels Ist: {:d} != Anz. Ticklabeles Soll: {:d} ?!".format(logStr,len(labels),len(kwds['CBTickLabels']))
                    logger.error(logStrFinal) 
                    raise RmError(logStrFinal)     

        except RmError:
            raise
                                                                    
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                       
        finally:       
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))                   

    @classmethod
    def pltHP(cls,pDf,**kwds):
        """
        Plots a Hydraulic Profile.
        
        Args:
                DATA:
                    pDf: dataFrame

                defining the HPLINES (xy-curves) Identification:

                    the different HPs in pDf are identified by the two cols
                    NAMECol: default: 'NAME'; set to None if NAMECol is not criteria for Identification ...
                    and 
                    LayerCol: default: 'Layer'; set to None if LayerCol is not criteria for Identification ...

                    for each HP several lines (xy-curves) are plotted

                    ... not criteria ...
                    if NAMECol is None only LayerCol is used
                    if LayerCol also is None, all rows are treated as "the" HPLINE

                defining the HPLINES (xy-curves) Geometry:

                    * xCol: col in pDf for x; example: 'x'
                    the col is the same for all HPs and all y

                    * edgeNodesColSequence: cols to be used for start-node, end-node, next-node; default: ['NAME_i','NAME_k','nextNODE']

                    * 'NAME'_'Layer' (i.e. Nord-Süd_1)  NAMECol_LayerCol is used as an Index in hpLineGeoms

                    * hpLineGeoms - Example - = {
                    'V-Abzweig_1':{'masterHP':'AGFW Symposium DH_1','masterNode':'V-3107','matchType':'starts'}            
                    }
                    - masterHP: Bezugs-Schnitt
                    - masterNode: muss es      in masterHP geben
                    - masterNode: muss es auch im Schnitt  geben bei matchType='matches'; bei 'starts' wird der Anfang gemapped; bei 'ends' das Ende                    

                defining the HPLINES (xy-curves) y-Achsentypen (y-Axes):

                    * hpLines: list of cols in pDf for y;  example: ['P']
                    each col in hpLines defines a hpLine (a xy-curve) to be plotted 
                    for each identified HP all defined hpLines are plotted 

                defining the HPLINES (xy-curves) Layout:

                    # 'NAME'_'Layer'_'hpLineType' (i.e. Nord-Süd_1_P) is used as an Index in hpLineProps 

                    * hpLineProps - Example - = {
                        'Nord-Süd_1_P':{'label':'VL','color':'red' ,'linestyle':'-','linewidth':3}
                       ,'Nord-Süd_2_P':{'label':'RL','color':'blue','linestyle':'-','linewidth':3}        
                    }
                    
                    if 'NAME'_'Layer'_'hpLine' not in hpLineProps:
                        default props are used
                    if hpLineProps['NAME'_'Layer'_'hpLine'] == None:
                        HPLINE is not plotted

                    y-Achsentypen (y-Axes):
                        * werden ermittelt aus hpLines
                        * der Spaltenname - z.B. 'P' - wird dabei als Bezeichner für den Achsentyp benutzt
                        * die Achsen werden erstellt in der Reihenfolge in der sie in hpLines auftreten
                        * Bezeichner wie 'P','P_1',... werden dabei als vom selben Achsentyp 'P' (selbe y-Achse also) gewertet 
                        * P_1, P_2, ... können z.B. P zu verschiedenen Zeiten sein oder Aggregate über die Zeit wie Min/Max 
                        * yAxesDetectionPattern: regExp mit welcher die Achsentypen ermittelt werden; default: '([\w ]+)(_)(\d+)$'
                        * yTwinedAxesPosDeltaHPStart: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche; default: -0.0125
                        * yTwinedAxesPosDeltaHP: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche; default: -0.05
                                            
                AXES:
                    pAx: Axes to be plotted on; if not specified: gca() is used

        Return:
                yAxes: dct with AXES; key=y-Achsentypen
                yLines: dct with Line2Ds; key=Index from hpLineProps
                xNodeInfs: dct with NodeInformation; key=Index also used in i.e. hpLineGeoms
                    key: NAMECol_LayerCol
                    value: dct
                        key: node
                        value: dct
                            kwds['xCol']:        x in HP
                            kwds['xCol']+'Plot': x in HP-Plot
                            pDfIdx:              Index in pDf
                            
                >>> #  -q -m 0 -s pltHP -y no -z no -w DHNetwork
                >>> import pandas as pd
                >>> import matplotlib
                >>> import matplotlib.pyplot as plt
                >>> import matplotlib.gridspec as gridspec
                >>> import math
                >>> try:
                ...   import Rm
                ... except ImportError:                   
                ...   from PT3S import Rm
                >>> # ---
                >>> xm=xms['DHNetwork']       
                >>> mx=mxs['DHNetwork']   
                >>> xm.MxAdd(mx=mx,aggReq=['TIME','TMIN','TMAX'],timeReq=3*[mx.df.index[0]],timeReq2nd=3*[mx.df.index[-1]],viewList=['vAGSN'],ForceNoH5Update=True)
                >>> vAGSN=xm.dataFrames['vAGSN']
                >>> for PH,P,RHO,Z in zip(['PH','PH_1','PH_2'],['P','P_1','P_2'],['RHO','RHO_1','RHO_2'],['Z','Z_1','Z_2']):
                ...     vAGSN[PH]=vAGSN.apply(lambda row: row[P]*math.pow(10.,5.)/(row[RHO]*9.81),axis=1)
                ...     vAGSN[PH]=vAGSN[PH]+vAGSN[Z].astype('float64')
                >>> for bBzg,P,RHO,Z in zip(['bBzg','bBzg_1','bBzg_2'],['P','P_1','P_2'],['RHO','RHO_1','RHO_2'],['Z','Z_1','Z_2']):
                ...     vAGSN[bBzg]=vAGSN.apply(lambda row: row[RHO]*9.81/math.pow(10.,5.),axis=1)
                ...     vAGSN[bBzg]=vAGSN[P]+vAGSN[Z].astype('float64')*vAGSN[bBzg]                
                >>> plt.close()
                >>> fig=plt.figure(figsize=Rm.DINA3q,dpi=Rm.dpiSize)         
                >>> gs = gridspec.GridSpec(3, 1)
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[0])       
                >>> yAxes,yLines,xNodeInfs=Rm.Rm.pltHP(vAGSN,pAx=axNfd
                ... ,hpLines=['bBzg','bBzg_1','bBzg_2','Q']
                ... ,hpLineProps={
                ...     'AGFW Symposium DH_1_bBzg':{'label':'VL','color':'red' ,'linestyle':'-','linewidth':3}
                ...    ,'AGFW Symposium DH_2_bBzg':{'label':'RL','color':'blue','linestyle':'-','linewidth':3}                
                ...    ,'AGFW Symposium DH_2_bBzg_1':{'label':'RL min','color':'blue','linestyle':'-.','linewidth':1}
                ...    ,'AGFW Symposium DH_1_bBzg_2':{'label':'VL max','color':'red' ,'linestyle':'-.','linewidth':1}  
                ...    ,'AGFW Symposium DH_1_bBzg_1':None
                ...    ,'AGFW Symposium DH_2_bBzg_2':None  
                ...    ,'AGFW Symposium DH_1_Q':{'label':'VL Q','color':'magenta' ,'linestyle':'--','linewidth':2}
                ...    ,'AGFW Symposium DH_2_Q':{'label':'RL Q','color':'lightblue','linestyle':'--','linewidth':2}                          
                ... }
                ... )          
                >>> yAxes.keys()
                dict_keys(['bBzg', 'Q'])
                >>> yLines.keys()      
                dict_keys(['AGFW Symposium DH_1_bBzg', 'AGFW Symposium DH_1_bBzg_2', 'AGFW Symposium DH_1_Q', 'AGFW Symposium DH_2_bBzg', 'AGFW Symposium DH_2_bBzg_1', 'AGFW Symposium DH_2_Q'])
                >>> txt=axNfd.set_title('HP')  
                >>> gs.tight_layout(fig)
                >>> plt.show()        
                >>> ###
                >>> Rcuts=[
                ...  {'NAME':'R-Abzweig','nl':['R-3107','R-3427']}
                ... ,{'NAME':'R-EndsTest','nl':['R-HWSU','R-HKW3S']}
                ... ,{'NAME':'R-MatchesTest','nl':['R-HKW1','R-2104']}
                ... ]
                >>> Vcuts=[
                ...  {'NAME':'V-Abzweig','nl':['V-3107','V-3427']}
                ... ,{'NAME':'V-EndsTest','nl':['V-HWSU','V-HKW3S']}
                ... ,{'NAME':'V-MatchesTest','nl':['V-HKW1','V-2104']}
                ... ]
                >>> fV=lambda row: True if row.KVR_i=='1' and row.KVR_k=='1' else False
                >>> fR=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False                
                >>> for vcut,rcut in zip(Vcuts,Rcuts):
                ...     ret=xm.vAGSN_Add(nl=vcut['nl'],weight='L',Layer=1,AKTIV=None,NAME=vcut['NAME'],fmask=fV)
                ...     ret=xm.vAGSN_Add(nl=rcut['nl'],weight='L',Layer=2,AKTIV=None,NAME=rcut['NAME'],fmask=fR)
                >>> # Schnitte erneut mit Ergebnissen versorgen, da Schnitte neu definiert wurden
                >>> xm.MxAdd(mx=mx,ForceNoH5Update=True)
                >>> vAGSN=xm.dataFrames['vAGSN']
                >>> for PH,P,RHO,Z in zip(['PH'],['P'],['RHO'],['Z']):
                ...     vAGSN[PH]=vAGSN.apply(lambda row: row[P]*math.pow(10.,5.)/(row[RHO]*9.81),axis=1)
                ...     vAGSN[PH]=vAGSN[PH]+vAGSN[Z].astype('float64')
                >>> for bBzg,P,RHO,Z in zip(['bBzg'],['P'],['RHO'],['Z']):
                ...     vAGSN[bBzg]=vAGSN.apply(lambda row: row[RHO]*9.81/math.pow(10.,5.),axis=1)
                ...     vAGSN[bBzg]=vAGSN[P]+vAGSN[Z].astype('float64')*vAGSN[bBzg]            
                >>> plt.close()
                >>> fig=plt.figure(figsize=Rm.DINA3q,dpi=Rm.dpiSize)         
                >>> gs = gridspec.GridSpec(3, 1)
                >>> # --------------------------
                >>> axNfd = fig.add_subplot(gs[0])       
                >>> yAxes,yLines,xNodeInfs=Rm.Rm.pltHP(vAGSN[vAGSN['NAME'].isin(['R-Abzweig','V-Abzweig','AGFW Symposium DH','R-EndsTest','V-EndsTest','R-MatchesTest','V-MatchesTest'])],pAx=axNfd
                ... ,hpLines=['bBzg','Q']
                ... ,hpLineGeoms={
                ...    'V-Abzweig_1':{'masterHP':'AGFW Symposium DH_1','masterNode':'V-3107','matchType':'starts'}
                ...   ,'R-Abzweig_2':{'masterHP':'AGFW Symposium DH_2','masterNode':'R-3107','matchType':'starts'}
                ...   ,'V-EndsTest_1':{'masterHP':'AGFW Symposium DH_1','masterNode':'V-HKW3S','matchType':'ends'}
                ...   ,'R-EndsTest_2':{'masterHP':'AGFW Symposium DH_2','masterNode':'R-HKW3S','matchType':'ends'}
                ...   ,'V-MatchesTest_1':{'masterHP':'AGFW Symposium DH_1','masterNode':'V-1312','matchType':'matches','offset':-500}
                ...   ,'R-MatchesTest_2':{'masterHP':'AGFW Symposium DH_2','masterNode':'R-1312','matchType':'matches'}
                ... }
                ... ,hpLineProps={
                ...     'AGFW Symposium DH_1_bBzg':{'label':'VL','color':'red' ,'linestyle':'-','linewidth':3}
                ...    ,'AGFW Symposium DH_2_bBzg':{'label':'RL','color':'blue','linestyle':'-','linewidth':3}        
                ...    ,'AGFW Symposium DH_1_Q':{'label':'VL Q','color':'magenta' ,'linestyle':'--','linewidth':2}
                ...    ,'AGFW Symposium DH_2_Q':{'label':'RL Q','color':'lightblue','linestyle':'--','linewidth':2}                           
                ...    ,'V-Abzweig_1_bBzg':{'label':'VL','color':'tomato' ,'linestyle':'-','linewidth':3}
                ...    ,'R-Abzweig_2_bBzg':{'label':'RL','color':'plum' ,'linestyle':'-','linewidth':3}
                ...    ,'V-Abzweig_1_Q':{'label':'VL Q','color':'magenta' ,'linestyle':'--','linewidth':2}         
                ...    ,'R-Abzweig_2_Q':{'label':'VL Q','color':'lightblue' ,'linestyle':'--','linewidth':2}       
                ...    ,'V-EndsTest_1_bBzg':{'label':'VL','color':'lightcoral' ,'linestyle':'-','linewidth':3}
                ...    ,'R-EndsTest_2_bBzg':{'label':'RL','color':'aquamarine' ,'linestyle':'-','linewidth':3}
                ...    ,'V-EndsTest_1_Q':{'label':'VL Q','color':'magenta' ,'linestyle':'--','linewidth':2}         
                ...    ,'R-EndsTest_2_Q':{'label':'VL Q','color':'lightblue' ,'linestyle':'--','linewidth':2}       
                ...    #,'V-MatchesTest_1_bBzg':{'label':'VL','color':'orange' ,'linestyle':'-','linewidth':1}
                ...    ,'R-MatchesTest_2_bBzg':{'label':'RL','color':'slateblue' ,'linestyle':'-','linewidth':1}
                ...    ,'V-MatchesTest_1_Q':{'label':'VL Q','color':'magenta' ,'linestyle':'--','linewidth':2}         
                ...    ,'R-MatchesTest_2_Q':{'label':'VL Q','color':'lightblue' ,'linestyle':'--','linewidth':2}                       
                ... }
                ... )                        
                >>> txt=axNfd.set_title('HP')  
                >>> gs.tight_layout(fig)
                >>> plt.show()     
                >>> sorted(xNodeInfs.keys())
                ['AGFW Symposium DH_1', 'AGFW Symposium DH_2', 'R-Abzweig_2', 'R-EndsTest_2', 'R-MatchesTest_2', 'V-Abzweig_1', 'V-EndsTest_1', 'V-MatchesTest_1']
                >>> xNodeInf=xNodeInfs['R-Abzweig_2']
                >>> nl=Rcuts[0]['nl']
                >>> nodeInfS=xNodeInf[nl[0]]
                >>> nodeInfE=xNodeInf[nl[-1]]
                >>> sorted(nodeInfS.keys())
                ['pDfIdx', 'x', 'xPlot']
                >>> dxPlot=nodeInfE['xPlot']-nodeInfS['xPlot']
                >>> dxHP=nodeInfE['x']-nodeInfS['x']
                >>> dxPlot==dxHP
                True
                >>> nodeInfE['x']=round(nodeInfE['x'],3)
                >>> nodeInfE['xPlot']=round(nodeInfE['xPlot'],3)
                >>> {key:value for key,value in nodeInfE.items() if key not in ['pDfIdx']}          
                {'x': 3285.0, 'xPlot': 20312.428}
                >>> 
        """
        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
                keys = sorted(kwds.keys())
                
                # AXES
                if 'pAx' not in keys:
                    kwds['pAx']=plt.gca()

                if 'NAMECol' not in keys:
                    kwds['NAMECol']='NAME'
                if 'LayerCol' not in keys:
                    kwds['LayerCol']='Layer'

                if 'xCol' not in keys:
                    kwds['xCol']='x'
                if 'hpLines' not in keys:
                    kwds['hpLines']=['P']
                if 'hpLineProps' not in keys:
                    kwds['hpLineProps']={'NAME_1_P':{'label':'HP NAME Layer 1 P','color':'red','linestyle':'-','linewidth':3}}

                if 'hpLineGeoms' not in keys:
                    kwds['hpLineGeoms']=None 
                if 'edgeColSequence' not in keys:
                    kwds['edgeColSequence']=['NAME_i','NAME_k','nextNODE']  

                if 'yTwinedAxesPosDeltaHPStart' not in keys:
                     # (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche; default: -0.0125
                    kwds['yTwinedAxesPosDeltaHPStart']=-0.0125

                if 'yTwinedAxesPosDeltaHP' not in keys:
                     # (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche; default: -0.05
                    kwds['yTwinedAxesPosDeltaHP']=-0.05

                if 'yAxesDetectionPattern' not in keys:
                     #  regExp mit welcher die Achsentypen ermittelt werden
                    kwds['yAxesDetectionPattern']='([\w ]+)(_)(\d+)$'

                logger.debug("{:s}xCol:      {:s}.".format(logStr,kwds['xCol']))
                logger.debug("{:s}hpLines:     {:s}.".format(logStr,str(kwds['hpLines'])))
                logger.debug("{:s}hpLineProps: {:s}.".format(logStr,str(kwds['hpLineProps'])))
                logger.debug("{:s}hpLineGeoms: {:s}.".format(logStr,str(kwds['hpLineGeoms'])))
                logger.debug("{:s}edgeColSequence: {:s}.".format(logStr,str(kwds['edgeColSequence'])))
                logger.debug("{:s}yTwinedAxesPosDeltaHPStart: {:s}.".format(logStr,str(kwds['yTwinedAxesPosDeltaHPStart'])))
                logger.debug("{:s}yTwinedAxesPosDeltaHP: {:s}.".format(logStr,str(kwds['yTwinedAxesPosDeltaHP'])))
                logger.debug("{:s}yAxesDetectionPattern: {:s}.".format(logStr,str(kwds['yAxesDetectionPattern'])))

                # Schnitte und Layer ermitteln
                if kwds['NAMECol'] != None and kwds['LayerCol'] != None:
                    hPs=pDf[[kwds['NAMECol'],kwds['LayerCol']]].drop_duplicates()
                elif kwds['NAMECol'] != None:
                    hPs=pDf[[kwds['NAMECol']]].drop_duplicates()
                    hPs['Layer']=None
                elif kwds['LayerCol'] != None:
                    hPs=pDf[[kwds['LayerCol']]].drop_duplicates()
                    hPs['NAME']=None
                    hPs=hPs[['NAME','Layer']]
                else:
                    hPs=pd.DataFrame(data={'NAME':[None],'Layer':[None]})
                #logger.debug("{:s}hPs: {:s}.".format(logStr,hPs.to_string()))
                # hPs hat 2 Spalten: NAME und Layer

                # y-Achsen-Typen ermitteln
                hpLineTypesSequence=[col if re.search(kwds['yAxesDetectionPattern'],col)==None else re.search(kwds['yAxesDetectionPattern'],col).group(1) for col in kwds['hpLines']]          
                
                # y-Achsen konstruieren
                yAxes={}
                colType1st=hpLineTypesSequence[0]
                axHP=kwds['pAx'] 
                axHP.spines["left"].set_position(("axes",kwds['yTwinedAxesPosDeltaHPStart'] )) 

                axHP.set_ylabel(colType1st)  
                yAxes[colType1st]=axHP                  
                logger.debug("{:s}colType: {:s} is attached to Axes pcAx .".format(logStr,colType1st))
                for idx,colType in enumerate(hpLineTypesSequence[1:]):
                    if colType not in yAxes:    
                        yPos=kwds['yTwinedAxesPosDeltaHPStart']+kwds['yTwinedAxesPosDeltaHP']*len(yAxes)
                        logger.debug("{:s}colType: {:s}: new Axes_ yPos: {:1.4f} ...".format(logStr,colType,yPos))

                        # weitere y-Achse 
                        axHP = axHP.twinx()
                        axHP.spines["left"].set_position(("axes", yPos)) 
                        pltMakePatchSpinesInvisible(axHP)
                        axHP.spines['left'].set_visible(True)  
                        axHP.yaxis.set_label_position('left')
                        axHP.yaxis.set_ticks_position('left')
                        axHP.set_ylabel(colType)  
                        yAxes[colType]=axHP 

                yLines={}
                xNodeInfs={}
                for index,row in hPs.iterrows():
                    # über alle Schnitte (NAME) und Layer (Layer)   

                    def getKeyBaseAndDf(dfSource,col1Name,col2Name,col1Value,col2Value):             
                        
                        #logger.debug("{:s}getKeyBaseAndDf: dfSource: {:s} ...".format(logStr,dfSource[[col1Name,col2Name,'nextNODE']].to_string())) 

                        # dfSource bzgl. cols filtern
                        if col1Name != None and col2Name != None:
                            dfFiltered=dfSource[
                                (dfSource[col1Name].astype(str)==str(col1Value)) 
                                & 
                                (dfSource[col2Name].astype(str)==str(col2Value))
                                   ]
                            keyBase=str(row[col1Name])+'_'+str(col2Value)+'_'#+hpLine
                            logger.debug("{:s}getKeyBaseAndDf: Schnitt: {!s:s} Layer: {!s:s} ...".format(logStr,col1Value,col2Value)) 
                        elif col1Name != None:
                            dfFiltered=dfSource[
                                (dfSource[col1Name].astype(str)==str(col1Value))                       
                                   ]           
                            keyBase=str(col1Value)+'_'#+hpLine
                            logger.debug("{:s}getKeyBaseAndDf: Schnitt: {!s:s} ...".format(logStr,col1Value)) 
                        elif col2Name != None:
                            dfFiltered=dfSource[
                                (dfSource[col2Name].astype(str)==str(col2Value))                       
                                   ]        
                            keyBase=str(col2Value)+'_'#+hpLine
                            logger.debug("{:s}getKeyBaseAndDf: Layer: {!s:s} ...".format(logStr,col2Value)) 
                        else:
                            dfFiltered=dfSource
                            keyBase=''


                        #logger.debug("{:s}getKeyBaseAndDf: dfFiltered: {:s} ...".format(logStr,dfFiltered[[col1Name,col2Name,'nextNODE']].to_string())) 
                        return keyBase, dfFiltered

                    # Schnitt+Layer nach hPpDf filtern
                    keyBase,hPpDf=getKeyBaseAndDf(pDf
                                                  ,kwds['NAMECol'] # Spaltenname 1
                                                  ,kwds['LayerCol'] # Spaltenname 2
                                                  ,row[kwds['NAMECol']] # Spaltenwert 1
                                                  ,row[kwds['LayerCol']] # Spaltenwert 2
                                                  )

                    if hPpDf.empty:
                        logger.info("{:s}Schnitt: {!s:s} Layer: {!s:s}: NICHT in pDf ?! ...".format(logStr,row[kwds['NAMECol']],row[kwds['LayerCol']])) 
                        continue

                    xOffset=0
                    xOffsetStatic=0
                    xFactorStatic=1
                    if kwds['hpLineGeoms'] != None:
                        if keyBase.rstrip('_') in kwds['hpLineGeoms'].keys():
                            hpLineGeom=kwds['hpLineGeoms'][keyBase.rstrip('_')]
                            
                            logger.debug("{:s}Line: {:s}: hpLineGeom: {:s} ...".format(logStr,keyBase.rstrip('_'),str(hpLineGeom)))

                            if 'offset' in hpLineGeom.keys():
                                    xOffsetStatic=hpLineGeom['offset']          
                                    
                            if 'factor' in hpLineGeom.keys():
                                    xFactorStatic=hpLineGeom['factor']     
                                                            
                            if 'masterHP' in hpLineGeom.keys():
                                    masterHP=hpLineGeom['masterHP']
                                    name=masterHP.split('_')[0]
                                    layer=masterHP.replace(name,'')
                                    layer=layer.replace('_','')

                                    keyBaseMaster,hPpDfMaster=getKeyBaseAndDf(pDf
                                                  ,kwds['NAMECol'] # Spaltenname 1
                                                  ,kwds['LayerCol'] # Spaltenname 2
                                                  ,name # Spaltenwert 1
                                                  ,layer # Spaltenwert 2
                                                  )


                                    if 'masterNode' in hpLineGeom.keys():
                                        masterNode=hpLineGeom['masterNode']

                                        def fGetMatchingRows(row,cols,matchNode):
                                            for col in cols:
                                                if row[col]==matchNode:
                                                    return True
                                            return False

                                        # Anker x suchen anhand der Spalten ...
                                        if 'matchAnchorCols' in hpLineGeom.keys():
                                            matchAnchorCols=hpLineGeom['matchAnchorCols']
                                        else:                                            
                                            matchAnchorCols=[kwds['edgeColSequence'][2]]
                                       
                                        # AnkerKnoten: Zeilen die in Frage kommen ....
                                        hPpDfMatched=hPpDf[hPpDf.apply(fGetMatchingRows,axis=1,cols=matchAnchorCols,matchNode=masterNode)]                                            
                                        hPpDfMasterMatched=hPpDfMaster[hPpDfMaster.apply(fGetMatchingRows,axis=1,cols=matchAnchorCols,matchNode=masterNode)]
                                      
                                        if 'matchType' in hpLineGeom.keys():
                                            matchType=hpLineGeom['matchType']
                                        else:
                                            matchType='starts'

                                        # Anker x suchen in Master -------------------------
                                        if 'matchAnchor' in hpLineGeom.keys():
                                            matchAnchor=hpLineGeom['matchAnchor']
                                        else:
                                            matchAnchor='max'
                                       
                                        if hPpDfMasterMatched.empty:
                                            logger.info("{:s}Schnitt: {!s:s}_{!s:s} Master: {!s:s}_{!s:s} masterNode: {!s:s}: in Master in den cols {!s:s} NICHT gefunden.  Loesung: xMasterOffset=0.".format(logStr,row[kwds['NAMECol']],row[kwds['LayerCol']],name,layer,masterNode,matchAnchorCols)) 
                                            xMasterOffset=0                                                                                             
                                        else:  
                                            if matchAnchor=='min':                                                  
                                                hPpDfMasterMatched=hPpDfMaster.loc[hPpDfMasterMatched[kwds['xCol']].idxmin(),:]
                                            else: # matchAnchor=='max'                                          
                                                hPpDfMasterMatched=hPpDfMaster.loc[hPpDfMasterMatched.iloc[::-1][kwds['xCol']].idxmax(),:]     
                                            xMasterOffset=hPpDfMasterMatched[kwds['xCol']]                                            
                                            logger.debug("{:s}Schnitt: {!s:s}_{!s:s} Master: {!s:s}_{!s:s} masterNode: {!s:s} xMasterOffset={:9.3f} ...".format(logStr,row[kwds['NAMECol']],row[kwds['LayerCol']],name,layer,masterNode,xMasterOffset)) 

                                        # Anker x suchen in HP selbst --------------------------
                                        if 'matchAnchorChild' in hpLineGeom.keys():
                                            matchAnchorChild=hpLineGeom['matchAnchorChild']
                                        else:
                                            matchAnchorChild='max'
                                                                                               
                                        if hPpDfMatched.empty:
                                            logStrTmp="{:s}Schnitt: {!s:s}_{!s:s} Master: {!s:s}_{!s:s} masterNode: {!s:s}: in Child in den cols {!s:s} NICHT gefunden.".format(logStr,row[kwds['NAMECol']],row[kwds['LayerCol']],name,layer,masterNode,matchAnchorCols)
                                            if matchType=='matches':
                                                logger.info(logStrTmp+' Loesung: xChildOffset=0.') 
                                            else:
                                                if matchType=='ends':
                                                    logger.debug(logStrTmp+' Child endet nicht   mit masterNode. xChildOffset=0') 
                                                else:
                                                    logger.debug(logStrTmp+' Child startet evtl. mit masterNode. xChildOffset=0') 
                                            xChildOffset=0
                                        else:
                                            if matchAnchorChild=='min':
                                                hPpDfMatched=hPpDf.loc[hPpDfMatched[kwds['xCol']].idxmin(),:]                                           
                                            else: # matchAnchorChild=='max'
                                                hPpDfMatched=hPpDf.loc[hPpDfMatched.iloc[::-1][kwds['xCol']].idxmax(),:]                         
                                            xChildOffset=hPpDfMatched[kwds['xCol']]
                                            logger.debug("{:s}Schnitt: {!s:s}_{!s:s} Master: {!s:s}_{!s:s} masterNode: {!s:s} xChildOffset={:9.3f} ...".format(logStr,row[kwds['NAMECol']],row[kwds['LayerCol']],name,layer,masterNode,xChildOffset)) 
                      
                                        # xOffset errechnen
                                        if matchType=='starts':
                                            xOffset=xMasterOffset-hPpDf[kwds['xCol']].min() # der Beginn
                                            # matchNode ist Anfang
                                            if hPpDf[kwds['edgeColSequence'][2]].iloc[0] == hPpDf[kwds['edgeColSequence'][1]].iloc[0]:
                                                # nextNode = k
                                                matchNode=hPpDf[kwds['edgeColSequence'][0]].iloc[0]
                                            else:
                                                # nextNode = i
                                                matchNode=hPpDf[kwds['edgeColSequence'][1]].iloc[0]
                                        elif matchType=='ends':
                                            xOffset=xMasterOffset-hPpDf[kwds['xCol']].max() # das Ende
                                            # matchNode ist Ende
                                            if hPpDf[kwds['edgeColSequence'][2]].iloc[-1] == hPpDf[kwds['edgeColSequence'][1]].iloc[-1]:
                                                # nextNode = k
                                                matchNode=hPpDf[kwds['edgeColSequence'][1]].iloc[-1]
                                            else:
                                                # nextNode = i
                                                matchNode=hPpDf[kwds['edgeColSequence'][0]].iloc[-1]
                                        else: # 'matches'
                                            # per Knoten
                                            matchNode=masterNode
                                            xOffset=xMasterOffset-xChildOffset 
                                        
                                        # xOffset wurde berechnet
                                        # masterNode und matchNode sind bekannt

                                        logger.debug("{:s}hPpDfMatched: {:s} ...".format(logStr,hPpDfMatched[[kwds['NAMECol'],kwds['LayerCol'],'nextNODE',kwds['xCol'],'NAME_i','NAME_k','OBJTYPE','IptIdx']].to_string())) 
                                        logger.debug("{:s}hPpDfMasterMatched: {:s} ...".format(logStr,hPpDfMasterMatched[[kwds['NAMECol'],kwds['LayerCol'],'nextNODE',kwds['xCol'],'NAME_i','NAME_k','OBJTYPE','IptIdx']].to_string())) 
                        else:
                            logger.debug("{:s}Line: {:s}: keine Geometrieeigenschaften definiert.".format(logStr,keyBase.rstrip('_')))
                    # xNodeInfs ermitteln                    
                    nodeList=hPpDf[kwds['edgeColSequence'][2]].copy()
                    if hPpDf[kwds['edgeColSequence'][2]].iloc[0] == hPpDf[kwds['edgeColSequence'][1]].iloc[0]:
                        # nextNode = k
                        # 1. Knoten i                        
                        nodeList.iloc[0]=hPpDf[kwds['edgeColSequence'][0]].iloc[0]
                    else:
                        # nextNode = i
                        # 1. Knoten k
                        nodeList.iloc[0]=hPpDf[kwds['edgeColSequence'][1]].iloc[0]
                    nodeList=nodeList.unique()
                    xNodeInf={}
                    for idx,node in enumerate(nodeList):
                        nodeInf={}                        
                        if idx==0:
                            nodeInf[kwds['xCol']]=0
                            nodeInf['pDfIdx']=hPpDf.index.values[0]
                        else:
                            nodeInf[kwds['xCol']]=hPpDf[hPpDf[kwds['edgeColSequence'][2]]==node][kwds['xCol']].max()
                            nodeInf['pDfIdx']=hPpDf[hPpDf[kwds['edgeColSequence'][2]]==node][kwds['xCol']].idxmax()
                        nodeInf[kwds['xCol']+'Plot']=nodeInf[kwds['xCol']]*xFactorStatic+xOffset+xOffsetStatic
                        xNodeInf[node]=nodeInf
                    xNodeInfs[keyBase.rstrip('_')]=xNodeInf

                    # über alle Spalten (d.h. darzustellenden y-Werten)                   
                    for idx,hpLine in enumerate(kwds['hpLines']):                             
                        key=keyBase+hpLine

                        logger.debug("{:s}Line: {:s} ...".format(logStr,key))

                        if key in kwds['hpLineProps']:
                            hpLineProp=kwds['hpLineProps'][key]                                                       
                            if hpLineProp == None:
                                logger.debug("{:s}Line: {:s} ...: kein Plot.".format(logStr,key))
                                continue # kein Plot

                        label=key
                        color='black'
                        linestyle='-'
                        linewidth=3

                        hpLineType=hpLineTypesSequence[idx]
                        axHP=yAxes[hpLineType]
                        lines=axHP.plot(hPpDf[kwds['xCol']]*xFactorStatic+xOffset+xOffsetStatic,hPpDf[hpLine],label=label,color=color,linestyle=linestyle,linewidth=linewidth)
                        yLines[label]=lines[0]

                        if key in kwds['hpLineProps']:
                            hpLineProp=kwds['hpLineProps'][key]        
                            logger.debug("{:s}Line: {:s}: hpLineProp: {:s}.".format(logStr,key,str(hpLineProp)))                            
                            for prop,value in hpLineProp.items():
                                plt.setp(yLines[label],"{:s}".format(prop),value)                                                        
                        else:                            
                            logger.debug("{:s}Line: {:s}: keine Eigenschaften definiert.".format(logStr,key))
                            continue

                                                                                                                                                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                       
        finally:       
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))       
            return yAxes,yLines,xNodeInfs

    @classmethod
    def pltTC(cls,pDf,tcLines,**kwds):
        """
        Plots a Time Curve Diagram.
        
        Args:
                DATA:
                    pDf: dataFrame
                            index:  times
                            cols:   values (with mx.df colnames)

                    tcLines: dct
                          
                        defining the Curves and their Layout:

                        Key:
                            OBJTYPE~NAME1~NAME2~ATTRTYPE is used as a key, d.h. OBJTYPE_PK ist nicht im Schluessel enthalten

                        * tcLines - Example - = {
                            'KNOT~NAME1~~PH':{'label':'VL','color':'red' ,'linestyle':'-','linewidth':3}                       
                        }


                        Definition der y-Achsentypen (y-Axes):
                            * werden ermittelt aus den verschiedenen ATTRTYPEs in tcLines
                            * ATTRTYPE - z.B. 'PH' - wird dabei als Bezeichner für den Achsentyp benutzt
                            * die Achsen werden erstellt in der Reihenfolge in der sie in tcLines auftreten                      
                            * yTwinedAxesPosDeltaHPStart: (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche; default: -0.0125
                            * yTwinedAxesPosDeltaHP: (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche; default: -0.05


                        Attribute:
                            * alle gültigen
                     
                            * +
                            
                            * forceYType
                            
                            * offset
                            * factor
                            
                            * timeStart
                            * timeEnd
                            
                            * legendInfosFmt
                            * label
                     
                AXES:
                    pAx: Axes to be plotted on; if not specified: gca() is used

                x-Achsen-Formatierung:                   
                    majLocator - Beispiele:
                            mdates.MinuteLocator(interval=5)
                            mdates.MinuteLocator(byminute=[0,5,10,15,20,25,30,35,40,45,50,55])
                    majFormatter - Beispiele:
                            mdates.DateFormatter('%d.%m.%y: %H:%M')
                    xTicksLabelsOff: wenn True, dann keine x-Achsen TickLabels

        Return:
                yAxes: dct with AXES; key=y-Achsentypen
                yLines: dct with Line2Ds; key=Index from tcLines     
                vLines: dct with Line2Ds; key=Index from vLines     
                yLinesLegendLabels: dct with Legendlabels; key=Index from tcLines     
                            
                >>> #  -q -m 0 -s pltTC -y no -z no -w DHNetwork                
                >>> import pandas as pd
                >>> import matplotlib
                >>> import matplotlib.pyplot as plt
                >>> import matplotlib.gridspec as gridspec
                >>> import matplotlib.dates as mdates
                >>> import math
                >>> try:
                ...   import Rm
                ... except ImportError:                   
                ...   from PT3S import Rm
                >>> # ---
                >>> # xm=xms['DHNetwork']       
                >>> mx=mxs['DHNetwork'] 
                >>> sir3sID=mx.getSir3sIDFromSir3sIDoPK('ALLG~~~LINEPACKGEOM') # 'ALLG~~~5151766074450398225~LINEPACKGEOM'
                >>> # mx.df[sir3sID].describe()
                >>> # mx.df[sir3sID].iloc[0]
                >>> plt.close()
                >>> fig=plt.figure(figsize=Rm.DINA3q,dpi=Rm.dpiSize)         
                >>> gs = gridspec.GridSpec(3, 1)
                >>> # --------------------------
                >>> axTC = fig.add_subplot(gs[0])       
                >>> yAxes,yLines,vLines,yLinesLegendLabels=Rm.Rm.pltTC(mx.df             
                ... ,tcLines={ 
                ...     'ALLG~~~LINEPACKRATE':{'label':'Linepackrate','color':'red' ,'linestyle':'-','linewidth':3,'drawstyle':'steps','factor':10}
                ...    ,'ALLG~~~LINEPACKGEOM':{'label':'Linepackgeometrie','color':'b' ,'linestyle':'-','linewidth':3,'offset':-mx.df[sir3sID].iloc[0]
                ...         ,'timeStart':mx.df.index[0]+pd.Timedelta('10 Minutes')
                ...         ,'timeEnd':mx.df.index[-1]-pd.Timedelta('10 Minutes')}
                ...    ,'RSLW~wNA~~XA':{'label':'RSLW~wNA~~XA','color':'lime','forceYType':'N'}
                ...    ,'PUMP~R-A-SS~R-A-DS~N':{'label':'PUMP~R-A-SS~R-A-DS~N','color':'aquamarine','linestyle':'--','legendInfosFmt':'{:4.0f}'}
                ... }
                ... ,pAx=axTC  
                ... ,vLines={
                ...   'a vLine Label':{'time': mx.df.index[0] + pd.Timedelta('10 Minutes')
                ...                        ,'color':'dimgrey'
                ...                        ,'linestyle':'--'
                ...                        ,'linewidth':5.}
                ... }
                ... ,majLocator=mdates.MinuteLocator(byminute=[0,5,10,15,20,25,30,35,40,45,50,55])
                ... ,majFormatter=mdates.DateFormatter('%d.%m.%y: %H:%M')
                ... #,xTicksLabelsOff=True
                ... )       
                >>> sorted(yAxes.keys())  
                ['LINEPACKGEOM', 'LINEPACKRATE', 'N']
                >>> sorted(yLines.keys())  
                ['ALLG~~~LINEPACKGEOM', 'ALLG~~~LINEPACKRATE', 'PUMP~R-A-SS~R-A-DS~N', 'RSLW~wNA~~XA']
                >>> sorted(vLines.keys())  
                ['a vLine Label']
                >>> gs.tight_layout(fig)
                >>> plt.show()                               
                >>> 
        """
        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
                keys = sorted(kwds.keys())
                
                # AXES
                if 'pAx' not in keys:
                    kwds['pAx']=plt.gca()

                if 'yTwinedAxesPosDeltaHPStart' not in keys:
                     # (i.d.R. negativer) Abstand der 1. y-Achse von der Zeichenfläche; default: -0.0125
                    kwds['yTwinedAxesPosDeltaHPStart']=-0.0125

                if 'yTwinedAxesPosDeltaHP' not in keys:
                     # (i.d.R. negativer) zus. Abstand jeder weiteren y-Achse von der Zeichenfläche; default: -0.05
                    kwds['yTwinedAxesPosDeltaHP']=-0.05

                logger.debug("{:s}tcLines: {:s}.".format(logStr,str(tcLines)))
                logger.debug("{:s}yTwinedAxesPosDeltaHPStart: {:s}.".format(logStr,str(kwds['yTwinedAxesPosDeltaHPStart'])))
                logger.debug("{:s}yTwinedAxesPosDeltaHP: {:s}.".format(logStr,str(kwds['yTwinedAxesPosDeltaHP'])))

                if 'lLoc' not in keys:                    
                    kwds['lLoc']='best'                
                if 'lFramealpha' not in keys:                    
                    kwds['lFramealpha']=matplotlib.rcParams["legend.framealpha"]
                if 'lFacecolor' not in keys:                    
                    kwds['lFacecolor']='white'
                if 'lOff' not in keys:                    
                    kwds['lOff']=False

                yAxes=yLines=vLines=None

                # fuer jede Spalte Schluessel ohne OBJTYPE_PK ermitteln == Schluessel in tcLines                
                colFromTcKey={}
                for col in pDf.columns.tolist():
                    if pd.isna(col):
                        continue
                    try:
                        colNew=Mx.getSir3sIDoPKFromSir3sID(col)
                        colFromTcKey[colNew]=col # merken welche Originalspalte zu dem tcLines Schluessel gehoert  
                        logger.debug("{:s}Zu Spalte ohne Schlüssel: {:s} gehört Spalte: {:s} in pDf.".format(logStr,colNew,col))
                    except:
                        logger.debug("{:s}keine Zuordnung gefunden (z.B. kein Mx.getSir3sIDoPKFromSir3sID-match) fuer pDf-Spalte: {:s}. Spaltenname(n) keine vollständigen SIR 3S Schluessel (mehr)?!".format(logStr,col))
                
                # y-Achsen-Typen ermitteln
                yTypesSequence=[]                
                for key,props in tcLines.items():
                    try:
                        mo=re.match(Mx.reSir3sIDoPKcompiled,key)     
                        yType=mo.group('ATTRTYPE')
                        if 'forceYType' in props.keys():
                            yType=props['forceYType']
                        if yType not in yTypesSequence:
                            yTypesSequence.append(yType)
                            logger.debug("{:s}neuer y-Achsentyp: {:s}.".format(logStr,yType))
                    except:
                        logger.debug("{:s}kein Achsentyp ermittelt (z.B. kein Mx.reSir3sIDoPKcompiled-match) fuer: {:s}. tcLine(s) Schluessel kein SIR 3S Schluessel oPK?!".format(logStr,key))
                  
                # y-Achsen konstruieren
                yAxes={}
                colType1st=yTypesSequence[0]
                axTC=kwds['pAx'] 
                axTC.spines["left"].set_position(("axes",kwds['yTwinedAxesPosDeltaHPStart'] )) 

                axTC.set_ylabel(colType1st)  
                yAxes[colType1st]=axTC                  
                logger.debug("{:s}colType: {:s}: is attached to 1st Axes.".format(logStr,colType1st))
                for idx,colType in enumerate(yTypesSequence[1:]):    
                    # weitere y-Achse
                    yPos=kwds['yTwinedAxesPosDeltaHPStart']+kwds['yTwinedAxesPosDeltaHP']*len(yAxes)
                    logger.debug("{:s}colType: {:s}: is attached to a new Axes: yPos: {:1.4f} ...".format(logStr,colType,yPos))
                     
                    axTC = axTC.twinx()
                    axTC.spines["left"].set_position(("axes", yPos)) 
                    pltMakePatchSpinesInvisible(axTC)
                    axTC.spines['left'].set_visible(True)  
                    axTC.yaxis.set_label_position('left')
                    axTC.yaxis.set_ticks_position('left')
                    axTC.set_ylabel(colType)  
                    yAxes[colType]=axTC                     


                # ueber alle definierten Kurven         
                # max. Länge label vor Infos ermitteln
                labels=[]
                infos=[]
                for key,props in tcLines.items(): 
                        label=key
                        if 'label' in props:
                            label=props['label']
                        labels.append(label)

                        if 'legendInfosFmt' in props:
                            legendInfosFmt=props['legendInfosFmt']
                        else:
                            legendInfosFmt='{:6.2f}'


                        if key not in colFromTcKey.keys():                       
                            logger.debug("{:s}Line: {:s}: es konnte keine Spalte in pDf ermittelt werden. Spaltenname(n) kein SIR 3S Schluessel?! Kein Plot.".format(logStr,key))
                            continue      
                        else:
                            col=colFromTcKey[key]
                            logger.debug("{:s}Line: {:s}: Spalte in pDf: {:s}.".format(logStr,key,col))


                            if 'timeStart' in props:
                                timeStart=props['timeStart']
                            else:
                                timeStart=pDf.index[0]

                            if 'timeEnd' in props:
                                timeEnd=props['timeEnd']
                            else:
                                timeEnd=pDf.index[-1]

                            plotDf=pDf.loc[timeStart:timeEnd,:]
                            infos.append(legendInfosFmt.format(plotDf[col].min()))
                            infos.append(legendInfosFmt.format(plotDf[col].max()))


                labelsLength=[len(label) for label in labels]
                labelsLengthMax=max(labelsLength)

                infosLength=[len(info) for info in infos]
                infosLengthMax=max(infosLength)

                # zeichnen
                yLines={}       
                yLinesLegendLabels={}
                # ueber alle definierten Kurven         
                for key,props in tcLines.items():                    
                    if key not in colFromTcKey.keys():                       
                        logger.debug("{:s}Line: {:s}: es konnte keine Spalte in pDf ermittelt werden. Spaltenname(n) kein SIR 3S Schluessel?! Kein Plot.".format(logStr,key))
                        continue      
                    else:
                        col=colFromTcKey[key]

                    mo=re.match(Mx.reSir3sIDoPKcompiled,key) 
                    yType=mo.group('ATTRTYPE')
                    if 'forceYType' in props.keys():
                        yType=props['forceYType']

                    axTC=yAxes[yType]

                    logger.debug("{:s}Line: {:s} on Axes {:s} ...".format(logStr,key,yType))
                         
                    label=key
                    color='black'
                    linestyle='-'
                    linewidth=3
                    
                    if 'offset' in props:
                        offset=props['offset']
                    else:
                        offset=0.
                    if 'factor' in props:
                        factor=props['factor']
                    else:
                        factor=1.

                    if 'timeStart' in props:
                        timeStart=props['timeStart']
                    else:
                        timeStart=pDf.index[0]

                    if 'timeEnd' in props:
                        timeEnd=props['timeEnd']
                    else:
                        timeEnd=pDf.index[-1]

                    if 'legendInfosFmt' in props:
                        legendInfosFmt=props['legendInfosFmt']
                    else:
                        legendInfosFmt='{:6.2f}'

                    plotDf=pDf.loc[timeStart:timeEnd,:]
                    lines=axTC.plot(plotDf.index.values,plotDf[col]*factor+offset,label=label,color=color,linestyle=linestyle,linewidth=linewidth)                   
                    yLines[key]=lines[0]

                    if 'label' in props:
                        label=props['label']
                    else:
                        label=label

                    legendLabelFormat="Anf.: {:s} Ende: {:s} Min: {:s} Max: {:s}"#.format(*4*[legendInfosFmt])
                    legendLabelFormat="{:s} "+legendLabelFormat
                    legendInfos=[plotDf[col].iloc[0],plotDf[col].iloc[-1],plotDf[col].min(),plotDf[col].max()]                   
                    legendInfos=[factor*legendInfo+offset for legendInfo in legendInfos]
                    legendLabel=legendLabelFormat.format(label.ljust(labelsLengthMax,' '),
                                                         *["{:s}".format(legendInfosFmt).format(legendInfo).rjust(infosLengthMax,' ') for legendInfo in legendInfos]
                                                         )
                    yLinesLegendLabels[key]=legendLabel
                    logger.debug("{:s}legendLabel: {:s}.".format(logStr,legendLabel))
                           
                    for prop,value in props.items():       
                        if prop not in ['forceYType','offset','factor','timeStart','timeEnd','legendInfosFmt']:
                            plt.setp(yLines[key],"{:s}".format(prop),value)             
                        
                # x-Achse 
                # ueber alle Axes
                for key,ax in yAxes.items():
                    ax.set_xlim(pDf.index[0],pDf.index[-1])     
                    if 'majLocator' in kwds.keys():
                        ax.xaxis.set_major_locator(kwds['majLocator'])
                    if 'majFormatter' in kwds.keys():
                        ax.xaxis.set_major_formatter(kwds['majFormatter'])                       
                    plt.setp(ax.xaxis.get_majorticklabels(),rotation='vertical',ha='center')
                    ax.xaxis.grid()

                    # Beschriftung ausschalten
                    if 'xTicksLabelsOff' in kwds.keys(): # xTicksOff
                        if kwds['xTicksLabelsOff']:
                            logger.debug("{:s}Achse: {:s}: x-Achse Labels aus.".format(logStr,key))
                            #for tic in ax.xaxis.get_major_ticks():
                            #    tic.tick1On = tic.tick2On = False
                            ax.set_xticklabels([])

                # vLines                                
                # ueber alle definierten vLines
                vLines={}
                if 'vLines' in kwds.keys():
                    for key,props in kwds['vLines'].items():       
                        if 'time' in props.keys():
                            logger.debug("{:s}vLine: {:s} ....".format(logStr,key))
                            vLine=ax.axvline(x=props['time'], ymin=0, ymax=1, label=key)
                            vLines[key]=vLine
                            for prop,value in props.items():
                                if prop not in ['time']:
                                    plt.setp(vLine,"{:s}".format(prop),value)   
                        else:
                            logger.debug("{:s}vLine: {:s}: time nicht definiert.".format(logStr,key))


                # Legend
                import matplotlib.font_manager as font_manager
                font = font_manager.FontProperties(family='monospace'
                                   #weight='bold',
                                   #style='normal', 
                                   #size=16
                                   )

                if not kwds['lOff']:
                    l=kwds['pAx'].legend(
                        tuple([yLines[yline] for yline in yLines])
                       ,
                        tuple([yLinesLegendLabels[yLine] for yLine in yLinesLegendLabels])
                       ,loc=kwds['lLoc']
                       ,framealpha=kwds['lFramealpha']
                       ,facecolor=kwds['lFacecolor']  
                       ,prop=font
                    )                
                                                                                                                                                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                       
        finally:       
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))       
            return yAxes,yLines,vLines,yLinesLegendLabels

    def __init__(self,xm=None,mx=None): 
        """
        Args:
            xm: Xm.Xm Object
            mx: Mx.Mx Object
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            self.xm=xm
            self.mx=mx
 
            try:
                vNRCV_Mx1=self.xm.dataFrames['vNRCV_Mx1'] # d.h. Sachdaten bereits annotiert mit MX1-Wissen 
            except:
                logger.debug("{:s}{:s} not in {:s}. Sachdaten mit MX1-Wissen zu annotieren wird nachgeholt ...".format(logStr,'vNRCV_Mx1','dataFrames'))
                self.xm.MxSync(mx=self.mx)                      
                                                       
        except RmError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def pltNetDHUS(self,**kwds):
        """Plot: Net: DistrictHeatingUnderSupply. 

        Args (optional):

            TIMEs (als TIMEDELTA zu Szenariumbeginn):
                * timeDeltaToRef: Reference Scenariotime (for MeasureInRefPerc-Calculations) (default: pd.to_timedelta('0 seconds'))
                * timeDeltaToT: Scenariotime (default: pd.to_timedelta('0 seconds'))

            FWVB
               * pFWVBFilterFunction: Filterfunction to be applied to FWVB to determine the FWVB to be plotted
                    * default: lambda df: (df.CONT_ID.astype(int).isin([1001])) & (df.W0LFK>0)
                        * CONT_IDisIn: [1001]
                            * um zu vermeiden, dass FWVB aus Bloecken gezeichnet werden (unwahrscheinlich, dass es solche gibt)    
                        * W0LFK>0:
                            * um zu vermeiden, dass versucht wird, FWVB mit der Soll-Leistung 0 zu zeichnen (pFWVBAttribute default is 'W0LFK')              

            FWVB Attribute (Size, z-Order) - from vFWVB
                * pFWVBAttribute: columnName (default: 'W0LFK') 

                    * the column must be able to be converted to a float
                    * the conversion is done before FilterFunction 
                    * see ApplyFunction and NaNValue for conversion details:
                        * pFWVBAttributeApplyFunction: Function to be applied to column pFWVBAttribute 
                                            * default: lambda x: pd.to_numeric(x,errors='coerce')                                    
                        * pFWVBAttributeApplyFunctionNaNValue: Value for NaN-Values produced by pFWVBAttributeApplyFunction if any  
                                            * default: 0
                                            * .fillna(pFWVBAttributeApplyFunktionNaNValue).astype(float) is called after ApplyFunction

                * pFWVBAttributeAsc: z-Order (default: False d.h. "kleine auf große")
                * pFWVBAttributeRefSize: scatter Sy-Area in pts^2 of for RefSizeValue (default: 10**2)  
                      
                    * corresponding RefSizeValue is Attribute.std() or Attribute.mean() if Attribute.std() is < 1

            FWVB (plot only large (small, medium) FWVB ...)
               * quantil_pFWVBAttributeHigh <= (default: 1.) 
               * quantil_pFWVBAttributeLow >= (default: .0)
               * default: all FWVB are plotted 
               * note that Attribute >0 is a precondition 

            FWVB Measure (Color) - from mx
                * pFWVBMeasure (default: 'FWVB~*~*~*~W') 

                    * float() must be possible                

                * pFWVBMeasureInRefPerc (default: True d.h. Measure wird verarbeitet in Prozent T zu Ref) 

                    * 0-1
                    * if refValue is 0 than refPerc-Result is set to 1 

                * pFWVBMeasureAlpha/Colormap/Clip

                * 3Classes

                    * pFWVBMeasure3Classes (default: False)
                        * False:
                            * Measure wird nicht in 3 Klassen dargestellt
                            * die Belegung von MCategory gemaess FixedLimitsHigh/Low erfolgt dennoch

                    * CatTexts (werden verwendet wenn 3Classes Wahr gesetzt ist)

                        * für CBLegend (3Classes) als _zusätzliche Beschriftung rechts
                        * als Texte für die Spalte MCategory in return pFWVB

                        * pMCatTopText
                        * pMCatMidText
                        * pMCatBotText

                    * CatAttribs (werden verwendet wenn 3Classes Wahr gesetzt ist)

                        * für die Knotendarstellung                        

                        * pMCatTopAlpha/Color/Clip
                        * pMCatMidAlpha/Colormap/Clip
                        * pMCatBotAlpha/Color/Clip
                                   
                * CBFixedLimits 
                
                    * pFWVBMeasureCBFixedLimits (default: False d.h. Farbskala nach vorh. min./max. Wert)

                        * wird Wahr gesetzt sein, wenn 3Classes Wahr gesetzt ist
                        * damit die mittlere Farbskala den Klassengrenzen "gehorcht"

                    * pFWVBMeasureCBFixedLimitLow (default: .10) 
                    * pFWVBMeasureCBFixedLimitHigh (default: .95) 

            CB
                * CBFraction: fraction of original axes to use for colorbar (default: 0.05)
                * CBHpad: fraction of original axes between colorbar and new image axes (default: 0.0275)               
                * CBLabelPad (default: -50)         
                * CBTicklabelsHPad (default: 0.)      
                * CBAspect: ratio of long to short dimension (default: 10.)
                * CBShrink: fraction by which to shrink the colorbar (default: .3)
                * CBAnchorHorizontal: horizontaler Fußpunkt der colorbar in Plot-% (default: 0.)
                * CBAnchorVertical: vertikaler Fußpunkt der colorbar in Plot-% (default: 0.2)     

            CBLegend (3Classes) - Parameterization of the representative Symbols
                * CBLe3cTopVPad (default: 1+1*1/4)
                * CBLe3cMidVPad (default: .5)                                                                         
                * CBLe3cBotVPad (default: 0-1*1/4)
                
                    * "1" is the height of the Colorbar                                                                   
                    * the VPads (the vertical Sy-Positions) are defined in cax.transAxes Coordinates    
                    * cax is the Colorbar Axes               

                * CBLe3cSySize=10**2 (Sy-Area in pts^2)
                * CBLe3cSyType='o' 

            ROHR
               * pROHRFilterFunction: Filterfunction to be applied to PIPEs to determine the PIPEs to be plotted
                    * default: lambda df: (df.KVR.astype(int).isin([2])) & (df.CONT_ID.astype(int).isin([1001])) & (df.DI.astype(float)>0)
                        * KVRisIn: [2]
                            * 1: supply-line
                            * 2: return-line                                       
                        * CONT_IDisIn: [1001]
                            * um zu vermeiden, dass Rohre aus Bloecken gezeichnet werden (deren Koordinaten nicht zu den Koordinaten von Rohren aus dem Ansichtsblock passen)    
                        * DI>0:
                            * um zu vermeiden, dass versucht wird, Rohre mit dem Innendurchmesser 0 zu zeichnen (pROHRAttribute default is 'DI')              

            ROHR (PIPE-Line: Size and Color, z-Order) - from vROHR  
                * pROHRAttribute: columnName (default: 'DI')
                    * the column must be able to be converted to a float
                    * the conversion is done before FilterFunction 
                    * see ApplyFunction and NaNValue for conversion details:
                        * pROHRAttributeApplyFunction: Function to be applied to column pROHRAttribute 
                                            * default: lambda x: pd.to_numeric(x,errors='coerce')                                    
                        * pROHRAttributeApplyFunctionNaNValue: Value for NaN-Values produced by pROHRAttributeApplyFunction if any  
                                            * default: 0
                                            * .fillna(pROHRAttributeApplyFunktionNaNValue).astype(float) is called after ApplyFunction
      
                * pROHRAttributeAsc: z-Order (default: False d.h. "kleine auf grosse")                                               

                * pROHRAttributeLs (default: '-')
                * pROHRAttributeRefSize: plot linewidth in pts for RefSizeValue (default: 1.0)    
                * pROHRAttributeSizeMin (default: None): if set: use pROHRAttributeSizeMin-Value as Attribute for LineSize if Attribute < pROHRAttributeSizeMin

                    * corresponding RefSizeValue is Attribute.std() or Attribute.mean() if Attribute.std() is < 1

                * pROHRAttributeColorMap (default: plt.cm.binary)    
                * pROHRAttributeColorMapUsageStart (default: 1./3; Wertebereich: [0,1])        

                    * Farbskala nach vorh. min./max. Wert
                    * die Farbskala wird nur ab UsageStart genutzt
                    * d.h. Werte die eine "kleinere" Farbe haetten, bekommen die Farbe von UsageStart

            ROHR (plot only large (small, medium) pipes ...)
               * quantil_pROHRAttributeHigh <= (default: 1.) 
               * quantil_pROHRAttributeLow >= (default: .75)
               * default: only the largest 25% are plotted 
               * note that Attribute >0 is a precondition 

            ROHR (PIPE-Marker: Size and Color) - from mx
                * pROHRMeasure columnName (default: 'ROHR~*~*~*~QMAV') 
                * pROHRMeasureApplyFunction: Function to be applied to column pROHRMeasure (default: lambda x: math.fabs(x))  
                
                * pROHRMeasureMarker (default: '.')
                * pROHRMeasureRefSize: plot markersize for RefSizeValue in pts (default: 1.0)

                * pROHRMeasureSizeMin (default: None): if set: use pROHRMeasureSizeMin-Value as Measure for MarkerSize if Measure < pROHRMeasureSizeMin
                    
                        * corresponding RefSizeValue is Measure.std() or Measure.mean() if Measure.std() is < 1                        
                        * if pROHRMeasureRefSize is None: plot markersize will be plot linewidth

                * pROHRMeasureColorMap (default: plt.cm.cool) 
                * pROHRMeasureColorMapUsageStart (default: 0.; Wertebereich: [0,1])        

                    * Farbskala nach vorh. min./max. Wert
                    * die Farbskala wird nur ab UsageStart genutzt
                    * d.h. Werte die eine "kleinere" Farbe hätten, bekommen die Farbe von UsageStart
               
            NRCVs - NumeRiCal Values to be displayed
                * pFIGNrcv: List of Sir3sID RegExps to be displayed (i.e. ['KNOT~PKON-Knoten~\S*~\S+~QM']) default: None
                    the 1st Match is used if a RegExp matches more than 1 Channel
                    
                    further Examples for RegExps (and corresponding Texts):
                        * WBLZ~WärmeblnzGes~\S*~\S+~WES (Generation)
                        * WBLZ~WärmeblnzGes~\S*~\S+~WVB (Load)
                        * WBLZ~WärmeblnzGes~\S*~\S+~WVERL (Loss)

                    WBLZ~[\S ]+~\S*~\S+~\S+: Example for a RegExp matching all Channels with OBJTYPE WBLZ  

                * pFIGNrcvTxt: corresponding (same length required!) List of Texts (i.e. ['Kontrolle DH']) default: None
                    
                * pFIGNrcvFmt (i.e. '{:12s}: {:8.2f} {:6s}')
                    * Text (from pFIGNrcvTxt)
                    * Value
                    * UNIT (determined from Channel-Data)

                * pFIGNrcvPercFmt (i.e. ' {:6.1f}%')                   
                    * ValueInRefPercent
                    * if refValue==0: 100% 

                * pFIGNrcvXStart (.5 default)
                * pFIGNrcvYStart (.5 default)

            Category - User Heat Balances to be displayed
                * pFWVBGCategory: List of Heat Balances to be displayed (i.e. ['BLNZ1u5u7']) default: None
                * pFWVBGCategoryUnit:  Unit of all these Balances (default: '[kW]'])               
                * pFWVBGCategoryXStart (.1 default)
                * pFWVBGCategoryYStart (.9 default)

                * pFWVBGCategoryCatFmt (i.e. '{:12s}: {:6.1f} {:4s}')
                    * Category NAME
                    * Category Load
                    * pFWVBGCategoryUnit                   

                * pFWVBGCategoryPercFmt (i.e. ' {:6.1f}%')                   
                    * Last Ist/Soll
                    
                * pFWVBGCategory3cFmt (i.e. ' {:5d}/{:5d}/{:5d}')
                    * NOfTops
                    * NOfMids
                    * NOfBots                
                                       
            VICs - VeryImportantCustomers whose Values to be displayed
                * pVICsDf: DataFrame with VeryImportantCustomers (Text & Specification)
                    columns expected:
                        * Kundenname (i.e. 'VIC1') - Text
                        * Knotenname (i.e. 'V-K007') - Specification by Supply-Node

                    i.e.: pd.DataFrame({'Kundenname': ['VIC1'],'Knotenname': ['V-K007']})

                 * pVICsPercFmt (i.e. '{:12s}: {:6.1f}%')
                    * Kundenname
                    * Load in Percent to Reference

                 * pVICsFmt (i.e. '{:12s}: {:6.1f} {:6s}')
                    * Kundenname
                    * Load
                    * pFWVBGCategoryUnit

                * pVICsXStart (.5 default)
                * pVICsYStart (.1 default)              

            Figure:
                * pltTitle: title [not suptitle] (default: 'pltNetFigAx') 
                * figFrameon: figure frame (background): displayed or invisible (default: True)
                * figEdgecolor: edge color of the Figure rectangle (default: 'black')
                * figFacecolor: face color of the Figure rectangle (default: 'white')

            Returns:
                pFWVB
                    * columns changed (compared to vFWVB):
                        * pFWVBAttribute (wg. z.B. pFWVBAttributeApplyFunction und .astype(float))

                    * columns added (compared to vFWVB):
                        * Measure (in % zu Ref wenn pFWVBMeasureInRefPer=True) 
                        * MeasureRef (Wert von Measure im Referenzzustand)
                        * MeasureOrig (Wert von Measure)

                        * MCategory: str (Kategorisierung von Measure mit FixedLimitHigh/Low-Werten):                           
                                * TopText or
                                * MidText or
                                * BotText
                            
                        * GCategory: list (non-empty only if req. GCategories are a subset of the available Categories and object belongs to a req. Category)
                        * VIC (filled with Kundenname from pVICsDf)

                    * rows (compared to vFWVB):
                        * pFWVB enthaelt dieselben Objekte wie vFWVB
                        * aber: die geplotteten Objekte sind ggf. nur eine Teilmenge (wg. z.B. pFWVBFilterFunction) 
        """
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        try:
            
            keysDefined=['CBAnchorHorizontal', 'CBAnchorVertical', 'CBAspect', 'CBFraction', 'CBHpad', 'CBLabelPad'
                         ,'CBLe3cBotVPad', 'CBLe3cMidVPad', 'CBLe3cSySize', 'CBLe3cSyType', 'CBLe3cTopVPad'
                         ,'CBShrink', 'CBTicklabelsHPad'

                         ,'figEdgecolor', 'figFacecolor', 'figFrameon'
                         
                         ,'pFIGNrcv','pFIGNrcvFmt', 'pFIGNrcvPercFmt','pFIGNrcvTxt', 'pFIGNrcvXStart', 'pFIGNrcvYStart'
                         
                         ,'pFWVBFilterFunction'
                         ,'pFWVBAttribute'
                         ,'pFWVBAttributeApplyFunction','pFWVBAttributeApplyFunctionNaNValue'
                         ,'pFWVBAttributeAsc'
                         ,'pFWVBAttributeRefSize'
                         
                         ,'pFWVBGCategory', 'pFWVBGCategoryUnit','pFWVBGCategory3cFmt','pFWVBGCategoryCatFmt', 'pFWVBGCategoryPercFmt', 'pFWVBGCategoryXStart', 'pFWVBGCategoryYStart'
                         
                         ,'pFWVBMeasure', 'pFWVBMeasure3Classes', 'pFWVBMeasureAlpha', 'pFWVBMeasureCBFixedLimitHigh', 'pFWVBMeasureCBFixedLimitLow', 'pFWVBMeasureCBFixedLimits', 'pFWVBMeasureClip', 'pFWVBMeasureColorMap', 'pFWVBMeasureInRefPerc'
                         ,'pMCatBotAlpha', 'pMCatBotClip', 'pMCatBotColor', 'pMCatBotText', 'pMCatMidAlpha', 'pMCatMidClip', 'pMCatMidColorMap', 'pMCatMidText', 'pMCatTopAlpha', 'pMCatTopClip', 'pMCatTopColor', 'pMCatTopText'
                         
                         ,'pROHRFilterFunction'                        
                         ,'pROHRAttribute'
                         ,'pROHRAttributeApplyFunction','pROHRAttributeApplyFunctionNaNValue'
                         ,'pROHRAttributeAsc', 'pROHRAttributeColorMap', 'pROHRAttributeColorMapUsageStart', 'pROHRAttributeLs', 'pROHRAttributeRefSize','pROHRAttributeSizeMin'
                         
                         ,'pROHRMeasure','pROHRMeasureApplyFunction'
                         ,'pROHRMeasureColorMap', 'pROHRMeasureColorMapUsageStart', 'pROHRMeasureMarker', 'pROHRMeasureRefSize','pROHRMeasureSizeMin'

                         ,'pVICsDf','pVICsPercFmt','pVICsFmt','pVICsXStart', 'pVICsYStart'
                         ,'pltTitle'
                         
                         ,'quantil_pFWVBAttributeHigh', 'quantil_pFWVBAttributeLow'
                         
                         ,'quantil_pROHRAttributeHigh', 'quantil_pROHRAttributeLow'
                         
                         ,'timeDeltaToRef', 'timeDeltaToT']

            keys=sorted(kwds.keys())
            for key in keys:
                if key in keysDefined:
                    value=kwds[key]
                    logger.debug("{0:s}kwd {1:s}: {2:s}".format(logStr,key,str(value))) 
                else:
                    logger.warning("{0:s}kwd {1:s} NOT defined!".format(logStr,key)) 
                    del kwds[key]

            # TIMEs
            if 'timeDeltaToRef' not in keys:
                kwds['timeDeltaToRef']=pd.to_timedelta('0 seconds')
            if 'timeDeltaToT' not in keys:
                kwds['timeDeltaToT']=pd.to_timedelta('0 seconds')

            # FWVB
            if 'pFWVBFilterFunction' not in keys:
                kwds['pFWVBFilterFunction']=lambda df: (df.CONT_ID.astype(int).isin([1001])) & (df.W0LFK.astype(float)>0)

            # FWVB Attribute (Size)
            if 'pFWVBAttribute' not in keys:
                kwds['pFWVBAttribute']='W0LFK'
            if 'pFWVBAttributeApplyFunction' not in keys:
                kwds['pFWVBAttributeApplyFunction']=lambda x: pd.to_numeric(x,errors='coerce') # .apply(kwds['pFWVBAttributeApplyFunktion'])
            if 'pFWVBAttributeApplyFunctionNaNValue' not in keys:
                kwds['pFWVBAttributeApplyFunctionNaNValue']=0 # .fillna(kwds['pFWVBAttributeApplyFunktionNaNValue']).astype(float)

            if 'pFWVBAttributeAsc' not in keys:
                kwds['pFWVBAttributeAsc']=False

            if 'pFWVBAttributeRefSize' not in keys:
                kwds['pFWVBAttributeRefSize']=10**2

            if 'quantil_pFWVBAttributeHigh' not in keys:
                kwds['quantil_pFWVBAttributeHigh']=1.
            if 'quantil_pFWVBAttributeLow' not in keys:
                kwds['quantil_pFWVBAttributeLow']=.0

            # FWVB Measure (Color)
            if 'pFWVBMeasure' not in keys:
                kwds['pFWVBMeasure']='FWVB~*~*~*~W'
            if 'pFWVBMeasureInRefPerc' not in keys:
                kwds['pFWVBMeasureInRefPerc']=True

            if 'pFWVBMeasureAlpha' not in keys:
                kwds['pFWVBMeasureAlpha']=0.9
            if 'pFWVBMeasureColorMap' not in keys:
                kwds['pFWVBMeasureColorMap']=plt.cm.autumn
            if 'pFWVBMeasureClip' not in keys:
                kwds['pFWVBMeasureClip']=False

            # 3Classes
            if 'pFWVBMeasure3Classes' not in keys:
                kwds['pFWVBMeasure3Classes']=False

            # CatTexts (werden verwendet wenn 3Classes Wahr gesetzt ist)
            if 'pMCatTopText' not in keys:
                kwds['pMCatTopText']='Top'
            if 'pMCatMidText' not in keys:
                kwds['pMCatMidText']='Middle'
            if 'pMCatBotText' not in keys:
                kwds['pMCatBotText']='Bottom'

            # CatAttribs (werden verwendet wenn 3Classes Wahr gesetzt ist)
            if 'pMCatTopAlpha' not in keys:
                kwds['pMCatTopAlpha']=0.9
            if 'pMCatTopColor' not in keys:
                kwds['pMCatTopColor']='palegreen'
            if 'pMCatTopClip' not in keys:
                kwds['pMCatTopClip']=False

            if 'pMCatMidAlpha' not in keys:
                kwds['pMCatMidAlpha']=0.9
            if 'pMCatMidColorMap' not in keys:
                kwds['pMCatMidColorMap']=plt.cm.autumn
            if 'pMCatMidClip' not in keys:
                kwds['pMCatMidClip']=False

            if 'pMCatBotAlpha' not in keys:
                kwds['pMCatBotAlpha']=0.9
            if 'pMCatBotColor' not in keys:
                kwds['pMCatBotColor']='violet'
            if 'pMCatBotClip' not in keys:
                kwds['pMCatBotClip']=False

            # CBFixedLimits 
            if 'pFWVBMeasureCBFixedLimits' not in keys:
                kwds['pFWVBMeasureCBFixedLimits']=False
            if 'pFWVBMeasureCBFixedLimitLow' not in keys:
                kwds['pFWVBMeasureCBFixedLimitLow']=.10
            if 'pFWVBMeasureCBFixedLimitHigh' not in keys:
                kwds['pFWVBMeasureCBFixedLimitHigh']=.95

            # CB
            if 'CBFraction' not in keys:
                kwds['CBFraction']=0.05
            if 'CBHpad' not in keys:
                kwds['CBHpad']=0.0275
            if 'CBLabelPad' not in keys:
                kwds['CBLabelPad']=-50
            if 'CBTicklabelsHPad' not in keys:
                kwds['CBTicklabelsHPad']=0
            if 'CBAspect' not in keys:
                kwds['CBAspect']=10.
            if 'CBShrink' not in keys:
                kwds['CBShrink']=0.3
            if 'CBAnchorHorizontal' not in keys:
                kwds['CBAnchorHorizontal']=0.
            if 'CBAnchorVertical' not in keys:
                kwds['CBAnchorVertical']=0.2
                      
            # CBLegend (3Classes) 
            if 'CBLe3cTopVPad' not in keys:
                kwds['CBLe3cTopVPad']=1+1*1/4  
            if 'CBLe3cMidVPad' not in keys:
                kwds['CBLe3cMidVPad']=.5    
            if 'CBLe3cBotVPad' not in keys:
                kwds['CBLe3cBotVPad']=0-1*1/4    
            if 'CBLe3cSySize' not in keys:
                kwds['CBLe3cSySize']=10**2
            if 'CBLe3cSyType' not in keys:
                kwds['CBLe3cSyType']='o'

            # ROHR             
            if 'pROHRFilterFunction' not in keys:
                kwds['pROHRFilterFunction']=lambda df: (df.KVR.astype(int).isin([2])) & (df.CONT_ID.astype(int).isin([1001])) & (df.DI.astype(float)>0)

            # pROHR (PIPE-Line: Size and Color)
            if 'pROHRAttribute' not in keys:
                kwds['pROHRAttribute']='DI'
            if 'pROHRAttributeApplyFunction' not in keys:
                kwds['pROHRAttributeApplyFunction']=lambda x: pd.to_numeric(x,errors='coerce') # .apply(kwds['pROHRAttributeApplyFunktion'])
            if 'pROHRAttributeApplyFunctionNaNValue' not in keys:
                kwds['pROHRAttributeApplyFunctionNaNValue']=0 # .fillna(kwds['pROHRAttributeApplyFunktionNaNValue']).astype(float)

            if 'pROHRAttributeAsc' not in keys:
                kwds['pROHRAttributeAsc']=False

            if 'pROHRAttributeLs' not in keys:
                kwds['pROHRAttributeLs']='-'
            if 'pROHRAttributeRefSize' not in keys:
                kwds['pROHRAttributeRefSize']=1.
            
            if 'pROHRAttributeSizeMin' not in keys:
                kwds['pROHRAttributeSizeMin']=None

            if 'pROHRAttributeColorMap' not in keys:
                kwds['pROHRAttributeColorMap']=plt.cm.binary
            if 'pROHRAttributeColorMapUsageStart' not in keys:
                kwds['pROHRAttributeColorMapUsageStart']=1./3.

            if 'quantil_pROHRAttributeHigh' not in keys:
                kwds['quantil_pROHRAttributeHigh']=1.
            if 'quantil_pROHRAttributeLow' not in keys:
                kwds['quantil_pROHRAttributeLow']=.75

            # pROHR (PIPE-Marker: Size and Color)
            if 'pROHRMeasure' not in keys:
                kwds['pROHRMeasure']='ROHR~*~*~*~QMAV'
            if 'pROHRMeasureApplyFunction' not in keys:
                kwds['pROHRMeasureApplyFunction']=lambda x: math.fabs(x)

            if 'pROHRMeasureMarker' not in keys:
                kwds['pROHRMeasureMarker']='.'
            if 'pROHRMeasureRefSize' not in keys:
                kwds['pROHRMeasureRefSize']=1.0

            if 'pROHRMeasureSizeMin' not in keys:
                kwds['pROHRMeasureSizeMin']=None

            if 'pROHRMeasureColorMap' not in keys:
                kwds['pROHRMeasureColorMap']=plt.cm.cool
            if 'pROHRMeasureColorMapUsageStart' not in keys:
                kwds['pROHRMeasureColorMapUsageStart']=0.

            # NRCVs to be displayed
            if 'pFIGNrcv' not in keys:
                kwds['pFIGNrcv']=None #['KNOT~PKON-Knoten~\S*~\S+~QM']  
            if 'pFIGNrcvTxt' not in keys:
                kwds['pFIGNrcvTxt']=None #['Kontrolle DH']
            if 'pFIGNrcvFmt' not in keys:
                kwds['pFIGNrcvFmt']='{:12s}: {:8.2f} {:6s}'
            if 'pFIGNrcvPercFmt' not in keys:
                kwds['pFIGNrcvPercFmt']=' {:6.1f}%'
            if 'pFIGNrcvXStart' not in keys:
                kwds['pFIGNrcvXStart']=.5
            if 'pFIGNrcvYStart' not in keys:
                kwds['pFIGNrcvYStart']=.5

            # User Heat Balances to be displayed
            if 'pFWVBGCategory' not in keys:
                kwds['pFWVBGCategory']=None #['BLNZ1u5u7']  
            if 'pFWVBGCategoryUnit' not in keys:
                kwds['pFWVBGCategoryUnit']='[kW]'  

            if 'pFWVBGCategoryCatFmt' not in keys:
                kwds['pFWVBGCategoryCatFmt']='{:12s}: {:6.1f} {:4s}'
            if 'pFWVBGCategoryPercFmt' not in keys:
                kwds['pFWVBGCategoryPercFmt']=' {:6.1f}%'
            if 'pFWVBGCategory3cFmt' not in keys:
                kwds['pFWVBGCategory3cFmt']=' {:5d}/{:5d}/{:5d}'  

            if 'pFWVBGCategoryXStart' not in keys:
                kwds['pFWVBGCategoryXStart']=.1
            if 'pFWVBGCategoryYStart' not in keys:
                kwds['pFWVBGCategoryYStart']=.9

            # VICs
            if 'pVICsDf' not in keys:
                kwds['pVICsDf']=None #pd.DataFrame({'Kundenname': ['VIC1'],'Knotenname': ['V-K007']})
            if 'pVICsPercFmt' not in keys:
                kwds['pVICsPercFmt']='{:12s}: {:6.1f}%'
            if 'pVICsFmt' not in keys:
                kwds['pVICsFmt']='{:12s}: {:6.1f} {:6s}'                
            if 'pVICsXStart' not in keys:
                kwds['pVICsXStart']=.5
            if 'pVICsYStart' not in keys:
                kwds['pVICsYStart']=.1        
                
            # Figure
            if 'pltTitle' not in keys:
                kwds['pltTitle']='pltNetDHUS'
            if 'figFrameon' not in keys:
                kwds['figFrameon']=True
            if 'figEdgecolor' not in keys:
                kwds['figEdgecolor']='black'
            if 'figFacecolor' not in keys:
                kwds['figFacecolor']='white'      
                
            # Plausis
            if kwds['pFWVBMeasure3Classes'] and not kwds['pFWVBMeasureCBFixedLimits']:
                kwds['pFWVBMeasureCBFixedLimits']=True
                logger.debug("{0:s}kwd {1:s} set to {2:s} because kwd {3:s}={4:s}".format(logStr,'pFWVBMeasureCBFixedLimits',str(kwds['pFWVBMeasureCBFixedLimits']),'pFWVBMeasure3Classes',str(kwds['pFWVBMeasure3Classes']))) 
                      
            keys = sorted(kwds.keys())
            logger.debug("{0:s}keys: {1:s}".format(logStr,str(keys))) 
            for key in keys:
                value=kwds[key]
                logger.debug("{0:s}kwd {1:s}: {2:s}".format(logStr,key,str(value))) 

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                     
        
        try: 
            # 2 Szenrariumzeiten ermitteln ===============================================
            firstTime=self.mx.df.index[0]
            if isinstance(kwds['timeDeltaToRef'],pd.Timedelta):
                timeRef=firstTime+kwds['timeDeltaToRef']
            else:
                logStrFinal="{:s}{:s} not Type {:s}.".format(logStr,'timeDeltaToRef','pd.Timedelta')
                logger.error(logStrFinal) 
                raise RmError(logStrFinal)  
            if isinstance(kwds['timeDeltaToT'],pd.Timedelta):
                timeT=firstTime+kwds['timeDeltaToT']
            else:
                logStrFinal="{:s}{:s} not Type {:s}.".format(logStr,'timeDeltaToT','pd.Timedelta')
                logger.error(logStrFinal) 
                raise RmError(logStrFinal)  
           
            # Vektorergebnisse zu den 2 Zeiten holen ===============================================
            timesReq=[]
            timesReq.append(timeRef)
            timesReq.append(timeT)           
            plotTimeDfs=self.mx.getMxsVecsFileData(timesReq=timesReq)
            timeRefIdx=0
            timeTIdx=1

            # Sachdatenbasis ===============================================
            vROHR=self.xm.dataFrames['vROHR'] 
            vKNOT=self.xm.dataFrames['vKNOT']
            vFWVB=self.xm.dataFrames['vFWVB']
            vNRCV_Mx1=self.xm.dataFrames['vNRCV_Mx1']

            if isinstance(kwds['pVICsDf'],pd.core.frame.DataFrame):
                vFWVB=vFWVB.merge(kwds['pVICsDf'],left_on='NAME_i',right_on='Knotenname',how='left')
                vFWVB.rename(columns={'Kundenname':'VIC'},inplace=True)
                vFWVB.drop('Knotenname',axis=1,inplace=True)
           
            # Einheit der Measures ermitteln (fuer Annotationen)
            pFWVBMeasureCh=self.mx.mx1Df[self.mx.mx1Df['Sir3sID'].str.startswith(kwds['pFWVBMeasure'])]
            pFWVBMeasureUNIT=pFWVBMeasureCh.iloc[0].UNIT
            pFWVBMeasureATTRTYPE=pFWVBMeasureCh.iloc[0].ATTRTYPE

            pROHRMeasureCh=self.mx.mx1Df[self.mx.mx1Df['Sir3sID'].str.startswith(kwds['pROHRMeasure'])]
            pROHRMeasureUNIT=pROHRMeasureCh.iloc[0].UNIT
            pROHRMeasureATTRTYPE=pROHRMeasureCh.iloc[0].ATTRTYPE

            # Sachdaten annotieren mit Spalte Measure 

            # FWVB            
            pFWVBMeasureValueRaw=plotTimeDfs[timeTIdx][kwds['pFWVBMeasure']].iloc[0] 
            pFWVBMeasureValueRefRaw=plotTimeDfs[timeRefIdx][kwds['pFWVBMeasure']].iloc[0] 

            pFWVBMeasureValue=[None for m in pFWVBMeasureValueRaw]
            pFWVBMeasureValueRef=[None for m in pFWVBMeasureValueRefRaw]
            for idx in range(len(pFWVBMeasureValueRaw)):                   
                mx2Idx=vFWVB['mx2Idx'].iloc[idx]
                
                m=pFWVBMeasureValueRaw[mx2Idx]
                pFWVBMeasureValue[idx]=m
                m=pFWVBMeasureValueRefRaw[mx2Idx]
                pFWVBMeasureValueRef[idx]=m
              
            if kwds['pFWVBMeasureInRefPerc']:  # auch in diesem Fall traegt die Spalte Measure das Ergebnis                               
                pFWVBMeasureValuePerc=[float(m)/float(mRef) if float(mRef) >0 else 1 for m,mRef in zip(pFWVBMeasureValue,pFWVBMeasureValueRef)]
                pFWVB=vFWVB.assign(Measure=pd.Series(pFWVBMeasureValuePerc)) #!                                
            else:
                pFWVB=vFWVB.assign(Measure=pd.Series(pFWVBMeasureValue)) #!                              

            pFWVB=pFWVB.assign(MeasureOrig=pd.Series(pFWVBMeasureValue)) 
            pFWVB=pFWVB.assign(MeasureRef=pd.Series(pFWVBMeasureValueRef)) 

            # Sachdaten annotieren mit Spalte MCategory           
            pFWVBCat=[]
            for index, row in pFWVB.iterrows():
                if row.Measure >= kwds['pFWVBMeasureCBFixedLimitHigh']:
                    pFWVBCat.append(kwds['pMCatTopText'])
                elif row.Measure <= kwds['pFWVBMeasureCBFixedLimitLow']:
                    pFWVBCat.append(kwds['pMCatBotText'])
                else:
                    pFWVBCat.append(kwds['pMCatMidText'])
            pFWVB=pFWVB.assign(MCategory=pd.Series(pFWVBCat)) 

            # Sachdaten annotieren mit Spalte GCategory (mit den verlangten Waermebilanzen zu denen ein FWVB gehoert)     
            if isinstance(kwds['pFWVBGCategory'],list):         
                sCatReq=set(kwds['pFWVBGCategory'])       
                pFWVBCat=[]
                for index, row in pFWVB.iterrows():
                    gCat=row.WBLZ
                    sCat=set(gCat)
                    s=sCat.intersection(sCatReq)
                    if len(s) == 0:
                        pFWVBCat.append('')
                    elif len(s) > 1:
                        pFWVBCat.append("{!s:s}".format(s)) 
                    else:
                        pFWVBCat.append(s.pop())
                pFWVB=pFWVB.assign(GCategory=pd.Series(pFWVBCat)) 
            else:
                pFWVB=pFWVB.assign(GCategory=pd.Series()) 

            # ROHR
            pROHRMeasureValueRaw=plotTimeDfs[timeTIdx][kwds['pROHRMeasure']].iloc[0]               
            pROHRMeasureValue=[None for m in pROHRMeasureValueRaw]
            for idx in range(len(pROHRMeasureValueRaw)):                   
                mx2Idx=vROHR['mx2Idx'].iloc[idx]
                m=pROHRMeasureValueRaw[mx2Idx]

                mApplied=kwds['pROHRMeasureApplyFunction'](m)
                pROHRMeasureValue[idx]=mApplied

            pROHR=vROHR.assign(Measure=pd.Series(pROHRMeasureValue)) #!

            # ========================================
            # ROHR Attribute-Behandlung wg. float & Filter
            # ========================================        
            pROHR[kwds['pROHRAttribute']]=pROHR[kwds['pROHRAttribute']].apply(kwds['pROHRAttributeApplyFunction']) 
            pROHR[kwds['pROHRAttribute']]=pROHR[kwds['pROHRAttribute']].fillna(kwds['pROHRAttributeApplyFunctionNaNValue']).astype(float)       
             
            # ROHRe filtern
            row,col=pROHR.shape
            logger.debug("{:s}pROHR vor   filtern: Zeilen: {:d}".format(logStr,row))   
            f=kwds['pROHRFilterFunction']  
            logger.debug("{:s}pltROHR Filterfunktion: {:s}".format(logStr,str(f)))     
            pltROHR=pROHR[f] #!    
            row,col=pltROHR.shape
            logger.debug("{:s}pltROHR nach filtern: Zeilen: {:d}".format(logStr,row))        

            # ========================================
            # FWVB Attribute-Behandlung wg. float & Filter
            # ========================================
            pFWVB[kwds['pFWVBAttribute']]=pFWVB[kwds['pFWVBAttribute']].apply(kwds['pFWVBAttributeApplyFunction'])
            pFWVB[kwds['pFWVBAttribute']]=pFWVB[kwds['pFWVBAttribute']].fillna(kwds['pFWVBAttributeApplyFunctionNaNValue']).astype(float) 
            
            # FWVB filtern
            row,col=pFWVB.shape
            logger.debug("{:s}pFWVB vor   filtern: Zeilen: {:d}".format(logStr,row))   
            f=kwds['pFWVBFilterFunction']  
            logger.debug("{:s}pltFWVB Filterfunktion: {:s}".format(logStr,str(f)))     
            pltFWVB=pFWVB[f] #!          
            row,col=pltFWVB.shape
            logger.debug("{:s}pltFWVB nach filtern: Zeilen: {:d}".format(logStr,row))    

            
            pltFWVB=pltFWVB[(pltFWVB[kwds['pFWVBAttribute']]<=pltFWVB[kwds['pFWVBAttribute']].quantile(kwds['quantil_pFWVBAttributeHigh']))
                            &
                            (pltFWVB[kwds['pFWVBAttribute']]>=pltFWVB[kwds['pFWVBAttribute']].quantile(kwds['quantil_pFWVBAttributeLow']))
                           ]

            logger.debug("{:s}pltROHR: quantil_pROHRAttributeHigh: {:f} f(): {:f}".format(logStr
                                                                                          ,kwds['quantil_pROHRAttributeHigh']
                                                                                          ,pltROHR[kwds['pROHRAttribute']].quantile(kwds['quantil_pROHRAttributeHigh'])
                                                                                          ))
            logger.debug("{:s}pltROHR: quantil_pROHRAttributeLow: {:f} f(): {:f}".format(logStr
                                                                                          ,kwds['quantil_pROHRAttributeLow']
                                                                                          ,pltROHR[kwds['pROHRAttribute']].quantile(kwds['quantil_pROHRAttributeLow'])
                                                                                          ))                              


            pltROHR=pltROHR[(pltROHR[kwds['pROHRAttribute']]<=pltROHR[kwds['pROHRAttribute']].quantile(kwds['quantil_pROHRAttributeHigh']))
                            &
                            (pltROHR[kwds['pROHRAttribute']]>=pltROHR[kwds['pROHRAttribute']].quantile(kwds['quantil_pROHRAttributeLow']))
                           ]

            row,col=pltROHR.shape
            logger.debug("{:s}pltROHR nach selektieren: {:d}".format(logStr,row))     

            # Grundsortierung z-Order
            pltFWVB=pltFWVB.sort_values(by=[kwds['pFWVBAttribute']],ascending=kwds['pFWVBAttributeAsc']) 
            pltROHR=pltROHR.sort_values(by=[kwds['pROHRAttribute']],ascending=kwds['pROHRAttributeAsc']) 
           
            # ############################################################
            # ============================================================
            # Plotten
            # ============================================================
            # ############################################################
            pltNetFigAx(
                pDf=pltROHR
               ,pXCor_i='pXCor_i'  # colName 
               ,pYCor_i='pYCor_i'  # colName          
               ,pXCor_k='pXCor_k'  # colName 
               ,pYCor_k='pYCor_k'  # colName   

               ,CBFraction=kwds['CBFraction'] 
               ,CBHpad=kwds['CBHpad']              

               ,pltTitle=kwds['pltTitle']
               ,figFrameon=kwds['figFrameon']
               #,figLinewidth=1.
               ,figEdgecolor=kwds['figEdgecolor'] 
               ,figFacecolor=kwds['figFacecolor']                                                                                            
            )
            fig = plt.gcf()  
            ax=plt.gca()

            pFWVBrefSizeValue=pltFWVB[kwds['pFWVBAttribute']].std()
            if pFWVBrefSizeValue < 1:
                pFWVBrefSizeValue=pltFWVB[kwds['pFWVBAttribute']].mean()
            logger.debug("{:s}pFWVBrefSizeValue (Attributwert): {:6.2f}".format(logStr,pFWVBrefSizeValue)) 
            pFWVBSizeFactor=kwds['pFWVBAttributeRefSize']/pFWVBrefSizeValue
            
            pcFWVB, CBLimitLow, CBLimitHigh = pltNetNodes(
                # ALLG
                 pDf=pltFWVB   
                ,pMeasure3Classes=kwds['pFWVBMeasure3Classes'] 

                ,CBFixedLimits=kwds['pFWVBMeasureCBFixedLimits']
                ,CBFixedLimitLow=kwds['pFWVBMeasureCBFixedLimitLow'] 
                ,CBFixedLimitHigh=kwds['pFWVBMeasureCBFixedLimitHigh'] 
                # FWVB
                ,pMeasure='Measure' 
                ,pAttribute=kwds['pFWVBAttribute']
                                             
                ,pSizeFactor=pFWVBSizeFactor
                   
                ,pMeasureColorMap=kwds['pFWVBMeasureColorMap'] 
                ,pMeasureAlpha=kwds['pFWVBMeasureAlpha']
                ,pMeasureClip=kwds['pFWVBMeasureClip']    
   
                ,pMCategory='MCategory' 
                ,pMCatTopTxt=kwds['pMCatTopText'] # 'Top'     
                ,pMCatBotTxt=kwds['pMCatBotText'] # 'Bottom'    
                ,pMCatMidTxt=kwds['pMCatMidText'] # 'Middle'             
               
                ,pMCatTopColor=kwds['pMCatTopColor']
                ,pMCatTopAlpha=kwds['pMCatTopAlpha']
                ,pMCatTopClip=kwds['pMCatTopClip']   
                                                                        
                ,pMCatBotColor=kwds['pMCatBotColor'] 
                ,pMCatBotAlpha=kwds['pMCatBotAlpha']
                ,pMCatBotClip=kwds['pMCatBotClip']
                  
                ,pMCatMidColorMap=kwds['pMCatMidColorMap']
                ,pMCatMidAlpha=kwds['pMCatMidAlpha']
                ,pMCatMidClip=kwds['pMCatMidClip']
            )

            #fig.sca(ax)

            pROHRMeasureRefSizeValue=pltROHR['Measure'].std()
            if pROHRMeasureRefSizeValue < 1:
                pROHRMeasureRefSizeValue=pltROHR['Measure'].mean()
            logger.debug("{:s}pROHRMeasureRefSizeValue: {:6.2f}".format(logStr,pROHRMeasureRefSizeValue)) 
            pROHRMeasureSizeFactor=kwds['pROHRMeasureRefSize']/pROHRMeasureRefSizeValue

            pROHRAttributeRefSizeValue=pltROHR[kwds['pROHRAttribute']].std()
            if pROHRAttributeRefSizeValue < 1:
                pROHRAttributeRefSizeValue=pltROHR[kwds['pROHRAttribute']].mean()
            logger.debug("{:s}pROHRAttributeRefSizeValue: {:6.2f}".format(logStr,pROHRAttributeRefSizeValue)) 
            pROHRAttributeSizeFactor=kwds['pROHRAttributeRefSize']/pROHRAttributeRefSizeValue

            pltNetPipes(
                pltROHR
               ,pAttribute=kwds['pROHRAttribute']  # Line
               ,pMeasure='Measure'  # Marker

               ,pClip=False
               ,pAttributeLs=kwds['pROHRAttributeLs'] 
               ,pMeasureMarker=kwds['pROHRMeasureMarker']

               ,pAttributeColorMap=kwds['pROHRAttributeColorMap'] 
               ,pAttributeColorMapUsageStart=kwds['pROHRAttributeColorMapUsageStart'] 
               ,pAttributeSizeFactor=pROHRAttributeSizeFactor   
               ,pAttributeSizeMin=kwds['pROHRAttributeSizeMin'] 

               ,pMeasureColorMap=kwds['pROHRMeasureColorMap'] 
               ,pMeasureColorMapUsageStart=kwds['pROHRMeasureColorMapUsageStart']             
               ,pMeasureSizeFactor=pROHRMeasureSizeFactor     
               ,pMeasureSizeMin=kwds['pROHRMeasureSizeMin'] 
            )

            # ============================================================
            # Legend
            # ============================================================

            cax=pltNetLegendColorbar(
                # ALLG
                 pc=pcFWVB # PathCollection aus pltNetNodes                                        
                ,pDf=pltFWVB 
                ,pMeasureInPerc=kwds['pFWVBMeasureInRefPerc'] 
                ,pMeasure3Classes=kwds['pFWVBMeasure3Classes']      
                
                # Ticks (TickLabels und TickValues)
                ,CBFixedLimits=kwds['pFWVBMeasureCBFixedLimits']
                ,CBFixedLimitLow=kwds['pFWVBMeasureCBFixedLimitLow']
                ,CBFixedLimitHigh=kwds['pFWVBMeasureCBFixedLimitHigh']                       

                #
                ,pMeasure='Measure'           
         
                # Label
                ,pMeasureUNIT=pFWVBMeasureUNIT
                ,pMeasureTYPE=pFWVBMeasureATTRTYPE

                # Geometrie
                ,CBFraction=kwds['CBFraction']  
                ,CBHpad=kwds['CBHpad']          
                ,CBLabelPad=kwds['CBLabelPad']    
                ,CBTicklabelsHPad=kwds['CBTicklabelsHPad']                          
                ,CBAspect=kwds['CBAspect'] 
                ,CBShrink=kwds['CBShrink'] 
                ,CBAnchorHorizontal=kwds['CBAnchorHorizontal'] 
                ,CBAnchorVertical=kwds['CBAnchorVertical'] 
            )
    
            if kwds['pFWVBMeasure3Classes']:                                                                   
                 bbTop, bbMid, bbBot = pltNetLegendColorbar3Classes(                 
                     pDf=pltFWVB          
                    ,pMCategory='MCategory' 
                    ,pMCatTopTxt=kwds['pMCatTopText']     
                    ,pMCatBotTxt=kwds['pMCatBotText']       
                    ,pMCatMidTxt=kwds['pMCatMidText']     

                    ,pMCatBotColor=kwds['pMCatBotColor'] 
                    ,pMCatTopColor=kwds['pMCatTopColor'] 

                    ,CBLe3cTopVPad=kwds['CBLe3cTopVPad'] 
                    ,CBLe3cMidVPad=kwds['CBLe3cMidVPad']                                                                     
                    ,CBLe3cBotVPad=kwds['CBLe3cBotVPad'] 
                    ,CBLe3cSySize=kwds['CBLe3cSySize'] 
                    ,CBLe3cSyType=kwds['CBLe3cSyType']                                                                                                    
                 )
                 TBAV=1.15*bbTop.y1
            else:
                 TBAV=1.15
            
            xmFileName,ext = os.path.splitext(os.path.basename(self.xm.xmlFile))
            (wDir,modelDir,modelName,mx1File)=self.xm.getWDirModelDirModelName()
            Projekt=self.xm.dataFrames['MODELL']['PROJEKT'].iloc[0]
            Planer=self.xm.dataFrames['MODELL']['PLANER'].iloc[0]
            Inst=self.xm.dataFrames['MODELL']['INST'].iloc[0]       
            Model="M: {:s}".format(xmFileName)   
            Result="E: {:s}".format(mx1File)   
            Times="TRef: {!s:s} T: {!s:s}".format(kwds['timeDeltaToRef'],kwds['timeDeltaToT']).replace('days','Tage')       
            pltNetLegendTitleblock(
               text=str(Projekt)+'\n'+str(Planer)+'\n'+str(Inst)+'\n'+str(Model)+'\n'+str(Result)+'\n'+str(Times) 
              ,anchorVertical=TBAV                    
            )
                   
            # ============================================================
            # NRCVs to be displayed in Net
            # ============================================================
            text=None
            if isinstance(kwds['pFIGNrcv'],list) and isinstance(kwds['pFIGNrcvTxt'],list):
                if len(kwds['pFIGNrcv']) == len(kwds['pFIGNrcvTxt']):                    
                    for idx,Sir3sIDRexp in  enumerate(kwds['pFIGNrcv']):                           
                        try:
                            sCh=self.mx.mx1Df[self.mx.mx1Df['Sir3sID'].str.contains(Sir3sIDRexp)].iloc[0]
                        except:
                            logger.debug("{:s} Sir3sIDRexp {:s} nicht in .MX1".format(logStr,Sir3sIDRexp))
                            continue # NRCV wird ausgelassen
                    
                        s=self.mx.df[sCh.Sir3sID]                
                        v=s[timeT]  
                        v0=s[timeRef]
                        if v0==0:                            
                            vp=100.
                        else:
                            vp=v/v0*100     
                                              
                        fmtStr=kwds['pFIGNrcvFmt']
                        if kwds['pFWVBMeasureInRefPerc']:
                            fmtStr=fmtStr+kwds['pFIGNrcvPercFmt']                                                  
                            txt=fmtStr.format(kwds['pFIGNrcvTxt'][idx],v,sCh.UNIT,vp) 
                        else:
                            txt=fmtStr.format(kwds['pFIGNrcvTxt'][idx],v,sCh.UNIT)                        

                        if text==None:
                            text=txt
                        else:
                            text=text+'\n'+txt
                    
                    fig.sca(ax)            
                    pltNetTextblock(text=text,x=kwds['pFIGNrcvXStart'],y=kwds['pFIGNrcvYStart'])         
                      
            # ============================================================
            # User Heat Balances to be displayed in Net
            # ============================================================            
                                         
            vWBLZ=self.xm.dataFrames['vWBLZ']
            vWBLZ_vKNOT=pd.merge(vWBLZ,vKNOT,left_on='OBJID',right_on='pk')
            vWBLZ_vKNOT_pFWVB=pd.merge(vWBLZ_vKNOT,pFWVB,left_on='NAME_y',right_on='NAME_i')

            vWBLZ_vKNOT_pFWVB=vWBLZ_vKNOT_pFWVB[['NAME_x','NAME_i','pk','W','pk_x','WBLZ', 'Measure', 'MeasureRef','MeasureOrig','MCategory', 'GCategory']]
            vWBLZ_vKNOT_pFWVB.rename(columns={'NAME_x':'NAME','pk_x':'pkWBLZ'},inplace=True)

            vNRCV_Mx1=self.xm.dataFrames['vNRCV_Mx1']
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1=pd.merge(vWBLZ_vKNOT_pFWVB,vNRCV_Mx1,left_on='pkWBLZ',right_on='fkOBJTYPE',how='left')
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1['Sir3sID']=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1['Sir3sID'].fillna(value='')
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1['cRefLfdNr']=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1['cRefLfdNr'].fillna(value=1)
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1.rename(columns={'pk_x':'pkFWVB'},inplace=True)

            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1[['NAME','NAME_i','pkFWVB','W','WBLZ','Sir3sID'
                                                         , 'Measure', 'MeasureRef','MeasureOrig','MCategory', 'GCategory','cRefLfdNr']]
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1[vWBLZ_vKNOT_pFWVB_vNRCV_Mx1['cRefLfdNr']==1]
            vWBLZ_vKNOT_pFWVB_vNRCV_Mx1.drop('cRefLfdNr',axis=1,inplace=True)
            
            vAggNumAnz=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1.groupby(['NAME','Sir3sID']).size()            

            vAggWblzMCat=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1.groupby(['NAME','MCategory']).agg(
            {
                 'W': ['size','min', 'max', 'sum']
                ,'Measure': ['size','min', 'max', 'sum']
                ,'MeasureOrig': ['size','min', 'max', 'sum']
                ,'MeasureRef': ['size','min', 'max', 'sum']
            })

            vAggWblz=vWBLZ_vKNOT_pFWVB_vNRCV_Mx1.groupby(['NAME']).agg(
            {
                'W': ['size','min', 'max', 'sum']
               ,'Measure': ['size','min', 'max', 'sum']
               ,'MeasureOrig': ['size','min', 'max', 'sum']
               ,'MeasureRef': ['size','min', 'max', 'sum']
            })

            if isinstance(kwds['pFWVBGCategory'],list):    
                text=None
                for NAME in kwds['pFWVBGCategory']: # verlangte Wärmebilanzen       
                    try: 
                        vSoll=vAggWblz.loc[NAME]['MeasureRef']['sum']
                        vIst=vAggWblz.loc[NAME]['MeasureOrig']['sum']                                     
                        vpAgg=vIst/vSoll*100                                                                                                             
                    except:
                        logger.debug("{:s} verlangte Wärmebilanz (aus pFWVBGCategory)={:s} ist nicht definiert.".format(logStr,NAME))    
                        continue

                    try:                                       
                        topAnz=int(vAggWblzMCat.loc[NAME,kwds['pMCatTopText']]['Measure']['size'])                                                                                
                    except:
                        topAnz=0
                   
                    try:                                                          
                        midAnz=int(vAggWblzMCat.loc[NAME,kwds['pMCatMidText']]['Measure']['size'])                                                                             
                    except:                 
                        midAnz=0
                  
                    try:                                                         
                        botAnz=int(vAggWblzMCat.loc[NAME,kwds['pMCatBotText']]['Measure']['size'])                                                                 
                    except:                   
                        botAnz=0                   

                    try: 
                        Sir3sID=vAggNumAnz.loc[NAME].index[0]   
                        sCh=self.mx.mx1Df[self.mx.mx1Df['Sir3sID'].str.startswith(Sir3sID)].iloc[0]
                        s=self.mx.df[Sir3sID]    
                        v=s[timeT]                
                        v0=s[timeRef]
                        vp=v/v0*100     
                    
                        if math.fabs(vpAgg-vp) > 0.1:
                            logger.error("{:s} für verlangte Wärmebilanz (aus pFWVBGCategory)={:s} ist das NumAnz Ergebnis verschieden vom Agg Ergebnis!".format(logStr,NAME))  
                                                                                                                                        
                    except:
                        logger.debug("{:s} für verlangte Wärmebilanz (aus pFWVBGCategory)={:s} ist keine NumAnz definiert.".format(logStr,NAME))  
                        continue                      
                                                                                    
                    vpIstZuvSoll=vIst/vSoll
                    if kwds['pFWVBGCategoryUnit']=='[MW]':
                        vIst=vIst/1000.

                    fmtStr=kwds['pFWVBGCategoryCatFmt']
                    if kwds['pFWVBMeasureInRefPerc'] and kwds['pFWVBMeasure3Classes']:
                        fmtStr=fmtStr+kwds['pFWVBGCategoryPercFmt']+kwds['pFWVBGCategory3cFmt']
                        txt=fmtStr.format(NAME,vIst,kwds['pFWVBGCategoryUnit'],vpIstZuvSoll*100,topAnz,midAnz,botAnz)
                    if kwds['pFWVBMeasureInRefPerc'] and not kwds['pFWVBMeasure3Classes']:
                        fmtStr=fmtStr+kwds['pFWVBGCategoryPercFmt']
                        txt=fmtStr.format(NAME,vIst,kwds['pFWVBGCategoryUnit'],vpIstZuvSoll*100)
                    if not kwds['pFWVBMeasureInRefPerc'] and kwds['pFWVBMeasure3Classes']:
                        fmtStr=fmtStr+kwds['pFWVBGCategory3cFmt']
                        txt=fmtStr.format(NAME,vIst,kwds['pFWVBGCategoryUnit'],topAnz,midAnz,botAnz)

                    if text==None:
                            text=txt
                    else:
                            text=text+'\n'+txt
                
                fig.sca(ax)            
                pltNetTextblock(text=text,x=kwds['pFWVBGCategoryXStart'],y=kwds['pFWVBGCategoryYStart'])         

            # ============================================================
            # VICs to be displayed in Net
            # ============================================================                                    

            if isinstance(kwds['pVICsDf'],pd.core.frame.DataFrame):
                text=None
                for index, row in pFWVB[pd.isnull(pFWVB['VIC'])==False].sort_values(['VIC'],ascending=False).iterrows():      
                        kunde=row.VIC                         
                        v=row.Measure
                        if kwds['pFWVBMeasureInRefPerc']:
                            txt=kwds['pVICsPercFmt'].format(kunde,v*100)      
                        else:                           
                            txt=kwds['pVICsFmt'].format(kunde,v,pFWVBMeasureUNIT)    
                        
                        if text==None:
                            text=txt
                        else:
                            text=text+'\n'+txt
                
                fig.sca(ax)            
                pltNetTextblock(text=text,x=kwds['pVICsXStart'],y=kwds['pVICsYStart'])   
                                                                           
        except RmError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise RmError(logStrFinal)                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return pFWVB 

if __name__ == "__main__":
    """
    Run Tests.
    """

    try:      
        
        # Arguments      
        parser = argparse.ArgumentParser(description='Run Tests.'
        ,epilog='''
        UsageExamples: 

        Modultest:

        -q -m 1 -t both -w OneLPipe -w LocalHeatingNetwork -w GPipe -w GPipes -w TinyWDN 

        Singletests:
        
        -q -m 0 -s "^Mx\." -t both -y yes -z no -w OneLPipe -w LocalHeatingNetwork -w GPipe -w GPipes -w TinyWDN 

        Singletests: separater MockUp-Lauf:

        -q -m 0 -t before -u yes -w DHNetwork
        
        Singletests (die auf dem vorstehenden MockUp-Lauf basieren):
        -q -m 0 -s "^Mx\." -z no -w DHNetwork

        '''                                 
        )

        group = parser.add_mutually_exclusive_group()                                
        group.add_argument("-v","--verbose", help="Debug Messages On", action="store_true",default=True)      
        group.add_argument("-q","--quiet", help="Debug Messages Off", action="store_true")           

        parser.add_argument('--testDir',type=str,default='testdata',help="value for global 'testDir' i.e. testdata")
        parser.add_argument('--dotResolution',type=str,default='.1',help="value for global 'dotResolution' i.e. .1 (default); use NONE for no dotResolution")      
                                 
        parser.add_argument("-m","--moduleTest", help="execute the Module Doctest On/Off: -m 1 (default)", action="store",default='1')      
        parser.add_argument("-s","--singleTest", help='execute single Doctest: Exp.1: -s  "^Rm.": all Doctests in Module Rm are executed - but not the Module Doctest (which is named Rm) Exp.2:  -s "^Xm."  -s "^Mx."  -s "^Rm.": all Doctests in the 3 Modules are executed - but not the Module Doctests'
                            ,action="append"
                            ,default=[])    
        parser.add_argument("-x","--singleTestNO", help='execute NOT single Doctest: Exp.1: -s  "^Rm.": NO Doctests in Module Rm are executed - but not the Module Doctest (which is named Rm) Exp.2:  -s "^Xm."  -s "^Mx."  -s "^Rm.": NO Doctests in the 3 Modules are executed - but not the Module Doctests'
                            ,action="append"
                            ,default=[])               
        parser.add_argument("-t","--delGenFiles", help="Tests: decide if generated Files - i.e. .h5-Files - shall be deleted: Exp.: -t both: generated Files are deleted before and after the Tests"
                            ,choices=['before', 'after', 'both','nothing'],default='nothing')

        parser.add_argument("-y","--mockUpDetail1", help="MockUp Detail1: decide if NoH5 shall be used during MockUps: Exp.: -y yes"
                            ,choices=['no','yes'],default='no')

        parser.add_argument("-z","--mockUpDetail2", help="MockUp Detail2: decide if Sync/Add and ToH5 shall be done during MockUps: Exp.: -z no"
                            ,choices=['no','yes'],default='yes')

        parser.add_argument("-u","--mockUpAtTheEnd", help="Tests: decide if after all Tests and after delGenFiles some mockUp shall be done: Exp.: -u yes"
                            ,choices=['no','yes'],default='no')

        parser.add_argument("-w","--testModel", help='specify a testModel: Exp.: -w DHNetwork'
                            ,action="append"
                            ,default=[])           

        parser.add_argument("-l","--logExternDefined", help="Logging (File etc.) ist extern defined", action="store_true",default=False)      


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
        logger.debug("{0:s}{1:s}{2:s}".format(logStr,'testDir: ',args.testDir)) 

        if args.dotResolution == 'NONE':
            args.dotResolution=''

        try:
            from PT3S import Mx, Xm
        except ImportError:
            logger.debug("{0:s}{1:s}".format("test: from PT3S import Mx, Xm: ImportError: ","trying import Mx, Xm ..."))  
            import Mx, Xm

        testModels=args.testModel 

        # die Modultests gehen i.d.R. vom Ausgangszustand aus; Relikte aus alten Tests müssen daher i.d.R. gelöscht werden ...
        if args.delGenFiles in ['before','both']:
                for testModel in testModels:   
                    #Xm                    
                    xmlFile=os.path.join(os.path.join('.',args.testDir),testModel+'.XML')                      
                    h5FileXm=os.path.join(os.path.join('.',args.testDir),testModel+'.h5')
                    #Mx
                    mx1File=os.path.join('.',os.path.join(args.testDir,'WD'+testModel+'\B1\V0\BZ1\M-1-0-1'+args.dotResolution+'.MX1'))                     
                    (wD,fileName)=os.path.split(mx1File)
                    (base,ext)=os.path.splitext(fileName)
                    (base,dotResolution)=os.path.splitext(base)                                                                             
                    h5File=wD+os.path.sep+base+'.'+'h5'    
                    h5FileVecs=wD+os.path.sep+base+dotResolution+'.'+'vec'+'.'+'h5' 
                    h5FileMx1FmtString=h5File+'.metadata'
                    #loeschen
                    for file in [h5FileXm,h5File,h5FileVecs,h5FileMx1FmtString]:                    
                        if os.path.exists(file):      
                            logger.debug("{:s}Tests Vorbereitung {:s} Delete {:s} ...".format(logStr,testModel,file)) 
                            os.remove(file)


        if args.moduleTest == '1':
            # as unittests
            logger.info("{0:s}{1:s}{2:s}".format(logStr,'Start unittests (by DocTestSuite...). testDir: ',args.testDir)) 

            dtFinder=doctest.DocTestFinder(recurse=False,verbose=args.verbose) # recurse = False findet nur den Modultest

            suite=doctest.DocTestSuite(test_finder=dtFinder #,setUp=setUpFct
                                   ,globs={'testDir':args.testDir
                                           ,'dotResolution':args.dotResolution
                                           })   
            unittest.TextTestRunner().run(suite)
                      
        if len(args.singleTest)>0:

            #Relikte, die die Modultests oder andere Tests produziert haben ggf. loeschen
            if args.delGenFiles in ['before','both']:
                for testModel in testModels:   
                    #Xm                    
                    xmlFile=os.path.join(os.path.join('.',args.testDir),testModel+'.XML')                      
                    h5FileXm=os.path.join(os.path.join('.',args.testDir),testModel+'.h5')
                    #Mx
                    mx1File=os.path.join('.',os.path.join(args.testDir,'WD'+testModel+'\B1\V0\BZ1\M-1-0-1'+args.dotResolution+'.MX1'))                     
                    (wD,fileName)=os.path.split(mx1File)
                    (base,ext)=os.path.splitext(fileName)
                    (base,dotResolution)=os.path.splitext(base)                                                                             
                    h5File=wD+os.path.sep+base+'.'+'h5'    
                    h5FileVecs=wD+os.path.sep+base+dotResolution+'.'+'vec'+'.'+'h5' 
                    h5FileMx1FmtString=h5File+'.metadata'
                    #loeschen
                    for file in [h5FileXm,h5File,h5FileVecs,h5FileMx1FmtString]:                    
                        if os.path.exists(file):      
                            logger.debug("{:s}singleTests Vorbereitung {:s} Delete {:s} ...".format(logStr,testModel,file)) 
                            os.remove(file)

            #MockUp
            logger.debug("{:s}singleTests Vorbereitung Start ...".format(logStr)) 
            xms={}   
            mxs={} 
            ms={}
                               
            for testModel in testModels:   
                logger.debug("{:s}singleTests Vorbereitung {:s} Start ...".format(logStr,testModel)) 


                #Xm
                xmlFile=os.path.join(os.path.join('.',args.testDir),testModel+'.XML')  
                ms[testModel]=xmlFile
                if args.mockUpDetail1 in ['yes']:   
                    xm=Xm.Xm(xmlFile=xmlFile,NoH5Read=True) 
                else:
                    xm=Xm.Xm(xmlFile=xmlFile)      
                logger.debug("{:s}singleTests Vorbereitung {:s} xm instanziert.".format(logStr,testModel)) 

                #Mx
                mx1File=os.path.join('.',os.path.join(args.testDir,'WD'+testModel+'\B1\V0\BZ1\M-1-0-1'+args.dotResolution+'.MX1'))    
                if args.mockUpDetail1 in ['yes']:   
                     mx=Mx.Mx(mx1File=mx1File,NoH5Read=True) 
                else:
                    mx=Mx.Mx(mx1File=mx1File) 
                logger.debug("{:s}singleTests Vorbereitung {:s} mx instanziert.".format(logStr,testModel)) 

                if args.mockUpDetail2 in ['yes']:                    
                    #Sync                
                    xm.MxSync(mx=mx)
                    xm.MxAdd(mx=mx)
                    logger.debug("{:s}singleTests Vorbereitung {:s} Sync/Add erfolgt.".format(logStr,testModel)) 

                    #H5
                    xm.ToH5()
                    mx.ToH5()
                    logger.debug("{:s}singleTests Vorbereitung {:s} ToH5 erfolgt.".format(logStr,testModel)) 
                
                xms[testModel]=xm
                mxs[testModel]=mx
                logger.debug("{:s}singleTests Vorbereitung {:s} fertig.".format(logStr,testModel)) 
 
            dtFinder=doctest.DocTestFinder(verbose=args.verbose)
                     
            logger.debug("{:s}singleTests suchen in Rm ...".format(logStr)) 
            dTests=dtFinder.find(Rm,globs={'testDir':args.testDir     
                                           ,'dotResolution':args.dotResolution
                                           ,'xms':xms
                                           ,'mxs':mxs})

            dTests.extend(dtFinder.find(pltMakeCategoricalColors))
            dTests.extend(dtFinder.find(pltMakeCategoricalCmap))       
            dTests.extend(dtFinder.find(findAllTimeIntervallsSeries))

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

        if args.delGenFiles in ['after','both']:              
            for testModel in testModels:   
                logger.debug("{:s}Tests Nachbereitung {:s} Delete files ...".format(logStr,testModel)) 
                mx=mxs[testModel]
                mx.delFiles()        
                xm=xms[testModel]
                xm.delFiles()   
                if os.path.exists(mx.mxsZipFile):                        
                    os.remove(mx.mxsZipFile)
                mxsDumpFile=mx.mxsFile+'.dump'
                if os.path.exists(mxsDumpFile):                        
                    os.remove(mxsDumpFile)

        if args.mockUpAtTheEnd in ['yes']:                
            for testModel in testModels:
                logger.debug("{:s}Tests Nachbereitung {:s} mockUpAtTheEnd ...".format(logStr,testModel)) 

                #Mx
                mx1File=os.path.join('.',os.path.join(args.testDir,'WD'+testModel+'\B1\V0\BZ1\M-1-0-1'+args.dotResolution+'.MX1')) 
                if args.mockUpDetail1 in ['yes']:                 
                    mx=Mx.Mx(mx1File=mx1File,NoH5Read=True) # avoid doing anything than just plain Init                         
                else:
                    mx=Mx.Mx(mx1File=mx1File) 
                #Xm                     
                xmlFile=os.path.join(os.path.join('.',args.testDir),testModel+'.XML')
                if args.mockUpDetail1 in ['yes']:    
                    xm=Xm.Xm(xmlFile=xmlFile,NoH5Read=True) # avoid doing anything than just plain Init                                           
                else:
                    xm=Xm.Xm(xmlFile=xmlFile) 
                   
                if args.mockUpDetail2 in ['yes']:                    
                    #Sync                
                    xm.MxSync(mx=mx)
                    xm.MxAdd(mx=mx)
                    logger.debug("{:s}Tests Nachbereitung {:s} Sync/Add erfolgt.".format(logStr,testModel)) 

                    #H5
                    xm.ToH5()
                    mx.ToH5()
                    logger.debug("{:s}Tests Nachbereitung {:s} ToH5 erfolgt.".format(logStr,testModel)) 
                                
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

