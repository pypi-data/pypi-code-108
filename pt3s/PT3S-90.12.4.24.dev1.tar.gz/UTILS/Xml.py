import os
import shutil
import sys
import logging
logger = logging.getLogger('PT3S.UTILS')       
import argparse
import unittest
import doctest

import re

import csv

import xml.etree.ElementTree as ET
import copy

import collections

try:
    from PT3S.UTILS import Db
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S.UTILS import Db - trying from UTILS import Db instead ... maybe pip install -e . is active ...')) 
    from UTILS import Db

def XmlGetODIsHelperFct(XmlFileIn=r".\VSICS\AppOfflineTest_SirOPC.xml",checkOPC=False):
            """
            Kanalnamen aus Xml extrahieren und als Liste liefern
            """
            # Kanalnamen aus Xml extrahieren

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            IDs=[]
            IDsOPCCheck=[]

            try:                                    
                XmlFileInTree = ET.parse(XmlFileIn)
                XmlFileInRoot =  XmlFileInTree.getroot()   
                parent_map = {c:p for p in XmlFileInRoot.iter() for c in p}  

                # in dataItem ist die PV immer - im OfflineTest (nur IMDIs) und in der App SIM (OPCs XOR IMDIs)
                ElementTypeName='dataItem'
                ElementIdName='Name'                               
                for dataItem in XmlFileInRoot.iter(ElementTypeName):                                                           
                    ID=dataItem.find(ElementIdName).text
                    IDs.append(ID)                
                    ParentElement=parent_map[dataItem]
                    ParentElementTypeName=ParentElement.tag
                    PParentElement=parent_map[ParentElement]
                    PParentElementTypeName=PParentElement.tag    
                    # <Type>OPC UA</Type>
                    # <Type>InMemory Plugin</Type>
                    if PParentElement.find('Type').text=='OPC UA':
                        IDsOPCCheck.append(ID)      
                    #logger.debug("{0:s} {1:s}: {2:s}={3:s} Parent: {4:s} :PParent: {5:s} {6:s} {7:s}".format(logStr,ElementTypeName,ElementIdName,ID,ParentElementTypeName,PParentElementTypeName,PParentElement.find('Name').text,PParentElement.find('Type').text)) 

                if checkOPC:                                    
                    # die PV muss auch noch in OPCItem sein, wenn es sich um ein OPC und nicht um ein IMDI handelt ...
                    IDsOPC=[]
                    ElementTypeName='OPCItem'
                    ElementIdName='ItemPath'                               
                    for dataItem in XmlFileInRoot.iter(ElementTypeName):                                                           
                        ID=dataItem.find(ElementIdName).text
                        IDsOPC.append(ID)                    
                        ParentElement=parent_map[dataItem]
                        ParentElementTypeName=ParentElement.tag
                        PParentElement=parent_map[ParentElement]
                        PParentElementTypeName=PParentElement.tag    
                        #logger.debug("{0:s} {1:s}: {2:s}={3:s} Parent: {4:s} :PParent: {5:s} {6:s}".format(logStr,ElementTypeName,ElementIdName,ID,ParentElementTypeName,PParentElementTypeName,PParentElement.find('Name').text)) 

                    IDsOPCCheck_NotInOPC = set(IDsOPCCheck)-set(IDsOPC)
                    for ID in sorted(IDsOPCCheck_NotInOPC):                         
                        logger.debug("{0:s} {1:s}: als dataItem aber nicht als OPCItem?!: {2:s}".format(logStr,XmlFileIn,ID))

                    IDsOPC_NotInOPCCheck = set(IDsOPC)-set(IDsOPCCheck)
                    for ID in sorted(IDsOPC_NotInOPCCheck):                         
                        logger.debug("{0:s} {1:s} als OPCItem aber nicht als dataItem?!: {2:s}".format(logStr,XmlFileIn,ID))
                                                                       
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))           
                return IDs
           
def XmlExportODIsHelperFct(XmlFileIn="AppSIM_SirOPC_3SCACT.xml",CsvFileOut="AppSIM_SirOPC_3SCACT.csv",TabImport='AppSIM_SirOPC_3SCACT',conStr=None):
            # Xml fuer Analyse 1x extrahieren und wieder importieren        

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:                                    
                XmlFileInTree = ET.parse(XmlFileIn)
                XmlFileInRoot =  XmlFileInTree.getroot()     

                colNames=[]
                colNames.append('ID')
                dicts=[]

                IDs=XmlGetODIsHelperFct(XmlFileIn=XmlFileIn)

                for ID in IDs: 
                    dict={}                    
                    dict[colNames[0]]=ID
                    dicts.append(dict)
                    #logger.debug("{0:s}{1:s}{2:s}".format(logStr,'dataItem: ',ID)) 

                with open(CsvFileOut,'w') as f:
                    csv.register_dialect('exportToCsvFile','excel',delimiter=';',lineterminator='\n')
                    writer = csv.DictWriter(f,fieldnames=colNames,dialect='exportToCsvFile')
                    writer.writeheader()
                    writer.writerows(dicts)
                        
                obj = Db.Db(conStr) 
                obj.importCsvFileWithHeaderToTable(TabImport,CsvFileOut)
                obj.close()               
                                               
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                pass
           
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))       
            
# XML-konfigurierte DPs die nicht ODI-konfiguriert sind (oder umgekehrt)
# nachfolgend DP-Mengen die diesbezueglich (wenn sie XML- aber nicht ODI-konfiguriert sind (oder umgekehrt)) _keine Meldung ausgeben
# die Mengen sind nachfolgend alle auf "leer" gesetzt weil sie nicht gepflegt wurden (bzw. auch nicht gepflegt werden muessen)
set_XML_Not_ODI_AppOfflineTest_SirOPC_ok=set()          
set_XML_Not_ODI_AppSIM_SirOPC_3SCXXX_ok=set()
set_ODI_Not_Xml_AppSIM_SirOPC_3SCXXX_ok=set()

def f_XML_Not_ODI_AppSIM_SirOPC_3SCXXX_ok_relevant(channel):    
    if (
                        (re.search(re.compile('\.AL_S$'),channel) == None)
                        and
                        (re.search(re.compile('\.AM_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.LD_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.LP_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.LR_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.NG_AV$'),channel) == None)                     
                        and
                        (re.search(re.compile('\.SB_S$'),channel) == None)
                        and
                        (re.search(re.compile('\.STAT_S$'),channel) == None)
                        and
                        (re.search(re.compile('\.ZHKNR_S$'),channel) == None)
                        and
                        (re.search(re.compile('\.MZ_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.QD_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.SD_AV$'),channel) == None)
                        and
                        (re.search(re.compile('\.In\.STOER$'),channel) == None)
                        and
                        (re.search(re.compile('\.MSTOER$'),channel) == None)
                        and
                        (re.search(re.compile('_TT_'),channel) == None)
                        and
                        (re.search(re.compile('_DTI_'),channel) == None)
                        ):
                        
        return True                 
    else:
        return False

def XmlEditODIsHelperFctPre(XmlFile=r".\VSICS\AppOfflineTest_SirOPC.xml"
                            ,MdbFile=r"C:\3S\Modelle\FBG.mdb"
                            ,ViewOdi=r"V_AppLDS_ODI"
                            ,set_XML_Not_ODI_ok=set([])
                            ,set_ODI_Not_Xml_ok=set([])
                            ,f_XML_Not_ODI_ok_relevant=lambda x: True # f_XML_Not_ODI_AppSIM_SirOPC_3SCMUC_ok_relevant
                            ):
    """Test ob alle IDs in _ODI.csv auch in _SirOPC.xml konfiguriert sind. Und umgekehrt.    
    ggf. Korrektur        
    .
    """
            
    logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

    # ODI -----------------------------------------------------------------------
    logger.debug("ODI-IDs lesen ...") 
    
    obj = Db.Db(Db.getMdbConStr(MdbFile))                                                           
    rows,colNames,colTypes,colSizes,dicts = obj.selectSmart(ViewOdi)                    
    IDs_ODI = [[row[i] for row in rows] for i in [7]]  
    IDs_ODI = IDs_ODI[0]                      
    Channels_ODI=[]
    for dict in dicts:
        channel=dict['ID']+'~'+dict['TYPE']+'~'+dict['OBJTYPE']+'~'+dict['NAME1']+'~'+dict['NAME2']+'~'+dict['ATTRIBUTE']+'~'+dict['UC']+'~'+dict['ETYPE']+'~'+dict['EVALUE']+'~'+dict['ETIME']+'~'+dict['REF_ID']
        Channels_ODI.append(channel)            
    obj.close()
    for channel in sorted(Channels_ODI):
        pass
        #logger.debug("{0:s}{1:s}{2:s}".format(logStr,'Channels_ODI: ',channel))                                                         
    logger.debug("ODI-IDs pruefen ...")  
    #logger.debug("{0:s} Laenge von IDs_ODI {1:d}".format(logStr,len(IDs_ODI))) 
    IDsMehrfach =[(ID, count) for ID, count in collections.Counter(IDs_ODI).items() if count > 1]
    IDsMehrfachDct={}
    for ID, count in IDsMehrfach:
        IDsMehrfachDct[ID]=count               
    for ID in sorted(IDsMehrfachDct.keys()):
        count=IDsMehrfachDct[ID]
        #logger.debug("{0:s} dataItem {1:s} nehrfach in ODI: {2:d}x".format(logStr,ID,count)) 
    logger.debug("{0:s} {1:s}: Anzahl von ODI-Zeilen: {2:d}".format(logStr,ViewOdi,len(IDs_ODI))) 
    IDs_ODI=list(set(IDs_ODI))
    logger.debug("{0:s} {1:s}: Anzahl von verschiedenen ODI-IDs: {2:d}".format(logStr,ViewOdi,len(IDs_ODI))) 
            
    ODI_keine_leeren_IDs=True # Ok           
    for idx,ID in enumerate(IDs_ODI):
        if ID=='':
            ODI_keine_leeren_IDs=False
            logger.error("{0:s} dataItem {1:d} leer".format(logStr,idx))      
    if not ODI_keine_leeren_IDs:                                                       
        IDs_ODI=list(filter(lambda ID: ID != '',IDs_ODI))

    # Xml ---
    logger.debug("Xml-IDs lesen ...")
    IDs_Xml = XmlGetODIsHelperFct(XmlFileIn=XmlFile,checkOPC=True)          
      
    IDsMehrfach =[(ID, count) for ID, count in collections.Counter(IDs_Xml).items() if count > 1]
    IDsMehrfachDct={}
    for ID, count in IDsMehrfach:
        IDsMehrfachDct[ID]=count               
    for ID in sorted(IDsMehrfachDct.keys()):
        count=IDsMehrfachDct[ID]
        logger.debug("{0:s} {1:s} dataItem {2:s} mehrfach in Xml: {3:d}x".format(logStr,XmlFile,ID,count)) 

    logger.debug("{0:s} {1:s} Anzahl von Xml-IDs: {2:d}".format(logStr,XmlFile,len(IDs_Xml)))     
    logger.debug("{0:s} {1:s} Anzahl von verschiedenen Xml-IDs: {2:d}".format(logStr,XmlFile,len(list(set(IDs_Xml))))) 

    # sets --------------------------

    set_ODI=set(IDs_ODI)                
    set_XML=set(IDs_Xml) 

    set_ODI_Not_XML = set_ODI - set_XML
    set_XML_Not_ODI = set_XML - set_ODI

    # Ausgaben ------------------------------------------------------

    # Unstimmigkeiten bei der Definition der Menge set_ODI_Not_Xml_ok
    for channel in sorted(set_ODI_Not_Xml_ok-set_ODI):     # 2       
            logger.debug("{0:s} ODI_Not_Xml - aber gar nicht in ODI?!: dataItem {1:s}".format(logStr,channel))    
    for channel in sorted(set_ODI_Not_Xml_ok.intersection(set_ODI.intersection(set_XML))):            # 3
            logger.debug("{0:s} ODI_Not_Xml - aber in Xml?!: dataItem {1:s}".format(logStr,channel))    
              
    ODI_Not_XML=True # Ok                 
    for channel in sorted(set_ODI_Not_XML-set_ODI_Not_Xml_ok):
            ODI_Not_XML=False
            logger.debug("{0:s} ODI_Not_XML dataItem {1:s} (unter Ber. von set_ODI_Not_Xml_ok)".format(logStr,channel))           
            
    # Unstimmigkeiten bei der Definition der Menge set_XML_Not_ODI
    for channel in sorted(set_XML_Not_ODI-set_XML):     # 2       
            logger.debug("{0:s} XML_Not_ODI - aber gar nicht in Xml?!: dataItem {1:s}".format(logStr,channel))    
    for channel in sorted(set_XML_Not_ODI_ok.intersection(set_ODI.intersection(set_XML))):            # 3
            # jetzt als Debug gekennzeichnet weil es so viele davon gibt 
            logger.debug("{0:s} XML_Not_ODI_ - aber in ODI?!: dataItem {1:s}".format(logStr,channel))                
                          
    XML_Not_ODI=True # Ok    
    sXML =set_XML_Not_ODI-set_XML_Not_ODI_ok
    sXML= filter(f_XML_Not_ODI_ok_relevant,list(sXML))           
    for channel in sorted(sXML):    
            XML_Not_ODI=False    
            logger.debug("{0:s} XML_Not_ODI dataItem {1:s} (unter Ber. von set_XML_Not_ODI_ok)".format(logStr,channel))                   
    
    # Korrektur Xml vs. ODI                              
    XmlEditODIsHelperFct(XmlFileIn=XmlFile,set_ODI_Not_XML=set_ODI_Not_XML-set_ODI_Not_Xml_ok,set_XML_Not_ODI=set(sXML))    
                                                                                                                                      
    logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         

def XmlEditODIsHelperFct(XmlFileIn=r".\VSICS\AppOfflineTest_SirOPC.xml",set_ODI_Not_XML=set(),set_XML_Not_ODI=set()):
            """
            set_ODI_Not_XML: Kanaele erzeugen (als dataItem)
            set_XML_Not_ODI: Kanaele loeschen
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

           

            try:                  
                XmlFileInTree = ET.parse(XmlFileIn)
                XmlFileInRoot =  XmlFileInTree.getroot()   
                parent_map = {c:p for p in XmlFileInRoot.iter() for c in p}  
                
                IDElements = [Element for Element in XmlFileInRoot.iter() if Element.tag in ['dataItem']]                   
                IDElementIDs={} # Key: ID Value: (Element,ParentElement)                 
                for Element in IDElements:   
                    SubElement=Element.find('Name')
                    if SubElement != None:
                        IDElementIDs[SubElement.text]=(Element,parent_map[Element])    
                        #logger.debug("{0:s}Element: {1:s} {2:s}".format(logStr,Element.tag,SubElement.text))                          
                                
                # ParentElements
                ParentElements = [ParentElement for Element,ParentElement in IDElementIDs.values()]
                ParentElements=list(set(ParentElements))
                for ParentElement in ParentElements:                   
                    logger.debug("{0:s}ParentElementTag: {1:s}".format(logStr,ParentElement.tag))    

                IDsToRemove=set_XML_Not_ODI & set(IDElementIDs.keys())   
                IDsToRemove=sorted(list(IDsToRemove))

                logger.debug("{0:s}REMOVE: ElementToRemove: {1:d}".format(logStr,len(IDsToRemove)))      
                for ID in IDsToRemove:   
                    (Element,ParentElement)=IDElementIDs[ID]                   
                    ParentParentElement=parent_map[ParentElement]                                                  
                    logger.debug("{0:s}REMOVE: ElementToRemove: {1:s} For ID: {2:s} ParentElement: {3:s} ParentParentElement: {4:s}".format(logStr,Element.tag,ID,ParentElement.tag,ParentParentElement.tag))      
                    ParentElement.remove(Element)     

                IDsToAdd=sorted(list(set_ODI_Not_XML))
                #?! Where to Add
                ParentElement=ParentElements[0]

                logger.debug("{0:s}ADD: ElementToAdd: {1:d}".format(logStr,len(IDsToAdd)))      
                for IDToAdd in  IDsToAdd:                   
                    dataItem=ET.Element('dataItem')
                    Name=ET.SubElement(dataItem,'Name')
                    Name.text=IDToAdd
                    Description=ET.SubElement(dataItem,'Description')
                    Classification=ET.SubElement(dataItem,'Classification')
                    Classification.text='V79'
                    AccessRigths=ET.SubElement(dataItem,'AccessRigths')
                    AccessRigths.text='ReadWrite'
                    logger.debug("{0:s}ADD: {1:s}".format(logStr,str(ET.tostring(dataItem))))     
                    ParentElement.append(dataItem)  
                
                # Korrekturen abspeichern
                XmlFileInTree.write(XmlFileIn)                                                                                                                                                       
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))                                     

def XmlGenLDSParamStdHelperFct():
            """
            returns LDSIElem mit Standardwerten
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
           
            try:                     
                
                LDSIElem= ET.Element('LDSI')   
                

                LDSIElem.set('DESIGNFLOW','250')    
                LDSIElem.set('L_PERCENT_STDY','1.6')    
                LDSIElem.set('L_PERCENT_STRAN','1.6')    
                LDSIElem.set('L_PERCENT_TRANS','1.6')    

                LDSIElem.set('L_TRANSIENT','10')    
                LDSIElem.set('L_TRANSIENTQP','10')  # NEU V61   
                LDSIElem.set('L_SLOWTRANSIENT','4')
                LDSIElem.set('L_SLOWTRANSIENTQP','4')  # NEU V61
                LDSIElem.set('L_STANDSTILL','2')
                LDSIElem.set('L_STANDSTILLQP','2') # NEU V61 

                LDSIElem.set('L_SHUTOFF','2')
                LDSIElem.set('ACC_SLOWTRANSIENT','0.10')                    
                LDSIElem.set('ACC_TRANSIENT','0.80')
                LDSIElem.set('TIMER','180')
                LDSIElem.set('TIMERTOLISS','180') 
                LDSIElem.set('TIMERTOLIST','180') 
                LDSIElem.set('FILTERWINDOW','180')
                
                #LDSIElem.set('TTIMERTOALARM','45')
                LDSIElem.set('L_TRANSIENTVBIGF','3')
                LDSIElem.set('L_TRANSIENTPDNTF','1.5')
                
                LDSIElem.set('DT','1')
                LDSIElem.set('MEAN','1')      

            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
                return LDSIElem

def XmlSetLDSParamIndHelperFct(LDSIElem=None,LDSParamInd={}):
            """
            returns LDSIElem mit individuellen Werten wo angefordert
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                      
            try:                                     
                NAME = LDSIElem.get('NAME')
                if NAME in LDSParamInd.keys():
                    attribDct = LDSParamInd[NAME]
                    for attrib in attribDct.keys():
                        attribValue = attribDct[attrib]
                        LDSIElem.set(attrib,attribValue)   
                        logger.debug("{0:s}LDSI individuell fuer {1:s}: {2:s} {3:s}".format(logStr,NAME,attrib,str(attribValue)))                                                                                                                                                                                         
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
                return LDSIElem           
                        
def XmlGenLDSParaHelperFct(XmlFileOut=None,LDSParamInd={},DBFile=None):
            """
            LDS Para generieren
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
           
            try:                     
                # View mit Segmenten lesen
                
                obj = Db.Db(Db.getMdbConStr(DBFile)) # r"C:\3S\Modelle\FBG.mdb"     
                rows,colNames,colTypes,colSizes,dicts = obj.selectSmart('V_AppLDS_IPLS_SEGM_RICHT') #V_SIR3S_DP_ODI_LDS_IPLS_SEGM # jetzt sollten es 66 Segmente sein              

                obj.close()                  
                
                KIs = [[row[i] for row in rows] for i in [3]]
                KKs = [[row[i] for row in rows] for i in [4]]
                KIs = KIs[0]
                KKs = KKs[0]

                NAMES=[]
                for KI,KK in zip(KIs,KKs):
                    NAMES.append(KI+'~'+KK)

                # Parametrierung generieren
                ConfigurationElem=ET.Element('Configuration')
                for NAME in sorted(NAMES):                   
                    # Std ohne NAME
                    LDSIElem=XmlGenLDSParamStdHelperFct()
                    # mit NAME
                    LDSIElem.set('NAME',NAME)   
                    # ggf. individualisieren                   
                    LDSIElem=XmlSetLDSParamIndHelperFct(LDSIElem,LDSParamInd)
                    # abspeichern
                    ConfigurationElem.append(LDSIElem)                                                                                         
                    logger.debug("{0:s}LDSI generiert: {1:s}".format(logStr,str(ET.tostring(LDSIElem))))    

                # Parametrierung schreiben                        
                XmlFileETObj=ET.ElementTree(element=ConfigurationElem)                
                XmlFileETObj.write(XmlFileOut)                    
                                                                                                                                                                                      
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

def XmlLDSParaStripHelperFct(XmlFile=None):
            """
            LDS Para generieren
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
           
            try:                             
                # lesen           
                strippedLines=[]     
                XmlSrcFileTree = ET.parse(XmlFile)
                XmlSrcFileRoot =  XmlSrcFileTree.getroot()     
                for LdsiElem in XmlSrcFileRoot.iter('LDSI'):
                    LdsiElemString=ET.tostring(LdsiElem,encoding="unicode")
                    logger.debug("{0:s}LDSI: {1:s}".format(logStr,LdsiElemString)) 
                    strippedLines.append(LdsiElemString)

                # schreiben in dieselbe Datei
                with open(XmlFile,'w') as f:
                     f.writelines(strippedLines)
                f.close()
                               
                                                                                                                                                                    
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   

def XmlLDSInitValueHelperFct(CSVFile=None):
            """
            LDS InitValues generieren/updaten
            """            

            logStr = "{0:s}: ".format(sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
           
            try:       
                data = dict()
                with open(CSVFile, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for row in read :
                        data[row[0]] = row[1]
                f.close()
                               
                                                                                                                                                                    
            except SystemExit:
                logger.error('{0:s}SytemExit Exeption.'.format(logStr))
            except:
                logging.exception('') 
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))   