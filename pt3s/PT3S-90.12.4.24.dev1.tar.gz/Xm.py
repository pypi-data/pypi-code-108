"""
>>> # ---
>>> # Imports
>>> # ---
>>> import os
>>> import logging
>>> logger = logging.getLogger('PT3S.Xm')  
>>> # ---
>>> # path
>>> # ---
>>> if __name__ == "__main__":
...   try:
...      dummy=__file__
...      logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ','path = os.path.dirname(__file__)'," .")) 
...      path = os.path.dirname(__file__)
...   except NameError:    
...      logger.debug("{0:s}{1:s}{2:s}".format('DOCTEST: __main__ Context: ',"path = '.' because __file__ not defined: ","from Xm import Xm follows ...")) 
...      path = '.'
...      from Xm import Xm
... else:
...    logger.debug("{0:s}{1:s}{2:s}{3:s}".format('DOCTEST: Not __main__ Context: ','__name__: ',__name__,"path = '.'")) 
...    path = '.'
>>> try:
...    from PT3S import Mx
... except ImportError:
...    logger.debug("{0:s}{1:s}".format("DOCTEST: ImportError: from PT3S import Mx: ","- trying import Mx instead ... maybe pip install -e . is active ..."))  
...    import Mx
>>> # ---
>>> # testDir
>>> # ---
>>> # globs={'testDir':'testdata'}
>>> try:
...    dummy= testDir
... except NameError:
...    testDir='testdata' 
>>> import pandas as pd
>>> # ---
>>> # Clean Up
>>> # ---
>>> h5File=os.path.join(os.path.join(path,testDir),'OneLPipe.h5')
>>> if os.path.exists(h5File):                        
...    os.remove(h5File)
>>> # ---
>>> # Init
>>> # ---
>>> xmlFile=os.path.join(os.path.join(path,testDir),'OneLPipe.XML')
>>> xm=Xm(xmlFile=xmlFile)
>>> # ---
>>> # a View
>>> # ---
>>> v='vKNOT'
>>> v in xm.dataFrames
True
>>> isinstance(xm.dataFrames[v],pd.core.frame.DataFrame)
True
>>> # ---
>>> # ToH5
>>> # ---
>>> xm.ToH5()
>>> os.path.exists(xm.h5File) 
True
>>> # ---
>>> # force Read H5 instead of Xml
>>> # ---
>>> os.rename(xm.xmlFile,xm.xmlFile+'.blind')
>>> xm=Xm(xmlFile=xmlFile)
>>> os.rename(xm.xmlFile+'.blind',xm.xmlFile)
>>> # ---
>>> vKNOT=xm.dataFrames['vKNOT']
>>> vStr=xm.getVersion(type='BZ')
>>> import re
>>> m=re.search('Sir(?P<Db3s>[DBdb3Ss]{2})-(?P<Major>\d+)-(?P<Minor>\d+)$',vStr) # i.e. Sir3S-90-10
>>> minorVer=int(m.group('Minor'))
>>> # minorVer
>>> if minorVer>=12:
...    shapeSet=(2,40)
... else:
...    shapeSet=(2,40)
>>> shapeSet == vKNOT[(vKNOT.KTYP.isin(['QKON','PKON'])) & (vKNOT.BESCHREIBUNG.fillna('').str.startswith('Template Element')==False)].shape
True
>>> vROHR=xm.dataFrames['vROHR']
>>> vROHR.shape
(1, 74)
>>> isinstance(vROHR['pXCors'],pd.core.series.Series)
True
>>> vROHR['pXCors'][0]
[0.0, 500.0]
>>> vROHR.pYCors[0]
[0.0, 0.0]
>>> # ---
>>> # getWDirModelDirModelName()
>>> # ---
>>> (wDir,modelDir,modelName,mx1File)=xm.getWDirModelDirModelName()
>>> modelName
'M-1-0-1'
>>> # ---
>>> # H5-Deletion if NoH5Read=True
>>> # ---
>>> if os.path.exists(xm.h5File):                        
...    os.remove(xm.h5File)
>>> xm=Xm(xmlFile=xmlFile)
>>> xm.ToH5()
>>> os.path.exists(xm.h5File)
True
>>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)
>>> os.path.exists(xm.h5File)
False
>>> # ---
>>> # print-Options
>>> # ---
>>> pd.set_option('display.max_columns',None)
>>> pd.set_option('display.max_rows',None)
>>> pd.set_option('display.max_colwidth',666666)   
>>> pd.set_option('display.width',666666666)
>>> # ---
>>> # vKNOT
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vKNOT',dropColList=['LFKT_NAME','LF','LF_min','LF_max','PVAR_NAME','PH','PH_min','PH_max','PZON_NAME','FSTF_NAME','STOF_NAME','GMIX_NAME','UTMP_NAME','2L_NAME','2L_KVR','fkHYDR','fkFQPS']))
  NAME BESCHREIBUNG             IDREFERENZ      CONT CONT_ID CONT_LFDNR CONT_VKNO  KTYP LFAKT    QM_EIN QVAR_NAME  QM  QM_min  QM_max KVR   TE  TM XKOR YKOR ZKOR                   pk                   tk  pXCor  pYCor
0    I          NaN  3S5642914844465475844  OneLPipe    1001        NaN       NaN  QKON     1  176.7146       NaN NaN     NaN     NaN   0  NaN  10  300  600   10  5642914844465475844  5642914844465475844    0.0    0.0
1    K          NaN  3S5289899964753656852  OneLPipe    1001        NaN       NaN  PKON     1         0       NaN NaN     NaN     NaN   0  NaN  10  800  600   10  5289899964753656852  5289899964753656852  500.0    0.0
>>> # ---
>>> # vROHR
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vROHR',dropColList=['NAME_i_2L','NAME_k_2L']))
  BESCHREIBUNG             IDREFERENZ BAUJAHR HAL IPLANUNG KENNUNG      L LZU   RAU ZAUS ZEIN ZUML JLAMBS LAMBDA0 ASOLL INDSCHALL KVR AUSFALLZEIT DA   DI   DN KT PN REHABILITATION REPARATUR  S WSTEIG WTIEFE LTGR_NAME LTGR_BESCHREIBUNG SICHTBARKEIT VERLEGEART DTRO_NAME                           DTRO_BESCHREIBUNG        E fkSTRASSE fkSRAT                   pk                   tk IRTRENN LECKSTART LECKEND LECKMENGE LECKORT LECKSTATUS QSVB ZVLIMPTNZ KANTENZV      CONT CONT_ID CONT_LFDNR NAME_i KVR_i TM_i XKOR_i YKOR_i ZKOR_i NAME_k KVR_k TM_k XKOR_k YKOR_k ZKOR_k  pXCor_i  pYCor_i  pXCor_k  pYCor_k        pXCors      pYCors    pWAYPXCors  pWAYPYCors                              WAYP
0          NaN  3S4737064599036143765    2017   0        1       0  10000   0  0.25    0    0    0      1   0.025  1000         0   0           0  0  250  250  0  0              0         0  0      0      0   STDROHR               NaN            1     999999   STDROHR  Standard-Druckrohre mit di = DN (DIN 2402)  2.1E+11        -1     -1  4737064599036143765  4737064599036143765       0         0       0         0       0          0    0         0        0  OneLPipe    1001        NaN      I     0   10    300    600     10      K     0   10    800    600     10      0.0      0.0    500.0      0.0  [0.0, 500.0]  [0.0, 0.0]  [0.0, 500.0]  [0.0, 0.0]  [(300.0, 600.0), (800.0, 600.0)]
>>> # ---
>>> # Clean Up
>>> # ---
>>> xm.delFiles()
>>> # ---
>>> # LocalHeatingNetwork
>>> # ---
>>> xmlFile=os.path.join(os.path.join(path,testDir),'LocalHeatingNetwork.XML')
>>> xm=Xm(xmlFile=xmlFile)
>>> # ---
>>> # vKNOT
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vKNOT',dropColList=['LFKT_NAME','LF','LF_min','LF_max','PVAR_NAME','PH','PH_min','PH_max','PZON_NAME','FSTF_NAME','STOF_NAME','GMIX_NAME','UTMP_NAME','2L_NAME','2L_KVR','fkHYDR','fkFQPS']))
           NAME                    BESCHREIBUNG IDREFERENZ                                      CONT CONT_ID CONT_LFDNR CONT_VKNO  KTYP LFAKT QM_EIN QVAR_NAME  QM  QM_min  QM_max KVR  TE  TM     XKOR     YKOR ZKOR                   pk                   tk   pXCor  pYCor
0        R-K004                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541539  5706361   20  4638663808856251977  4638663808856251977   799.0  152.0
1        V-K002                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541059  5706265   20  4731792362611615619  4731792362611615619   319.0   56.0
2        V-K001                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2540867  5706228   20  4756962427318766791  4756962427318766791   127.0   19.0
3        V-K000                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2540793  5706209   20  4766681917240867943  4766681917240867943    53.0    0.0
4        R-K001                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2540867  5706228   20  4807712987325933680  4807712987325933680   127.0   19.0
5        R-K003                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541457  5706345   20  4891048046264179170  4891048046264179170   717.0  136.0
6        R-K000                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2540793  5706209   20  4979785838440534851  4979785838440534851    53.0    0.0
7        R-K005                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541627  5706363   20  5183147862966701025  5183147862966701025   887.0  154.0
8           R-L                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1      BHKW  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2540740  5706225   20  5356267303828212700  5356267303828212700     0.0   16.0
9        R-K002                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541059  5706265   20  5364712333175450942  5364712333175450942   319.0   56.0
10       V-K004                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541539  5706361   20  5370423799772591808  5370423799772591808   799.0  152.0
11       V-K005                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541627  5706363   20  5444644492819213978  5444644492819213978   887.0  154.0
12       R-K007                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541899  5706325   20  5508992300317633799  5508992300317633799  1159.0  116.0
13       V-K006                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541790  5706338   20  5515313800585145571  5515313800585145571  1050.0  129.0
14       R-K006                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541790  5706338   20  5543326527366090679  5543326527366090679  1050.0  129.0
15       V-K003                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541457  5706345   20  5646671866542823796  5646671866542823796   717.0  136.0
16          V-L                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1      BHKW  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2540740  5706240   20  5736262931552588702  5736262931552588702     0.0   31.0
17       V-K007                            None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90  2541899  5706325   20  5741235692335544560  5741235692335544560  1159.0  116.0
18           R2                            None         -1                                      BHKW    1002         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60      170       20   20  5002109894154139899  5002109894154139899   170.0   20.0
19          V-1                            None         -1                                      BHKW    1002         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   1  10  90      140      160   20  5049461676240771430  5049461676240771430   140.0  160.0
20           R3                            None         -1                                      BHKW    1002         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60      140       20   20  5219230031772497417  5219230031772497417   140.0   20.0
21  PKON-Knoten  Druckhaltung - 2 bar Ruhedruck         -1                                      BHKW    1002         -1       NaN  PKON     1      0       NaN NaN     NaN     NaN   2  60  60      200       40   20  5397990465339071638  5397990465339071638   200.0   40.0
22          R-1          Anbindung Druckhaltung         -1                                      BHKW    1002         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60      195       20   20  5557222628687032084  5557222628687032084   195.0   20.0
>>> # ---
>>> # vROHR
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vROHR',dropColList=['NAME_i_2L','NAME_k_2L']))
   BESCHREIBUNG IDREFERENZ BAUJAHR HAL IPLANUNG KENNUNG       L LZU  RAU ZAUS ZEIN ZUML JLAMBS LAMBDA0 ASOLL INDSCHALL KVR AUSFALLZEIT     DA     DI   DN     KT   PN REHABILITATION REPARATUR    S WSTEIG WTIEFE LTGR_NAME            LTGR_BESCHREIBUNG SICHTBARKEIT VERLEGEART DTRO_NAME                        DTRO_BESCHREIBUNG        E fkSTRASSE fkSRAT                   pk                   tk IRTRENN LECKSTART LECKEND LECKMENGE LECKORT LECKSTATUS QSVB ZVLIMPTNZ KANTENZV                                      CONT CONT_ID CONT_LFDNR  NAME_i KVR_i TM_i   XKOR_i   YKOR_i ZKOR_i  NAME_k KVR_k TM_k   XKOR_k   YKOR_k ZKOR_k  pXCor_i  pYCor_i  pXCor_k  pYCor_k            pXCors          pYCors                                pWAYPXCors                                pWAYPYCors                                                                                               WAYP
0          None         -1    None   0        1       0   88.02   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4613782368750024999  4613782368750024999       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K004     2   60  2541539  5706361     20  R-K005     2   60  2541627  5706363     20    799.0    152.0    887.0    154.0    [799.0, 887.0]  [152.0, 154.0]    [807.8999999999069, 895.9500000001863]  [140.09999999962747, 142.04999999981374]                                                 [(2541547.9, 5706349.1), (2541635.95, 5706351.05)]
1          None         -1    None   0        1       0  405.96   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4614949065966596185  4614949065966596185       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K002     1   90  2541059  5706265     20  V-K003     1   90  2541457  5706345     20    319.0     56.0    717.0    136.0    [319.0, 717.0]   [56.0, 136.0]                [319.0, 716.9500000001863]               [56.049999999813735, 136.0]                                                 [(2541059.0, 5706265.05), (2541456.95, 5706345.0)]
2          None         -1    None   0        1       0   83.55   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4637102239750163477  4637102239750163477       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K003     2   60  2541457  5706345     20  R-K004     2   60  2541539  5706361     20    717.0    136.0    799.0    152.0    [717.0, 799.0]  [136.0, 152.0]    [725.8500000000931, 807.8999999999069]  [124.04999999981374, 140.09999999962747]                                                 [(2541465.85, 5706333.05), (2541547.9, 5706349.1)]
3          None         -1    None   0        1       0   88.02   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4713733238627697042  4713733238627697042       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K004     1   90  2541539  5706361     20  V-K005     1   90  2541627  5706363     20    799.0    152.0    887.0    154.0    [799.0, 887.0]  [152.0, 154.0]                [799.0, 887.0499999998137]                            [152.0, 154.0]                                                  [(2541539.0, 5706361.0), (2541627.05, 5706363.0)]
4          None         -1    None   0        1       0  195.53   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4789218195240364437  4789218195240364437       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K001     1   90  2540867  5706228     20  V-K002     1   90  2541059  5706265     20    127.0     19.0    319.0     56.0    [127.0, 319.0]    [19.0, 56.0]                            [127.0, 319.0]                [19.0, 56.049999999813735]                                                  [(2540867.0, 5706228.0), (2541059.0, 5706265.05)]
5          None         -1    None   0        1       0  109.77   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4945727430885351042  4945727430885351042       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K006     2   60  2541790  5706338     20  R-K007     2   60  2541899  5706325     20   1050.0    129.0   1159.0    116.0  [1050.0, 1159.0]  [129.0, 116.0]  [1058.8500000000931, 1167.8999999999069]               [117.0, 104.09999999962747]                                                  [(2541798.85, 5706326.0), (2541907.9, 5706313.1)]
6          None         -1    None   0        1       0    76.4   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4984202422877610920  4984202422877610920       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K000     1   90  2540793  5706209     20  V-K001     1   90  2540867  5706228     20     53.0      0.0    127.0     19.0     [53.0, 127.0]     [0.0, 19.0]               [53.049999999813735, 127.0]             [-0.049999999813735485, 19.0]                                                 [(2540793.05, 5706208.95), (2540867.0, 5706228.0)]
7          None         -1    None   0        1       0   83.55   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5037777106796980248  5037777106796980248       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K003     1   90  2541457  5706345     20  V-K004     1   90  2541539  5706361     20    717.0    136.0    799.0    152.0    [717.0, 799.0]  [136.0, 152.0]                [716.9500000001863, 799.0]                            [136.0, 152.0]                                                  [(2541456.95, 5706345.0), (2541539.0, 5706361.0)]
8          None         -1    None   0        1       0  164.91   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5123819811204259837  5123819811204259837       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K005     1   90  2541627  5706363     20  V-K006     1   90  2541790  5706338     20    887.0    154.0   1050.0    129.0   [887.0, 1050.0]  [154.0, 129.0]   [887.0499999998137, 1049.9500000001863]               [154.0, 128.95000000018626]                                                [(2541627.05, 5706363.0), (2541789.95, 5706337.95)]
9          None         -1    None   0        1       0  195.53   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5266224553324203132  5266224553324203132       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K001     2   60  2540867  5706228     20  R-K002     2   60  2541059  5706265     20    127.0     19.0    319.0     56.0    [127.0, 319.0]    [19.0, 56.0]  [135.89999999990687, 327.89999999990687]   [7.0499999998137355, 44.09999999962747]                                                  [(2540875.9, 5706216.05), (2541067.9, 5706253.1)]
10         None         -1    None   0        1       0  405.96   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5379365049009065623  5379365049009065623       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K002     2   60  2541059  5706265     20  R-K003     2   60  2541457  5706345     20    319.0     56.0    717.0    136.0    [319.0, 717.0]   [56.0, 136.0]   [327.89999999990687, 725.8500000000931]   [44.09999999962747, 124.04999999981374]                                                 [(2541067.9, 5706253.1), (2541465.85, 5706333.05)]
11         None         -1    None   0        1       0  164.91   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5611703699850694889  5611703699850694889       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K005     2   60  2541627  5706363     20  R-K006     2   60  2541790  5706338     20    887.0    154.0   1050.0    129.0   [887.0, 1050.0]  [154.0, 129.0]   [895.9500000001863, 1058.8500000000931]               [142.04999999981374, 117.0]                                                [(2541635.95, 5706351.05), (2541798.85, 5706326.0)]
12         None         -1    None   0        1       0  109.77   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5620197984230756681  5620197984230756681       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K006     1   90  2541790  5706338     20  V-K007     1   90  2541899  5706325     20   1050.0    129.0   1159.0    116.0  [1050.0, 1159.0]  [129.0, 116.0]              [1049.9500000001863, 1159.0]  [128.95000000018626, 116.04999999981374]                                                [(2541789.95, 5706337.95), (2541899.0, 5706325.05)]
13         None         -1    None   0        1       0    76.4   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5647213228462830353  5647213228462830353       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K000     2   60  2540793  5706209     20  R-K001     2   60  2540867  5706228     20     53.0      0.0    127.0     19.0     [53.0, 127.0]     [0.0, 19.0]  [61.950000000186265, 135.89999999990687]               [-12.0, 7.0499999998137355]                                                 [(2540801.95, 5706197.0), (2540875.9, 5706216.05)]
14         None         -1    None   0        1       0   73.42   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  168.3  160.3  150   0.45  NaN            NaN       NaN    4    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4769996343148550485  4769996343148550485       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1     R-L     2   60  2540740  5706225     20  R-K000     2   60  2540793  5706209     20      0.0     16.0     53.0      0.0       [0.0, 53.0]     [16.0, 0.0]     [0.0, 24.0, 45.0, 61.950000000186265]                [16.0, 16.0, -12.0, -12.0]  [(2540740.0, 5706225.0), (2540764.0, 5706225.0), (2540785.0, 5706197.0), (2540801.95, 5706197.0)]
15         None         -1    None   0        1       0    68.6   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  168.3  160.3  150   0.45  NaN            NaN       NaN    4    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4939422678063487923  4939422678063487923       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1     V-L     1   90  2540740  5706240     20  V-K000     1   90  2540793  5706209     20      0.0     31.0     53.0      0.0       [0.0, 53.0]     [31.0, 0.0]           [0.0, 30.0, 53.049999999813735]       [31.0, 31.0, -0.049999999813735485]                         [(2540740.0, 5706240.0), (2540770.0, 5706240.0), (2540793.05, 5706208.95)]
>>> # ---
>>> # vWBLZ
>>> # ---
>>> print("'''{:s}'''".format(repr(xm.dataFrames['vWBLZ']).replace('\\n','\\n   ')))
'''   AKTIV BESCHREIBUNG IDIM       NAME OBJTYPE                OBJID                   pk
   0      1  Wärmebilanz    0      BLNZ1    KNOT  4731792362611615619  5579937562601803472
   1      1  Wärmebilanz    0      BLNZ1    KNOT  5364712333175450942  5579937562601803472
   2      1  Wärmebilanz    0    BLNZ1u5    KNOT  5183147862966701025  5187647097142898375
   3      1  Wärmebilanz    0    BLNZ1u5    KNOT  5444644492819213978  5187647097142898375
   4      1  Wärmebilanz    0    BLNZ1u5    KNOT  4731792362611615619  5187647097142898375
   5      1  Wärmebilanz    0    BLNZ1u5    KNOT  5364712333175450942  5187647097142898375
   6      1  Wärmebilanz    0  BLNZ1u5u7    KNOT  5183147862966701025  4694700216019268978
   7      1  Wärmebilanz    0  BLNZ1u5u7    KNOT  5444644492819213978  4694700216019268978
   8      1  Wärmebilanz    0  BLNZ1u5u7    KNOT  4731792362611615619  4694700216019268978
   9      1  Wärmebilanz    0  BLNZ1u5u7    KNOT  5364712333175450942  4694700216019268978
   10     1  Wärmebilanz    0  BLNZ1u5u7    KNOT  5508992300317633799  4694700216019268978
   11     1  Wärmebilanz    0  BLNZ1u5u7    KNOT  5741235692335544560  4694700216019268978
   12     1  Wärmebilanz    0      BLNZ5    KNOT  5183147862966701025  5581152085151655438
   13     1  Wärmebilanz    0      BLNZ5    KNOT  5444644492819213978  5581152085151655438'''
>>> # ---
>>> # vAGSN
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vAGSN',end=7,dropColList=['nrObjIdTypeInAgsn','compNr']))
  LFDNR                                      NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  Layer nextNODE
0     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  4939422678063487923  5252525269080005909  5252525269080005909              1      1   V-K000
1     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  4984202422877610920  5252525269080005909  5252525269080005909              2      1   V-K001
2     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  4789218195240364437  5252525269080005909  5252525269080005909              3      1   V-K002
3     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  4614949065966596185  5252525269080005909  5252525269080005909              4      1   V-K003
4     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  5037777106796980248  5252525269080005909  5252525269080005909              5      1   V-K004
5     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  4713733238627697042  5252525269080005909  5252525269080005909              6      1   V-K005
6     1  Netzdruckdiagramm VL/RL: BHKW - Netzende   101    ROHR  5123819811204259837  5252525269080005909  5252525269080005909              7      1   V-K006
>>> # ---
>>> # vFWVB
>>> # ---
>>> print("'''{:s}'''".format(repr(xm.dataFrames['vFWVB']).replace('\\n','\\n   ')))
'''  BESCHREIBUNG IDREFERENZ   W0  LFK  W0LFK  TVL0  TRS0  LFKT      W  W_min  W_max  INDTR  TRSK  VTYP  DPHAUS  IMBG  IRFV                   pk                   tk  NAME_i KVR_i TM_i   XKOR_i   YKOR_i ZKOR_i  pXCor_i  pYCor_i  NAME_k KVR_k TM_k   XKOR_k   YKOR_k ZKOR_k  pXCor_k  pYCor_k                                      CONT CONT_ID CONT_LFDNR                         WBLZ
   0            1         -1  200  0.8  160.0    90    50  LFKT  160.0  160.0  160.0      1    55    14     0.7     0   0.0  4643800032883366034  4643800032883366034  V-K002     1   90  2541059  5706265     20    319.0     56.0  R-K002     2   60  2541059  5706265     20    319.0     56.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  [BLNZ1, BLNZ1u5, BLNZ1u5u7]
   1            3         -1  200  1.0  200.0    90    65  LFKT  200.0  200.0  200.0      1    65    14     0.7     0   0.0  4704603947372595298  4704603947372595298  V-K004     1   90  2541539  5706361     20    799.0    152.0  R-K004     2   60  2541539  5706361     20    799.0    152.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                           []
   2            4         -1  200  0.8  160.0    90    60  LFKT  160.0  160.0  160.0      1    60    14     0.7     0   0.0  5121101823283893406  5121101823283893406  V-K005     1   90  2541627  5706363     20    887.0    154.0  R-K005     2   60  2541627  5706363     20    887.0    154.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  [BLNZ1u5, BLNZ1u5u7, BLNZ5]
   3            5         -1  200  0.8  160.0    90    55  LFKT  160.0  160.0  160.0      1    55    14     0.7     0   0.0  5400405917816384862  5400405917816384862  V-K007     1   90  2541899  5706325     20   1159.0    116.0  R-K007     2   60  2541899  5706325     20   1159.0    116.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                  [BLNZ1u5u7]
   4            2         -1  200  0.6  120.0    90    60  LFKT  120.0  120.0  120.0      1    62    14     0.7     0   0.0  5695730293103267172  5695730293103267172  V-K003     1   90  2541457  5706345     20    717.0    136.0  R-K003     2   60  2541457  5706345     20    717.0    136.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                           []'''
>>> # ---
>>> # vLAYR
>>> # ---
>>> # print("'''{:s}'''".format(repr(xm.dataFrames['vLAYR'].sort_values(['LFDNR','NAME','OBJTYPE','OBJID'],ascending=True)).replace('\\n','\\n   ')))

>>> vStr=xm.getVersion(type='BZ')
>>> import re
>>> m=re.search('Sir(?P<Db3s>[DBdb3Ss]{2})-(?P<Major>\d+)-(?P<Minor>\d+)$',vStr) # i.e. Sir3S-90-10
>>> minorVer=int(m.group('Minor'))
>>> vLAYR=xm.dataFrames['vLAYR']#.copy()
>>> #print(vLAYR.shape)
>>> if minorVer>=12:
...   vLAYR['OBJTYPE']=vLAYR['OBJTYPE'].map(lambda x: 'TEXT' if x=='GTXT' else x)
...   vLAYR['OBJTYPE']=vLAYR['OBJTYPE'].map(lambda x: 'BSYM' if x=='CONT' else x)
...   sortList=['LFDNR','NAME','OBJTYPE','OBJID']
... else:
...   sortList=None
>>> # Analyse der Unterschiede zu Testzwecken ...
>>> sGot=xm._getvXXXXAsOneString(vXXXX='vLAYR',sortList=sortList,index=False)
>>> sExp='''LFDNR           NAME OBJTYPE                OBJID                   pk                   tk  nrObjInGroup  nrObjtypeInGroup\
    1        Vorlauf    FWES  5638756766880678918  5206516471428693478  5206516471428693478             1                 1\
    1        Vorlauf    KNOT  4731792362611615619  5206516471428693478  5206516471428693478             1                 1\
    1        Vorlauf    KNOT  4756962427318766791  5206516471428693478  5206516471428693478             1                 2\
    1        Vorlauf    KNOT  4766681917240867943  5206516471428693478  5206516471428693478             1                 3\
    1        Vorlauf    KNOT  5049461676240771430  5206516471428693478  5206516471428693478             1                 4\
    1        Vorlauf    KNOT  5370423799772591808  5206516471428693478  5206516471428693478             1                 5\
    1        Vorlauf    KNOT  5444644492819213978  5206516471428693478  5206516471428693478             1                 6\
    1        Vorlauf    KNOT  5515313800585145571  5206516471428693478  5206516471428693478             1                 7\
    1        Vorlauf    KNOT  5646671866542823796  5206516471428693478  5206516471428693478             1                 8\
    1        Vorlauf    KNOT  5736262931552588702  5206516471428693478  5206516471428693478             1                 9\
    1        Vorlauf    KNOT  5741235692335544560  5206516471428693478  5206516471428693478             1                10\
    1        Vorlauf    ROHR  4614949065966596185  5206516471428693478  5206516471428693478             1                 1\
    1        Vorlauf    ROHR  4713733238627697042  5206516471428693478  5206516471428693478             1                 2\
    1        Vorlauf    ROHR  4789218195240364437  5206516471428693478  5206516471428693478             1                 3\
    1        Vorlauf    ROHR  4939422678063487923  5206516471428693478  5206516471428693478             1                 4\
    1        Vorlauf    ROHR  4984202422877610920  5206516471428693478  5206516471428693478             1                 5\
    1        Vorlauf    ROHR  5037777106796980248  5206516471428693478  5206516471428693478             1                 6\
    1        Vorlauf    ROHR  5123819811204259837  5206516471428693478  5206516471428693478             1                 7\
    1        Vorlauf    ROHR  5620197984230756681  5206516471428693478  5206516471428693478             1                 8\
    1        Vorlauf    VENT  4678923650983295610  5206516471428693478  5206516471428693478             1                 1\
    2       Rücklauf    KLAP  4801110583764519435  4693347477612662930  4693347477612662930             1                 1\
    2       Rücklauf    KNOT  4638663808856251977  4693347477612662930  4693347477612662930             1                 1\
    2       Rücklauf    KNOT  4807712987325933680  4693347477612662930  4693347477612662930             1                 2\
    2       Rücklauf    KNOT  4891048046264179170  4693347477612662930  4693347477612662930             1                 3\
    2       Rücklauf    KNOT  4979785838440534851  4693347477612662930  4693347477612662930             1                 4\
    2       Rücklauf    KNOT  5002109894154139899  4693347477612662930  4693347477612662930             1                 5\
    2       Rücklauf    KNOT  5183147862966701025  4693347477612662930  4693347477612662930             1                 6\
    2       Rücklauf    KNOT  5219230031772497417  4693347477612662930  4693347477612662930             1                 7\
    2       Rücklauf    KNOT  5356267303828212700  4693347477612662930  4693347477612662930             1                 8\
    2       Rücklauf    KNOT  5364712333175450942  4693347477612662930  4693347477612662930             1                 9\
    2       Rücklauf    KNOT  5397990465339071638  4693347477612662930  4693347477612662930             1                10\
    2       Rücklauf    KNOT  5508992300317633799  4693347477612662930  4693347477612662930             1                11\
    2       Rücklauf    KNOT  5543326527366090679  4693347477612662930  4693347477612662930             1                12\
    2       Rücklauf    KNOT  5557222628687032084  4693347477612662930  4693347477612662930             1                13\
    2       Rücklauf    PUMP  5481331875203087055  4693347477612662930  4693347477612662930             1                 1\
    2       Rücklauf    ROHR  4613782368750024999  4693347477612662930  4693347477612662930             1                 1\
    2       Rücklauf    ROHR  4637102239750163477  4693347477612662930  4693347477612662930             1                 2\
    2       Rücklauf    ROHR  4769996343148550485  4693347477612662930  4693347477612662930             1                 3\
    2       Rücklauf    ROHR  4945727430885351042  4693347477612662930  4693347477612662930             1                 4\
    2       Rücklauf    ROHR  5266224553324203132  4693347477612662930  4693347477612662930             1                 5\
    2       Rücklauf    ROHR  5379365049009065623  4693347477612662930  4693347477612662930             1                 6\
    2       Rücklauf    ROHR  5611703699850694889  4693347477612662930  4693347477612662930             1                 7\
    2       Rücklauf    ROHR  5647213228462830353  4693347477612662930  4693347477612662930             1                 8\
    2       Rücklauf    VENT  4897018421024717974  4693347477612662930  4693347477612662930             1                 1\
    2       Rücklauf    VENT  5525310316015533093  4693347477612662930  4693347477612662930             1                 2\
    3  Kundenanlagen    FWVB  4643800032883366034  5003333277973347346  5003333277973347346             1                 1\
    3  Kundenanlagen    FWVB  4704603947372595298  5003333277973347346  5003333277973347346             1                 2\
    3  Kundenanlagen    FWVB  5121101823283893406  5003333277973347346  5003333277973347346             1                 3\
    3  Kundenanlagen    FWVB  5400405917816384862  5003333277973347346  5003333277973347346             1                 4\
    3  Kundenanlagen    FWVB  5695730293103267172  5003333277973347346  5003333277973347346             1                 5\
    4           BHKW    BSYM  5043395081363401573  5555393404073362943  5555393404073362943             1                 1\
    4           BHKW    TEXT  5056836766824229789  5555393404073362943  5555393404073362943             1                 1\
    4           BHKW    TEXT  5329748935118523443  5555393404073362943  5555393404073362943             1                 2\
    5          Texte    ARRW  4664845735864571219  5394410243594912680  5394410243594912680             1                 1\
    5          Texte    ARRW  4902474974831811106  5394410243594912680  5394410243594912680             1                 2\
    5          Texte    ARRW  5026846801782366678  5394410243594912680  5394410243594912680             1                 3\
    5          Texte    ARRW  5688313372729413840  5394410243594912680  5394410243594912680             1                 4\
    5          Texte    NRCV  4681213816714574464  5394410243594912680  5394410243594912680             1                 1\
    5          Texte    NRCV  4857294696992797631  5394410243594912680  5394410243594912680             1                 2\
    5          Texte    NRCV  4914949875368816179  5394410243594912680  5394410243594912680             1                 3\
    5          Texte    NRCV  4946584950744559030  5394410243594912680  5394410243594912680             1                 4\
    5          Texte    NRCV  4968703141722117357  5394410243594912680  5394410243594912680             1                 5\
    5          Texte    NRCV  5091374651838464239  5394410243594912680  5394410243594912680             1                 6\
    5          Texte    NRCV  5097127385155151127  5394410243594912680  5394410243594912680             1                 7\
    5          Texte    NRCV  5179988968597313889  5394410243594912680  5394410243594912680             1                 8\
    5          Texte    NRCV  5281885868749421521  5394410243594912680  5394410243594912680             1                 9\
    5          Texte    NRCV  5410904806390050339  5394410243594912680  5394410243594912680             1                10\
    5          Texte    NRCV  5476262878682325254  5394410243594912680  5394410243594912680             1                11\
    5          Texte    NRCV  5557806245003742769  5394410243594912680  5394410243594912680             1                12\
    5          Texte    RECT  4994817837124479818  5394410243594912680  5394410243594912680             1                 1\
    5          Texte    RPFL  5158870568935841216  5394410243594912680  5394410243594912680             1                 1\
    5          Texte    TEXT  4628671704393700430  5394410243594912680  5394410243594912680             1                 1\
    5          Texte    TEXT  4654104397990769217  5394410243594912680  5394410243594912680             1                 2\
    5          Texte    TEXT  4666644549022031339  5394410243594912680  5394410243594912680             1                 3\
    5          Texte    TEXT  4693143208412077585  5394410243594912680  5394410243594912680             1                 4\
    5          Texte    TEXT  4768731522550494423  5394410243594912680  5394410243594912680             1                 5\
    5          Texte    TEXT  4770844990228490264  5394410243594912680  5394410243594912680             1                 6\
    5          Texte    TEXT  4782197969172967134  5394410243594912680  5394410243594912680             1                 7\
    5          Texte    TEXT  4855692488683645764  5394410243594912680  5394410243594912680             1                 8\
    5          Texte    TEXT  4965628942555351751  5394410243594912680  5394410243594912680             1                 9\
    5          Texte    TEXT  4995961504641886710  5394410243594912680  5394410243594912680             1                10\
    5          Texte    TEXT  5017907661719368413  5394410243594912680  5394410243594912680             1                11\
    5          Texte    TEXT  5028052147238787802  5394410243594912680  5394410243594912680             1                12\
    5          Texte    TEXT  5036153631350515544  5394410243594912680  5394410243594912680             1                13\
    5          Texte    TEXT  5054433315422452796  5394410243594912680  5394410243594912680             1                14\
    5          Texte    TEXT  5108336975548011049  5394410243594912680  5394410243594912680             1                15\
    5          Texte    TEXT  5262441422409836340  5394410243594912680  5394410243594912680             1                16\
    5          Texte    TEXT  5297832234834839298  5394410243594912680  5394410243594912680             1                17\
    5          Texte    TEXT  5370727463979416592  5394410243594912680  5394410243594912680             1                18\
    5          Texte    TEXT  5421223289472778073  5394410243594912680  5394410243594912680             1                19\
    5          Texte    TEXT  5501963349880613918  5394410243594912680  5394410243594912680             1                20\
    5          Texte    TEXT  5502619581048467908  5394410243594912680  5394410243594912680             1                21\
    5          Texte    TEXT  5540395812045688781  5394410243594912680  5394410243594912680             1                22\
    5          Texte    TEXT  5550982489075668484  5394410243594912680  5394410243594912680             1                23\
    5          Texte    TEXT  5610916400841895317  5394410243594912680  5394410243594912680             1                24\
    5          Texte    TEXT  5646820849868629537  5394410243594912680  5394410243594912680             1                25\
    5          Texte    TEXT  5696590398594231893  5394410243594912680  5394410243594912680             1                26\
    5          Texte    TEXT  5697088036451277538  5394410243594912680  5394410243594912680             1                27'''
>>> import difflib
>>> s = difflib.SequenceMatcher(None,sExp,sGot)
>>> for block in s.get_matching_blocks():
...    pass 
...    # print(block)
>>> print(xm._getvXXXXAsOneString(vXXXX='vLAYR',sortList=sortList,index=False))
LFDNR           NAME OBJTYPE                OBJID                   pk                   tk  nrObjInGroup  nrObjtypeInGroup
    1        Vorlauf    FWES  5638756766880678918  5206516471428693478  5206516471428693478             1                 1
    1        Vorlauf    KNOT  4731792362611615619  5206516471428693478  5206516471428693478             1                 1
    1        Vorlauf    KNOT  4756962427318766791  5206516471428693478  5206516471428693478             1                 2
    1        Vorlauf    KNOT  4766681917240867943  5206516471428693478  5206516471428693478             1                 3
    1        Vorlauf    KNOT  5049461676240771430  5206516471428693478  5206516471428693478             1                 4
    1        Vorlauf    KNOT  5370423799772591808  5206516471428693478  5206516471428693478             1                 5
    1        Vorlauf    KNOT  5444644492819213978  5206516471428693478  5206516471428693478             1                 6
    1        Vorlauf    KNOT  5515313800585145571  5206516471428693478  5206516471428693478             1                 7
    1        Vorlauf    KNOT  5646671866542823796  5206516471428693478  5206516471428693478             1                 8
    1        Vorlauf    KNOT  5736262931552588702  5206516471428693478  5206516471428693478             1                 9
    1        Vorlauf    KNOT  5741235692335544560  5206516471428693478  5206516471428693478             1                10
    1        Vorlauf    ROHR  4614949065966596185  5206516471428693478  5206516471428693478             1                 1
    1        Vorlauf    ROHR  4713733238627697042  5206516471428693478  5206516471428693478             1                 2
    1        Vorlauf    ROHR  4789218195240364437  5206516471428693478  5206516471428693478             1                 3
    1        Vorlauf    ROHR  4939422678063487923  5206516471428693478  5206516471428693478             1                 4
    1        Vorlauf    ROHR  4984202422877610920  5206516471428693478  5206516471428693478             1                 5
    1        Vorlauf    ROHR  5037777106796980248  5206516471428693478  5206516471428693478             1                 6
    1        Vorlauf    ROHR  5123819811204259837  5206516471428693478  5206516471428693478             1                 7
    1        Vorlauf    ROHR  5620197984230756681  5206516471428693478  5206516471428693478             1                 8
    1        Vorlauf    VENT  4678923650983295610  5206516471428693478  5206516471428693478             1                 1
    2       Rücklauf    KLAP  4801110583764519435  4693347477612662930  4693347477612662930             1                 1
    2       Rücklauf    KNOT  4638663808856251977  4693347477612662930  4693347477612662930             1                 1
    2       Rücklauf    KNOT  4807712987325933680  4693347477612662930  4693347477612662930             1                 2
    2       Rücklauf    KNOT  4891048046264179170  4693347477612662930  4693347477612662930             1                 3
    2       Rücklauf    KNOT  4979785838440534851  4693347477612662930  4693347477612662930             1                 4
    2       Rücklauf    KNOT  5002109894154139899  4693347477612662930  4693347477612662930             1                 5
    2       Rücklauf    KNOT  5183147862966701025  4693347477612662930  4693347477612662930             1                 6
    2       Rücklauf    KNOT  5219230031772497417  4693347477612662930  4693347477612662930             1                 7
    2       Rücklauf    KNOT  5356267303828212700  4693347477612662930  4693347477612662930             1                 8
    2       Rücklauf    KNOT  5364712333175450942  4693347477612662930  4693347477612662930             1                 9
    2       Rücklauf    KNOT  5397990465339071638  4693347477612662930  4693347477612662930             1                10
    2       Rücklauf    KNOT  5508992300317633799  4693347477612662930  4693347477612662930             1                11
    2       Rücklauf    KNOT  5543326527366090679  4693347477612662930  4693347477612662930             1                12
    2       Rücklauf    KNOT  5557222628687032084  4693347477612662930  4693347477612662930             1                13
    2       Rücklauf    PUMP  5481331875203087055  4693347477612662930  4693347477612662930             1                 1
    2       Rücklauf    ROHR  4613782368750024999  4693347477612662930  4693347477612662930             1                 1
    2       Rücklauf    ROHR  4637102239750163477  4693347477612662930  4693347477612662930             1                 2
    2       Rücklauf    ROHR  4769996343148550485  4693347477612662930  4693347477612662930             1                 3
    2       Rücklauf    ROHR  4945727430885351042  4693347477612662930  4693347477612662930             1                 4
    2       Rücklauf    ROHR  5266224553324203132  4693347477612662930  4693347477612662930             1                 5
    2       Rücklauf    ROHR  5379365049009065623  4693347477612662930  4693347477612662930             1                 6
    2       Rücklauf    ROHR  5611703699850694889  4693347477612662930  4693347477612662930             1                 7
    2       Rücklauf    ROHR  5647213228462830353  4693347477612662930  4693347477612662930             1                 8
    2       Rücklauf    VENT  4897018421024717974  4693347477612662930  4693347477612662930             1                 1
    2       Rücklauf    VENT  5525310316015533093  4693347477612662930  4693347477612662930             1                 2
    3  Kundenanlagen    FWVB  4643800032883366034  5003333277973347346  5003333277973347346             1                 1
    3  Kundenanlagen    FWVB  4704603947372595298  5003333277973347346  5003333277973347346             1                 2
    3  Kundenanlagen    FWVB  5121101823283893406  5003333277973347346  5003333277973347346             1                 3
    3  Kundenanlagen    FWVB  5400405917816384862  5003333277973347346  5003333277973347346             1                 4
    3  Kundenanlagen    FWVB  5695730293103267172  5003333277973347346  5003333277973347346             1                 5
    4           BHKW    BSYM  5043395081363401573  5555393404073362943  5555393404073362943             1                 1
    4           BHKW    TEXT  5056836766824229789  5555393404073362943  5555393404073362943             1                 1
    4           BHKW    TEXT  5329748935118523443  5555393404073362943  5555393404073362943             1                 2
    5          Texte    ARRW  4664845735864571219  5394410243594912680  5394410243594912680             1                 1
    5          Texte    ARRW  4902474974831811106  5394410243594912680  5394410243594912680             1                 2
    5          Texte    ARRW  5026846801782366678  5394410243594912680  5394410243594912680             1                 3
    5          Texte    ARRW  5688313372729413840  5394410243594912680  5394410243594912680             1                 4
    5          Texte    NRCV  4681213816714574464  5394410243594912680  5394410243594912680             1                 1
    5          Texte    NRCV  4857294696992797631  5394410243594912680  5394410243594912680             1                 2
    5          Texte    NRCV  4914949875368816179  5394410243594912680  5394410243594912680             1                 3
    5          Texte    NRCV  4946584950744559030  5394410243594912680  5394410243594912680             1                 4
    5          Texte    NRCV  4968703141722117357  5394410243594912680  5394410243594912680             1                 5
    5          Texte    NRCV  5091374651838464239  5394410243594912680  5394410243594912680             1                 6
    5          Texte    NRCV  5097127385155151127  5394410243594912680  5394410243594912680             1                 7
    5          Texte    NRCV  5179988968597313889  5394410243594912680  5394410243594912680             1                 8
    5          Texte    NRCV  5281885868749421521  5394410243594912680  5394410243594912680             1                 9
    5          Texte    NRCV  5410904806390050339  5394410243594912680  5394410243594912680             1                10
    5          Texte    NRCV  5476262878682325254  5394410243594912680  5394410243594912680             1                11
    5          Texte    NRCV  5557806245003742769  5394410243594912680  5394410243594912680             1                12
    5          Texte    RECT  4994817837124479818  5394410243594912680  5394410243594912680             1                 1
    5          Texte    RPFL  5158870568935841216  5394410243594912680  5394410243594912680             1                 1
    5          Texte    TEXT  4628671704393700430  5394410243594912680  5394410243594912680             1                 1
    5          Texte    TEXT  4654104397990769217  5394410243594912680  5394410243594912680             1                 2
    5          Texte    TEXT  4666644549022031339  5394410243594912680  5394410243594912680             1                 3
    5          Texte    TEXT  4693143208412077585  5394410243594912680  5394410243594912680             1                 4
    5          Texte    TEXT  4768731522550494423  5394410243594912680  5394410243594912680             1                 5
    5          Texte    TEXT  4770844990228490264  5394410243594912680  5394410243594912680             1                 6
    5          Texte    TEXT  4782197969172967134  5394410243594912680  5394410243594912680             1                 7
    5          Texte    TEXT  4855692488683645764  5394410243594912680  5394410243594912680             1                 8
    5          Texte    TEXT  4965628942555351751  5394410243594912680  5394410243594912680             1                 9
    5          Texte    TEXT  4995961504641886710  5394410243594912680  5394410243594912680             1                10
    5          Texte    TEXT  5017907661719368413  5394410243594912680  5394410243594912680             1                11
    5          Texte    TEXT  5028052147238787802  5394410243594912680  5394410243594912680             1                12
    5          Texte    TEXT  5036153631350515544  5394410243594912680  5394410243594912680             1                13
    5          Texte    TEXT  5054433315422452796  5394410243594912680  5394410243594912680             1                14
    5          Texte    TEXT  5108336975548011049  5394410243594912680  5394410243594912680             1                15
    5          Texte    TEXT  5262441422409836340  5394410243594912680  5394410243594912680             1                16
    5          Texte    TEXT  5297832234834839298  5394410243594912680  5394410243594912680             1                17
    5          Texte    TEXT  5370727463979416592  5394410243594912680  5394410243594912680             1                18
    5          Texte    TEXT  5421223289472778073  5394410243594912680  5394410243594912680             1                19
    5          Texte    TEXT  5501963349880613918  5394410243594912680  5394410243594912680             1                20
    5          Texte    TEXT  5502619581048467908  5394410243594912680  5394410243594912680             1                21
    5          Texte    TEXT  5540395812045688781  5394410243594912680  5394410243594912680             1                22
    5          Texte    TEXT  5550982489075668484  5394410243594912680  5394410243594912680             1                23
    5          Texte    TEXT  5610916400841895317  5394410243594912680  5394410243594912680             1                24
    5          Texte    TEXT  5646820849868629537  5394410243594912680  5394410243594912680             1                25
    5          Texte    TEXT  5696590398594231893  5394410243594912680  5394410243594912680             1                26
    5          Texte    TEXT  5697088036451277538  5394410243594912680  5394410243594912680             1                27
>>> 
>>> # ---
>>> # vGTXT
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vGTXT',sortList=['CONT_ID','pk'],index=False,header=False))                                 
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                          numerische Anzeige:  4614148870174765680  4614148870174765680                           (219.0, -278.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                           Georeferenzpunkt 2  4628671704393700430  4628671704393700430              (1115.9500000001863, -323.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                                        Block  4666644549022031339  4666644549022031339                            (-58.0, -77.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                           numerische Anzeige  4693143208412077585  4693143208412077585                            (1211.0, -9.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                             Knoten und Rohre  4995961504641886710  4995961504641886710                            (570.0, -49.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                                Vorlaufstrang  5017907661719368413  5017907661719368413  (358.20699999993667, 220.39499999955297)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                          LocalHeatingNetwork  5028052147238787802  5028052147238787802                           (1163.0, 536.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1   Tel. 05131 - 4980-0 ; Fax. 05131 - 4980-15  5054433315422452796  5054433315422452796                         (-230.0, -1143.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                    Kontrolle: DH-Massenstrom  5100960407865990868  5100960407865990868                           (-60.0, -160.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                        Wärmebilanz: 3 Kunden  5150752151066924202  5150752151066924202                           (219.0, -318.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1  eMail. info@3SConsult.de ; www.3SConsult.de  5370727463979416592  5370727463979416592                         (-230.0, -1204.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                Differenzdruck VL-/ RL-Knoten  5502619581048467908  5502619581048467908                           (1211.0, -49.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                                 Kundenanlage  5540395812045688781  5540395812045688781  (1131.9500000001863, 283.95000000018626)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                         Fernwärmeverbraucher  5550982489075668484  5550982489075668484                           (1050.0, 239.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                               Rücklaufstrang  5610916400841895317  5610916400841895317                             (570.0, -9.0)
 Nahwärmenetz mit 1000 kW Anschlussleistu  1001  -1                             Knoten und Rohre  5646820849868629537  5646820849868629537  (358.20699999993667, 174.39499999955297)
                                     BHKW  1002  -1                          Fernwärmeeinspeiser  4654104397990769217  4654104397990769217                             (115.0, 80.0)
                                     BHKW  1002  -1                                        Pumpe  4768731522550494423  4768731522550494423                             (175.0, 25.0)
                                     BHKW  1002  -1                            Wärmebilanz Netz:  4770844990228490264  4770844990228490264                             (90.0, 160.0)
                                     BHKW  1002  -1                                  Speicherung  4782197969172967134  4782197969172967134                            (110.0, 140.0)
                                     BHKW  1002  -1                               Richtungspfeil  4855692488683645764  4855692488683645764                            (220.0, 105.0)
                                     BHKW  1002  -1                                     Verluste  4965628942555351751  4965628942555351751                            (110.0, 145.0)
                                     BHKW  1002  -1                          (Element verbinden)  5036153631350515544  5036153631350515544                             (150.0, 90.0)
                                     BHKW  1002  -1                    BHKW Modul 1000 kW therm.  5056836766824229789  5056836766824229789                              (35.0, 55.0)
                                     BHKW  1002  -1                                       Ventil  5108336975548011049  5108336975548011049                             (205.0, 25.0)
                                     BHKW  1002  -1                                    Verbrauch  5262441422409836340  5262441422409836340                            (110.0, 150.0)
                                     BHKW  1002  -1                                  Einspeisung  5297832234834839298  5297832234834839298                            (110.0, 155.0)
                                     BHKW  1002  -1                           Druckhaltung 2 bar  5329748935118523443  5329748935118523443                             (180.0, 65.0)
                                     BHKW  1002  -1                           Numerische Anzeige  5421223289472778073  5421223289472778073                            (190.0, 115.0)
                                     BHKW  1002  -1                             Verbindungslinie  5501963349880613918  5501963349880613918                             (150.0, 95.0)
                                     BHKW  1002  -1                                       (Text)  5696590398594231893  5696590398594231893                              (35.0, 50.0)
                                     BHKW  1002  -1                                       Klappe  5697088036451277538  5697088036451277538                             (145.0, 25.0)
>>> # ---
>>> # vNRCV
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vNRCV',end=14,dropColList=['DPGR','CONT_LFDNR','pk_ROWS'],sortList=['OBJTYPE'
... ,'fkOBJTYPE' # 90-12 in BZ
... ,'ATTRTYPE','cRefLfdNr']))
   cRefLfdNr                                      CONT CONT_ID OBJTYPE            fkOBJTYPE ATTRTYPE              tk_ROWS                   pk                   tk                                  pXYLB
0          1                                      BHKW    1002    FWES  5638756766880678918        W  5762106696740202356  4857294696992797631  4857294696992797631                           (90.0, 65.0)
1          1                                      BHKW    1002    KNOT  5049461676240771430        T  4723443975311885965  5097127385155151127  5097127385155151127                           (90.0, 95.0)
2          1                                      BHKW    1002    KNOT  5219230031772497417        T  5602301870151014230  5557806245003742769  5557806245003742769                           (90.0, 35.0)
3          1                                      BHKW    1002    KNOT  5356267303828212700       PH  5000989080893535213  4968703141722117357  4968703141722117357                          (220.0, 25.0)
4          1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001    KNOT  5397990465339071638       QM  5134531789044068877  5410059595276504750  5410059595276504750                          (91.0, -94.0)
5          2                                      BHKW    1002    KNOT  5397990465339071638       QM  5134531789044068877  5357021981944933535  5357021981944933535  (184.999999464624, 57.99999953107601)
6          1                                      BHKW    1002    KNOT  5736262931552588702       PH  4754881272083464445  4681213816714574464  4681213816714574464                          (220.0, 85.0)
7          1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001    KNOT  5741235692335544560       DP  4949183695502554728  4914949875368816179  4914949875368816179                         (1234.0, 83.0)
8          1                                      BHKW    1002    PUMP  5481331875203087055        N  5563842594211689762  5091374651838464239  5091374651838464239                          (170.0, 45.0)
9          1                                      BHKW    1002    VENT  4678923650983295610       QM  5126307362398248950  5410904806390050339  5410904806390050339                         (200.0, 110.0)
10         1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001    WBLZ  4694700216019268978      WVB  4778244458749966216  4991097791264453745  4991097791264453745                        (354.0, -225.0)
11         1                                      BHKW    1002    WBLZ  5262603207038486299      WES  5690691957596882133  5179988968597313889  5179988968597313889                          (90.0, 155.0)
12         1                                      BHKW    1002    WBLZ  5262603207038486299    WSPEI  5153847813311339683  4946584950744559030  4946584950744559030                          (90.0, 140.0)
13         1                                      BHKW    1002    WBLZ  5262603207038486299      WVB  5214984699859365639  5281885868749421521  5281885868749421521                          (90.0, 150.0)
>>> # ---
>>> # MxSync() - without Mx-Object
>>> # ---
>>> vROHR=xm.dataFrames['vROHR']
>>> vROHR.shape
(16, 74)
>>> 'vNRCV_Mx1' in xm.dataFrames
False
>>> mx=xm.MxSync()
>>> 'vNRCV_Mx1' in xm.dataFrames
True
>>> vROHR.shape
(16, 76)
>>> print(xm._getvXXXXAsOneString(vXXXX='vROHR',dropColList=['NAME_i_2L','NAME_k_2L']))
   BESCHREIBUNG IDREFERENZ BAUJAHR HAL IPLANUNG KENNUNG       L LZU  RAU ZAUS ZEIN ZUML JLAMBS LAMBDA0 ASOLL INDSCHALL KVR AUSFALLZEIT     DA     DI   DN     KT   PN REHABILITATION REPARATUR    S WSTEIG WTIEFE LTGR_NAME            LTGR_BESCHREIBUNG SICHTBARKEIT VERLEGEART DTRO_NAME                        DTRO_BESCHREIBUNG        E fkSTRASSE fkSRAT                   pk                   tk IRTRENN LECKSTART LECKEND LECKMENGE LECKORT LECKSTATUS QSVB ZVLIMPTNZ KANTENZV                                      CONT CONT_ID CONT_LFDNR  NAME_i KVR_i TM_i   XKOR_i   YKOR_i ZKOR_i  NAME_k KVR_k TM_k   XKOR_k   YKOR_k ZKOR_k  pXCor_i  pYCor_i  pXCor_k  pYCor_k            pXCors          pYCors                                pWAYPXCors                                pWAYPYCors                                                                                               WAYP  mx2NofPts  mx2Idx
0          None         -1    None   0        1       0   88.02   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4613782368750024999  4613782368750024999       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K004     2   60  2541539  5706361     20  R-K005     2   60  2541627  5706363     20    799.0    152.0    887.0    154.0    [799.0, 887.0]  [152.0, 154.0]    [807.8999999999069, 895.9500000001863]  [140.09999999962747, 142.04999999981374]                                                 [(2541547.9, 5706349.1), (2541635.95, 5706351.05)]          2       0
1          None         -1    None   0        1       0  405.96   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4614949065966596185  4614949065966596185       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K002     1   90  2541059  5706265     20  V-K003     1   90  2541457  5706345     20    319.0     56.0    717.0    136.0    [319.0, 717.0]   [56.0, 136.0]                [319.0, 716.9500000001863]               [56.049999999813735, 136.0]                                                 [(2541059.0, 5706265.05), (2541456.95, 5706345.0)]          2       1
2          None         -1    None   0        1       0   83.55   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4637102239750163477  4637102239750163477       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K003     2   60  2541457  5706345     20  R-K004     2   60  2541539  5706361     20    717.0    136.0    799.0    152.0    [717.0, 799.0]  [136.0, 152.0]    [725.8500000000931, 807.8999999999069]  [124.04999999981374, 140.09999999962747]                                                 [(2541465.85, 5706333.05), (2541547.9, 5706349.1)]          2       2
3          None         -1    None   0        1       0   88.02   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4713733238627697042  4713733238627697042       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K004     1   90  2541539  5706361     20  V-K005     1   90  2541627  5706363     20    799.0    152.0    887.0    154.0    [799.0, 887.0]  [152.0, 154.0]                [799.0, 887.0499999998137]                            [152.0, 154.0]                                                  [(2541539.0, 5706361.0), (2541627.05, 5706363.0)]          2       3
4          None         -1    None   0        1       0  195.53   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4789218195240364437  4789218195240364437       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K001     1   90  2540867  5706228     20  V-K002     1   90  2541059  5706265     20    127.0     19.0    319.0     56.0    [127.0, 319.0]    [19.0, 56.0]                            [127.0, 319.0]                [19.0, 56.049999999813735]                                                  [(2540867.0, 5706228.0), (2541059.0, 5706265.05)]          2       5
5          None         -1    None   0        1       0  109.77   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4945727430885351042  4945727430885351042       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K006     2   60  2541790  5706338     20  R-K007     2   60  2541899  5706325     20   1050.0    129.0   1159.0    116.0  [1050.0, 1159.0]  [129.0, 116.0]  [1058.8500000000931, 1167.8999999999069]               [117.0, 104.09999999962747]                                                  [(2541798.85, 5706326.0), (2541907.9, 5706313.1)]          2       7
6          None         -1    None   0        1       0    76.4   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4984202422877610920  4984202422877610920       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K000     1   90  2540793  5706209     20  V-K001     1   90  2540867  5706228     20     53.0      0.0    127.0     19.0     [53.0, 127.0]     [0.0, 19.0]               [53.049999999813735, 127.0]             [-0.049999999813735485, 19.0]                                                 [(2540793.05, 5706208.95), (2540867.0, 5706228.0)]          2       8
7          None         -1    None   0        1       0   83.55   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5037777106796980248  5037777106796980248       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K003     1   90  2541457  5706345     20  V-K004     1   90  2541539  5706361     20    717.0    136.0    799.0    152.0    [717.0, 799.0]  [136.0, 152.0]                [716.9500000001863, 799.0]                            [136.0, 152.0]                                                  [(2541456.95, 5706345.0), (2541539.0, 5706361.0)]          2       9
8          None         -1    None   0        1       0  164.91   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5123819811204259837  5123819811204259837       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K005     1   90  2541627  5706363     20  V-K006     1   90  2541790  5706338     20    887.0    154.0   1050.0    129.0   [887.0, 1050.0]  [154.0, 129.0]   [887.0499999998137, 1049.9500000001863]               [154.0, 128.95000000018626]                                                [(2541627.05, 5706363.0), (2541789.95, 5706337.95)]          2      10
9          None         -1    None   0        1       0  195.53   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5266224553324203132  5266224553324203132       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K001     2   60  2540867  5706228     20  R-K002     2   60  2541059  5706265     20    127.0     19.0    319.0     56.0    [127.0, 319.0]    [19.0, 56.0]  [135.89999999990687, 327.89999999990687]   [7.0499999998137355, 44.09999999962747]                                                  [(2540875.9, 5706216.05), (2541067.9, 5706253.1)]          2      11
10         None         -1    None   0        1       0  405.96   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5379365049009065623  5379365049009065623       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K002     2   60  2541059  5706265     20  R-K003     2   60  2541457  5706345     20    319.0     56.0    717.0    136.0    [319.0, 717.0]   [56.0, 136.0]   [327.89999999990687, 725.8500000000931]   [44.09999999962747, 124.04999999981374]                                                 [(2541067.9, 5706253.1), (2541465.85, 5706333.05)]          2      12
11         None         -1    None   0        1       0  164.91   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5611703699850694889  5611703699850694889       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K005     2   60  2541627  5706363     20  R-K006     2   60  2541790  5706338     20    887.0    154.0   1050.0    129.0   [887.0, 1050.0]  [154.0, 129.0]   [895.9500000001863, 1058.8500000000931]               [142.04999999981374, 117.0]                                                [(2541635.95, 5706351.05), (2541798.85, 5706326.0)]          2      13
12         None         -1    None   0        1       0  109.77   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5620197984230756681  5620197984230756681       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  V-K006     1   90  2541790  5706338     20  V-K007     1   90  2541899  5706325     20   1050.0    129.0   1159.0    116.0  [1050.0, 1159.0]  [129.0, 116.0]              [1049.9500000001863, 1159.0]  [128.95000000018626, 116.04999999981374]                                                [(2541789.95, 5706337.95), (2541899.0, 5706325.05)]          2      14
13         None         -1    None   0        1       0    76.4   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  114.3  107.1  100  0.325  NaN            NaN       NaN  3.6    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  5647213228462830353  5647213228462830353       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  R-K000     2   60  2540793  5706209     20  R-K001     2   60  2540867  5706228     20     53.0      0.0    127.0     19.0     [53.0, 127.0]     [0.0, 19.0]  [61.950000000186265, 135.89999999990687]               [-12.0, 7.0499999998137355]                                                 [(2540801.95, 5706197.0), (2540875.9, 5706216.05)]          2      15
14         None         -1    None   0        1       0   73.42   0  0.1    0    0    0      1   0.025  1000         0   2         NaN  168.3  160.3  150   0.45  NaN            NaN       NaN    4    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4769996343148550485  4769996343148550485       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1     R-L     2   60  2540740  5706225     20  R-K000     2   60  2540793  5706209     20      0.0     16.0     53.0      0.0       [0.0, 53.0]     [16.0, 0.0]     [0.0, 24.0, 45.0, 61.950000000186265]                [16.0, 16.0, -12.0, -12.0]  [(2540740.0, 5706225.0), (2540764.0, 5706225.0), (2540785.0, 5706197.0), (2540801.95, 5706197.0)]          2       4
15         None         -1    None   0        1       0    68.6   0  0.1    0    0    0      1   0.025  1000         0   1         NaN  168.3  160.3  150   0.45  NaN            NaN       NaN    4    NaN    NaN   KUMANRO  Beschreibung Leitungsgruppe            1     999999   KUMANRO  Kunststoffmantelrohr DN20-800 PANISOVIT  2.1E+11        -1     -1  4939422678063487923  4939422678063487923       0         0       0         0       0          0    0       NaN      NaN  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1     V-L     1   90  2540740  5706240     20  V-K000     1   90  2540793  5706209     20      0.0     31.0     53.0      0.0       [0.0, 53.0]     [31.0, 0.0]           [0.0, 30.0, 53.049999999813735]       [31.0, 31.0, -0.049999999813735485]                         [(2540740.0, 5706240.0), (2540770.0, 5706240.0), (2540793.05, 5706208.95)]          2       6
>>> # ---------
>>> # MxSync() 
>>> # ---------
>>> xm=Xm(xmlFile=xmlFile)
>>> vROHR=xm.dataFrames['vROHR']
>>> vROHR.shape
(16, 74)
>>> 'vNRCV_Mx1' in xm.dataFrames
False
>>> (wDir,modelDir,modelName,mx1File)=xm.getWDirModelDirModelName()    
>>> mx=Mx.Mx(mx1File=mx1File)
>>> xm.MxSync(mx=mx)
>>> vROHR.shape
(16, 76)
>>> 'vNRCV_Mx1' in xm.dataFrames
True
>>> # ---
>>> # vNRCV_Mx1
>>> # ---
>>> import re
>>> f=lambda s: re.match('(\S+)~(\S*)~(\S*)~(\d+)~(\S+)',s).group(1)+'~~~'+re.match('(\S+)~(\S*)~(\S*)~(\d+)~(\S+)',s).group(4)+'~'+re.match('(\S+)~(\S*)~(\S*)~(\d+)~(\S+)',s).group(5)
>>> print(xm._getvXXXXAsOneString(vXXXX='vNRCV_Mx1',end=14,dropColList=['DPGR','CONT_LFDNR','pk_ROWS'],mapFunc={'Sir3sID':f},sortList=['Sir3sID'],fmtFunc={'Sir3sID':f},index=False,header=False))
     FWES~~~5638756766880678918~W  1                                      BHKW  1002  FWES  5638756766880678918      W  5762106696740202356  4857294696992797631  4857294696992797631     (90.0, 65.0)
     KNOT~~~5049461676240771430~T  1                                      BHKW  1002  KNOT  5049461676240771430      T  4723443975311885965  5097127385155151127  5097127385155151127     (90.0, 95.0)
     KNOT~~~5219230031772497417~T  1                                      BHKW  1002  KNOT  5219230031772497417      T  5602301870151014230  5557806245003742769  5557806245003742769     (90.0, 35.0)
    KNOT~~~5356267303828212700~PH  1                                      BHKW  1002  KNOT  5356267303828212700     PH  5000989080893535213  4968703141722117357  4968703141722117357    (220.0, 25.0)
    KNOT~~~5397990465339071638~QM  1  Nahwärmenetz mit 1000 kW Anschlussleistu  1001  KNOT  5397990465339071638     QM  5134531789044068877  5410059595276504750  5410059595276504750    (91.0, -94.0)
    KNOT~~~5736262931552588702~PH  1                                      BHKW  1002  KNOT  5736262931552588702     PH  4754881272083464445  4681213816714574464  4681213816714574464    (220.0, 85.0)
    KNOT~~~5741235692335544560~DP  1  Nahwärmenetz mit 1000 kW Anschlussleistu  1001  KNOT  5741235692335544560     DP  4949183695502554728  4914949875368816179  4914949875368816179   (1234.0, 83.0)
     PUMP~~~5481331875203087055~N  1                                      BHKW  1002  PUMP  5481331875203087055      N  5563842594211689762  5091374651838464239  5091374651838464239    (170.0, 45.0)
    VENT~~~4678923650983295610~QM  1                                      BHKW  1002  VENT  4678923650983295610     QM  5126307362398248950  5410904806390050339  5410904806390050339   (200.0, 110.0)
   WBLZ~~~4694700216019268978~WVB  1  Nahwärmenetz mit 1000 kW Anschlussleistu  1001  WBLZ  4694700216019268978    WVB  4778244458749966216  4991097791264453745  4991097791264453745  (354.0, -225.0)
   WBLZ~~~5262603207038486299~WES  1                                      BHKW  1002  WBLZ  5262603207038486299    WES  5690691957596882133  5179988968597313889  5179988968597313889    (90.0, 155.0)
 WBLZ~~~5262603207038486299~WSPEI  1                                      BHKW  1002  WBLZ  5262603207038486299  WSPEI  5153847813311339683  4946584950744559030  4946584950744559030    (90.0, 140.0)
   WBLZ~~~5262603207038486299~WVB  1                                      BHKW  1002  WBLZ  5262603207038486299    WVB  5214984699859365639  5281885868749421521  5281885868749421521    (90.0, 150.0)
 WBLZ~~~5262603207038486299~WVERL  1                                      BHKW  1002  WBLZ  5262603207038486299  WVERL  4722863010266870887  5476262878682325254  5476262878682325254    (90.0, 145.0)
>>> # ---
>>> # vKNOT
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vKNOT',end=1,dropColList=['LFKT_NAME','LF','LF_min','LF_max','PVAR_NAME','PH','PH_min','PH_max','PZON_NAME','FSTF_NAME','STOF_NAME','GMIX_NAME','UTMP_NAME','2L_NAME','2L_KVR','fkHYDR','fkFQPS']))
     NAME BESCHREIBUNG IDREFERENZ                                      CONT CONT_ID CONT_LFDNR CONT_VKNO  KTYP LFAKT QM_EIN QVAR_NAME  QM  QM_min  QM_max KVR  TE  TM     XKOR     YKOR ZKOR                   pk                   tk  pXCor  pYCor  mx2Idx
0  R-K004         None         -1  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1       NaN  QKON     1      0       NaN NaN     NaN     NaN   2  10  60  2541539  5706361   20  4638663808856251977  4638663808856251977  799.0  152.0       0
>>> print(xm._getvXXXXAsOneString(vXXXX='vFWVB',dropColList=['BESCHREIBUNG','IDREFERENZ','W0','W','IRFV','LFK','TVL0','TRS0','LFKT','W_min','W_max','INDTR','TRSK','VTYP','DPHAUS','IMBG', 'pk','tk','KVR_i','TM_i', 'XKOR_i','YKOR_i','ZKOR_i','pXCor_i','pYCor_i','KVR_k','TM_k', 'XKOR_k','YKOR_k','ZKOR_k','pXCor_k', 'pYCor_k','CONT','CONT_ID', 'CONT_LFDNR']))
   W0LFK  NAME_i  NAME_k                         WBLZ  mx2Idx
0  160.0  V-K002  R-K002  [BLNZ1, BLNZ1u5, BLNZ1u5u7]       0
1  200.0  V-K004  R-K004                           []       1
2  160.0  V-K005  R-K005  [BLNZ1u5, BLNZ1u5u7, BLNZ5]       2
3  160.0  V-K007  R-K007                  [BLNZ1u5u7]       3
4  120.0  V-K003  R-K003                           []       4
>>> # ---
>>> # vXXXX
>>> # ---
>>> xm.dataFrames['vVBEL_forTestOnly']=xm.dataFrames['vVBEL'].reset_index(inplace=False) # Multiindex to Cols
>>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL_forTestOnly',index=True,dropColList=['Z_i','pk_i','CONT_i','CONT_VKNO_i','Z_k','pk_k','CONT_k','CONT_VKNO_k','IDREFERENZ','tk']))
   OBJTYPE                OBJID                   BESCHREIBUNG       NAME_i  NAME_k             LAYR       L      D  mx2Idx
0     FWES  5638756766880678918  BHKW - Modul - 1000 kW therm.           R3     V-1        [Vorlauf]       0     80       0
1     FWVB  4643800032883366034                              1       V-K002  R-K002  [Kundenanlagen]       0    NaN       0
2     FWVB  4704603947372595298                              3       V-K004  R-K004  [Kundenanlagen]       0    NaN       1
3     FWVB  5121101823283893406                              4       V-K005  R-K005  [Kundenanlagen]       0    NaN       2
4     FWVB  5400405917816384862                              5       V-K007  R-K007  [Kundenanlagen]       0    NaN       3
5     FWVB  5695730293103267172                              2       V-K003  R-K003  [Kundenanlagen]       0    NaN       4
6     KLAP  4801110583764519435                           None           R2      R3       [Rücklauf]       0     80       0
7     PGRP  4986517622672493603                   Pumpengruppe          R-1      R3               []       0    NaN       0
8     PUMP  5481331875203087055                    Umwälzpumpe          R-1      R2       [Rücklauf]       0    NaN       0
9     ROHR  4613782368750024999                           None       R-K004  R-K005       [Rücklauf]   88.02  107.1       0
10    ROHR  4614949065966596185                           None       V-K002  V-K003        [Vorlauf]  405.96  107.1       1
11    ROHR  4637102239750163477                           None       R-K003  R-K004       [Rücklauf]   83.55  107.1       2
12    ROHR  4713733238627697042                           None       V-K004  V-K005        [Vorlauf]   88.02  107.1       3
13    ROHR  4769996343148550485                           None          R-L  R-K000       [Rücklauf]   73.42  160.3       4
14    ROHR  4789218195240364437                           None       V-K001  V-K002        [Vorlauf]  195.53  107.1       5
15    ROHR  4939422678063487923                           None          V-L  V-K000        [Vorlauf]    68.6  160.3       6
16    ROHR  4945727430885351042                           None       R-K006  R-K007       [Rücklauf]  109.77  107.1       7
17    ROHR  4984202422877610920                           None       V-K000  V-K001        [Vorlauf]    76.4  107.1       8
18    ROHR  5037777106796980248                           None       V-K003  V-K004        [Vorlauf]   83.55  107.1       9
19    ROHR  5123819811204259837                           None       V-K005  V-K006        [Vorlauf]  164.91  107.1      10
20    ROHR  5266224553324203132                           None       R-K001  R-K002       [Rücklauf]  195.53  107.1      11
21    ROHR  5379365049009065623                           None       R-K002  R-K003       [Rücklauf]  405.96  107.1      12
22    ROHR  5611703699850694889                           None       R-K005  R-K006       [Rücklauf]  164.91  107.1      13
23    ROHR  5620197984230756681                           None       V-K006  V-K007        [Vorlauf]  109.77  107.1      14
24    ROHR  5647213228462830353                           None       R-K000  R-K001       [Rücklauf]    76.4  107.1      15
25    VENT  4678923650983295610                           None          V-1     V-L        [Vorlauf]       0    150       0
26    VENT  4897018421024717974                           None          R-L     R-1       [Rücklauf]       0    150       1
27    VENT  5525310316015533093                           None  PKON-Knoten     R-1       [Rücklauf]       0     50       2
>>> # ---
>>> # vRART
>>> # ---
>>> print(xm._getvXXXXAsOneString(vXXXX='vRART',index=True,sortList=['INDSTD','NAME']))
  NAME              BESCHREIBUNG                                   INDSTD_TXT  INDSTD   DWDT WSOSTD                   pk NAME_KREF1 NAME_KREF2 NAME_SWVT
0   dp  Bezeichnung Regelungsart  Differenzdruck Druckseite, Sollwert Tabelle      55  1E+20      0  5552938346422332788     V-K007     R-K007      SWVT
>>> # ------
>>> # MxAdd
>>> # ------
>>> if 'vNRCV_Mx1' in xm.dataFrames:
...    del xm.dataFrames['vNRCV_Mx1'] # delete MxSync-Result to force MxSync-Call in MxAdd
>>> oldShape=xm.dataFrames['vKNOT'].shape
>>> mx=xm.MxAdd()
>>> firstShape=xm.dataFrames['vKNOT'].shape
>>> oldShape[1]<firstShape[1]
True
>>> xm.MxAdd(mx=mx)
>>> secondShape=xm.dataFrames['vKNOT'].shape
>>> secondShape==firstShape
True
>>> xm.MxAdd(mx=mx)
>>> thirdShape=xm.dataFrames['vKNOT'].shape
>>> thirdShape==firstShape
True
>>> xm.dataFrames['vKNOT_forTestOnly']=xm.dataFrames['vKNOT'].rename(columns={'KNOT~*~*~*~PH':'Druck'})
>>> if 'Druck' not in xm.dataFrames['vKNOT_forTestOnly']:
...     xm.dataFrames['vKNOT_forTestOnly'].rename(columns={'KNOT~*~*~*~H':'Druck'},inplace=True)
>>> if 'Druck' not in xm.dataFrames['vKNOT_forTestOnly']:
...     xm.dataFrames['vKNOT_forTestOnly'].rename(columns={'KNOT~*~~*~PH':'Druck'},inplace=True) #09 
>>> f = lambda x: round(x,1) if x != None else None  
>>> print(xm._getvXXXXAsOneString(vXXXX='vKNOT_forTestOnly',filterColList=['mx2Idx','KVR','NAME','Druck'],mapFunc={'Druck':f},index=True))
    mx2Idx KVR         NAME  Druck
0        0   2       R-K004    2.3
1        1   1       V-K002    4.0
2        2   1       V-K001    4.1
3        3   1       V-K000    4.1
4        4   2       R-K001    2.0
5        5   2       R-K003    2.3
6        6   2       R-K000    2.0
7        9   2       R-K005    2.3
8       11   2          R-L    2.0
9       12   2       R-K002    2.1
10      13   1       V-K004    3.8
11      15   1       V-K005    3.8
12      16   2       R-K007    2.3
13      17   1       V-K006    3.8
14      18   2       R-K006    2.3
15      20   1       V-K003    3.8
16      21   1          V-L    4.1
17      22   1       V-K007    3.8
18       7   2           R2    4.3
19       8   1          V-1    4.1
20      10   2           R3    4.3
21      14   2  PKON-Knoten    2.0
22      19   2          R-1    2.0
>>> print(xm._getvXXXXAsOneString(vXXXX='vROHR',filterColList=['mx2Idx','L','KVR','NAME_i','NAME_k','ROHR~*~*~*~QMAV'],mapFunc={'ROHR~*~*~*~QMAV':f},sortList=['ROHR~*~*~*~QMAV','NAME_i'],index=True))
    mx2Idx       L KVR  NAME_i  NAME_k  ROHR~*~*~*~QMAV
13      15    76.4   2  R-K000  R-K001            -23.0
9       11  195.53   2  R-K001  R-K002            -23.0
14       4   73.42   2     R-L  R-K000            -23.0
10      12  405.96   2  R-K002  R-K003            -19.1
2        2   83.55   2  R-K003  R-K004            -15.4
0        0   88.02   2  R-K004  R-K005             -8.5
11      13  164.91   2  R-K005  R-K006             -3.9
5        7  109.77   2  R-K006  R-K007             -3.9
8       10  164.91   1  V-K005  V-K006              3.9
12      14  109.77   1  V-K006  V-K007              3.9
3        3   88.02   1  V-K004  V-K005              8.5
7        9   83.55   1  V-K003  V-K004             15.4
1        1  405.96   1  V-K002  V-K003             19.1
6        8    76.4   1  V-K000  V-K001             23.0
4        5  195.53   1  V-K001  V-K002             23.0
15       6    68.6   1     V-L  V-K000             23.0
>>> print(xm._getvXXXXAsOneString(vXXXX='vFWVB',filterColList=['mx2Idx','NAME_i','NAME_k','FWVB~*~*~*~W'],mapFunc={'FWVB~*~*~*~W':f},sortList=['FWVB~*~*~*~W','NAME_i'],index=True))
   mx2Idx  NAME_i  NAME_k  FWVB~*~*~*~W
4       4  V-K003  R-K003         120.0
0       0  V-K002  R-K002         160.0
2       2  V-K005  R-K005         160.0
3       3  V-K007  R-K007         160.0
1       1  V-K004  R-K004         200.0
>>> xm.dataFrames['vVBEL_forTestOnly2']=xm.dataFrames['vVBEL'].loc[['ROHR','FWVB'],:].reset_index(inplace=False) # Multiindex to Cols
>>> xm.dataFrames['vVBEL_forTestOnly2'].rename(columns={'KNOT~*~*~*~PH_i':'Druck_i'},inplace=True)
>>> if 'Druck_i' not in xm.dataFrames['vVBEL_forTestOnly2']:
...     xm.dataFrames['vVBEL_forTestOnly2'].rename(columns={'KNOT~*~*~*~H_i':'Druck_i'},inplace=True)
>>> if 'Druck_i' not in xm.dataFrames['vVBEL_forTestOnly2']:
...     xm.dataFrames['vVBEL_forTestOnly2'].rename(columns={'KNOT~*~~*~PH_i':'Druck_i'},inplace=True) #09 
>>> f = lambda x: round(x,1) if x != None else None  
>>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL_forTestOnly2',filterColList=['OBJTYPE','mx2Idx','L','D','NAME_i','NAME_k','Druck_i','Q'],mapFunc={'Druck_i':f,'Q':f},sortList=['OBJTYPE','NAME_i','Q'],index=False))
OBJTYPE  mx2Idx       L      D  NAME_i  NAME_k  Druck_i     Q
   FWVB       0       0    NaN  V-K002  R-K002      4.0   3.9
   FWVB       4       0    NaN  V-K003  R-K003      3.8   3.7
   FWVB       1       0    NaN  V-K004  R-K004      3.8   6.9
   FWVB       2       0    NaN  V-K005  R-K005      3.8   4.6
   FWVB       3       0    NaN  V-K007  R-K007      3.8   3.9
   ROHR      15    76.4  107.1  R-K000  R-K001      2.0 -23.0
   ROHR      11  195.53  107.1  R-K001  R-K002      2.0 -23.0
   ROHR      12  405.96  107.1  R-K002  R-K003      2.1 -19.1
   ROHR       2   83.55  107.1  R-K003  R-K004      2.3 -15.4
   ROHR       0   88.02  107.1  R-K004  R-K005      2.3  -8.5
   ROHR      13  164.91  107.1  R-K005  R-K006      2.3  -3.9
   ROHR       7  109.77  107.1  R-K006  R-K007      2.3  -3.9
   ROHR       4   73.42  160.3     R-L  R-K000      2.0 -23.0
   ROHR       8    76.4  107.1  V-K000  V-K001      4.1  23.0
   ROHR       5  195.53  107.1  V-K001  V-K002      4.1  23.0
   ROHR       1  405.96  107.1  V-K002  V-K003      4.0  19.1
   ROHR       9   83.55  107.1  V-K003  V-K004      3.8  15.4
   ROHR       3   88.02  107.1  V-K004  V-K005      3.8   8.5
   ROHR      10  164.91  107.1  V-K005  V-K006      3.8   3.9
   ROHR      14  109.77  107.1  V-K006  V-K007      3.8   3.9
   ROHR       6    68.6  160.3     V-L  V-K000      4.1  23.0
>>> # ---
>>> # Clean Up LocalHeatingNetwork Xm and Mx
>>> # ---
>>> xm.delFiles()
>>> mx.delFiles()
>>> # ---
>>> # TinyWDN
>>> # ---
>>> xmlFile=os.path.join(os.path.join(path,testDir),'TinyWDN.XML')
>>> xm=Xm(xmlFile=xmlFile)
>>> # ---
>>> # GPipe
>>> # ---
>>> xmlFile=os.path.join(os.path.join(path,testDir),'GPipe.XML')
>>> xm=Xm(xmlFile=xmlFile)
"""

__version__='90.12.4.23.dev1'

import warnings # 3.6
#...\Anaconda3\lib\site-packages\h5py\__init__.py:36: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated. In future, it will be treated as `np.float64 == np.dtype(float).type`.
#  from ._conv import register_converters as _register_converters
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys

import xml.etree.ElementTree as ET
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

import networkx as nx
import math

vVBEL_edges =['ROHR','VENT','FWVB','FWES','PUMP','KLAP','REGV','PREG','MREG','DPRG','PGRP']
vVBEL_edgesD=[''    ,'DN'  ,''    ,'DN'  ,''    ,'DN'  ,'DN'  ,'DN'  ,'DN'  ,'DN'  ,'']

# list of all RXXX-Nodes but RUES-Nodes
vRXXX_nodes =['RSLW','RMES','RHYS','RLVG','RLSR','RMMA','RADD','RMUL','RDIV','RTOT','RPT1','RINT','RPID','RFKT','RSTN']

# ---
# --- PT3S Imports
# ---
logger = logging.getLogger('PT3S')  
if __name__ == "__main__":
    logger.debug("{0:s}{1:s}".format('in MODULEFILE: __main__ Context:','.')) 
else:
    logger.debug("{0:s}{1:s}{2:s}{3:s}".format('in MODULEFILE: Not __main__ Context: ','__name__: ',__name__," .")) 

try:
    from PT3S import Mx
except ImportError:
    logger.debug("{0:s}{1:s}".format('in MODULEFILE: ImportError: ','from PT3S import Mx - trying import Mx instead ... maybe pip install -e . is active ...')) 
    import Mx

# ---
# --- main Imports
# ---
import argparse
import unittest
import doctest

class renamer():
    def __init__(self):
        self.d = dict()

    def __call__(self, x):
        if x not in self.d:
            self.d[x] = 0
            return x
        else:
            self.d[x] += 1
            return "%s_%d" % (x, self.d[x])


   
class XmError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Xm():
    """SIR 3S modelFile to pandas DataFrames.

    Args:
        * xmlFile (str): SIR 3S modelFile
        * NoH5Read (bool): 
                False (default): 
                    * An existing _and newer h5File will be read _instead of xmlFile.
                    * xmlFile will _not be read (it does even not have to exist)
                True:
                    * An existing h5File will be deleted.
                    * xmlFile will be read.
    
    Attributes:
        * states
            * h5Read: True, if read from H5

        * fileNames
            * xmlFile
            *  constructed from MX during Init and Usage:           
            * h5File: corresponding h5File(name) derived from xmlFile(name)

        * dataFrames
            * dict with pandas DataFrames
            * one pandas DataFrame per SIR 3S Objecttype (i.e. KNOT, ROHR, ...)
            * keys: KNOT, ROHR, ... and vKNOT, vROHR, ...
            * some Views as pandas DataFrames 
                * i.e. vKNOT, vROHR, ...
                * The Views are designed to deal with tedious groundwork.
                * The Views are aggregated somewhat arbitrary.
                * However: Usage of SIR 3S Modeldata is more convenient and efficient with appropriate Views.     
                
        * pXCorZero, pYCorZero
            * min. X aller Knoten der Netzansicht
            * min. Y dito
   
    Raises:
        XmError
    """

    @classmethod
    #def constructNewMultiindexFromCols(cls,df=None,mColNames=['OBJTYPE','pk'],mIdxNames=['OBJTYPE','OBJID']):

    def _xmlRoot2Dfs(cls,root):
        """Parse root into DataFrames.
           
        * Return: 
            * dict with dfs with root-content

        Raises:
            XmError

        >>> XmlString='<data><country name="Liechtenstein"><rank>1</rank><year>2008</year><gdppc>141100</gdppc><neighbor name="Austria" direction="E"/><neighbor name="Switzerland" direction="W"/></country><country name="Singapore"><rank>4</rank><year>2011</year><gdppc>59900</gdppc><neighbor name="Malaysia" direction="N"/></country></data>'
        >>> import xml.etree.ElementTree as ET
        >>> root = ET.fromstring(XmlString)
        >>> import Xm
        >>> dfDct=Xm.Xm._xmlRoot2Dfs(root)
        >>> dfDct.keys()
        dict_keys(['country'])
        >>> dfDct['country']
          rank  year   gdppc neighbor neighborname neighbordirection
        0    1  2008  141100     None  Switzerland                 W
        1    4  2011   59900     None     Malaysia                 N
        >>> xmlAgsnLayout='<Layout><DIAGRAM><PK_DB>5556431006082193278</PK_DB><RK_DB>5556431006082193278</RK_DB><TITLE>HP GLD-WAA</TITLE><TYPE>3</TYPE><LINES_PER_GAP>2</LINES_PER_GAP><AVOID_SLACK_LINE>0</AVOID_SLACK_LINE><IDPH_DIM_TABLE_RA>0</IDPH_DIM_TABLE_RA><IDPH_DIM_TABLE_PRESSURES>2</IDPH_DIM_TABLE_PRESSURES><WATER_PRESSURE_DIMENSION>0</WATER_PRESSURE_DIMENSION><OVERVIEW>0</OVERVIEW><SHOW_NODE_NAMES>1</SHOW_NODE_NAMES><SHOW_KM>1</SHOW_KM><SHOW_DIAMETERS>1</SHOW_DIAMETERS><SHOW_PUMP>1</SHOW_PUMP><SHOW_KLAP>1</SHOW_KLAP><SHOW_REGV>1</SHOW_REGV><SHOW_VENT>0</SHOW_VENT><SHOW_BEVE>1</SHOW_BEVE><SHOW_BEWI>1</SHOW_BEWI><SHOW_OBEH>1</SHOW_OBEH><SHOW_STRO>1</SHOW_STRO><SHOW_WIND>1</SHOW_WIND><SHOW_ACT_P>1</SHOW_ACT_P><SHOW_PIPE_AXIS>1</SHOW_PIPE_AXIS><SHOW_STAT_PRESSURE_LINE>1</SHOW_STAT_PRESSURE_LINE><SHOW_PDAMPF_LINE>1</SHOW_PDAMPF_LINE><SHOW_PNIV_LINE>0</SHOW_PNIV_LINE><SHOW_PMAX_LINE>1</SHOW_PMAX_LINE><SHOW_PMIN_LINE>1</SHOW_PMIN_LINE><SHOW_PEND_LINE>1</SHOW_PEND_LINE><SHOW_MAOP>1</SHOW_MAOP><SHOW_STAT_QM_LINE>0</SHOW_STAT_QM_LINE><SHOW_STAT_TEMP_LINE>0</SHOW_STAT_TEMP_LINE><SHOW_ACT_QM_LINE>1</SHOW_ACT_QM_LINE><SHOW_ACT_TEMP_LINE>0</SHOW_ACT_TEMP_LINE><LINE_STYLE_PIPE_AXIS>1</LINE_STYLE_PIPE_AXIS><LINE_STYLE_STAT_LINE>5</LINE_STYLE_STAT_LINE><LINE_STYLE_STAT_LINE_RL>5</LINE_STYLE_STAT_LINE_RL><LINE_STYLE_PDAMPF>5</LINE_STYLE_PDAMPF><LINE_STYLE_PDAMPF_RL>5</LINE_STYLE_PDAMPF_RL><LINE_STYLE_PNIV>3</LINE_STYLE_PNIV><LINE_STYLE_MAOP>5</LINE_STYLE_MAOP><LINE_STYLE_ACT_P>5</LINE_STYLE_ACT_P><LINE_STYLE_ACT_P_RL>5</LINE_STYLE_ACT_P_RL><LINE_STYLE_MAX>5</LINE_STYLE_MAX><LINE_STYLE_MAX_RL>1</LINE_STYLE_MAX_RL><LINE_STYLE_MIN>2</LINE_STYLE_MIN><LINE_STYLE_MIN_RL>2</LINE_STYLE_MIN_RL><LINE_STYLE_END>5</LINE_STYLE_END><LINE_STYLE_END_RL>5</LINE_STYLE_END_RL><LINE_STYLE_STAT_QM>5</LINE_STYLE_STAT_QM><LINE_STYLE_STAT_QM_RL>5</LINE_STYLE_STAT_QM_RL><LINE_STYLE_STAT_TEMP>5</LINE_STYLE_STAT_TEMP><LINE_STYLE_STAT_TEMP_RL>5</LINE_STYLE_STAT_TEMP_RL><LINE_STYLE_ACT_QM>5</LINE_STYLE_ACT_QM><LINE_STYLE_ACT_QM_RL>4</LINE_STYLE_ACT_QM_RL><LINE_STYLE_ACT_TEMP>4</LINE_STYLE_ACT_TEMP><LINE_STYLE_ACT_TEMP_RL>4</LINE_STYLE_ACT_TEMP_RL><LINE_WIDTH_ACT_P>0,4</LINE_WIDTH_ACT_P><LINE_WIDTH_ACT_P_RL>0,4</LINE_WIDTH_ACT_P_RL><LINE_WIDTH_PIPE_AXIS>0,3</LINE_WIDTH_PIPE_AXIS><LINE_WIDTH_STAT_LINE>0,6</LINE_WIDTH_STAT_LINE><LINE_WIDTH_STAT_LINE_RL>0,6</LINE_WIDTH_STAT_LINE_RL><LINE_WIDTH_PDAMPF>0,2</LINE_WIDTH_PDAMPF><LINE_WIDTH_PDAMPF_RL>0,2</LINE_WIDTH_PDAMPF_RL><LINE_WIDTH_PNIV>0,3</LINE_WIDTH_PNIV><LINE_WIDTH_MAOP>0,1</LINE_WIDTH_MAOP><LINE_WIDTH_MAX>0,1</LINE_WIDTH_MAX><LINE_WIDTH_MAX_RL>0,4</LINE_WIDTH_MAX_RL><LINE_WIDTH_MIN>0,4</LINE_WIDTH_MIN><LINE_WIDTH_MIN_RL>0,4</LINE_WIDTH_MIN_RL><LINE_WIDTH_END>0,8</LINE_WIDTH_END><LINE_WIDTH_END_RL>0,4</LINE_WIDTH_END_RL><LINE_WIDTH_STAT_QM>0,3</LINE_WIDTH_STAT_QM><LINE_WIDTH_STAT_QM_RL>0,3</LINE_WIDTH_STAT_QM_RL><LINE_WIDTH_STAT_TEMP>0,3</LINE_WIDTH_STAT_TEMP><LINE_WIDTH_STAT_TEMP_RL>0,3</LINE_WIDTH_STAT_TEMP_RL><LINE_WIDTH_ACT_QM>0,3</LINE_WIDTH_ACT_QM><LINE_WIDTH_ACT_QM_RL>0,3</LINE_WIDTH_ACT_QM_RL><LINE_WIDTH_ACT_TEMP>0,3</LINE_WIDTH_ACT_TEMP><LINE_WIDTH_ACT_TEMP_RL>0,3</LINE_WIDTH_ACT_TEMP_RL></DIAGRAM><Y_AXIS><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><USE_DEF_SETTINGS>0</USE_DEF_SETTINGS><YMIN>0</YMIN><YMAX>1400</YMAX><INTERVALS>7</INTERVALS><PRECISION>0</PRECISION><USE_DEF_SETTINGS_T>1</USE_DEF_SETTINGS_T><YMIN_T>0</YMIN_T><YMAX_T>150</YMAX_T><PRECISION_T>2</PRECISION_T><USE_DEF_SETTINGS_QM>0</USE_DEF_SETTINGS_QM><YMIN_QM>0</YMIN_QM><YMAX_QM>280</YMAX_QM><PRECISION_QM>0</PRECISION_QM></Y_AXIS><X_AXIS><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM></X_AXIS><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>75,1943462897527</X><Y>249,988250732422</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>GLONS</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>381,908127208481</X><Y>250,977630615234</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>WAHN</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>155,005889281508</X><Y>250,318023681641</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>Dt. Grenze</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>177,762073027091</X><Y>250,647811889648</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>Würselen 1</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>368,716136631331</X><Y>250,977615356445</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>ALD</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>268,687115981817</X><Y>251,146667480469</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>LX1</TEXT_CONTENT></TEXT><TEXT><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><X>330,787173430551</X><Y>250,313110351563</Y><FONT_HEIGHT_MM>4</FONT_HEIGHT_MM><FONT_COLOR>0</FONT_COLOR><FONT_NAME>Arial</FONT_NAME><FONT_BOLD>0</FONT_BOLD><FONT_ITALIC>0</FONT_ITALIC><ANGLE>90</ANGLE><UNDERLINE>0</UNDERLINE><STRIKEOUT>0</STRIKEOUT><TEXT_CONTENT>URX</TEXT_CONTENT></TEXT><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>1</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>0</LINE_COLOR><LINE_COLOR_RL>0</LINE_COLOR_RL><LINE_STYLE>1</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>2</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>16744448</LINE_COLOR><LINE_COLOR_RL>16711680</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>8</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>65280</LINE_COLOR><LINE_COLOR_RL>16711680</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>3</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>9109643</LINE_COLOR><LINE_COLOR_RL>12615680</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>13</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>255</LINE_COLOR><LINE_COLOR_RL>255</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>5</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>33023</LINE_COLOR><LINE_COLOR_RL>16711680</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>1</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>6</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>16711680</LINE_COLOR><LINE_COLOR_RL>16711680</LINE_COLOR_RL><LINE_STYLE>2</LINE_STYLE><LINE_STYLE_RL>2</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>7</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>16744703</LINE_COLOR><LINE_COLOR_RL>32768</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>5</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><LINE_TYPE>12</LINE_TYPE><DRUCKNIV_P>1</DRUCKNIV_P><LINE_COLOR>16744576</LINE_COLOR><LINE_COLOR_RL>32768</LINE_COLOR_RL><LINE_STYLE>5</LINE_STYLE><LINE_STYLE_RL>4</LINE_STYLE_RL></PROFILE_LINE><PROFILE_LINE_COLORS><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><ACT_P>65280</ACT_P><ACT_P_RL>16711680</ACT_P_RL><RA>0</RA><STAT>16744448</STAT><STAT_RL>16711680</STAT_RL><DAMPF>9109643</DAMPF><DAMPF_RL>12615680</DAMPF_RL><DRUCKNIV_P>8421504</DRUCKNIV_P><MAOP>255</MAOP><MIN>16711680</MIN><MIN_RL>16711680</MIN_RL><MAX>33023</MAX><MAX_RL>16711680</MAX_RL><END>16744703</END><END_RL>32768</END_RL><ACT_TEMP>13688896</ACT_TEMP><ACT_TEMP_RL>13422920</ACT_TEMP_RL><ACT_QM>16744576</ACT_QM><ACT_QM_RL>32768</ACT_QM_RL><STAT_TEMP>3107669</STAT_TEMP><STAT_TEMP_RL>2330219</STAT_TEMP_RL><STAT_QM>25600</STAT_QM><STAT_QM_RL>32768</STAT_QM_RL></PROFILE_LINE_COLORS><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-41-GLD-RBT</NODE_NAME><NODE_LABEL>7-41-GLD-RBT</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>4981170782120393923</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-41-NO1</NODE_NAME><NODE_LABEL>7-41-NO1</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5584076006373654663</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-41-ORV</NODE_NAME><NODE_LABEL>7-41-ORV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>4964043826387417801</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-41-WU1-RB</NODE_NAME><NODE_LABEL>7-41-WU1-RB</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>4627214911656931640</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-43-WWV</NODE_NAME><NODE_LABEL>7-43-WWV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5324151752243791071</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-43-KRV</NODE_NAME><NODE_LABEL>7-43-KRV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>4843167124143783966</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-43-LX1-RB</NODE_NAME><NODE_LABEL>7-43-LX1-RB</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5228061767436841487</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-44-RBV</NODE_NAME><NODE_LABEL>7-44-RBV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5648059305057361817</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-44-URX</NODE_NAME><NODE_LABEL>7-44-URX</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5471075831203424054</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-44-NKV</NODE_NAME><NODE_LABEL>7-44-NKV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5259889438821344021</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-44-SPV</NODE_NAME><NODE_LABEL>7-44-SPV</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5548917687498105828</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-44-ALD-RB</NODE_NAME><NODE_LABEL>7-44-ALD-RB</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5395654839887243877</FK_KNOT></FORCE_DISPLAY_NODES><FORCE_DISPLAY_NODES><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><NODE_NAME>7-51-WAA-RBT</NODE_NAME><NODE_LABEL>7-51-WAA-RBT</NODE_LABEL><SHOW_LABEL>1</SHOW_LABEL><LABEL_DIRECTION>1</LABEL_DIRECTION><FK_KNOT>5564393610957983223</FK_KNOT></FORCE_DISPLAY_NODES><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5696816027628008633</FK_KNOT><FK_RSLW>4808829114850961099</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>4774229715715644595</FK_KNOT><FK_RSLW>5468150380408270201</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5013655786080686882</FK_KNOT><FK_RSLW>5732389966512168862</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>4943746274077686975</FK_KNOT><FK_RSLW>5026408578843360078</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5591473557944807466</FK_KNOT><FK_RSLW>5172478010600045505</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5681287721180972670</FK_KNOT><FK_RSLW>4847471410361330583</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>4733201276580834622</FK_KNOT><FK_RSLW>4862900383109045212</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5535372591188407609</FK_KNOT><FK_RSLW>4909877841151045872</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>4688009443988778540</FK_KNOT><FK_RSLW>5592902961516490161</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5027825128788497349</FK_KNOT><FK_RSLW>5374847666199546461</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5570221034797298909</FK_KNOT><FK_RSLW>5650209335377114460</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY><NOMINAL_VALUE_DISPLAY><FK_DIAGRAM>5556431006082193278</FK_DIAGRAM><FK_KNOT>5168063508501641470</FK_KNOT><FK_RSLW>5191618168634067049</FK_RSLW><SHOW_NUMERIC_VALUE>0</SHOW_NUMERIC_VALUE><RL>0</RL><VALUE_TYPE>0</VALUE_TYPE></NOMINAL_VALUE_DISPLAY></Layout>'
        >>> root = ET.fromstring(xmlAgsnLayout)        
        >>> dfDct=Xm.Xm._xmlRoot2Dfs(root)
        >>> dfDct.keys()
        dict_keys(['DIAGRAM', 'Y_AXIS', 'X_AXIS', 'TEXT', 'PROFILE_LINE', 'PROFILE_LINE_COLORS', 'FORCE_DISPLAY_NODES', 'NOMINAL_VALUE_DISPLAY'])
        >>> dfDct['DIAGRAM']
                         PK_DB                RK_DB       TITLE TYPE LINES_PER_GAP AVOID_SLACK_LINE IDPH_DIM_TABLE_RA IDPH_DIM_TABLE_PRESSURES WATER_PRESSURE_DIMENSION OVERVIEW SHOW_NODE_NAMES SHOW_KM SHOW_DIAMETERS SHOW_PUMP SHOW_KLAP SHOW_REGV SHOW_VENT SHOW_BEVE SHOW_BEWI SHOW_OBEH SHOW_STRO SHOW_WIND SHOW_ACT_P SHOW_PIPE_AXIS SHOW_STAT_PRESSURE_LINE SHOW_PDAMPF_LINE SHOW_PNIV_LINE SHOW_PMAX_LINE SHOW_PMIN_LINE SHOW_PEND_LINE SHOW_MAOP SHOW_STAT_QM_LINE SHOW_STAT_TEMP_LINE SHOW_ACT_QM_LINE SHOW_ACT_TEMP_LINE LINE_STYLE_PIPE_AXIS LINE_STYLE_STAT_LINE LINE_STYLE_STAT_LINE_RL LINE_STYLE_PDAMPF LINE_STYLE_PDAMPF_RL LINE_STYLE_PNIV LINE_STYLE_MAOP LINE_STYLE_ACT_P LINE_STYLE_ACT_P_RL LINE_STYLE_MAX LINE_STYLE_MAX_RL LINE_STYLE_MIN LINE_STYLE_MIN_RL LINE_STYLE_END LINE_STYLE_END_RL LINE_STYLE_STAT_QM LINE_STYLE_STAT_QM_RL LINE_STYLE_STAT_TEMP LINE_STYLE_STAT_TEMP_RL LINE_STYLE_ACT_QM LINE_STYLE_ACT_QM_RL LINE_STYLE_ACT_TEMP LINE_STYLE_ACT_TEMP_RL LINE_WIDTH_ACT_P LINE_WIDTH_ACT_P_RL LINE_WIDTH_PIPE_AXIS LINE_WIDTH_STAT_LINE LINE_WIDTH_STAT_LINE_RL LINE_WIDTH_PDAMPF LINE_WIDTH_PDAMPF_RL LINE_WIDTH_PNIV LINE_WIDTH_MAOP LINE_WIDTH_MAX LINE_WIDTH_MAX_RL LINE_WIDTH_MIN LINE_WIDTH_MIN_RL LINE_WIDTH_END LINE_WIDTH_END_RL LINE_WIDTH_STAT_QM LINE_WIDTH_STAT_QM_RL LINE_WIDTH_STAT_TEMP LINE_WIDTH_STAT_TEMP_RL LINE_WIDTH_ACT_QM LINE_WIDTH_ACT_QM_RL LINE_WIDTH_ACT_TEMP LINE_WIDTH_ACT_TEMP_RL
        0  5556431006082193278  5556431006082193278  HP GLD-WAA    3             2                0                 0                        2                        0        0               1       1              1         1         1         1         0         1         1         1         1         1          1              1                       1                1              0              1              1              1         1                 0                   0                1                  0                    1                    5                       5                 5                    5               3               5                5                   5              5                 1              2                 2              5                 5                  5                     5                    5                       5                 5                    4                   4                      4              0,4                 0,4                  0,3                  0,6                     0,6               0,2                  0,2             0,3             0,1            0,1               0,4            0,4               0,4            0,8               0,4                0,3                   0,3                  0,3                     0,3               0,3                  0,3                 0,3                    0,3
        >>> dfDct['NOMINAL_VALUE_DISPLAY']
                     FK_DIAGRAM              FK_KNOT              FK_RSLW SHOW_NUMERIC_VALUE RL VALUE_TYPE
        0   5556431006082193278  5696816027628008633  4808829114850961099                  0  0          0
        1   5556431006082193278  4774229715715644595  5468150380408270201                  0  0          0
        2   5556431006082193278  5013655786080686882  5732389966512168862                  0  0          0
        3   5556431006082193278  4943746274077686975  5026408578843360078                  0  0          0
        4   5556431006082193278  5591473557944807466  5172478010600045505                  0  0          0
        5   5556431006082193278  5681287721180972670  4847471410361330583                  0  0          0
        6   5556431006082193278  4733201276580834622  4862900383109045212                  0  0          0
        7   5556431006082193278  5535372591188407609  4909877841151045872                  0  0          0
        8   5556431006082193278  4688009443988778540  5592902961516490161                  0  0          0
        9   5556431006082193278  5027825128788497349  5374847666199546461                  0  0          0
        10  5556431006082193278  5570221034797298909  5650209335377114460                  0  0          0
        11  5556431006082193278  5168063508501641470  5191618168634067049                  0  0          0
        """

        logStr = "{0:s}.{1:s}: ".format(__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            
            logger.debug("{0:s}parse Xml ...".format(logStr))                     
           
            pm = {c:p for p in root.iter() for c in p}   # parentMap
            logger.debug("{0:s}... done.".format(logStr)) 


            logger.debug("{0:s}Xml to pandas DataFrames ...".format(logStr))      
            tableNames=[]
            oldTableName=None
            for element in root.iter():
                p = None
                if element in pm:
                    p = pm[element]
                if p != root:
                    continue
                actTableName=element.tag
                if actTableName != oldTableName:
                    tableNames.append(actTableName)
                    oldTableName=actTableName                
            dataFrames={}
            for tableName in tableNames:
                all_records = []
                for elementRow in root.iter(tag=tableName):
                    record = {}
                    for elementCol in elementRow:                       
                        record[elementCol.tag] = elementCol.text
                        for key, value in elementCol.attrib.items():
                            record[elementCol.tag+key]=value                            
                    all_records.append(record)
                dataFrames[tableName]=pd.DataFrame(all_records) 
            logger.debug("{0:s}... done.".format(logStr)) 
            logger.debug("{:s}tableNames: {!s:s}.".format(logStr,sorted(dataFrames.keys()))) 
                                           
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return dataFrames


    @classmethod
    def constructNewMultiindexFromCols(cls,df=None,mColNames=['OBJTYPE','pk'],mIdxNames=['OBJTYPE','OBJID']):
            """Constructs a new Multiindex from existing cols and returns the constructed df.

            Args:
                * df: dataFrame without Multiindex              
                * mColNames: list of columns which shall be used as Multiindex; the columns must exist; the columns will be droped
                * mIdxNames: list of names for the indices for the Cols above

            Returns:
                * df with Multiindex       
                * empty DataFrame is returned if an Error occurs
                       
            >>> d = {'OBJTYPE': ['ROHR', 'VENT'], 'pk': [123, 345], 'data': ['abc', 'def']}
            >>> import pandas as pd
            >>> df = pd.DataFrame(data=d)
            >>> from Xm import Xm
            >>> df=Xm.constructNewMultiindexFromCols(df=df,mColNames=['OBJTYPE','pk'],mIdxNames=['OBJTYPE','OBJID'])
            >>> df['data']
            OBJTYPE  OBJID
            ROHR     123      abc
            VENT     345      def
            Name: data, dtype: object
            """

            logStr = "{0:s}.{1:s} (classmethod): ".format(__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
            try:                    
                arrays=[]
                for col in mColNames:
                    arrays.append(df[col].tolist())
                tuples = list(zip(*(arrays)))
                index = pd.MultiIndex.from_tuples(tuples,names=mIdxNames)
                df.drop(mColNames,axis=1,inplace=True)   
                df=pd.DataFrame(df.values,index=index,columns=df.columns)
                df = df.sort_index() # PerformanceWarning: indexing past lexsort depth may impact performance.
            except Exception as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrFinal)    
                df=pd.DataFrame()
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
                return df   

    @classmethod            
    def constructShortestPathFromNodeList(cls,df=None,sourceCol='NAME_i',targetCol='NAME_k',nl=None,weight=None,query=None,fmask=None,filterNonQ0Rows=True):    
            """Returns a DataFrame with Edges (one per row) implementing the shortest Path over NodeList.
    
                Args:
                    * df: DataFrame with (all) Edges (one per row)
                        * adjusting/filtering/constructing (if the corresponding cols are existing) _before using df
                            * L: converted to float before usage here
                            * Q:
                                * non Null Q-rows are filtered (d.h. nur Kanten mit "Wert" bei Q werden berücksichtigt bei der Pfadermittlung)
                                * non Q=0-rows are filtered if filterNonQ0Rows (d.h. nur durchflossene Kanten werden berücksichtigt bei der Pfadermittlung)
                                * constructed:
                                    * QAbs
                                    * QAbsInv (if filterNonQ0Rows)
                    * nl: NodeList
                    * weight: columnName of the weight attribute
            
                        # Der kürzeste Weg zwischen zwei Knoten in einem
                        # zusammenhängenden Graphen ist derjenige, bei dem die
                        # Summe der Gewichte über die durchlaufenen Kanten den
                        # kleinstmöglichen Wert annimmt.

                        # also bei konstantem Kantengewicht die kleinste Kantenanzahl
                        # kürzeste Weglaenge: L als Gewicht
                        # Durchflussstärkster Weg: 1 / Abs(Q) (Flüsse mit 0 oder Kanten ohne Flusswert müssen vorher eliminiert werden um das Kriterium berechnen zu können ...
                        # ... birgt die Gefahr, dass es dann keinen Weg mehr gibt)
                        # Durchflussschwächster Weg: Q

                        * examples for weight: 
                            * L 
                            * Q (QAbs,QAbsInv)
       
                        * query: query to filter vVBEL (to filter Edges) before constructing the Graph 
                        * fmask: function to filter vVBEL (to filter Edges) before constructing the Graph 
                        * query and fmask are used both if not None

                Returns:
                    * df: DataFrame with Edges (one per row) implementing the shortest Path over NodeList
                    * empty DataFrame is returned if an error occurs
                    * columns

                        * OBJTYPE
                        * OBJID
                        * nextNODE
                        * compNr

                            * starts with 1
                            * the number of the connected component
                            * 1 for all edges if all nodes in NodeList are connected

             
                >>> # -q -m 0 -s constructShortestPathFromNodeList -y no -z no -w GPipes -w LocalHeatingNetwork
                >>> xmlFile=ms['GPipes']   
                >>> from Xm import Xm
                >>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)       
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['GL','GR'])                
                  OBJTYPE                OBJID nextNODE  compNr
                0    VENT  5309992331398639768       G1       1
                1    ROHR  5244313507655010738      GKS       1
                2    VENT  5116489323526156845      GKD       1
                3    ROHR  5114681686941855110       G3       1
                4    ROHR  4979507900871287244       G4       1
                5    VENT  5745097345184516675       GR       1
                >>> mx=xm.MxSync()
                >>> xm.MxAdd(mx=mx)    
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['GL','GR'],weight='QAbsInv')  # durchflussstaerkster Weg
                  OBJTYPE                OBJID nextNODE  compNr
                0    VENT  5309992331398639768       G1       1
                1    ROHR  5244313507655010738      GKS       1
                2    VENT  5508684139418025293      GKD       1
                3    ROHR  5114681686941855110       G3       1
                4    ROHR  4979507900871287244       G4       1
                5    VENT  5745097345184516675       GR       1
                >>> ###
                >>> f=lambda row: True if row.NAME_i != 'GKS' else False 
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['GL','GKS','GKD','GR'],fmask=f)  
                  OBJTYPE                OBJID nextNODE  compNr
                0    VENT  5309992331398639768       G1       1
                1    ROHR  5244313507655010738      GKS       1
                2    ROHR  5114681686941855110       G3       2
                3    ROHR  4979507900871287244       G4       2
                4    VENT  5745097345184516675       GR       2
                >>> ###
                >>> xmlFile=ms['LocalHeatingNetwork']                   
                >>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)       
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['V-L','V-K07'])     
                Empty DataFrame
                Columns: []
                Index: []
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['V-L','V-K007'])   
                  OBJTYPE                OBJID nextNODE  compNr
                0    ROHR  4939422678063487923   V-K000       1
                1    ROHR  4984202422877610920   V-K001       1
                2    ROHR  4789218195240364437   V-K002       1
                3    ROHR  4614949065966596185   V-K003       1
                4    ROHR  5037777106796980248   V-K004       1
                5    ROHR  4713733238627697042   V-K005       1
                6    ROHR  5123819811204259837   V-K006       1
                7    ROHR  5620197984230756681   V-K007       1
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['V-K007','R-K007'])   
                  OBJTYPE                OBJID nextNODE  compNr
                0    FWVB  5400405917816384862   R-K007       1
                >>> f=lambda row: True if row.KVR_i=='2' and row.KVR_k=='2' else False 
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['V-K007','R-K007'],fmask=f)  
                Empty DataFrame
                Columns: []
                Index: []
                >>> xm.constructShortestPathFromNodeList(df=xm.getvVBELwithNodeAttributeAdded(),nl=['R-K007','V-K007'],query="OBJTYPE not in ['FWVB','PGRP']")       
                   OBJTYPE                OBJID nextNODE  compNr
                0     ROHR  4945727430885351042   R-K006       1
                1     ROHR  5611703699850694889   R-K005       1
                2     ROHR  4613782368750024999   R-K004       1
                3     ROHR  4637102239750163477   R-K003       1
                4     ROHR  5379365049009065623   R-K002       1
                5     ROHR  5266224553324203132   R-K001       1
                6     ROHR  5647213228462830353   R-K000       1
                7     ROHR  4769996343148550485      R-L       1
                8     VENT  4897018421024717974      R-1       1
                9     PUMP  5481331875203087055       R2       1
                10    KLAP  4801110583764519435       R3       1
                11    FWES  5638756766880678918      V-1       1
                12    VENT  4678923650983295610      V-L       1
                13    ROHR  4939422678063487923   V-K000       1
                14    ROHR  4984202422877610920   V-K001       1
                15    ROHR  4789218195240364437   V-K002       1
                16    ROHR  4614949065966596185   V-K003       1
                17    ROHR  5037777106796980248   V-K004       1
                18    ROHR  4713733238627697042   V-K005       1
                19    ROHR  5123819811204259837   V-K006       1
                20    ROHR  5620197984230756681   V-K007       1
            """

            logStr = "{0:s}.{1:s} (classmethod): ".format(__class__.__name__, sys._getframe().f_code.co_name)
            logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

            try:         
                              
                # Kanten ggf. filtern
                if query != None:                    
                    df=pd.DataFrame(df.query(query).values,columns=df.columns)
                if fmask != None:
                    df=pd.DataFrame(df[df.apply(fmask,axis=1)].values,columns=df.columns)                   
                
                # Graphen konstruieren ###############################################################
               
                # adjusting/constructing some cols and some content before constructing the Graph          
                if 'L' in df.columns.tolist():              
                    df.loc[:,'L']=df['L'].astype('float').values

                if 'Q' in df.columns.tolist():
                    # nur durchflossene Kanten
                    df=df[pd.isnull(df['Q']) == False]
                    if filterNonQ0Rows:
                        df=df[df['Q'] != 0]
                    df.loc[:,'QAbs']=df['Q'].apply(lambda x: math.fabs(x))
                    if filterNonQ0Rows:
                        df.loc[:,'QAbsInv']=df['QAbs'].apply(lambda x: 1/x)

                df.loc[:,'SOURCE_i']=df[sourceCol].values
                df.loc[:,'SOURCE_k']=df[targetCol].values

                G=nx.from_pandas_edgelist(df, source='SOURCE_i', target='SOURCE_k', edge_attr=True,create_using=nx.MultiGraph())

                # Pfad suchen über Knotenliste ######################################################
                # Kantengewicht
                if weight not in df.columns.tolist():   
                    weight=None
    
                dfList=[]
    
                logger.debug("{:s}Knotenliste: {:s}".format(logStr,str(nl))) 

                # Knotenpaare ermitteln
                pathPairs = list(zip(nl[:-1],nl[1:]))
                logger.debug("{:s}Knotenpaare zwischen denen Abschnittsweise ein Pfad gesucht wird: {:s}".format(logStr,str(pathPairs))) 
    
                error=False
                compNr=1
                # Pfad suchen über Knotenpaar #######################################################
                for source,target in pathPairs:
                    logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}".format(logStr,source,target)) 
                
                    # Pfad suchen
                    try:            
                        pathNodes=nx.shortest_path(G,source,target,weight=weight)
                        # Kanten
                        pathEdges = list(zip(pathNodes[:-1],pathNodes[1:]))
                        # ueber alle Kanten
                        for u,v in pathEdges:
                                logger.debug("{:s}          Kante: {:s} {:s}".format(logStr,u,v))
                    
                                dct=G[u][v]
                    
                                idxEdge=0
                                if weight==None:
                                    pass # die 1. Kante bei Multigraphen
                                else:    
                                    edgeData=dct[idxEdge]
                                    w=edgeData[weight]
                                    # die "kleinste" Kante bei Multigraphen                        
                                    for edgeIdx,edgeDct in dct.items():                            
                                        if edgeDct[weight] < w:
                                            idxEdge=edgeIdx
            
                                edgeData=dct[idxEdge] 
                                # benoetigte Attribute der Kante
                                cols=[]
                                for col in ['OBJTYPE','OBJID']:
                                    cols.append(edgeData[col])
                                # weitere Attribute
                                cols.append(v) # nextNODE
                                cols.append(compNr) # compNr
                                df=pd.DataFrame([cols],columns=['OBJTYPE','OBJID','nextNODE','compNr'])
                                dfList.append(df)

                    except ValueError as e:
                        logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}: Fehler ValueError:".format(logStr,source,target)) 
                        logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                        logger.debug(logStrTmp)  
                        error=True
                        break     

                    except KeyError as e:
                        logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}: Fehler KeyError: Ursache nicht ermittelt - z.B. Knoten (?1bei source wird lt. Doku nx.NodeNotFound generiert) nicht gefunden!".format(logStr,source,target)) 
                        logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                        logger.debug(logStrTmp)  
                        error=True
                        break     
                               
                    except nx.NodeNotFound as e:
                        logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}: Fehler nx.NodeNotFound: Knoten (?!source - lt. Doku wird bei source nx.NodeNotFound generiert) nicht gefunden!".format(logStr,source,target)) 
                        logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                        logger.debug(logStrTmp)  
                        error=True
                        break                                              

                    except nx.NetworkXNoPath as e:                        
                        logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}: Fehler nx.NetworkXNoPath:".format(logStr,source,target)) 
                        logger.debug("{:s}     Knotenpaar: source: {:s} target: {:s}: Zwischen dem Knotenpaar konnte kein Pfad ermittelt werden. Weiter mit dem naechsten Paar ... . Aktuelle Komponentenanzahl ist: {:d}.".format(logStr,source,target,compNr)) 
                        compNr+=1
        
                if not error:
                    if len(dfList) > 0:
                        df=pd.concat(dfList).reset_index(drop=True)
                    else: 
                        logger.debug("{:s}Zwischen keinem Knotenpaar konnte ein Pfad ermittelt werden!".format(logStr)) 
                        df=pd.DataFrame()
                else:
                    df=pd.DataFrame()
                                
            except Exception as e:
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrFinal)    
                df=pd.DataFrame()
            finally:
                logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
                return df                   
                              
    def __init__(self,xmlFile,NoH5Read=False):

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            if type(xmlFile) == str:
                self.xmlFile=os.path.realpath(xmlFile)  
                #check if xmlFile exists ...
                if not os.path.exists(self.xmlFile) and NoH5Read: 
                    logStrFinal="{0:s}{1:s}: Not existing!".format(logStr,xmlFile)                                 
                    raise XmError(logStrFinal)  
            else:
                logStrFinal="{0:s}{1!s}: Not of type str!".format(logStr,xmlFile)                                 
                raise XmError(logStrFinal)     
                              
            #Determine corresponding .h5 Filename
            (wD,fileName)=os.path.split(self.xmlFile)
            (base,ext)=os.path.splitext(fileName)
            self.h5File=wD+os.path.sep+base+'.'+'h5'

            if NoH5Read: 
                if os.path.exists(self.h5File):  
                    if os.access(self.h5File,os.W_OK):
                        pass
                    else:
                        logger.debug("{0:s}{1:s}: not os.W_OK ... sleep(1) ...".format(logStr,self.h5File))     
                        time.sleep(1)
                    logger.debug("{0:s}{1:s}: Delete ...".format(logStr,self.h5File))     
                    try:
                        os.remove(self.h5File)
                    except PermissionError:
                        logger.debug("{0:s}{1:s}: PermissionError ... sleep(1) ...".format(logStr,self.h5File))     
                        time.sleep(1)
                        os.remove(self.h5File)

            if os.path.exists(self.xmlFile):  
                xmlFileTime=os.path.getmtime(self.xmlFile) 
            else:
                xmlFileTime=0

            #check if h5File exists 
            if os.path.exists(self.h5File):  
                #check if h5File is newer
                h5FileTime=os.path.getmtime(self.h5File)
                if(h5FileTime>xmlFileTime):
                    logger.debug("{0:s}h5File {1:s} exists and is newer than an (existing) xmlFile {2:s}:".format(logStr,self.h5File,self.xmlFile))     
                    logger.debug("{0:s}The h5File is read (instead) of the xmlFile.".format(logStr))   
                    self.h5Read=True  
                else:
                    logger.debug("{0:s}h5File {1:s} exists parallel but is NOT newer than xmlFile {2:s}.".format(logStr,self.h5File,self.xmlFile))     
                    self.h5Read=False
            else:
                self.h5Read=False               
            
            if not self.h5Read:                
                self._xmlRead()
            else:
                self.FromH5(h5File=self.h5File)
                          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def delFiles(self): 
        """Deletes Files constructed by XM during Init and Usage.
        """
        
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:           
            if os.path.exists(self.h5File):                        
               os.remove(self.h5File)    
               logger.debug("{0:s} File {1:s} deleted.".format(logStr,self.h5File))            
        except XmError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def _xmlRead(self):
        """Reads the SIR 3S modelFile.
           
        * Performs fixes and basic conversions inplace the dataFrames read from modelFile: _convertAndFix()
        * Creates some Views: _vXXXX()

        Raises:
            XmError

        >>> # -q -m 0 -s xmlRead -t nothing -y yes -z no -w OneLPipe         
        >>> xmlFile=ms['OneLPipe']   
        >>> import Xm
        >>> xm=Xm.Xm(xmlFile)       
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            
            logger.debug("{0:s}xmlFile: {1:s} parse Xml ...".format(logStr,self.xmlFile))                     
            tree = ET.parse(self.xmlFile) # ElementTree                 
            root = tree.getroot()  # Element

            self.dataFrames=Xm._xmlRoot2Dfs(root)

            #fixes and conversions
            self._convertAndFix()

            #Views
            self._vXXXX()
                                            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def FromH5(self,h5File=None):
        """Reads all dataFrames stored in h5File into self.DataFrames.
        
        Args:
            h5File: 
                * (str): the h5File(name) to be read
                * (None): self.h5File will be read
            
          
        * Reads all keys.
        * Existing keys in self.dataFrames are overwritten.

        Note that after .FromH5() the content of self.dataFrames may differ from the content given by an existing self.xmlFile.

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        if h5File == None:
            h5File=self.h5File

        #Check if h5File exists
        if not os.path.exists(h5File):    
            logStrFinal="{0:s}{1:s}: Not Existing!".format(logStr,h5File)                                 
            raise XmError(logStrFinal)           
  
        try:
            self.dataFrames={}   
            with pd.HDFStore(h5File) as h5Store:
                h5Keys=sorted(h5Store.keys())
                for h5Key in h5Keys:
                    match=re.search('(/)(\w+$)',h5Key)
                    key=match.group(2)
                    logger.debug("{0:s}{1:s}: Reading h5Key {2:s} to tableName {3:s}.".format(logStr,h5File,h5Key,key)) 
                    self.dataFrames[key]=h5Store[h5Key]
                

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                                            
      
        finally:
            h5Store.close()
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def ToH5(self,h5File=None):
        """Stores self.dataFrames to h5File.

        Args:
            h5File: 
                * (str): the h5File(name) to be used
                * (None): self.h5File will be used

        * Stores all keys.
        * Existing keys in h5File are overwritten.       
        
        Raises:
            XmError         
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            if h5File == None:
                h5File=self.h5File

            #Delete .h5 File if exists
            if os.path.exists(h5File):                        
                logger.debug("{0:s}{1:s}: Delete ...".format(logStr,h5File))     
                os.remove(h5File)

            #Determine .h5 BaseKey

            relPath2XmlromCurDir=os.path.normpath(os.path.relpath(os.path.normpath(self.xmlFile),start=os.path.normpath(os.path.curdir))) # ..\..\..\..\..\3S\Modelle\....XML
            #print(repr(relPath2XmlromCurDir)) # '..\\..\\..\\..\\..\\3S\\Modelle\\....XML'
            h5KeySep='/'
            h5KeyCharForDot='_'
            h5KeyCharForMinus='_'
            relPath2XmlromCurDirH5BaseKey=re.sub('\.',h5KeyCharForDot,re.sub(r'\\',h5KeySep,re.sub('-',h5KeyCharForMinus,re.sub('.xml','',relPath2XmlromCurDir,flags=re.IGNORECASE))))
            #__/__/__/__/__/3S/Modelle/...

            warnings.filterwarnings('ignore',category=pd.io.pytables.PerformanceWarning) #your performance may suffer as PyTables will pickle object types that it cannot map directly to c-types 
            warnings.filterwarnings('ignore',category=tables.exceptions.NaturalNameWarning) #\lib\site-packages\tables\path.py:100: NaturalNameWarning: object name is not a valid Python identifier: '3S'; it does not match the pattern ``^[a-zA-Z_][a-zA-Z0-9_]*$``; you will not be able to use natural naming to access this object; using ``getattr()`` will still work, though)
                         
            #Write .h5 File
            logger.debug("{0:s}pd.HDFStore({1:s}) ...".format(logStr,h5File))                 
            with pd.HDFStore(h5File) as h5Store: 
                #for tableName,table in self.dataFrames.items():
                for tableName in sorted(self.dataFrames.keys()):
                    table=self.dataFrames[tableName]
                    h5Key=relPath2XmlromCurDirH5BaseKey+h5KeySep+tableName      
                    logger.debug("{0:s}{1:s}: Writing DataFrame {2:s} with h5Key={3:s}".format(logStr,h5File,tableName,h5Key))     
                    try:
                        h5Store.put(h5Key,table)#,format='table')         
                    except Exception as e:
                        logger.error("{0:s}{1:s}: Writing DataFrame {2:s} with h5Key={3:s} FAILED!".format(logStr,h5File,tableName,h5Key))    
                        raise e
                        

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                                           
            
        finally:
            h5Store.close()
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def _convertAndFix(self):
        """Performs fixes and basic conversions inplace the dataFrames read from self.xmlFile.

        * Fixes and conversions here are integrity-oriented.
        * Usage-oriented conversions (i.e. pd.to_numeric and base64.b64decode) - if any - are done in the ._vXXXX-methods.
        * Vorgehen in den Sichten: Anwendungs-orientierte Konvertierung von pandas Object in ein spezifisches Format nur wenn sinnvoll bzw. erforderlich

        Conversions: 
            * , > . (converted in: SWVT_ROWT, LFKT_ROWT, QVAR_ROWT, PVAR_ROWT)

        Fixes:
            * No SWVT_ROWT, LFKT_ROWT, QVAR_ROWT, PVAR_ROWT?!
                *  * SWVT, LFKT, QVAR, PVAR are constructed to
            * 1st Time without Value?! (fixed in: SWVT_ROWT, LFKT_ROWT, QVAR_ROWT, PVAR_ROWT)       
            * Template Node(s)?!
            * in new Models constructed from SIR 3S 
               * not all Objectattributes are written?!   
                    * KMOT/TE
                    * FWVB/LFK
                    * LTGR/BESCHREIBUNG
                    * DTRO_ROWD
                        * AUSFALLZEIT
                        * PN
                        * REHABILITATION
                        * REPARATUR
                        * WSTEIG, WTIEFE
                    * RSLW
                        * WMIN
                        * WMAX

                * not all Objecttypes are written?!
                    * CONT    
            * Models with no PZONs ...
            * Models with no GMIXs ...
            * Models with no STOFs ...
            * empty WBLZ OBJS-BLOBs
            * empty LAYR OBJS-BLOBs

            * BESCHREIBUNG nicht in RLVG?...
            * BESCHREIBUNG nicht in RADD?...
        Raises:
            XmError                                       
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            
            if 'SWVT_ROWT' not in self.dataFrames:
                self.dataFrames['SWVT_ROWT']=self._constructEmptyDf(['pk','fk','ZEIT','W'])
                self.dataFrames['SWVT']=self._constructEmptyDf(['pk','NAME','BESCHREIBUNG','INTPOL','ZEITOPTION'])

            if not self.dataFrames['SWVT_ROWT'].empty:
                self.dataFrames['SWVT_ROWT'].ZEIT=self.dataFrames['SWVT_ROWT'].ZEIT.str.replace(',', '.')
                self.dataFrames['SWVT_ROWT'].W=self.dataFrames['SWVT_ROWT'].W.str.replace(',', '.')

            if 'LFKT_ROWT' not in self.dataFrames:
                self.dataFrames['LFKT_ROWT']=self._constructEmptyDf(['pk','fk','ZEIT','LF'])     
                self.dataFrames['LFKT']=self._constructEmptyDf(['pk','NAME','BESCHREIBUNG','INTPOL','ZEITOPTION'])

            if not self.dataFrames['LFKT_ROWT'].empty:
                self.dataFrames['LFKT_ROWT'].ZEIT=self.dataFrames['LFKT_ROWT'].ZEIT.str.replace(',', '.')
                self.dataFrames['LFKT_ROWT'].LF=self.dataFrames['LFKT_ROWT'].LF.str.replace(',', '.')

            if 'QVAR_ROWT' not in self.dataFrames:
                self.dataFrames['QVAR_ROWT']=self._constructEmptyDf(['pk','fk','ZEIT','QM'])    
                self.dataFrames['QVAR']=self._constructEmptyDf(['pk','NAME','BESCHREIBUNG','INTPOL','ZEITOPTION'])

            if not self.dataFrames['QVAR_ROWT'].empty:
                self.dataFrames['QVAR_ROWT'].ZEIT=self.dataFrames['QVAR_ROWT'].ZEIT.str.replace(',', '.')
                self.dataFrames['QVAR_ROWT'].QM=self.dataFrames['QVAR_ROWT'].QM.str.replace(',', '.')

            if 'PVAR_ROWT' not in self.dataFrames:
                self.dataFrames['PVAR_ROWT']=self._constructEmptyDf(['pk','fk','ZEIT','PH'])     
                self.dataFrames['PVAR']=self._constructEmptyDf(['pk','NAME','BESCHREIBUNG','INTPOL','ZEITOPTION'])

            if not self.dataFrames['PVAR_ROWT'].empty:
                self.dataFrames['PVAR_ROWT'].ZEIT=self.dataFrames['PVAR_ROWT'].ZEIT.str.replace(',', '.')
                self.dataFrames['PVAR_ROWT'].PH=self.dataFrames['PVAR_ROWT'].PH.str.replace(',', '.')

            # 1st Time without Value?!
            self.dataFrames['SWVT_ROWT']=self.dataFrames['SWVT_ROWT'].fillna(0) 
            self.dataFrames['LFKT_ROWT']=self.dataFrames['LFKT_ROWT'].fillna(0) 
            self.dataFrames['QVAR_ROWT']=self.dataFrames['QVAR_ROWT'].fillna(0) 
            self.dataFrames['PVAR_ROWT']=self.dataFrames['PVAR_ROWT'].fillna(0) 
                        
            # Template Node
            self.dataFrames['KNOT']=self.dataFrames['KNOT'][self.dataFrames['KNOT'].NAME.fillna('').astype(str).isin(['TemplateNode','TemplNode-VL','TemplNode-RL'])==False]            
            
            # TE only in Heatingmodels ? ...
            try:
                isinstance(self.dataFrames['KNOT_BZ']['TE'],pd.core.series.Series)
            except:
                logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['KNOT_BZ']['TE']",'TE only in Heatingmodels?!')) 
                self.dataFrames['KNOT_BZ']['TE']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     

            # FWVB LFK
            if 'FWVB' in self.dataFrames:
                try:
                    isinstance(self.dataFrames['FWVB']['LFK'],pd.core.series.Series)
                except:
                    logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['FWVB']['LFK']",'LFK not set?!')) 
                    self.dataFrames['FWVB']['LFK']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.
                self.dataFrames['FWVB']['LFK'].fillna(value=1,inplace=True)

            # Models with only one Standard LTGR ...
            try:
                isinstance(self.dataFrames['LTGR']['BESCHREIBUNG'],pd.core.series.Series)
            except:
                self.dataFrames['LTGR']['BESCHREIBUNG']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.    

            # Models with old DTRO_ROWD                 
            for attrib in ['AUSFALLZEIT','PN','REHABILITATION','REPARATUR','WSTEIG','WTIEFE']:
                 try:
                    isinstance(self.dataFrames['DTRO_ROWD'][attrib],pd.core.series.Series)
                 except:
                    self.dataFrames['DTRO_ROWD'][attrib]=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.   

            # Models with no CONTs ...
            try:
                isinstance(self.dataFrames['CONT']['LFDNR'],pd.core.series.Series)
            except:
                self.dataFrames['CONT']['LFDNR']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.    
            try:
                isinstance(self.dataFrames['CONT']['GRAF'],pd.core.series.Series)
            except:
                self.dataFrames['CONT']['GRAF']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.       

            # Models with no PZONs ...
            if not 'PZON' in self.dataFrames: 
                self.dataFrames['PZON']=pd.DataFrame()       
                self.dataFrames['PZON']['NAME']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                self.dataFrames['PZON']['pk']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  

            # Models with no STOFs ...
            if not 'STOF' in self.dataFrames: 
                #                                                            BESCHREIBUNG
                self.dataFrames['STOF']=self._constructEmptyDf(['pk','NAME','BESCHREIBUNG']) 

            # Models with no GMIXs ...
            if not 'GMIX' in self.dataFrames: 
                self.dataFrames['GMIX']=self._constructEmptyDf(['pk','NAME']) 
                   
            # empty WBLZ OBJS-BLOBs
            if 'WBLZ' in self.dataFrames.keys():
                self.dataFrames['WBLZ']=self.dataFrames['WBLZ'][pd.notnull(self.dataFrames['WBLZ']['OBJS'])]      
            # empty LAYR OBJS-BLOBs
            if 'LAYR' in self.dataFrames.keys():
                if 'OBJS' in self.dataFrames['LAYR'].columns:
                    self.dataFrames['LAYR']=self.dataFrames['LAYR'][pd.notnull(self.dataFrames['LAYR']['OBJS'])]     

            # BESCHREIBUNG nicht in RLVG?...
            if 'RLVG'  in self.dataFrames:                    
                try:
                    isinstance(self.dataFrames['RLVG']['BESCHREIBUNG'],pd.core.series.Series)
                except:
                    logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['RLVG']['BESCHREIBUNG']",'BESCHREIBUNG nicht in RLVG?...')) 
                    self.dataFrames['RLVG']['BESCHREIBUNG']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     

            # BESCHREIBUNG nicht in RADD?...
            if 'RADD' in self.dataFrames:         
                try:
                    isinstance(self.dataFrames['RADD']['BESCHREIBUNG'],pd.core.series.Series)
                except:
                    logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['RADD']['BESCHREIBUNG']",'BESCHREIBUNG nicht in RADD?...')) 
                    self.dataFrames['RADD']['BESCHREIBUNG']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  

            # RSLW: WMIN/WMAX nicht immer vorhanden? ...
            if 'RSLW' in self.dataFrames:               
                try:
                    isinstance(self.dataFrames['RSLW']['WMIN'],pd.core.series.Series)
                except:
                    logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['RSLW']['WMIN']",'WMIN nicht vorhanden?!')) 
                    self.dataFrames['RSLW']['WMIN']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.           
                try:
                    isinstance(self.dataFrames['RSLW']['WMAX'],pd.core.series.Series)
                except:
                    logger.debug("{:s}Error: {:s}: {:s}.".format(logStr,"self.dataFrames['RSLW']['WMAX']",'WMAX nicht vorhanden?!')) 
                    self.dataFrames['RSLW']['WMAX']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.   
                 
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)             
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def _constructEmptyDf(self,cols=['DummyCol1','DummyCol2']):
        """Constructs an empty df with cols.

        Args:
            * cols: list of colNames

        Returns:
            df: constructed df

        Raises:
            XmError                                       
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            df=pd.DataFrame()       
            for col in cols:
                df[col]=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.
             
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)             
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     
            return df

    def getWDirModelDirModelName(self):
        """ Returns (wDir,modelDir,modelName,mx1FileName).

        Returns:            
            (wDir,modelDir,modelName,mx1FileName)

        wDir
            If wDir as given literally in .xmlFile is not a valid Dir 
            or such a wDir relative to .xmlFile-Path exists the wDir relative is returned. 

        mx1FileName
            mx1FileName is assumed to be: .:\...\WD...\B...\V...\BZ...\M... .MX1
            If not existing: .*.MX1 (first match is returned)
            If a suitable mx1File is not existing an INFO-Message is generated.
           
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        result=tuple(['','',''])
        
        try:    
            # wDir literally from Model 
            t=self.dataFrames['SYSTEMKONFIG']
            WDirFromModel=t[t['ID'].astype(int)==1]['WERT'].iloc[0] 

            # such a wDir relative to Modelfile-Path
            head,wDirTail=os.path.split(os.path.abspath(WDirFromModel))
            xmlDirHead,tail=os.path.split(os.path.abspath(self.xmlFile))
            WDirFromModelFilePath=os.path.join(xmlDirHead,wDirTail)
            
            if not os.path.isdir(WDirFromModel) and not os.path.isdir(WDirFromModelFilePath):   
                    logStrFinal="{:s}wDirs {:s} and {:s} both not existing!".format(logStr,WDirFromModel,WDirFromModelFilePath)                          
                    logger.error(logStrFinal)       
                    raise XmError(logStrFinal)  
            elif os.path.isdir(WDirFromModel) and not os.path.isdir(WDirFromModelFilePath):   
                    logStr="{:s}Only wDir {:s} exists.".format(logStr,WDirFromModel)                          
                    logger.debug(logStr)       
                    wDir=WDirFromModel
            elif not os.path.isdir(WDirFromModel) and os.path.isdir(WDirFromModelFilePath):   
                    logStr="{:s}Only wDir {:s} exists.".format(logStr,WDirFromModelFilePath)                          
                    logger.debug(logStr)       
                    wDir=WDirFromModelFilePath
            else: # beide Verzeichnisse existieren ....   
                    if WDirFromModel == WDirFromModelFilePath:
                        pass # der Normalfall
                    else:
                        logStr="{:s}wDirs {:s} and {:s} both are existing.".format(logStr,WDirFromModel,WDirFromModelFilePath)      
                        logger.debug(logStr)  
                        logStr="{:s}wDir {:s} is used.".format(logStr,WDirFromModelFilePath)   
                        logger.debug(logStr)       
                    wDir=WDirFromModelFilePath

            t=self.dataFrames['DATENEBENE']
            B=t[t['TYP'].str.contains('BASIS')]['ORDNERNAME'].iloc[0] 
            V=t[t['TYP'].str.contains('VARIANTE')]['ORDNERNAME'].iloc[0]
            BZ=t[t['TYP'].str.contains('BZ')]['ORDNERNAME'].iloc[0]
            modelDir=os.path.join(B,os.path.join(V,BZ))

            t=self.dataFrames['MODELL']
            modelName=t['BEZEICHNER'].iloc[0]          
  
            mx1FilenamePre=os.path.join(wDir,os.path.join(modelDir,modelName))     
            mx1Filename=mx1FilenamePre+'.MX1' 
            if not os.path.isfile(mx1Filename):                                          
                logger.debug("{:s}This mx1FileName: {:s} does not exist. Trying .*.MX1 ...".format(logStr,mx1Filename))
                mx1FileNames=glob.glob(mx1FilenamePre+'.*'+'.MX1')
                if len(mx1FileNames)==0:
                    logger.info("{:s}Those mx1FileName(s): {:s} also do not exist?!".format(logStr,mx1FilenamePre+'.*'+'.MX1'))  
                else:
                    mx1Filename=mx1FileNames[0]

            result=tuple([wDir,modelDir,modelName,mx1Filename])

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.error(logStrFinal)       
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return result 

    def getVersion(self,type='BASIS'):
        """ Returns VERSION-String i.e. Sir3S-90-10.

        Args:
            * type: BASIS or VARIANTE or BZ; the DATENEBENEn-TYPe from which the VERSION-String is requested 
     
        Returns:
            * VERSION-String i.e. Sir3S-90-10; Sir3S-90-09 is returned wenn der Versionsstring nicht ermittelt werden konnte
        Raises:
            XmError

        >>> xm=xms['OneLPipe']
        >>> vStr=xm.getVersion()
        >>> import re
        >>> m=re.search('Sir(?P<Db3s>[DBdb3Ss]{2})-(?P<Major>\d+)-(?P<Minor>\d+)$',vStr) # i.e. Sir3S-90-10
        >>> int(m.group('Major')[0])
        9
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
                
        try:               
            vStr=None
            t=self.dataFrames['DATENEBENE']
            if 'VERSION' not in t.columns.tolist():
                logger.debug("{0:s}Spalte VERSION not in Tabelle DATENEBENE - vStr set to Sir3S-90-09".format(logStr)) 
                vStr='Sir3S-90-09'
            else:           
                tType=t[t['TYP'].str.contains(type)]
                vStr=tType['VERSION'].iloc[0] 
                if vStr == None or str(vStr) == 'nan' or str(vStr) == 'NaN':
                    logger.debug("{0:s}vStr is None (type={1:s}) - vStr set to Sir3S-90-09".format(logStr,type)) 
                    vStr='Sir3S-90-09'                    
            logger.debug("{0:s}vStr: {1:s} (type={2:s})".format(logStr,str(vStr),type)) 
                       
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.error(logStrFinal)       
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vStr

    def _getvXXXXAsOneString(self,vXXXX=None,start=0,end=-1,dropColList=None,filterColList=None,mapFunc={},sortList=None,ascending=True,roundDct=None,fmtFunc={},index=True,header=True):
        """Returns vXXXX-Content as one String (for Doctest-Purposes).

        Args:
            * vXXXX: df=self.dataFrames[vXXXX]
            * start
            * end
            * dropColList
            * filterColList
            * mapFunc: col:func: df[col].map(func)
            * sortList
            * ascending
            * roundDct
            * fmtFunc: col:func: passed to df.to_string(formatters=fmtFunc, ...)
            * index
            * header

        Returns:
            * df.to_string(formatters=fmtFunc,index=index,header=header)                
           
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 

        dfContentAsOneString=None

        df=self.dataFrames[vXXXX]

        # select rows
        if end == -1:
            df=df[start:]
        else:
            df=df[start:end]

        # select cols        
        colList=df.columns.values.tolist()
        if isinstance(dropColList,list):
            colListOut=[col for col in colList if col not in dropColList]
        else:
            colListOut=colList
        df=df.loc[:,colListOut]
        if filterColList!=None:
            df=df.filter(items=filterColList)

        # map cols
        for col,func in mapFunc.items():          
            if col not in df.columns:
                pass
            else:
                df[col]=df[col].map(func)

        # sort 
        if isinstance(sortList,list):
            df=df.sort_values(sortList,ascending=ascending)    

        # round 
        if isinstance(roundDct,dict):
            df=df.round(roundDct)    

        try:                 
            dfContentAsOneString=df.to_string(formatters=fmtFunc,index=index,header=header,justify='right')                                                                            
        except MxError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)            
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     
            return dfContentAsOneString

    def _vXXXX(self):
        """Creates all Views.

        Views created:
            * BLOB-Data 
                * vLAYR
                * vWBLZ
                * vAGSN u. vAGSN_raw
            * Timeseries
                * vLFKT
                * vQVAR
                * vPVAR
                * vSWVT
            * Signalmodel               
                * vRUES: RUES-Nodes of R
                * vRXXX: Nodes of R but RUES-Nodes                          
                * vREdges: die Kanten des Knoten-Kanten-Signalmodells

                * vRSLW 
                * vRART
                * vRSTN                           
            * Hydraulicmodel
                * Nodes
                    * vVKNO: CONT-Nodes (also called Block-Nodes)
                    * vKNOT
                    * pXCorZero, pYCorZero
                * Edges
                    * vROHR: Pipes
                    * vFWVB: Housestations (district heating)    
                * all Edges (all; implemented Edges see vVBEL_edges)
                    * vVBEL
            * Annotations
                * vNRCV
                * vGTXT                       
                    
        Raises:
            XmError                      
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 

            #BLOB-Data
            self.dataFrames['vLAYR']=self._vLAYR()
            self.dataFrames['vWBLZ']=self._vWBLZ()            

            #timeseries
            self.dataFrames['vLFKT']=self._vLFKT()   
            self.dataFrames['vQVAR']=self._vQVAR()           
            self.dataFrames['vPVAR']=self._vPVAR()           
            self.dataFrames['vSWVT']=self._vSWVT()

            #signalmodel            
            self.dataFrames['vRUES']=self._vRUES() # RUES-Nodes
            self.dataFrames['vRXXX']=self._vRXXX() # all RXXX-Nodes but RUES-Nodes
            self.dataFrames['vREdges']=self._vREdges()            
            
            self.dataFrames['vRSLW']=self._vRSLW(vSWVT=self.dataFrames['vSWVT'])             
            
            #nodes    
            self.dataFrames['vVKNO']=self._vVKNO()
            self.dataFrames['vKNOT']=self._vKNOT(
                 vVKNO=self.dataFrames['vVKNO']
                ,vQVAR=self.dataFrames['vQVAR']
                ,vPVAR=self.dataFrames['vPVAR']
                ,vLFKT=self.dataFrames['vLFKT']
                )
            #
            vKNOT=self.dataFrames['vKNOT']
            self.pXCorZero=vKNOT[
                (vKNOT['CONT_ID'].astype(int)==1001) 
                & 
                (vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element') == False)]['XKOR'].astype(np.double).min()

            self.pYCorZero=vKNOT[
                (vKNOT['CONT_ID'].astype(int)==1001) 
                & (vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element') == False)]['YKOR'].astype(np.double).min()

            #special edges
            self.dataFrames['vROHR']=self._vROHR(vKNOT=self.dataFrames['vKNOT'])
            self.dataFrames['vFWVB']=self._vFWVB(vKNOT=self.dataFrames['vKNOT']
                                            ,vLFKT=self.dataFrames['vLFKT']
                                            ,vWBLZ=self.dataFrames['vWBLZ']
                                            )                                             

            #all edges
            self.dataFrames['vVBEL']=self._vVBEL(vKNOT=self.dataFrames['vKNOT'])

            self.dataFrames['vAGSN']=self._vAGSN()
            self.dataFrames['vAGSN_raw']=self.dataFrames['vAGSN']

            #signalmodel cont.       
            self.dataFrames['vRART']=self._vRART()       
            self.dataFrames['vRSTN']=self._vRSTN() 

            #annotations
            self.dataFrames['vNRCV']=self._vNRCV()            
            self.dataFrames['vGTXT']=self._vGTXT()

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     

    def _vLAYR(self):
        """One row per LAYR and OBJ.
        
        Returns:
            columns           
                LAYR (also called 'Group')
                    * LFDNR
                    * NAME

                    from SIR 3S OBJ BLOB collection:
                        * OBJTYPE: type (i.e.ROHR) of a LAYR OBJ
                        * OBJID: pk (or tk?!) of a LAYR OBJ      
                                 
                LAYR IDs
                    * pk, tk         

                ANNOTATION
                    * nrObjInGroup: Element Nr. in LAYR (LFDNR) - should be 1 otherwise the same OBJ occurs in the same LAYR multiple times               
                    * nrObjtypeInGroup: Element Nr. of OBJTYPE in LAYR (LFDNR)     
                    
                SORTING
                    LFDNR,NAME,OBJTYPE,OBJID       
                    
        Raises:
            XmError                     
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vLAYR=None
            vLAYR=self._OBJS('LAYR')

            vLAYR=vLAYR[[
            'LFDNR'
            ,'NAME'
            #from LAYR's OBJS: 
            ,'OBJTYPE' #type (i.e.ROHR) of a LAYR OBJ
            ,'OBJID' #pk (or tk?!) of a LAYR OBJ          
            #IDs (of the LAYR)
            ,'pk','tk'
            ]]

            vLAYR.sort_values(['LFDNR','NAME','OBJTYPE','OBJID'],ascending=True,inplace=True)

            #reindex:
            vLAYR=pd.DataFrame(vLAYR.values,columns=vLAYR.columns)

            #Element Nr.  ... in Gruppe
            vLAYR=vLAYR.assign(nrObjInGroup=vLAYR.sort_values(['LFDNR','OBJTYPE','OBJID']).groupby(['LFDNR','OBJID']).cumcount()+1)
            #Element Nr. ... vom Typ x in Gruppe 
            vLAYR=vLAYR.assign(nrObjtypeInGroup=vLAYR.sort_values(['LFDNR','OBJTYPE','OBJID']).groupby(['LFDNR','OBJTYPE']).cumcount()+1)
          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vLAYR,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vLAYR=pd.DataFrame()                   
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vLAYR

    def _vWBLZ(self):
        """One row per WBLZ and OBJ.

        Returns:
            columns
                WBLZ
                    * AKTIV            
                    * BESCHREIBUNG
                    * IDIM
                    * NAME

                    from SIR 3S OBJ BLOB collection:
                        * OBJTYPE: type (always KNOT?!) 
                        * OBJID: pk (or tk?!) 
                      
                WBLZ IDs
                    * pk   
                    
                SORTING
                    NAME,pk                                  
                    
        Raises:
            XmError                                
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vWBLZ=None
            vWBLZ=self._OBJS('WBLZ')
          
            vWBLZ=vWBLZ[[
             'AKTIV'            
            ,'BESCHREIBUNG'
            ,'IDIM'
            ,'NAME'
            #from WBLZ's OBJS: 
            ,'OBJTYPE' #type (i.e. KNOT) of a WBLZ OBJ
            ,'OBJID' #pk (or tk?!) of a WBLZ OBJ          
            #IDs (of the WBLZ)
            ,'pk'
            ]]
            vWBLZ.sort_values(['NAME','pk'],ascending=True,inplace=True)
            #reindex:
            vWBLZ=pd.DataFrame(vWBLZ.values,columns=vWBLZ.columns)
          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vWBLZ,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vWBLZ=pd.DataFrame()   
                vWBLZ['AKTIV']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['BESCHREIBUNG']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['IDIM']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['NAME']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['OBJID']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['OBJTYPE']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.  
                vWBLZ['pk']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     
                                                               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vWBLZ

    def _vAGSN(self):
        """One row per AGSN and OBJ.

        Returns:
            columns
                AGSN
                    * LFDNR 
                    * NAME
                    * AKTIV
                   
                    * from SIR 3S OBJ BLOB collection:

                        * OBJTYPE: type (i.e.ROHR) 
                        * OBJID: pk (or tk?!)   
                                 
                AGSN IDs
                    * pk, tk   

                Sequence
                    * Model
                        * therefore nrObjIdInAgsn (see ANNOTATION below) should be the realwolrd sequence
                        
                ANNOTATION
                    * nrObjIdInAgsn: lfd.Nr. (in Schnittreihenfolge) Obj. (der Kante) in AGSN (AGSN is defined by LFDNR not by NAME)                      
                    * nrObjIdTypeInAgsn: should be 1 determined by raw data
                        * nrObjIdTypeInAgsn>1 - if any - are not part of the view
                        * the 1st occurance is in the view 
                    * Layer
                        0=undef
                        bei Netztyp 21: 1=VL, 2=RL, 0=undef 
                        wenn keine BN-Trennzeile gefunden wird, wird VL angenommen und gesetzt
                        die BN-Trennzeile wird dem VL (1) zugerechnet
                    * nextNODE: node which is connected by the edge
                        * the cut-direction is defined (per cut and comp) by edge-sequence
                        * the cut node-sequence ist the (longest shortest) path between the nodes of the 1st and last edge                         
                        * in case of 1 edge cut-direction  is edge-definition and cut node-sequence is edge-definition
                        * the nextNODEs are the node-sequence omitting the start-node ... 
                        * ... nextNODE of an edge is the node connected by this edge in cut-direction; so nextNODE might be the i-node (the source-node) of the edge
                        * if edge-direction is cut-direction nextNODE is the k-node (the sink-node) of the edge
                    * compNr
                        * all 1 if all edges in the cut are connected
                        * otherwise the compNr (starting with 1) the edge belongs to
                        * the comp-Sequence is defined by the edge-sequence 
                        * the nodes of the 1st and last edge in cut-definition of the comp are defining the node-Sequence of the (longest shortest) path in the comp 
                    * parallel Edges 
                        * are omitted in the cut-Result; the 1st edge in cut-definition is in the edge
                    * Abzweige
                        * are omitted in the cut-Result
                        * the nodes of the 1st and last edge in cut-definition are defining the node-Sequence of the (longest shortest) path (comp-wise)
                        * only edges implementing this path are in the cut-Result

        Raises:
            XmError             
            
        >>> xmlFile=ms['GPipes']   
        >>> from Xm import Xm
        >>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)
        >>> vAGSN=xm.dataFrames['vAGSN']
        >>> schnitt=vAGSN[vAGSN['NAME']=='LR']
        >>> xm.dataFrames['schnitt']=schnitt.reset_index()
        >>> print(xm._getvXXXXAsOneString(vXXXX='schnitt',index=True))
           index LFDNR NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        0      7    14   LR   101    VENT  5309992331398639768  5625063016896368599  5625063016896368599              1                  1      0       G1      1
        1      8    14   LR   101    ROHR  5244313507655010738  5625063016896368599  5625063016896368599              2                  1      0      GKS      1
        2      9    14   LR   101    VENT  5508684139418025293  5625063016896368599  5625063016896368599              3                  1      0      GKD      1
        3     10    14   LR   101    ROHR  5114681686941855110  5625063016896368599  5625063016896368599              4                  1      0       G3      1
        4     11    14   LR   101    ROHR  4979507900871287244  5625063016896368599  5625063016896368599              5                  1      0       G4      1
        5     12    14   LR   101    VENT  5745097345184516675  5625063016896368599  5625063016896368599              6                  1      0       GR      1
        >>> schnitt=vAGSN[vAGSN['NAME']=='LR-Lücke']
        >>> xm.dataFrames['schnitt']=schnitt.reset_index()
        >>> print(xm._getvXXXXAsOneString(vXXXX='schnitt',index=True))
           index LFDNR      NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        0     13    16  LR-Lücke   101    VENT  5309992331398639768  5630543731618051887  5630543731618051887              1                  1      0       G1      1
        1     14    16  LR-Lücke   101    ROHR  5244313507655010738  5630543731618051887  5630543731618051887              2                  1      0      GKS      1
        2     15    16  LR-Lücke   101    ROHR  5114681686941855110  5630543731618051887  5630543731618051887              3                  1      0       G3      2
        3     16    16  LR-Lücke   101    ROHR  4979507900871287244  5630543731618051887  5630543731618051887              4                  1      0       G4      2
        4     17    16  LR-Lücke   101    VENT  5745097345184516675  5630543731618051887  5630543731618051887              5                  1      0       GR      2
        >>> schnitt=vAGSN[vAGSN['NAME']=='LR-Flansch']
        >>> xm.dataFrames['schnitt']=schnitt.reset_index()
        >>> print(xm._getvXXXXAsOneString(vXXXX='schnitt',index=True))    
           index LFDNR        NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        0     18    18  LR-Flansch   101    VENT  5309992331398639768  5134530907542044265  5134530907542044265              1                  1      0       G1      1
        1     19    18  LR-Flansch   101    ROHR  5244313507655010738  5134530907542044265  5134530907542044265              2                  1      0      GKS      1
        2     20    18  LR-Flansch   101    VENT  5508684139418025293  5134530907542044265  5134530907542044265              3                  1      0      GKD      1
        3     21    18  LR-Flansch   101    ROHR  5114681686941855110  5134530907542044265  5134530907542044265              4                  1      0       G3      1
        4     22    18  LR-Flansch   101    ROHR  4979507900871287244  5134530907542044265  5134530907542044265              5                  1      0       G4      1
        5     24    18  LR-Flansch   101    VENT  5745097345184516675  5134530907542044265  5134530907542044265              7                  1      0       GR      1
        >>> schnitt=vAGSN[vAGSN['NAME']=='LR-Parallel']
        >>> xm.dataFrames['schnitt']=schnitt.reset_index()
        >>> print(xm._getvXXXXAsOneString(vXXXX='schnitt',index=True))          
           index LFDNR         NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        0     25    20  LR-Parallel   101    VENT  5309992331398639768  4694969854935170169  4694969854935170169              1                  1      0       G1      1
        1     26    20  LR-Parallel   101    ROHR  5244313507655010738  4694969854935170169  4694969854935170169              2                  1      0      GKS      1
        2     27    20  LR-Parallel   101    VENT  5116489323526156845  4694969854935170169  4694969854935170169              3                  1      0      GKD      1
        3     29    20  LR-Parallel   101    ROHR  5114681686941855110  4694969854935170169  4694969854935170169              5                  1      0       G3      1
        4     30    20  LR-Parallel   101    ROHR  4979507900871287244  4694969854935170169  4694969854935170169              6                  1      0       G4      1
        5     31    20  LR-Parallel   101    VENT  5745097345184516675  4694969854935170169  4694969854935170169              7                  1      0       GR      1
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vAGSN=None
            vAGSN=self._OBJS('AGSN')
          
            vAGSN=vAGSN[[
             'LFDNR'
             ,'NAME'
             ,'AKTIV'
            #from OBJS
            ,'OBJTYPE' #type (i.e. KNOT) 
            ,'OBJID' #pk (or tk?!) 
            #IDs
            ,'pk','tk'
            ]]
            #vAGSN['LFDNR']=vAGSN['LFDNR'].astype('int')
            vAGSN=vAGSN.assign(nrObjIdInAgsn=vAGSN.groupby(['LFDNR']).cumcount()+1) # dieses VBEL-Obj. ist im Schnitt Nr. x
            vAGSN=vAGSN.assign(nrObjIdTypeInAgsn=vAGSN.groupby(['LFDNR','OBJTYPE','OBJID']).cumcount()+1) # dieses VBEL-Obj kommt im Schnitt zum x. Mal vor

            tModell=self.dataFrames['MODELL']
            netzTyp=tModell['NETZTYP'][0] # '21'

            vAGSN['Layer']=0
            if netzTyp == '21':
                #vAGSN['Layer']=-666

                for lfdnr in sorted(vAGSN['LFDNR'].unique()):
                
                    oneAgsn=vAGSN[vAGSN['LFDNR']==lfdnr]
                   
                    dfSplitRow=oneAgsn[oneAgsn['OBJID'].str.endswith('\n')]
                    # Test if empty Dataframe
                    if dfSplitRow.empty:                        
                        logger.debug("{0:s}vAGSN {1:s} has no OBJID\n-Row to seperate SL/RL.".format(logStr,oneAgsn.iloc[0].NAME)) 
                        vAGSN.loc[oneAgsn.index.values[0]:oneAgsn.index.values[-1],'Layer']=1 

                    else:
                        splitRowIdx=dfSplitRow.index.values[0]                                    
    
                        vAGSN.loc[splitRowIdx,'Layer']=1#0
                        vAGSN.loc[oneAgsn.index.values[0]:splitRowIdx-1,'Layer']=1
                        vAGSN.loc[splitRowIdx+1:oneAgsn.index.values[-1],'Layer']=2

                        ObjId=vAGSN.loc[splitRowIdx,'OBJID']
                        vAGSN.loc[splitRowIdx,'OBJID']=ObjId.rstrip('\n')

            #vAGSN['Layer']=vAGSN['Layer'].astype('int')

            df=pd.merge(
                    vAGSN[vAGSN['nrObjIdTypeInAgsn']==1] # mehrfach vorkommende selbe VBEL im selben Schnitt ausschliessen
                   ,self.dataFrames['vVBEL']
                   ,how='left' 
                   ,left_on=['OBJTYPE','OBJID']  
                   ,right_index=True ,suffixes=('', '_y'))
            df.rename(columns={'tk_y':'tk_VBEL'},inplace=True)
            df=df[pd.isnull(df['tk_VBEL']) != True].copy()

            df['nextNODE']=None
            df['compNr']=None
            df['pEdgeNr']=0
            df['SOURCE_i']=df['NAME_i']
            df['SOURCE_k']=df['NAME_k']

            for nr in df['LFDNR'].unique():                
                
                for ly in df[df['LFDNR']==nr]['Layer'].unique():                                        

                    dfSchnitt=df[(df['LFDNR']==nr) & (df['Layer']==ly)]                                      
                    logger.debug("{0:s}Schnitt: {1:s} Nr: {2:s} Layer: {3:s}".format(logStr
                                                                           ,str(dfSchnitt['NAME'].iloc[0])
                                                                           ,str(dfSchnitt['LFDNR'].iloc[0])
                                                                           ,str(dfSchnitt['Layer'].iloc[0])
                                                                          )) 
                    self.dataFrames['dummy']=dfSchnitt
                    logString="{0:s}dfSchnitt: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy'))
                    logger.debug(logString)
                  
                    dfSchnitt=dfSchnitt.reset_index() # stores index as a column named index
                    GSchnitt=nx.from_pandas_edgelist(dfSchnitt, source='SOURCE_i', target='SOURCE_k', edge_attr=True,create_using=nx.MultiGraph())
                    
                    iComp=0
                    for comp in nx.connected_components(GSchnitt):
                        iComp+=1

                        logger.debug("{0:s}CompNr.: {1:s}".format(logStr,str(iComp))) 
                        
                        GSchnittComp=GSchnitt.subgraph(comp)
                                                
                        # Knoten der ersten Kante                        
                        for u,v, datadict in sorted(GSchnittComp.edges(data=True), key=lambda x: x[2]['nrObjIdInAgsn']):                            
                            #logger.debug("{0:s}1st: i: {1:s} (Graph: {2:s}) k:{3:s} (Graph: {4:s})".format(logStr,datadict['NAME_i'],u,datadict['NAME_k'],v)) 
                            sourceKi=datadict['NAME_i']
                            sourceKk=datadict['NAME_k']      
                            break
                        # Knoten der letzten Kante; sowie Ausgabe über alle Kanten
                        ieComp=0
                        for u,v, datadict in sorted(GSchnittComp.edges(data=True), key=lambda x: x[2]['nrObjIdInAgsn']):                                                        
                            ieComp+=1
                            if datadict['NAME_i']==u and datadict['NAME_k']==v:
                                GraphStr="=" # die SIR 3S Kantendef. ist = der nx-Kantendefinition
                            elif datadict['NAME_i']==v and datadict['NAME_k']==u:                                                                                            
                                GraphStr="{0:s}>{1:s}".format(u,v) # die SIR 3S Kantendef. ist u>v und nicht v>u wie bei nx
                            # die nx-Kante ist definiert durch u und v; die Reihenfolge ist für nx egal da kein gerichteter Graph 
                            else:
                                GraphStr="Fehler: Die NX-Kante ist ungl. der SIR 3S Kante?!"
                            logger.debug("{0:s}iComp: {1:d} ieComp: {2:d} idx: {3:d} NX i: {4:s} > NX k:{5:s} (SIR 3S Kantendef.: {6:s})".format(logStr,iComp,ieComp,datadict['index'],u,v,GraphStr)) 
                        #logger.debug("{0:s}Lst: i: {1:s} (Graph: {2:s}) k:{3:s} (Graph: {4:s})".format(logStr,datadict['NAME_i'],u,datadict['NAME_k'],v)) 
                        targetKi=datadict['NAME_i']
                        targetKk=datadict['NAME_k']
                        
                        
                        # laengster Pfad zwischen den Knoten der ersten und letzten Kante (4 Möglichkeiten)
                        nlComp=nx.shortest_path(GSchnittComp,sourceKi,targetKk)
                        nlCompTmp=nx.shortest_path(GSchnittComp,sourceKk,targetKk)
                        if len(nlCompTmp)>len(nlComp):
                            nlComp=nlCompTmp
                        nlCompTmp=nx.shortest_path(GSchnittComp,sourceKi,targetKi)
                        if len(nlCompTmp)>len(nlComp):
                            nlComp=nlCompTmp
                        nlCompTmp=nx.shortest_path(GSchnittComp,sourceKk,targetKi)
                        if len(nlCompTmp)>len(nlComp):
                            nlComp=nlCompTmp        
                        
                        logger.debug("{0:s}Pfad: Start: {1:s} > Ende: {2:s}".format(logStr,nlComp[0],nlComp[-1])) 
                                                
                        # SP-Kanten ermitteln (es koennten Abzweige in GSchnittComp dabei sein; die sind in GSchnittCompSP dann nicht mehr enthalten)
                        GSchnittCompSP=GSchnittComp.subgraph(nlComp)
                        # index-Liste der SP-Kanten
                        idxLst=[]                        
                        ieComp=0
                        for u,v, datadict in sorted(GSchnittCompSP.edges(data=True), key=lambda x: x[2]['nrObjIdInAgsn']):              
                            idxLst.append(datadict['index'])
                            # SP-Kanten Ausgabe
                            ieComp+=1
                            if datadict['NAME_i']==u and datadict['NAME_k']==v:
                                GraphStr="=" # die SIR 3S Kantendef. ist = der nx-Kantendefinition
                            elif datadict['NAME_i']==v and datadict['NAME_k']==u:                                                                                            
                                GraphStr="{0:s}>{1:s}".format(u,v) # die SIR 3S Kantendef. ist u>v und nicht v>u wie bei nx
                            # die nx-Kante ist definiert durch u und v; die Reihenfolge ist für nx egal da kein gerichteter Graph 
                            else:
                                GraphStr="Fehler: Die NX-Kante ist ungl. der SIR 3S Kante?!"
                            ###logger.debug("{0:s}iComp: {1:d} ieCompSP: {2:d} idx: {3:d} NX i: {4:s} > NX k:{5:s} (SIR 3S Kantendef.: {6:s})".format(logStr,iComp,ieComp,datadict['index'],u,v,GraphStr)) 
                        
                        # parallele Kanten bis auf eine aus der index-Liste eliminieren
                        idxLstWithoutP=[idx for idx in idxLst] # Belegung mit allen Kanten; parallele Kanten werden entnommen
                        idxLstOnlyP=[]
                        nrOfParallel=[]
                        # For every node in graph
                        for node in GSchnittCompSP.nodes(): 
                            # We look for adjacent nodes
                            for adj_node in GSchnittCompSP[node]: 
                                # If adjacent node has an edge to the first node
                                # Or our graph as several edges from the first to the adjacent node
                                if node in GSchnittCompSP[adj_node] or len(GSchnittCompSP[node][adj_node]) > 1: 
                                    #
                                    GSchnittCompSPParallel=GSchnittCompSP.subgraph([node,adj_node])
                                    ip=1
                                    for u,v, datadict in sorted(GSchnittCompSPParallel.edges(data=True), key=lambda x: x[2]['nrObjIdInAgsn']):                                                                                       
                                        if ip>1:
                                            idx=datadict['index']
                                            if idx in idxLstWithoutP:
                                                if datadict['NAME_i']==u and datadict['NAME_k']==v:
                                                    GraphStr="="  # die SIR 3S Kantendef. ist = der nx-Kantendefinition
                                                elif datadict['NAME_i']==v and datadict['NAME_k']==u:                                                                                            
                                                    GraphStr="{0:s}>{1:s}".format(u,v) # die SIR 3S Kantendef. ist u>v und nicht v>u wie bei nx
                                                # die nx-Kante ist definiert durch u und v; die Reihenfolge ist für nx egal da kein gerichteter Graph 
                                                else:
                                                    GraphStr="Fehler: Die NX-Kante ist ungl. der SIR 3S Kante?!"
                                                ###logger.debug("{0:s}idx: {1:d} parallele Kante: NX i: {2:s} > NX k:{3:s} (SIR 3S Kantendef.: {4:s})".format(logStr,idx,u,v,GraphStr))                                                                                               
                                                idxLstWithoutP.remove(idx)
                                                idxLstOnlyP.append(idx)
                                                nrOfParallel.append(ip-1)                                            
                                        ip+=1                      

                        # compNr-List: Laenge = Anzahl der Kanten  (parallele sind in GSchnittCompSP dabei ...)                                                                        
                        compNr=np.empty(GSchnittCompSP.number_of_edges(),dtype=int) 
                        compNr.fill(iComp)
                                                                           
                        logger.debug("{0:s}Len NodeList (with 1st Node): {1:d}".format(logStr,len(nlComp)))   
                        logger.debug("{0:s}Len CompList                : {1:d}".format(logStr,len(compNr)))         
                        logger.debug("{0:s}Len IdxList                 : {1:d}".format(logStr,len(idxLst)))
                        logger.debug("{0:s}Len IdxListWithoutP         : {1:d}".format(logStr,len(idxLstWithoutP)))   

                        logger.debug("{0:s}NodeList (with 1st Node): {1:s}".format(logStr,str(nlComp)))   
                        logger.debug("{0:s}CompList                : {1:s}".format(logStr,str(compNr)))   
                        logger.debug("{0:s}IdxList                 : {1:s}".format(logStr,str(idxLst)))   
                        logger.debug("{0:s}IdxListWithoutP         : {1:s}".format(logStr,str(idxLstWithoutP)))   

                        df.loc[idxLstWithoutP,'nextNODE']=nlComp[1:]  # parallele Kanten ohne nextNODE-Eintrag
                        df.loc[idxLst,'compNr']=compNr # alle Kanten (ausser Abzweige) mit compNr-Eintrag > Eliminierung Abzweige weiter unten
                        df.loc[idxLstOnlyP,'pEdgeNr']=nrOfParallel # nur parallle Kanten mit pEdgeNr-Eintrag > Eliminierung paralleler Kanten weiter unten
                       
            df['pEdgeNr']=df['pEdgeNr'].astype(int)
            df.drop(['SOURCE_i', 'SOURCE_k'], axis=1,inplace=True)

            # Testausgabe
            self.dataFrames['vAGSN_rawTest']=df[['LFDNR','NAME','OBJTYPE','nrObjIdInAgsn','Layer','NAME_i','NAME_k','L','D','nextNODE','compNr','pEdgeNr']]
            logger.debug("{0:s}df: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='vAGSN_rawTest',index=True)))

            vAGSN=df[(df['pEdgeNr']==0) # als parallel markierte Kanten eliminieren
                     & 
                     (pd.notnull(df['compNr'])) # als Abzweige erkannte Kanten eliminieren
                     ].filter(items=[
                        'LFDNR'
                        ,'NAME'
                        ,'AKTIV'
                        ,'OBJTYPE'
                        ,'OBJID'
                        ,'pk'
                        ,'tk'
                        ,'nrObjIdInAgsn'
                        ,'nrObjIdTypeInAgsn'
                        ,'Layer'
                        ,'nextNODE'
                        ,'compNr'
                        #,'pEdgeNr'
                        ])

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vAGSN,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vAGSN=pd.DataFrame()   
                                                                              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vAGSN

    def getvVBELwithNodeAttributeAdded(self,nodeAttribute='KVR',preserveMultiindex=False):
        """Adds two nodeAttribute-Cols (not already in vVBEL) to vVBEL and returns the df.

        Args:
            * nodeAttribute (default: 'KVR'): the Node Attribute which shall be added
            * preserveMultiindex (default: False): if True an existing Multiindex will be preserved; False: existing Index(Indices) will be col(s)
        Returns:
            * df (which might be incomplete, corrupt or empty if an error occurs; vVBEL is unchanged):
                * new Cols: 
                    * nodeAttribute_i
                    * nodeAttribute_k

        Raises:
            XmError  
                        
        >>> xmlFile=ms['LocalHeatingNetwork']   
        >>> from Xm import Xm
        >>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)
        >>> df=xm.getvVBELwithNodeAttributeAdded()
        >>> xm.dataFrames['tmp']=df
        >>> print(xm._getvXXXXAsOneString(vXXXX='tmp',index=True,filterColList=['OBJTYPE','OBJID','NAME_i','NAME_k','KVR_i','KVR_k']))
           OBJTYPE                OBJID       NAME_i  NAME_k KVR_i KVR_k
        0     FWES  5638756766880678918           R3     V-1     2     1
        1     FWVB  4643800032883366034       V-K002  R-K002     1     2
        2     ROHR  5266224553324203132       R-K001  R-K002     2     2
        3     ROHR  4614949065966596185       V-K002  V-K003     1     1
        4     FWVB  4704603947372595298       V-K004  R-K004     1     2
        5     ROHR  4637102239750163477       R-K003  R-K004     2     2
        6     ROHR  4713733238627697042       V-K004  V-K005     1     1
        7     FWVB  5121101823283893406       V-K005  R-K005     1     2
        8     ROHR  4613782368750024999       R-K004  R-K005     2     2
        9     ROHR  5123819811204259837       V-K005  V-K006     1     1
        10    FWVB  5400405917816384862       V-K007  R-K007     1     2
        11    ROHR  4945727430885351042       R-K006  R-K007     2     2
        12    FWVB  5695730293103267172       V-K003  R-K003     1     2
        13    ROHR  5379365049009065623       R-K002  R-K003     2     2
        14    ROHR  5037777106796980248       V-K003  V-K004     1     1
        15    KLAP  4801110583764519435           R2      R3     2     2
        16    PGRP  4986517622672493603          R-1      R3     2     2
        17    PUMP  5481331875203087055          R-1      R2     2     2
        18    ROHR  4769996343148550485          R-L  R-K000     2     2
        19    VENT  4897018421024717974          R-L     R-1     2     2
        20    VENT  5525310316015533093  PKON-Knoten     R-1     2     2
        21    ROHR  4789218195240364437       V-K001  V-K002     1     1
        22    ROHR  4939422678063487923          V-L  V-K000     1     1
        23    ROHR  4984202422877610920       V-K000  V-K001     1     1
        24    ROHR  5611703699850694889       R-K005  R-K006     2     2
        25    ROHR  5620197984230756681       V-K006  V-K007     1     1
        26    ROHR  5647213228462830353       R-K000  R-K001     2     2
        27    VENT  4678923650983295610          V-1     V-L     1     1
        >>> len(df.columns.tolist())
        20
        >>> df.index.names
        FrozenList([None])
        >>> df=xm.getvVBELwithNodeAttributeAdded(preserveMultiindex=True)
        >>> len(df.columns.tolist())
        18
        >>> df.index.names
        FrozenList(['OBJTYPE', 'OBJID'])
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vVBEL=self.dataFrames['vVBEL']
            vKNOT=self.dataFrames['vKNOT']

            vVBELCols_raw=vVBEL.columns.tolist()
                       
            # get indexNames before resetting them to cols
            if isinstance(vVBEL.index,pd.MultiIndex):
                indexColNames=vVBEL.index.names                
            df=vVBEL.reset_index() # stores index as a column and returns DataFrame with the new index 
            vVBELCols=df.columns.tolist() # with old indexCol(s)

            df=pd.merge(df,vKNOT,left_on='pk_i',right_on='pk',suffixes=['','_i']).filter(items=vVBELCols+[nodeAttribute])
            df.rename(columns={nodeAttribute: nodeAttribute+'_i'},inplace=True)
            df=pd.merge(df,vKNOT,left_on='pk_k',right_on='pk',suffixes=['','_k']).filter(items=vVBELCols+[nodeAttribute+'_i']+[nodeAttribute])
            df.rename(columns={nodeAttribute: nodeAttribute+'_k'},inplace=True)

            if isinstance(vVBEL.index,pd.MultiIndex) and preserveMultiindex:                                
                df=Xm.constructNewMultiindexFromCols(df=df,mColNames=indexColNames,mIdxNames=indexColNames)

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(df,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                df=pd.DataFrame()   
                                                                                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return df
        
    def vAGSN_Add(self,nl=None,weight=None,Layer=0,AKTIV=None,NAME='NEU',query=None,fmask=None,filterNonQ0Rows=True):
        """Adds a new User-defined Cut to the Model-defined Cuts. 

        Arguments:
             see constructShortestPathFromNodeList:
                 * nl: NodeList for the Cut
                 * weight: columnName of the weight attribute
                 * query: mask to filter vVBEL (to filter Edges) before constructing the Graph 
                 * fmask: function to filter vVBEL (to filter Edges) before constructing the Graph 
                 * query and fmask are used both if not None                 
           
             * Layer (to use in constructed cut)
             * AKTIV (to use in constructed cut)
             * NAME (to use in constructed cut): the cut will NOT be constructed if such a NAME already exists: ERROR
        
        Returns:
            True if successfull
            False else

        Raises:
            XmError               
            
        >>> xmlFile=ms['GPipes']   
        >>> from Xm import Xm
        >>> xm=Xm(xmlFile=xmlFile,NoH5Read=True)       
        >>> xm.vAGSN_Add(nl=['GL','GR'])           
        True
        >>> import pandas as pd
        >>> pd.set_option('display.max_columns',None)
        >>> pd.set_option('display.max_rows',None)
        >>> pd.set_option('display.max_colwidth',666666)   
        >>> pd.set_option('display.width',666666666)
        >>> xm.dataFrames['vAGSN_raw']        
           LFDNR         NAME AKTIV OBJTYPE                OBJID                   pk                   tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        0      2       1 Rohr   101    ROHR  5244313507655010738  5015814781412926392  5015814781412926392              1                  1      0      GKS      1
        1      6       V-Rohr   101    VENT  5309992331398639768  5396484903084432138  5396484903084432138              1                  1      0       G1      1
        2      6       V-Rohr   101    ROHR  5244313507655010738  5396484903084432138  5396484903084432138              2                  1      0      GKS      1
        3      8       Rohr-V   101    ROHR  4979507900871287244  4989935433418681990  4989935433418681990              1                  1      0       G4      1
        4      8       Rohr-V   101    VENT  5745097345184516675  4989935433418681990  4989935433418681990              2                  1      0       GR      1
        5     12      2 Rohre   101    ROHR  5114681686941855110  5748019382126004712  5748019382126004712              1                  1      0       G3      1
        6     12      2 Rohre   101    ROHR  4979507900871287244  5748019382126004712  5748019382126004712              2                  1      0       G4      1
        7     14           LR   101    VENT  5309992331398639768  5625063016896368599  5625063016896368599              1                  1      0       G1      1
        8     14           LR   101    ROHR  5244313507655010738  5625063016896368599  5625063016896368599              2                  1      0      GKS      1
        9     14           LR   101    VENT  5508684139418025293  5625063016896368599  5625063016896368599              3                  1      0      GKD      1
        10    14           LR   101    ROHR  5114681686941855110  5625063016896368599  5625063016896368599              4                  1      0       G3      1
        11    14           LR   101    ROHR  4979507900871287244  5625063016896368599  5625063016896368599              5                  1      0       G4      1
        12    14           LR   101    VENT  5745097345184516675  5625063016896368599  5625063016896368599              6                  1      0       GR      1
        13    16     LR-Lücke   101    VENT  5309992331398639768  5630543731618051887  5630543731618051887              1                  1      0       G1      1
        14    16     LR-Lücke   101    ROHR  5244313507655010738  5630543731618051887  5630543731618051887              2                  1      0      GKS      1
        15    16     LR-Lücke   101    ROHR  5114681686941855110  5630543731618051887  5630543731618051887              3                  1      0       G3      2
        16    16     LR-Lücke   101    ROHR  4979507900871287244  5630543731618051887  5630543731618051887              4                  1      0       G4      2
        17    16     LR-Lücke   101    VENT  5745097345184516675  5630543731618051887  5630543731618051887              5                  1      0       GR      2
        18    18   LR-Flansch   101    VENT  5309992331398639768  5134530907542044265  5134530907542044265              1                  1      0       G1      1
        19    18   LR-Flansch   101    ROHR  5244313507655010738  5134530907542044265  5134530907542044265              2                  1      0      GKS      1
        20    18   LR-Flansch   101    VENT  5508684139418025293  5134530907542044265  5134530907542044265              3                  1      0      GKD      1
        21    18   LR-Flansch   101    ROHR  5114681686941855110  5134530907542044265  5134530907542044265              4                  1      0       G3      1
        22    18   LR-Flansch   101    ROHR  4979507900871287244  5134530907542044265  5134530907542044265              5                  1      0       G4      1
        23    18   LR-Flansch   101    VENT  5745097345184516675  5134530907542044265  5134530907542044265              7                  1      0       GR      1
        24    20  LR-Parallel   101    VENT  5309992331398639768  4694969854935170169  4694969854935170169              1                  1      0       G1      1
        25    20  LR-Parallel   101    ROHR  5244313507655010738  4694969854935170169  4694969854935170169              2                  1      0      GKS      1
        26    20  LR-Parallel   101    VENT  5116489323526156845  4694969854935170169  4694969854935170169              3                  1      0      GKD      1
        27    20  LR-Parallel   101    ROHR  5114681686941855110  4694969854935170169  4694969854935170169              5                  1      0       G3      1
        28    20  LR-Parallel   101    ROHR  4979507900871287244  4694969854935170169  4694969854935170169              6                  1      0       G4      1
        29    20  LR-Parallel   101    VENT  5745097345184516675  4694969854935170169  4694969854935170169              7                  1      0       GR      1
        30    21          NEU  None    VENT  5309992331398639768                 PT3S                 PT3S              1                  1      0       G1      1
        31    21          NEU  None    ROHR  5244313507655010738                 PT3S                 PT3S              2                  1      0      GKS      1
        32    21          NEU  None    VENT  5116489323526156845                 PT3S                 PT3S              3                  1      0      GKD      1
        33    21          NEU  None    ROHR  5114681686941855110                 PT3S                 PT3S              4                  1      0       G3      1
        34    21          NEU  None    ROHR  4979507900871287244                 PT3S                 PT3S              5                  1      0       G4      1
        35    21          NEU  None    VENT  5745097345184516675                 PT3S                 PT3S              6                  1      0       GR      1
        >>> # Test if the same NAME is _not constructed twice ...
        >>> xm.vAGSN_Add(nl=['GL','GR'])      
        False
        >>> xm.dataFrames['vAGSN_raw'].shape 
        (36, 12)
        >>> # test if re-use works without erors ...
        >>> mx=xm.MxSync()
        >>> xm.MxAdd(mx=mx)    
        >>> # Test weight-Option ...
        >>> xm.vAGSN_Add(nl=['GL','GR'],weight='QAbsInv',NAME='GL-GR w')  # durchflussstaerksten Weg erzwingen  
        True
        >>> df=xm.dataFrames['vAGSN_raw']
        >>> df.query("LFDNR in [21,22] and nextNODE=='GKD'")
           LFDNR     NAME AKTIV OBJTYPE                OBJID    pk    tk  nrObjIdInAgsn  nrObjIdTypeInAgsn  Layer nextNODE compNr
        32    21      NEU  None    VENT  5116489323526156845  PT3S  PT3S              3                  1      0      GKD      1
        38    22  GL-GR w  None    VENT  5508684139418025293  PT3S  PT3S              3                  1      0      GKD      1
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            
           retValue=False

           vAGSN_raw=self.dataFrames['vAGSN_raw']   

           if NAME in vAGSN_raw['NAME'].unique():
                logger.debug("{0:s}Fehler: Schnitt {1:s} konnte nicht erzeugt werden da es bereits mind. einen Schnitt dieses Namens in df vAGSN_raw gibt!".format(logStr,NAME))   
                
           else:                                
                df=self.getvVBELwithNodeAttributeAdded()
                df=Xm.constructShortestPathFromNodeList(df=df,nl=nl,weight=weight,query=query,fmask=fmask,filterNonQ0Rows=filterNonQ0Rows)  

                if not df.empty:                                
                        df['Layer']=Layer
                        df['AKTIV']=AKTIV
               
                        df['NAME']=NAME

                        if not vAGSN_raw.empty:
                            nr=vAGSN_raw['LFDNR'].astype('int')
                            df['LFDNR']=nr.max()+1 
                        else:
                            df['LFDNR']=1

                        df=df.assign(nrObjIdInAgsn=df.groupby(['LFDNR']).cumcount()+1) # dieses VBEL-Obj. ist im Schnitt Nr. x
                        df=df.assign(nrObjIdTypeInAgsn=df.groupby(['LFDNR','OBJTYPE','OBJID']).cumcount()+1) # dieses VBEL-Obj kommt im Schnitt zum x. Mal vor

                        df['pk']='PT3S'
                        df['tk']='PT3S'

                        cols=vAGSN_raw.columns.tolist() # ['LFDNR','NAME','AKTIV','OBJTYPE','OBJID','pk','tk','nrObjIdInAgsn','nrObjIdTypeInAgsn','Layer','nextNODE','compNr']  
                        df = df[cols] 

                        vAGSN_rawNew=pd.concat([vAGSN_raw,df])

                        self.dataFrames['vAGSN_raw']=vAGSN_rawNew.reset_index(drop=True)

                        retValue=True
                else:
                        logger.debug("{0:s}Fehler: Schnitt {1:s} konnte nicht erzeugt werden da die Pfadermittlung kein Ergebnis ergeben hat!".format(logStr,NAME))    
                
            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal)                 
                                                                              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return retValue

    def _vRART(self):
        """One row per RART.

        Returns:
            columns:
                RART
                    * NAME
                    * BESCHREIBUNG
                    * INDSTD_TXT
                    * INDSTD (numeric)
                    * DWDT
                RART_BZ
                    * WSOSTD
                ID
                    * pk
                References
                    * NAME_KREF1
                    * NAME_KREF2
                    * NAME_SWVT
                    * [NAME_RCPL] - only if RCPLs exist
            
            sequence: Model

        Raises:
            XmError                                
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vRART=None            
        
            sPgrp='(0=aus | 2=Drehzahl | 21=Regelpunktliste Druckseite | 22=Regelpunktliste Saugseite | 41=Netzdruck Druckseite, Sollwert konstant | 43=Netzdruck Druckseite, Sollwert Tabelle | 42=Netzdruck Saugseite, Sollwert konstant | 44=Netzdruck Saugseite, Sollwert Tabelle | 51=Druckerhoehung/-abfall am Stellglied selbst, Sollwert konstant | 54=Druckerhoehung/-abfall am Stellglied selbst, Sollwert Tabelle | 52=Differenzdruck Druckseite, Sollwert konstant | 55=Differenzdruck Druckseite, Sollwert Tabelle | 53=Differenzdruck Saugseite, Sollwert konstant | 56=Differenzdruck Saugseite, Sollwert Tabelle | 62=Mitteldruck Druckseite, Sollwert konstant | 65=Mitteldruck Druckseite, Sollwert Tabelle | 63=Mitteldruck Saugseite, Sollwert konstant | 66=Mitteldruck Saugseite, Sollwert Tabelle | 71=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert konstant | 73=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert Tabelle | 72=Durchfluss Messstelle, Wirkungsrichtung negativ, Sollwert konstant | 74=Durchfluss Messstelle, Wirkungsrichtung negativ, Sollwert Tabelle)'            
            sRegv='(1002=Stellung | 1021=Regelpunktliste Unterstrom | 1022=Regelpunktliste Oberstrom | 1041=Netzdruck Unterstrom, Sollwert konstant | 1043=Netzdruck Unterstrom, Sollwert Tabelle | 1042=Netzdruck Oberstrom, Sollwert konstant | 1044=Netzdruck Oberstrom, Sollwert Tabelle | 1051=Druckabfall Regelventil, Sollwert konstant | 1054=Druckabfall Regelventil, Sollwert Tabelle | 1052=Differenzdruck Unterstrom, Sollwert konstant | 1055=Differenzdruck Unterstrom, Sollwert Tabelle | 1053=Differenzdruck Oberstrom, Sollwert konstant | 1056=Differenzdruck Oberstrom, Sollwert Tabelle | 1062=Mitteldruck Unterstrom, Sollwert konstant | 1065=Mitteldruck Unterstrom, Sollwert Tabelle | 1063=Mitteldruck Oberstrom, Sollwert konstant | 1066=Mitteldruck Oberstrom, Sollwert Tabelle | 1071=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert konstant | 1073=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert Tabelle | 1072=Durchfluss Messstelle, Wirkungsrichtung negativ, Sollwert konstant | 1074=Durchfluss Messstelle, Wirkungsrichtung negativ, Sollwert Tabelle)'
            sRegvGas='(1002=Stellung | 1041=Netzdruck, Unterstrom, Sollwert konstant | 1042=Netzdruck, Oberstrom, Sollwert konstant | 1071=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert konstant | 1073=Durchfluss Messstelle, Wirkungsrichtung positiv, Sollwert Tabelle)'

            items=sPgrp.strip('()').split(sep='|')+sRegv.strip('()').split(sep='|')+sRegvGas.strip('()').split(sep='|')
            IndstdDct=dict(zip([int(pair[0]) for pair in [item.split(sep='=') for item in items]]
                ,[pair[1].strip()  for pair in [item.split(sep='=') for item in items]]
                     ))
            #logger.debug("{0:s}{1:s}".format(logStr,str(IndstdDct))) 

            vRART=pd.merge(self.dataFrames['RART_BZ'],self.dataFrames['RART'],left_on='fk',right_on='pk',suffixes=['_BZ',''])[['NAME','BESCHREIBUNG'
            ,'INDSTD','DWDT'
            ,'fkKREF1','fkKREF2'
            #BZ
            ,'WSOSTD','fkRCPL', 'fkSWVT','pk']]

            vKnot=self.dataFrames['vKNOT']
            colLst=vRART.columns.tolist()
            colLst.append('NAME_KREF1')
            vRART=pd.merge(vRART,vKnot,left_on='fkKREF1',right_on='pk',suffixes=['','_KREF1'],how='left')[colLst]
            colLst.remove('fkKREF1')
            colLst.append('NAME_KREF2')
            colLst.remove('fkKREF2')
            vRART=pd.merge(vRART,vKnot,left_on='fkKREF2',right_on='pk',suffixes=['','_KREF2'],how='left')[colLst]

            vSwvt=self.dataFrames['vSWVT']
            colLst.append('NAME_SWVT')

              # * W: 1st Value
              #      * W_min
              #      * W_max

            colLst.remove('fkSWVT')
            vRART=pd.merge(vRART,vSwvt,left_on='fkSWVT',right_on='pk',suffixes=['','_SWVT'],how='left')[colLst]

            if 'RCPL' in self.dataFrames:
                tRcpl=self.dataFrames['RCPL']
                colLst.append('NAME_RCPL')
                colLst.remove('fkRCPL')
                vRART=pd.merge(vRART,tRcpl,left_on='fkRCPL',right_on='pk',suffixes=['','_RCPL'],how='left')[colLst]
            else:
                vRART.drop(columns=['fkRCPL'],inplace=True)      

            vRART['INDSTD']=pd.to_numeric(vRART['INDSTD'])                 
            vRART['INDSTD_TXT']=vRART.apply(lambda row: IndstdDct[row.INDSTD] if row.INDSTD in IndstdDct  else -1  , axis=1)
            cols=vRART.columns.tolist()
            cols.pop(cols.index('INDSTD_TXT'))
            cols.insert(cols.index('INDSTD'),'INDSTD_TXT')
            vRART=vRART.reindex(cols,axis="columns")

            #['NAME', 'BESCHREIBUNG', 'INDSTD_TXT', 'INDSTD', 'DWDT', 'WSOSTD', 'pk', 'NAME_KREF1', 'NAME_KREF2', 'NAME_SWVT']

            logger.debug("{0:s}{1:s}".format(logStr,str(vRART.columns.tolist())))
          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vRART,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vRART=pd.DataFrame()   
                                                                              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vRART

    def _OBJS(self,dfName,OBJSDecodedColName='OBJSDec'):
        """Decode a column OBJS (a BLOB containing a SIR 3S OBJ collection).

        Args:
            dfName: Name of a dataFrame with column OBJS
            
                columns used (in self.dataFrames[dfName]):
                    * OBJS (BLOB): i.e.: KNOT~4668229590574507160\t...
                    * pk: ID (of the row) 
                    * None is returned if these columns are missing
                    * in this case no changes concerning column OBJSDecodedColName in self.dataFrames[dfName]

            OBJSDecodedColName: colName of the decoded OBJS; default: OBJSDec (i.e. the BLOB is not overwritten)

        Returns:
            column OBJSDecodedColName in self.dataFrames[dfName] set to OBJS decoded
                decoded to 'XXXX~' if OBJS was None 

            dfOBJS: dataFrame with one row per OBJ in OBJS: 
                columns added (compared to self.dataFrames[dfName]):
                    * OBJTYPE
                    * OBJID 
                    * OBJSDecodedColName (if not set to 'OBJS')
                rows missing (compared to self.dataFrames[dfName]):
                    * rows with OBJS None
        Raises:
            XmError
                    
        >>> # -q -m 0 -t both -s _OBJS -y yes -z no -w LocalHeatingNetwork
        >>> xm=xms['LocalHeatingNetwork']
        >>> df=xm._OBJS('AGSN')
        >>> df['OBJSDecStrShort']=df['OBJSDec'].str[1:24]        
        >>> df[['pk','NAME','OBJSDecStrShort','OBJTYPE','OBJID']].iloc[:3]
                            pk                                      NAME          OBJSDecStrShort OBJTYPE                OBJID
        0  5252525269080005909  Netzdruckdiagramm VL/RL: BHKW - Netzende  ROHR~493942267806348792    ROHR  4939422678063487923
        1  5252525269080005909  Netzdruckdiagramm VL/RL: BHKW - Netzende  ROHR~493942267806348792    ROHR  4984202422877610920
        2  5252525269080005909  Netzdruckdiagramm VL/RL: BHKW - Netzende  ROHR~493942267806348792    ROHR  4789218195240364437
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            dfOBJS=None

            if dfName not in self.dataFrames.keys():
                 logger.debug("{0:s}{1:s} not in dataFrames.keys()".format(logStr,dfName)) 
            else:
                 logger.debug("{0:s}{1:s}     in dataFrames.keys()".format(logStr,dfName)) 

            if 'OBJS' not in self.dataFrames[dfName].columns.tolist():
                 logger.debug("{0:s}column OBJS not in dataFrame!".format(logStr)) 
                 logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
                 return dfOBJS

            if 'pk' not in self.dataFrames[dfName].columns.tolist():
                 logger.debug("{0:s}column pk not in dataFrame!".format(logStr)) 
                 logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
                 return dfOBJS
                      
            try:           
                # Spalte OBJS dekodieren; wenn leer ((noch) keine OBJS), dann 'XXXX~'      
                #                                                                   4668229590574507160
                # cp1252
                self.dataFrames[dfName].loc[:,OBJSDecodedColName]=self.dataFrames[dfName]['OBJS'].apply(lambda x: 'XXXX~' if x is None else base64.b64decode(x)).str.decode('utf-8')                
            except UnicodeDecodeError as e:  
                x=self.dataFrames[dfName]['OBJS'].iloc[0]
                logger.debug("{:s} {!s:s} {!s:s}".format(logStr,x,base64.b64decode(x)))    
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.error(logStrFinal) 
                raise XmError(logStrFinal)      
                
                

            # einzelne OBJS als neuer df
            # ------------------------->           
            sList=[pd.Series(row['pk'],index=row[OBJSDecodedColName].split('\t'),name='pk_Echo') for index,row in self.dataFrames[dfName].iterrows()]                

            # sList[0]:
            # index:                      pk_Echo 
            # KNOT~4668229590574507160    5403356857783326643
            # XXXX~                       5403356857783326643

            dfOBJS_OBJS=pd.concat(sList).reset_index() # When we reset the index, the old index is added as a column named 'index', and a new sequential index is used
            dfOBJS_OBJS.rename(columns={'index':'ETYPEEID'},inplace=True)
            # dfOBJS_OBJS:
            #	ETYPEEID	              pk_Echo
            # 0	KNOT~4668229590574507160  5403356857783326643
            # 0 XXXX~                     5403356857783326643

            # ETYPEEID Checks als Filter
            dfOBJS_OBJS=dfOBJS_OBJS[dfOBJS_OBJS['ETYPEEID'].notnull()]
            dfOBJS_OBJS=dfOBJS_OBJS[dfOBJS_OBJS['ETYPEEID'].str.len()>5]

            # ETYPEEID: neue Spalten bilden 
            dfOBJS_OBJS['OBJTYPE']=dfOBJS_OBJS['ETYPEEID'].str[:4]
            dfOBJS_OBJS['OBJID']=dfOBJS_OBJS['ETYPEEID'].str[5:]
            # ETYPEEID: loeschen
            dfOBJS_OBJS.drop(['ETYPEEID'],axis=1,inplace=True)
            # dfOBJS_OBJS:
            #	OBJTYPE OBJID 	            pk_Echo
            # 0	KNOT    4668229590574507160	5403356857783326643   
            # <-------------------------                   
            
            # neuer df
            # --------                
            dfOBJS=pd.merge(self.dataFrames[dfName],dfOBJS_OBJS,left_on='pk',right_on='pk_Echo')
            dfOBJS.drop(['pk_Echo'],axis=1,inplace=True)

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(dfOBJS,pd.core.frame.DataFrame):
                pass 
            else:
                pass

            logger.debug(logStrFinal) 
                                                  
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return dfOBJS

    def _LAYOUT_XML(self,dfName):
        """Decode a column LAYOUT_XML (a BLOB containing XML) in dfName.

        Args:
            dfName: Name of a dataFrame with column LAYOUT_XML
            
                columns used (in self.dataFrames[dfName]):
                    * LAYOUT_XML (BLOB)                   
                    * None is returned if these columns are missing                   

        Returns:
            dctDfsLAYOUT: a dct with dfs with LAYOUT-content
 
        Raises:
            XmError
                    
        >>> # -v -m 0 -t both -s _LAYOUT_XML -y yes -z no -w LocalHeatingNetwork
        >>> xm=xms['LocalHeatingNetwork']
        >>> dctDfsLAYOUT=xm._LAYOUT_XML('AGSN')
        >>> sorted(dctDfsLAYOUT.keys())
        ['DIAGRAM', 'PROFILE_LINE', 'PROFILE_LINE_COLORS', 'X_AXIS', 'Y_AXIS']
        >>> dctDfsLAYOUT['PROFILE_LINE']
                    FK_DIAGRAM LINE_TYPE DRUCKNIV_P LINE_COLOR LINE_COLOR_RL LINE_STYLE LINE_STYLE_RL
        0  5252525269080005909         1          1          0             0          1             5
        1  5252525269080005909         8          1        255      16711680          5             5
        2  5252525269080005909         3          1   16711935           128          5             5
        >>> dctDfsLAYOUT=xm._LAYOUT_XML('SPLZ')        
        >>> sorted(dctDfsLAYOUT.keys())
        ['DIAGRAM', 'LINE', 'Y_AXIS']
        >>> dctDfsLAYOUT['LINE']
                    FK_DIAGRAM LINE_TYPE LABEL            DATAPOINT LINE_COLOR CONST_NIVEAU_VALUE LINE_STYLE DYNAMIC LINE_WIDTH FACTOR ADDEND
        0  4715028732328060917         1  None  5458207635769388996   11829830                  0          5       0        0,4      1      0
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            dctDfsLAYOUT=None

            if dfName not in self.dataFrames.keys():
                 logStrFinal="{0:s}{1:s} not in dataFrames.keys()!".format(logStr,dfName)
                 logger.debug(logStrFinal) 
                 raise XmError(logStrFinal)                   
            else:
                 logger.debug("{0:s}{1:s}     in dataFrames.keys().".format(logStr,dfName)) 

            if 'LAYOUT_XML' not in self.dataFrames[dfName].columns.tolist():
                 logStrFinal="{0:s}column LAYOUT_XML not in dataFrame!".format(logStr)
                 logger.debug(logStrFinal) 
                 raise XmError(logStrFinal) 
            else:
                 logger.debug("{0:s}column LAYOUT_XML    in dataFrame.".format(logStr))
                      
            try:     
                dctDfsLAYOUTLst=[]
                for index, row in self.dataFrames[dfName].iterrows():                    
                    xmlBLOB=row['LAYOUT_XML']
                    logger.debug("{:s}xmlBLOB={!s:s}".format(logStr,xmlBLOB)) 
                    xmlBLOBInB=base64.b64decode(xmlBLOB)
                    logger.debug("{:s}xmlBLOBInB={!s:s}".format(logStr,xmlBLOBInB)) 
                    xmlBLOBInStr=xmlBLOBInB.decode('cp1252') 
                    logger.debug("{:s}xmlBLOBInStr={:s}".format(logStr,re.sub('\r\n[ ]*','',xmlBLOBInStr))) 
                    root = ET.fromstring(xmlBLOBInStr)
                    dctDfsLAYOUTLst.append(Xm._xmlRoot2Dfs(root))

                # TabellenTypen ermitteln
                tabTypes=set()
                for dct in  dctDfsLAYOUTLst:
                    tabTypes=tabTypes.union(dct.keys())

                dctDfsLAYOUT={}
                # ueber alle Tabellen
                for tabType in tabTypes:                    
                    tabTypeTables=[]
                    for dct in dctDfsLAYOUTLst:
                        if tabType not in dct.keys():
                            continue
                        else:
                            # Tabelle anhängen
                            tabTypeTables.append(dct[tabType])
                    # ... wenn nicht alle Tabellen dieselben Spalten haben ?! ...
                    dctDfsLAYOUT[tabType]=pd.concat(tabTypeTables)
         
            except UnicodeDecodeError as e:                 
                logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.error(logStrFinal) 
                raise XmError(logStrFinal)      
                              
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
                                                  
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return dctDfsLAYOUT

    def _vLFKT(self):
        """One row per Loadfactor Timeseries.

        Returns:
            columns
                LFKT
                    * NAME
                    * BESCHREIBUNG
                    * INTPOL
                    * ZEITOPTION
                SERIES
                    * LF: 1st Value
                    * LF_min
                    * LF_max
                LFKT ID
                    * pk

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vLFKT=None
            vLFKT=pd.merge(self.dataFrames['LFKT'],self.dataFrames['LFKT_ROWT'],left_on='pk',right_on='fk')
            vLFKT['ZEIT']=pd.to_numeric(vLFKT['ZEIT']) 
            vLFKT['LF']=pd.to_numeric(vLFKT['LF']) 
            vLFKT['ZEIT_RANG']=vLFKT.groupby(['pk_x'])['ZEIT'].rank(ascending=True)
            #
            vLFKT_gLF=vLFKT.groupby(['pk_x'], as_index=False).agg({'LF':[np.min,np.max]})
            vLFKT_gLF.columns= [tup[0]+tup[1] for tup in zip(vLFKT_gLF.columns.get_level_values(0),vLFKT_gLF.columns.get_level_values(1))]
            vLFKT_gLF.rename(columns={'LFamin':'LF_min','LFamax':'LF_max'},inplace=True)
            #
            vLFKT=pd.merge(vLFKT,vLFKT_gLF,left_on='pk_x',right_on='pk_x')
            #
            vLFKT=vLFKT[vLFKT['ZEIT_RANG']==1]
            #
            vLFKT=vLFKT[['NAME','BESCHREIBUNG','LF','LF_min','LF_max','INTPOL','ZEITOPTION','pk_x']]
            #
            vLFKT.rename(columns={'pk_x':'pk'},inplace=True)
            #
            vLFKT=vLFKT[[
                'NAME','BESCHREIBUNG'
                ,'LF','LF_min','LF_max'
                ,'INTPOL','ZEITOPTION'
                ,'pk'
                ]]
                                 
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)                
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vLFKT  

    def _vNRCV(self):
        """One row per NRCV (NumeRiCal Value).

        Returns:
            columns
                ANNOTATIONS
                    * cRefLfdNr
                CONT
                    * CONT
                    * CONT_ID
                    * CONT_LFDNR
                DP
                    Datapointgroup
                        * DPGR
                    Datapoint
                        * OBJTYPE
                        * fkOBJTYPE
                        * ATTRTYPE                    
                    Datapoint IDs
                        * pk_ROWS (pk from DPKT ab 90-10)
                        * tk_ROWS (tk from DPKT ab 90-10)
                NRCV IDs
                    * pk
                    * tk
                PLot Coordinates
                    * pXYLB: (X,Y): Left,Bottom

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vNRCV=None
            vNRCV=self.dataFrames['NRCV']

            import re
            vStr=self.getVersion(type='BZ')
            m=re.search('Sir(?P<Db3s>[DBdb3Ss]{2})-(?P<Major>\d+)-(?P<Minor>\d+)$',vStr) # i.e. Sir3S-90-10
            minorVer=int(m.group('Minor'))

            if 'DPGR_ROWS' in self.dataFrames.keys():
                # 90-09
                vNRCV=vNRCV.merge(self.dataFrames['DPGR_ROWS'],left_on='fkDPGR_ROWS',right_on='pk',suffixes=['_NR','_DR'])                
                vNRCV=vNRCV.merge(self.dataFrames['DPGR'],left_on='fk',right_on='pk',suffixes=['_DR2','_DG'])
            else:
                # 90-10                
                vNRCV=vNRCV.merge(self.dataFrames['DPGR_DPKT'],left_on='fkDPGR_DPKT',right_on='pk',suffixes=['_NR','_DR'])
                vNRCV=vNRCV.merge(self.dataFrames['DPKT'],left_on='fkDPKT',right_on='pk',suffixes=['_NR','_DR'])
                vNRCV=vNRCV.merge(self.dataFrames['DPGR'],left_on='fkDPGR',right_on='pk',suffixes=['_DR2','_DG'])

                logger.debug("{:s}vNRCV columns vor DPKT_BZ: {:s}".format(logStr,str(vNRCV.columns)))   

                # (['pk_NR', 'fkDE_NR', 'rk_NR', 'tk_NR', 'UNIT_NR', 'DECPOINT', 'ABSWERT', 'PRFTXT', 'fkDPGR_DPKT', 'fkCONT', 'GRAF', 'FONT'
                # , 'BESCHREIBUNG', 'DELETED_NR', 'SELECT1_NR'
                # , 'pk_DR', 'fkDE_DR', 'rk_DR', 'tk_DR', 'fkDPGR', 'fkDPKT', 'DELETED_DR', 'SELECT1_DR'
                # , 'pk_DR2', 'fkDE_DR2', 'rk_DR2', 'tk_DR2', 'OBJTYPE', 'ATTRTYPE', 'EPKZ', 'TITLE', 'UNIT_DR'
                # , 'FLAGS', 'OL3COMMAND', 'DATATYPE', 'DATALENGTH', 'DESCRIPTION_DR2', 'rkDPKT', 'DELETED_DR2', 'SELECT1_DR2'
                # , 'pk_DG', 'fkDE_DG', 'rk_DG', 'tk_DG', 'NAME', 'PERMISSION_FLAGS', 'TYP'
                # , 'DTFAK', 'OPCGROUP_NAME', 'OPCSERVER_PATH', 'DESCRIPTION_DG', 'IDREFERENZ', 'DELETED_DG', 'SELECT1_DG'], dtype='object')

                if 'DPKT_BZ' in self.dataFrames.keys():  # 90-12                  
                    pass
                    vNRCV=vNRCV.merge(self.dataFrames['DPKT_BZ'],left_on='pk_DR2',right_on='fk',suffixes=['_DR1a','_DRBZ'])

                logger.debug("{:s}vNRCV Shape nach DPKT_BZ: {:s}".format(logStr,str(vNRCV.shape)))   
                logger.debug("{:s}vNRCV columns nach DPKT_BZ: {:s}".format(logStr,str(vNRCV.columns)))                   

            
            vNRCV=vNRCV.merge(self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=['_DR3','_CONT'])

            # GRAF ###
            xyLeftBottom=[]
            for index,row in vNRCV.iterrows():
                if pd.isnull(row.GRAF_DR3):                 
                    xyLeftBottom.append(())
                    continue
                geomBytes=base64.b64decode(row.GRAF_DR3)               
                XYLeftBottom=struct.unpack('2d',geomBytes[8:24]) 
                xyLeftBottom.append(XYLeftBottom)

         
            pXyLeftBottom=[]
            for index,row in vNRCV.iterrows():
                 xyLB=xyLeftBottom[index]
                 if int(row.ID)!=1001:
                    pXyLeftBottom.append(xyLB)
                 else:
                    x,y=xyLB
                    x=x-self.pXCorZero
                    y=y-self.pYCorZero
                    pXyLeftBottom.append((x,y))
            vNRCV['pXYLB']=pd.Series(pXyLeftBottom)

            logger.debug("{:s}vNRCV columns: {:s}".format(logStr,str(vNRCV.columns)))      

            # 90-12:
            # Index(['pk_NR', 'fkDE_NR', 'rk_NR', 'tk_NR', 'UNIT_NR'
            # , 'DECPOINT', 'ABSWERT', 'PRFTXT', 'fkDPGR_DPKT', 'fkCONT', 'GRAF_DR3', 'FONT_DR3'
            # , 'BESCHREIBUNG', 'DELETED_NR', 'SELECT1_NR', 'pk_DR', 'fkDE_DR', 'rk_DR', 'tk_DR'
            # , 'fkDPGR', 'fkDPKT', 'DELETED_DR', 'SELECT1_DR', 'pk_DR2', 'fkDE_DR2', 'rk_DR2', 'tk_DR2'
            # , 'OBJTYPE', 'ATTRTYPE', 'EPKZ', 'TITLE', 'UNIT_DR', 'FLAGS', 'OL3COMMAND'
            # , 'DATATYPE', 'DATALENGTH', 'DESCRIPTION_DR2', 'rkDPKT', 'DELETED_DR2', 'SELECT1_DR2'
            # , 'pk_DG', 'fkDE_DG', 'rk_DG', 'tk_DG', 'NAME_DR3', 'PERMISSION_FLAGS', 'TYP'
            # , 'DTFAK', 'OPCGROUP_NAME', 'OPCSERVER_PATH', 'DESCRIPTION_DG', 'IDREFERENZ_DR3'
            # , 'DELETED_DG', 'SELECT1_DG'
            #, 'pk_DR3', 'fkDE_DR3'
            #, 'fk', 'NAME1', 'NAME2', 'NAME3', 'fkOBJTYPE', 'CLIENT_ID', 'OPCITEM_ID', 'CLIENT_FLAGS', 'FACTOR', 'ADDEND'
            #, 'DEVIATION', 'LOWER_LIMIT', 'UPPER_LIMIT', 'pk_CONT', 'fkDE_CONT', 'rk', 'tk', 'ID'
            #, 'NAME_CONT', 'IDPARENT', 'rkPARENT', 'LFDNR', 'GRAF_CONT', 'FONT_CONT', 'GEOM', 'IDREFERENZ_CONT', 'pXYLB'], dtype='object')

            if minorVer>=12:
                vNRCV=vNRCV[[
                   'NAME_CONT'
                  ,'ID'
                  ,'LFDNR'              
                  # DPGR
                  ,'NAME_DR3'
                   # Data (of the DPGR_ROW)
                  ,'OBJTYPE'
                  ,'fkOBJTYPE'  # 90-12 in BZ
                  ,'ATTRTYPE'
                  # IDs (of the Datapoint)
                  ,'pk_DR2'
                  ,'tk_DR2'       
                  # IDs (of the NRCV)
                  ,'pk_NR'
                  ,'tk_NR'
                  ,'pXYLB'
                ]]                
            else:
                vNRCV=vNRCV[[
                   'NAME_CONT'
                  ,'ID'
                  ,'LFDNR'              
                  # DPGR
                  ,'NAME_DR3'
                   # Data (of the DPGR_ROW)
                  ,'OBJTYPE'
                  ,'fkOBJTYPE'  # 90-12 in BZ
                  ,'ATTRTYPE'
                  # IDs (of the Datapoint)
                  ,'pk_DR'
                  ,'tk_DR'       
                  # IDs (of the NRCV)
                  ,'pk_NR'
                  ,'tk_NR'
                  ,'pXYLB'
                ]]

            if minorVer>=12:
                vNRCV.rename(columns={'NAME_CONT':'CONT','ID':'CONT_ID','LFDNR':'CONT_LFDNR'
                          ,'NAME_DR3':'DPGR'
                         ,'pk_NR':'pk'
                         ,'tk_NR':'tk'
                         ,'pk_DR2':'pk_ROWS'
                         ,'tk_DR2':'tk_ROWS'},inplace=True)                  
            else:
                vNRCV.rename(columns={'NAME_CONT':'CONT','ID':'CONT_ID','LFDNR':'CONT_LFDNR'
                          ,'NAME_DR3':'DPGR'
                         ,'pk_NR':'pk'
                         ,'tk_NR':'tk'
                         ,'pk_DR':'pk_ROWS'
                         ,'tk_DR':'tk_ROWS'},inplace=True)  

            vNRCV=vNRCV.assign(cRefLfdNr=vNRCV.sort_values(['CONT_ID','pk'], ascending=True)
                   .groupby(['OBJTYPE'
                             ,'fkOBJTYPE' # 90-12 in BZ
                             ,'ATTRTYPE']).cumcount()+1)

            vNRCV=vNRCV[[
               'cRefLfdNr' 
              # CONT
              ,'CONT'
              ,'CONT_ID'
              ,'CONT_LFDNR'
              # DPGR
              ,'DPGR'
               # Data (of the DPGR_ROW)
              ,'OBJTYPE'
              ,'fkOBJTYPE'  # 90-12 in BZ
              ,'ATTRTYPE'
              # IDs (of the Datapoint)
              ,'pk_ROWS'
              ,'tk_ROWS'       
              # IDs (of the NRCV)
              ,'pk'
              ,'tk'
              ,'pXYLB'
            ]]

            vNRCV.sort_values(['OBJTYPE'
                               ,'fkOBJTYPE'  # 90-12 in BZ
                               ,'ATTRTYPE','cRefLfdNr'],ascending=True,inplace=True)
            vNRCV=pd.DataFrame(vNRCV.values,columns=vNRCV.columns)
                                                        
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            if isinstance(vNRCV,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vNRCV=pd.DataFrame()                 
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vNRCV

    def _vGTXT(self):
        """One row per GTXT (Graphic TeXT).

        Returns:
            columns
                GTXT
                    * GRAFTEXT (the text)
                CONT
                    * CONT
                    * CONT_ID
                    * CONT_LFDNR
                GTXT IDs
                    * pk
                    * tk
                PLot Coordinates
                    * pXYLB: (X,Y): Left,Bottom

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vGTXT=None
            vGTXT=self.dataFrames['GTXT']            
            vGTXT=vGTXT.merge(self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=['_DR3','_CONT'])

            # GRAF ###
            xyLeftBottom=[]
            for index,row in vGTXT.iterrows():
                if pd.isnull(row.GRAF_DR3):                 
                    xyLeftBottom.append(())
                    continue
                geomBytes=base64.b64decode(row.GRAF_DR3)               
                XYLeftBottom=struct.unpack('2d',geomBytes[4:20]) 
                xyLeftBottom.append(XYLeftBottom)
           
            pXyLeftBottom=[]
            for index,row in vGTXT.iterrows():
                 xyLB=xyLeftBottom[index]
                 if int(row.ID)!=1001:
                    pXyLeftBottom.append(xyLB)
                 else:
                    x,y=xyLB
                    x=x-self.pXCorZero
                    y=y-self.pYCorZero
                    pXyLeftBottom.append((x,y))
            vGTXT['pXYLB']=pd.Series(pXyLeftBottom)

            vGTXT=vGTXT[[
               'NAME'
              ,'ID'
              ,'LFDNR'   
              ,'GRAFTEXT'                     
              # IDs (of the NRCV)
              ,'pk_DR3'
              ,'tk_DR3'
              ,'pXYLB'
            ]]

            vGTXT.rename(columns={'NAME':'CONT','ID':'CONT_ID','LFDNR':'CONT_LFDNR'                    
                     ,'pk_DR3':'pk'
                     ,'tk_DR3':'tk'
                     ,'pk_DR':'pk_ROWS'
                     ,'tk_DR':'tk_ROWS'},inplace=True)             

            vGTXT=vGTXT[[
             
              # CONT
               'CONT'
              ,'CONT_ID'
              ,'CONT_LFDNR'
              ,'GRAFTEXT'
              # IDs (of the NRCV)
              ,'pk'
              ,'tk'
              ,'pXYLB'
            ]]
                                                   
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vGTXT,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vGTXT=pd.DataFrame()                 
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vGTXT

    def _vSWVT(self):
        """One row per Timeseries.

        Returns:
            columns
                SWVT
                    * NAME
                    * BESCHREIBUNG
                    * INTPOL
                    * ZEITOPTION
                SERIES
                    * W: 1st Value
                    * W_min
                    * W_max
                SWVT ID
                    * pk

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vSWVT = None
            vSWVT=pd.merge(self.dataFrames['SWVT'],self.dataFrames['SWVT_ROWT'],left_on='pk',right_on='fk')
            vSWVT['ZEIT']=pd.to_numeric(vSWVT['ZEIT']) 
            vSWVT['W']=pd.to_numeric(vSWVT['W']) 
            vSWVT['ZEIT_RANG']=vSWVT.groupby(['pk_x'])['ZEIT'].rank(ascending=True)
            #
            vSWVT_g=vSWVT.groupby(['pk_x'], as_index=False).agg({'W':[np.min,np.max]})
            vSWVT_g.columns= [tup[0]+tup[1] for tup in zip(vSWVT_g.columns.get_level_values(0),vSWVT_g.columns.get_level_values(1))]
            vSWVT_g.rename(columns={'Wamin':'W_min','Wamax':'W_max'},inplace=True)
            #
            vSWVT=pd.merge(vSWVT,vSWVT_g,left_on='pk_x',right_on='pk_x')
            #
            vSWVT=vSWVT[vSWVT['ZEIT_RANG']==1]
            #
            vSWVT=vSWVT[['NAME','BESCHREIBUNG','INTPOL','ZEITOPTION','W','W_min','W_max','pk_x']]
            #
            vSWVT.rename(columns={'pk_x':'pk'},inplace=True)
                                 
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
            return vSWVT   


    def _vRUES(self):
        """One row per RUES (per Übergangssymbol).

        1 Zeile für jede Definition(jeden Eingang).
        1 Zeile für jede Referenz einer Definition (jeden Ausgang).
        Der Eingang muss nicht mit einem Signal versorgt  sein.
        Der Ausgang muss nicht per       Signal verwendet sein.

        Returns:
            columns
                RUES
                    * IDUE: Name (eindeutige ID) der Übergangsstelle; bei IOTYP=3: IDUE kann offenbar undefiniert sein oder einen anderen nicht nachvollziehbaren Wert tragen; eingebbar in der GUI ist IDUE nur bei IOTYP=1 
                    * IOTYP:  0=undefiniert|1=Eingang|3=Ausgang
                    * rkRUES: bei IOTYP=3: Verweis auf referenzierte Übergangsstelle; -1 sonst

                    * IDUE_rkRUES: bei IOTYP=3: Name (eindeutige ID) der referenzierten Übergangsstelle
                    * IOTYP_rkRUES: bei IOTYP=3: Typ der referenzierten Übergangsstelle

                    * Kn: Knotenname der RUES im Sinne eines Knoten-Kanten-Modells; IDUE bei IOTYP=1 und IDUE_rkRUES bei IOTYP=3

                CONT
                    * CONT
                    * ID

                    * CONT_rkRUES: CONT der  referenzierten Übergangsstelle
                    * ID_rkRUES: CONT ID der referenzierten Übergangsstelle

                RUES IDs
                    * pk
                    * tk

        Raises:
            XmError

        >>> import pandas as pd             
        >>> # ---
        >>> xm=xms['DHNetwork']
        >>> # ---             
        >>> vRUES=xm.dataFrames['vRUES']   
        >>> pd.set_option('display.width', 333)
        >>> pd.set_option('display.max_columns',None)
        >>> pd.set_option('display.max_rows',None)
        >>> vRUES.sort_values(by=['Kn','IOTYP'])[[ # pro Kn oten steht zuerst die Definition, dann die Referenz(en)
        ...      'Kn'
        ...     ,'IOTYP'       
        ...     ,'IDUE' # zur Kontrolle       
        ...     ,'CONT'       
        ...     ]].sort_index()
                       Kn IOTYP          IDUE                 CONT
        0      Leck_1_Ein     1    Leck_1_Ein    AGFW Symposium DH
        1      Leck_2_Ein     1    Leck_2_Ein    AGFW Symposium DH
        2      Leck_3_Ein     1    Leck_3_Ein    AGFW Symposium DH
        3             wNA     1           wNA    AGFW Symposium DH
        4             wNB     1           wNB    AGFW Symposium DH
        5             wNC     1           wNC    AGFW Symposium DH
        6        vorOrtNA     1      vorOrtNA    AGFW Symposium DH
        7        wDH_RD_A     1      wDH_RD_A    AGFW Symposium DH
        8        wDH_MD_A     1      wDH_MD_A    AGFW Symposium DH
        9     wDH_BA_A_RD     1   wDH_BA_A_RD    AGFW Symposium DH
        10    wDH_BA_A_RD     3           NaN    AGFW Symposium DH
        11    wDH_BA_A_MD     1   wDH_BA_A_MD    AGFW Symposium DH
        12            dpA     1           dpA    AGFW Symposium DH
        13             qB     1            qB    AGFW Symposium DH
        14             qC     1            qC    AGFW Symposium DH
        15       vorOrtNA     3           NaN    AGFW Symposium DH
        16         wNAEin     1        wNAEin    AGFW Symposium DH
        17       vorOrtNB     1      vorOrtNB    AGFW Symposium DH
        18       vorOrtNB     3           NaN    AGFW Symposium DH
        19         wNBEin     1        wNBEin    AGFW Symposium DH
        20       vorOrtNC     1      vorOrtNC    AGFW Symposium DH
        21       vorOrtNC     3           NaN    AGFW Symposium DH
        22         wNCEin     1        wNCEin    AGFW Symposium DH
        23          wLast     1         wLast    AGFW Symposium DH
        24          wTRST     1         wTRST    AGFW Symposium DH
        25     Leck_Menge     1    Leck_Menge    AGFW Symposium DH
        26        Leck_VL     1       Leck_VL    AGFW Symposium DH
        27        Leck_RL     1       Leck_RL    AGFW Symposium DH
        28              0     1             0  Diverse Steuerungen
        29              1     1             1  Diverse Steuerungen
        30           ADum     1          ADum  Diverse Steuerungen
        31           ADum     3           NaN  Diverse Steuerungen
        32           ADum     3           NaN  Diverse Steuerungen
        33           ADum     3           NaN  Diverse Steuerungen
        34     Leck_Menge     3           NaN  Diverse Steuerungen
        35     Leck_Menge     3           NaN  Diverse Steuerungen
        36     Leck_Menge     3           NaN  Diverse Steuerungen
        37     Leck_Menge     3           NaN  Diverse Steuerungen
        38     Leck_Menge     3           NaN  Diverse Steuerungen
        39     Leck_Menge     3           NaN  Diverse Steuerungen
        40              1     3           NaN  Diverse Steuerungen
        41              1     3           NaN  Diverse Steuerungen
        42              1     3           NaN  Diverse Steuerungen
        43              1     3           NaN  Diverse Steuerungen
        44              1     3           NaN  Diverse Steuerungen
        45              1     3           NaN  Diverse Steuerungen
        46           ADum     3          ADum  Diverse Steuerungen
        47              0     3     NTRx1xEin  Diverse Steuerungen
        48              0     3     NTRx1xEin  Diverse Steuerungen
        49           ADum     3          ADum  Diverse Steuerungen
        50              0     3     NTRx1xAus  Diverse Steuerungen
        51           ADum     3          ADum  Diverse Steuerungen
        52              0     3     NTRx1xAus  Diverse Steuerungen
        53           ADum     3          ADum  Diverse Steuerungen
        54              0     3     NTRx3xAus  Diverse Steuerungen
        55           ADum     3          ADum  Diverse Steuerungen
        56              0     3     NTRx3xAus  Diverse Steuerungen
        57           ADum     3          ADum  Diverse Steuerungen
        58              0     3     NTRx3xEin  Diverse Steuerungen
        59           ADum     3          ADum  Diverse Steuerungen
        60              0     3     NTRx3xEin  Diverse Steuerungen
        61           ADum     3          ADum  Diverse Steuerungen
        62              0     3     NTRx2xAus  Diverse Steuerungen
        63           ADum     3          ADum  Diverse Steuerungen
        64              0     3     NTRx2xAus  Diverse Steuerungen
        65           ADum     3          ADum  Diverse Steuerungen
        66              0     3     NTRx2xEin  Diverse Steuerungen
        67           ADum     3          ADum  Diverse Steuerungen
        68              0     3     NTRx2xEin  Diverse Steuerungen
        69           ADum     3          ADum  Diverse Steuerungen
        70      yDH_dp2_A     3           NaN  Diverse Steuerungen
        71       wDH_MD_A     3           NaN  Diverse Steuerungen
        72   wDH_MD_A_ERO     1  wDH_MD_A_ERO  Diverse Steuerungen
        73       wDH_RD_A     3           NaN  Diverse Steuerungen
        74   wDH_RD_A_ERO     1  wDH_RD_A_ERO  Diverse Steuerungen
        75   wDH_RD_A_ERO     3           NaN  Diverse Steuerungen
        76    wDH_BA_A_RD     3           NaN  Diverse Steuerungen
        77   wDH_MD_A_ERO     3           NaN  Diverse Steuerungen
        78    wDH_BA_A_MD     3           NaN  Diverse Steuerungen
        79          wLast     3           NaN  Diverse Steuerungen
        80              1     3           NaN  Diverse Steuerungen
        81          wTRST     3           NaN  Diverse Steuerungen
        82              1     3           NaN  Diverse Steuerungen
        83            100     1           100  Diverse Steuerungen
        84     Leck_1_Ein     3           NaN  Diverse Steuerungen
        85        Leck_VL     3           NaN  Diverse Steuerungen
        86           ADum     3           NaN  Diverse Steuerungen
        87           ADum     3           NaN  Diverse Steuerungen
        88     Leck_1_Ein     3           NaN  Diverse Steuerungen
        89        Leck_RL     3           NaN  Diverse Steuerungen
        90           ADum     3           NaN  Diverse Steuerungen
        91           ADum     3           NaN  Diverse Steuerungen
        92        Leck_RL     3           NaN  Diverse Steuerungen
        93     Leck_2_Ein     3           NaN  Diverse Steuerungen
        94     Leck_2_Ein     3           NaN  Diverse Steuerungen
        95        Leck_VL     3           NaN  Diverse Steuerungen
        96           ADum     3           NaN  Diverse Steuerungen
        97           ADum     3           NaN  Diverse Steuerungen
        98           ADum     3           NaN  Diverse Steuerungen
        99           ADum     3           NaN  Diverse Steuerungen
        100       Leck_RL     3           NaN  Diverse Steuerungen
        101    Leck_3_Ein     3           NaN  Diverse Steuerungen
        102    Leck_3_Ein     3           NaN  Diverse Steuerungen
        103       Leck_VL     3           NaN  Diverse Steuerungen
        104          ADum     3           NaN  Diverse Steuerungen
        105        wNAEin     3           NaN                    A
        106           wNA     3           NaN                    A
        107        wNBEin     3           NaN                    A
        108          ADum     3           NaN                    A
        109      vorOrtNC     3           NaN                    A
        110          ADum     3           NaN                    A
        111           dpA     3           NaN                    A
        112      vorOrtNC     3           NaN                    A
        113        wNBEin     3           NaN                    B
        114           wNB     3           NaN                    B
        115        wNBEin     3           NaN                    B
        116          ADum     3           NaN                    B
        117      vorOrtNB     3           NaN                    B
        118          ADum     3           NaN                    B
        119            qB     3           NaN                    B
        120      vorOrtNB     3           NaN                    B
        121        wNCEin     3           NaN                    C
        122           wNC     3           NaN                    C
        123        wNCEin     3           NaN                    C
        124          ADum     3           NaN                    C
        125          ADum     3           NaN                    C
        126      vorOrtNC     3           NaN                    C
        127            qC     3           NaN                    C
        128      vorOrtNC     3           NaN                    C
        129        QDHGes     1        QDHGes        Sekundärwerte
        130     yDH_dp2_A     1     yDH_dp2_A        Sekundärwerte
        131     yDH_dp2_A     3           NaN        Sekundärwerte
        132     yDH_pMD_A     1     yDH_pMD_A        Sekundärwerte
        133     yDH_pRL_A     1     yDH_pRL_A        Sekundärwerte
        134     yDH_pRL_A     3           NaN        Sekundärwerte
        135          yUWM     1          yUWM        Sekundärwerte
        136       wLastMW     1       wLastMW        Sekundärwerte
        137       yLastMW     1       yLastMW        Sekundärwerte
        138       yLastMW     3           NaN        Sekundärwerte
        139       wLastMW     3           NaN        Sekundärwerte
        140       dLastMW     1       dLastMW        Sekundärwerte
        141          yAMW     1          yAMW        Sekundärwerte
        142          yBMW     1          yBMW        Sekundärwerte
        143          yCMW     1          yCMW        Sekundärwerte
        144       yLastMW     3           NaN        Sekundärwerte
        145          yAMW     3           NaN        Sekundärwerte
        146           100     3           NaN        Sekundärwerte
        147       yLastMW     3           NaN        Sekundärwerte
        148          yBMW     3           NaN        Sekundärwerte
        149           100     3           NaN        Sekundärwerte
        150       yLastMW     3           NaN        Sekundärwerte
        151          yCMW     3           NaN        Sekundärwerte
        152           100     3           NaN        Sekundärwerte
        153       dUWMMin     1       dUWMMin        Sekundärwerte
        154       dUWMMax     1       dUWMMax        Sekundärwerte
        155      yUWMLast     1      yUWMLast        Sekundärwerte
        156          yUWM     3           NaN        Sekundärwerte
        >>> # ---
        >>> vRUESDefs=vRUES.loc[vRUES['IOTYP']=='1']
        >>> # für Defs die Originaldefinition finden ...
        >>> vRUESDefsCrgl=pd.merge(vRUESDefs,xm.dataFrames['CRGL'],left_on='pk',right_on='fkKk',suffixes=('','_CRGL'),how='left') # für alle sollte eine Referenz gefunden werden ...
        >>> vRUESDefsCrgl.sort_values(by=['Kn'])[[
        ...      'Kn'       
        ...     ,'CONT'       
        ...     ,'fkKi'       
        ...     ]]
                      Kn                 CONT                 fkKi
        24             0  Diverse Steuerungen  5486870913514090048
        25             1  Diverse Steuerungen  5377084992102722959
        29           100  Diverse Steuerungen  5055797784689898209
        26          ADum  Diverse Steuerungen  5408457159782566744
        0     Leck_1_Ein    AGFW Symposium DH  5706111677806224290
        1     Leck_2_Ein    AGFW Symposium DH  4704869532416514405
        2     Leck_3_Ein    AGFW Symposium DH  4808434710442736644
        21    Leck_Menge    AGFW Symposium DH  5390061625789905096
        23       Leck_RL    AGFW Symposium DH  5644481773793849108
        22       Leck_VL    AGFW Symposium DH  4880440884169110259
        30        QDHGes        Sekundärwerte  5345716897595312355
        37       dLastMW        Sekundärwerte  4611793887272861500
        42       dUWMMax        Sekundärwerte  4672771372882677276
        41       dUWMMin        Sekundärwerte  5463544828758888616
        11           dpA    AGFW Symposium DH  4849866990207957614
        12            qB    AGFW Symposium DH  4771725364091629759
        13            qC    AGFW Symposium DH  4978409087288292434
        6       vorOrtNA    AGFW Symposium DH  5194343043762135519
        15      vorOrtNB    AGFW Symposium DH  4705080808435797677
        17      vorOrtNC    AGFW Symposium DH  5620348872583735825
        10   wDH_BA_A_MD    AGFW Symposium DH  4873987359791313088
        9    wDH_BA_A_RD    AGFW Symposium DH  5322890886142492590
        8       wDH_MD_A    AGFW Symposium DH  5093705160009582980
        27  wDH_MD_A_ERO  Diverse Steuerungen  5729434727271745948
        7       wDH_RD_A    AGFW Symposium DH  4622192786925004485
        28  wDH_RD_A_ERO  Diverse Steuerungen  4980847179402621205
        19         wLast    AGFW Symposium DH  5741660563170722352
        35       wLastMW        Sekundärwerte  4833634373103605497
        3            wNA    AGFW Symposium DH  4991855568438544033
        14        wNAEin    AGFW Symposium DH  4742316320267545359
        4            wNB    AGFW Symposium DH  4658075570394029953
        16        wNBEin    AGFW Symposium DH  5013654033692161674
        5            wNC    AGFW Symposium DH  5240575308071562858
        18        wNCEin    AGFW Symposium DH  5670691593026035398
        20         wTRST    AGFW Symposium DH  5547011912763631199
        38          yAMW        Sekundärwerte  4726758453134789052
        39          yBMW        Sekundärwerte  5528896084200811302
        40          yCMW        Sekundärwerte  5274276049082272588
        31     yDH_dp2_A        Sekundärwerte  5512879293670562022
        32     yDH_pMD_A        Sekundärwerte  5255402486218254174
        33     yDH_pRL_A        Sekundärwerte  4639451967914783278
        36       yLastMW        Sekundärwerte  4817923247686815456
        34          yUWM        Sekundärwerte  5008805081156446169
        43      yUWMLast        Sekundärwerte  5574611204646558662
        >>> vRUESDefsCrglRuesDef=pd.merge(vRUESDefsCrgl,vRUES,left_on='fkKi',right_on='pk',suffixes=('','_vRUES'),how='inner') # für die RUES-definierten RUES sollte eine Referenz gefunden werden ...
        >>> vRUESDefsCrglRuesDef.sort_values(by=['Kn'])[[
        ...      'Kn'       
        ...     ,'CONT'       
        ...     ,'fkKi'       
        ...     ,'Kn_vRUES'
        ...     ]]
                     Kn                 CONT                 fkKi  Kn_vRUES
        0  wDH_RD_A_ERO  Diverse Steuerungen  4980847179402621205  wDH_RD_A
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:      
            vRUES=None                  
                         
            vRUES=pd.merge(self.dataFrames['RUES'],self.dataFrames['RUES_BZ'],left_on='pk',right_on='fk',suffixes=('','_BZ'))
            vRUES=pd.merge(vRUES,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=('','_CONT'))

            colsEff=vRUES.columns.tolist()
            colsEff.remove('GEOM')
            colsEff.remove('FONT')
            colsEff.remove('GRAF_CONT')

            vRUES=vRUES.filter(items=colsEff,axis=1)

            vRUES.rename(columns=
            {'NAME': 'CONT',}
            ,inplace=True)

            vRUES=vRUES[[
             
             'IDUE'            
            ,'IOTYP'
            ,'rkRUES'

            ,'CONT'
            ,'ID'

            ,'pk'
            ,'rk'
            ]]

            # zu jeder Referenz (ein potentieller Ausgang - Ki eines potentiellen Signals) die Definition suchen (Kk eines Signals)
            vRUES=pd.merge(vRUES,vRUES,how='left',left_on='rkRUES',right_on='pk',suffixes=('','_rkRUES'))

            vRUES=vRUES[[
             
             'IDUE'
            ,'IOTYP'
            ,'rkRUES'

            ,'IDUE_rkRUES'            
            ,'IOTYP_rkRUES'

            ,'CONT'
            ,'ID'

            ,'CONT_rkRUES'
            ,'ID_rkRUES'

            ,'pk'
            ,'rk'
            ]]
           
            vRUES['Kn']  = vRUES.apply(lambda row: row.IDUE if row.IOTYP=='1' else row.IDUE_rkRUES, axis=1)


            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vRUES,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vRUES=pd.DataFrame()              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vRUES

    def _vRSLW(self,vSWVT=None):
        """One row per RSLW.

        Args:
            * vSWVT 

        Returns:
            columns
                RSLW
                    * KA
                    * BESCHREIBUNG
                    * INDWBG
                    * WMIN
                    * WMAX
                    * INDWNO

                RSLW BZ
                    * INDSLW
                    * SLWKON

                CONT
                    * CONT
                    * ID
                    * CONT_PARENT     

                SWVT
                    * SWVT
                    * SWVT_Count (Anzahl der RSLW-Referenzierungen der SWVT; 0, wenn keine SWVT angegeben; INDSLW wird bei der Ermittlung nicht ausgewertet)
                    * BESCHREIBUNG_SWVT
                    * INTPOL
                    * ZEITOPTION

                    SERIES
                        * W: 1st Value
                        * W_min
                        * W_max

                RSLW IDs
                    * pk
                    * tk

        Raises:
            XmError

        >>> import pandas as pd             
        >>> # ---
        >>> xm=xms['DHNetwork']
        >>> # ---             
        >>> vRSLW=xm.dataFrames['vRSLW']
        >>> vRSLW[[
        ...  'KA'
        ... ,'BESCHREIBUNG'
        ... ,'INDSLW'
        ... ,'CONT'
        ... ,'CONT_PARENT'
        ... ,'SWVT'
        ... ]].sort_values(by=['KA'])
                     KA          BESCHREIBUNG INDSLW                 CONT          CONT_PARENT        SWVT
        20            0                  None      0  Diverse Steuerungen    AGFW Symposium DH         NaN
        21            1                  None      0  Diverse Steuerungen    AGFW Symposium DH         NaN
        23          100                  None      0  Diverse Steuerungen    AGFW Symposium DH         NaN
        22         ADum          Analog Dummy      0  Diverse Steuerungen    AGFW Symposium DH         NaN
        0    Leck_1_Ein            Leck_1_Ein      1    AGFW Symposium DH    AGFW Symposium DH      zLeck1
        1    Leck_2_Ein            Leck_2_Ein      1    AGFW Symposium DH    AGFW Symposium DH      zLeck2
        2    Leck_3_Ein            Leck_3_Ein      1    AGFW Symposium DH    AGFW Symposium DH      zLeck3
        11   Leck_Menge            Leck_Menge      1    AGFW Symposium DH    AGFW Symposium DH  zLeckMenge
        13      Leck_RL               Leck_RL      1    AGFW Symposium DH    AGFW Symposium DH    zLeck_RL
        12      Leck_VL               Leck_VL      1    AGFW Symposium DH    AGFW Symposium DH    zLeck_VL
        24           cp                   NaN      0        Sekundärwerte  Diverse Steuerungen         NaN
        17          dpA                   dpA      1    AGFW Symposium DH    AGFW Symposium DH         dpA
        18           qB                    qB      1    AGFW Symposium DH    AGFW Symposium DH          qB
        19           qC                    qC      1    AGFW Symposium DH    AGFW Symposium DH          qC
        6      vorOrtNA              vorOrtNA      1    AGFW Symposium DH    AGFW Symposium DH    vorOrtNA
        7      vorOrtNB              vorOrtNB      1    AGFW Symposium DH    AGFW Symposium DH    vorOrtNB
        8      vorOrtNC              vorOrtNC      1    AGFW Symposium DH    AGFW Symposium DH    vorOrtNC
        16  wDH_BA_A_RD  wDH_BA_A; 1=RD; 0=MD      1    AGFW Symposium DH    AGFW Symposium DH    wDH_BA_A
        15     wDH_MD_A              wDH_MD_A      1    AGFW Symposium DH    AGFW Symposium DH    wDH_MD_A
        14     wDH_RD_A              wDH_RD_A      1    AGFW Symposium DH    AGFW Symposium DH    wDH_RD_A
        9         wLast                 wLast      1    AGFW Symposium DH    AGFW Symposium DH       wLast
        3           wNA                   wNA      1    AGFW Symposium DH    AGFW Symposium DH         wNA
        4           wNB                   wNB      1    AGFW Symposium DH    AGFW Symposium DH         wNB
        5           wNC                   wNC      1    AGFW Symposium DH    AGFW Symposium DH         wNC
        10        wTRST                 wTRST      1    AGFW Symposium DH    AGFW Symposium DH       wTRSP
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:      
            vRSLW=None                  
                         
            vRSLW=pd.merge(self.dataFrames['RSLW'],self.dataFrames['RSLW_BZ'],left_on='pk',right_on='fk')
            vRSLW=pd.merge(vRSLW,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk')

            vRSLW=vRSLW[[
            # RSLW
            'KA'
            ,'BESCHREIBUNG'
            ,'INDWBG'
            ,'WMIN','WMAX'
            ,'INDWNO'
            # RSLW BZ
            ,'INDSLW','SLWKON','fkSWVT' 
            # CONT
            ,'NAME','ID','rkPARENT'
            # RSLW IDs   
            ,'pk_x', 'tk_x'
                 ]]
            vRSLW.rename(columns=
            {
             'NAME': 'CONT'}
            ,inplace=True)

            vRSLW=pd.merge(vRSLW,self.dataFrames['CONT'],left_on='rkPARENT',right_on='pk',suffixes=('','_PARENT'))
            vRSLW=vRSLW[[
            # RSLW
            'KA'
            ,'BESCHREIBUNG'
            ,'INDWBG'
            ,'WMIN','WMAX'
            ,'INDWNO'
            # RSLW BZ
            ,'INDSLW','SLWKON','fkSWVT' 
            # CONT
            ,'CONT','ID','NAME'#,'ID_PARENT'
            # RSLW IDs   
            ,'pk_x', 'tk_x'
                 ]]
            vRSLW.rename(columns=
            {
             'NAME': 'CONT_PARENT'}
            ,inplace=True)

            vRSLW=pd.merge(vRSLW,vSWVT,left_on='fkSWVT',right_on='pk',how='left')

            vRSLW=vRSLW[[
            # RSLW
            'KA'
            ,'BESCHREIBUNG_x'
            ,'INDWBG'
            ,'WMIN','WMAX'
            ,'INDWNO'
            # RSLW BZ
            ,'INDSLW','SLWKON'
            # CONT
            , 'CONT','ID','CONT_PARENT'                            
            # vSWVT
            ,'NAME', 'BESCHREIBUNG_y', 'W', 'W_min', 'W_max', 'INTPOL','ZEITOPTION'
            # RSLW IDs   
            ,'pk_x', 'tk_x'
                 ]]            

            vRSLW.rename(columns=
            {'BESCHREIBUNG_x': 'BESCHREIBUNG',
             'BESCHREIBUNG_y': 'BESCHREIBUNG_SWVT',
            # 'NAME_x': 'CONT',
             'NAME': 'SWVT',
             'pk_x': 'pk',
             'tk_x': 'tk'}
            ,inplace=True)

            vRSLW=vRSLW[[
            # RSLW
            'KA'
            ,'BESCHREIBUNG'
            ,'INDWBG'
            ,'WMIN','WMAX'
            ,'INDWNO'
            # RSLW BZ
            ,'INDSLW','SLWKON'
            # CONT
            ,'CONT','ID','CONT_PARENT'               
            # vSWVT
            ,'SWVT', 'BESCHREIBUNG_SWVT', 'W', 'W_min', 'W_max', 'INTPOL','ZEITOPTION'
            # RSLW IDs   
            ,'pk','tk'
                 ]]          

            # Anzahl der RSLW-Referenzierungen einer SWVT an jedem RSLW merken
            go=vRSLW.groupby(['SWVT']).count()            
            vRSLW=pd.merge(vRSLW,go.reset_index()[['SWVT','pk']].rename(columns={'pk':'SWVT_Count'}),how='left')
            fillValues={'SWVT_Count':0}
            vRSLW=vRSLW.fillna(value=fillValues)
            vRSLW=vRSLW.astype({'SWVT_Count': 'int32'},errors='ignore')
            vRSLW=vRSLW[[
            # RSLW
            'KA'
            ,'BESCHREIBUNG'
            ,'INDWBG'
            ,'WMIN','WMAX'
            ,'INDWNO'
            # RSLW BZ
            ,'INDSLW','SLWKON'
            # CONT
            ,'CONT','ID','CONT_PARENT'               
            # vSWVT
            ,'SWVT','SWVT_Count','BESCHREIBUNG_SWVT', 'W', 'W_min', 'W_max', 'INTPOL','ZEITOPTION'
            # RSLW IDs   
            ,'pk','tk'
                 ]]          
            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vRSLW,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vRSLW=pd.DataFrame()              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vRSLW

    def _vRSTN(self,vSWVT=None):
        """One row per RSTN.

        Returns:
            columns: see code

        Raises:
            XmError

        >>> # -q -m 0 -s vRSTN  -w DHNetwork  -y yes -z no
        >>> import pandas as pd             
        >>> # ---
        >>> xm=xms['DHNetwork']
        >>> # ---              
        >>> vRSTN=xm.dataFrames['vRSTN']        
        >>> vRSTN['RART_TYP']=vRSTN['RART_TYP'].str[:10]+'...' # zu lange Ausgabezeile vermeiden
        >>> pd.set_option('display.width', 333)
        >>> pd.set_option('display.max_columns',None)
        >>> pd.set_option('display.max_rows',None)
        >>> vRSTN[[
        ...  'CONT'
        ... ,'CONT_PARENT'
        ... ,'KA'
        ... ,'BESCHREIBUNG'            
        ... ,'ITYP_OBJTYPE'
        ... ,'ITYP_OBJATTR'    
        ... ,'Chk'
        ... ,'ik_Chk'
        ... ,'OBJTYPE'
        ... ,'NAME_i'
        ... ,'NAME_k'     
        ... ,'CONT_i'  
        ... ,'TABL_Chk'      
        ... ,'TABL'
        ... ,'KNOT'
        ... ,'RART'
        ... ,'RART_TYP'
        ... ,'RARTPG'
        ... ,'RCPL' 
        ... ,'RCPL_KNOT1'
        ... ,'RCPL_KNOT2'
        ... ,'NAME_i_PUMP'
        ... ,'NAME_k_PUMP'       
        ... ]].sort_values(by=['ITYP_OBJTYPE','ITYP_OBJATTR','CONT','KA']).sort_index()
                           CONT        CONT_PARENT        KA  BESCHREIBUNG ITYP_OBJTYPE ITYP_OBJATTR  Chk  ik_Chk OBJTYPE  NAME_i    NAME_k             CONT_i  TABL_Chk  TABL       KNOT     RART       RART_TYP RARTPG RCPL RCPL_KNOT1 RCPL_KNOT2 NAME_i_PUMP NAME_k_PUMP
        0                     A  AGFW Symposium DH  wNA_RSTN           NaN         PUMP            N    1     1.0    PUMP  R-A-SS    R-A-DS                  A       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        1                     A  AGFW Symposium DH   KA-0046           NaN         RART         SOLL    1     NaN     NaN     NaN       NaN                NaN       NaN   NaN        NaN   A_dpdS  Differenzd...    NaN  NaN        NaN        NaN         NaN         NaN
        2                     A  AGFW Symposium DH   KA-0044           NaN         PGRP        DEAKT    1     1.0    PGRP  R-A-SS  R-A-DS-2                  A       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        3                     A  AGFW Symposium DH   KA-0045           NaN         PGRP        AKTIV    1     1.0    PGRP  R-A-SS  R-A-DS-2                  A       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        4                     B  AGFW Symposium DH  wNB_RSTN           NaN         PUMP            N    1     1.0    PUMP  R-B-SS    R-B-DS                  B       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        5                     B  AGFW Symposium DH   KA-0053           NaN         PGRP        DEAKT    1     1.0    PGRP  R-B-SS  R-B-DS-2                  B       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        6                     B  AGFW Symposium DH   KA-0057           NaN         PGRP        AKTIV    1     1.0    PGRP  R-B-SS  R-B-DS-2                  B       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        7                     B  AGFW Symposium DH   KA-0058           NaN         RART         SOLL    1     NaN     NaN     NaN       NaN                NaN       NaN   NaN        NaN  B_Menge  Durchfluss...    NaN  NaN        NaN        NaN         NaN         NaN
        8                     C  AGFW Symposium DH  wNC_RSTN           NaN         PUMP            N    1     1.0    PUMP  R-C-SS    R-C-DS                  C       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        9                     C  AGFW Symposium DH   KA-0059           NaN         PGRP        DEAKT    1     1.0    PGRP  R-C-SS  R-C-DS-2                  C       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        10                    C  AGFW Symposium DH   KA-0060           NaN         PGRP        AKTIV    1     1.0    PGRP  R-C-SS  R-C-DS-2                  C       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        11                    C  AGFW Symposium DH   KA-0061           NaN         RART         SOLL    1     NaN     NaN     NaN       NaN                NaN       NaN   NaN        NaN  C_Menge  Durchfluss...    NaN  NaN        NaN        NaN         NaN         NaN
        12  Diverse Steuerungen  AGFW Symposium DH   KA-0004           NaN         LFKT         SOLL    1     NaN     NaN     NaN       NaN                NaN       1.0  LFKT        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        13  Diverse Steuerungen  AGFW Symposium DH   KA-0005           NaN         TEVT         SOLL    1     NaN     NaN     NaN       NaN                NaN       2.0  TRST        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        14  Diverse Steuerungen  AGFW Symposium DH   KA-0006           NaN         ROHR      LECKEIN    1     1.0    ROHR  V-1905    V-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        15  Diverse Steuerungen  AGFW Symposium DH   KA-0008           NaN         ROHR      LECKAUS    1     1.0    ROHR  V-1905    V-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        16  Diverse Steuerungen  AGFW Symposium DH   KA-0003           NaN         ROHR      LECKEIN    1     1.0    ROHR  R-1905    R-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        17  Diverse Steuerungen  AGFW Symposium DH   KA-0007           NaN         ROHR      LECKAUS    1     1.0    ROHR  R-1905    R-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        18  Diverse Steuerungen  AGFW Symposium DH   KA-0013           NaN         ROHR      LECKEIN    1     1.0    ROHR  V-1110    V-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        19  Diverse Steuerungen  AGFW Symposium DH   KA-0014           NaN         ROHR      LECKEIN    1     1.0    ROHR  R-1110    R-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        20  Diverse Steuerungen  AGFW Symposium DH   KA-0015           NaN         ROHR      LECKAUS    1     1.0    ROHR  V-1110    V-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        21  Diverse Steuerungen  AGFW Symposium DH   KA-0016           NaN         ROHR      LECKAUS    1     1.0    ROHR  R-1110    R-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        22  Diverse Steuerungen  AGFW Symposium DH   KA-0021           NaN         ROHR      LECKEIN    1     1.0    ROHR  V-3008    V-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        23  Diverse Steuerungen  AGFW Symposium DH   KA-0022           NaN         ROHR      LECKEIN    1     1.0    ROHR  R-3008    R-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        24  Diverse Steuerungen  AGFW Symposium DH   KA-0023           NaN         ROHR      LECKAUS    1     1.0    ROHR  V-3008    V-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        25  Diverse Steuerungen  AGFW Symposium DH   KA-0024           NaN         ROHR      LECKAUS    1     1.0    ROHR  R-3008    R-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        26  Diverse Steuerungen  AGFW Symposium DH   KA-0025           NaN         ROHR    LECKMENGE    1     1.0    ROHR  V-1905    V-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        27  Diverse Steuerungen  AGFW Symposium DH   KA-0027           NaN         ROHR    LECKMENGE    1     1.0    ROHR  R-1905    R-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        28  Diverse Steuerungen  AGFW Symposium DH   KA-0028           NaN         ROHR    LECKMENGE    1     1.0    ROHR  V-1110    V-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        29  Diverse Steuerungen  AGFW Symposium DH   KA-0029           NaN         ROHR    LECKMENGE    1     1.0    ROHR  R-1110    R-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        30  Diverse Steuerungen  AGFW Symposium DH   KA-0030           NaN         ROHR    LECKMENGE    1     1.0    ROHR  V-3008    V-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        31  Diverse Steuerungen  AGFW Symposium DH   KA-0031           NaN         ROHR    LECKMENGE    1     1.0    ROHR  R-3008    R-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        32  Diverse Steuerungen  AGFW Symposium DH   KA-0032  NTR_1_RL_Ein         ROHR           ZU    1     1.0    ROHR  R-1905    R-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        33  Diverse Steuerungen  AGFW Symposium DH   KA-0033  NTR_1_VL_Ein         ROHR           ZU    1     1.0    ROHR  V-1905    V-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        34  Diverse Steuerungen  AGFW Symposium DH   KA-0034  NTR_1_VL_Ein         ROHR          AUF    1     1.0    ROHR  V-1905    V-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        35  Diverse Steuerungen  AGFW Symposium DH   KA-0035  NTR_1_RL_Ein         ROHR          AUF    1     1.0    ROHR  R-1905    R-1906  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        36  Diverse Steuerungen  AGFW Symposium DH   KA-0036  NTR_3_Aus_VL         ROHR          AUF    1     1.0    ROHR  V-3008    V-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        37  Diverse Steuerungen  AGFW Symposium DH   KA-0037  NTR_3_Aus_RL         ROHR          AUF    1     1.0    ROHR  R-3008    R-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        38  Diverse Steuerungen  AGFW Symposium DH   KA-0038  NTR_3_Ein_VL         ROHR           ZU    1     1.0    ROHR  V-3008    V-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        39  Diverse Steuerungen  AGFW Symposium DH   KA-0039  NTR_3_Ein_RL         ROHR           ZU    1     1.0    ROHR  R-3008    R-3007  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        40  Diverse Steuerungen  AGFW Symposium DH   KA-0040  NTR_2_Aus_VL         ROHR          AUF    1     1.0    ROHR  V-1110    V-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        41  Diverse Steuerungen  AGFW Symposium DH   KA-0041  NTR_2_Aus_RL         ROHR          AUF    1     1.0    ROHR  R-1110    R-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        42  Diverse Steuerungen  AGFW Symposium DH   KA-0042  NTR_2_Ein_VL         ROHR           ZU    1     1.0    ROHR  V-1110    V-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        43  Diverse Steuerungen  AGFW Symposium DH   KA-0043  NTR_2_Ein_RL         ROHR           ZU    1     1.0    ROHR  R-1110    R-1111  AGFW Symposium DH       NaN   NaN        NaN      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        44  Diverse Steuerungen  AGFW Symposium DH   KA-0054           NaN         KNOT        PSOLL    1     NaN     NaN     NaN       NaN                NaN       NaN   NaN  A_DH_pDef      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        45  Diverse Steuerungen  AGFW Symposium DH   KA-0055           NaN         KNOT        PSOLL    1     NaN     NaN     NaN       NaN                NaN       NaN   NaN  A_DH_pDef      NaN            NaN    NaN  NaN        NaN        NaN         NaN         NaN
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:      
            vRSTN=None                  

            # BZ                         
            vRSTN=pd.merge(self.dataFrames['RSTN'],self.dataFrames['RSTN_BZ'],left_on='pk',right_on='fk',suffixes=('','_BZ'))
            colList=vRSTN.columns.tolist()

            # CONT
            vRSTN=pd.merge(vRSTN,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=('','_C'))
            vRSTN.rename(columns={'NAME':'CONT'},inplace=True)
            vRSTN=vRSTN.filter(items=colList+['CONT','ID','rkPARENT'])
            colList=vRSTN.columns.tolist()

            vRSTN=pd.merge(vRSTN,self.dataFrames['CONT'],left_on='rkPARENT',right_on='pk',suffixes=('','_CP'))
            vRSTN.rename(columns={'NAME':'CONT_PARENT'},inplace=True)
            vRSTN=vRSTN.filter(items=colList+['CONT_PARENT'])

            # ITYP
            sItyp='101=VENT_PHI | 102=VENT_AUF | 103=VENT_ZU | 104=VENT_HALT | 105=VENT_STOERFALL | 106=VENT_AUFZU | 107=VENT_DPHI | 108=VENT_FREIGABE | 201=PREG_PH | 301=DPRG_DPH | 401=MREG_PHI | 402=MREG_QM | 403=MREG_SOLL | 404=MREG_HALT | 411=MREG_BART_PHI | 412=MREG_BART_QM | 501=FWES_TEMP | 502=FWES_AUF | 503=FWES_ZU | 504=FWES_EIN | 505=FWES_AUS | 601=RART_SOLL | 701=PGRP_AKTIV | 702=PGRP_DEAKT | 703=PGRP_RART | 704=PGRP_PUAKT | 705=PGRP_PUDEA | 803=REGV_RART | 901=TABL_SOLL | 1002=ROHR_AUF | 1003=ROHR_ZU | 1006=ROHR_TRENN | 1008=ROHR_LECKEIN | 1009=ROHR_LECKAUS | 1010=ROHR_LECKEINAUS | 1011=ROHR_LECKORT | 1012=ROHR_LECKMENGE | 1101=PUMP_N | 1102=PUMP_EIN | 1103=PUMP_AUS | 1104=PUMP_HALT | 1105=PUMP_STOERFALL | 1106=PUMP_EINAUS | 1107=PUMP_DN | 1108=PUMP_ABSCHALT | 1109=PUMP_AUSFALL | 1201=OBEH_HSOLL | 1301=KNOT_PSOLL | 1401=KOMP_EIN | 1402=KOMP_AUS | 1403=KOMP_EINAUS | 1404=KOMP_QN | 1405=KOMP_N | 1406=KOMP_DP | 1407=KOMP_PK | 1501=GVWK_EIN | 1502=GVWK_AUS | 1503=GVWK_EINAUS | 1504=GVWK_TK | 1505=GVWK_W | 1510=RCPL_ROWT_AKT | 1511=RCPL_ROWT_SW'                       
            items=sItyp.split(sep='|')
            sItypDct=dict(zip([int(pair[0]) for pair in [item.split(sep='=') for item in items]]
                ,[pair[1].strip()  for pair in [item.split(sep='=') for item in items]]
                     ))
            logger.debug("{0:s}{1:s}".format(logStr,str(sItypDct))) 

            vRSTN['ITYP_TXT']=vRSTN.apply(lambda row: sItypDct[int(row.ITYP)] if int(row.ITYP) in sItypDct  else -1  , axis=1)
            vRSTN['ITYP_OBJTYPE']=vRSTN.apply(lambda row: row.TYP if str(row.ITYP_TXT).split(sep='_')[0] == 'TABL'  else str(row.ITYP_TXT).split(sep='_')[0]  , axis=1)
            vRSTN['ITYP_OBJATTR']=vRSTN.apply(lambda row: str(row.ITYP_TXT).split(sep='_')[1] , axis=1)
            
            #logger.debug("{0:s}{1:s}".format(logStr,str(vRSTN.columns.tolist()))) 

            vRSTN = vRSTN[[
                             'CONT'
                            ,'CONT_PARENT'
                            ,'KA'
                            ,'BESCHREIBUNG'    
                            #,'ITYP'     
                            #,'ITYP_TXT' 
                            #,'TYP'      
                            ,'ITYP_OBJTYPE'
                            ,'ITYP_OBJATTR'     
                            
                            , 'fkDPRG'
                            , 'fkFWES'
                            , 'fkGVWK'
                            , 'fkKNOT'
                            , 'fkKOMP'
                            , 'fkMREG'
                            , 'fkOBEH'
                            , 'fkPGRP'
                            , 'fkPREG'
                            , 'fkPUMP'
                            , 'fkPUMPPG'
                            , 'fkRART'
                            , 'fkRARTPG'
                            , 'fkRCPL'
                            , 'fkRCPL_ROWT'
                            , 'fkREGV'
                            , 'fkROHR'
                            , 'fkVENT'
                            , 'pk'                                     
                            , 'fkLFKT', 'fkPHI1', 'fkPUMD', 'fkPVAR', 'fkQVAR', 'fkSWVT', 'fkTEVT', 'fkWEVT'                                       
                        ]]

            # VBEL ---          
            lookUpVbel=self.dataFrames['vVBEL'][['NAME_i','NAME_k','CONT_i']]
            lookUpCols=lookUpVbel.columns.tolist()
            lookUpVbel.reset_index(inplace=True)

            lookUpKeys=['fkROHR', 'fkPGRP', 'fkPUMP', 'fkVENT' , 'fkFWES', 'fkREGV']  
            lookUpPosts=['_'+lookUpKey.lstrip('fk') for lookUpKey in lookUpKeys]
            lookUpObjtypes=[lookUpPost.lstrip('_') for lookUpPost in lookUpPosts]

            # pruefen, ob mehrere VBEL-Referenzschluessel hinterlegt sind
            vRSTN['ik_Chk']=vRSTN[lookUpKeys][vRSTN[lookUpKeys].astype('int64')>0].count(axis=1)             
            # Information auf unDef zurücksetzen, wenn es sich gar nicht um ein VBEL-Stellobjekt handelt                          
            vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(lookUpObjtypes)) & ~(vRSTN['ik_Chk'].isnull()),'ik_Chk']=None 
                      
            for lookUpKey,lookUpPost,lookUpObjtype in zip(lookUpKeys,lookUpPosts,lookUpObjtypes):      
                # es kommen pro VBEL neue Spalten hinzu ...
                vRSTN=pd.merge(vRSTN,lookUpVbel,left_on=[lookUpKey,'ITYP_OBJTYPE'],right_on=['OBJID','OBJTYPE'],suffixes=('',lookUpPost),how='left')  # nur 1 Treffer (1 Zeile) moeglich ...
                # ... allerdings pro fkXXXX, wenn mehrere voneinander verschiedene fkXXXX im RSTN belegt sind (ik_Chk ist dann >1) 
                # 1 RSTN erzeugt dann mehrere Zeilen: das ist falsch und wird weiter unten korrigiert ... (siehe Filtern ...)
              
            # die erzeugten Spalten auf eine ziehen und dann loeschen ...                     
            for lookUpCol in lookUpCols:                
                lookUpColsGen=[lookUpCol+lookUpPost for lookUpKey,lookUpPost in zip(lookUpKeys[1:],lookUpPosts[1:])]               
                vRSTN[lookUpCol] = vRSTN[[lookUpCol]+lookUpColsGen].bfill(axis=1).iloc[:, 0] # zugewiesen wird die (erste) Nicht-Nul Spalte 
                vRSTN=vRSTN.drop(lookUpColsGen, axis=1)
                               
                # belegte Spalte auf unDef zurücksetzen, wenn es sich gar nicht um ein VBEL-Stellobjekt handelt                               
                vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(lookUpObjtypes)) &  ~(vRSTN[lookUpCol].isnull()),lookUpCol]=None # Referenz vorhanden und gültig - aber irrelevant     
                
            
            # OBJTYPE in Ergebnis
            lookUpColsGen=['OBJTYPE'+lookUpPost for lookUpPost in lookUpPosts[1:]]               
            vRSTN['OBJTYPE'] = vRSTN[['OBJTYPE']+lookUpColsGen].bfill(axis=1).iloc[:, 0] # zugewiesen wird die (erste) Nicht-Nul Spalte 
            vRSTN=vRSTN.drop(lookUpColsGen, axis=1)
            # Filtern ...
            vRSTN=vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(lookUpObjtypes)) | ( (vRSTN['ITYP_OBJTYPE'].isin(lookUpObjtypes)) & (vRSTN['ITYP_OBJTYPE']==vRSTN['OBJTYPE'])) ,:]
          
            # TABL ---
            #lookUpTables=['LFKT','PHI1','PUMD','PVAR','QVAR','SWVT','TEVT','WEVT']  
            lookUpTables=[]
            for table in ['LFKT','PHI1','PUMD','PVAR','QVAR','SWVT','TEVT','WEVT']:                
                if table in self.dataFrames:
                    lookUpTables.append(table)
            lookUpPosts=['_'+lookUpTable for lookUpTable in lookUpTables]
            lookUpTableKeys=['fk'+lookUpTable for lookUpTable in lookUpTables]
            lookUpColsGen=['NAME']+['NAME'+lookUpPost for lookUpTable,lookUpPost in zip(lookUpTables[1:],lookUpPosts[1:])]

            # pruefen, ob mehrere TABL-Schluessel hinterlegt sind
            vRSTN['TABL_Chk']=vRSTN[lookUpTableKeys][vRSTN[lookUpTableKeys].astype('int64')>0].count(axis=1)   
            # Information auf unDef zurücksetzen, wenn OBJTYPE nicht passt                              
            vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(lookUpTables)) & ~(vRSTN['TABL_Chk'].isnull()),'TABL_Chk']=None 
            for lookUpTable,lookUpTableKey,lookUpPost,lookUpColGen in zip(lookUpTables,lookUpTableKeys,lookUpPosts,lookUpColsGen):
                 
                df=self.dataFrames[lookUpTable][['pk','NAME']]                 
                vRSTN=pd.merge(vRSTN,df,left_on=lookUpTableKey,right_on='pk',suffixes=('',lookUpPost),how='left')

                # belegte Spalte auf unDef zurücksetzen, wenn OBJTYPE nicht passt                              
                vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin([lookUpTable])) &  ~(vRSTN[lookUpColGen].isnull()),lookUpColGen]=None # Referenz vorhanden und gültig - aber irrelevant       

            
            # neue Spalte TABL bestücken     
            vRSTN['TABL'] = vRSTN[lookUpColsGen].bfill(axis=1).iloc[:, 0] # zugewiesen wird die erste Nicht-Nul Spalte 

            # dann generierte Spalten loeschen
            vRSTN=vRSTN.drop(lookUpColsGen, axis=1)

            # KNOT ---
            vRSTN=pd.merge(vRSTN,self.dataFrames['vKNOT'][['pk','NAME']],left_on='fkKNOT',right_on='pk',suffixes=('','_Kn'),how='left')  # nur 1 Treffer moeglich ...
            vRSTN.rename(columns={'NAME':'KNOT'},inplace=True)
            # belegte Spalte auf unDef zurücksetzen, wenn OBJTYPE nicht passt                              
            vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(['KNOT'])) & ~(vRSTN['KNOT'].isnull()),'KNOT']=None 

            # RART ---
            vRSTN=pd.merge(vRSTN,self.dataFrames['vRART'][['pk','NAME','INDSTD_TXT']],left_on='fkRART',right_on='pk',suffixes=('','_Ra'),how='left')  # nur 1 Treffer moeglich ...
            vRSTN.rename(columns={'NAME':'RART'},inplace=True)
            vRSTN.rename(columns={'INDSTD_TXT':'RART_TYP'},inplace=True)
            # belegte Spalte auf unDef zurücksetzen, wenn OBJTYPE nicht passt                              
            vRSTN.loc[~(vRSTN['ITYP_OBJTYPE'].isin(['RART'])) & ~(vRSTN['RART'].isnull()),['RART','RART_TYP']]=None 

        

            #logger.debug("{0:s}{1:s}".format(logStr,str(vRSTN.columns.tolist()))) -----------------------

            # RART PGRP --
            vRSTN=pd.merge(vRSTN,self.dataFrames['vRART'][['pk','NAME','INDSTD_TXT']],left_on='fkRARTPG',right_on='pk',suffixes=('','_RaPGRP'),how='left')  # nur 1 Treffer moeglich ...
            vRSTN.rename(columns={'NAME':'RARTPG'},inplace=True)
            vRSTN.rename(columns={'INDSTD_TXT':'RARTPG_TYP'},inplace=True)
            # belegte Spalte auf unDef zurücksetzen, wenn Stellglied nicht passt                           
            vRSTN.loc[
                ~(
                vRSTN['ITYP_OBJTYPE'].isin(['PGRP']) 
                &
                vRSTN['ITYP_OBJATTR'].isin(['RART']) 
                )
                & 
                ~(
                vRSTN['RARTPG'].isnull()
                )
                ,
                ['RARTPG','RARTPG_TYP']]=None 

            # RART REGV --
            vRSTN=pd.merge(vRSTN,self.dataFrames['vRART'][['pk','NAME','INDSTD_TXT']],left_on='fkRART',right_on='pk',suffixes=('','_RaREGV'),how='left')  # nur 1 Treffer moeglich ...
            vRSTN.rename(columns={'NAME':'RARTRV'},inplace=True)
            vRSTN.rename(columns={'INDSTD_TXT':'RARTRV_TYP'},inplace=True)
            # belegte Spalte auf unDef zurücksetzen, wenn Stellglied nicht passt                           
            vRSTN.loc[
                ~(
                vRSTN['ITYP_OBJTYPE'].isin(['REGV']) 
                &
                vRSTN['ITYP_OBJATTR'].isin(['RART']) 
                )
                & 
                ~(
                vRSTN['RARTRV'].isnull()
                )
                ,
                ['RARTRV','RARTRV_TYP']]=None 


            # RCPL ---
            if 'RCPL' in self.dataFrames:
                RCPL=self.dataFrames['RCPL']
                RCPL_ROWT=self.dataFrames['RCPL_ROWT']
                df=pd.merge(RCPL,RCPL_ROWT,left_on='pk',right_on='fk',suffixes=('','_ROWT'))
                vKNOT=self.dataFrames['vKNOT']
                df=pd.merge(df,vKNOT,left_on='fkKREF1',right_on='pk',suffixes=('','_KNOT1'))
                df=pd.merge(df,vKNOT,left_on='fkKREF2',right_on='pk',suffixes=('','_KNOT2'))
                df=df[[
                    'NAME'
                    ,'TYP'
                    ,'AKTIV_ROWT'
                    ,'W'
                    ,'NAME_KNOT1'
                    ,'NAME_KNOT2'
                    ,'pk'
                    ,'pk_ROWT'
                ]]
            
                #510=RCPL_ROWT_AKT | 1511=RCPL_ROWT_SW

                vRSTN=pd.merge(vRSTN,df,left_on=['fkRCPL','fkRCPL_ROWT'],right_on=['pk','pk_ROWT'],suffixes=('','_RCPL_ROWT'),how='left')  # nur 1 Treffer moeglich ...
                vRSTN.rename(columns={'NAME':'RCPL'},inplace=True)
                vRSTN.rename(columns={'NAME_KNOT1':'RCPL_KNOT1'},inplace=True)
                vRSTN.rename(columns={'NAME_KNOT2':'RCPL_KNOT2'},inplace=True)
            
                # belegte Spalte auf unDef zurücksetzen, wenn Stellglied nicht passt     
             
                # >>> 'RCPL_ROWT_SW'.split(sep='_')
                # ['RCPL', 'ROWT', 'SW']
                                        
                vRSTN.loc[
                    ~(
                    vRSTN['ITYP_OBJTYPE'].isin(['RCPL']) 
                    &
                    vRSTN['ITYP_OBJATTR'].isin(['ROWT']) 
                    )
                    & 
                    ~(
                    vRSTN['RCPL'].isnull()
                    )
                    ,
                    ['RCPL','RCPL_KNOT1','RCPL_KNOT2']]=None 


            # PUMP PGRP --------------------------------------------------------------------------------------------------
            vRSTN=pd.merge(vRSTN,lookUpVbel,left_on='fkPUMPPG',right_on='OBJID',suffixes=('','_PUMP'),how='left')  
            # belegte Spalte auf unDef zurücksetzen, wenn Stellglied nicht passt                           
            vRSTN.loc[
                ~(
                vRSTN['ITYP_OBJTYPE'].isin(['PGRP']) 
                &
                vRSTN['ITYP_OBJATTR'].isin(['PUAKT','PUDEA']) 

                  #704=PGRP_PUAKT | 705=PGRP_PUDEA 

                )
                & 
                ~(
                vRSTN['NAME_i_PUMP'].isnull()
                )
                ,
                ['NAME_i_PUMP','NAME_k_PUMP']]=None 



            # ggf. nicht generierbare Spalten generieren ------------------------------------
            missingCols=['RCPL' # befuellt wenn RCPL Stellglied
                   ,'RCPL_KNOT1'
                   ,'RCPL_KNOT2'
                    #704=PGRP_PUAKT | 705=PGRP_PUDEA 
                   , 'NAME_i_PUMP'
                   , 'NAME_k_PUMP'  ]
            for col in missingCols:
                if col not in vRSTN:
                    vRSTN[col]=None


            # pruefen, ob für jeden RSTN genau 1 Stellobjekt ermittelt wurde ------------------------------------------------
                # Ergebnisse
            cols=[      
                 'CONT_i'   # stellvertretend für die Ergebnisspalten von VBEL Stellobjekten       
                ,'TABL'
                ,'KNOT'
                ,'RART'
                # ,'RARTPG'
                # ,'RARTRV'
                ,'RCPL'
                #,'NAME_i_PUMP'
                ]
            vRSTN['Chk']=vRSTN[cols].count(axis=1)   
                # 0:  kein Stellobjekt
                # 1:  Ok: genau 1 Stellobjekt
                # >1: Ergebnisspalten dieses Views sind nicht konsistent befüllt

            vRSTN = vRSTN[[

                    'CONT'
                   ,'CONT_PARENT'
                   ,'KA'
                   ,'BESCHREIBUNG'
                   
                   ,'pk'

                 #  ,'TYP'
                   ,'ITYP_OBJTYPE'
                   ,'ITYP_OBJATTR'

                   ,'fkROHR', 'fkPGRP', 'fkPUMP', 'fkVENT' , 'fkFWES' , 'fkREGV' # covered
                   ,'fkRART', 'fkRARTPG' # covered

                   # uncovered

                   ,'fkDPRG', 'fkGVWK', 'fkKOMP', 'fkMREG', 'fkOBEH', 'fkPREG'                  
                                 
                    
                   # all covered

                   ,'fkLFKT', 'fkPHI1', 'fkPUMD', 'fkPVAR', 'fkQVAR', 'fkSWVT', 'fkTEVT', 'fkWEVT' 

                   # Results:
                   
                   , 'Chk'

                        # 0:  kein Stellobjekt
                        # 1:  Ok: genau 1 Stellobjekt
                        # >1: Ergebnisspalten dieses Views sind nicht konsistent befüllt

                   , 'ik_Chk' 
                                # None, wenn RSTN-Stellobjekt keines der behandelten VBELs
                                # sonst Anzahl der hinterlegten behandelten VBEL-Referenzen
                                # davon ist nur 1 stellend aktiv
                                # dieses sollte mit den nachfolgenden Spalten korrekt angezeigt sein
                   
                   , 'OBJTYPE'
                   , 'NAME_i'
                   , 'NAME_k'
                   , 'CONT_i'                   
                   
                   #, 'OBJTYPE_PGRP', 'OBJID_PGRP', 'OBJTYPE_PUMP', 'OBJID_PUMP', 'OBJTYPE_VENT', 'OBJID_VENT', 'OBJTYPE_FWES', 'OBJID_FWES'
                   
                   ,'TABL_Chk'    
                             # None, wenn RSTN-Stellobjekt keines der behandelten TABLs
                             # sonst Anzahl der hinterlegten behandelten TABL-Referenzen
                             # davon ist nur 1 stellend aktiv
                             # diese sollte in der nachfolgenden Spalte korrekt angezeigt sein

                   #, 'pk_LFKT', 'pk_PHI1', 'pk_PUMD', 'pk_PVAR', 'pk_QVAR', 'pk_SWVT', 'pk_TEVT', 'pk_WEVT'                   
                   ,'TABL'  # befuellt wenn eine TABL Stellglied

                   #, 'pk_Kn
                   , 'KNOT' # befuellt wenn KNOT Stellglied
                   
                   #, 'pk_Ra'
                   , 'RART' # befuellt wenn RART Stellglied
                   , 'RART_TYP'

                   ,'RARTPG' # befuellt wenn PGRP RART Stellglied
                   ,'RARTPG_TYP'

                   ,'RARTRV' # befuellt wenn PGRP RART Stellglied
                   ,'RARTRV_TYP'
                   
                      #| 1510=RCPL_ROWT_AKT | 1511=RCPL_ROWT_SW' 
                   ,'RCPL' # befuellt wenn RCPL Stellglied
                   ,'RCPL_KNOT1'
                   ,'RCPL_KNOT2'

                    #704=PGRP_PUAKT | 705=PGRP_PUDEA 
                   , 'NAME_i_PUMP'
                   , 'NAME_k_PUMP'                  

                   ]]
         
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vRSTN,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vRSTN=pd.DataFrame()              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vRSTN

    def _vQVAR(self):
        """One row per Timeseries.

        Returns:
            columns
                QVAR
                    * NAME
                    * BESCHREIBUNG
                    * INTPOL
                    * ZEITOPTION
                SERIES
                    * QM: 1st Value
                    * QM_min
                    * QM_max
                QVAR ID
                    * pk

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vQVAR = None
            vQVAR=pd.merge(self.dataFrames['QVAR'],self.dataFrames['QVAR_ROWT'],left_on='pk',right_on='fk')
            vQVAR['ZEIT']=pd.to_numeric(vQVAR['ZEIT']) 
            vQVAR['QM']=pd.to_numeric(vQVAR['QM']) 
            vQVAR['ZEIT_RANG']=vQVAR.groupby(['pk_x'])['ZEIT'].rank(ascending=True)
            #
            vQVAR_gQM=vQVAR.groupby(['pk_x'], as_index=False).agg({'QM':[np.min,np.max]})
            vQVAR_gQM.columns= [tup[0]+tup[1] for tup in zip(vQVAR_gQM.columns.get_level_values(0),vQVAR_gQM.columns.get_level_values(1))]
            vQVAR_gQM.rename(columns={'QMamin':'QM_min','QMamax':'QM_max'},inplace=True)
            #
            vQVAR=pd.merge(vQVAR,vQVAR_gQM,left_on='pk_x',right_on='pk_x')
            #
            vQVAR=vQVAR[vQVAR['ZEIT_RANG']==1]
            #
            vQVAR=vQVAR[['NAME','BESCHREIBUNG','INTPOL','ZEITOPTION','QM','QM_min','QM_max','pk_x']]
            #
            vQVAR.rename(columns={'pk_x':'pk'},inplace=True)
                                 
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vQVAR

    def _vPVAR(self):
        """One row per Timeseries.

        Returns:
            columns
                PVAR
                    * NAME
                    * BESCHREIBUNG
                    * INTPOL
                    * ZEITOPTION
                SERIES
                    * PH: 1st Value
                    * PH_min
                    * PH_max
                QVAR ID
                    * pk

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vPVAR = None
            vPVAR=pd.merge(self.dataFrames['PVAR'],self.dataFrames['PVAR_ROWT'],left_on='pk',right_on='fk')
            vPVAR['ZEIT']=pd.to_numeric(vPVAR['ZEIT']) 
            vPVAR['PH']=pd.to_numeric(vPVAR['PH']) 
            vPVAR['ZEIT_RANG']=vPVAR.groupby(['pk_x'])['ZEIT'].rank(ascending=True)
            #
            vPVAR_gPH=vPVAR.groupby(['pk_x'], as_index=False).agg({'PH':[np.min,np.max]})
            vPVAR_gPH.columns= [tup[0]+tup[1] for tup in zip(vPVAR_gPH.columns.get_level_values(0),vPVAR_gPH.columns.get_level_values(1))]
            vPVAR_gPH.rename(columns={'PHamin':'PH_min','PHamax':'PH_max'},inplace=True)
            #
            vPVAR=pd.merge(vPVAR,vPVAR_gPH,left_on='pk_x',right_on='pk_x')
            #
            vPVAR=vPVAR[vPVAR['ZEIT_RANG']==1]
            #
            vPVAR=vPVAR[['NAME','BESCHREIBUNG','INTPOL','ZEITOPTION','PH','PH_min','PH_max','pk_x']]
            #
            vPVAR.rename(columns={'pk_x':'pk'},inplace=True)
                                 
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            return vPVAR
   
            
    def _vVKNO(self):
        """One row per Blocknode.

        Returns:
            columns
                * NAME 
                * CONT (Blockname)
                * fkKNOT
                * fkCONT   

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:     
            vVKNO=None        
            vVKNO=pd.merge(self.dataFrames['VKNO'],self.dataFrames['CONT'],left_on='fkCONT',right_on='pk')
            vVKNO=pd.merge(vVKNO,self.dataFrames['KNOT'],left_on='fkKNOT',right_on='pk')

            vVKNO=vVKNO[[
               'NAME_x'     
              ,'NAME_y'     
              ,'fkCONT_x','fkKNOT' 
            ]]
            vVKNO.rename(columns={'NAME_x':'CONT','NAME_y':'NAME','fkCONT_x':'fkCONT'},inplace=True)

            vVKNO=vVKNO[[
                'NAME' # der Name des Knotens
               ,'CONT' # der Blockname des Blockes fuer den der Knoten Blockknoten ist
               ,'fkKNOT'
               ,'fkCONT'
            ]]
                               
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vVKNO,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vVKNO=pd.DataFrame()       
                vVKNO['NAME']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     
                vVKNO['CONT']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     
                vVKNO['fkKNOT']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.     
                vVKNO['fkCONT']=pd.Series(dtype='object')  # The default dtype for empty Series will be 'object' instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning.                
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vVKNO

    def _vKNOT(self,vVKNO=None,vQVAR=None,vPVAR=None,vLFKT=None):
        """One row per Node (KNOT).

        Args:
            * vVKNO
            * vQVAR
            * vPVAR
            * vLFKT

        Returns:
            rows
                sequence: Xml

            columns
                KNOT
                    * NAME
                    * BESCHREIBUNG
                    * IDREFERENZ
                CONT
                    * CONT
                    * CONT_ID
                    * CONT_LFDNR
                    * CONT_VKNO (name of the Block/Container for NAME is a Blocknode)
                KNOT 
                    * KTYP
                    * LFAKT (Umrechnungsfaktor) 
                    * QM_EIN
                QVAR
                    * QVAR_NAME
                    * QM, QM_min, QM_max 
                LFKT
                    * LFKT_NAME
                    * LF, LF_min, LF_max 
                PVAR
                    * PVAR_NAME
                    * PH, PH_min, PH_max 
                Zugehoerigkeit
                    * PZON_NAME
                    * FSTF_NAME,STOF_NAME,GMIX_NAME
                    * UTMP_NAME
                2L
                    * 2L_NAME
                    * 2L_KVR
                KNOT 
                    * KVR
                    * TE
                    * TM
                KNOT
                    * XKOR, YKOR, ZKOR
                KNOT IDs
                    * pk, tk
                KNOT: plot-Coordinates
                    * pXCor: X-pXCorZero
                    * pYCor: Y-pYCorZero
                Refs
                    * fkFQPS                   
                    
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             
            vKNOT=None

            vKNOT=pd.merge(self.dataFrames['KNOT'],self.dataFrames['KNOT_BZ'],left_on='pk',right_on='fk')
            vKNOT=pd.merge(vKNOT,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk')
            vKNOT=pd.merge(vKNOT,vVKNO,left_on='pk_x',right_on='fkKNOT',how='left')

            #logger.debug("{:s}vKNOT columns: {:s}".format(logStr,str(vKNOT.columns)))             
            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)            
                      
            vKNOT=vKNOT[[
                    'NAME_x'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'NAME_y' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'ID' # aus KNOT>CONT
                   ,'LFDNR' # aus KNOT>CONT
                   ,'CONT' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN','fkQVAR','fkLFKT','fkPVAR'   
                   ,'fk2LKNOT','fkFQPS','fkFSTF'
                   #,'fkHYDR'  #90-12
                   ,'fkPZON','fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk_x','tk_x'
                ]]

            vKNOT.rename(columns={'NAME_x':'NAME'
                                       ,'NAME_y':'CONT'
                                       ,'ID':'CONT_ID'
                                       ,'LFDNR':'CONT_LFDNR'
                                       ,'ID':'CONT_ID','LFDNR':'CONT_LFDNR'
                                       ,'CONT':'CONT_VKNO'
                                       ,'pk_x':'pk'
                                       ,'tk_x':'tk'},inplace=True)

            vKNOT=pd.merge(vKNOT,vQVAR,left_on='fkQVAR',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','BESCHREIBUNG_x':'BESCHREIBUNG','NAME_y':'QVAR_NAME'},inplace=True)
            vKNOT.rename(columns={'pk_x':'pk'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN','fkLFKT','fkPVAR'       
                   ,'fk2LKNOT','fkFQPS','fkFSTF'
                   # ,'fkHYDR'  #90-12
                   ,'fkPZON','fkUTMP'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,vLFKT,left_on='fkLFKT',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','BESCHREIBUNG_x':'BESCHREIBUNG','NAME_y':'LFKT_NAME','pk_x':'pk'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'fkPVAR'       
                   ,'fk2LKNOT','fkFQPS','fkFSTF'
                   # ,'fkHYDR'  #90-12
                   ,'fkPZON','fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]
          
            vKNOT=pd.merge(vKNOT,vPVAR,left_on='fkPVAR',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','BESCHREIBUNG_x':'BESCHREIBUNG','NAME_y':'PVAR_NAME','pk_x':'pk'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'fk2LKNOT','fkFQPS','fkFSTF'
                   # ,'fkHYDR'  #90-12
                   ,'fkPZON','fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,self.dataFrames['PZON'],left_on='fkPZON',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','NAME_y':'PZON_NAME','pk_x':'pk','tk_x':'tk'},inplace=True)

            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'fk2LKNOT','fkFQPS','fkFSTF'
                   #,'fkHYDR'  #90-12
                   ,'fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,self.dataFrames['FSTF'],left_on='fkFSTF',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','NAME_y':'FSTF_NAME','pk_x':'pk','tk_x':'tk'},inplace=True)

            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'FSTF_NAME'
                   ,'fk2LKNOT','fkFQPS','fkSTOF','fkGMIX'
                   #,'fkHYDR'  #90-12
                   ,'fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,self.dataFrames['STOF'],left_on='fkSTOF',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','BESCHREIBUNG_x':'BESCHREIBUNG','NAME_y':'STOF_NAME','pk_x':'pk','tk_x':'tk'},inplace=True)

            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'FSTF_NAME','STOF_NAME'
                   ,'fk2LKNOT','fkFQPS','fkGMIX'
                   #,'fkHYDR'  #90-12
                   ,'fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            gMix=self.dataFrames['GMIX']
            vKNOT=pd.merge(vKNOT,gMix[[col for col in gMix.columns.tolist() if col not in ['BESCHREIBUNG']]],left_on='fkGMIX',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','NAME_y':'GMIX_NAME','pk_x':'pk','tk_x':'tk'},inplace=True)

            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'FSTF_NAME','STOF_NAME','GMIX_NAME'
                   ,'fk2LKNOT','fkFQPS'
                   #,'fkHYDR'  #90-12
                   ,'fkUTMP'
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,self.dataFrames['UTMP'],left_on='fkUTMP',right_on='pk',how='left')
            vKNOT.rename(columns={'NAME_x':'NAME','NAME_y':'UTMP_NAME','pk_x':'pk','tk_x':'tk'},inplace=True)

            if 'IDREFERENZ_x' in vKNOT.columns.tolist(): #90-12
                vKNOT.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'FSTF_NAME','STOF_NAME','GMIX_NAME'
                   ,'UTMP_NAME'
                   ,'fk2LKNOT','fkFQPS'
                   #,'fkHYDR'  #90-12
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            vKNOT=pd.merge(vKNOT,self.dataFrames['KNOT'],left_on='fk2LKNOT',right_on='pk',how='left',suffixes=('', '_y'))
            vKNOT.rename(columns={'NAME_y':'2L_NAME','KVR_y':'2L_KVR'},inplace=True)

            vKNOT=vKNOT[[
                    'NAME'
                   ,'BESCHREIBUNG'
                   ,'IDREFERENZ'
                   ,'CONT' # aus KNOT>CONT (der Blockname des Knotens)
                   ,'CONT_ID' # aus KNOT>CONT
                   ,'CONT_LFDNR' # aus KNOT>CONT
                   ,'CONT_VKNO' # aus vVKNO (der Blockname des Blocks fuer den der Knoten Blockknoten ist)
                   ,'KTYP'
                   ,'LFAKT','QM_EIN'
                   ,'QVAR_NAME'
                   ,'QM','QM_min','QM_max'     
                   ,'LFKT_NAME'
                   ,'LF','LF_min','LF_max'     
                   ,'PVAR_NAME'
                   ,'PH','PH_min','PH_max'     
                   ,'PZON_NAME'
                   #,'IDIMRA','PKMINRA','PKMAXRA'
                   ,'FSTF_NAME','STOF_NAME','GMIX_NAME'
                   ,'UTMP_NAME'
                   ,'2L_NAME','2L_KVR'
                   ,'fkFQPS'
                   #,'fkHYDR'  #90-12
                   ,'KVR' 
                   ,'TE','TM' 
                   ,'XKOR','YKOR','ZKOR'
                   ,'pk','tk'
                ]]

            pXCorZero=vKNOT[
                (vKNOT['CONT_ID'].astype(int)==1001) 
                & 
                (vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element') == False)]['XKOR'].astype(np.double).min()

            vKNOT['pXCor'] = [
                 x-pXCorZero 
                 if 
                 y==1001 and not z
                 else
                 x
                 for x,y,z in zip(vKNOT['XKOR'].astype(np.double)
                             ,vKNOT['CONT_ID'].astype(int)
                             ,vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element')
                             )
                ] 

            pYCorZero=vKNOT[
                (vKNOT['CONT_ID'].astype(int)==1001) 
                & (vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element') == False)]['YKOR'].astype(np.double).min()

            vKNOT['pYCor'] = [
                 x-pYCorZero 
                 if 
                 y==1001 and not z
                 else
                 x
                 for x,y,z in zip(vKNOT['YKOR'].astype(np.double)
                             ,vKNOT['CONT_ID'].astype(int)
                             ,vKNOT['BESCHREIBUNG'].fillna('').str.startswith('Template Element')
                             )
                ] 
            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vKNOT

    def vKNOTexpEBES(self,AColIdx=0):
        """Expands Resultcolumns in vKNOT: FWVB and ESQUELLSP. 

        Precondition:
            * vFWVB added with Resultcolumns FWVB~*~*~*~W, FWVB~*~*~*~QM
            * vKNOT added with Resultcolumn ESQUELLSP

        Arguments:
            * AColIdx: Idx (LFDNR-1) of the EG which represents qsA (and defines qsNotA)

        new Cols:
            * qsStr: ESQUELLSP of the node as plain text

            * qs_LFDNR_NAME: share of EBES Nr. LFDNR in the supply of the node - i.e.:
                * qs_1_Drei Linden
                * qs_4_Biogas Wette
                * ...
            * the columns are derived from column ESQUELLSP
            * the column ESQUELLSP is unchanged

            * qsigStr                 

            * qs100: Index beginnend mit 1 der EG die den jeweiligen Knoten zu 100% versorgt - 0 sonst (d.h. dieser Knoten wird von keiner EG zu 100% versorgt)                  
            * qsSUM: Summe aller EGs - 100, wenn der Knoten zu 100% von den EGs versorgt wird               
            * qsA                   
            * qsNotA                  
            
            * qsAnzKnoten
            * qsAnzFwvb

            * qsKNOT~*~*~*~QM'
            * qsFWVB~*~*~*~W
            * qsFWVB~*~*~*~QM

            * qsigKNOT~*~*~*~QM'
            * qsigFWVB~*~*~*~W
            * qsigFWVB~*~*~*~QM
            
            
            * qsRank: NrOfGroup: order is perc. desc. in EBES LFDNR order (the ESQUELLSP with max. share of 1st EBES is No. 1)
            * qsRankAnzKnoten: NrOfGroup: order is Anzahl Knoten (the ESQUELLSP with max. NOfNodes is No. 1)
            * qsRank: die mit der größten neg. Abnahme ist die 1.

            * qsRankAnzFwvb
            * qsRankFWVB~*~*~*~W

            * qsigRank: lexikalisch absteigend (d.h. die alles 1-Signatur ist die 1. und die alle 0-Signatur ist die letzte)
            * qsigRankAnzKnoten: die mit den wenigsten Knoten ist die 1.
            * qsigRank: die mit der größten neg. Abnahme ist die 1.
    
            * qsigRankAnzFwvb
            * qsigRankFWVB~*~*~*~W
            * qsigqsRankFWVB~*~*~*~W: lfd. Nr. QS nach W-Größe sig, qs absteigend (d.h. No. 1 ist W-größte QSPK in der W-größten QSIG) 
        
        Returns:
            * vKNOT with the new Cols

        Raises:
            XmError

        >>> # -q -m 0 -s vKNOTexpEBES -y no -z no -w DHNetwork
        >>> # ---
        >>> xm=xms['DHNetwork']                      
        >>> # ---
        >>> vKNOT=xm.dataFrames['vKNOT']
        >>> vKNOTexp=xm.vKNOTexpEBES()
        >>> r,c=vKNOT.shape
        >>> r2,c2=vKNOTexp.shape
        >>> r==r2
        True
        >>> a=sorted(vKNOTexp['qsigStr'].unique()) # sortierte Liste der voneinander verschiedenen Quellsignaturen
        >>> a
        ['000', '001', '010', '011', '100', '110']
        >>> len(a)
        6
        >>> vKNOTexp['qsRank'].max() # Anzahl verschiedener Quellspektren unter Berücksichtigung von KVR / Numerierung EBES
        26
        >>> # KVR:
        >>> # in Wärmenetzen haben RL-Knoten i.d.R. 0 0 0 ... für alle RL-Knoten
        >>> # dieses QS wird voneinander verschieden gezählt von einem möglichen QS 0 0 0 ... für VL-Knoten (wenn es welche gibt die von keiner aktiven EG versorgt werden)
        >>> vKNOTexp['qsRankAnzKnoten'].max() # Anzahl verschiedener Quellspektren unter Berücksichtigung von KVR / Numerierung Anzahl Knoten
        26
        >>> import pandas as pd
        >>> pd.set_option('display.width', 333)       
        >>> print(vKNOTexp[['KVR','qs_1_A','qs_2_B','qs_3_C','qsigStr','qsAnzKnoten','qsRank','qsRankAnzKnoten']].drop_duplicates(keep='first').sort_values(by=['qsRank']).to_string(index=False))      
        KVR qs_1_A qs_2_B qs_3_C qsigStr  qsAnzKnoten  qsRank  qsRankAnzKnoten
          1    100      0      0     100          210       1                1
          1     99      1      0     110            9       2               10
          1     98      2      0     110            2       3               17
          1     97      3      0     110           55       4                4
          1     96      4      0     110           28       5                7
          1     95      5      0     110            2       6               18
          1     82     18      0     110           18       7                8
          1     76     24      0     110            1       8               21
          1     74     26      0     110           79       9                3
          1     67     33      0     110            4      10               12
          1     61     39      0     110            3      11               14
          1     58     42      0     110            4      12               13
          1     48     52      0     110            2      13               19
          1     39     61      0     110            2      14               20
          1     36     64      0     110            5      15               11
          1     35     65      0     110            3      16               15
          1     24     76      0     110           46      17                5
          1     11     89      0     110            1      18               22
          1     10     90      0     110           12      19                9
          1      6     94      0     110            1      20               23
          1      0    100      0     010          195      21                2
          1      0     92      8     011            1      22               24
          1      0     67     33     011            3      23               16
          1      0     44     56     011            1      24               25
          1      0      0    100     001           40      25                6
          2      0      0      0     000          735      26               26
        >>> print(vKNOTexp[['KVR','qs_1_A','qs_2_B','qs_3_C','qsAnzKnoten','qsRank','qsRankAnzKnoten']].drop_duplicates(keep='first').sort_values(by=['qsRankAnzKnoten']).to_string(index=False))            
        KVR qs_1_A qs_2_B qs_3_C  qsAnzKnoten  qsRank  qsRankAnzKnoten
          1    100      0      0          210       1                1
          1      0    100      0          195      21                2
          1     74     26      0           79       9                3
          1     97      3      0           55       4                4
          1     24     76      0           46      17                5
          1      0      0    100           40      25                6
          1     96      4      0           28       5                7
          1     82     18      0           18       7                8
          1     10     90      0           12      19                9
          1     99      1      0            9       2               10
          1     36     64      0            5      15               11
          1     67     33      0            4      10               12
          1     58     42      0            4      12               13
          1     61     39      0            3      11               14
          1     35     65      0            3      16               15
          1      0     67     33            3      23               16
          1     98      2      0            2       3               17
          1     95      5      0            2       6               18
          1     48     52      0            2      13               19
          1     39     61      0            2      14               20
          1     76     24      0            1       8               21
          1     11     89      0            1      18               22
          1      6     94      0            1      20               23
          1      0     92      8            1      22               24
          1      0     44     56            1      24               25
          2      0      0      0          735      26               26
        >>> print(vKNOTexp[['KVR','qs_1_A','qs_2_B','qs_3_C', 'qsAnzFwvb','qsRankFWVB~*~*~*~W','qsFWVB~*~*~*~W', 'qsFWVB~*~*~*~QM']].drop_duplicates(keep='first').sort_values(by=['qsRankFWVB~*~*~*~W']).round(-2).to_string(index=False))                    
        KVR qs_1_A qs_2_B qs_3_C  qsAnzFwvb  qsRankFWVB~*~*~*~W  qsFWVB~*~*~*~W  qsFWVB~*~*~*~QM
          1    100      0      0      500.0                   0        182000.0           2100.0
          1      0    100      0      300.0                   0         92500.0           1100.0
          1     97      3      0      200.0                   0         40100.0            500.0
          1     74     26      0      200.0                   0         34500.0            400.0
          1     24     76      0      100.0                   0         27400.0            300.0
          1      0      0    100      100.0                   0         25200.0            300.0
          1     96      4      0      100.0                   0         20500.0            200.0
          1     11     89      0        0.0                   0         18800.0            200.0
          1     82     18      0        0.0                   0         10900.0            100.0
          1     95      5      0        0.0                   0          6500.0            100.0
          1     99      1      0        0.0                   0          4700.0            100.0
          1     58     42      0        0.0                   0          4100.0              0.0
          1     10     90      0        0.0                   0          3800.0              0.0
          1     36     64      0        0.0                   0          2600.0              0.0
          1     39     61      0        0.0                   0          2500.0              0.0
          1     35     65      0        0.0                   0          2300.0              0.0
          1     61     39      0        0.0                   0          2100.0              0.0
          1     67     33      0        0.0                   0          1900.0              0.0
          1      0     67     33        0.0                   0          1300.0              0.0
          1      6     94      0        0.0                   0           900.0              0.0
          1     98      2      0        0.0                   0           600.0              0.0
          1      0     44     56        0.0                   0           500.0              0.0
          1     48     52      0        0.0                   0           400.0              0.0
          1      0     92      8        0.0                   0           400.0              0.0
          1     76     24      0        0.0                   0           300.0              0.0
          2      0      0      0        0.0                   0             0.0              0.0
        >>> # --- AnzFwvb in Knot
        >>> vFWVB=xm.dataFrames['vFWVB']
        >>> r,c=vFWVB.shape    
        >>> r==vKNOTexp['AnzFwvb'].sum()
        True
        >>> # --- Summe W in Knot
        >>> WSumme=round(vFWVB['FWVB~*~*~*~W'].sum(),2)
        >>> WSumme==round(vKNOTexp['FWVB~*~*~*~W'].sum(),2)
        True
        >>> # --------------------------------------             
        >>> # in vKNOTexp sind die FWVB in Summe Anz und Summe W korrekt
        >>> # --------------------------------------
        >>> grpObj=vKNOTexp[['KVR','KNOT~*~*~*~ESQUELLSP','FWVB~*~*~*~W','qsFWVB~*~*~*~W']].groupby(by=['KVR','KNOT~*~*~*~ESQUELLSP'],as_index=False)
        >>> df=grpObj['FWVB~*~*~*~W'].sum().round(-2) 
        >>> df[['KVR','FWVB~*~*~*~W']]           
           KVR  FWVB~*~*~*~W
        0    1       25200.0
        1    1         500.0
        2    1        1300.0
        3    1         400.0
        4    1       92500.0
        5    1         900.0
        6    1        3800.0
        7    1       18800.0
        8    1       27400.0
        9    1        2300.0
        10   1        2600.0
        11   1        2500.0
        12   1         400.0
        13   1        4100.0
        14   1        2100.0
        15   1        1900.0
        16   1       34500.0
        17   1         300.0
        18   1       10900.0
        19   1        6500.0
        20   1       20500.0
        21   1       40100.0
        22   1         600.0
        23   1        4700.0
        24   1      182000.0
        25   2           0.0
        >>> round(WSumme,-3)==round(df['FWVB~*~*~*~W'].sum(),-3)
        True
        >>> # round(WSumme,0)
        >>> df=grpObj['qsFWVB~*~*~*~W'].first() 
        >>> dfFirst=df[['KVR','qsFWVB~*~*~*~W']].round(1)
        >>> df=grpObj['qsFWVB~*~*~*~W'].last() 
        >>> dfLast=df[['KVR','qsFWVB~*~*~*~W']].round(1)
        >>> # dfFirst
        >>> # dfLast
        >>> dfFirst.equals(dfLast)
        True
        >>> df=grpObj['qsFWVB~*~*~*~W'].mean() 
        >>> dfMean=df[['KVR','qsFWVB~*~*~*~W']].round(1)
        >>> dfFirst.equals(dfMean)
        True
        >>> print(dfFirst.sort_values(by=['qsFWVB~*~*~*~W'],ascending=False).round(-2).to_string(index=False))                    
        KVR  qsFWVB~*~*~*~W
          1        182000.0
          1         92500.0
          1         40100.0
          1         34500.0
          1         27400.0
          1         25200.0
          1         20500.0
          1         18800.0
          1         10900.0
          1          6500.0
          1          4700.0
          1          4100.0
          1          3800.0
          1          2600.0
          1          2500.0
          1          2300.0
          1          2100.0
          1          1900.0
          1          1300.0
          1           900.0
          1           600.0
          1           500.0
          1           400.0
          1           400.0
          1           300.0
          2             0.0
        >>> df=vKNOTexp[['KVR','qsigStr','qsigRankFWVB~*~*~*~W','qsigFWVB~*~*~*~W', 'qsigFWVB~*~*~*~QM']].drop_duplicates(keep='first').sort_values(by=['qsigRankFWVB~*~*~*~W']).round({'qsigFWVB~*~*~*~W': -2, 'qsigFWVB~*~*~*~QM': -2})      
        >>> print(df.to_string(index=False))      
        KVR qsigStr  qsigRankFWVB~*~*~*~W  qsigFWVB~*~*~*~W  qsigFWVB~*~*~*~QM
          1     110                     1          184800.0             2200.0
          1     100                     2          182000.0             2100.0
          1     010                     3           92500.0             1100.0
          1     001                     4           25200.0              300.0
          1     011                     5            2200.0                0.0
          2     000                     6               0.0                0.0
        >>> round(WSumme,-3)==round(df['qsigFWVB~*~*~*~W'].sum(),-3)
        True
        >>> grpObj=vKNOTexp.groupby(by=['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W'],as_index=False)        
        >>> d={col:'min' for col in ['qsigStr','qs_1_A','qs_2_B','qs_3_C','qsigqsRankFWVB~*~*~*~W']}       
        >>> d.update({'qsigFWVB~*~*~*~W':'min'})
        >>> d.update({'qsFWVB~*~*~*~W':'min'})
        >>> d.update({'pk':'count'}) # Anzahl Knoten 
        >>> d.update({'NAME':'first'}) # ein Knotenname
        >>> # d.update({'AnzFwvb':'sum'}) # muss gleich d.update({'qsAnzFwvb':'first'}) sein
        >>> d.update({'qsigAnzFwvb':'first'})
        >>> d.update({'qsAnzFwvb':'first'})
        >>> df=grpObj.agg(d).sort_values(by=['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W'],ascending=True)       
        >>> df.rename(columns={'pk':'AnzKnoten','NAME':'1 NAME'},inplace=True)
        >>> xm.dataFrames['df']=df.round({'qsigFWVB~*~*~*~W': -2, 'qsFWVB~*~*~*~W': -2})
        >>> print(xm._getvXXXXAsOneString(vXXXX='df'))
            qsigRankFWVB~*~*~*~W  qsRankFWVB~*~*~*~W qsigStr qs_1_A qs_2_B qs_3_C  qsigqsRankFWVB~*~*~*~W  qsigFWVB~*~*~*~W  qsFWVB~*~*~*~W  AnzKnoten  1 NAME  qsigAnzFwvb  qsAnzFwvb
        0                      1                   3     110     97      3      0                       1          184800.0         40100.0         55  V-1852        598.0      157.0
        1                      1                   4     110     74     26      0                       2          184800.0         34500.0         79  V-3611        598.0      150.0
        2                      1                   5     110     24     76      0                       3          184800.0         27400.0         46  V-1630        598.0       92.0
        3                      1                   7     110     96      4      0                       4          184800.0         20500.0         28  V-1773        598.0       58.0
        4                      1                   8     110     11     89      0                       5          184800.0         18800.0          1  V-3109        598.0        3.0
        5                      1                   9     110     82     18      0                       6          184800.0         10900.0         18  V-1712        598.0       38.0
        6                      1                  10     110     95      5      0                       7          184800.0          6500.0          2  V-1132        598.0        1.0
        7                      1                  11     110     99      1      0                       8          184800.0          4700.0          9  V-1335        598.0       17.0
        8                      1                  12     110     58     42      0                       9          184800.0          4100.0          4  V-1751        598.0       12.0
        9                      1                  13     110     10     90      0                      10          184800.0          3800.0         12  V-3426        598.0       19.0
        10                     1                  14     110     36     64      0                      11          184800.0          2600.0          5  V-1755        598.0        9.0
        11                     1                  15     110     39     61      0                      12          184800.0          2500.0          2  V-1372        598.0        4.0
        12                     1                  16     110     35     65      0                      13          184800.0          2300.0          3  V-1744        598.0        9.0
        13                     1                  17     110     61     39      0                      14          184800.0          2100.0          3  V-1742        598.0        7.0
        14                     1                  18     110     67     33      0                      15          184800.0          1900.0          4  V-1607        598.0        8.0
        15                     1                  20     110      6     94      0                      16          184800.0           900.0          1  V-1374        598.0        3.0
        16                     1                  21     110     98      2      0                      17          184800.0           600.0          2  V-1803        598.0        7.0
        17                     1                  23     110     48     52      0                      18          184800.0           400.0          2  V-1308        598.0        2.0
        18                     1                  25     110     76     24      0                      19          184800.0           300.0          1  V-1743        598.0        2.0
        19                     2                   1     100    100      0      0                      20          182000.0        182000.0        210  V-1208        485.0      485.0
        20                     3                   2     010      0    100      0                      21           92500.0         92500.0        195  V-3202        338.0      338.0
        21                     4                   6     001      0      0    100                      22           25200.0         25200.0         40  V-2400         74.0       74.0
        22                     5                  19     011      0     67     33                      23            2200.0          1300.0          3  V-2351         10.0        5.0
        23                     5                  22     011      0     44     56                      24            2200.0           500.0          1  V-2352         10.0        2.0
        24                     5                  24     011      0     92      8                      25            2200.0           400.0          1  V-2140         10.0        3.0
        25                     6                  26     000      0      0      0                      26               0.0             0.0        735  R-3709          0.0        0.0
        >>> import re
        >>> qsColsEgr=[col for col in vKNOTexp.columns.tolist() if re.search('^qs_',col) != None]
        >>> qsColsEgr
        ['qs_1_A', 'qs_2_B', 'qs_3_C']
        >>> qsColsInf=[col for col in vKNOTexp.columns.tolist() if re.search('^qs',col) != None and re.search('^qs_',col) == None]
        >>> qsColsInf
        ['qsStr', 'qsigStr', 'qs100', 'qsSUM', 'qsA', 'qsNotA', 'qsARank', 'qsAnzKnoten', 'qsAnzFwvb', 'qsFWVB~*~*~*~W', 'qsFWVB~*~*~*~QM', 'qsRank', 'qsRankAnzKnoten', 'qsRankAnzFwvb', 'qsRankFWVB~*~*~*~W', 'qsigAnzKnoten', 'qsigAnzFwvb', 'qsigFWVB~*~*~*~W', 'qsigFWVB~*~*~*~QM', 'qsigRank', 'qsigRankAnzKnoten', 'qsigRankAnzFwvb', 'qsigRankFWVB~*~*~*~W', 'qsigqsRankFWVB~*~*~*~W']
        >>> #xm=xms['OneLPipe']                     
        >>> # ---        
        >>> #vKNOTexp=xm.vKNOTexpEBES()
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:
            vKNOTexp=None

            # EBES
            if 'EBES' in self.dataFrames.keys():
                EBES = self.dataFrames['EBES']
                EBES_BZ = self.dataFrames['EBES_BZ']
                vEBES=pd.merge(EBES,EBES_BZ,left_on='pk',right_on='fk',suffixes=('','_BZ')).sort_values(by=['LFDNR','AKTIVQS']).reset_index() # der alte Index bleibt als Index erhalten
                ### vEBES=vEBES[vEBES['AKTIVQS']=='101'] # nur die berechneten Ebes
                Names=vEBES['NAME'].tolist()
                Lfdnrs=vEBES['LFDNR'].tolist()
                expColNames=['qs' + '_' + str(Lfdnr) + '_' + Name for Lfdnr,Name in zip(Lfdnrs,Names)]

            if not vEBES.shape == vEBES[vEBES['AKTIVQS']=='101'].shape:
                logger.info("{:s}: Es gibt inaktive Einspeisergruppen!".format(logStr))               

            # vKnot
            vKNOTexp=self.dataFrames['vKNOT']       
            vKNOTexp['KVR'].fillna('0',inplace=True) # vermeiden, dass spaetere Aggregierungen mit KVR Null-Ergebnisse produzieren für KVR-Nulls

            if 'KNOT~*~*~*~ESQUELLSP' in vKNOTexp.columns.tolist():
                vKNOTexp['qsStr']=vKNOTexp['KNOT~*~*~*~ESQUELLSP'].str.decode('utf-8')
                vKNOTexp['qsStr']=vKNOTexp['qsStr'].str.rstrip()

                # die Anzahl der Spalten ist die Anzahl der definierten ### berechneten Ebes
                expDf=vKNOTexp['qsStr'].str.split('\t', expand = True)

                # die Spalten dranhängen (heißen 1,2,...)
                vKNOTexp=pd.merge(vKNOTexp,expDf,left_index=True,right_index=True,suffixes=('','_expDf'))




                # die Spalten umbenennen

                ### if len(expDf.columns.tolist()) != len(expColNames):
                ###    logStrFinal="{:s}: Anzahl der expandierten qs-Komponenten: {:d} != Anzahl der als zu berechnen definierten Einspeisergruppen: {:d} ?!".format(logStr,len(expDf.columns.tolist()),len(expColNames))
                ###    logger.error(logStrFinal) 
                ###    raise XmError(logStrFinal)                    
                ### else:

                # neue Spaltennamen:
                vKNOTexp=vKNOTexp.rename(columns={idx:colName for idx,colName in zip(expDf.columns.tolist(),expColNames)})

                #vKNOTexp[expColNames]=vKNOTexp[expColNames].astype('int')
                
                def f(vec):                    
                    qsigStr=''
                    for idx,val in enumerate(vec):
                        if int(val)>0:
                            qsigStr=qsigStr+'1'
                        else:
                            qsigStr=qsigStr+'0'
                    return qsigStr
                    
                vKNOTexp['qsigStr']=vKNOTexp[expColNames].apply(f,axis=1)

                def f(vec):
                    for idx,val in enumerate(vec):
                        if int(val)>=100:
                            return idx+1
                    return 0

                vKNOTexp['qs100']=vKNOTexp[expColNames].apply(f,axis=1) # belegt mit 1,2,3. ... oder 0
                vKNOTexp['qsSUM']=vKNOTexp[expColNames].astype(int).sum(axis=1)

                ACol=expColNames[AColIdx]
                vKNOTexp['qsA']=vKNOTexp[ACol].astype(int)
                NotACols=[col for col in expColNames if col != ACol]
                vKNOTexp['qsNotA']=vKNOTexp[NotACols].astype(int).sum(axis=1)

                # bis hier: ... ,'qsStr', 'qs_1_A', 'qs_2_B', 'qs_3_C', 'qsigStr', 'qs100', 'qsSUM', 'qsA', 'qsNotA' ...

                colsARank=['KVR','qsA']
                colsARankOrder=[True,False]
                vKNOTexp['qsARank'] = vKNOTexp.sort_values(colsARank,ascending=colsARankOrder).groupby(colsARank,sort=False).ngroup() + 1
       
            # --- vKNOTexp annotieren mit FWVB-Aggregaten
            if 'vFWVB' in self.dataFrames.keys():
                vFWVB=self.dataFrames['vFWVB']
                expFwvbCols=['FWVB~*~*~*~W','FWVB~*~*~*~QM']
                if set([item in vFWVB.columns.tolist() for item in expFwvbCols]) == set([True]):
                    grpObj=vFWVB[['NAME_i']+expFwvbCols+['pk']].groupby(by=['NAME_i'],as_index=False)
                    d={'pk':'count'} 
                    if 'FWVB~*~*~*~W' in vFWVB.columns:
                        d.update({'FWVB~*~*~*~W':'sum'} )
                    if 'FWVB~*~*~*~QM' in vFWVB.columns:
                        d.update({'FWVB~*~*~*~QM':'sum'} )
                    df=grpObj.agg(d)
                    df.rename(columns={'pk':'AnzFwvb'},inplace=True)                   
                    df=pd.merge(vKNOTexp,df,left_on='NAME',right_on='NAME_i',how='left',suffixes=('','_Fwvb'))        
                    df.drop(['NAME_i'],axis=1,inplace=True)
                    vKNOTexp=df

             # bis hier: ... ,'AnzFwvb', 'FWVB~*~*~*~W', 'FWVB~*~*~*~QM' 

            # --- vKNOTexp annotieren Spektrum-Aggregaten
            # Spektrum-Aggregate bilden
            grpKatLst=['KVR']
            if set([item in vKNOTexp.columns.tolist() for item in grpKatLst+['KNOT~*~*~*~ESQUELLSP']]) == set([True]):
            
                grpObj=vKNOTexp.groupby(by=grpKatLst+['KNOT~*~*~*~ESQUELLSP'], as_index=False) #df=df.reset_index() # wg. as_index=False
                # Aggregate berechnen
                d={'NAME':'count'} 
                dRename={'NAME':'qsAnzKnoten'}
                if 'KNOT~*~*~*~QM' in vKNOTexp.columns:
                    d.update({'KNOT~*~*~*~QM':'sum'})
                    dRename.update({'KNOT~*~*~*~QM':'qsKNOT~*~*~*~QM'})
                if 'AnzFwvb' in vKNOTexp.columns:
                    d.update({'AnzFwvb':'sum'} )
                    dRename.update({'AnzFwvb':'qsAnzFwvb'} )
                if 'FWVB~*~*~*~W' in vKNOTexp.columns:
                    d.update({'FWVB~*~*~*~W':'sum'} )
                    dRename.update({'FWVB~*~*~*~W':'qsFWVB~*~*~*~W'} )
                if 'FWVB~*~*~*~QM' in vKNOTexp.columns:
                    d.update({'FWVB~*~*~*~QM':'sum'} )
                    dRename.update({'FWVB~*~*~*~QM':'qsFWVB~*~*~*~QM'} )
                df=grpObj.agg(d)                   
                df.rename(columns=dRename,inplace=True)
               
                # verbinden
                cols=vKNOTexp.columns.tolist()             
                cols.extend(list(dRename.values()))                           
                vKNOTexp=pd.merge(vKNOTexp,df,left_on=grpKatLst+['KNOT~*~*~*~ESQUELLSP'],right_on=grpKatLst+['KNOT~*~*~*~ESQUELLSP'],how='left',suffixes=('','_exp'))
                vKNOTexp=vKNOTexp.filter(items=cols)   
           
                # Quellspektren numerieren
                cols=['KVR']+expColNames            
                vKNOTexp['qsRank'] = vKNOTexp.sort_values(cols,ascending=[True] + len(expColNames)*[False]).groupby(cols,sort=False).ngroup() + 1
                colsSort=['KVR']+['qsAnzKnoten']+expColNames
                vKNOTexp['qsRankAnzKnoten'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+ len(expColNames)*[False]).groupby(cols,sort=False).ngroup() + 1

                if 'qsKNOT~*~*~*~QM' in vKNOTexp.columns:
                    colsSort=['KVR']+['qsKNOT~*~*~*~QM']+expColNames
                    vKNOTexp['qsRankQM'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[True]+ len(expColNames)*[False]).groupby(cols,sort=False).ngroup() + 1

                if 'AnzFwvb' in vKNOTexp.columns:

                    colsSort=['KVR']+['qsAnzFwvb']+expColNames
                    vKNOTexp['qsRankAnzFwvb'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+ len(expColNames)*[False]).groupby(cols,sort=False).ngroup() + 1
                    colsSort=['KVR']+['qsFWVB~*~*~*~W']+expColNames
                    vKNOTexp['qsRankFWVB~*~*~*~W'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+ len(expColNames)*[False]).groupby(cols,sort=False).ngroup() + 1

                # QuellSignatur #########################################################
                grpObj=vKNOTexp.groupby(by=grpKatLst+['qsigStr'], as_index=False) 
                # Aggregate berechnen
                d={'NAME':'count'} 
                dRename={'NAME':'qsigAnzKnoten'}
                if 'KNOT~*~*~*~QM' in vKNOTexp.columns:
                    d.update({'KNOT~*~*~*~QM':'sum'})
                    dRename.update({'KNOT~*~*~*~QM':'qsigKNOT~*~*~*~QM'})
                if 'AnzFwvb' in vKNOTexp.columns:
                    d.update({'AnzFwvb':'sum'} )
                    dRename.update({'AnzFwvb':'qsigAnzFwvb'} )
                if 'FWVB~*~*~*~W' in vKNOTexp.columns:
                    d.update({'FWVB~*~*~*~W':'sum'} )
                    dRename.update({'FWVB~*~*~*~W':'qsigFWVB~*~*~*~W'} )
                if 'FWVB~*~*~*~QM' in vKNOTexp.columns:
                    d.update({'FWVB~*~*~*~QM':'sum'} )
                    dRename.update({'FWVB~*~*~*~QM':'qsigFWVB~*~*~*~QM'} )
                df=grpObj.agg(d)                   
                df.rename(columns=dRename,inplace=True)

                # verbinden
                cols=vKNOTexp.columns.tolist()             
                cols.extend(list(dRename.values()))                           
                vKNOTexp=pd.merge(vKNOTexp,df,left_on=grpKatLst+['qsigStr'],right_on=grpKatLst+['qsigStr'],how='left',suffixes=('','_exp'))
                vKNOTexp=vKNOTexp.filter(items=cols)   

                # Quellsignatur numerieren
                cols=['KVR']+['qsigStr']                 
                vKNOTexp['qsigRank'] = vKNOTexp.sort_values(cols,ascending=[True] + [False]).groupby(cols,sort=False).ngroup() + 1

                colsSort=['KVR']+['qsigAnzKnoten']+['qsigStr']                   
                vKNOTexp['qsigRankAnzKnoten'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+[False]).groupby(cols,sort=False).ngroup() + 1

                if 'qsigKNOT~*~*~*~QM' in vKNOTexp.columns:
                    colsSort=['KVR']+['qsigKNOT~*~*~*~QM']+['qsigStr']                   
                    vKNOTexp['qsigRankQM'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[True]+[False]).groupby(cols,sort=False).ngroup() + 1


                if 'AnzFwvb' in vKNOTexp.columns:

                    colsSort=['KVR']+['qsigAnzFwvb']+['qsigStr']   
                    vKNOTexp['qsigRankAnzFwvb'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+[False]).groupby(cols,sort=False).ngroup() + 1

                    colsSort=['KVR']+['qsigFWVB~*~*~*~W']+['qsigStr']   
                    vKNOTexp['qsigRankFWVB~*~*~*~W'] = vKNOTexp.sort_values(colsSort,ascending=[True]+[False]+ [False]).groupby(cols,sort=False).ngroup() + 1


                    # qsigqsRankFWVB~*~*~*~W
                    cols=['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W']
                    vKNOTexp['qsigqsRankFWVB~*~*~*~W'] = vKNOTexp.sort_values(cols,ascending=[True]+[True]).groupby(cols,sort=False).ngroup() + 1

                #vKNOTexp.sort_values(['KVR','qsigRankFWVB~*~*~*~W','qsRank'],ascending=True).groupby(['KVR','qsigRankFWVB~*~*~*~W'],sort=False).ngroup() + 1


        except XmError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vKNOTexp

    def vROHRexpEBES(self,vKNOTexpEBES):
        """Expands Resultcolumns in vROHR with ESQUELLSP-columns. 
       
        Arguments:
            * vKNOTexpEBES: df with ESQUELLSP-columns

        new Cols:
           
        
        Returns:
            * vROHR with the new Cols

        Raises:
            XmError

        >>> # -q -m 0 -s vROHRexpEBES -y no -z no -w DHNetwork
        >>> # ---
        >>> import pandas as pd
        >>> pd.set_option('display.width', 333)
        >>> xm=xms['DHNetwork']   
        >>> vKNOTexp=xm.vKNOTexpEBES()
        >>> vROHRexp=xm.vROHRexpEBES(vKNOTexp)
        >>> r,c=xm.dataFrames['vROHR'].shape
        >>> r2,c2=vROHRexp.shape
        >>> r==r2
        True
        >>> c2>c
        True
        >>> grpObj=vROHRexp.groupby(by=['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W'],as_index=False)        
        >>> d={col:'min' for col in ['qsigStr','qs_1_A','qs_2_B','qs_3_C','qsigqsRankFWVB~*~*~*~W']}       
        >>> d.update({'qsigFWVB~*~*~*~W':'min'})
        >>> d.update({'qsFWVB~*~*~*~W':'min'})
        >>> #d.update({'NAME_k':'count'}) # Anzahl Knoten 
        >>> d.update({'NAME_i':'first'}) # ein Knotenname
        >>> # d.update({'AnzFwvb':'sum'}) # muss gleich d.update({'qsAnzFwvb':'first'}) sein
        >>> d.update({'qsigAnzFwvb':'first'})
        >>> d.update({'qsAnzFwvb':'first'})
        >>> d.update({'pk':'count'}) # Anzahl Rohre
        >>> #d.update({'L':'sum'}) # Länge Rohre 
        >>> d.update({'qsigRank_sumL':'first'}) 
        >>> d.update({'qsRank_sumL':'first'}) 
        >>> d.update({'qsigRank_L':'first'}) 
        >>> d.update({'qsRank_L':'first'}) 
        >>> df=grpObj.agg(d).sort_values(by=['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W'],ascending=True)       
        >>> df.rename(columns={'NAME_k':'AnzKnoten','NAME_i':'1 NAME','pk':'AnzRohre'},inplace=True)
        >>> xm.dataFrames['df']=df[['qsigRankFWVB~*~*~*~W','qsRankFWVB~*~*~*~W','qsigStr','qs_1_A','qs_2_B','qs_3_C','qsigqsRankFWVB~*~*~*~W','qsigFWVB~*~*~*~W','qsFWVB~*~*~*~W','1 NAME','qsigAnzFwvb','qsAnzFwvb','AnzRohre','qsigRank_sumL']].round({'qsigRankFWVB~*~*~*~W':-2,'qsRankFWVB~*~*~*~W':-2,'qsigqsRankFWVB~*~*~*~W':-2,'qsigFWVB~*~*~*~W':-2,'qsFWVB~*~*~*~W':-2,'qsigRank_sumL':-2})
        >>> print(xm._getvXXXXAsOneString(vXXXX='df'))
            qsigRankFWVB~*~*~*~W  qsRankFWVB~*~*~*~W qsigStr qs_1_A qs_2_B qs_3_C  qsigqsRankFWVB~*~*~*~W  qsigFWVB~*~*~*~W  qsFWVB~*~*~*~W  1 NAME  qsigAnzFwvb  qsAnzFwvb  AnzRohre  qsigRank_sumL
        0                      0                   0     110     97      3      0                       0          184800.0         40100.0  V-1802        598.0      157.0        72        51200.0
        1                      0                   0     110     74     26      0                       0          184800.0         34500.0  V-3505        598.0      150.0        89        51200.0
        2                      0                   0     110     24     76      0                       0          184800.0         27400.0  V-1633        598.0       92.0        53        51200.0
        3                      0                   0     110     96      4      0                       0          184800.0         20500.0  V-1114        598.0       58.0        33        51200.0
        4                      0                   0     110     82     18      0                       0          184800.0         10900.0  V-1711        598.0       38.0        20        51200.0
        5                      0                   0     110     95      5      0                       0          184800.0          6500.0  V-1132        598.0        1.0         1        51200.0
        6                      0                   0     110     99      1      0                       0          184800.0          4700.0  V-1336        598.0       17.0         8        51200.0
        7                      0                   0     110     58     42      0                       0          184800.0          4100.0  V-1750        598.0       12.0         4        51200.0
        8                      0                   0     110     10     90      0                       0          184800.0          3800.0  V-3420        598.0       19.0        11        51200.0
        9                      0                   0     110     36     64      0                       0          184800.0          2600.0  V-1755        598.0        9.0         5        51200.0
        10                     0                   0     110     39     61      0                       0          184800.0          2500.0  V-1373        598.0        4.0         2        51200.0
        11                     0                   0     110     35     65      0                       0          184800.0          2300.0  V-1743        598.0        9.0         5        51200.0
        12                     0                   0     110     61     39      0                       0          184800.0          2100.0  V-1740        598.0        7.0         3        51200.0
        13                     0                   0     110     67     33      0                       0          184800.0          1900.0  V-1605        598.0        8.0         4        51200.0
        14                     0                   0     110      6     94      0                       0          184800.0           900.0  V-1374        598.0        3.0         1        51200.0
        15                     0                   0     110     98      2      0                       0          184800.0           600.0  V-1802        598.0        7.0         3        51200.0
        16                     0                   0     110     48     52      0                       0          184800.0           400.0  V-1308        598.0        2.0         3        51200.0
        17                     0                   0     110     76     24      0                       0          184800.0           300.0  V-1742        598.0        2.0         1        51200.0
        18                     0                   0     100    100      0      0                       0          182000.0        182000.0  V-1591        485.0      485.0       261        36800.0
        19                     0                   0     010      0    100      0                       0           92500.0         92500.0  V-3204        338.0      338.0       214        37400.0
        20                     0                   0     001      0      0    100                       0           25200.0         25200.0  V-2602         74.0       74.0        43         7300.0
        21                     0                   0     011      0     67     33                       0            2200.0          1300.0  V-2113         10.0        5.0         3          300.0
        22                     0                   0     000      0      0      0                       0               0.0             0.0  R-1226          0.0        0.0       839       133000.0
        >>> grpObj=vROHRexp.groupby(by=['qsigRank_L','qsRank_L'],as_index=False)        
        >>> d={col:'min' for col in ['qsigStr','qs_1_A','qs_2_B','qs_3_C','qsigqsRank_L']}       
        >>> d.update({'qsigFWVB~*~*~*~W':'min'})
        >>> d.update({'qsFWVB~*~*~*~W':'min'})
        >>> #d.update({'NAME_k':'count'}) # Anzahl Knoten 
        >>> d.update({'NAME_i':'first'}) # ein Knotenname
        >>> # d.update({'AnzFwvb':'sum'}) # muss gleich d.update({'qsAnzFwvb':'first'}) sein
        >>> d.update({'qsigAnzFwvb':'first'})
        >>> d.update({'qsAnzFwvb':'first'})
        >>> d.update({'pk':'count'}) # Anzahl Rohre
        >>> #d.update({'L':'sum'}) # Länge Rohre 
        >>> d.update({'qsigRank_sumL':'first'}) 
        >>> d.update({'qsRank_sumL':'first'})         
        >>> #d.update({'qsigRank_L':'first'}) 
        >>> #d.update({'qsRank_L':'first'}) 
        >>> df=grpObj.agg(d).sort_values(by=['qsigRank_L','qsRank_L'],ascending=True)       
        >>> df.rename(columns={'NAME_k':'AnzKnoten','NAME_i':'1 NAME','pk':'AnzRohre'},inplace=True)
        >>> xm.dataFrames['df']=df.round({'qsigFWVB~*~*~*~W':-2,'qsFWVB~*~*~*~W':-2,'qsigRank_sumL':-2,'qsRank_sumL':-2})      
        >>> print(xm._getvXXXXAsOneString(vXXXX='df'))
            qsigRank_L  qsRank_L qsigStr qs_1_A qs_2_B qs_3_C  qsigqsRank_L  qsigFWVB~*~*~*~W  qsFWVB~*~*~*~W  1 NAME  qsigAnzFwvb  qsAnzFwvb  AnzRohre  qsigRank_sumL  qsRank_sumL
        0            1         3     110     74     26      0             1          184800.0         34500.0  V-3505        598.0      150.0        89        51200.0      16200.0
        1            1         4     110     97      3      0             2          184800.0         40100.0  V-1802        598.0      157.0        72        51200.0       9800.0
        2            1         5     110     24     76      0             3          184800.0         27400.0  V-1633        598.0       92.0        53        51200.0       9700.0
        3            1         7     110     96      4      0             4          184800.0         20500.0  V-1114        598.0       58.0        33        51200.0       4500.0
        4            1         8     110     82     18      0             5          184800.0         10900.0  V-1711        598.0       38.0        20        51200.0       2900.0
        5            1         9     110     10     90      0             6          184800.0          3800.0  V-3420        598.0       19.0        11        51200.0       2200.0
        6            1        10     110     99      1      0             7          184800.0          4700.0  V-1336        598.0       17.0         8        51200.0       1400.0
        7            1        11     110     35     65      0             8          184800.0          2300.0  V-1743        598.0        9.0         5        51200.0        800.0
        8            1        12     110     48     52      0             9          184800.0           400.0  V-1308        598.0        2.0         3        51200.0        600.0
        9            1        13     110     36     64      0            10          184800.0          2600.0  V-1755        598.0        9.0         5        51200.0        600.0
        10           1        14     110     67     33      0            11          184800.0          1900.0  V-1605        598.0        8.0         4        51200.0        600.0
        11           1        15     110     98      2      0            12          184800.0           600.0  V-1802        598.0        7.0         3        51200.0        400.0
        12           1        16     110     58     42      0            13          184800.0          4100.0  V-1750        598.0       12.0         4        51200.0        400.0
        13           1        17     110      6     94      0            14          184800.0           900.0  V-1374        598.0        3.0         1        51200.0        400.0
        14           1        18     110     61     39      0            15          184800.0          2100.0  V-1740        598.0        7.0         3        51200.0        300.0
        15           1        19     110     39     61      0            16          184800.0          2500.0  V-1373        598.0        4.0         2        51200.0        300.0
        16           1        21     110     95      5      0            17          184800.0          6500.0  V-1132        598.0        1.0         1        51200.0        200.0
        17           1        22     110     76     24      0            18          184800.0           300.0  V-1742        598.0        2.0         1        51200.0        100.0
        18           2         1     010      0    100      0            19           92500.0         92500.0  V-3204        338.0      338.0       214        37400.0      37400.0
        19           3         2     100    100      0      0            20          182000.0        182000.0  V-1591        485.0      485.0       261        36800.0      36800.0
        20           4         6     001      0      0    100            21           25200.0         25200.0  V-2602         74.0       74.0        43         7300.0       7300.0
        21           5        20     011      0     67     33            22            2200.0          1300.0  V-2113         10.0        5.0         3          300.0        300.0
        22           6        23     000      0      0      0            23               0.0             0.0  R-1226          0.0        0.0       839       133000.0     133000.0
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:
            vROHRexp=None
            

            qsColsEgr=[col for col in vKNOTexpEBES.columns.tolist() if re.search('^qs_',col) != None]
            qsColsInf=[col for col in vKNOTexpEBES.columns.tolist() if re.search('^qs',col) != None and re.search('^qs_',col) == None]
            qsCols=qsColsEgr+qsColsInf

            vROHR=self.dataFrames['vROHR']
            vROHRexp=pd.merge(vROHR,vKNOTexpEBES[['NAME']+qsCols],left_on='NAME_i',right_on='NAME',suffixes=('','_i'))          
            vROHRexp.drop(['NAME'],axis=1,inplace=True)
            vROHRexp.rename(columns={col:col+'_i' for col in qsCols},inplace=True)

            vROHRexp=pd.merge(vROHRexp,vKNOTexpEBES[['NAME']+qsCols],left_on='NAME_k',right_on='NAME',suffixes=('','_k'))          
            vROHRexp.drop(['NAME'],axis=1,inplace=True)
            vROHRexp.rename(columns={col:col+'_k' for col in qsCols},inplace=True)

            for col in qsCols:
                vROHRexp[col]=vROHRexp.apply(lambda row: row[col+'_i'] if row['ROHR~*~*~*~QMAV'] >= 0 else row[col+'_k'] ,axis=1)
            vROHRexp.drop([col+'_i' for col in qsCols],axis=1,inplace=True)
            vROHRexp.drop([col+'_k' for col in qsCols],axis=1,inplace=True)

            # nicht all QS müssen notwendigerweise durch Rohre erfasst werden
            # wenn z.B. an einem Vereinigungsknoten der ein neues QS kreiert kein Rohr abgeht und dieses QS auch sonst nicht mehr mit einem abgehenden Rohr vorkommt
            # das führt dazu, dass die Ranks Lücken haben - unhandlich für diskrete Farbskalen
            # diese evtl. Lücken werden nachfolgend beseitigt
            qsRankCols=['qsARank'
                       #---
                       ,'qsRank'
                       ,'qsRankAnzKnoten'
                       ,'qsRankAnzFwvb'
                       ,'qsRankFWVB~*~*~*~W'
                       #---
                       ,'qsigRank'
                       ,'qsigRankAnzKnoten'
                       ,'qsigRankAnzFwvb'
                       ,'qsigRankFWVB~*~*~*~W'
                       #---
                       ,'qsigqsRankFWVB~*~*~*~W']
            for qsRankCol in qsRankCols:                                  
                if qsRankCol in vROHRexp.columns.tolist():
                    vROHRexp[qsRankCol]=vROHRexp[qsRankCol].rank(method='dense').astype('int')

            vROHRexp['L']=vROHRexp['L'].astype('float')

            # Längensumme pro Signatur und Spektrum
            for qsRankCol in ['qsigRank','qsRank']:    
                grpObj=vROHRexp.groupby(by=[qsRankCol],as_index=False)   
                d={'L':'sum'} 
                df=grpObj.agg(d)
                newColName=qsRankCol+'_sumL' #  
                df.rename(columns={'L':newColName},inplace=True)
                # verbinden
                cols=vROHRexp.columns.tolist()             
                cols.extend([newColName])     
                #print(cols)
                vROHRexp=pd.merge(vROHRexp,df,left_on=[qsRankCol],right_on=[qsRankCol],how='left',suffixes=('','_exp'))
                #print(vROHRexp.columns.tolist() )
                vROHRexp=vROHRexp.filter(items=cols)   
                #print(vROHRexp.columns.tolist() )



                







            cols=['qsigRank']                   
            colsSort=['KVR']+['qsigRank_sumL']+['qsigRank']   
            vROHRexp['qsigRank_L'] = vROHRexp.sort_values(colsSort,ascending=[True]+[False]+[True]).groupby(cols,sort=False).ngroup() + 1

            cols=['qsRank']                   
            colsSort=['KVR']+['qsRank_sumL']+['qsRank']   
            vROHRexp['qsRank_L'] = vROHRexp.sort_values(colsSort,ascending=[True]+[False]+[True]).groupby(cols,sort=False).ngroup() + 1

            cols=['qsigRank_L','qsRank_L']
            vROHRexp['qsigqsRank_L'] = vROHRexp.sort_values(cols,ascending=[True]+[True]).groupby(cols,sort=False).ngroup() + 1

        except XmError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)               
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vROHRexp

    def _vROHR(self,vKNOT=None):
        """One row per Pipe (ROHR).

        Args:
            vKNOT

        Returns:
            rows
                sequence: Xml

            columns
                ROHR
                    * BESCHREIBUNG
                    * IDREFERENZ
                ROHR
                    * BAUJAHR, HAL
                    * IPLANUNG, KENNUNG
                ROHR
                    * L, LZU, RAU, ZAUS, ZEIN, ZUML
                    * JLAMBS, LAMBDA0
                ROHR
                    * ASOLL, INDSCHALL
                ROHR FW                   
                    * NAME_i_2L
                    * NAME_k_2L
                    * KVR
                DTRO_ROWD
                    * AUSFALLZEIT, DA , DI , DN , KT , PN , REHABILITATION , REPARATUR , S , WSTEIG , WTIEFE
                LTGR
                    * LTGR_NAME, LTGR_BESCHREIBUNG , SICHTBARKEIT , VERLEGEART
                DTRO
                    * DTRO_NAME, DTRO_BESCHREIBUNG, E
                REF
                    * fkSTRASSE, fkSRAT
                ROHR IDs
                    * pk, tk
                ROHR BZ
                    * ITRENN
                    * LECKSTART, LECKEND, LECKMENGE, LECKORT, LECKSTATUS
                Rest
                    * QSVB, ZVLIMPTNZ, KANTENZV
                CONT
                    * CONT
                    * CONT_ID
                    * CONT_LFDNR
                vKNOT
                    KI
                        * NAME_i
                        * KVR_i, TM_i
                        * XKOR_i, YKOR_i, ZKOR_i
                    KK
                        * NAME_k
                        * KVR_k, TM_k
                        * XKOR_k, YKOR_k, ZKOR_k
                    
                    pXCor_i, pYCor_i # X / Y des KNOTens i
                    pXCor_k, pYCor_k # X / Y des KNOTens k
                PLOT
                    * pXCors, pYCors # KNOTenkoordinaten i,k als je 2-elementige Liste
                    * pWAYPXCors, pWAYPYCors  # um min. X / min. Y aller Knoten der Netzansicht bereinigte Wegpunktkoordinatenlisten, d.h. der Wegpunkt "ganz links unten" hat die Koordinaten 0/0      

        Raises:
            XmError                           
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vROHR=None            
                                         
            vROHR=pd.merge(self.dataFrames['ROHR'],self.dataFrames['ROHR_BZ'],left_on='pk',right_on='fk')

            vROHR=vROHR[[
                     'BESCHREIBUNG'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'fk2LROHR','KVR'
                    #Ref.
                    ,'fkCONT'
                    ,'fkDTRO_ROWD'
                    ,'fkLTGR','fkSTRASSE'
                    ,'fkKI','fkKK'
                   #IDs 
                    ,'pk_x','tk'
                    ,'GEOM','GRAF'
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                            ]]

            vROHR.rename(columns={'pk_x':'pk'},inplace=True)
            vROHR=pd.merge(vROHR,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk')

            if 'IDREFERENZ_x' in vROHR.columns.tolist(): #90-12
                vROHR.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vROHR=vROHR[[
             'BESCHREIBUNG'
            ,'IDREFERENZ'
            #Asset
            ,'BAUJAHR','HAL'
            ,'IPLANUNG','KENNUNG'
            #Reibung
            ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
            ,'JLAMBS','LAMBDA0'
            #inst.
            ,'ASOLL','INDSCHALL'
            #FW
            ,'fk2LROHR','KVR'
            #Ref.
            ,'fkDTRO_ROWD'
            ,'fkLTGR','fkSTRASSE'
            ,'fkKI','fkKK'
           #IDs 
            ,'pk_x','tk_x'
            ,'GEOM_x','GRAF_x'
           #BZ
            ,'IRTRENN'
            ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
           #Rest
            ,'QSVB'
            ,'ZVLIMPTNZ'
            ,'KANTENZV'
           #CONT
            ,'NAME' 
            ,'ID'
            ,'LFDNR'
                    ]]
            vROHR.rename(columns={'pk_x':'pk','tk_x':'tk','NAME':'CONT','ID':'CONT_ID','LFDNR':'CONT_LFDNR'},inplace=True)    
            vROHR=pd.merge(vROHR,self.dataFrames['DTRO_ROWD'],left_on='fkDTRO_ROWD',right_on='pk')   

            vROHR=vROHR[[
             'BESCHREIBUNG'
            ,'IDREFERENZ'
            #Asset
            ,'BAUJAHR','HAL'
            ,'IPLANUNG','KENNUNG'
            #Reibung
            ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
            ,'JLAMBS','LAMBDA0'
            #inst.
            ,'ASOLL','INDSCHALL'
            #FW
            ,'fk2LROHR','KVR'
            #DTRO_ROWD
            ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
            #Ref.
            ,'fkLTGR','fkSTRASSE'
            ,'fkKI','fkKK'
           #IDs 
            ,'pk_x','tk_x'
            ,'GEOM_x','GRAF_x'
           #BZ
            ,'IRTRENN'
            ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
           #Rest
            ,'QSVB'
            ,'ZVLIMPTNZ'
            ,'KANTENZV'
           #CONT
            ,'CONT' 
            ,'CONT_ID'
            ,'CONT_LFDNR'
                    ]]
            vROHR.rename(columns={'pk_x':'pk','tk_x':'tk'},inplace=True)
            vROHR=pd.merge(vROHR,self.dataFrames['LTGR'],left_on='fkLTGR',right_on='pk')

            vROHR=vROHR[[
             'BESCHREIBUNG_x'
            ,'IDREFERENZ'
            #Asset
            ,'BAUJAHR','HAL'
            ,'IPLANUNG','KENNUNG'
            #Reibung
            ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
            ,'JLAMBS','LAMBDA0'
            #inst.
            ,'ASOLL','INDSCHALL'
            #FW
            ,'fk2LROHR','KVR'
            #DTRO_ROWD
            ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
            #LTGR
            ,'NAME','BESCHREIBUNG_y','SICHTBARKEIT','VERLEGEART','fkDTRO','fkSRAT'
            #Ref.
            ,'fkSTRASSE'
            ,'fkKI','fkKK'
           #IDs 
            ,'pk_x','tk_x'
            ,'GEOM_x','GRAF_x'
           #BZ
            ,'IRTRENN'
            ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
           #Rest
            ,'QSVB'
            ,'ZVLIMPTNZ'
            ,'KANTENZV'
           #CONT
            ,'CONT' 
            ,'CONT_ID'
            ,'CONT_LFDNR'
                    ]]
            vROHR.rename(columns={'pk_x':'pk','tk_x':'tk','NAME':'LTGR_NAME','BESCHREIBUNG_y':'LTGR_BESCHREIBUNG','BESCHREIBUNG_x':'BESCHREIBUNG'},inplace=True)

            vROHR=vROHR[[
                     'BESCHREIBUNG'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'fk2LROHR','KVR'
                    #DTRO_ROWD
                    ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
                    #LTGR
                    ,'LTGR_NAME','LTGR_BESCHREIBUNG','SICHTBARKEIT','VERLEGEART','fkDTRO','fkSRAT'
                    #Ref.
                    ,'fkSTRASSE'
                    ,'fkKI','fkKK'
                   #IDs 
                    ,'pk','tk'
                    ,'GEOM_x','GRAF_x'
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                   #CONT
                    ,'CONT' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                            ]]
                                 
            vROHR=pd.merge(vROHR,self.dataFrames['DTRO'],left_on='fkDTRO',right_on='pk')

            if 'IDREFERENZ_x' in vROHR.columns.tolist(): #90-12
                vROHR.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vROHR=vROHR[[
                     'BESCHREIBUNG_x'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'fk2LROHR','KVR'
                    #DTRO_ROWD
                    ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
                    #LTGR
                    ,'LTGR_NAME','LTGR_BESCHREIBUNG','SICHTBARKEIT','VERLEGEART'
                    #DTRO
                    ,'NAME'
                    ,'BESCHREIBUNG_y'
                    ,'E'
                    #Ref.
                    ,'fkSTRASSE','fkSRAT'
                    ,'fkKI','fkKK'
                   #IDs 
                    ,'pk_x','tk_x'
                    ,'GEOM_x','GRAF_x'
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                   #CONT
                    ,'CONT' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                            ]]
            vROHR.rename(columns={'pk_x':'pk','tk_x':'tk','NAME':'DTRO_NAME','BESCHREIBUNG_y':'DTRO_BESCHREIBUNG','BESCHREIBUNG_x':'BESCHREIBUNG'},inplace=True)
            
            #logger.debug("{:s} vor fkKI: {!s:s}".format(logStr,(vROHR)))   
            vROHR=pd.merge(vROHR,vKNOT,left_on='fkKI',right_on='pk')   
            #logger.debug("{:s} nach fkKI: {!s:s}".format(logStr,(vROHR)))   
            vROHR.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG','IDREFERENZ_x':'IDREFERENZ'
                                       ,'pk_x':'pk','tk_x':'tk'
                                       ,'CONT_ID_x':'CONT_ID','CONT_LFDNR_x':'CONT_LFDNR'
                                       },inplace=True) 

            vROHR=vROHR[[
                     'BESCHREIBUNG'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'fk2LROHR','KVR_x'
                    #DTRO_ROWD
                    ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
                    #LTGR
                    ,'LTGR_NAME','LTGR_BESCHREIBUNG','SICHTBARKEIT','VERLEGEART'
                    #DTRO
                    ,'DTRO_NAME'
                    ,'DTRO_BESCHREIBUNG'
                    ,'E'
                    #Ref.
                    ,'fkSTRASSE','fkSRAT'
                    ,'fkKK'
                   #IDs 
                    ,'pk','tk'
                    ,'GEOM_x','GRAF_x'
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                   #CONT
                    ,'CONT_x' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                   #Ki
                   ,'NAME'
                   ,'KVR_y','TM'
                   ,'XKOR','YKOR','ZKOR'
                   ,'pXCor','pYCor'
                            ]]

            vROHR.rename(columns={'NAME':'NAME_i','KVR_x':'KVR','KVR_y':'KVR_i','TM':'TM_i','CONT_x':'CONT'},inplace=True)  
            vROHR.rename(columns={'XKOR':'XKOR_i','YKOR':'YKOR_i','ZKOR':'ZKOR_i'
                                       ,'pXCor':'pXCor_i'
                                       ,'pYCor':'pYCor_i'
                                       },inplace=True)    
            
            vROHR=pd.merge(vROHR,vKNOT,left_on='fkKK',right_on='pk')    
            vROHR.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG','IDREFERENZ_x':'IDREFERENZ'
                                       ,'pk_x':'pk','tk_x':'tk'
                                       ,'CONT_ID_x':'CONT_ID','CONT_LFDNR_x':'CONT_LFDNR'
                                       },inplace=True)  

            vROHR.rename(columns={'NAME':'NAME_k','KVR_x':'KVR','KVR_y':'KVR_k','TM':'TM_k','CONT_x':'CONT'},inplace=True)  
            vROHR.rename(columns={'XKOR':'XKOR_k','YKOR':'YKOR_k','ZKOR':'ZKOR_k'
                                       ,'pXCor':'pXCor_k'
                                       ,'pYCor':'pYCor_k'
                                       },inplace=True)                                   

            vROHR['pXCors']=[[xi,xk] for xi,xk in zip(vROHR['pXCor_i'],vROHR['pXCor_k'])]
            vROHR['pYCors']=[[xi,xk] for xi,xk in zip(vROHR['pYCor_i'],vROHR['pYCor_k'])]

            vROHR.rename(columns={'GEOM_x':'GEOM'},inplace=True)         

            vROHR=pd.merge(vROHR,vROHR,left_on='fk2LROHR',right_on='pk',how='left',suffixes=('','_2L'))   

            vROHR=vROHR[[
                     'BESCHREIBUNG'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'NAME_i_2L'
                    ,'NAME_k_2L'
                    ,'KVR'                  
                    #DTRO_ROWD
                    ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
                    #LTGR
                    ,'LTGR_NAME','LTGR_BESCHREIBUNG','SICHTBARKEIT','VERLEGEART'
                    #DTRO
                    ,'DTRO_NAME'
                    ,'DTRO_BESCHREIBUNG'
                    ,'E'
                    #Ref.
                    ,'fkSTRASSE','fkSRAT'
                   #IDs 
                    ,'pk','tk'          
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                   #CONT
                    ,'CONT' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                   #Ki
                   ,'NAME_i'
                   ,'KVR_i','TM_i'
                   ,'XKOR_i','YKOR_i','ZKOR_i'                 
                   #Kk
                   ,'NAME_k'
                   ,'KVR_k','TM_k'
                   ,'XKOR_k','YKOR_k','ZKOR_k'
                   #plotCors
                   ,'pXCor_i','pYCor_i'
                   ,'pXCor_k','pYCor_k'
                   # matplotlibs's .plot(pXCors,pYCors,...)
                   ,'pXCors','pYCors' # nur die Endpunkte     
                   # ...........
                   ,'GEOM'
                            ]]
            
            # WAYP ###
            vROHR['WAYP']=[list() for dummy in vROHR['pk']] # leere Liste von Wegpunkten
            for index,row in vROHR.iterrows():
                if pd.isnull(row.GEOM):                    
                    continue
                geomBytes=base64.b64decode(row.GEOM)
                # 1. Byte: Endianess: 0=little
                # 1. Byte auslassen
    
                # 2 ints lesen ...
                headerData = struct.unpack('2i',geomBytes[1:9])                
                graphType,NOfWaypoints=headerData #  graphType: Werte von 1 bis 6 bedeuten: Point, LineString, Polygon, MultiPoint, ...
    
                # xy-Koordinatenpaare lesen                 
                # 2 double: xi, yi
                for idx in range(NOfWaypoints):
                    offset=9+idx*16                   
                    end=offset+16                  
                    waypXY=struct.unpack('2d',geomBytes[offset:end])                    
                    row.WAYP.append(waypXY)
          
            vROHR['pWAYPXCors']=[list() for dummy in vROHR['pk']] # leere Liste von pWegpunkten X
            vROHR['pWAYPYCors']=[list() for dummy in vROHR['pk']] # leere Liste von pWegpunkten Y
            for index,row in vROHR.iterrows():
                for waypXY in row.WAYP:
                    X,Y=waypXY
                    if int(row.CONT_ID)==1001:
                        row.pWAYPXCors.append(X-self.pXCorZero)
                        row.pWAYPYCors.append(Y-self.pYCorZero)
                    else:
                        row.pWAYPXCors.append(X)
                        row.pWAYPYCors.append(Y)

            vROHR=vROHR[[
                     'BESCHREIBUNG'
                    ,'IDREFERENZ'
                    #Asset
                    ,'BAUJAHR','HAL'
                    ,'IPLANUNG','KENNUNG'
                    #Reibung
                    ,'L','LZU','RAU','ZAUS','ZEIN','ZUML'
                    ,'JLAMBS','LAMBDA0'
                    #inst.
                    ,'ASOLL','INDSCHALL'
                    #FW
                    ,'NAME_i_2L'
                    ,'NAME_k_2L'
                    ,'KVR'
                    #DTRO_ROWD
                    ,'AUSFALLZEIT', 'DA', 'DI', 'DN', 'KT', 'PN', 'REHABILITATION','REPARATUR', 'S', 'WSTEIG', 'WTIEFE'
                    #LTGR
                    ,'LTGR_NAME','LTGR_BESCHREIBUNG','SICHTBARKEIT','VERLEGEART'
                    #DTRO
                    ,'DTRO_NAME'
                    ,'DTRO_BESCHREIBUNG'
                    ,'E'
                    #Ref.
                    ,'fkSTRASSE','fkSRAT'
                   #IDs 
                    ,'pk','tk'          
                   #BZ
                    ,'IRTRENN'
                    ,'LECKSTART','LECKEND','LECKMENGE','LECKORT','LECKSTATUS'
                   #Rest
                    ,'QSVB'
                    ,'ZVLIMPTNZ'
                    ,'KANTENZV'
                   #CONT
                    ,'CONT' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                   #Ki
                   ,'NAME_i'
                   ,'KVR_i','TM_i'
                   ,'XKOR_i','YKOR_i','ZKOR_i'                 
                   #Kk
                   ,'NAME_k'
                   ,'KVR_k','TM_k'
                   ,'XKOR_k','YKOR_k','ZKOR_k'
                   #plotCors
                   ,'pXCor_i','pYCor_i'
                   ,'pXCor_k','pYCor_k'
                   # matplotlibs's .plot(pXCors,pYCors,...)
                   ,'pXCors','pYCors' # nur die Endpunkte
                   ,'pWAYPXCors','pWAYPYCors' # alle Wegpunkte
                   #WAYP
                   ,'WAYP' #List of Tuples: [(x1,y1),...,(xN,yN)] 
                            ]]

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)           
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))         
            return vROHR 

    def _vFWVB(self,vKNOT=None,vLFKT=None,vWBLZ=None):
        """One row per DistrictHeatingHousestation (FWVB).

        Args:
            * vKNOT 
            * vLFKT
            * wWBLZ

        Returns:
            columns
                FWVB
                    * BESCHREIBUNG
                    * IDREFERENZ
                    * W0
                    * LFK
                    * W0LFK
                    * TVL0, TRS0
                vLFKT
                    * LFKT
                    * W, W_min, W_max
                FWVB contd.
                    * INDTR, TRSK
                    * VTYP 
                    * DPHAUS, IMBG, IRFV
                FWVB IDs
                    * pk, tk  
                vKNOT
                    Ki
                        * NAME_i
                        * KVR_i, TM_i
                        * XKOR_i, YKOR_i, ZKOR_i
                        * pXCor_i, pYCor_i
                    Kk
                        * NAME_k
                        * KVR_k, TM_i
                        * XKOR_k, YKOR_k, ZKOR_i
                        * pXCor_k, pYCor_i                   
                vCONT
                    * CONT 
                    * CONT_ID
                    * CONT_LFDNR 
                vWBLZ
                    * ['BLZ1','BLZ2',...]
                        list of the WBLZ-Names of the FWVB in alphabetical Order;  
                        empty list, if FWVB is not a WBLZ-Member      
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:         
            vFWVB=None

            #logger.debug("{:s} vor _BZ: {!s:s}".format(logStr,(vFWVB)))
                            
            vFWVB=pd.merge(self.dataFrames['FWVB'],self.dataFrames['FWVB_BZ'],left_on='pk',right_on='fk')

            #logger.debug("{:s} nach _BZ: {!s:s}".format(logStr,(vFWVB)))
            #
            vFWVB=vFWVB[vFWVB['W0'].notnull()]
            vFWVB['W0']=vFWVB['W0'].str.replace(',', '.')
            vFWVB['W0']=pd.to_numeric(vFWVB['W0']) 
            #
            vFWVB['LFK']=pd.to_numeric(vFWVB['LFK']) 
            vFWVB['TVL0']=pd.to_numeric(vFWVB['TVL0']) 
            vFWVB['TRS0']=pd.to_numeric(vFWVB['TRS0'])  
            vFWVB['INDTR']=pd.to_numeric(vFWVB['INDTR'])  
            vFWVB['TRSK']=pd.to_numeric(vFWVB['TRSK'])  
            vFWVB['VTYP']=pd.to_numeric(vFWVB['VTYP'])  
            vFWVB['DPHAUS']=pd.to_numeric(vFWVB['DPHAUS']) 
            vFWVB['IMBG']=pd.to_numeric(vFWVB['IMBG']) 
            vFWVB['IRFV']=pd.to_numeric(vFWVB['IRFV']) 
            
            #
            vFWVB=pd.merge(vFWVB,vLFKT,left_on='fkLFKT',right_on='pk',how='left')
            #logger.debug("{:s} nach vLFKT: {!s:s}".format(logStr,(vFWVB)))
            #
            vFWVB['W0LFK']  = vFWVB.apply(lambda row: row.LFK    * row.W0   , axis=1)
            vFWVB['W']      = vFWVB.apply(lambda row: row.LF     * row.W0LFK, axis=1)
            vFWVB['W_min']  = vFWVB.apply(lambda row: row.LF_min * row.W0LFK, axis=1)
            vFWVB['W_max']  = vFWVB.apply(lambda row: row.LF_max * row.W0LFK, axis=1)
            #
            vFWVB=vFWVB[[
                    'BESCHREIBUNG_x','IDREFERENZ'
                   ,'W0','LFK','W0LFK','TVL0' ,'TRS0'
                   ,'W','W_min','W_max'
                   ,'INDTR' ,'TRSK'
                   ,'VTYP' 
                   ,'DPHAUS','IMBG' ,'IRFV'
                   ,'pk_x','tk'
                   ,'NAME','BESCHREIBUNG_y'
                   ,'fkKI','fkKK'
                   ,'fkCONT'
                 ]]
            vFWVB.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG','pk_x':'pk','NAME':'LFKT'},inplace=True)       
            vFWVB=vFWVB[[
                    #FWVB
                    'BESCHREIBUNG','IDREFERENZ'
                   ,'W0','LFK','W0LFK','TVL0' ,'TRS0'
                    #LFKT
                   ,'LFKT'
                   ,'W','W_min','W_max'
                    #FWVB contd.
                   ,'INDTR' ,'TRSK'
                   ,'VTYP' 
                   ,'DPHAUS', 'IMBG' ,'IRFV'
                    #FWVB IDs
                   ,'pk','tk'  
                   ,'fkKI','fkKK'   
                   ,'fkCONT'            
                 ]]    

            #logger.debug("{:s} vor fkKI: {!s:s}".format(logStr,(vFWVB)))

            vFWVB=pd.merge(vFWVB,vKNOT,left_on='fkKI',right_on='pk')   
            #logger.debug("{:s} nach fkKI: {!s:s}".format(logStr,(vFWVB)))
            vFWVB.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG','IDREFERENZ_x':'IDREFERENZ','pk_x':'pk','tk_x':'tk'},inplace=True)  
            vFWVB=vFWVB[[
                    #FWVB
                    'BESCHREIBUNG','IDREFERENZ'
                   ,'W0','LFK','W0LFK','TVL0' ,'TRS0'
                    #LFKT
                   ,'LFKT'
                   ,'W','W_min','W_max'
                    #FWVB contd.
                   ,'INDTR' ,'TRSK'
                   ,'VTYP' 
                   ,'DPHAUS','IMBG' ,'IRFV'
                    #FWVB IDs
                   ,'pk','tk'  
                    #Ki
                   ,'NAME'
                   ,'KVR','TM'
                   ,'XKOR','YKOR','ZKOR'
                   ,'pXCor','pYCor'
                   ,'fkKK'    
                   ,'fkCONT'           
                 ]]     
            vFWVB.rename(columns={'NAME':'NAME_i','KVR':'KVR_i','TM':'TM_i'},inplace=True)  
            vFWVB.rename(columns={'XKOR':'XKOR_i','YKOR':'YKOR_i','ZKOR':'ZKOR_i'
                                       ,'pXCor':'pXCor_i'
                                       ,'pYCor':'pYCor_i'},inplace=True)    
            
            vFWVB=pd.merge(vFWVB,vKNOT,left_on='fkKK',right_on='pk')    
            vFWVB.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG','IDREFERENZ_x':'IDREFERENZ','pk_x':'pk','tk_x':'tk'},inplace=True)  
            vFWVB=vFWVB[[
                    #FWVB
                    'BESCHREIBUNG','IDREFERENZ'
                   ,'W0','LFK','W0LFK','TVL0' ,'TRS0'
                    #LFKT
                   ,'LFKT'
                   ,'W','W_min','W_max'
                    #FWVB contd.
                   ,'INDTR' ,'TRSK'
                   ,'VTYP' 
                   ,'DPHAUS','IMBG' ,'IRFV'
                    #FWVB IDs
                   ,'pk','tk'  
                    #Ki
                   ,'NAME_i'
                   ,'KVR_i','TM_i'
                   ,'XKOR_i','YKOR_i','ZKOR_i'
                   ,'pXCor_i','pYCor_i'
                    #Kk
                   ,'NAME'
                   ,'KVR','TM'
                   ,'XKOR','YKOR','ZKOR'  
                   ,'pXCor','pYCor'
                   ,'fkCONT'        
                 ]]     
            vFWVB.rename(columns={'NAME':'NAME_k','KVR':'KVR_k','TM':'TM_k'},inplace=True)  
            vFWVB.rename(columns={'XKOR':'XKOR_k','YKOR':'YKOR_k','ZKOR':'ZKOR_k'
                                       ,'pXCor':'pXCor_k'
                                       ,'pYCor':'pYCor_k'},inplace=True)     
                        
            vFWVB=pd.merge(vFWVB,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk')  
            vFWVB.rename(columns={'pk_x':'pk','tk_x':'tk','NAME':'CONT','ID':'CONT_ID','LFDNR':'CONT_LFDNR'},inplace=True)    

            if 'IDREFERENZ_x' in vFWVB.columns.tolist(): #90-12
                vFWVB.rename(columns={'IDREFERENZ_x':'IDREFERENZ'},inplace=True)

            vFWVB=vFWVB[[
                    #FWVB
                    'BESCHREIBUNG','IDREFERENZ'
                   ,'W0','LFK','W0LFK','TVL0' ,'TRS0'
                    #LFKT
                   ,'LFKT'
                   ,'W','W_min','W_max'
                    #FWVB contd.
                   ,'INDTR' ,'TRSK'
                   ,'VTYP' 
                   ,'DPHAUS','IMBG' ,'IRFV'
                    #FWVB IDs
                   ,'pk','tk'  
                    #Ki
                   ,'NAME_i'
                   ,'KVR_i','TM_i'
                   ,'XKOR_i','YKOR_i','ZKOR_i'
                   ,'pXCor_i','pYCor_i'
                    #Kk
                   ,'NAME_k'
                   ,'KVR_k','TM_k'
                   ,'XKOR_k','YKOR_k','ZKOR_k'  
                   ,'pXCor_k','pYCor_k'
                    #CONT
                    ,'CONT' 
                    ,'CONT_ID'
                    ,'CONT_LFDNR' 
                     ]]

            
            #logger.debug("{:s} vor WBLZ: {!s:s}".format(logStr,(vFWVB)))

            # Waermebilanzenzugehoerigkeit            
            blzKnoten=vWBLZ.merge(vKNOT,left_on='OBJID',right_on='tk')
            rowsTk,cols=blzKnoten.shape
            blzKnotenPk=vWBLZ.merge(vKNOT,left_on='OBJID',right_on='pk')
            rowsPk,cols=blzKnotenPk.shape
            # pks oder tks in OBJID?
            if rowsTk>=rowsPk:
                pass    
            else:
                # warning
                logger.warning("{:s}pk select: {:d} > tk select {:d}?!".format(logStr,rowsPk,rowsTk))

            blzKnoten=blzKnoten[[
             'AKTIV'            
            ,'BESCHREIBUNG_x'
            ,'IDIM'
            ,'NAME_x'
            #IDs (of the WBLZ)
            ,'pk_x'
            #
            ,'pk_y'
            ,'tk'
            ,'NAME_y'
            #
            ]]
            
            blzKnoten.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG'},inplace=True)
            blzKnoten.rename(columns={'NAME_x':'NAME'},inplace=True)
            blzKnoten.rename(columns={'pk_x':'pk'},inplace=True)
            blzKnoten.rename(columns={'pk_y':'pk_NODE'},inplace=True)
            blzKnoten.rename(columns={'NAME_y':'NAME_NODE'},inplace=True)

            #VL --------------
            blzKnotenFwvbVL=blzKnoten.merge(vFWVB,left_on='NAME_NODE',right_on='NAME_i') 

            blzKnotenFwvbVL.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG'},inplace=True)
            blzKnotenFwvbVL.rename(columns={'pk_x':'pk'},inplace=True)
            blzKnotenFwvbVL.rename(columns={'tk_x':'tk_NODE'},inplace=True)
            blzKnotenFwvbVL.rename(columns={'pk_y':'pk_FWVB'},inplace=True)
            blzKnotenFwvbVL.rename(columns={'tk_y':'tk_FWVB'},inplace=True)

            blzKnotenFwvbVL=blzKnotenFwvbVL[[
             'AKTIV'            
            ,'BESCHREIBUNG'
            ,'IDIM'
            ,'NAME'
            #IDs (of the WBLZ)
            ,'pk'
            #
            ,'pk_NODE'
            ,'tk_NODE'
            ,'NAME_NODE'
            #
            ,'pk_FWVB'
            ,'tk_FWVB'
            #
            ]]

            #RL ----------------
            blzKnotenFwvbRL=blzKnoten.merge(vFWVB,left_on='NAME_NODE',right_on='NAME_k') 

            blzKnotenFwvbRL.rename(columns={'BESCHREIBUNG_x':'BESCHREIBUNG'},inplace=True)
            blzKnotenFwvbRL.rename(columns={'pk_x':'pk'},inplace=True)
            blzKnotenFwvbRL.rename(columns={'tk_x':'tk_NODE'},inplace=True)
            blzKnotenFwvbRL.rename(columns={'pk_y':'pk_FWVB'},inplace=True)
            blzKnotenFwvbRL.rename(columns={'tk_y':'tk_FWVB'},inplace=True)

            blzKnotenFwvbRL=blzKnotenFwvbRL[[
             'AKTIV'            
            ,'BESCHREIBUNG'
            ,'IDIM'
            ,'NAME'
            #IDs (of the WBLZ)
            ,'pk'
            #
            ,'pk_NODE'
            ,'tk_NODE'
            ,'NAME_NODE'
            #
            ,'pk_FWVB'
            ,'tk_FWVB'
            #
            ]]

            VLOk=vFWVB.merge(blzKnotenFwvbVL,left_on='NAME_i',right_on='NAME_NODE',suffixes=['_1','_2'])
            RLOk=vFWVB.merge(blzKnotenFwvbRL,left_on='NAME_k',right_on='NAME_NODE',suffixes=['_1','_2'])

            VLRLOk=VLOk.merge(RLOk,left_on='pk_FWVB',right_on='pk_FWVB',suffixes=['_VL','_RL'])
            #logger.debug("{:s}{!s:s}".format(logStr,(VLRLOk)))
            VLRLOk=VLRLOk[VLRLOk['NAME_VL']==VLRLOk['NAME_RL']][['pk_FWVB','NAME_VL']]
            VLRLOk.rename(columns={'NAME_VL':'NAME'},inplace=True)
            
            VLRLOk=VLRLOk.assign(wblzLfdNr=VLRLOk.sort_values(['NAME'], ascending=True)
                          .groupby(['pk_FWVB'])
                          .cumcount() + 1)

            vFWVB['WBLZ']=[list() for dummy in vFWVB['pk']]
            for index, row in vFWVB.merge(VLRLOk,left_on='pk',right_on='pk_FWVB',how='left').sort_values(by=['pk','NAME'],na_position='first').iterrows():                
                if pd.isnull(row.NAME):
                    continue
                row.WBLZ.append(row.NAME)

            #vFWVB[vFWVB['WBLZ'].apply(lambda x: 'BLNZ1' in x)]
            
            ## Last Kategorien (Load Categories); kategorisieren der FWVB nach Anschlusswert
            #Load=vFWVB.W0

            #bins=[]
            #binlabels=[]

            #bins.append(0)
            #binlabels.append('=0')

            #epsZero=0.001 #to distinguish FWVB Cat. with W0=0 from those with W0>0
            #bins.append(epsZero)
            #binlabels.append('>0')

            #bins.append(Load.quantile(.25))
            #binlabels.append('>=25%-Quart.')

            #if Load.median() < Load.mean(): #50%-Quartil < Mittelwert
            #    bins.append(Load.median()) 
            #    binlabels.append('>=Median')

            #bins.append(Load.mean())
            #binlabels.append('>=Mittelwert')

            #bins.append(bins[-1]*2)
            #binlabels.append('>=2xMittelw.')

            #if bins[-1] < Load.std():
            #    bins.append(Load.std())
            #    binlabels.append('>=Standardabw.')

            #if bins[-1] < 2*Load.std():
            #    bins.append(2*Load.std())
            #    binlabels.append('>=2*Standardabw.')

            #if bins[-1] < Load.quantile(.90):
            #    bins.append(Load.quantile(.90))
            #    binlabels.append('>=90%-Quartil')
            #else: 
            #    if bins[-1] < Load.quantile(.95):
            #        bins.append(Load.quantile(.95))
            #        binlabels.append('>=95%-Quartil')

            #bins.append(Load.max())
            #binlabels.append('Max.')

            #W0cat=pd.cut(Load,bins,include_lowest=True,right=True,precision=1)

            #W0catLabels=[x + '-: ' +  re.sub('\]$','[',re.sub('\(' ,'[', y))  for x,y in zip(binlabels[:-1],W0cat.cat.categories)]
            #W0catLabels[-1]=re.sub('\[$',']',W0catLabels[-1])

            #W0cat.cat.rename_categories(W0catLabels,inplace=True)

            ##vFWVB['W0cat']=W0cat
            ##vFWVB.groupby('W0Cat').describe()
            ##vFWVB.groupby('W0Cat').W0.sum()

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vFWVB,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vFWVB=pd.DataFrame()                 
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
            return vFWVB             

    #def vFWVB_Plt_Hist(self
    #                   ,epsZero=0.001 #to distinguish FWVB Cat. with W0=0 from those with W0>0
    #                   ,spaceBetweenCats=0.3 #the Space between the Categories; 1.0: no Space 
    #                   ):
    #    """
    #    Plots a Histogram-alike Presentation on gca().  
       
    #    """

    #    logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
    #    logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
    #    try:  
    #        #Categories 
    #        bins=[]
    #        binlabels=[]

    #        bins.append(0)
    #        binlabels.append('=0')

    #        bins.append(epsZero)
    #        binlabels.append('>0')

    #        bins.append(vFWVB.W0.quantile(.25))
    #        binlabels.append('>=25%-Quart.')

    #        if vFWVB.W0.median() < vFWVB.W0.mean(): #50%-Quartil < Mittelwert
    #            bins.append(vFWVB.W0.median()) 
    #            binlabels.append('>=Median')

    #        bins.append(vFWVB.W0.mean())
    #        binlabels.append('>=Mittelwert')

    #        bins.append(bins[-1]*2)
    #        binlabels.append('>=2xMittelw.')

    #        if bins[-1] < vFWVB.W0.std():
    #            bins.append(vFWVB.W0.std())
    #            binlabels.append('>=Standardabw.')

    #        if bins[-1] < vFWVB.W0.quantile(.95):
    #            bins.append(vFWVB.W0.quantile(.95))
    #            binlabels.append('>=95%-Quartil')

    #        bins.append(vFWVB.W0.max())
    #        binlabels.append('Max.')

    #        W0cat=pd.cut(vFWVB.W0,bins,include_lowest=True,right=True,precision=1)

    #        W0catLabels=[x + '-: ' +  re.sub('\]$','[',re.sub('\(' ,'[', y))  for x,y in zip(binlabels[:-1],W0cat.cat.categories)]
    #        W0catLabels[-1]=re.sub('\[$',']',W0catLabels[-1])

    #        #Category Data
    #        W0catSumPercent=vFWVB[vFWVB.W0>=0].groupby(W0cat).W0.sum()  /vFWVB[vFWVB.W0>=0].W0.sum() # kW Summe
    #        W0catAnzPercent=vFWVB[vFWVB.W0>=0].groupby(W0cat).W0.count()/vFWVB[vFWVB.W0>=0].W0.count() # Anzahl Summe

    #        W0catSumPercentcs=W0catSumPercent.cumsum()
    #        W0catAnzPercentcs=W0catAnzPercent.cumsum()

    #        #Bar Layout
    #        numOfBarsPerCat=2 # MW u. Anzahl
    #        numOfCats=len(W0cat.cat.categories)
    #        widthPerBar=numOfCats/(numOfCats*numOfBarsPerCat)*min(1.-spaceBetweenCats,1.0)
    #        xCats0=np.arange(numOfCats) # the x-Coordinate of the left-most Bar per Cat


    #        ax=plt.gca()

    #        #1st MW Bars
    #        barsW0catSumPercent = ax.bar(xCats0,W0catSumPercent,widthPerBar)
    #        norm = colors.Normalize(W0catSumPercentcs.min(),W0catSumPercentcs.max())
    #        colorSumPercent=[]
    #        for thisfrac, thisbar in zip(W0catSumPercentcs,barsW0catSumPercent):
    #            color = plt.cm.cool(norm(thisfrac))
    #            thisbar.set_facecolor(color)
    #            colorSumPercent.append(color)

    #        #2nd Anz Bars
    #        barsW0catAnzPercent = ax.bar(xCats0+widthPerBar,W0catAnzPercent,widthPerBar)
    #        norm = colors.Normalize(W0catAnzPercentcs.min(),W0catAnzPercentcs.max())
    #        colorAnzPercent=[]
    #        for thisfrac, thisbar in zip(W0catAnzPercentcs,barsW0catAnzPercent):
    #            color = plt.cm.autumn(norm(thisfrac))
    #            thisbar.set_facecolor(color)
    #            colorAnzPercent.append(color)

    #        #xTicks
    #        xTicks=ax.set_xticks(xCats0+numOfBarsPerCat*widthPerBar/2) #xTicks in the Middle of each Cat.
    #        xTickValues=ax.get_xticks()

    #        #xLabels
    #        xTickLabels=ax.set_xticklabels(W0catLabels,rotation='vertical')
    #        for xTickLabel in xTickLabels:
    #            x,y=xTickLabel.get_position()
    #            xTickLabel.set_position((x,y-0.0625*numOfBarsPerCat)) #Space for Cat Datanumbers (one row per Measure)

    #        #yTicks rechts (0-1)
    #        yTicksR=[x/10 for x in np.arange(10)+1]
    #        yTicksR.insert(0,0)

    #        #yTicks links
    #        # 10 Abstaende / 11 Ticks wie die r. y-Achse
    #        yMaxL=max(W0catSumPercent.max(),W0catAnzPercent.max())
    #        dyMinL=yMaxL/(len(yTicksR)-1)
    #        dyMinLr=round(dyMinL,2)
    #        if dyMinLr*(len(yTicksR)-1) < yMaxL:
    #            dyL=dyMinLr+0.01
    #        else:
    #            dyL=dyMinLr
    #        yTicksL=[x*dyL for x in np.arange(10)+1]
    #        yTicksL.insert(0,0)
    #        yTicksLObjects=ax.set_yticks(yTicksL)
    #        yTicksL=ax.get_yticks()

    #        #r. y-Achse
    #        ax2 = ax.twinx()
    #        yTicksRObjects=ax2.set_yticks(yTicksR)
    #        yTicksR=ax2.get_yticks()

    #        #Sum Curves
    #        lineW0catSumPercent,=ax2.plot(xTickValues,W0catSumPercentcs,color='gray',linewidth=1.0, ls='-',marker='s',clip_on=False)
    #        lineW0catAnzPercent,=ax2.plot(xTickValues,W0catAnzPercentcs,color='gray',linewidth=1.0, ls='-',marker='o',clip_on=False)

    #        # Cat Datanumbers (one row per Measure)
    #        measureIdx=1

    #        for kWSum, x,color in zip(vFWVB[vFWVB.W0>=0].groupby(W0cat).W0.sum(),xTickValues,colorSumPercent):
    #            txt="{0:.0f}".format(float(kWSum)/1000)
    #            ax.annotate(txt 
    #                        ,xy=(x, 0), xycoords=('data', 'axes fraction')
    #                        ,xytext=(0, measureIdx*-10), textcoords='offset points', va='top', ha='center'
    #                        ,color=color
    #                       )
    #        ax.annotate("{0:.0f} MW Ges.".format(float(vFWVB[vFWVB.W0>=0].W0.sum())/1000) 
    #                        ,xy=(x, 0), xycoords=('data', 'axes fraction')
    #                        ,xytext=(+20,measureIdx*-10), textcoords='offset points', va='top', ha='left'
    #                   )             

    #        measureIdx=measureIdx+1
    #        for count,x,color in zip(vFWVB[vFWVB.W0>=0].groupby(W0cat).W0.count(),xTickValues,colorAnzPercent):
    #            txt="{0:d}".format(int(count))
    #            ax.annotate(txt
    #                       ,xy=(x, 0),xycoords=('data', 'axes fraction')
    #                       ,xytext=(0, measureIdx*-10),textcoords='offset points', va='top', ha='center'
    #                       ,color=color
    #                       )
    #        ax.annotate("{0:d} Anz Ges.".format(int(vFWVB[vFWVB.W0>=0].W0.count())) 
    #                      ,xy=(x, 0),xycoords=('data', 'axes fraction')
    #                      ,xytext=(+20, measureIdx*-10), textcoords='offset points', va='top', ha='left'
    #                   )  
            
    #        #y-Labels 
    #        txyl=ax.set_ylabel('MW/MW Ges. u. Anz/Anz Ges.')
    #        txyr=ax2.set_ylabel('MW kum. in % u. Anz kum. in %')

    #        legend=plt.legend([lineW0catSumPercent,lineW0catAnzPercent],['MW kum. in %','Anz kum. in %'],loc='upper left')
    #        plt.grid()

    #    except Exception as e:
    #        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
    #        logger.error(logStrFinal) 
    #        raise XmError(logStrFinal)                
    #    else:
    #        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))     


    def _vVBEL(self,vKNOT=None,edges=vVBEL_edges,edgesD=vVBEL_edgesD,mColNames=['OBJTYPE','pk'],mIdxNames=['OBJTYPE','OBJID']):
        """One row per Edge.

        Args:
            * vKNOT: df 
            * edges: list of strs
            * edgesD: list of strs
            * mColNames: list of columns which shall be used as MIndex; the columns will be droped; the columns must be delivered by _vVBEL_XXXX
            * mIdxNames: list of names for the indices for the columns above

        Returns:
            Edge-df
            returned Edge-df is None if an exception occurs 

            rows:
                * sequence edges: edges
                * sequence within edges: Xml

            Mindices:
                * OBJTYPE: str: 'ROHR','VENT',... [default a MIndex not a column]
                * OBJID [default a MIndex not a column]      
              
            columns:                
                * LAYR
                * L in m (0 if edge <> ROHR)
                * D in mm (NaN if no Diameter could be determined)

            columns:                
                * see _vVBEL_XXXX
                                 
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:    
            # construct 
            vVBEL=None
            vVBEL_UnionList=[]

            for VBEL in edges:
                if VBEL in self.dataFrames:
                    vXXXX=self._vVBEL_XXXX(vKNOT=vKNOT,OBJTYPE=VBEL)
                    if vXXXX is None:
                        pass
                    else:
                        vVBEL_UnionList.append(vXXXX)
            vVBEL=pd.concat(vVBEL_UnionList)

            # MIndices
            vVBEL=Xm.constructNewMultiindexFromCols(df=vVBEL,mColNames=mColNames,mIdxNames=mIdxNames)

            # Gruppenzugeh. ergaenzen
            vVBEL['LAYR']=[list() for dummy in vVBEL['tk']]
            dfLayr=self.dataFrames['vLAYR']
            if not dfLayr.empty:
                dfLayr=dfLayr.rename(columns={'OBJTYPE':'TYPE'})         
                dfLayr=pd.merge(
                    vVBEL
                   ,dfLayr
                   ,how='inner' # nur die VBEL die eine Gruppenzugehoerigkeit haben
                   ,left_index=True 
                   ,right_on=['TYPE','OBJID']               
                   ,suffixes=('', '_y'))[['NAME','TYPE','OBJID','nrObjInGroup','nrObjtypeInGroup']]
                dfLayr=dfLayr[dfLayr.nrObjInGroup <= 1] # pro VBEL und Gruppe nur 1 Zeile

                for index, row in vVBEL.merge(dfLayr.sort_values(by=['NAME','OBJID']),how='left',left_index=True ,right_on=['TYPE','OBJID'],suffixes=('', '_y')).iterrows():                
                    if pd.isnull(row.NAME):
                        continue
                    row.LAYR.append(row.NAME)

            # L ergaenzen
            Rohr=self.dataFrames['ROHR']
            VbelL=vVBEL.join(Rohr.set_index('pk').rename_axis('OBJID', axis='index'),rsuffix='_y')[['L']]            
            vVBEL['L']=VbelL['L'].fillna(0)            

            # D ergaenzen
            # Spalte erzeugen ... 
            vRohr=self.dataFrames['vROHR']
            VbelD=vVBEL.join(vRohr.set_index('pk').rename_axis('OBJID', axis='index'),rsuffix='_y')[['DI']]
            vVBEL['D']=VbelD['DI'] # ... mit ROHR

            # ueber alle ausser ROHR
            for eIdx,edge in enumerate(edges):
                if edge == 'ROHR':
                    continue
                edgeDCol=edgesD[eIdx]
                if edgeDCol=='':
                    continue     
                if edge not in self.dataFrames:
                    continue
                Edge=self.dataFrames[edge]                      
                if edgeDCol not in Edge.columns.tolist():
                    continue
                edgeD=vVBEL.join(Edge.set_index('pk').rename_axis('OBJID', axis='index'),rsuffix='_y',how='inner')[[edgeDCol]]
                vVBEL.loc[[edge],'D']=edgeD.loc[[edge],:].values


            # fehlende Spaltenwerte zuweisen
            #Vent=self.dataFrames['VENT']
            #VentD=vVBEL.join(Vent.set_index('pk'),rsuffix='_y',how='inner')[['DN']]
            #vVBEL.loc[['VENT'],'D']=VentD.loc[['VENT'],:].values

            # Finish
            vVBEL.sort_index(level=0,inplace=True)

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.debug(logStrFinal)    
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
            return vVBEL     
        
    def _vVBEL_XXXX(self,vKNOT=None,OBJTYPE=None):
        """One row per Edge.

        Args:
            * vKNOT: df 
            * OBJTYPE: str ('ROHR','VENT',...)
                self.dataFrames[OBJTYPE] is used to build with vKNOT the returned Edge-df 

        Returns:
            Edge-df
            None is returned if an exception occurs

            columns:
                * OBJTYPE: str: ROHR,VENT,...
                
                * BESCHREIBUNG
                * IDREFERENZ
                * pk      
                * tk
                
                * NAME_i
                * CONT_i
                * CONT_VKNO_i
                * Z_i
                * pk_i
                * NAME_k
                * CONT_k
                * CONT_VKNO_k
                * Z_k
                * pk_k
                                 
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:        
            
            #'KVR','PZON_NAME', 'FSTF_NAME', 'STOF_NAME', 'GMIX_NAME','UTMP_NAME'



            vXXXX=None

            vXXXX=pd.merge(self.dataFrames[OBJTYPE],vKNOT,left_on='fkKI',right_on='pk',suffixes=('','_i'))            
            vXXXX=vXXXX[['fkKK','BESCHREIBUNG','IDREFERENZ','pk','tk','NAME','CONT','CONT_VKNO','pk_i','ZKOR']]
            vXXXX.rename(columns={'NAME':'NAME_i','CONT':'CONT_i','CONT_VKNO':'CONT_VKNO_i','ZKOR':'Z_i'},inplace=True)

            vXXXX=pd.merge(vXXXX,vKNOT,left_on='fkKK',right_on='pk',suffixes=('','_k'))
            vXXXX=vXXXX[['BESCHREIBUNG','IDREFERENZ','pk','tk','NAME_i','CONT_i','CONT_VKNO_i','Z_i','pk_i','NAME','CONT','CONT_VKNO','pk_k','ZKOR']]
            vXXXX.rename(columns={'NAME':'NAME_k','CONT':'CONT_k','CONT_VKNO':'CONT_VKNO_k','ZKOR':'Z_k'},inplace=True)
            
            vXXXX=vXXXX.assign(OBJTYPE=lambda x: OBJTYPE)
            vXXXX=vXXXX[['OBJTYPE','BESCHREIBUNG','IDREFERENZ','pk','tk','NAME_i','CONT_i','CONT_VKNO_i','Z_i','pk_i','NAME_k','CONT_k','CONT_VKNO_k','Z_k','pk_k']]

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.debug(logStrFinal) 
            vXXXX=None
         
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
            return vXXXX     

    def _vRXXX(self,nodes=vRXXX_nodes):
        """One row per R-Node.

        Args:
            * nodes: List of all R-Node Elements but RUES            

        Returns:
            R-Node df
            returned R-Node df is None if an exception occurs 

            rows:
                * sequence nodes: nodes
                * sequence within nodes: Xml

            columns:                
                * see _vRXXX_XXXX

        >>> import pandas as pd   
        >>> pd.set_option('display.width', 333)
        >>> # ---
        >>> xm=xms['DHNetwork']
        >>> # ---         
        >>> vRXXX=xm.dataFrames['vRXXX']    
        >>> vRXXX['lfdNr']=range(len(vRXXX))
        >>> vRXXX
           OBJTYPE          BESCHREIBUNG            KA                 CONT                   pk                   tk  lfdNr
        0     RSLW            Leck_1_Ein    Leck_1_Ein    AGFW Symposium DH  5706111677806224290  5706111677806224290      0
        1     RSLW            Leck_2_Ein    Leck_2_Ein    AGFW Symposium DH  4704869532416514405  4704869532416514405      1
        2     RSLW            Leck_3_Ein    Leck_3_Ein    AGFW Symposium DH  4808434710442736644  4808434710442736644      2
        3     RSLW                   wNA           wNA    AGFW Symposium DH  4991855568438544033  4991855568438544033      3
        4     RSLW                   wNB           wNB    AGFW Symposium DH  4658075570394029953  4658075570394029953      4
        5     RSLW                   wNC           wNC    AGFW Symposium DH  5240575308071562858  5240575308071562858      5
        6     RSLW              vorOrtNA      vorOrtNA    AGFW Symposium DH  5194343043762135519  5194343043762135519      6
        7     RSLW              vorOrtNB      vorOrtNB    AGFW Symposium DH  4705080808435797677  4705080808435797677      7
        8     RSLW              vorOrtNC      vorOrtNC    AGFW Symposium DH  5620348872583735825  5620348872583735825      8
        9     RSLW                 wLast         wLast    AGFW Symposium DH  5741660563170722352  5741660563170722352      9
        10    RSLW                 wTRST         wTRST    AGFW Symposium DH  5547011912763631199  5547011912763631199     10
        11    RSLW            Leck_Menge    Leck_Menge    AGFW Symposium DH  5390061625789905096  5390061625789905096     11
        12    RSLW               Leck_VL       Leck_VL    AGFW Symposium DH  4880440884169110259  4880440884169110259     12
        13    RSLW               Leck_RL       Leck_RL    AGFW Symposium DH  5644481773793849108  5644481773793849108     13
        14    RSLW              wDH_RD_A      wDH_RD_A    AGFW Symposium DH  4622192786925004485  4622192786925004485     14
        15    RSLW              wDH_MD_A      wDH_MD_A    AGFW Symposium DH  5093705160009582980  5093705160009582980     15
        16    RSLW  wDH_BA_A; 1=RD; 0=MD   wDH_BA_A_RD    AGFW Symposium DH  5322890886142492590  5322890886142492590     16
        17    RSLW                   dpA           dpA    AGFW Symposium DH  4849866990207957614  4849866990207957614     17
        18    RSLW                    qB            qB    AGFW Symposium DH  4771725364091629759  4771725364091629759     18
        19    RSLW                    qC            qC    AGFW Symposium DH  4978409087288292434  4978409087288292434     19
        20    RSLW                  None             0  Diverse Steuerungen  5486870913514090048  5486870913514090048     20
        21    RSLW                  None             1  Diverse Steuerungen  5377084992102722959  5377084992102722959     21
        22    RSLW          Analog Dummy          ADum  Diverse Steuerungen  5408457159782566744  5408457159782566744     22
        23    RSLW                  None           100  Diverse Steuerungen  5055797784689898209  5055797784689898209     23
        24    RSLW                   NaN            cp        Sekundärwerte  4838608935279518502  4838608935279518502     24
        0     RMES                   NaN          yUWM        Sekundärwerte  5008805081156446169  5008805081156446169     25
        1     RMES                   NaN            mP        Sekundärwerte  5180980864512333141  5180980864512333141     26
        2     RMES                   NaN          TRSP        Sekundärwerte  4964809001779537631  4964809001779537631     27
        3     RMES                   NaN           TVL        Sekundärwerte  5137355888694407298  5137355888694407298     28
        4     RMES                   NaN       wLastMW        Sekundärwerte  4833634373103605497  4833634373103605497     29
        5     RMES                   NaN       yLastMW        Sekundärwerte  4817923247686815456  4817923247686815456     30
        6     RMES                   NaN          yAMW        Sekundärwerte  4726758453134789052  4726758453134789052     31
        7     RMES                   NaN          yBMW        Sekundärwerte  5528896084200811302  5528896084200811302     32
        8     RMES                   NaN          yCMW        Sekundärwerte  5274276049082272588  5274276049082272588     33
        9     RMES                   NaN       dUWMMin        Sekundärwerte  5463544828758888616  5463544828758888616     34
        10    RMES                   NaN       dUWMMax        Sekundärwerte  4672771372882677276  4672771372882677276     35
        11    RMES                   NaN       KA-0026        Sekundärwerte  5714273708462554381  5714273708462554381     36
        12    RMES                   NaN        QDHGes        Sekundärwerte  5345716897595312355  5345716897595312355     37
        13    RMES                dp / 2     yDH_dp2_A        Sekundärwerte  5512879293670562022  5512879293670562022     38
        14    RMES                  None     yDH_pRL_A        Sekundärwerte  4639451967914783278  4639451967914783278     39
        0     RLVG                   NaN     wNAEin_vO    AGFW Symposium DH  4742316320267545359  4742316320267545359     40
        1     RLVG                   NaN     wNBEin_vO    AGFW Symposium DH  5013654033692161674  5013654033692161674     41
        2     RLVG                   NaN     wNCEin_vO    AGFW Symposium DH  5670691593026035398  5670691593026035398     42
        3     RLVG                   NaN   wDH_BA_A_MD    AGFW Symposium DH  4873987359791313088  4873987359791313088     43
        4     RLVG                   NaN     Leck_1_VL  Diverse Steuerungen  5669152199869266879  5669152199869266879     44
        5     RLVG                   NaN    nLeck_1_VL  Diverse Steuerungen  5517055963660007188  5517055963660007188     45
        6     RLVG                   NaN       KA-0001  Diverse Steuerungen  4937005671108174325  4937005671108174325     46
        7     RLVG                   NaN       KA-0002  Diverse Steuerungen  5752519230439786595  5752519230439786595     47
        8     RLVG                   NaN       KA-0009  Diverse Steuerungen  5660961189098354654  5660961189098354654     48
        9     RLVG                   NaN       KA-0010  Diverse Steuerungen  5510085446018401887  5510085446018401887     49
        10    RLVG                   NaN       KA-0011  Diverse Steuerungen  4894802981639605379  4894802981639605379     50
        11    RLVG                   NaN       KA-0012  Diverse Steuerungen  5310832758005678867  5310832758005678867     51
        12    RLVG                   NaN       KA-0017  Diverse Steuerungen  4879781051055847299  4879781051055847299     52
        13    RLVG                   NaN       KA-0018  Diverse Steuerungen  4806239740367977881  4806239740367977881     53
        14    RLVG                   NaN       KA-0019  Diverse Steuerungen  5447964234902471608  5447964234902471608     54
        15    RLVG                   NaN       KA-0020  Diverse Steuerungen  4717907439365620025  4717907439365620025     55
        0     RADD                   NaN            dT        Sekundärwerte  4654077245127093202  4654077245127093202     56
        1     RADD                   NaN       dLastMW        Sekundärwerte  4611793887272861500  4611793887272861500     57
        2     RADD                   NaN      yUWMLast        Sekundärwerte  5574611204646558662  5574611204646558662     58
        3     RADD                   NaN     yDH_pMD_A        Sekundärwerte  5255402486218254174  5255402486218254174     59
        4     RADD                   NaN  wDH_MD_A_ERO  Diverse Steuerungen  5729434727271745948  5729434727271745948     60
        0     RSTN                   NaN      wNA_RSTN                    A  5165635044767172069  5165635044767172069     61
        1     RSTN                   NaN       KA-0046                    A  5137384799783014264  5137384799783014264     62
        2     RSTN                   NaN       KA-0044                    A  5636962607360173089  5636962607360173089     63
        3     RSTN                   NaN       KA-0045                    A  5597572325891198144  5597572325891198144     64
        4     RSTN                   NaN      wNB_RSTN                    B  5342104608381486733  5342104608381486733     65
        5     RSTN                   NaN       KA-0053                    B  5338620382667478180  5338620382667478180     66
        6     RSTN                   NaN       KA-0057                    B  5226612456739754122  5226612456739754122     67
        7     RSTN                   NaN       KA-0058                    B  5537037692802520861  5537037692802520861     68
        8     RSTN                   NaN      wNC_RSTN                    C  5103693862180601916  5103693862180601916     69
        9     RSTN                   NaN       KA-0059                    C  4792266770335818241  4792266770335818241     70
        10    RSTN                   NaN       KA-0060                    C  5286169822203128424  5286169822203128424     71
        11    RSTN                   NaN       KA-0061                    C  4848495011382561496  4848495011382561496     72
        12    RSTN                   NaN       KA-0004  Diverse Steuerungen  5625633953643797107  5625633953643797107     73
        13    RSTN                   NaN       KA-0005  Diverse Steuerungen  4851348857631426312  4851348857631426312     74
        14    RSTN                   NaN       KA-0006  Diverse Steuerungen  5185169121447805605  5185169121447805605     75
        15    RSTN                   NaN       KA-0008  Diverse Steuerungen  4760680402451575539  4760680402451575539     76
        16    RSTN                   NaN       KA-0003  Diverse Steuerungen  5249070009027066113  5249070009027066113     77
        17    RSTN                   NaN       KA-0007  Diverse Steuerungen  5721409231684230901  5721409231684230901     78
        18    RSTN                   NaN       KA-0013  Diverse Steuerungen  5075554822852863012  5075554822852863012     79
        19    RSTN                   NaN       KA-0014  Diverse Steuerungen  5320878233009751638  5320878233009751638     80
        20    RSTN                   NaN       KA-0015  Diverse Steuerungen  5749069735826810904  5749069735826810904     81
        21    RSTN                   NaN       KA-0016  Diverse Steuerungen  5704472379299329003  5704472379299329003     82
        22    RSTN                   NaN       KA-0021  Diverse Steuerungen  5629658054546932585  5629658054546932585     83
        23    RSTN                   NaN       KA-0022  Diverse Steuerungen  5162821695312832398  5162821695312832398     84
        24    RSTN                   NaN       KA-0023  Diverse Steuerungen  5357357577779591773  5357357577779591773     85
        25    RSTN                   NaN       KA-0024  Diverse Steuerungen  5357348958190741976  5357348958190741976     86
        26    RSTN                   NaN       KA-0025  Diverse Steuerungen  4635966862484721732  4635966862484721732     87
        27    RSTN                   NaN       KA-0027  Diverse Steuerungen  5700600513951468434  5700600513951468434     88
        28    RSTN                   NaN       KA-0028  Diverse Steuerungen  5367185280774605989  5367185280774605989     89
        29    RSTN                   NaN       KA-0029  Diverse Steuerungen  5445770133105602710  5445770133105602710     90
        30    RSTN                   NaN       KA-0030  Diverse Steuerungen  4885570100974274375  4885570100974274375     91
        31    RSTN                   NaN       KA-0031  Diverse Steuerungen  5223383850171539514  5223383850171539514     92
        32    RSTN          NTR_1_RL_Ein       KA-0032  Diverse Steuerungen  5333724089944967011  5333724089944967011     93
        33    RSTN          NTR_1_VL_Ein       KA-0033  Diverse Steuerungen  4825143842549434339  4825143842549434339     94
        34    RSTN          NTR_1_VL_Ein       KA-0034  Diverse Steuerungen  4693599139501858956  4693599139501858956     95
        35    RSTN          NTR_1_RL_Ein       KA-0035  Diverse Steuerungen  5693503518255620080  5693503518255620080     96
        36    RSTN          NTR_3_Aus_VL       KA-0036  Diverse Steuerungen  4901609871029871596  4901609871029871596     97
        37    RSTN          NTR_3_Aus_RL       KA-0037  Diverse Steuerungen  5327767233627106399  5327767233627106399     98
        38    RSTN          NTR_3_Ein_VL       KA-0038  Diverse Steuerungen  5760765754619184144  5760765754619184144     99
        39    RSTN          NTR_3_Ein_RL       KA-0039  Diverse Steuerungen  4994799657516451637  4994799657516451637    100
        40    RSTN          NTR_2_Aus_VL       KA-0040  Diverse Steuerungen  5348583181653286363  5348583181653286363    101
        41    RSTN          NTR_2_Aus_RL       KA-0041  Diverse Steuerungen  5499083775210733192  5499083775210733192    102
        42    RSTN          NTR_2_Ein_VL       KA-0042  Diverse Steuerungen  4990389026836623226  4990389026836623226    103
        43    RSTN          NTR_2_Ein_RL       KA-0043  Diverse Steuerungen  5697786347617919077  5697786347617919077    104
        44    RSTN                   NaN       KA-0054  Diverse Steuerungen  5623872434691357889  5623872434691357889    105
        45    RSTN                   NaN       KA-0055  Diverse Steuerungen  5283008774827895454  5283008774827895454    106
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:    
            # construct 
            vRXXX=None
            vRXXX_UnionList=[]

            for NODE in nodes:
                if NODE in self.dataFrames:
                    vRXXX=self._vRXXX_XXXX(OBJTYPE=NODE)
                    if vRXXX is None:
                        pass
                    else:
                        vRXXX_UnionList.append(vRXXX)
            vRXXX=pd.concat(vRXXX_UnionList)
          
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vRXXX,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vRXXX=pd.DataFrame()              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vRXXX
        
    def _vRXXX_XXXX(self,OBJTYPE=None):
        """One row per R-Node of Type OBJTYPE.

        Args:
            OBJTYPE: str: i.e. RHYS

        Returns:
            R-Node df
            None is returned if an exception occurs

            columns:
                * OBJTYPE: str: i.e. RADD
                
                * BESCHREIBUNG
                * KA

                * CONT   

                * pk      
                * tk                                           
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:        
                        
            vRXXX=None

            vRXXX=self.dataFrames[OBJTYPE]            

            vRXXX=pd.merge(vRXXX,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=('','_CONT'))
            
            vRXXX=vRXXX[[
                'BESCHREIBUNG'
               ,'KA'
               ,'pk'      
               ,'tk'
               ,'NAME'
            ]]

            vRXXX.rename(columns={"NAME": "CONT"},inplace=True)

            vRXXX['OBJTYPE']=OBJTYPE

            vRXXX=vRXXX[[
                'OBJTYPE'
               ,'BESCHREIBUNG'
               ,'KA'
               ,'CONT'
               ,'pk'      
               ,'tk'               
            ]]

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.debug(logStrFinal) 
            vRXXX=None
         
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))
            return vRXXX     

    def MxSync(self,mx=None,ForceNoH5ReadForMx=False,ForceNoH5Update=False):
        """Xm: NEW 1st Call: vNRCV_Mx1: vNRCV with MX1-Information. Some Xm-Views with MX2-Information (mx2Idx).Mx: Sir3sID Update in Mx-Object. 

        Args:
            mx (default: None): Mx-Object
                * If no Mx-Object is given the Mx-Object corresponding to the Xm-Object is constructed and returned.       
                * Notes:                  
                    * The Sync-Result in Xm is persisted if xm were read from H5:                    
                        * xm.ToH5() is called if xm.h5Read is True and not ForceNoH5Update. 
                    * The Sync-Result in Mx is persisted if mx were read from H5:    
                        * mx.ToH5() is called (from __Mx1_Sir3sIDUpd) if Sir3sID-Updates occured and mx.h5Read is True and not ForceNoH5Update.

            ForceNoH5ReadForMx (deafault: False): has an Effect onlx if a new Mx-Object is constructed
                * ForceNoH5ReadForMx = True:
                    * the new Mx-Object is constructed with NoH5Read=True
                * ForceNoH5ReadForMx = False: 
                    * the new Mx-Object is constructed with NoH5Read = not self.h5Read 
                    * if the Xm was read from H5 the Mx is constructed with NoH5Read=False
                    * if the Xm was not read from H5 the Mx is constructed with NoH5Read=True

            ForceNoH5Update (default: False): if read from H5, H5 is updated if ForceNoH5Update is False
                       
        Returns:
            Mx-Object if no Mx-Object was given; Nothing else

        Raises:
            XmError

        >>> # -q -m 0 -s MxAdd -t both -y yes -z no -w LocalHeatingNetwork        
        >>> xm=xms['LocalHeatingNetwork']
        >>> xm.h5Read # False due to MockUp
        False
        >>> mx=xm.MxSync()
        >>> mx.h5Read # False due to MockUp
        False
        """
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            returnNothing=False
            if isinstance(mx,Mx.Mx):                
                returnNothing=True
            else:
                mx=self._MxSyncAddMx(ForceNoH5ReadForMx=ForceNoH5ReadForMx)
             
            self.__Mx1_Sir3sIDUpd(mx,ForceNoH5Update=ForceNoH5Update) # Sir3sID

            self.__Mx1_vNRCV(mx) # vNRCV

            self.__Mx2_vKNOT(mx) # vKNOT
            self.__Mx2_vROHR(mx) # vROHR
            self.__Mx2_vFWVB(mx) # vFWVB           
            self.__Mx2_vVBEL(mx) # vVBEL

            if self.h5Read and not ForceNoH5Update:
                self.ToH5()
                                                       
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            if not returnNothing:
                return mx

    def _vREdges(self):
        """Returns vREdges.

        columns:

            OBJTYPE_Ki
            BESCHREIBUNG_Ki
            Kn_Ki: Node ID
            pk_Ki: Node ID

            OBJTYPE_Kk
            BESCHREIBUNG_Kk
            Kn_Kk
            pk_Kk
            CONT
            
            KnExt_Ki: with OBJTYPE extended Node ID
            KnExt_Kk: with OBJTYPE extended Node ID
            
        >>> import pandas as pd             
        >>> # ---
        >>> xm=xms['DHNetwork']
        >>> # ---                    
        >>> vREdges=xm.dataFrames['vREdges']
        >>> pd.set_option('display.width', 333)
        >>> pd.set_option('display.max_columns',None)
        >>> pd.set_option('display.max_rows',None)
        >>> vREdges[[
        ...  'CONT'
        ... ,'CONT_PARENT'
        ... ,'OBJTYPE_Ki'
        ... ,'OBJTYPE_Kk'        
        ... ,'Kn_Ki'
        ... ,'Kn_Kk'
        ... ,'KnExt_Ki'
        ... ,'KnExt_Kk'
        ... ]].sort_values(by=['KnExt_Ki','KnExt_Kk','CONT']).sort_index()
                            CONT          CONT_PARENT OBJTYPE_Ki OBJTYPE_Kk         Kn_Ki         Kn_Kk           KnExt_Ki           KnExt_Kk
        0      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES    Leck_1_Ein    Leck_1_Ein    Leck_1_Ein_RSLW    Leck_1_Ein_RUES
        1      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES    Leck_2_Ein    Leck_2_Ein    Leck_2_Ein_RSLW    Leck_2_Ein_RUES
        2      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES    Leck_3_Ein    Leck_3_Ein    Leck_3_Ein_RSLW    Leck_3_Ein_RUES
        3      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES           wNA           wNA           wNA_RSLW           wNA_RUES
        4      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES           wNB           wNB           wNB_RSLW           wNB_RUES
        5      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES           wNC           wNC           wNC_RSLW           wNC_RUES
        6      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES      vorOrtNA      vorOrtNA      vorOrtNA_RSLW      vorOrtNA_RUES
        7      AGFW Symposium DH    AGFW Symposium DH       RUES       RLVG      vorOrtNA     wNAEin_vO      vorOrtNA_RUES     wNAEin_vO_RLVG
        8      AGFW Symposium DH    AGFW Symposium DH       RLVG       RUES     wNAEin_vO        wNAEin     wNAEin_vO_RLVG        wNAEin_RUES
        9      AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES      vorOrtNB      vorOrtNB      vorOrtNB_RSLW      vorOrtNB_RUES
        10     AGFW Symposium DH    AGFW Symposium DH       RUES       RLVG      vorOrtNB     wNBEin_vO      vorOrtNB_RUES     wNBEin_vO_RLVG
        11     AGFW Symposium DH    AGFW Symposium DH       RLVG       RUES     wNBEin_vO        wNBEin     wNBEin_vO_RLVG        wNBEin_RUES
        12     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES      vorOrtNC      vorOrtNC      vorOrtNC_RSLW      vorOrtNC_RUES
        13     AGFW Symposium DH    AGFW Symposium DH       RUES       RLVG      vorOrtNC     wNCEin_vO      vorOrtNC_RUES     wNCEin_vO_RLVG
        14     AGFW Symposium DH    AGFW Symposium DH       RLVG       RUES     wNCEin_vO        wNCEin     wNCEin_vO_RLVG        wNCEin_RUES
        15     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES         wLast         wLast         wLast_RSLW         wLast_RUES
        16     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES         wTRST         wTRST         wTRST_RSLW         wTRST_RUES
        17     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES    Leck_Menge    Leck_Menge    Leck_Menge_RSLW    Leck_Menge_RUES
        18     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES       Leck_VL       Leck_VL       Leck_VL_RSLW       Leck_VL_RUES
        19     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES       Leck_RL       Leck_RL       Leck_RL_RSLW       Leck_RL_RUES
        20     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES      wDH_RD_A      wDH_RD_A      wDH_RD_A_RSLW      wDH_RD_A_RUES
        21     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES      wDH_MD_A      wDH_MD_A      wDH_MD_A_RSLW      wDH_MD_A_RUES
        22     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES   wDH_BA_A_RD   wDH_BA_A_RD   wDH_BA_A_RD_RSLW   wDH_BA_A_RD_RUES
        23     AGFW Symposium DH    AGFW Symposium DH       RUES       RLVG   wDH_BA_A_RD   wDH_BA_A_MD   wDH_BA_A_RD_RUES   wDH_BA_A_MD_RLVG
        24     AGFW Symposium DH    AGFW Symposium DH       RLVG       RUES   wDH_BA_A_MD   wDH_BA_A_MD   wDH_BA_A_MD_RLVG   wDH_BA_A_MD_RUES
        25     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES           dpA           dpA           dpA_RSLW           dpA_RUES
        26     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES            qB            qB            qB_RSLW            qB_RUES
        27     AGFW Symposium DH    AGFW Symposium DH       RSLW       RUES            qC            qC            qC_RSLW            qC_RUES
        28   Diverse Steuerungen    AGFW Symposium DH       RSLW       RUES             0             0             0_RSLW             0_RUES
        29   Diverse Steuerungen    AGFW Symposium DH       RSLW       RUES             1             1             1_RSLW             1_RUES
        30   Diverse Steuerungen    AGFW Symposium DH       RSLW       RUES          ADum          ADum          ADum_RSLW          ADum_RUES
        31   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN         wLast       KA-0004         wLast_RUES       KA-0004_RSTN
        32   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0004             1_RUES       KA-0004_RSTN
        33   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN         wTRST       KA-0005         wTRST_RUES       KA-0005_RSTN
        34   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0005             1_RUES       KA-0005_RSTN
        35   Diverse Steuerungen    AGFW Symposium DH       RSLW       RUES           100           100           100_RSLW           100_RUES
        36   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_1_Ein     Leck_1_VL    Leck_1_Ein_RUES     Leck_1_VL_RLVG
        37   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_VL     Leck_1_VL       Leck_VL_RUES     Leck_1_VL_RLVG
        38   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN     Leck_1_VL       KA-0006     Leck_1_VL_RLVG       KA-0006_RSTN
        39   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0006          ADum_RUES       KA-0006_RSTN
        40   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG     Leck_1_VL    nLeck_1_VL     Leck_1_VL_RLVG    nLeck_1_VL_RLVG
        41   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0008          ADum_RUES       KA-0008_RSTN
        42   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN    nLeck_1_VL       KA-0008    nLeck_1_VL_RLVG       KA-0008_RSTN
        43   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_1_Ein       KA-0001    Leck_1_Ein_RUES       KA-0001_RLVG
        44   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_RL       KA-0001       Leck_RL_RUES       KA-0001_RLVG
        45   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0001       KA-0003       KA-0001_RLVG       KA-0003_RSTN
        46   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0003          ADum_RUES       KA-0003_RSTN
        47   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG       KA-0001       KA-0002       KA-0001_RLVG       KA-0002_RLVG
        48   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0007          ADum_RUES       KA-0007_RSTN
        49   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0002       KA-0007       KA-0002_RLVG       KA-0007_RSTN
        50   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_RL       KA-0011       Leck_RL_RUES       KA-0011_RLVG
        51   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_2_Ein       KA-0011    Leck_2_Ein_RUES       KA-0011_RLVG
        52   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_2_Ein       KA-0009    Leck_2_Ein_RUES       KA-0009_RLVG
        53   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_VL       KA-0009       Leck_VL_RUES       KA-0009_RLVG
        54   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0009       KA-0013       KA-0009_RLVG       KA-0013_RSTN
        55   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0013          ADum_RUES       KA-0013_RSTN
        56   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG       KA-0009       KA-0010       KA-0009_RLVG       KA-0010_RLVG
        57   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0015          ADum_RUES       KA-0015_RSTN
        58   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0010       KA-0015       KA-0010_RLVG       KA-0015_RSTN
        59   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0011       KA-0014       KA-0011_RLVG       KA-0014_RSTN
        60   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0014          ADum_RUES       KA-0014_RSTN
        61   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG       KA-0011       KA-0012       KA-0011_RLVG       KA-0012_RLVG
        62   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0016          ADum_RUES       KA-0016_RSTN
        63   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0012       KA-0016       KA-0012_RLVG       KA-0016_RSTN
        64   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_RL       KA-0019       Leck_RL_RUES       KA-0019_RLVG
        65   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_3_Ein       KA-0019    Leck_3_Ein_RUES       KA-0019_RLVG
        66   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG    Leck_3_Ein       KA-0017    Leck_3_Ein_RUES       KA-0017_RLVG
        67   Diverse Steuerungen    AGFW Symposium DH       RUES       RLVG       Leck_VL       KA-0017       Leck_VL_RUES       KA-0017_RLVG
        68   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0017       KA-0021       KA-0017_RLVG       KA-0021_RSTN
        69   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0021          ADum_RUES       KA-0021_RSTN
        70   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG       KA-0017       KA-0018       KA-0017_RLVG       KA-0018_RLVG
        71   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0023          ADum_RUES       KA-0023_RSTN
        72   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0018       KA-0023       KA-0018_RLVG       KA-0023_RSTN
        73   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0019       KA-0022       KA-0019_RLVG       KA-0022_RSTN
        74   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0022          ADum_RUES       KA-0022_RSTN
        75   Diverse Steuerungen    AGFW Symposium DH       RLVG       RLVG       KA-0019       KA-0020       KA-0019_RLVG       KA-0020_RLVG
        76   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0024          ADum_RUES       KA-0024_RSTN
        77   Diverse Steuerungen    AGFW Symposium DH       RLVG       RSTN       KA-0020       KA-0024       KA-0020_RLVG       KA-0024_RSTN
        78   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0025    Leck_Menge_RUES       KA-0025_RSTN
        79   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0025             1_RUES       KA-0025_RSTN
        80   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0027    Leck_Menge_RUES       KA-0027_RSTN
        81   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0027             1_RUES       KA-0027_RSTN
        82   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0028    Leck_Menge_RUES       KA-0028_RSTN
        83   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0028             1_RUES       KA-0028_RSTN
        84   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0029    Leck_Menge_RUES       KA-0029_RSTN
        85   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0029             1_RUES       KA-0029_RSTN
        86   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0030    Leck_Menge_RUES       KA-0030_RSTN
        87   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0030             1_RUES       KA-0030_RSTN
        88   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN    Leck_Menge       KA-0031    Leck_Menge_RUES       KA-0031_RSTN
        89   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             1       KA-0031             1_RUES       KA-0031_RSTN
        90   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0032          ADum_RUES       KA-0032_RSTN
        91   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0032             0_RUES       KA-0032_RSTN
        92   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0033             0_RUES       KA-0033_RSTN
        93   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0033          ADum_RUES       KA-0033_RSTN
        94   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0034             0_RUES       KA-0034_RSTN
        95   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0034          ADum_RUES       KA-0034_RSTN
        96   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0035             0_RUES       KA-0035_RSTN
        97   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0035          ADum_RUES       KA-0035_RSTN
        98   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0036             0_RUES       KA-0036_RSTN
        99   Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0036          ADum_RUES       KA-0036_RSTN
        100  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0037             0_RUES       KA-0037_RSTN
        101  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0037          ADum_RUES       KA-0037_RSTN
        102  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0038             0_RUES       KA-0038_RSTN
        103  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0038          ADum_RUES       KA-0038_RSTN
        104  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0039             0_RUES       KA-0039_RSTN
        105  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0039          ADum_RUES       KA-0039_RSTN
        106  Diverse Steuerungen    AGFW Symposium DH       RUES       RADD     yDH_dp2_A  wDH_MD_A_ERO     yDH_dp2_A_RUES  wDH_MD_A_ERO_RADD
        107  Diverse Steuerungen    AGFW Symposium DH       RUES       RADD      wDH_MD_A  wDH_MD_A_ERO      wDH_MD_A_RUES  wDH_MD_A_ERO_RADD
        108  Diverse Steuerungen    AGFW Symposium DH       RADD       RUES  wDH_MD_A_ERO  wDH_MD_A_ERO  wDH_MD_A_ERO_RADD  wDH_MD_A_ERO_RUES
        109  Diverse Steuerungen    AGFW Symposium DH       RUES       RUES      wDH_RD_A  wDH_RD_A_ERO      wDH_RD_A_RUES  wDH_RD_A_ERO_RUES
        110  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN  wDH_RD_A_ERO       KA-0054  wDH_RD_A_ERO_RUES       KA-0054_RSTN
        111  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN   wDH_BA_A_RD       KA-0054   wDH_BA_A_RD_RUES       KA-0054_RSTN
        112  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN  wDH_MD_A_ERO       KA-0055  wDH_MD_A_ERO_RUES       KA-0055_RSTN
        113  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN   wDH_BA_A_MD       KA-0055   wDH_BA_A_MD_RUES       KA-0055_RSTN
        114  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0040             0_RUES       KA-0040_RSTN
        115  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0040          ADum_RUES       KA-0040_RSTN
        116  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0041             0_RUES       KA-0041_RSTN
        117  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0041          ADum_RUES       KA-0041_RSTN
        118  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0042             0_RUES       KA-0042_RSTN
        119  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0042          ADum_RUES       KA-0042_RSTN
        120  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN             0       KA-0043             0_RUES       KA-0043_RSTN
        121  Diverse Steuerungen    AGFW Symposium DH       RUES       RSTN          ADum       KA-0043          ADum_RUES       KA-0043_RSTN
        122                    A    AGFW Symposium DH       RUES       RSTN        wNAEin      wNA_RSTN        wNAEin_RUES      wNA_RSTN_RSTN
        123                    A    AGFW Symposium DH       RUES       RSTN           wNA      wNA_RSTN           wNA_RUES      wNA_RSTN_RSTN
        124                    A    AGFW Symposium DH       RUES       RSTN        wNBEin       KA-0044        wNBEin_RUES       KA-0044_RSTN
        125                    A    AGFW Symposium DH       RUES       RSTN          ADum       KA-0044          ADum_RUES       KA-0044_RSTN
        126                    A    AGFW Symposium DH       RUES       RSTN      vorOrtNC       KA-0045      vorOrtNC_RUES       KA-0045_RSTN
        127                    A    AGFW Symposium DH       RUES       RSTN          ADum       KA-0045          ADum_RUES       KA-0045_RSTN
        128                    A    AGFW Symposium DH       RUES       RSTN           dpA       KA-0046           dpA_RUES       KA-0046_RSTN
        129                    A    AGFW Symposium DH       RUES       RSTN      vorOrtNC       KA-0046      vorOrtNC_RUES       KA-0046_RSTN
        130                    B    AGFW Symposium DH       RUES       RSTN        wNBEin      wNB_RSTN        wNBEin_RUES      wNB_RSTN_RSTN
        131                    B    AGFW Symposium DH       RUES       RSTN           wNB      wNB_RSTN           wNB_RUES      wNB_RSTN_RSTN
        132                    B    AGFW Symposium DH       RUES       RSTN        wNBEin       KA-0053        wNBEin_RUES       KA-0053_RSTN
        133                    B    AGFW Symposium DH       RUES       RSTN          ADum       KA-0053          ADum_RUES       KA-0053_RSTN
        134                    B    AGFW Symposium DH       RUES       RSTN      vorOrtNB       KA-0057      vorOrtNB_RUES       KA-0057_RSTN
        135                    B    AGFW Symposium DH       RUES       RSTN          ADum       KA-0057          ADum_RUES       KA-0057_RSTN
        136                    B    AGFW Symposium DH       RUES       RSTN            qB       KA-0058            qB_RUES       KA-0058_RSTN
        137                    B    AGFW Symposium DH       RUES       RSTN      vorOrtNB       KA-0058      vorOrtNB_RUES       KA-0058_RSTN
        138                    C    AGFW Symposium DH       RUES       RSTN        wNCEin      wNC_RSTN        wNCEin_RUES      wNC_RSTN_RSTN
        139                    C    AGFW Symposium DH       RUES       RSTN           wNC      wNC_RSTN           wNC_RUES      wNC_RSTN_RSTN
        140                    C    AGFW Symposium DH       RUES       RSTN        wNCEin       KA-0059        wNCEin_RUES       KA-0059_RSTN
        141                    C    AGFW Symposium DH       RUES       RSTN          ADum       KA-0059          ADum_RUES       KA-0059_RSTN
        142                    C    AGFW Symposium DH       RUES       RSTN          ADum       KA-0060          ADum_RUES       KA-0060_RSTN
        143                    C    AGFW Symposium DH       RUES       RSTN      vorOrtNC       KA-0060      vorOrtNC_RUES       KA-0060_RSTN
        144                    C    AGFW Symposium DH       RUES       RSTN            qC       KA-0061            qC_RUES       KA-0061_RSTN
        145                    C    AGFW Symposium DH       RUES       RSTN      vorOrtNC       KA-0061      vorOrtNC_RUES       KA-0061_RSTN
        146        Sekundärwerte  Diverse Steuerungen       RMES       RADD          TRSP            dT          TRSP_RMES            dT_RADD
        147        Sekundärwerte  Diverse Steuerungen       RMES       RADD           TVL            dT           TVL_RMES            dT_RADD
        148        Sekundärwerte  Diverse Steuerungen       RMES       RUES          yUWM          yUWM          yUWM_RMES          yUWM_RUES
        149        Sekundärwerte  Diverse Steuerungen       RMES       RUES       wLastMW       wLastMW       wLastMW_RMES       wLastMW_RUES
        150        Sekundärwerte  Diverse Steuerungen       RMES       RUES       yLastMW       yLastMW       yLastMW_RMES       yLastMW_RUES
        151        Sekundärwerte  Diverse Steuerungen       RUES       RADD       yLastMW       dLastMW       yLastMW_RUES       dLastMW_RADD
        152        Sekundärwerte  Diverse Steuerungen       RUES       RADD       wLastMW       dLastMW       wLastMW_RUES       dLastMW_RADD
        153        Sekundärwerte  Diverse Steuerungen       RADD       RUES       dLastMW       dLastMW       dLastMW_RADD       dLastMW_RUES
        154        Sekundärwerte  Diverse Steuerungen       RMES       RUES          yAMW          yAMW          yAMW_RMES          yAMW_RUES
        155        Sekundärwerte  Diverse Steuerungen       RMES       RUES          yBMW          yBMW          yBMW_RMES          yBMW_RUES
        156        Sekundärwerte  Diverse Steuerungen       RMES       RUES          yCMW          yCMW          yCMW_RMES          yCMW_RUES
        157        Sekundärwerte  Diverse Steuerungen       RMES       RUES       dUWMMin       dUWMMin       dUWMMin_RMES       dUWMMin_RUES
        158        Sekundärwerte  Diverse Steuerungen       RMES       RUES       dUWMMax       dUWMMax       dUWMMax_RMES       dUWMMax_RUES
        159        Sekundärwerte  Diverse Steuerungen       RUES       RADD          yUWM      yUWMLast          yUWM_RUES      yUWMLast_RADD
        160        Sekundärwerte  Diverse Steuerungen       RMES       RADD       KA-0026      yUWMLast       KA-0026_RMES      yUWMLast_RADD
        161        Sekundärwerte  Diverse Steuerungen       RADD       RUES      yUWMLast      yUWMLast      yUWMLast_RADD      yUWMLast_RUES
        162        Sekundärwerte  Diverse Steuerungen       RMES       RUES        QDHGes        QDHGes        QDHGes_RMES        QDHGes_RUES
        163        Sekundärwerte  Diverse Steuerungen       RMES       RUES     yDH_dp2_A     yDH_dp2_A     yDH_dp2_A_RMES     yDH_dp2_A_RUES
        164        Sekundärwerte  Diverse Steuerungen       RUES       RADD     yDH_dp2_A     yDH_pMD_A     yDH_dp2_A_RUES     yDH_pMD_A_RADD
        165        Sekundärwerte  Diverse Steuerungen       RUES       RADD     yDH_pRL_A     yDH_pMD_A     yDH_pRL_A_RUES     yDH_pMD_A_RADD
        166        Sekundärwerte  Diverse Steuerungen       RADD       RUES     yDH_pMD_A     yDH_pMD_A     yDH_pMD_A_RADD     yDH_pMD_A_RUES
        167        Sekundärwerte  Diverse Steuerungen       RMES       RUES     yDH_pRL_A     yDH_pRL_A     yDH_pRL_A_RMES     yDH_pRL_A_RUES
        >>> import networkx as nx
        >>> G=nx.from_pandas_edgelist(vREdges, source='KnExt_Ki', target='KnExt_Kk', edge_attr=True,create_using=nx.DiGraph())
        >>> list(nx.selfloop_edges(G))
        []
        >>> pathNodes=nx.shortest_path(G,'Leck_1_Ein_RSLW','KA-0008_RSTN')
        >>> pathNodes
        ['Leck_1_Ein_RSLW', 'Leck_1_Ein_RUES', 'Leck_1_VL_RLVG', 'nLeck_1_VL_RLVG', 'KA-0008_RSTN']
        >>> sink_nodes = [node for node, outdegree in G.out_degree(G.nodes()) if outdegree == 0]        
        >>> source_nodes = [node for node, indegree in G.in_degree(G.nodes()) if indegree == 0]        
        >>> import re
        >>> for source, sink in [(source, sink) for sink in sink_nodes for source in source_nodes]: # ueber alle Quellen pro Senke ...
        ...     if re.search('_RSTN$',sink) != None:
        ...         for path in nx.all_simple_paths(G, source=source, target=sink):
        ...             if sink=='KA-0008_RSTN':
        ...                 path  
        ['Leck_1_Ein_RSLW', 'Leck_1_Ein_RUES', 'Leck_1_VL_RLVG', 'nLeck_1_VL_RLVG', 'KA-0008_RSTN']
        ['Leck_VL_RSLW', 'Leck_VL_RUES', 'Leck_1_VL_RLVG', 'nLeck_1_VL_RLVG', 'KA-0008_RSTN']
        ['ADum_RSLW', 'ADum_RUES', 'KA-0008_RSTN']
        >>> #---
        >>> # dasselbe mit Knotennamen ohne Postfix ...
        >>> G=nx.from_pandas_edgelist(vREdges, source='Kn_Ki', target='Kn_Kk', edge_attr=True,create_using=nx.DiGraph())
        >>> # alle RUES Eingänge deren ID mit der des aufnehmenden Signals identisch ist führen dann zu Schleifen ...
        >>> # ... die entfernt werden muessen wenn Quellen am Indegree erkannt werden sollen ...
        >>> G.remove_edges_from(list(nx.selfloop_edges(G)))
        >>> pathNodes=nx.shortest_path(G,'Leck_1_Ein','KA-0008')
        >>> pathNodes # (auf die Pfadknotensequenz haben Schleifen keinen Einfluss, das Ergebnis waere mit den Schleifen dasselbe ...)
        ['Leck_1_Ein', 'Leck_1_VL', 'nLeck_1_VL', 'KA-0008']
        >>> sink_nodes = [node for node, outdegree in G.out_degree(G.nodes()) if outdegree == 0]        
        >>> source_nodes = [node for node, indegree in G.in_degree(G.nodes()) if indegree == 0]           
        >>> for source, sink in [(source, sink) for sink in sink_nodes for source in source_nodes]: # ueber alle Quellen pro Senke ...      
        ...         for path in nx.all_simple_paths(G, source=source, target=sink):
        ...             if sink=='KA-0008':
        ...                 path    
        ['Leck_1_Ein', 'Leck_1_VL', 'nLeck_1_VL', 'KA-0008']
        ['Leck_VL', 'Leck_1_VL', 'nLeck_1_VL', 'KA-0008']
        ['ADum', 'KA-0008']
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:    

            vREdges=None

            vRUES=self.dataFrames['vRUES'] # IDUE IOTYP               rkRUES   IDUE_rkRUES IOTYP_rkRUES                 CONT    ID          CONT_rkRUES ID_rkRUES                   pk                   rk            Kn
            vRXXX=self.dataFrames['vRXXX'] # OBJTYPE          BESCHREIBUNG            KA                 CONT                   pk                   tk
                        
            # vRNodes
            # Aenderungen fuer Union
            vRUES['OBJTYPE']='RUES'
            vRUES['BESCHREIBUNG']=None
            vRXXX=vRXXX.rename(columns={'KA':'Kn'})
                                                         
            vRNodes=None

            vRNodes_UnionList=[]
            vRNodes_UnionList.append(vRXXX[['OBJTYPE','BESCHREIBUNG','Kn','CONT','pk']])
            vRNodes_UnionList.append(vRUES[['OBJTYPE','BESCHREIBUNG','Kn','CONT','pk']])
            vRNodes=pd.concat(vRNodes_UnionList)
           
            # vREdges            
            CRGL=self.dataFrames['CRGL']

            # CONT ergänzen
            colList=CRGL.columns.tolist()
            CRGL=pd.merge(CRGL,self.dataFrames['CONT'],left_on='fkCONT',right_on='pk',suffixes=('','_CONT'))
            CRGL=CRGL.filter(items=colList+['NAME']+['rkPARENT'])            
            CRGL.rename(columns={'NAME':'CONT'},inplace=True)

            colList=CRGL.columns.tolist()
            CRGL=pd.merge(CRGL,self.dataFrames['CONT'],left_on='rkPARENT',right_on='pk',suffixes=('','_CONT'))
            CRGL=CRGL.filter(items=colList+['NAME'])            
            CRGL.rename(columns={'NAME':'CONT_PARENT'},inplace=True)

            howMode='inner'
            vREdges=pd.merge(CRGL,vRNodes,left_on='fkKi',right_on='pk',suffixes=('','_Ki'),how=howMode)
            vREdges=vREdges[['fkKk','OBJTYPE','BESCHREIBUNG','Kn','CONT','CONT_PARENT','pk']]
            vREdges['KnExt']=vREdges['Kn']+'_'+vREdges['OBJTYPE'] 
            vREdges=vREdges.rename(columns={'OBJTYPE':'OBJTYPE_Ki','BESCHREIBUNG':'BESCHREIBUNG_Ki','Kn':'Kn_Ki','pk':'pk_Ki','KnExt':'KnExt_Ki'})
            vREdges=pd.merge(vREdges,vRNodes,left_on='fkKk',right_on='pk',suffixes=('','_Kk'),how=howMode)
            vREdges['KnExt']=vREdges['Kn']+'_'+vREdges['OBJTYPE'] 
            vREdges=vREdges.rename(columns={'OBJTYPE':'OBJTYPE_Kk','BESCHREIBUNG':'BESCHREIBUNG_Kk','Kn':'Kn_Kk','pk':'pk_Kk','KnExt':'KnExt_Kk'})
            vREdges=vREdges[['OBJTYPE_Ki','BESCHREIBUNG_Ki','Kn_Ki','pk_Ki','OBJTYPE_Kk','BESCHREIBUNG_Kk','Kn_Kk','pk_Kk','CONT','CONT_PARENT','KnExt_Ki','KnExt_Kk']]           

        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if isinstance(vREdges,pd.core.frame.DataFrame):
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal) 
                vREdges=pd.DataFrame()              
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return vREdges

    def _MxSyncAddMx(self,ForceNoH5ReadForMx=False):
        """Mx-Object corresponding to the Xm-Object is constructed and returned. 

            ForceNoH5ReadForMx (deafault: False)
                * ForceNoH5ReadForMx = True:
                    * the new Mx-Object is constructed with NoH5Read=True
                * ForceNoH5ReadForMx = False: 
                    * the new Mx-Object is constructed with NoH5Read = not self.h5Read 
                        * if the Xm was read from H5 the Mx is constructed with NoH5Read=False
                        * if the Xm was not read from H5 the Mx is constructed with NoH5Read=True
                       
        Returns:
            Mx-Object

        Raises:
            XmError

        """
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            (wDir,modelDir,modelName,mx1File)=self.getWDirModelDirModelName()   
            if not ForceNoH5ReadForMx:
                MxNoH5Read=not self.h5Read
            else:
                MxNoH5Read=True
            mx=Mx.Mx(mx1File=mx1File,NoH5Read=MxNoH5Read)

                                                       
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))             
            return mx

    def __Mx1_Sir3sIDUpd(self,mx,checkAllChannels=True,ForceNoH5Update=False):
        """Update NAME1,2 and Sir3sID in mx.mx1Df and mx.df.

        Args:
            mx: Mx-Object
            checkAllChannels: if False only Channels with empty NAME1 are updated; default: True: all Channels are checked and updated if necessary
            ForceNoH5Update: if False, H5 is updated if read from H5

        Notes:
            Das Update ist erforderlich,
            weil SIR 3S die hier aktualisierten Kanal-Attribute _nicht nachführt, 
            wenn diese sich im referenzierten Objekt geändert haben.
            Die Nachführung hier stellt sicher, dass der Sir3sID Kanalbezeichner, der sich aus Mx Kanal-Attributen ergibt
            dem Sir3sID Kanalbezeichner aus Xm Sachdaten-Attributen entspricht.   
            
            Unabhängig von der Nachführung: SirCalc:
            WARNUNG  MXX  Es gibt in der MX1-Datei ... Datenpunkte mit falschem DATATLENGTH-Attributwert
            WARNUNG  MXX  ... ungueltige oder unbekannte Datenpunkte erhalten das Ergebnis 0 oder Leerzeichen
            Das ist ein Hinweis auf Zombie-Kanäle, Kanäle deren Objekt nicht (mehr) existiert. 

            Diese Sachstände führen beim Nachführen zu ... Spalten mit demselben Namen (nan) in mx.df.
            Spalten mit demselben Namen sind generell in mehrfacher Hinsicht ungeeignet.
            Kommen sie vor, werden sie wie folgt umbenannt: Vorher: x,x,x,... Nachher: x,x_1,x_2, ... 

            The following OBJTYPEs are covered:
                * KNOT
                * WBLZ
                * RXXXX
                * alle Kanäle von Objekten die in vVBEL vorkommen

            mx.ToH5() is called if Sir3sID-Updates occured and mx.h5Read is True and not ForceNoH5Update. 

        Raises:
            XmError

        >>> xm=xms['LocalHeatingNetwork']
        >>> (wDir,modelDir,modelName,mx1File)=xm.getWDirModelDirModelName()          
        >>> try:
        ...     import Mx
        ... except:
        ...     from PT3S import Mx
        >>> mx=Mx.Mx(mx1File=mx1File)      
        >>> # mx.mx1Df
        >>> Sir3sIDStr='FWVB~V-K003~R-K003~5695730293103267172~INDUV'
        >>> Sir3sIDStr='FWVB~~~5695730293103267172~INDUV'
        >>> mx.mx1Df.loc[mx.mx1Df['Sir3sID']==Sir3sIDStr,'NAME1']='Sir3sIDUpdTest'
        >>> mx.mx1Df.loc[mx.mx1Df['Sir3sID']==Sir3sIDStr,'Sir3sID']='FWVB~Sir3sIDUpdTest~R-K003~5695730293103267172~INDUV'     
        >>> print(mx.mx1Df.loc[mx.mx1Df['NAME1']=='Sir3sIDUpdTest',['Sir3sID']].to_string(index=False))
                                                      Sir3sID
         FWVB~Sir3sIDUpdTest~R-K003~5695730293103267172~INDUV
        >>> xm._Xm__Mx1_Sir3sIDUpd(mx) 
        >>> print(mx.mx1Df.loc[mx.mx1Df['Sir3sID']=='FWVB~V-K003~R-K003~5695730293103267172~INDUV',['NAME1']].to_string(index=False))
          NAME1
         V-K003
        >>> # -------
        >>> # doppelte Spaltennamen behandeln
        >>> # -------        
        >>> mx.df.rename(columns={'PUMP~R-1~R2~5481331875203087055~ETAW':'Sir3sIDUpdTest'},inplace=True)
        >>> mx.df.rename(columns={'PUMP~R-1~R2~5481331875203087055~DP':'Sir3sIDUpdTest'},inplace=True)
        >>> list(mx.df.columns[mx.df.columns.duplicated()])
        ['Sir3sIDUpdTest']
        >>> mx.df.filter(regex='^Sir3sIDUpdTest').round(1).head(2)
                                   Sir3sIDUpdTest  Sir3sIDUpdTest
        2004-09-22 08:30:00+00:00             0.6             2.3
        2004-09-22 08:30:15+00:00             0.7             1.3
        >>> xm._Xm__Mx1_Sir3sIDUpd(mx) 
        >>> mx.df.filter(regex='^Sir3sIDUpdTest').round(1).head(2)
                                   Sir3sIDUpdTest  Sir3sIDUpdTest_1
        2004-09-22 08:30:00+00:00             0.6               2.3
        2004-09-22 08:30:15+00:00             0.7               1.3
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:
            # Sir3sID split
            df=mx.mx1Df['Sir3sID'].str.extract(Mx.reSir3sIDcompiled)               
            # Sir3sID reconstruction
            sep=Mx.reSir3sIDSep
            df=df.assign(Sir3sID=lambda df: df.OBJTYPE+sep+df.NAME1+sep+df.NAME2+sep+df.OBJTYPE_PK+sep+df.ATTRTYPE)

            nOfSir3sIDsUpdated=0
            
            # KNOT -----------------------------------
            dfUpd=df[(df['OBJTYPE'].isin(['KNOT']))]
            if not checkAllChannels:
                dfUpd=dfUpd[(dfUpd['NAME1'].str.len()==0)]
            nOfSir3sIDsUpdated=nOfSir3sIDsUpdated+self.__Mx1_Sir3sIDUpd_ObjTypeNode(mx=mx
                                                                 ,dfUpd=dfUpd                                                                                                                                 
                                                                 ,dfNAME1=self.dataFrames['KNOT']
                                                                 ,NAME1Col='NAME')
            # WBLZ ------------------------------------
            dfUpd=df[(df['OBJTYPE'].isin(['WBLZ']))]
            if not checkAllChannels:
                dfUpd=dfUpd[(dfUpd['NAME1'].str.len()==0)]
            if 'WBLZ' in self.dataFrames.keys():
                nOfSir3sIDsUpdated=nOfSir3sIDsUpdated+self.__Mx1_Sir3sIDUpd_ObjTypeNode(mx=mx
                                                                     ,dfUpd=dfUpd                                                                   
                                                                     ,dfNAME1=self.dataFrames['WBLZ']
                                                                     ,NAME1Col='NAME')
            # RXXXX -----------------------------
            for ObjType in ['RSLW','RMES','RFKT','RTOT','RVGL','RHYS','RINT','RPT1','RADD','RMUL','RDIV','RMIN','RPID','RVGL']:       
                if ObjType in self.dataFrames:
                    dfUpd=df[(df['OBJTYPE'].isin([ObjType]))]
                    if not checkAllChannels:
                        dfUpd=dfUpd[(dfUpd['NAME1'].str.len()==0)]
                    nOfSir3sIDsUpdated=nOfSir3sIDsUpdated+self.__Mx1_Sir3sIDUpd_ObjTypeNode(mx=mx
                                                                     ,dfUpd=dfUpd                                                                                                                                       
                                                                     ,dfNAME1=self.dataFrames[ObjType]
                                                                     ,NAME1Col='KA')
            
            # VBEL (NAME1,2 und Sir3sID) ---------------------------------------------
            dfUpd=df[(df['OBJTYPE'].isin(vVBEL_edges))]
            if not checkAllChannels:
                dfUpd=dfUpd[(dfUpd['NAME1'].str.len()==0)]

            # fuer Col-Auswahl nach Merge
            dfUpdCols=dfUpd.columns.tolist()
            dfUpdCols.append('NAME_i')
            dfUpdCols.append('NAME_k')

            # right (hat die zu mergenden Keys als Index)
            dfVBEL=self.dataFrames['vVBEL']
            
            #logger.debug("{0:s}dfUpd vor Merge: {1:s}.".format(logStr,str(dfUpd)))
            #logger.debug("{0:s}dfVBEL vor Merge: {1:s}.".format(logStr,str(dfVBEL)))
            #logger.debug("{0:s}dfVBEL index vor Merge: {1:s}.".format(logStr,str(dfVBEL.index)))

            dfUpd=pd.merge(
                dfUpd
               ,dfVBEL
               ,how='left' # expected: no NaNs/Nones in Merge-Result
               ,left_on=['OBJTYPE','OBJTYPE_PK'] # diese left Key-Spalten ... 
               ,right_index=True # ... matchen mit den right Indices 
               ,suffixes=('', '_y'))[dfUpdCols]

            #logger.debug("{0:s}dfUpd nach Merge: {1:s}.".format(logStr,str(dfUpd)))

            # calculate Sir3sID Update 
            dfUpd=dfUpd.assign(Sir3sIDUpd=lambda df: df.OBJTYPE+sep+df.NAME_i+sep+df.NAME_k+sep+df.OBJTYPE_PK+sep+df.ATTRTYPE)
            # iterate over all Sir3sIDs to be updated
            for index, row in dfUpd.iterrows():
                if row['Sir3sID'] != row['Sir3sIDUpd']: 
                    nOfSir3sIDsUpdated=nOfSir3sIDsUpdated+1
                    # set Sir3sID to Sir3sIDUpd in mx.mx1Df
                    mx.mx1Df.loc[lambda df: df.Sir3sID==row['Sir3sID'],'Sir3sID']=row['Sir3sIDUpd']
                    logger.debug("{0:s}Changing Sir3sID {1!s} to {2!s}.".format(logStr,row['Sir3sID'],row['Sir3sIDUpd']))    
                    # set NAME1 to NAME_i in mx.mx1Df
                    mx.mx1Df.loc[lambda df: df.Sir3sID==row['Sir3sIDUpd'],'NAME1']=row['NAME_i']
                    logger.debug("{0:s}Changing NAME1 (now:{1:s}) to {2!s}.".format(logStr,row['NAME1'],row['NAME_i']))    
                    # set NAME2 to NAME_k in mx.mx1Df
                    mx.mx1Df.loc[lambda df: df.Sir3sID==row['Sir3sIDUpd'],'NAME2']=row['NAME_k']
                    logger.debug("{0:s}Changing NAME2 (now:{1:s}) to {2!s}.".format(logStr,row['NAME2'],row['NAME_k']))    
                    if isinstance(mx.df,pd.core.frame.DataFrame):  
                        # rename the corresponding col in mx.df
                        mx.df.rename(columns={row['Sir3sID']:row['Sir3sIDUpd']},inplace=True)  
                        logger.debug("{0:s}Changing Col {1!s} to {2!s}.".format(logStr,row['Sir3sID'],row['Sir3sIDUpd']))
                else:
                    pass
                    #logger.debug("{0:s}Sir3sID {1!s:50s} == {2!s}.".format(logStr,row['Sir3sID'],row['Sir3sIDUpd']))            
                    #
            # doppelte Spaltennamen          
            l=list(mx.df.columns[mx.df.columns.duplicated()])
            if len(l) > 0:      
                logger.debug("{0:s}Spaltennamen X die mehrfach vorkommen (hier: {1!s}) werden in X,X_1,X_2, ... umbenannt.".format(logStr,l))
                mx.df.rename(columns=renamer(),inplace=True)  

            if nOfSir3sIDsUpdated>0 and mx.h5Read and not ForceNoH5Update:
                mx.ToH5()
                           
        except Exception as e:            
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e)) 
            logger.error(logStrFinal) 
                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

    def __Mx1_Sir3sIDUpd_ObjTypeNode(self,mx=None,dfUpd=None,dfNAME1=None,NAME1Col='NAME'):
        """Update Sir3sID and NAME1 in mx.mx1Df and mx.df for Channels in dfUpd.

        Args:
            mx: Mx-Object
            dfUpd: df with OBJTYPE,NAME1,NAME2,OBJTYPE_PK,ATTRTYPE,Sir3sID to be updated
            dfNAME1: df with NAME1-Information
            NAME1Col: col in dfNAME1 with NAME1-Information

        Returns:
            nOfSir3sIDsUpdated

        Note:
            only wrong Channels are updated

        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:
            nOfSir3sIDsUpdated=0

            dfUpdCols=dfUpd.columns.tolist()
            dfUpdCols.append(NAME1Col)
            dfUpd=pd.merge(
                dfUpd
               ,dfNAME1
               ,how='inner'
               ,left_on='OBJTYPE_PK'
               ,right_on='pk'
               ,suffixes=('', '_y'))[dfUpdCols]
            dfUpd.rename(columns={NAME1Col:'NAME1Col'},inplace=True)
            # calculate Sir3sID Update 
            sep=Mx.reSir3sIDSep
            dfUpd=dfUpd.assign(Sir3sIDUpd=lambda df: df.OBJTYPE+sep+df.NAME1Col+sep+df.NAME2+sep+df.OBJTYPE_PK+sep+df.ATTRTYPE)

            # iterate over all Sir3sIDs to be updated
            for index, row in dfUpd.iterrows():
                if row['Sir3sID'] != row['Sir3sIDUpd']: 
                    nOfSir3sIDsUpdated=nOfSir3sIDsUpdated+1
                    # set Sir3sID to Sir3sIDUpd in mx.mx1Df
                    mx.mx1Df.loc[lambda df: df.Sir3sID==row['Sir3sID'],'Sir3sID']=row['Sir3sIDUpd']
                    logger.debug("{0:s}Changing Sir3sID {1:s} to {2:s}.".format(logStr,row['Sir3sID'],row['Sir3sIDUpd']))    
                    # set NAME1 to NAME1Col in mx.mx1Df
                    mx.mx1Df.loc[lambda df: df.Sir3sID==row['Sir3sIDUpd'],'NAME1']=row['NAME1Col']
                    logger.debug("{0:s}Changing NAME1 (now:{1:s}) to {2:s}.".format(logStr,row['NAME1'],row['NAME1Col']))    
                    if isinstance(mx.df,pd.core.frame.DataFrame):  
                        # rename the corresponding col in mx.df
                        mx.df.rename(columns={row['Sir3sID']:row['Sir3sIDUpd']},inplace=True)  
                        logger.debug("{0:s}Changing Col {1:s} to {2:s}.".format(logStr,row['Sir3sID'],row['Sir3sIDUpd']))
                           
        except Exception as e:            
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e)) 
            logger.error(logStrFinal) 
                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            return nOfSir3sIDsUpdated

    def __Mx1_vNRCV(self,mx):
        """vNRCV_Mx1 (vNRCV with Mx1-Information) is added to dataFrames.

        Args:
            mx: Mx-Object

        self.dataFrames['vNRCV_Mx1']
                index
                    * reindex
                FILTERed
                    * existing MX-Channels only
                    * cRefLfdNr: 1st references only 
                SORTed
                    * Sir3sID 
                columns NEW
                    * Sir3sID
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             

            vNRCV=self.dataFrames['vNRCV']
            vNRCV_Mx1=pd.DataFrame()   

            if 'fkOBJTYPE' in vNRCV.columns.tolist():

                vNRCV_Mx1=vNRCV.merge(mx.mx1Df,left_on='fkOBJTYPE',right_on='OBJTYPE_PK',suffixes=['_NR','_MX1'])

                vNRCV_Mx1=vNRCV_Mx1[(vNRCV_Mx1['cRefLfdNr']==1)
                        &
                        (vNRCV_Mx1['OBJTYPE_NR']==vNRCV_Mx1['OBJTYPE_MX1'])
                        &
                        (vNRCV_Mx1['ATTRTYPE_NR']==vNRCV_Mx1['ATTRTYPE_MX1'])
                        ]

                # reindex:
                vNRCV_Mx1=pd.DataFrame(vNRCV_Mx1.values,columns=vNRCV_Mx1.columns)
            
                vNRCV_Mx1=vNRCV_Mx1[[  'Sir3sID'
                    ,'cRefLfdNr' 
                    # CONT
                    ,'CONT'
                    ,'CONT_ID'
                    ,'CONT_LFDNR'
                    # DPGR
                    ,'DPGR'
                    # Data (of the DPGR_ROW)
                    ,'OBJTYPE_NR'
                    ,'fkOBJTYPE'
                    ,'ATTRTYPE_NR'
                    # IDs (of the DPGR_ROW)
                    ,'pk_ROWS'
                    ,'tk_ROWS'       
                    # IDs (of the NRCV)
                    ,'pk'
                    ,'tk'
                    ,'pXYLB'
                ]]

                vNRCV_Mx1.rename(columns={'OBJTYPE_NR':'OBJTYPE','ATTRTYPE_NR':'ATTRTYPE'},inplace=True)  

                vNRCV_Mx1.sort_values(['Sir3sID'],ascending=True,inplace=True)
                #reindex:
                vNRCV_Mx1=pd.DataFrame(vNRCV_Mx1.values,columns=vNRCV_Mx1.columns)
                                            
        except Exception as e:            
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            if not vNRCV.empty and not vNRCV_Mx1.empty:
                logger.error(logStrFinal) 
            else:
                logger.debug(logStrFinal)                            
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            self.dataFrames['vNRCV_Mx1']=vNRCV_Mx1

    def __Mx2_vROHR(self,mx):
        """Mx2-Information into vROHR.
        
        Args:
            mx: Mx-Object

        self.dataFrames['vROHR']
                columns NEW
                    * mx2NoPts
                    * mx2Idx
                   
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            xksROHRMx=mx.mx2Df[
            (mx.mx2Df['ObjType'].str.match('ROHR'))
            &
            ~(mx.mx2Df['AttrType'].str.contains('N_OF_POINTS'))
            ]['Data'].iloc[0] # Liste der IDs in Mx2

            xkTypeMx=mx.mx2Df[
            (mx.mx2Df['ObjType'].str.match('ROHR'))
            &
            ~(mx.mx2Df['AttrType'].str.contains('N_OF_POINTS'))
            ]['AttrType'].iloc[0]

            vROHR=self.dataFrames['vROHR']
            xksROHRXm=vROHR[xkTypeMx.strip()] # Liste der IDs in vROHR

            mxXkRohrIdx=[xksROHRMx.index(xk) for xk in xksROHRXm] # zugeh. Liste der mx2Idx in vROHR

            ##vROHR['mx2Idx']=pd.Series(mxXkRohrIdx)
            
            nOfPtsROHRMx=mx.mx2Df[
            (mx.mx2Df['ObjType'].str.match('ROHR'))
            &
            (mx.mx2Df['AttrType'].str.contains('N_OF_POINTS'))
            ]['Data'].iloc[0]  # Liste der NOfPts in Mx2

            nOfPtsROHRMxXk=[nOfPtsROHRMx[mx2Idx] for mx2Idx in mxXkRohrIdx] # zugeh. Liste der NOfPts in vROHR

            
            vROHR['mx2NofPts']=pd.Series(nOfPtsROHRMxXk)#nOfPtsROHRMx)
            vROHR['mx2Idx']=pd.Series(mxXkRohrIdx) # Abschluss mit mx2Idx
            ##
            ####vROHR['mx2Idx']=pd.Series(mxXkRohrIdx)
                                                                   
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.error(logStrFinal) 
                          
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))      
            self.dataFrames['vROHR']=vROHR     

    def __Mx2_vFWVB(self,mx):
        """Mx2-Information into vFWVB.
        
        Args:
            mx: Mx-Object

        self.dataFrames['vFWVB']
                columns NEW
                    * mx2Idx
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            vFWVB=self.dataFrames['vFWVB']

            xksFWVBMx=mx.mx2Df[
            (mx.mx2Df['ObjType'].str.match('FWVB'))
            ]['Data'].iloc[0]

            xkTypeMx=mx.mx2Df[
            (mx.mx2Df['ObjType'].str.match('FWVB'))
            ]['AttrType'].iloc[0]

            xksFWVBXm=vFWVB[xkTypeMx.strip()]
            mxXkFwvbIdx=[xksFWVBMx.index(xk) for xk in xksFWVBXm]

            vFWVB['mx2Idx']=pd.Series(mxXkFwvbIdx)
                                                                               
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.debug(logStrFinal) 
                          
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))      
            self.dataFrames['vFWVB']=vFWVB     
            
    def __Mx2_vKNOT(self,mx):
        """Mx2-Information into vKNOT.
        
        Args:
            mx: Mx-Object

        self.dataFrames['vKNOT']
                columns NEW
                    * mx2Idx
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            xksKNOTMx=mx.mx2Df[(mx.mx2Df['ObjType'].str.match('KNOT'))]['Data'].iloc[0]
            xkTypeMx=mx.mx2Df[(mx.mx2Df['ObjType'].str.match('KNOT'))]['AttrType'].iloc[0]
            vKNOT=self.dataFrames['vKNOT']
            xksKNOTXm=vKNOT[xkTypeMx.strip()]
            mxXkKNOTIdx=[xksKNOTMx.index(xk) for xk in xksKNOTXm]
            vKNOT['mx2Idx']=pd.Series(mxXkKNOTIdx)
                                                  
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.error(logStrFinal) 
                          
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))      
            self.dataFrames['vKNOT']=vKNOT     

    def __Mx2_vVBEL(self,mx,edges=vVBEL_edges):
        """Mx2-Information into vVBEL.
        
        Args:
            mx: Mx-Object

        self.dataFrames['vVBEL']:
                columns NEW
                    * mx2Idx                   

                    * Notes:                        
                        * for all edges mx2Idx is taken from mx.mx2Df
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 

            # new col mx2Idx in dfVBEL
            dfVBEL=self.dataFrames['vVBEL']
            dfVBEL=dfVBEL.assign(mx2Idx=lambda x: -1)
            dfVBEL['mx2Idx'].astype('int64',copy=False)

            # all edges
            for edge in [edge for edge in edges]:
                 try:                     
                     xksEDGEMx=mx.mx2Df[
                                (mx.mx2Df['ObjType'].str.match(edge))
                         ]['Data'].iloc[0]

                     xkTypeMx=mx.mx2Df[
                                (mx.mx2Df['ObjType'].str.match(edge))
                         ]['AttrType'].iloc[0]

                     if xkTypeMx == 'tk':
                        xksEDGEXm=dfVBEL.loc[(edge,),xkTypeMx]
                     else:
                        # pk
                        xksEDGEXm=dfVBEL.loc[(edge,),:].index

                     logger.debug("{0:s}{1:s}: xkTypeMx: {2:s}".format(logStr,edge,xkTypeMx))   
                     logger.debug("{0:s}{1:s}: xksEDGEXm: {2:s}".format(logStr,edge,str(xksEDGEXm.values.tolist())))   
                     logger.debug("{0:s}{1:s}: xksEDGEMx: {2:s}".format(logStr,edge,str(xksEDGEMx)))      
                                      
                     mxXkEDGEIdx=[xksEDGEMx.index(tk) for tk in xksEDGEXm]
                     
                     dfVBEL.loc[(edge,),'mx2Idx']=mxXkEDGEIdx

                 except Exception as e:
                    logStrEdge="{:s}Exception: Line: {:d}: {!s:s}: {:s}: mx2Idx for {:s} failed. mx2Idx = -1.".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e),edge)            
                    logger.debug(logStrEdge) 
                                                                                                               
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))            
            logger.error(logStrFinal) 
                          
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))    
            self.dataFrames['vVBEL']=dfVBEL

    def MxAdd(self
              # same Args as MxSync:
              ,mx=None
              ,ForceNoH5ReadForMx=False
              ,ForceNoH5Update=False
              # Args special to MxAdd              
              ,timeReq=None
              ,aggReq=None
              ,timeReq2nd=None
              ,viewList=[]):
        """Add MX-Resultcolumn-Set to some Xm-Views. A Result-Set from previous Calls is deleted. NEW 1st Call: vROHRVecResults, vAGSN.

        Args:               
            * mx, ForceNoH5ReadForMx, ForceNoH5Update : same Args as for MxSync; see description there
            * timeReq:
                * TIMESTAMP (defining the MX-Resultcolumn-Set) 
                * if None 1st TIME in Mx is used      
                * if aggReq considered as TIMESTAMPL
            * aggReq (defining the MX-Resultcolumn-Set):               
                * 'TIME','TMIN','TMAX' (source: MXS) or 'MIN','MAX', ... (source: mx.getVecAggs())
                * if not None, timeReq und timeReq2nd define the timespan
                * if List
                    * MX-Resultcolumns for several times/timespans are calculated 
                    * timeReq and timeReq2nd must also be Lists
                    * if viewList is not None, in the views in viewList several MX-Resultcolumn-Sets are added: one per requested time/timespan
                    * the 2nd Resultcol of the same type is named _1, the 3rd _2, ...                    
            * timeReq2nd (defining the MX-Resultcolumn-Set):
                * TIMESTAMP 
                * if None last TIME in Mx is used    
                * if aggReq considered as TIMESTAMPR (ignored if aggReq = TIME)

        viewList: Views with MX-Resultcolumn-Set to be added:            
            * in the Xm-Views below col mx2Idx must exist (i.e. MxSync mus have been called)
            * mx2Idx is considered to be the last of the Model-cols
            * right from mx2Idx all available Result-cols are added if not already existing
            * already existing Result-cols are overwritten
            * mx2Idx-Views:
                * vKNOT (KNOT...) 
                * vROHR (ROHR...) - only Non-VEC-Channel-Results are added
                * vFWVB (FWVB...)
                * vVBEL (KNOT..._i and KNOT..._k and Q)

            * NEW 1st Call:

                * vROHRVecResults: VEC-Channel-Results for Pipe-Interior-Pts (IPts):
                    * pk
                    * mx2Idx
                    * IptIdx: S,0,...,E - Interior Point Index; S=Start EdgeDefNode, E=End EdgeDefNode, 0=1st Ipt in EdgeDefDirection
                    * one column per VEC-Channel

                * vAGSN
                    * from vVBEL: KNOT..._i and KNOT..._k and Q
                    * from vROHRVecResults: vecResults
                    * Topology:
                        * nextNODE                   
                        * IptIdx                    
                    * Geometry:
                        * dx                       
                        * x                        
                        * xVbel      
                        * Z (the corresponding Z_i, Z_k and ZVEC are droped)
                    * Results:
                        * Q: from Q before and QMVEC for PIPEs; in Schnittrichtung; QMVEC is droped
                        * for available KNOT...#_i, KNOT...#_k and ...#VEC:
                            * i.e. KNOT~*~*~*~P_i KNOT~*~*~*~P_k  ROHR~*~*~*~PVEC
                            * P is new column
                            * the correspondig 3 columns are droped

        Returns:
            Mx-Object if no Mx-Object was given; Nothing else

        Raises:
            XmError      
                                  
        >>> # -q -m 0 -t before -s Xm.MxAdd -y yes -z yes -w LocalHeatingNetwork -w GPipes
        >>> import pandas as pd
        >>> pd.set_option('display.max_columns',None)
        >>> pd.set_option('display.max_rows',None)
        >>> pd.set_option('display.max_colwidth',666666)   
        >>> pd.set_option('display.width',666666666)
        >>> xm=xms['LocalHeatingNetwork']
        >>> (wDir,modelDir,modelName,mx1File)=xm.getWDirModelDirModelName()
        >>> try:
        ...     import Mx
        ... except:
        ...     from PT3S import Mx        
        >>> mx=Mx.Mx(mx1File=mx1File)           
        >>> mx.dfVecAggs.loc[(['TIME','TMIN','TMAX'],'KNOT~*~*~*~PH',slice(None),slice(None)),0:3].round(1).reset_index()  
           TYPE        Sir3sID          TIMESTAMPL          TIMESTAMPR    0    1    2    3
        0  TIME  KNOT~*~*~*~PH 2004-09-22 08:30:00 2004-09-22 08:30:00  2.3  4.0  4.1  4.1
        1  TMIN  KNOT~*~*~*~PH 2004-09-22 08:30:00 2004-09-22 08:31:00  2.1  2.2  2.2  2.2
        2  TMAX  KNOT~*~*~*~PH 2004-09-22 08:30:00 2004-09-22 08:31:00  2.3  4.0  4.1  4.1
        >>> print(xm._getvXXXXAsOneString(vXXXX='vKNOT',filterColList=['BESCHREIBUNG','IDREFERENZ','NAME','KNOT~*~*~*~PH'],roundDct={'KNOT~*~*~*~PH':1}))
                              BESCHREIBUNG IDREFERENZ         NAME  KNOT~*~*~*~PH
        0                             None         -1       R-K004            2.3
        1                             None         -1       V-K002            4.0
        2                             None         -1       V-K001            4.1
        3                             None         -1       V-K000            4.1
        4                             None         -1       R-K001            2.0
        5                             None         -1       R-K003            2.3
        6                             None         -1       R-K000            2.0
        7                             None         -1       R-K005            2.3
        8                             None         -1          R-L            2.0
        9                             None         -1       R-K002            2.1
        10                            None         -1       V-K004            3.8
        11                            None         -1       V-K005            3.8
        12                            None         -1       R-K007            2.3
        13                            None         -1       V-K006            3.8
        14                            None         -1       R-K006            2.3
        15                            None         -1       V-K003            3.8
        16                            None         -1          V-L            4.1
        17                            None         -1       V-K007            3.8
        18                            None         -1           R2            4.3
        19                            None         -1          V-1            4.1
        20                            None         -1           R3            4.3
        21  Druckhaltung - 2 bar Ruhedruck         -1  PKON-Knoten            2.0
        22          Anbindung Druckhaltung         -1          R-1            2.0
        >>> print(xm._getvXXXXAsOneString(vXXXX='vROHR',filterColList=['BESCHREIBUNG','IDREFERENZ','NAME_i','NAME_k','ROHR~*~*~*~QMAV'],roundDct={'ROHR~*~*~*~QMAV':1}))
           BESCHREIBUNG IDREFERENZ  NAME_i  NAME_k  ROHR~*~*~*~QMAV
        0          None         -1  R-K004  R-K005             -8.5
        1          None         -1  V-K002  V-K003             19.1
        2          None         -1  R-K003  R-K004            -15.4
        3          None         -1  V-K004  V-K005              8.5
        4          None         -1  V-K001  V-K002             23.0
        5          None         -1  R-K006  R-K007             -3.9
        6          None         -1  V-K000  V-K001             23.0
        7          None         -1  V-K003  V-K004             15.4
        8          None         -1  V-K005  V-K006              3.9
        9          None         -1  R-K001  R-K002            -23.0
        10         None         -1  R-K002  R-K003            -19.1
        11         None         -1  R-K005  R-K006             -3.9
        12         None         -1  V-K006  V-K007              3.9
        13         None         -1  R-K000  R-K001            -23.0
        14         None         -1     R-L  R-K000            -23.0
        15         None         -1     V-L  V-K000             23.0
        >>> print(xm._getvXXXXAsOneString(vXXXX='vFWVB'))
          BESCHREIBUNG IDREFERENZ   W0  LFK  W0LFK  TVL0  TRS0  LFKT      W  W_min  W_max  INDTR  TRSK  VTYP  DPHAUS  IMBG  IRFV                   pk                   tk  NAME_i KVR_i TM_i   XKOR_i   YKOR_i ZKOR_i  pXCor_i  pYCor_i  NAME_k KVR_k TM_k   XKOR_k   YKOR_k ZKOR_k  pXCor_k  pYCor_k                                      CONT CONT_ID CONT_LFDNR                         WBLZ  mx2Idx  FWVB~*~*~*~W  FWVB~*~*~*~QM  FWVB~*~*~*~IAKTIV
        0            1         -1  200  0.8  160.0    90    50  LFKT  160.0  160.0  160.0      1    55    14     0.7     0   0.0  4643800032883366034  4643800032883366034  V-K002     1   90  2541059  5706265     20    319.0     56.0  R-K002     2   60  2541059  5706265     20    319.0     56.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  [BLNZ1, BLNZ1u5, BLNZ1u5u7]       0         160.0       3.928166                0.0
        1            3         -1  200  1.0  200.0    90    65  LFKT  200.0  200.0  200.0      1    65    14     0.7     0   0.0  4704603947372595298  4704603947372595298  V-K004     1   90  2541539  5706361     20    799.0    152.0  R-K004     2   60  2541539  5706361     20    799.0    152.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                           []       1         200.0       6.869426                0.0
        2            4         -1  200  0.8  160.0    90    60  LFKT  160.0  160.0  160.0      1    60    14     0.7     0   0.0  5121101823283893406  5121101823283893406  V-K005     1   90  2541627  5706363     20    887.0    154.0  R-K005     2   60  2541627  5706363     20    887.0    154.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1  [BLNZ1u5, BLNZ1u5u7, BLNZ5]       2         160.0       4.581308                0.0
        3            5         -1  200  0.8  160.0    90    55  LFKT  160.0  160.0  160.0      1    55    14     0.7     0   0.0  5400405917816384862  5400405917816384862  V-K007     1   90  2541899  5706325     20   1159.0    116.0  R-K007     2   60  2541899  5706325     20   1159.0    116.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                  [BLNZ1u5u7]       3         160.0       3.928166                0.0
        4            2         -1  200  0.6  120.0    90    60  LFKT  120.0  120.0  120.0      1    62    14     0.7     0   0.0  5695730293103267172  5695730293103267172  V-K003     1   90  2541457  5706345     20    717.0    136.0  R-K003     2   60  2541457  5706345     20    717.0    136.0  Nahwärmenetz mit 1000 kW Anschlussleistu    1001         -1                           []       4         120.0       3.680879                0.0
        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['BESCHREIBUNG','IDREFERENZ','NAME_i','NAME_k','Q'])) 
                                                      BESCHREIBUNG IDREFERENZ       NAME_i  NAME_k            Q
        OBJTYPE OBJID                                                                                          
        FWES    5638756766880678918  BHKW - Modul - 1000 kW therm.         -1           R3     V-1      22.9879
        FWVB    4643800032883366034                              1         -1       V-K002  R-K002      3.92817
                4704603947372595298                              3         -1       V-K004  R-K004      6.86943
                5121101823283893406                              4         -1       V-K005  R-K005      4.58131
                5400405917816384862                              5         -1       V-K007  R-K007      3.92817
                5695730293103267172                              2         -1       V-K003  R-K003      3.68088
        KLAP    4801110583764519435                           None         -1           R2      R3      22.9879
        PGRP    4986517622672493603                   Pumpengruppe         -1          R-1      R3         None
        PUMP    5481331875203087055                    Umwälzpumpe         -1          R-1      R2      22.9879
        ROHR    4613782368750024999                           None         -1       R-K004  R-K005     -8.50947
                4614949065966596185                           None         -1       V-K002  V-K003      19.0598
                4637102239750163477                           None         -1       R-K003  R-K004     -15.3789
                4713733238627697042                           None         -1       V-K004  V-K005      8.50948
                4769996343148550485                           None         -1          R-L  R-K000     -22.9879
                4789218195240364437                           None         -1       V-K001  V-K002      22.9879
                4939422678063487923                           None         -1          V-L  V-K000      22.9879
                4945727430885351042                           None         -1       R-K006  R-K007     -3.92817
                4984202422877610920                           None         -1       V-K000  V-K001      22.9879
                5037777106796980248                           None         -1       V-K003  V-K004      15.3789
                5123819811204259837                           None         -1       V-K005  V-K006      3.92817
                5266224553324203132                           None         -1       R-K001  R-K002     -22.9879
                5379365049009065623                           None         -1       R-K002  R-K003     -19.0598
                5611703699850694889                           None         -1       R-K005  R-K006     -3.92817
                5620197984230756681                           None         -1       V-K006  V-K007      3.92817
                5647213228462830353                           None         -1       R-K000  R-K001     -22.9879
        VENT    4678923650983295610                           None         -1          V-1     V-L      22.9879
                4897018421024717974                           None         -1          R-L     R-1      22.9879
                5525310316015533093                           None         -1  PKON-Knoten     R-1  2.19997e-06
        >>> print(xm._getvXXXXAsOneString(vXXXX='vROHRVecResults'
        ...     ,filterColList=['pk','mx2Idx','IptIdx','ROHR~*~*~*~RHOVEC','ROHR~*~*~*~TVEC','ROHR~*~*~*~MVEC','ROHR~*~*~*~SVEC','ROHR~*~*~*~PVEC','ROHR~*~*~*~ZVEC']
        ...     ,roundDct={'ROHR~*~*~*~RHOVEC':2,'ROHR~*~*~*~TVEC':1,'ROHR~*~*~*~MVEC':1,'ROHR~*~*~*~SVEC':2,'ROHR~*~*~*~PVEC':1,'ROHR~*~*~*~ZVEC':1}
        ...     ))
                             pk  mx2Idx IptIdx  ROHR~*~*~*~RHOVEC  ROHR~*~*~*~TVEC  ROHR~*~*~*~MVEC  ROHR~*~*~*~SVEC  ROHR~*~*~*~PVEC  ROHR~*~*~*~ZVEC
        0   4613782368750024999       0      S              983.7             60.0             -2.4             0.00              3.3             20.0
        1   4613782368750024999       0      E              983.7             60.0             -2.4            88.02              3.3             20.0
        2   4614949065966596185       1      S              965.7             90.0              5.3             0.00              5.0             20.0
        3   4614949065966596185       1      E              965.7             90.0              5.3           405.96              4.8             20.0
        4   4637102239750163477       2      S              983.7             60.0             -4.3             0.00              3.3             20.0
        5   4637102239750163477       2      E              983.7             60.0             -4.3            83.55              3.3             20.0
        6   4713733238627697042       3      S              965.7             90.0              2.4             0.00              4.8             20.0
        7   4713733238627697042       3      E              965.7             90.0              2.4            88.02              4.8             20.0
        8   4789218195240364437       5      S              965.7             90.0              6.4             0.00              5.1             20.0
        9   4789218195240364437       5      E              965.7             90.0              6.4           195.53              5.0             20.0
        10  4945727430885351042       7      S              983.7             60.0             -1.1             0.00              3.3             20.0
        11  4945727430885351042       7      E              983.7             60.0             -1.1           109.77              3.3             20.0
        12  4984202422877610920       8      S              965.7             90.0              6.4             0.00              5.1             20.0
        13  4984202422877610920       8      E              965.7             90.0              6.4            76.40              5.1             20.0
        14  5037777106796980248       9      S              965.7             90.0              4.3             0.00              4.8             20.0
        15  5037777106796980248       9      E              965.7             90.0              4.3            83.55              4.8             20.0
        16  5123819811204259837      10      S              965.7             90.0              1.1             0.00              4.8             20.0
        17  5123819811204259837      10      E              965.7             90.0              1.1           164.91              4.8             20.0
        18  5266224553324203132      11      S              983.7             60.0             -6.4             0.00              3.0             20.0
        19  5266224553324203132      11      E              983.7             60.0             -6.4           195.53              3.1             20.0
        20  5379365049009065623      12      S              983.7             60.0             -5.3             0.00              3.1             20.0
        21  5379365049009065623      12      E              983.7             60.0             -5.3           405.96              3.3             20.0
        22  5611703699850694889      13      S              983.7             60.0             -1.1             0.00              3.3             20.0
        23  5611703699850694889      13      E              983.7             60.0             -1.1           164.91              3.3             20.0
        24  5620197984230756681      14      S              965.7             90.0              1.1             0.00              4.8             20.0
        25  5620197984230756681      14      E              965.7             90.0              1.1           109.77              4.8             20.0
        26  5647213228462830353      15      S              983.7             60.0             -6.4             0.00              3.0             20.0
        27  5647213228462830353      15      E              983.7             60.0             -6.4            76.40              3.0             20.0
        28  4769996343148550485       4      S              983.7             60.0             -6.4             0.00              3.0             20.0
        29  4769996343148550485       4      E              983.7             60.0             -6.4            73.42              3.0             20.0
        30  4939422678063487923       6      S              965.7             90.0              6.4             0.00              5.1             20.0
        31  4939422678063487923       6      E              965.7             90.0              6.4            68.60              5.1             20.0
        >>> mx.dfVecAggs.shape # unverändert a
        (123, 32)
        >>> xm.MxAdd(mx=mx,aggReq='TMAX',ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape # unverändert b
        (123, 32)
        >>> dfTMax=xm.dataFrames['vROHRVecResults'].copy()        
        >>> xm.MxAdd(mx=mx,aggReq='TMIN',ForceNoH5Update=True)        
        >>> mx.dfVecAggs.shape # unverändert c
        (123, 32)
        >>> dfTMin=xm.dataFrames['vROHRVecResults'].copy() 
        >>> xm.MxAdd(mx=mx,aggReq='MAX',ForceNoH5Update=True) # erzeugt MIN/MAX/DIF
        >>> mx.dfVecAggs.shape # doppelt a
        (246, 32)
        >>> dfMax=xm.dataFrames['vROHRVecResults'].copy()
        >>> xm.MxAdd(mx=mx,aggReq='MIN',ForceNoH5Update=True) # ueberfluessig
        >>> mx.dfVecAggs.shape # doppelt b
        (246, 32)
        >>> dfMin=xm.dataFrames['vROHRVecResults'].copy()
        >>> import pandas as pd
        >>> decimals=pd.Series([6],index=['ROHR~*~*~*~PVEC'])        
        >>> dfTMax.round(decimals=decimals).equals(dfMax.round(decimals=decimals))
        True
        >>> dfTMin.round(decimals=decimals).equals(dfMin.round(decimals=decimals))
        True
        >>> # ----- einzelne Zeiten
        >>> r,c=mx.dfVecAggs.shape
        >>> xm.MxAdd(mx=mx,aggReq='TIME',ForceNoH5Update=True)
        >>> rn,cn=mx.dfVecAggs.shape
        >>> (rn,cn)==(r,c)
        True
        >>> xm.MxAdd(mx=mx,aggReq='TIME',timeReq=mx.df.index[3],ForceNoH5Update=True)
        >>> rn,cn=mx.dfVecAggs.shape
        >>> (r,c)
        (246, 32)
        >>> (rn,cn) # 41 neue Einträge = 123/3
        (287, 32)
        >>> xm.MxAdd(mx=mx,aggReq='TIME',timeReq=mx.df.index[3],ForceNoH5Update=True)
        >>> (rn,cn)==mx.dfVecAggs.shape
        True
        >>> mx=xm.MxAdd(ForceNoH5Update=True)           
        >>> mx.dfVecAggs.shape # h5-Inhalt unver#ndert 1
        (123, 32)
        >>> # --- mehrere Zeiten/Aggs
        >>> wDir,modelDir,modelName,mx1Filename = xm.getWDirModelDirModelName()
        >>> try:
        ...     import Mx
        ... except:
        ...     from PT3S import Mx
        >>> mx = None
        >>> mx=Mx.Mx(mx1File=mx1Filename)           
        >>> mx.dfVecAggs.shape # h5-Inhalt unver#ndert 2
        (123, 32)
        >>> xm.MxAdd(mx=mx,aggReq=['TIME','TMIN','TMAX'],timeReq=[mx.df.index[0],mx.df.index[0],mx.df.index[0]],timeReq2nd=[mx.df.index[0],mx.df.index[-1],mx.df.index[-1]],ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape 
        (123, 32)
        >>> xm.MxAdd(mx=mx,aggReq=['TIME','MIN'],timeReq=[mx.df.index[3],mx.df.index[0]],timeReq2nd=[mx.df.index[3],mx.df.index[-3]],ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape 
        (287, 32)
        >>> xm=xms['LocalHeatingNetwork']
        >>> mx=xm.MxAdd(ForceNoH5Update=True)           
        >>> mx.dfVecAggs.shape
        (123, 32)
        >>> # mx.dfVecAggs.loc[(slice(None),['KNOT~*~*~*~P','ROHR~*~*~*~QMI','ROHR~*~*~*~PVECMIN_INST'],slice(None),slice(None)),[0,1,2,31]].round(2)        
        >>> vAGSN=xm.dataFrames['vAGSN']
        >>> vAGSN.shape   
        (32, 55)
        >>> xm.MxAdd(mx=mx,aggReq=['TIME','TMIN','TMAX'],timeReq=3*[mx.df.index[0]],timeReq2nd=3*[mx.df.index[-1]],viewList=['vAGSN'],ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape 
        (123, 32)
        >>> vAGSN=xm.dataFrames['vAGSN']
        >>> vAGSN.shape   
        (32, 111)
        >>> # vAGSN.filter(regex='([\w ]+)(_)(\d+)$').columns  
        >>> xm.dataFrames['vAGSNTmp']=vAGSN.round(2)
        >>> print(xm._getvXXXXAsOneString(vXXXX='vAGSNTmp',filterColList=['P','P_1','P_2'],roundDct={'P':1,'P_1':1,'P_2':1})) 
              P  P_1  P_2
        0   5.1  3.2  5.1
        1   5.1  3.2  5.1
        2   5.1  3.2  5.1
        3   5.1  3.2  5.1
        4   5.1  3.2  5.1
        5   5.0  3.2  5.0
        6   5.0  3.2  5.0
        7   4.8  3.2  4.8
        8   4.8  3.2  4.8
        9   4.8  3.2  4.8
        10  4.8  3.2  4.8
        11  4.8  3.2  4.8
        12  4.8  3.2  4.8
        13  4.8  3.2  4.8
        14  4.8  3.2  4.8
        15  4.8  3.2  4.8
        16  3.0  3.0  3.0
        17  3.0  3.0  3.0
        18  3.0  3.0  3.0
        19  3.0  3.0  3.0
        20  3.0  3.0  3.0
        21  3.1  3.0  3.1
        22  3.1  3.0  3.1
        23  3.3  3.0  3.3
        24  3.3  3.0  3.3
        25  3.3  3.0  3.3
        26  3.3  3.0  3.3
        27  3.3  3.0  3.3
        28  3.3  3.0  3.3
        29  3.3  3.0  3.3
        30  3.3  3.0  3.3
        31  3.3  3.0  3.3
        >>> mx.dfVecAggs.shape 
        (123, 32)
        >>> xm.MxAdd(mx=mx,aggReq=['MIN'],timeReq=1*[mx.df.index[1]],timeReq2nd=1*[mx.df.index[-2]],viewList=['vAGSN'],ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape 
        (246, 32)
        >>> xm.MxAdd(mx=mx,aggReq=['MAX'],timeReq=1*[mx.df.index[0]],timeReq2nd=1*[mx.df.index[1]],viewList=['vAGSN','vKNOT','vFWVB','vROHR'],ForceNoH5Update=True)
        >>> mx.dfVecAggs.shape 
        (369, 32)
        >>> #mx.dfVecAggs.loc[(slice(None),['KNOT~*~*~*~P','ROHR~*~*~*~QMI','ROHR~*~*~*~PVECMIN_INST'],slice(None),slice(None)),[0,1,2,31]].round(2)      
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=['TIME']
        ... ,timeReq=1*[mx.df.index[0]]
        ... ,timeReq2nd=[None]
        ... ,viewList=['vAGSN']
        ... ,ForceNoH5Update=True)  
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=['TIME']
        ... ,timeReq=1*[mx.df.index[0]]
        ... ,timeReq2nd=[None]
        ... ,viewList=['vKNOT']
        ... ,ForceNoH5Update=True)      
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=['TIME']
        ... ,timeReq=1*[mx.df.index[0]]
        ... ,timeReq2nd=[None]
        ... ,viewList=['vROHR']   
        ... ,ForceNoH5Update=True)          
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=['TIME']
        ... ,timeReq=1*[mx.df.index[0]]
        ... ,timeReq2nd=[None]
        ... ,viewList=['vFWVB']
        ... ,ForceNoH5Update=True)          
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=['TIME']
        ... ,timeReq=1*[mx.df.index[0]]
        ... ,timeReq2nd=[None]
        ... ,viewList=['vVBEL']
        ... ,ForceNoH5Update=True)
        >>> ###
        >>> aggReqLst=['TIME','TMIN','TMAX','TIME']
        >>> timeReqLst=3*[mx.df.index[0]]+[mx.df.index[-1]]
        >>> timeReq2ndLst=4*[mx.df.index[-1]]
        >>> viewLst=['vAGSN','vKNOT','vROHR','vFWVB','vVBEL']
        >>> xm.MxAdd(mx=mx
        ... ,aggReq=aggReqLst
        ... ,timeReq=timeReqLst
        ... ,timeReq2nd=timeReq2ndLst
        ... ,viewList=viewLst
        ... ,ForceNoH5Update=True)    
        >>> vKNOT=xm.dataFrames['vKNOT']
        >>> xm.dataFrames['vKNOTTmp']=vKNOT.round(2)
        >>> print(xm._getvXXXXAsOneString(vXXXX='vKNOTTmp',filterColList=['KNOT~*~*~*~PH','KNOT~*~*~*~PH_1','KNOT~*~*~*~PH_2','KNOT~*~*~*~PH_3'],roundDct={'KNOT~*~*~*~PH':1,'KNOT~*~*~*~PH_1':1,'KNOT~*~*~*~PH_2':1,'KNOT~*~*~*~PH_3':1})) 
            KNOT~*~*~*~PH  KNOT~*~*~*~PH_1  KNOT~*~*~*~PH_2  KNOT~*~*~*~PH_3
        0             2.3              2.0              2.3              2.3
        1             4.0              2.2              4.0              4.0
        2             4.1              2.2              4.1              4.1
        3             4.1              2.2              4.1              4.1
        4             2.0              2.0              2.0              2.0
        5             2.3              2.0              2.3              2.3
        6             2.0              2.0              2.0              2.0
        7             2.3              2.0              2.3              2.3
        8             2.0              2.0              2.0              2.0
        9             2.1              2.0              2.1              2.1
        10            3.8              2.2              3.8              3.8
        11            3.8              2.2              3.8              3.8
        12            2.3              2.0              2.3              2.3
        13            3.8              2.2              3.8              3.8
        14            2.3              2.0              2.3              2.3
        15            3.8              2.2              3.8              3.8
        16            4.1              2.2              4.1              4.1
        17            3.8              2.2              3.8              3.8
        18            4.3              2.2              4.3              4.3
        19            4.1              2.2              4.1              4.1
        20            4.3              2.2              4.3              4.3
        21            2.0              2.0              2.0              2.0
        22            2.0              2.0              2.0              2.0
        >>> xm.MxAdd(mx=mx)
        >>> vKNOT=xm.dataFrames['vKNOT']
        >>> xm.dataFrames['vKNOTTmp']=vKNOT.round(2)        
        >>> print(xm._getvXXXXAsOneString(vXXXX='vKNOTTmp',filterColList=['KNOT~*~*~*~PH','KNOT~*~*~*~PH_1','KNOT~*~*~*~PH_2','KNOT~*~*~*~PH_3'])) 
            KNOT~*~*~*~PH
        0            2.30
        1            3.99
        2            4.08
        3            4.12
        4            2.04
        5            2.28
        6            2.00
        7            2.31
        8            2.00
        9            2.14
        10           3.83
        11           3.82
        12           2.31
        13           3.82
        14           2.31
        15           3.85
        16           4.13
        17           3.81
        18           4.31
        19           4.13
        20           4.29
        21           2.00
        22           2.00
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 

            logger.debug("{:s}aggReq: {!s} TimeL {!s:30s} TimeR {!s:30s} (Eingabeparameter).".format(logStr,aggReq,timeReq,timeReq2nd))   

            returnNothing=False
            if isinstance(mx,Mx.Mx):                
                returnNothing=True
            else:
                mx=self._MxSyncAddMx(ForceNoH5ReadForMx=ForceNoH5ReadForMx)
                      
            if 'vNRCV_Mx1' not in self.dataFrames:
                self.MxSync(mx=mx,ForceNoH5Update=ForceNoH5Update)

            if timeReq==None:
                timeReq=mx.df.index[0]


            # ZielDfs kürzen auf Sachdaten inkl. mx2Idx
            for view in ['vKNOT','vROHR','vFWVB','vVBEL']:
                viewDf=self.dataFrames[view]       

                cols=viewDf.columns.to_list()        
                if 'mx2Idx' in cols:
                    mx2Idx=cols.index('mx2Idx') # mx2Idx

                    viewModelCols=cols[:mx2Idx+1]
                    viewDf=viewDf.filter(items=viewModelCols,axis=1)

                    self.dataFrames[view]=viewDf





            aggReqListmode=False

            if aggReq==None:

                logger.debug("{:s}aggReq: {!s} TimeL {!s:30s} TimeR {!s:30s} (Eingabeparameter verarbeitet).".format(logStr,aggReq,timeReq,timeReq2nd))   

                mxVecsFileData=mx.getMxsVecsFileData(timesReq=[timeReq])[0] 

                # unPack requests a mIndex ...
                colsToBeUnpacked=mxVecsFileData.columns.tolist() # all columns      
                arrays=[[mxVecsFileData.index[0]]*len(colsToBeUnpacked),colsToBeUnpacked]
                tuples = list(zip(*arrays))            
                mIndex = pd.MultiIndex.from_tuples(tuples, names=['Timestamp', 'Sir3sID'])        
                # unPack
                dfUnpacked=mx.unPackMxsVecsFileDataDf(mxVecsFileData,mIndex,returnMultiIndex=False)

                # process
                vKNOT=self.dataFrames['vKNOT']
                vKNOT=self.__MxAddForOneDf(dfTarget=vKNOT
                                            ,dfSource=dfUnpacked.filter(regex='^KNOT'),testStr='KNOT')

                vROHR=self.dataFrames['vROHR']
                vROHR=self.__MxAddForOneDf(dfTarget=vROHR
                                            ,dfSource=dfUnpacked.filter(regex='^ROHR').filter(regex='^(?!.*VEC)'),testStr='ROHR')

                vFWVB=self.dataFrames['vFWVB']            
                if not vFWVB.empty:
                    vFWVB=self.__MxAddForOneDf(dfTarget=vFWVB 
                                                ,dfSource=dfUnpacked.filter(regex='^FWVB'),testStr='FWVB')
           
                self.dataFrames['vKNOT']=vKNOT
                self.dataFrames['vROHR']=vROHR
                self.dataFrames['vFWVB']=vFWVB

                self._MxAddvVBEL(dfSource=dfUnpacked)
                self._MxAddvROHRVecResults(dfSource=dfUnpacked)
                self._MxAddvAGSN()

            else:      
                if timeReq2nd==None:
                    timeReq2nd=mx.df.index[-1]                
                
                logger.debug("{:s}aggReq: {!s} TimeL {!s:30s} TimeR {!s:30s} (Eingabeparameter verarbeitet - vor Check auf Liste).".format(logStr,aggReq,timeReq,timeReq2nd))   

                if isinstance(aggReq,list):
                    if isinstance(timeReq,list) and isinstance(timeReq2nd,list):
                        if len(aggReq)==len(timeReq) and len(aggReq)==len(timeReq2nd):
                            logger.debug("{:s}aggReq: {!s} TimeL {!s} TimeR {!s}: aggReq ist Liste - die Zeiten auch - ok.".format(logStr,aggReq,timeReq,timeReq2nd))  
                            aggReqL=aggReq
                            timeReqL=timeReq
                            timeReq2ndL=timeReq2nd
                            aggReqListmode=True
                        else:
                            logStrFinal="{:s}aggReq: {!s} TimeL {!s} TimeR {!s}: aggReq ist Liste - die Zeiten auch - aber nicht selbe Länge?!".format(logStr,aggReq,timeReq,timeReq2nd)                               
                            raise XmError(logStrFinal)                             
                    else:
                        logStrFinal="{:s}aggReq: {!s} TimeL {!s} TimeR {!s}: aggReq ist Liste - die Zeiten aber nicht?!".format(logStr,aggReq,timeReq,timeReq2nd)                               
                        raise XmError(logStrFinal)  
                else:                    
                    aggReqL=[aggReq]
                    timeReqL=[timeReq]
                    timeReq2ndL=[timeReq2nd]  
                    
                
                for idx, (aggReq, timeReq, timeReq2nd) in enumerate(zip(aggReqL, timeReqL, timeReq2ndL)):
                    

                    if aggReq == 'TIME':
                            aTIME=True
                            timeReq2nd=timeReq
                    else:
                            aTIME=False

                    reqAggFound=False
                    if mx.dfVecAggs.index.isin([aggReq],level=0).any(): # aggReq existiert 
                        if mx.dfVecAggs.loc[(aggReq,slice(None),slice(None),slice(None)),:].index.isin([timeReq],level=2).any(): # mit dieser ZeitL
                            if mx.dfVecAggs.loc[(aggReq,slice(None),timeReq,slice(None)),:].index.isin([timeReq2nd],level=3).any(): # mit dieser ZeitR
                                logger.debug("{:s}aggReq: {!s} TimeL {!s:30s} TimeR {!s:30s}     in mx.dfVecAggs.".format(logStr,aggReq,timeReq,timeReq2nd))                               
                                reqAggFound=True

                    if not reqAggFound:                         
                        logger.debug("{:s}aggReq: {!s} TimeL {!s:30s} TimeR {!s:30s} not in mx.dfVecAggs. mx.getVecAggs() called ...".format(logStr,aggReq,timeReq,timeReq2nd))   
                        #if aggReq == 'TIME':
                        #    aTIME=True
                        #    timeReq2nd=timeReq
                        #else:
                        #    aTIME=False
                        df,tL,tR=mx.getVecAggs(time1st=timeReq,time2nd=timeReq2nd,aTIME=aTIME)
                        if df.empty:
                            logStrFinal="{:s}aggReq: {!s} TimeL {!s} TimeR {!s}: mx.getVecAggs kein Ergebnis!".format(logStr,aggReq,timeReq,timeReq2nd)                               
                            raise XmError(logStrFinal)   
 
                    try:
                        df=mx.dfVecAggs.loc[(aggReq,slice(None),timeReq,timeReq2nd),:]
                        dfT=df.transpose(copy=True)
                        colIndex=dfT.columns.droplevel(level=0)
                        colIndex=colIndex.droplevel(level=1)
                        colIndex=colIndex.droplevel(level=1)
                        colIndex.name=None
                        dfUnpacked=pd.DataFrame(dfT.values,columns=colIndex)
                    except Exception as e:
                        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
                        logger.error(logStrFinal) 
                        logger.debug("{:s}aggReq {:s} with TimeL {!s:30s} and TimeR {!s:30s} not in mx.dfVecAggs.".format(logStr,aggReq,timeReq,timeReq2nd)) 
                        raise XmError(logStrFinal)    

                    # process                      
                    vKNOT=self.dataFrames['vKNOT']
                    vKNOT=self.__MxAddForOneDf(dfTarget=vKNOT
                                                ,dfSource=dfUnpacked.filter(regex='^KNOT'),testStr='KNOT')

                    vROHR=self.dataFrames['vROHR']
                    vROHR=self.__MxAddForOneDf(dfTarget=vROHR
                                                ,dfSource=dfUnpacked.filter(regex='^ROHR').filter(regex='^(?!.*VEC)'),testStr='ROHR')

                    vFWVB=self.dataFrames['vFWVB']            
                    if not vFWVB.empty:
                        vFWVB=self.__MxAddForOneDf(dfTarget=vFWVB 
                                                    ,dfSource=dfUnpacked.filter(regex='^FWVB'),testStr='FWVB')
           
                    self.dataFrames['vKNOT']=vKNOT
                    self.dataFrames['vROHR']=vROHR
                    self.dataFrames['vFWVB']=vFWVB

                    self._MxAddvVBEL(dfSource=dfUnpacked)
                    self._MxAddvROHRVecResults(dfSource=dfUnpacked)
                    self._MxAddvAGSN()

                    logger.debug("{:s}Processing viewList: {!s:s} ...".format(logStr,viewList))   

                    if idx == 0: # nach dem ersten Durchlauf:                                      
                        sepColIdxDct={}   
                        colListDct={}
                        dfDct={}
                        for vView in viewList: #['vAGSN']:
                                
                            vViewDf = self.dataFrames[vView]    # view
                            colList=vViewDf.columns.tolist()    # liste der Spalten des Views
                            sepColIdx=colList.index('mx2Idx')   # Trennspalte ermitteln
                            sepColIdxDct[vView]=sepColIdx       # Trennspalte merken      
                            colListDct[vView]=colList           # Spalten nach einfachem Durchlauf merken
                                                                # Spalten nach Trennspalte sind dann die Ergebnisspalten pro Durchlauf

                            logger.debug("{:s}nach dem 1. Durchlauf von mehreren ({:d}) Zeiten: View: {:s} sepColIdx: {:d}".format(logStr,len(aggReqL),vView,sepColIdx))   

                            dfDct[vView]=pd.concat(
                                [
                                     vViewDf[colList[:sepColIdx+1]]
                                    ,vViewDf[colList[sepColIdx+1:]]
                                ],axis=1
                                 )

                    if idx >= 1: # ab nach dem zweiten Durchlauf                        
                        for vView in viewList: #['vAGSN']:
                            vViewDf = self.dataFrames[vView]  # view                          
                            sepColIdx=sepColIdxDct[vView]     # Trennspalte
                            colList=colListDct[vView]         # Spalten nach einfachem Durchlauf
                            
                            logger.debug("{:s}ab einschl. dem 2. Durchlauf von mehreren ({:d}) Zeiten: View: {:s} sepColIdx: {:d}: weitere Ergebnisspalten mit selbem Namen dranhaengen".format(logStr,len(aggReqL),vView,sepColIdx))   

                            dfDct[vView]=pd.concat(
                                [
                                     dfDct[vView]
                                    ,vViewDf[colList[sepColIdx+1:]] # Spalten nach Trennspalte dranhaengen (mit selbem Namen) 
                                ],axis=1
                                 )
                        
                    if idx == len(aggReqL)-1 and len(aggReqL) > 1:
                        for vView in viewList: # ['vAGSN']:

                             logger.debug("{:s}letzter Durchlauf von mehreren ({:d}) Zeiten: View: {:s}: entstandene Mehrfachspalten umbenennen".format(logStr,len(aggReqL),vView))   
                             
                             colCount={col:0 for col in dfDct[vView].columns.tolist() }
                             cols=[]
                             for col in dfDct[vView].columns:
                                if colCount[col] > 0:
                                    colName=str(col)+'_'+str(colCount[col])
                                else:
                                    colName=col
                                cols.append(colName)
                                colCount[col]=colCount[col]+1                  
                             
                             dfDct[vView].columns = cols          
                             self.dataFrames[vView]=dfDct[vView]  
          
            if self.h5Read and not ForceNoH5Update:
                self.ToH5()          
                                                  
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
            raise XmError(logStrFinal)      
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
            if not returnNothing:
                return mx

    def _MxAddvVBEL(self,dfSource):
        """(Re-)constructing vVBEL with MX2-Results.

        Arguments:
            dfSource

        Result:
            View with MX2-Results added:            
                * in the Xm-View below col mx2Idx must exist 
                * mx2Idx is considered to be the last of the Model-cols
                * right from mx2Idx Result-cols are added if not already existing
                * already existing Result-cols are overwritten
                * mx2Idx-View:
                    * ...                 
                    * vVBEL (KNOT..._i and KNOT..._k and Q)
         
        Raises:
            XmError

        >>> xm=xms['GPipes']
        >>> mx=xm.MxSync()
        >>> xm.MxAdd(mx=mx)    
        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['BESCHREIBUNG','IDREFERENZ','tk NAME_i','CONT_i',' CONT_VKNO_i','Z_i','pk_i']))
                                     BESCHREIBUNG             IDREFERENZ   CONT_i  Z_i                 pk_i
        OBJTYPE OBJID                                                                                      
        ROHR    4979507900871287244  _Split_Split  3S4979507900871287244  M-1-0-1    0  4731210032713520411
                5114681686941855110        _Split  3S5114681686941855110  M-1-0-1    0  5709889458254995435
                5244313507655010738           NaN  3S5244313507655010738  M-1-0-1    0  5256558483525770176
                5694016449043789006           NaN  3S5694016449043789006  M-1-0-1    0  4731210032713520411
        VENT    5116489323526156845           NaN  3S5508684139418025293  M-1-0-1  100  4683988347517083361
                5309992331398639768           NaN  3S5309992331398639768  M-1-0-1    0  5046108271210239718
                5508684139418025293           NaN  3S5508684139418025293  M-1-0-1  100  4683988347517083361
                5745097345184516675           NaN  3S5745097345184516675  M-1-0-1    0  5308591811899364960
        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['BESCHREIBUNG','IDREFERENZ','tk NAME_k','CONT_k',' CONT_VKNO_k','Z_k','pk_k']))
                                     BESCHREIBUNG             IDREFERENZ   CONT_k  Z_k                 pk_k
        OBJTYPE OBJID                                                                                      
        ROHR    4979507900871287244  _Split_Split  3S4979507900871287244  M-1-0-1    0  5441322867018839631
                5114681686941855110        _Split  3S5114681686941855110  M-1-0-1    0  5441322867018839631
                5244313507655010738           NaN  3S5244313507655010738  M-1-0-1  100  4683988347517083361
                5694016449043789006           NaN  3S5694016449043789006  M-1-0-1    0  5061043246189134395
        VENT    5116489323526156845           NaN  3S5508684139418025293  M-1-0-1    0  5709889458254995435
                5309992331398639768           NaN  3S5309992331398639768  M-1-0-1    0  5256558483525770176
                5508684139418025293           NaN  3S5508684139418025293  M-1-0-1    0  5709889458254995435
                5745097345184516675           NaN  3S5745097345184516675  M-1-0-1    0  4731210032713520411
        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['LAYR','L','D','mx2Idx']))
                                    LAYR           L    D  mx2Idx
        OBJTYPE OBJID                                            
        ROHR    4979507900871287244   []       10000  500       2
                5114681686941855110   []       10000  500       1
                5244313507655010738   []      160000  500       0
                5694016449043789006   []  100.498688  450       3
        VENT    5116489323526156845   []           0  666       3
                5309992331398639768   []           0  800       0
                5508684139418025293   []           0  800       2
                5745097345184516675   []           0  800       1

        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['KNOT~*~*~*~RHON_i','KNOT~*~*~*~H_i','KNOT~*~*~*~LFAKTAKT_i','KNOT~*~*~*~P_i','KNOT~*~*~*~PH_i','KNOT~*~*~*~PH_EIN_i','KNOT~*~*~*~QM_i','KNOT~*~*~*~RHO_i','KNOT~*~*~*~T_i','KNOT~*~*~*~EH_i']
        ...         ,roundDct={'KNOT~*~*~*~H_i':1,'KNOT~*~*~*~P_i':1,'KNOT~*~*~*~PH_i':1,'KNOT~*~*~*~PH_EIN_i':1,'KNOT~*~*~*~QM_i':1,'KNOT~*~*~*~RHO_i':1,'KNOT~*~*~*~T_i':1,'KNOT~*~*~*~EH_i':1}
        ...         ))         
                                     KNOT~*~*~*~RHON_i  KNOT~*~*~*~H_i  KNOT~*~*~*~LFAKTAKT_i  KNOT~*~*~*~P_i  KNOT~*~*~*~PH_i  KNOT~*~*~*~PH_EIN_i  KNOT~*~*~*~QM_i  KNOT~*~*~*~RHO_i  KNOT~*~*~*~T_i  KNOT~*~*~*~EH_i
        OBJTYPE OBJID                                                                                                                                                                                                  
        ROHR    4979507900871287244               0.83         10106.2                    1.0            11.1             10.1                 10.1              0.0               7.9            49.0          13046.7
                5114681686941855110               0.83         16375.8                    1.0            17.4             16.4                 16.4              0.0              12.8            40.9          13008.5
                5244313507655010738               0.83         39974.0                    1.0            41.0             40.0                 40.0              0.0              31.9            40.0          12777.4
                5694016449043789006               0.83         10106.2                    1.0            11.1             10.1                 10.1              0.0               7.9            49.0          13046.7
        VENT    5116489323526156845               0.83         16440.5                    1.0            17.4             16.4                 16.4              0.0              12.9            40.9          13111.2
                5309992331398639768               0.83         40000.0                    1.0            41.0             40.0                 40.0         118257.5              31.9            40.0          12777.4
                5508684139418025293               0.83         16440.5                    1.0            17.4             16.4                 16.4              0.0              12.9            40.9          13111.2
                5745097345184516675               0.83         10000.0                    1.0            11.0             10.0                 10.0        -118257.5               7.8            49.0          13034.1
        >>> print(xm._getvXXXXAsOneString(vXXXX='vVBEL',filterColList=['KNOT~*~*~*~HMAX_INST_i','KNOT~*~*~*~HMIN_INST_i','KNOT~*~*~*~PMAX_INST_i','KNOT~*~*~*~PMIN_INST_i','KNOT~*~*~*~IAKTIV_i','KNOT~*~*~*~PDAMPF_i']
        ...         ,roundDct={'KNOT~*~*~*~HMAX_INST_i':1,'KNOT~*~*~*~HMIN_INST_i':1,'KNOT~*~*~*~PMAX_INST_i':1,'KNOT~*~*~*~PMIN_INST_i':1}
        ...         ))
                                     KNOT~*~*~*~HMAX_INST_i  KNOT~*~*~*~HMIN_INST_i  KNOT~*~*~*~PMAX_INST_i  KNOT~*~*~*~PMIN_INST_i  KNOT~*~*~*~IAKTIV_i  KNOT~*~*~*~PDAMPF_i
        OBJTYPE OBJID                                                                                                                                                        
        ROHR    4979507900871287244                 10106.2                 10106.2                    11.1                    11.1                  0.0                  0.0
                5114681686941855110                 16375.8                 16375.8                    17.4                    17.4                  0.0                  0.0
                5244313507655010738                 39974.0                 39974.0                    41.0                    41.0                  0.0                  0.0
                5694016449043789006                 10106.2                 10106.2                    11.1                    11.1                  0.0                  0.0
        VENT    5116489323526156845                 16440.5                 16440.5                    17.4                    17.4                  0.0                  0.0
                5309992331398639768                 40000.0                 40000.0                    41.0                    41.0                  0.0                  0.0
                5508684139418025293                 16440.5                 16440.5                    17.4                    17.4                  0.0                  0.0
                5745097345184516675                 10000.0                 10000.0                    11.0                    11.0                  0.0                  0.0
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             
            #vVBEL - Knoten
            vKNOT=self.dataFrames['vKNOT']
            vVBEL=self.dataFrames['vVBEL']

            vVBELCols=vVBEL.columns.tolist()
            mx2IdxColVBELIdx=vVBELCols.index('mx2Idx')
            vKNOTCols=vKNOT.columns.tolist()
            mx2IdxColKNOTIdx=vKNOTCols.index('mx2Idx')

            knotResultCols=vKNOTCols[mx2IdxColKNOTIdx+1:]
            vbelModelCols=vVBELCols[:mx2IdxColVBELIdx+1]

            knotResultColsi=[col+'_i' for col in knotResultCols]
            knotResultColsk=[col+'_k' for col in knotResultCols]

            knotResultColsiRenameDct={}
            knotResultColskRenameDct={}
            for idx,col in enumerate(knotResultCols):
                knotResultColsiRenameDct[col]=knotResultColsi[idx]
                knotResultColskRenameDct[col]=knotResultColsk[idx]

            df=pd.merge(vVBEL.loc[:,vbelModelCols],vKNOT,left_on='pk_i',right_on='pk',suffixes=['','_i']).filter(items=vbelModelCols+knotResultCols)
            df.rename(columns=knotResultColsiRenameDct,inplace=True)
            
            df=pd.merge(df,vKNOT,left_on='pk_k',right_on='pk',suffixes=['','_k']).filter(items=vbelModelCols+knotResultColsi+knotResultCols)
            df.rename(columns=knotResultColskRenameDct,inplace=True)

            # merge again for correct alignment
            df=pd.merge(vVBEL.loc[:,vbelModelCols],df.filter(items=['tk','pk_i','pk_k']+knotResultColsi+knotResultColsk),on=['tk','pk_i','pk_k']).filter(items=vbelModelCols+knotResultColsi+knotResultColsk)
            dfResultColsOnly=df.filter(knotResultColsi+knotResultColsk)

            logger.debug("{:s}Spalten Knoten             : {!s:s}".format(logStr,vKNOT.columns.to_list()))      
            logger.debug("{:s}Ergebnisspalten konstruiert: {!s:s}".format(logStr,dfResultColsOnly.columns.to_list()))      

            if dfResultColsOnly.columns.isin(vVBELCols).all():
                pass
            else:
                if not dfResultColsOnly.columns.isin(vVBELCols).any():
                    # no col to be added exist
                    for col in dfResultColsOnly:
                        vVBEL[col]=None
                else:
                    # only some cols to be added exist?!       
                    logStringFinal="{0:s}Some but - not all! - cols from dfResultColsOnly exist in dfTarget vVBEL: existing: {1:s} not existing: {2:s}".format(logStr
                                                    ,str(list(set(vVBELCols) & set(dfResultColsOnly)))
                                                    ,str(list(set(dfResultColsOnly) - set(vVBELCols)))
                                                    )             
                    logger.error(logStringFinal) 
                    raise XmError(logStringFinal)

            shapeLeft=vVBEL.loc[:,knotResultColsi+knotResultColsk].shape 
            shapeRight=dfResultColsOnly.shape
            if shapeLeft != shapeRight:
                logStringFinal="{0:s}Alignment Mismatch: shapeLeft vVBEL: {1:s} <> shapeRight df: {2:s}".format(logStr
                                                    ,str(shapeLeft)
                                                    ,str(shapeRight)
                                                    )
                logger.error(logStringFinal) 
                raise XmError(logStringFinal)

            vVBEL.loc[:,knotResultColsi+knotResultColsk]=dfResultColsOnly.values


            #vVBEL - Q
            vVBEL['Q']=None 

            for idx,vbel in enumerate(vVBEL_edges):
                try:
                    df=vVBEL.loc[vbel] 
                except KeyError:
                    continue # VBEL nicht in Modell 
    
                #DataFrame: 1 Zeit, Spalte(n), in den Zelle stehen die Werte als Tuple 
                if vbel != 'ROHR':
                    dfQ=dfSource.filter(regex='~'+Mx.vVBEL_edgesQ[idx]+'$').filter(regex='^'+vbel)
                else:
                    dfQ=dfSource.filter(regex='~'+Mx.vVBEL_edgesQ[idx]+'$').filter(regex='^'+vbel).filter(regex='^(?!.*VEC)')
                shape=dfQ.shape
    
                if shape[1]==0:
                    continue # Spalte nicht in MX2
                if shape[1]>1:
                    continue # mehr als 1 matchende Spalte in MX2?!

                colName=dfQ.columns.tolist()[0]
                vVBEL=self.__MxAddForOneDf(dfTarget=vVBEL,dfSource=dfQ.rename(columns={colName:'Q'}),multiIndexKey=vbel,testStr='vVBEL_'+vbel)

                #logger.debug("{0:s}vVBEL Liste: {1:s}".format(logStr,str(vVBEL.columns.tolist())))  

            self.dataFrames['vVBEL']=vVBEL           
                                                  
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

    def _MxAddvROHRVecResults(self,dfSource):
        """(Re-)constructing vROHRVecResults.

        Arguments:
            * dfSource

        Result:
            * vROHRVecResults: VEC-Channel-Results for Pipe-Interior-Pts (IPts):
                * pk
                * mx2Idx
                * IptIdx: S,0,...,E - Interior Point Index; S=Start EdgeDefNode, E=End EdgeDefNode, 0=1st Ipt in EdgeDefDirection
                * one column per VEC-Channel
         
        Raises:
            XmError

        >>> xm=xms['GPipes']
        >>> mx=xm.MxSync()               
        >>> mxVecsFileDataLst=mx.getMxsVecsFileData()
        >>> mxVecsFileData=mxVecsFileDataLst[0]
        >>> # construct MultiIndex Start ... ---
        >>> colsToBeUnpacked=mxVecsFileData.columns.tolist() # all columns        
        >>> arrays=[[mxVecsFileData.index[0]]*len(colsToBeUnpacked),colsToBeUnpacked]
        >>> tuples = list(zip(*arrays))
        >>> import pandas as pd
        >>> mIndex = pd.MultiIndex.from_tuples(tuples, names=['Timestamp', 'Sir3sID'])                
        >>> # construct MultiIndex End ... ---
        >>> dfUnpacked=mx.unPackMxsVecsFileDataDf(mxVecsFileData,mIndex,returnMultiIndex=False)
        >>> xm._MxAddvROHRVecResults(dfSource=dfUnpacked)   
        >>> print(xm._getvXXXXAsOneString(vXXXX='vROHRVecResults',sortList=['ROHR~*~*~*~PHVEC','ROHR~*~*~*~SVEC'],ascending=False,roundDct={'ROHR~*~*~*~SVEC':1,'ROHR~*~*~*~TVEC':1,'ROHR~*~*~*~ZVEC':1,'ROHR~*~*~*~PVEC':1,'ROHR~*~*~*~MVEC':1,'ROHR~*~*~*~RHOVEC':1,'ROHR~*~*~*~PHVEC':1,'ROHR~*~*~*~QMVEC':1}))
                             pk  mx2Idx IptIdx  ROHR~*~*~*~SVEC  ROHR~*~*~*~TVEC  ROHR~*~*~*~ZVEC  ROHR~*~*~*~PVEC  ROHR~*~*~*~MVEC  ROHR~*~*~*~RHOVEC  ROHR~*~*~*~PHVEC  ROHR~*~*~*~QMVEC
        8   5244313507655010738       0      S              0.0             40.0              0.0             41.0             27.3               31.9              40.0            3077.8
        9   5244313507655010738       0      0           5000.0             40.4              3.1             40.5             27.3               31.4              39.5            3121.6
        10  5244313507655010738       0      1          10000.0             40.4              6.2             39.9             27.3               31.0              38.9            3166.3
        11  5244313507655010738       0      2          15000.0             40.4              9.4             39.4             27.3               30.5              38.4            3212.9
        12  5244313507655010738       0      3          20000.0             40.4             12.5             38.8             27.3               30.1              37.8            3261.5
        13  5244313507655010738       0      4          25000.0             40.4             15.6             38.3             27.3               29.6              37.3            3312.3
        14  5244313507655010738       0      5          30000.0             40.4             18.8             37.7             27.3               29.2              36.7            3365.3
        15  5244313507655010738       0      6          35000.0             40.4             21.9             37.2             27.3               28.7              36.2            3420.8
        16  5244313507655010738       0      7          40000.0             40.3             25.0             36.6             27.3               28.2              35.6            3478.9
        17  5244313507655010738       0      8          45000.0             40.3             28.1             36.0             27.3               27.7              35.0            3540.0
        18  5244313507655010738       0      9          50000.0             40.3             31.2             35.4             27.3               27.2              34.4            3604.2
        19  5244313507655010738       0     10          55000.0             40.3             34.4             34.8             27.3               26.7              33.8            3671.8
        20  5244313507655010738       0     11          60000.0             40.3             37.5             34.2             27.3               26.2              33.2            3743.2
        21  5244313507655010738       0     12          65000.0             40.3             40.6             33.5             27.3               25.7              32.5            3818.6
        22  5244313507655010738       0     13          70000.0             40.3             43.8             32.9             27.3               25.2              31.9            3898.6
        23  5244313507655010738       0     14          75000.0             40.3             46.9             32.2             27.3               24.6              31.2            3983.5
        24  5244313507655010738       0     15          80000.0             40.3             50.0             31.6             27.3               24.1              30.6            4073.9
        25  5244313507655010738       0     16          85000.0             40.3             53.1             30.9             27.3               23.5              29.9            4170.5
        26  5244313507655010738       0     17          90000.0             40.3             56.2             30.2             27.3               23.0              29.2            4273.9
        27  5244313507655010738       0     18          95000.0             40.3             59.4             29.5             27.3               22.4              28.5            4385.1
        28  5244313507655010738       0     19         100000.0             40.3             62.5             28.7             27.3               21.8              27.7            4505.0
        29  5244313507655010738       0     20         105000.0             40.3             65.6             28.0             27.3               21.2              27.0            4634.8
        30  5244313507655010738       0     21         110000.0             40.3             68.8             27.2             27.3               20.6              26.2            4776.0
        31  5244313507655010738       0     22         115000.0             40.4             71.9             26.4             27.3               19.9              25.4            4930.3
        32  5244313507655010738       0     23         120000.0             40.4             75.0             25.5             27.3               19.2              24.5            5100.1
        33  5244313507655010738       0     24         125000.0             40.4             78.1             24.7             27.3               18.6              23.7            5287.9
        34  5244313507655010738       0     25         130000.0             40.4             81.2             23.8             27.3               17.9              22.8            5497.2
        35  5244313507655010738       0     26         135000.0             40.5             84.4             22.9             27.3               17.1              21.9            5732.6
        36  5244313507655010738       0     27         140000.0             40.5             87.5             21.9             27.3               16.4              20.9            5999.9
        37  5244313507655010738       0     28         145000.0             40.6             90.6             20.9             27.3               15.6              19.9            6307.0
        38  5244313507655010738       0     29         150000.0             40.7             93.8             19.8             27.3               14.7              18.8            6665.0
        39  5244313507655010738       0     30         155000.0             40.8             96.9             18.7             27.3               13.8              17.7            7089.7
        40  5244313507655010738       0      E         160000.0             40.9            100.0             17.4             27.3               12.9              16.4            7604.8
        5   5114681686941855110       1      S              0.0             40.9              0.0             17.4             27.3               12.8              16.4            7652.5
        6   5114681686941855110       1      0           5000.0             43.7              0.0             16.1             27.3               11.8              15.1            8353.3
        4   4979507900871287244       2      E          10000.0             44.0              0.0             14.6            -27.3               10.6              13.6           -9242.2
        7   5114681686941855110       1      E          10000.0             44.0              0.0             14.6             27.3               10.7              13.6            9214.7
        3   4979507900871287244       2      0           5000.0             48.2              0.0             13.0            -27.3                9.3              12.0          -10534.3
        0   5694016449043789006       3      S              0.0             10.0              0.0             11.1              0.0                6.9              10.1               0.0
        2   4979507900871287244       2      S              0.0             49.0              0.0             11.1            -27.3                7.9              10.1          -12394.5
        1   5694016449043789006       3      E            100.5             10.0              0.0              1.0              0.0                0.6               0.0               0.0
        >>> print(xm._getvXXXXAsOneString(vXXXX='vROHRVecResults',roundDct={'ROHR~*~*~*~SVEC':1,'ROHR~*~*~*~TVEC':1,'ROHR~*~*~*~ZVEC':1,'ROHR~*~*~*~PVEC':1,'ROHR~*~*~*~MVEC':1,'ROHR~*~*~*~RHOVEC':1,'ROHR~*~*~*~PHVEC':1,'ROHR~*~*~*~QMVEC':1}))
                             pk  mx2Idx IptIdx  ROHR~*~*~*~SVEC  ROHR~*~*~*~TVEC  ROHR~*~*~*~ZVEC  ROHR~*~*~*~PVEC  ROHR~*~*~*~MVEC  ROHR~*~*~*~RHOVEC  ROHR~*~*~*~PHVEC  ROHR~*~*~*~QMVEC
        0   5694016449043789006       3      S              0.0             10.0              0.0             11.1              0.0                6.9              10.1               0.0
        1   5694016449043789006       3      E            100.5             10.0              0.0              1.0              0.0                0.6               0.0               0.0
        2   4979507900871287244       2      S              0.0             49.0              0.0             11.1            -27.3                7.9              10.1          -12394.5
        3   4979507900871287244       2      0           5000.0             48.2              0.0             13.0            -27.3                9.3              12.0          -10534.3
        4   4979507900871287244       2      E          10000.0             44.0              0.0             14.6            -27.3               10.6              13.6           -9242.2
        5   5114681686941855110       1      S              0.0             40.9              0.0             17.4             27.3               12.8              16.4            7652.5
        6   5114681686941855110       1      0           5000.0             43.7              0.0             16.1             27.3               11.8              15.1            8353.3
        7   5114681686941855110       1      E          10000.0             44.0              0.0             14.6             27.3               10.7              13.6            9214.7
        8   5244313507655010738       0      S              0.0             40.0              0.0             41.0             27.3               31.9              40.0            3077.8
        9   5244313507655010738       0      0           5000.0             40.4              3.1             40.5             27.3               31.4              39.5            3121.6
        10  5244313507655010738       0      1          10000.0             40.4              6.2             39.9             27.3               31.0              38.9            3166.3
        11  5244313507655010738       0      2          15000.0             40.4              9.4             39.4             27.3               30.5              38.4            3212.9
        12  5244313507655010738       0      3          20000.0             40.4             12.5             38.8             27.3               30.1              37.8            3261.5
        13  5244313507655010738       0      4          25000.0             40.4             15.6             38.3             27.3               29.6              37.3            3312.3
        14  5244313507655010738       0      5          30000.0             40.4             18.8             37.7             27.3               29.2              36.7            3365.3
        15  5244313507655010738       0      6          35000.0             40.4             21.9             37.2             27.3               28.7              36.2            3420.8
        16  5244313507655010738       0      7          40000.0             40.3             25.0             36.6             27.3               28.2              35.6            3478.9
        17  5244313507655010738       0      8          45000.0             40.3             28.1             36.0             27.3               27.7              35.0            3540.0
        18  5244313507655010738       0      9          50000.0             40.3             31.2             35.4             27.3               27.2              34.4            3604.2
        19  5244313507655010738       0     10          55000.0             40.3             34.4             34.8             27.3               26.7              33.8            3671.8
        20  5244313507655010738       0     11          60000.0             40.3             37.5             34.2             27.3               26.2              33.2            3743.2
        21  5244313507655010738       0     12          65000.0             40.3             40.6             33.5             27.3               25.7              32.5            3818.6
        22  5244313507655010738       0     13          70000.0             40.3             43.8             32.9             27.3               25.2              31.9            3898.6
        23  5244313507655010738       0     14          75000.0             40.3             46.9             32.2             27.3               24.6              31.2            3983.5
        24  5244313507655010738       0     15          80000.0             40.3             50.0             31.6             27.3               24.1              30.6            4073.9
        25  5244313507655010738       0     16          85000.0             40.3             53.1             30.9             27.3               23.5              29.9            4170.5
        26  5244313507655010738       0     17          90000.0             40.3             56.2             30.2             27.3               23.0              29.2            4273.9
        27  5244313507655010738       0     18          95000.0             40.3             59.4             29.5             27.3               22.4              28.5            4385.1
        28  5244313507655010738       0     19         100000.0             40.3             62.5             28.7             27.3               21.8              27.7            4505.0
        29  5244313507655010738       0     20         105000.0             40.3             65.6             28.0             27.3               21.2              27.0            4634.8
        30  5244313507655010738       0     21         110000.0             40.3             68.8             27.2             27.3               20.6              26.2            4776.0
        31  5244313507655010738       0     22         115000.0             40.4             71.9             26.4             27.3               19.9              25.4            4930.3
        32  5244313507655010738       0     23         120000.0             40.4             75.0             25.5             27.3               19.2              24.5            5100.1
        33  5244313507655010738       0     24         125000.0             40.4             78.1             24.7             27.3               18.6              23.7            5287.9
        34  5244313507655010738       0     25         130000.0             40.4             81.2             23.8             27.3               17.9              22.8            5497.2
        35  5244313507655010738       0     26         135000.0             40.5             84.4             22.9             27.3               17.1              21.9            5732.6
        36  5244313507655010738       0     27         140000.0             40.5             87.5             21.9             27.3               16.4              20.9            5999.9
        37  5244313507655010738       0     28         145000.0             40.6             90.6             20.9             27.3               15.6              19.9            6307.0
        38  5244313507655010738       0     29         150000.0             40.7             93.8             19.8             27.3               14.7              18.8            6665.0
        39  5244313507655010738       0     30         155000.0             40.8             96.9             18.7             27.3               13.8              17.7            7089.7
        40  5244313507655010738       0      E         160000.0             40.9            100.0             17.4             27.3               12.9              16.4            7604.8
        >>> xm=xms['LocalHeatingNetwork']
        >>> mx=xm.MxSync()
        >>> xm.MxAdd(mx=mx)          
        >>> print(xm._getvXXXXAsOneString(vXXXX='vROHRVecResults',filterColList=['mx2Idx','IptIdx','ROHR~*~*~*~SVEC'],index=True))
            mx2Idx IptIdx  ROHR~*~*~*~SVEC
        0        0      S         0.000000
        1        0      E        88.019997
        2        1      S         0.000000
        3        1      E       405.959991
        4        2      S         0.000000
        5        2      E        83.550003
        6        3      S         0.000000
        7        3      E        88.019997
        8        5      S         0.000000
        9        5      E       195.529999
        10       7      S         0.000000
        11       7      E       109.769997
        12       8      S         0.000000
        13       8      E        76.400002
        14       9      S         0.000000
        15       9      E        83.550003
        16      10      S         0.000000
        17      10      E       164.910004
        18      11      S         0.000000
        19      11      E       195.529999
        20      12      S         0.000000
        21      12      E       405.959991
        22      13      S         0.000000
        23      13      E       164.910004
        24      14      S         0.000000
        25      14      E       109.769997
        26      15      S         0.000000
        27      15      E        76.400002
        28       4      S         0.000000
        29       4      E        73.419998
        30       6      S         0.000000
        31       6      E        68.599998
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:       
            #VEC
            reExpNegLookAhead='(?P<ObjType>\S+)~(?P<Name_i>\S*)~(?P<Name_k>\S*)~(?!\d+)(?P<ObjId>[\*\d]*)~(?P<ChannelType>\S+)'
            dfSource=dfSource.filter(regex='(VEC$)').filter(regex='(^ROHR)').filter(regex=reExpNegLookAhead)
            
            vROHRVecResults=dfSource
            
            colsToBeAdded=vROHRVecResults.columns.tolist()
            colsMaybeAlreadyAdded=dfSource.filter(regex='(VEC$)').filter(regex='(^ROHR)').filter(regex=reExpNegLookAhead).columns.tolist()
            #.filter(regex='^ROHR').filter(regex='^(?!.*VEC)')
            #.columns.tolist()
            vROHR=self.dataFrames['vROHR']
            colsInTarget=vROHR.columns.tolist()
            colsInTargetNet=list(set(colsInTarget)-set(colsToBeAdded)-set(colsMaybeAlreadyAdded))
            colsInTargetNet=[col for col in colsInTarget if col in colsInTargetNet] # preserve the original col-Sequence


            rVecMx2Idx=[] 
            IptIdx=[] 

            for row in vROHR.sort_values(['mx2Idx']).itertuples(): # Mx2-Records sind in Mx2-Reihenfolge und muessen auch so annotiert werden ...
                oneVecIdx=np.empty(row.mx2NofPts,dtype=int) 
                oneVecIdx.fill(row.mx2Idx)                
                rVecMx2Idx.extend(oneVecIdx)
    
                oneLfdNrIdx=['S']
                if row.mx2NofPts>2:                    
                    oneLfdNrIdx.extend(np.arange(row.mx2NofPts-2,dtype=int))
                oneLfdNrIdx.append('E')
                IptIdx.extend(oneLfdNrIdx)
            
            vROHRVecResults['mx2Idx']=rVecMx2Idx
            vROHRVecResults['IptIdx']=IptIdx  
            vROHRVecResults=vROHRVecResults[['mx2Idx']+['IptIdx']+colsToBeAdded]

            dfMerge=pd.merge(vROHR.filter(items=colsInTargetNet),vROHRVecResults,how='inner',left_on='mx2Idx',right_on='mx2Idx')        
            #logString="{0:s}The cols from dfMerge: {1:s}".format(logStr,str(dfMerge.columns.tolist()))
            #logger.debug(logString)
            vROHRVecResults=dfMerge[['pk']+['mx2Idx']+['IptIdx']+colsToBeAdded]

            self.dataFrames['vROHRVecResults']=vROHRVecResults            
        
                                                  
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

    def _MxAddvAGSN(self):
        """(Re-)constructing vAGSN.

        Result:

            * vAGSN
                * all cols from vAGSN_raw
                * from vVBEL: 
                    * KNOT..._i (droped for processed RVECS)
                    * and KNOT..._k (droped for processed RVECS)
                    * and Q; Q also contains vROHRVecResults - RVEC QMVEC is droped; Q in Schnittrichtung
                * due to vROHRVecResults:                    
                    * IptIdx      
                    * RVECs not processed, i.e. ROHR~*~*~*~MVEC
                    * Geometry:
                        * dx                       
                        * x                        
                        * xVbel      
                    * RVECs processed, i.e.
                        * RHO - the corresponding KNOT~*~*~*~RHO_i KNOT~*~*~*~RHO_k  ROHR~*~*~*~RHOVEC are droped
                        * T   - the corresponding KNOT~*~*~*~T_i   KNOT~*~*~*~T_k    ROHR~*~*~*~TVEC   are droped 
                        * P   - the corresponding KNOT~*~*~*~P_i   KNOT~*~*~*~P_k    ROHR~*~*~*~PVEC   are droped                                                           
                            * P is new column
                            * the correspondig 3 source-columns are droped
                        * and Z (the corresponding Z_i, Z_k and ZVEC are droped)

        Raises:
            XmError

        >>> xm=xms['GPipes']
        >>> mx=xm.MxSync()
        >>> xm.MxAdd(mx=mx)       
        >>> vAGSN=xm.dataFrames['vAGSN']
        >>> schnitt=vAGSN[vAGSN['NAME']=='LR']
        >>> schnitt=schnitt.copy()       
        >>> schnitt.loc[:,'PH'] = schnitt['PH'].astype(float).values
        >>> schnitt.loc[:,'Q'] = schnitt['Q'].astype(float).values
        >>> xm.dataFrames['schnitt']=schnitt       
        >>> print(xm._getvXXXXAsOneString(vXXXX='schnitt',filterColList=['OBJTYPE','NAME_i','NAME_k','IptIdx','nextNODE','x','PH','Q'],roundDct={'PH':1,'Q':1},index=True))
            OBJTYPE NAME_i NAME_k IptIdx nextNODE         x    PH         Q
        79     VENT     GL     G1      S       G1       0.0  40.0  118257.5
        80     VENT     GL     G1      E       G1       0.0  40.0  118257.5
        81     ROHR     G1    GKS      S      GKS       0.0  40.0    3077.8
        82     ROHR     G1    GKS      0      GKS    5000.0  39.5    3121.6
        83     ROHR     G1    GKS      1      GKS   10000.0  38.9    3166.3
        84     ROHR     G1    GKS      2      GKS   15000.0  38.4    3212.9
        85     ROHR     G1    GKS      3      GKS   20000.0  37.8    3261.5
        86     ROHR     G1    GKS      4      GKS   25000.0  37.3    3312.3
        87     ROHR     G1    GKS      5      GKS   30000.0  36.7    3365.3
        88     ROHR     G1    GKS      6      GKS   35000.0  36.2    3420.8
        89     ROHR     G1    GKS      7      GKS   40000.0  35.6    3478.9
        90     ROHR     G1    GKS      8      GKS   45000.0  35.0    3540.0
        91     ROHR     G1    GKS      9      GKS   50000.0  34.4    3604.2
        92     ROHR     G1    GKS     10      GKS   55000.0  33.8    3671.8
        93     ROHR     G1    GKS     11      GKS   60000.0  33.2    3743.2
        94     ROHR     G1    GKS     12      GKS   65000.0  32.5    3818.6
        95     ROHR     G1    GKS     13      GKS   70000.0  31.9    3898.6
        96     ROHR     G1    GKS     14      GKS   75000.0  31.2    3983.5
        97     ROHR     G1    GKS     15      GKS   80000.0  30.6    4073.9
        98     ROHR     G1    GKS     16      GKS   85000.0  29.9    4170.5
        99     ROHR     G1    GKS     17      GKS   90000.0  29.2    4273.9
        100    ROHR     G1    GKS     18      GKS   95000.0  28.5    4385.1
        101    ROHR     G1    GKS     19      GKS  100000.0  27.7    4505.0
        102    ROHR     G1    GKS     20      GKS  105000.0  27.0    4634.8
        103    ROHR     G1    GKS     21      GKS  110000.0  26.2    4776.0
        104    ROHR     G1    GKS     22      GKS  115000.0  25.4    4930.3
        105    ROHR     G1    GKS     23      GKS  120000.0  24.5    5100.1
        106    ROHR     G1    GKS     24      GKS  125000.0  23.7    5287.9
        107    ROHR     G1    GKS     25      GKS  130000.0  22.8    5497.2
        108    ROHR     G1    GKS     26      GKS  135000.0  21.9    5732.6
        109    ROHR     G1    GKS     27      GKS  140000.0  20.9    5999.9
        110    ROHR     G1    GKS     28      GKS  145000.0  19.9    6307.0
        111    ROHR     G1    GKS     29      GKS  150000.0  18.8    6665.0
        112    ROHR     G1    GKS     30      GKS  155000.0  17.7    7089.7
        113    ROHR     G1    GKS      E      GKS  160000.0  16.4    7604.8
        114    VENT    GKS    GKD      S      GKD  160000.0  16.4  118257.5
        115    VENT    GKS    GKD      E      GKD  160000.0  16.4  118257.5
        116    ROHR    GKD     G3      S       G3  160000.0  16.4    7652.5
        117    ROHR    GKD     G3      0       G3  165000.0  15.1    8353.3
        118    ROHR    GKD     G3      E       G3  170000.0  13.6    9214.7
        119    ROHR     G4     G3      S       G4  170000.0  13.6    9242.2
        120    ROHR     G4     G3      0       G4  175000.0  12.0   10534.3
        121    ROHR     G4     G3      E       G4  180000.0  10.1   12394.5
        122    VENT     GR     G4      S       GR  180000.0  10.1  118257.5
        123    VENT     GR     G4      E       GR  180000.0  10.0  118257.5
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
           
            vAGSN=self.dataFrames['vAGSN_raw']           
            vAGSN_rawCols=vAGSN.columns.tolist()
            
            rows,cols=vAGSN.shape                        
            if rows==0:                
                raise XmError("{:s}vAGSN_raw @Start: rows: {:d}".format(logStr,rows))

            ###
            heavyLog=False
            if heavyLog: ###
                logString="{0:s}vAGSN_raw: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='vAGSN_raw'))
                logger.debug(logString)
            
            vVBEL=self.dataFrames['vVBEL']
            vVBEL_rawCols=vVBEL.columns.tolist()

            vROHRVecResults=self.dataFrames['vROHRVecResults']
            vROHRVecResults_rawCols=vROHRVecResults.columns.tolist()
                        
            vAGSN=pd.merge(
                    vAGSN
                   ,vVBEL
                   ,how='left' 
                   ,left_on=['OBJTYPE','OBJID']  
                   ,right_index=True ,suffixes=('', '_y'))
            vAGSN.rename(columns={'tk_y':'tk_VBEL'},inplace=True)

            if heavyLog: ###
                self.dataFrames['dummy']=vAGSN
                logString="{0:s}vAGSN_merge: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy'))
                logger.debug(logString)
           
            df=vAGSN[pd.isnull(vAGSN['tk_VBEL']) != True].copy() # nur VBEL, die in vVBEL enthalten sind; das sollten alle sein ...
            # ... 
            if heavyLog: ###                
                dfTest=vAGSN[pd.isnull(vAGSN['tk_VBEL']) == True].copy()
                if not dfTest.empty:
                    self.dataFrames['dummy']=dfTest
                    logString="{0:s}dfTest: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy'))
                    logger.error(logString)                    
            
            # 1 Zeile pro VBEL mit S/E verdoppeln; S/E in Spalte ik_tmp
            ik = {'ik_tmp': ['S', 'E']}
            dfIk = pd.DataFrame(data=ik)
            dfIk['key_tmp'] = 0
            df['key_tmp'] = 0
            df=pd.merge(df,dfIk,on='key_tmp',how='outer')

            if heavyLog: ###
                self.dataFrames['dummy']=df
                logString="{0:s}df S E: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy'))
                logger.debug(logString)

            # ROHRE mit E loeschen (da Vecs sonst doppelt ergaenzt werden) und Vecs fuer Rohre ergaenzen
            df=df[(df.OBJTYPE != 'ROHR') | ((df.OBJTYPE == 'ROHR') & (df.ik_tmp=='S'))]           
            df=pd.merge(df,vROHRVecResults,how='left',left_on='OBJID',right_on='pk',suffixes=['','_tmp']) # Spalte IptIdx sowie weitere Spalten kommen für Rohre befuellt dazu
            # Spalte IptIdx fuer alle Objekttypen verwenden:
            df['IptIdx']=df.apply(lambda row: row.IptIdx if row.OBJTYPE=='ROHR' else row.ik_tmp,axis=1)

            vAGSNGeomCols=[]
            vAGSNGeomCols.append('IptIdx')

            # alle _tmp eliminieren
            df=df.filter(items=[col for col in df.columns.tolist() if re.search('_tmp$',col) == None])

            if heavyLog: ###
                self.dataFrames['dummy']=df
                logString="{0:s}df nach Vecs-Erg. und IptIdx-Aktualisieurng: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy'))
                logger.debug(logString)

            if 'ROHR~*~*~*~SVEC' not in df.columns.tolist():
                df=vAGSN[pd.isnull(vAGSN['tk_VBEL']) != True].copy()
            else:
                # x
                df['dx']=df.groupby(['LFDNR','OBJID','Layer'])['ROHR~*~*~*~SVEC'].shift(0)-df.groupby(['LFDNR','OBJID','Layer'])['ROHR~*~*~*~SVEC'].shift(1)
                df['dx']=df.apply(lambda row: 0 if row.OBJTYPE=='ROHR' and  pd.isnull(row.dx) else row.dx,axis=1)
                df['dx']=df.apply(lambda row: 0 if row.OBJTYPE!='ROHR' and  pd.isnull(row.dx) and row.IptIdx=='S' else row.dx,axis=1)
                df['dx']=df.apply(lambda row: 0 if row.OBJTYPE!='ROHR' and  pd.isnull(row.dx) and row.IptIdx=='E' else row.dx,axis=1)
                df['x']=df.groupby(['LFDNR','Layer'])['dx'].cumsum()                

                # x mit Laengen fuer VBEL ungl. ROHR ...
                tLnet=df.groupby(['LFDNR','Layer'])['dx'].sum()
                tLnet=tLnet.reset_index()
                tLnet.rename(columns={'dx':'tLnet_tmp'},inplace=True)
                df=pd.merge(df,tLnet,how='inner',on=['LFDNR','Layer'],suffixes=['','_tmp'])
                # ... derzeit 1% der Schnittlaenge
                df['dx_tmp']=df.apply(lambda row: row.tLnet_tmp*0.01 if row.OBJTYPE!='ROHR' and row.IptIdx=='E' else row.dx,axis=1)
                df['xVbel']=df.groupby(['LFDNR','Layer'])['dx_tmp'].cumsum()

                # alle _tmp eliminieren
                df=df.filter(items=[col for col in df.columns.tolist() if re.search('_tmp$',col) == None])

                vAGSNGeomCols.append('dx')
                vAGSNGeomCols.append('x')
                vAGSNGeomCols.append('xVbel')

                if heavyLog: ###
                    self.dataFrames['dummy']=df
                    logString="{0:s}df nach x/xVbel: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy',filterColList=vAGSN_rawCols+[
                                                                                                                                 'NAME_i','NAME_k','mx2Idx'] #Ende Sachdaten
                                                                                                                                 #I
                                                                                                                                 #K
                                                                                                                                 +['Q'] #Ende Ergebnisdaten
                                                                                                                                 +vAGSNGeomCols))
                    logger.debug(logString)

                # ErgCols identifizieren ...
                # ki
                kiColsAll=[col for col in df.columns.tolist() if re.search('^(?P<Pre>KNOT~\*~\*~\*~)(?P<Channel>[a-zA-Z_]+)(?P<Post>_i$)',col) != None]          
                if 'KNOT~*~*~*~QM_i' in kiColsAll:
                    kiColsAll.remove('KNOT~*~*~*~QM_i') 
                mos=[re.search('^(?P<Pre>KNOT~\*~\*~\*~)(?P<Channel>[a-zA-Z_]+)(?P<Post>_i$)',col) for col in kiColsAll]
                cols=[mo.group('Pre')+mo.group('Channel') for mo in mos]
                # kk
                kkColsAll=[col+'_k' for col in cols]
                # gibt es korrespondierende vecCol?!
                vecErgColsAll=['ROHR~*~*~*~'+mo.group('Channel')+'VEC' for mo in mos]
                vAGSNErgCols_src_ki=[]
                for kiCol,kkCol,col,vecCol in zip(kiColsAll,kkColsAll,cols,vecErgColsAll):
                    if vecCol in df.columns.tolist():
                        vAGSNErgCols_src_ki.append(kiCol)
                
                # ErgCols identifizieren final ...
                mos=[re.search('^(?P<Pre>KNOT~\*~\*~\*~)(?P<Channel>[a-zA-Z_]+)(?P<Post>_i$)',col) for col in vAGSNErgCols_src_ki]
                cols=[mo.group('Pre')+mo.group('Channel') for mo in mos]
                vAGSNErgCols=[mo.group('Channel') for mo in mos]
                vAGSNErgCols_src_kk=[col+'_k' for col in cols]
                vAGSNErgCols_src_vec=['ROHR~*~*~*~'+mo.group('Channel')+'VEC' for mo in mos]
                if 'ROHR~*~*~*~ZVEC' in df.columns.tolist():
                    vAGSNErgCols.append('Z')
                    vAGSNErgCols_src_ki.append('Z_i')
                    vAGSNErgCols_src_kk.append('Z_k')                    
                    vAGSNErgCols_src_vec.append('ROHR~*~*~*~ZVEC')                
                for channel in vAGSNErgCols:                   
                    df[channel]=None
                
                # ... ErgSpalte aus folgenden ErgSpalteI/ErgSpalteK/VecSpalte     
                for idx,(col,kiCol,kkCol,vecCol) in enumerate(zip(vAGSNErgCols,vAGSNErgCols_src_ki,vAGSNErgCols_src_kk,vAGSNErgCols_src_vec)):    
                    logger.debug("{:s}Schnitt-Zustandsgroesse Nr.:{:d}: col {:20s} Quellen: kiCol {:20s} kkCol {:20s} vecCol {:20s}".format(logStr,idx+1,col,kiCol,kkCol,vecCol))

                if heavyLog: ###
                    self.dataFrames['dummy']=df
                    logString="{0:s}df vor Ergspaltenbefuellung: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy',filterColList=vAGSN_rawCols+[
                                                                                                                                 'NAME_i','NAME_k','mx2Idx'] #Ende Sachdaten
                                                                                                                                 #I
                                                                                                                                 #K
                                                                                                                                 +['Q'] #Ende Ergebnisdaten
                                                                                                                                 +vAGSNGeomCols
                                                                                                                                 +vAGSNErgCols+vAGSNErgCols_src_ki+vAGSNErgCols_src_kk+vAGSNErgCols_src_vec))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                    logger.debug(logString)

                vAGSNErgRows_tgt_vecIdx=[]
                vAGSNErgRows_src_vecIdx=[]
                vAGSNErgRows_kiIdx=[]
                vAGSNErgRows_kkIdx=[]
                vAGSNErgRowsInvIdx=[]
                
                grouped = df.groupby(['LFDNR','Layer','OBJTYPE','OBJID','nrObjIdInAgsn'])        
                logger.debug("{:s}SA.".format(logStr))          
                for name, group in grouped: 

                                 LFDNR,Layer,OBJTYPE,OBJID,nrObjIdInAgsn=name
                                 si=df.loc[group.index[0],:]
                              
                                 try:
                                    if OBJTYPE == 'ROHR':                                        
                                        vAGSNErgRows_tgt_vecIdx.extend(group.index.values)
                                        if si.NAME_k == si.nextNODE:              
                                            vAGSNErgRows_src_vecIdx.extend(group.index.values)
                                        else:
                                            vAGSNErgRows_src_vecIdx.extend(group.index.values[::-1])
                                                                                                                          
                                    else:                                                                                                                      
                                        if si.NAME_k == si.nextNODE:              
                                             vAGSNErgRows_kiIdx.append(group.index[0])     
                                             vAGSNErgRows_kkIdx.append(group.index[-1])  
                                        else:
                                             vAGSNErgRows_kiIdx.append(group.index[-1])     
                                             vAGSNErgRows_kkIdx.append(group.index[0])  

                                    if si.NAME_k == si.nextNODE:              
                                         pass
                                    else:
                                         vAGSNErgRowsInvIdx.extend(group.index.values)
                   
                                 except  Exception as e:
                                    logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
                                    logger.error(logStrFinal)    
                logger.debug("{:s}SE.".format(logStr))                                              

                df.loc[vAGSNErgRows_tgt_vecIdx,vAGSNErgCols]=df.loc[vAGSNErgRows_src_vecIdx,vAGSNErgCols_src_vec].values 
                df.loc[vAGSNErgRows_kiIdx,vAGSNErgCols]=df.loc[vAGSNErgRows_kiIdx,vAGSNErgCols_src_ki].values 
                df.loc[vAGSNErgRows_kkIdx,vAGSNErgCols]=df.loc[vAGSNErgRows_kkIdx,vAGSNErgCols_src_kk].values                       
                if 'ROHR~*~*~*~QMVEC' in df.columns.tolist():                                
                    df.loc[vAGSNErgRows_tgt_vecIdx,'Q']=df.loc[vAGSNErgRows_src_vecIdx,'ROHR~*~*~*~QMVEC'].values                                                      
                df.loc[vAGSNErgRowsInvIdx,'Q']*=-1. 
                logger.debug("{:s}SZ.".format(logStr))
                               
                # die verarbeiteten Kanaele loeschen ...
                for kiCol,kkCol,vecCol in zip(vAGSNErgCols_src_ki,vAGSNErgCols_src_kk,vAGSNErgCols_src_vec):
                    df.drop([kiCol], axis=1, inplace=True)
                    df.drop([kkCol], axis=1, inplace=True)
                    df.drop([vecCol], axis=1, inplace=True)
                if 'ROHR~*~*~*~QMVEC' in df.columns.tolist():
                    df.drop(['ROHR~*~*~*~QMVEC'], axis=1, inplace=True)
                if 'ROHR~*~*~*~SVEC' in df.columns.tolist():
                    df.drop(['ROHR~*~*~*~SVEC'], axis=1, inplace=True)


                if heavyLog: ###       
                    cols1=vAGSN_rawCols+['NAME_i','NAME_k','mx2Idx']+['Q']+vAGSNGeomCols+vAGSNErgCols
                    self.dataFrames['dummy']=df
                    logString="{0:s}vAGSN-Ergebnis: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='dummy',filterColList=cols1))                                                                                                                                                                                                                                                                                                                                                                                                         
                    logger.debug(logString)
                    cols2=list(set(df.columns.tolist())-set(cols1))
                    cols2Ordered=[]
                    for col in df.columns.tolist():
                        if col in cols2:
                            cols2Ordered.append(col)
                    logString="{0:s}vAGSN-Ergebnis-weitere Spalten: {1:s}".format(logStr,self._getvXXXXAsOneString(vXXXX='vAGSN',filterColList=cols2Ordered))                                                                                                                                                                                                                                                                                                                                                                                                         
                    logger.debug(logString)

                self.dataFrames['vAGSN']=df

        except XmError as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.debug(logStrFinal) 
                                                           
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

    def __MxAddForOneDf(self,dfTarget=None,dfSource=None,multiIndexKey=None,testStr='testStr'):
        """Add MX2-Resultdata from dfSource as cols to returned dfTarget.

        Args:
            dfTarget: df with col mx2Idx
            dfSource: df with mx2Idx-corresponding index and cols (containing MX2-Resultdata) to be added
            multiIndexKey: value for 1st Index if dfTarget is Multiindexed - i.e. 'XXXX'

        Notes:
            * all cols from dfSource are added at the end of dfTarget in dfSource-sequence
            * the cols can already exist in dfTarget
            * if so, _all cols must already exist ...
            * ... the dfTarget-sequence should but must be not necessary the dfSource-sequence 
            
        Returns:
            dfTarget
            
        Raises:
            XmError
        """

        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:             
            # maybe the cols are already added in previous calls: otherwise: construct them ... 
            colsToBeAdded=dfSource.columns.tolist()
            colsInTarget=dfTarget.columns.tolist()
            colsInTargetNet=list(set(colsInTarget)-set(colsToBeAdded))
            colsInTargetNet=[col for col in colsInTarget if col in colsInTargetNet] # preserve the original col-Sequence

            logger.debug("{:s}Quellspalten: {!s:s}".format(logStr,dfSource.columns.to_list())) 
            logger.debug("{:s}Zielspalten: {!s:s}".format(logStr,dfTarget.columns.to_list())) 

            if dfSource.columns.isin(colsInTarget).all():
                logger.debug("{:s}Alle Quellspalten (bereits) in Target: {!s:s}".format(logStr,dfSource.columns.to_list()))                 
            else:
                if not dfSource.columns.isin(colsInTarget).any():
                    # no col to be added exista
                    logString="{0:s}None of the cols from dfSource exist in dfTarget: {1:s}".format(logStr,str(colsToBeAdded))
                    logger.debug(logString)
                    for col in colsToBeAdded:
                        dfTarget[col]=None                                           
                else:
                    # only some cols to be added exists?!       
                    logStringFinal="{0:s}Some but - not all! - cols from dfSource exist in dfTarget: existing: {1:s} not existing: {2:s}".format(logStr
                                                    ,str(list(set(colsInTarget) & set(colsToBeAdded)))
                                                    ,str(list(set(colsToBeAdded) - set(colsInTarget)))
                                                    )             
                    logger.error(logStringFinal) 
                    raise XmError(logStringFinal)

            dfMx2Idx=dfSource          
                     
            if multiIndexKey != None:
                ###dfMx2Idx.to_excel(testStr+'_dfMx2Idx'+'_multiIndexKey'+'.xlsx')
                ###dfTarget.loc[[multiIndexKey]].filter(items=colsInTargetNet).to_excel(testStr+'_dfTarget'+'_multiIndexKey'+'.xlsx')
                dfMerge=pd.merge(dfTarget.loc[[multiIndexKey]].filter(items=colsInTargetNet),dfMx2Idx,how='inner',left_on='mx2Idx',right_index=True)            
                #logger.debug("{0:s}dfMerge: {1:s}".format(logStr,str(dfMerge)))
                ###dfMerge.filter(items=['mx2Idx','L','NAME_i','NAME_k','Q']).to_excel(testStr+'_dfMerge'+'_multiIndexKey'+'.xlsx')
                # check alignment ...
                shapeLeft=dfTarget.loc[[multiIndexKey],colsToBeAdded].shape
                shapeRight=dfMerge[colsToBeAdded].shape
                if shapeLeft != shapeRight:
                    logStringFinal="{0:s}Alignment Mismatch: shapeLeft dfTarget: {1:s} <> shapeRight dfMerge: {2:s}".format(logStr
                                                    ,str(shapeLeft)
                                                    ,str(shapeRight)
                                                    )
                    logger.error(logStringFinal) 
                    raise XmError(logStringFinal)
                dfTarget.loc[[multiIndexKey],colsToBeAdded]=dfMerge.filter(colsToBeAdded).values    

            else:
                dfMerge=pd.merge(dfTarget.filter(items=colsInTargetNet),dfMx2Idx,how='inner',left_on='mx2Idx',right_index=True)        
                ###logger.debug("{0:s}dfMerge: {1:s}".format(logStr,str(dfMerge)))
                ###dfMerge.to_excel(testStr+'_dfMerge'+'.xlsx')
                # check alignment ...
                shapeLeft=dfTarget.loc[:,colsToBeAdded].shape
                shapeRight=dfMerge[colsToBeAdded].shape
                if shapeLeft != shapeRight:
                    logStringFinal="{0:s}Alignment Mismatch: shapeLeft dfTarget: {1:s} <> shapeRight dfMerge: {2:s}".format(logStr
                                                    ,str(shapeLeft)
                                                    ,str(shapeRight)
                                                    )
                    logger.error(logStringFinal) 
                    raise XmError(logStringFinal)
                else:
                    dfTarget.loc[:,colsToBeAdded]=dfMerge[colsToBeAdded].values
                ###if testStr=='ROHR':                    
                    ###dfTarget.filter(items=['L','KVR','NAME_i','NAME_k','ROHR~*~*~*~QMAV']).to_excel(testStr+'_dfTarget'+'_multiIndexKey'+'.xlsx')
                ###logger.debug("{0:s}dfTarget: {1:s}".format(logStr,str(dfTarget)))
                   
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            #logger.debug("{:s}Zielspalten Ergebnis: {!s:s}".format(logStr,dfTarget.columns.to_list())) 
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

            return dfTarget

def setUpFct(dto):
        """
        """

        logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try:      
            testDir=dto.globs['testDir']
            dotResolution=dto.globs['dotResolution']
            h5File=os.path.join(os.path.join(path,testDir),'OneLPipe.h5')       
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))                       
            logger.error(logStrFinal) 
                     
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  

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
        
        -q -m 0 -s "^Xm\." -t both -y yes -z no -w OneLPipe -w LocalHeatingNetwork -w GPipe -w GPipes -w TinyWDN 

        Singletests: separater MockUp-Lauf:

        -q -m 0 -t before -u yes -w DHNetwork
        
        Singletests (die auf dem vorstehenden MockUp-Lauf basieren):
        -q -m 0 -s "^Xm\." -z no -w DHNetwork

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

        parser.add_argument("-l","--logExternDefined", help="Logging (File etc.) is extern defined", action="store_true",default=False)      


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
            from PT3S import Mx
        except ImportError:
            logger.debug("{0:s}{1:s}".format("test: from PT3S import Mx: ImportError: ","trying import Mx ..."))  
            import Mx

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
                    xm=Xm(xmlFile=xmlFile,NoH5Read=True) 
                else:
                    xm=Xm(xmlFile=xmlFile)      
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
            
        

            logger.debug("{:s}singleTests suchen in Xm ...".format(logStr)) 
            dTests=dtFinder.find(Xm,globs={'testDir':args.testDir                                                                                    
                                           ,'xms':xms
                                           ,'ms':ms})

            for test in dTests:
                pass
                #logger.debug("{0:s}singleTests: {1:s}: {2:s} ...".format(logStr,'Test found',test.name)) 

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
                    mx=Mx.Mx(mx1File=mx1File,NoH5Read=True,NoMxsRead=True) # avoid doing anything than just plain Init      
                    mx.setResultsToMxsFile()
                else:
                    mx=Mx.Mx(mx1File=mx1File) 
                #Xm                     
                xmlFile=os.path.join(os.path.join('.',args.testDir),testModel+'.XML')
                if args.mockUpDetail1 in ['yes']:    
                    xm=Xm(xmlFile=xmlFile,NoH5Read=True) # avoid doing anything than just plain Init                                           
                else:
                    xm=Xm(xmlFile=xmlFile) 
                   
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



