
"""

"""

__version__='90.12.4.23.dev1'

import sys
import os
import logging
import pandas as pd
import re
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

logger = logging.getLogger('PT3S')  

try:
    from PT3S import Rm
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Rm - trying import Rm instead ... maybe pip install -e . is active ...')) 
    import Rm

try:
    from PT3S import Lx
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Lx - trying import Lx instead ... maybe pip install -e . is active ...')) 
    import Lx

def addResVecToDfAlarmEreignisse(    
    dfAlarmEreignisse
   ,TCsLDSRes1=pd.DataFrame()
   ,TCsLDSRes2=pd.DataFrame()   
    ):
    """
    dfAlarmEreignisse:
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
        AlarmEvent:         AlarmEvent-Objekt       
        BZKat:              Betriebszustandskategorie des Alarms

    Returns:
    dfAlarmEreignisse with 2 Cols added:              
        resIDBase:          die 1. OrtID von OrteIDs
        dfResVec:           der resVec des Alarms
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        

    try:            

        dfAlarmEreignisse['resIDBase']=dfAlarmEreignisse['OrteIDs'].apply(lambda x: x[0])
              
        ### Ergebnisvektor fuer alle Orte bestimmen
        dfResVecs={}
        dfResVecsLst=[]

        for indexAlarm, rowAlarm in dfAlarmEreignisse.iterrows():
       
            resIDBase=rowAlarm['resIDBase']

            if resIDBase in dfResVecs.keys():
                # resIDBase schon behandelt
                dfResVecsLst.append(dfResVecs[resIDBase])
                continue

            # Spalten basierend auf resIDBase bestimmen 
            ErgIDs=[resIDBase+ext for ext in Rm.ResChannelTypesAll]
            IMDIErgIDs=['IMDI.'+ID for ID in ErgIDs] # jede Spalte koennte anstatt "normal" als IMDI. vorhanden sein
            ErgIDsAll=[*ErgIDs,*IMDIErgIDs] 
           
            # Ergebnisspalten  
            if rowAlarm['LDSResBaseType']=='SEG':
                dfFiltered=TCsLDSRes1.filter(items=ErgIDsAll,axis=1)
            else:
                dfFiltered=TCsLDSRes2.filter(items=ErgIDsAll,axis=1)
        
            # Ergebnisspalten umbenennen
            colDct={}
            for col in dfFiltered.columns:            
                m=re.search(Lx.pID,col)
                colDct[col]=m.group('E')
            dfFiltered.name=resIDBase
            dfResVec=dfFiltered.rename(columns=colDct)        

            # Ergebnisvektor merken
            dfResVecs[resIDBase]=dfResVec

            dfResVecsLst.append(dfResVec)

            logger.debug("{:s}resIDBase: {:50s} Anzahl gefundener Spalten in TCsLDSRes: {:d}".format(logStr, resIDBase, len(dfResVec.columns.to_list())))   

        dfAlarmEreignisse['dfResVec']=dfResVecsLst


                                                                                                                          
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise e   

    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return dfAlarmEreignisse

def fGenAlarmVisTimeSpan(
                     tA
                    ,tE                   
                    # alle nachfolgenden Werte sollten dieselbe Einheit haben und in dieser Einheit ganzzahlig sein
                    ,timeSpan=pd.Timedelta('25 Minutes')
                    ,timeRoundStr='1T'
                    ,timeBoundaryMin=pd.Timedelta('3 Minutes')
                    ,timeRef='A' # Alarme die laenger sind: Anfang oder Ende werden mit timeSpan dargestellt
                    ):
                    """
                    erzeugt eine Zeitspanne in welcher ein Alarm Zwecks Analyse dargestellt wird

                    tA, tE sind Anfang und Ende des Alarms
                    diese werden ab- (tA) bzw. aufgerundet (tE) mit timeRoundStr

                    zwischen den gerundeten Zeiten und tA/tE soll mindestens timeBoundaryMin liegen
                    wenn nicht, wird timeBoundaryMin auf tA/tE angewendet und dann wird gerundet 

                    timeSpan ist die gewuenschte minimale Zeitspanne

                    Alarme die kuerzer sind werden mit timeSpan dargestellt

                    Alarme die laenger sind: Anfang oder Ende wird mit timeSpan dargestellt
                    
                    """

                    # Zeiten ab- und aufrunden
                    timeStart=tA.floor(freq=timeRoundStr) 
                    timeEnd=tE.ceil(freq=timeRoundStr) 

                    # gerundete Zeiten auf Mindestabstand pruefen
                    if tA-timeStart < timeBoundaryMin:
                        timeStart=tA-timeBoundaryMin
                        timeStart= timeStart.floor(freq=timeRoundStr) 

                    if timeEnd-tE < timeBoundaryMin:
                        timeEnd=tE+timeBoundaryMin
                        timeEnd= timeEnd.ceil(freq=timeRoundStr) 

                    # gerundete Zeiten auf Zeitspanne pruefen
                    timeLeft=timeSpan-(timeEnd-timeStart)

                    if timeLeft > pd.Timedelta('0 Seconds'): # die aufgerundete Alarmzeit ist kuerzer als timeSpan; timeSpan wird dargestellt
                        timeStart=timeStart-timeLeft/2
                        timeStart= timeStart.floor(freq=timeRoundStr) 
                        timeEnd=timeEnd+timeLeft/2
                        timeEnd= timeEnd.ceil(freq=timeRoundStr) 

                    else:                    
                        # die aufgerundete Alarmzeit ist laenger als timeSpan; A oder E wird mit timeSpan wird dargestellt
                        if timeRef=='A':
                            timeM=tA.floor(freq=timeRoundStr) 
                        else:
                            timeM=tE.ceil(freq=timeRoundStr) 

                        timeStart=timeM-timeSpan/2
                        timeEnd=timeM+timeSpan/2
                          

                    if timeEnd-timeStart > timeSpan:
                        timeEnd=timeStart+timeSpan

                    ZeitbereichSel=timeEnd-timeStart

                    if ZeitbereichSel <= pd.Timedelta('1 Minutes'):
                             bysecond=list(np.arange(0,60,1))
                             byminute=None

                    elif ZeitbereichSel <= pd.Timedelta('3 Minutes'):
                             bysecond=list(np.arange(0,60,5))
                             byminute=None
                    elif ZeitbereichSel > pd.Timedelta('3 Minutes') and ZeitbereichSel <= pd.Timedelta('5 Minutes'):
                             bysecond=list(np.arange(0,60,15))           
                             byminute=None
                    elif ZeitbereichSel > pd.Timedelta('5 Minutes') and ZeitbereichSel <= pd.Timedelta('20 Minutes'):
                             bysecond=list(np.arange(0,60,30))
                             byminute=None
                    elif ZeitbereichSel > pd.Timedelta('20 Minutes') and ZeitbereichSel <= pd.Timedelta('30 Minutes'):
                             bysecond=None
                             byminute=list(np.arange(0,60,1))
                    else:
                             bysecond=None
                             byminute=list(np.arange(0,60,3))

                    return timeStart, timeEnd, byminute, bysecond

def rptAlarms(     
     pdfErgFile='rptAlarms.pdf'

    ,figsize=Rm.DINA2q
    ,dpi=Rm.dpiSize

    ,dfAlarmStatistik=pd.DataFrame()   # 1 Zeile pro SEG; Spalten mit Alarm-Informationen zum SEG
    ,dfAlarmEreignisse=pd.DataFrame() # 1 Zeile pro Alarm; Spalten mit Informationen zum Alarm

    ,TCsLDSRes1=pd.DataFrame()   
    ,TCsLDSRes2=pd.DataFrame()       

    ,TCsLDSIn=pd.DataFrame() 
    ,TCsOPC=pd.DataFrame() 

    ,TCsSIDEvents=pd.DataFrame() 
    ,IDSetsDctAlNr={} # AlNr-Keyed dct with ColIDs

    ,timeSpanMin={} # AlNr-Keyed dct with Timespan-Para

    ,QDct={} # AlNr-Keyed dct with QDct-Para
    ,pDct={} # AlNr-Keyed dct with pDct-Para
    ,QDctOPC={} # AlNr-Keyed dct with pDct-Para
    ,pDctOPC={} # AlNr-Keyed dct with pDctOPC-Para

    ,attrsDct=Rm.attrsDct  

    ,plotOnlyAlNrn=None # zu Testzwecken; Liste der zu reportenden Alarme 

    ,*args
    ,**kwds
    ):
    """
          
    # ueber alle Segmente mit Alarmen

    # alle Alarme eines SEGS in der Reihenfolge ihrer Nummerierung (also i.d.R. zeitlich) hintereinander
    
    # jeden Alarm mit HYD und LDS in einem Bild darstellen  

    # es werden Einzelbilder und ein PDF erzeugt

    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    try:   

        rptAlarmsResults={}
        # (gsHYD,gsLDS,pltLDSpQAndEventsResults,pltLDSErgVecResults)
                
        # PDF - DokAnfang
        pdf=PdfPages(pdfErgFile)
        (fileNameBase,ext)= os.path.splitext(pdfErgFile)

        # ueber alle Segmente 
      

        for indexSEG,rowSEG in dfAlarmStatistik.iterrows():

            strSEG="LfdNr {:2d} - {!s:3s}: {!s:15s}".format(
                    indexSEG+1
                   ,rowSEG.DIVPipelineName                           
                   ,rowSEG['SEGName']                                   
                 #  ,rowSEG['SEGResIDBase']
                  )

            if rowSEG['FörderZeitenAlAnz']==0 and rowSEG['RuheZeitenAlAnz']==0:
                logger.info("{:s}: FörderZeitenAlAnz=0 und RuheZeitenAlAnz=0".format(strSEG))     
                continue             
                
            # Segmente mit Alarmen ...

            # Alarmnummern
            AlNrn=sorted(rowSEG['FörderZeitenAlNrn']+rowSEG['RuheZeitenAlNrn'])
            #logger.info("{:s}: AlNrn: {!s:s}".format(strSEG, AlNrn))   


            # über alle Alarme des SEGs
            for idxAlarm,AlNr in enumerate(AlNrn):

                # der Alarm
                s=dfAlarmEreignisse[dfAlarmEreignisse['Nr']==AlNr].iloc[0]     

                titleStr="{:s}: AlNrn: {!s:s}: AlNr.: {:d} ({:s}: {:s})".format(strSEG, AlNrn, AlNr,s.LDSResBaseType,s.resIDBase)   

                if plotOnlyAlNrn != None:
                    if AlNr not in plotOnlyAlNrn:
                        logger.info("{:s}: nicht in plotOnlyAlNrn ...".format(titleStr))  
                        continue
                
                logger.info(titleStr)   

                # sein Ergebnisvektor
                resIDBase=s.resIDBase
                dfResVec=s.dfResVec

                # FIG
                fig=plt.figure(figsize=figsize,dpi=dpi)     


                # SEG- oder Druck-Alarm
                if s.LDSResBaseType=='SEG':                    
                    dfSegReprVec=dfResVec
                    dfDruckReprVec=pd.DataFrame()                    
                else:                    
                    dfSegReprVec=pd.DataFrame()
                    dfDruckReprVec=dfResVec

               
                timeStart, timeEnd, byminute, bysecond = fGenAlarmVisTimeSpan(s.tA,s.tE
                                                                           ,timeSpan=pd.Timedelta('25 Minutes')
                                                                           ,timeRoundStr='1T'
                                                                           ,timeBoundaryMin=pd.Timedelta('1 Minutes')
                                                                          )    
                xlims=[(timeStart, timeEnd)]
                byminute=byminute
                bysecond=bysecond
                vAreasX=[[(s.tA,s.tE)]]


                  
                gsHYD,gsLDS,pltLDSpQAndEventsResults,pltLDSErgVecResults=Rm.plotTimespans(     
                             xlims=xlims

                            ,sectionTitles=["{:s}".format(s.DIVPipelineName)]
                            ,sectionTitlesLDS=["tA={!s:s}".format(s.tA)]
                                                   
                            ,byminute=byminute
                            ,bysecond=bysecond
                            ,orientation='portrait'

                            ,vAreasX=vAreasX        
                            ,vLinesXLDS=[]
                            ,vAreasXLDS=[]   
                         
                            # --- Args Fct. ---:
                            ,TCsLDSIn=TCsLDSIn
                
                            ,TCsOPC=TCsOPC
                            ,TCsOPCScenTimeShift=pd.Timedelta('0 seconds') 

                            ,TCsSIDEvents=TCsSIDEvents.filter(items=IDSetsDctAlNr[s.Nr]['I'] if s.Nr in IDSetsDctAlNr.keys() else [])  
                            ,TCsSIDEventsTimeShift=pd.Timedelta('0 seconds') 
        
                            ,QDct=QDct[s.Nr]
                            ,pDct=pDct[s.Nr]
                            ,QDctOPC=QDctOPC[s.Nr] if s.Nr in QDctOPC.keys() else {}
                            ,pDctOPC=pDctOPC[s.Nr] if s.Nr in pDctOPC.keys() else {} 
                            ,attrsDct=attrsDct  
                            
                            #,fctsDct=fctsDct

                           
                         #   ,ylimp=(0,70)  
                         #   ,ylimQ=(-50,300)   
                         #   ,yGridSteps=14  
                        

                            # --- Args Fct. ---:            
                           ,dfSegReprVec=dfSegReprVec
                           ,dfDruckReprVec=dfDruckReprVec
        
                       
                   
                
                )

                rptAlarmsResults[AlNr]=(gsHYD,gsLDS,pltLDSpQAndEventsResults,pltLDSErgVecResults)

                fig.suptitle("{:s}: {!s:s} {!s:s}: ZHKName: {:s}: ZHKNR: {!s:s}".format(titleStr,s.Type,s.Voralarm,Rm.fCVDName(s.Name),s.ZHKNR),y=0.99)

                fig.tight_layout()

                # png                   
                fileName="{:s} {:2d} - {:s} {:s} {:s}.png".format(fileNameBase
                                                             ,int(rowSEG.Nr)+1
                                                             ,str(rowSEG.DIVPipelineName)
                                                             ,rowSEG['SEGName']
                                                             ,s.Orte[0]#resIDBase
                                                             )           
           
                # 
            
                fileNameAlarm="{:s} Nr {:d}.png".format(fileName.replace('.png',''),AlNr)                                  
                plt.savefig(fileNameAlarm)  
               
                plt.show()

                # PDF - Seite
                pdf.savefig(fig)            
                plt.close()  
    
        # PDF - DokEnde
        pdf.close()       
                                                                                                                   
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise e                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return rptAlarmsResults

def plotDfAlarmEreignisseMitKat(    
     dfAlarmEreignisse=pd.DataFrame()    
    ,sortBy=[]
    ,replaceTup=('2021-','')
    ,replaceTuptD=('0 days','')
    ):
    """
    Returns the plt.table and the df behind it
    """

    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
    


    try:                     
     
        df=dfAlarmEreignisse[['Nr'
                             ,'LDSResBaseType','Voralarm'
                             ,'Type'
                             ,'NrSD','tA','tE','tD'
                             ,'Orte'
                             ,'NrSEGName','SEGName','BZKat'
                             ,'Kategorie','Unterkat.','Information','Einfl. Release']].copy()

        df['tA']=df['tA'].apply(lambda x: str(x).replace(replaceTup[0],replaceTup[1]))
        df['tE']=df['tE'].apply(lambda x: str(x).replace(replaceTup[0],replaceTup[1]))    
        df['tD']=df['tD'].apply(lambda x: str(x).replace(replaceTuptD[0],replaceTuptD[1]))        

        df['Orte']=df['Orte'].apply(lambda x: str(x[0]))
        
        df['LDSResBaseType']=df.apply(lambda row: "{:s} {:s} - {:d}".format(row['LDSResBaseType'],row['Type'],row['Voralarm']),axis=1)
        df=df[['Nr','LDSResBaseType','NrSD','tA','tE','tD','NrSEGName','SEGName','Orte','BZKat','Kategorie','Unterkat.','Information','Einfl. Release']]
        df.rename(columns={'LDSResBaseType':'ResTyp - Voralarm'},inplace=True)
       
        df['NrSEGName (SEGName)']=df.apply(lambda row: "{!s:2s} ({!s:s})".format(row['NrSEGName'],row['SEGName']),axis=1)

        df=df[['Nr','ResTyp - Voralarm','NrSD','tA','tD'
               ,'Orte' 
               ,'BZKat'
               ,'NrSEGName (SEGName)','Kategorie','Unterkat.','Information','Einfl. Release']]

        df.rename(columns={'Orte':'ID'},inplace=True)       


        if sortBy!=[]:
            df=df.sort_values(by=sortBy)
       

        t=plt.table(cellText=df.values, colLabels=df.columns
                  
                    ,colWidths=[.03,.1 # Nr ResTyp-Voralarm
                                ,.04 # NrSD
                                ,.08,.08 # tA tD
                              
                                ,.1125,.07 # ID BZKat
                                
                                ,.14  # NrSEGName (SEGName)
                                ,.05
                                ,.055
                                ,.14,.1025] # 

                    , cellLoc='left'
                    , loc='center')    

        t.auto_set_font_size(False)
        t.set_fontsize(10)
                
        cols=df.columns.to_list()       
        colIdxNrSD=cols.index('NrSD')
        colIdxNrSEG=cols.index('NrSEGName (SEGName)')
        colIdxResTypVA=cols.index('ResTyp - Voralarm')

        cells = t.properties()["celld"]
        for cellTup,cellObj in cells.items():
             cellObj.set_text_props(ha='left')


             row,col=cellTup # row: 0 fuer Ueberschrift bei Ueberschrift; col mit 0
    
            
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
                
           
       
            
    

        plt.axis('off')       
                                                                                                                   
    except Rm.RmError:
        raise            
    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal) 
        raise Rm.RmError(logStrFinal)                       
    finally:       
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
        return t,df
