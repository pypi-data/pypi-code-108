from seeq import spy
import pandas as pd 
import numpy as np
from urllib.parse import urlparse, urlunparse, unquote, parse_qs

def parse_url(url):
    unquoted_url = unquote(url)
    return urlparse(unquoted_url)

def get_workbook_worksheet_workstep_ids(url):
    parsed = parse_url(url)
    params = parse_qs(parsed.query)
    workbook_id = None
    worksheet_id = None
    workstep_id = None
    if 'workbookId' in params:
        workbook_id = params['workbookId'][0]
    if 'worksheetId' in params:
        worksheet_id = params['worksheetId'][0]
    if 'workstepId' in params:
        workstep_id = params['workstepId'][0]
    return workbook_id, worksheet_id, workstep_id

#Capsuls no Oscillation
def PushSignalsCapNoOsci(df,worksheet_url,name,capsule): 
    signal_seeq=[]
    for i in range(len(df)):
        if capsule[i]==1:
            signal_seeq.append(0)
    capsule=capsule.loc[capsule== 1]
    df_results=pd.DataFrame(signal_seeq,index=capsule.index)
    df_results.columns=[name]
    spy.push(data=df_results,workbook=worksheet_url,quiet=True)
    return df_results

#Signal no Oscillation
def PushSignalsNoOsci(df,worksheet_url,name): 
    signal_seeq=[]
    for i in range(len(df)):
        signal_seeq.append(0)
    df_results=pd.DataFrame(signal_seeq,index=df.index)
    df_results.columns=[name]
    spy.push(data=df_results,workbook=worksheet_url,quiet=True)
    return df_results

#Capsuls
def PushSignalsCap(df,mean_stiction_list,worksheet_url,name,capsule): 
    signal_seeq=[]
    max_counter=len(mean_stiction_list)/5
    counter=0
    osci_counter=1
    start=False
    stop=False
    for i in range(len(df)):
        if stop ==False and str(df.index[i])==mean_stiction_list[osci_counter+1] and capsule[i]==1:
            start=False
            osci_counter=osci_counter+5
            counter+=1
            if counter==max_counter:
                stop=True
        if stop==False and str(df.index[i])==mean_stiction_list[osci_counter] or start==True and capsule[i]==1: 
            start=True
            signal_seeq.append(round(mean_stiction_list[osci_counter+2],2))

        if start == False and capsule[i]==1:
                signal_seeq.append(0)
    capsule=capsule.loc[capsule== 1]
    df_results=pd.DataFrame(signal_seeq,index=capsule.index)
    df_results.columns=[name]
    spy.push(data=df_results,workbook=worksheet_url,quiet=True)
    return df_results

#Oscillation Signal
def PushSignalsCapOsci(df,osci_index_final_date,worksheet_url,name,capsule):   
    #------- Oscillation ---------
    signal_seeq_osci=[]
    max_counter=len(osci_index_final_date)/2
    counter=0
    osci_counter=0
    start=False
    stop=False
    for i in range(len(df)):
        if stop ==False and str(df.index[i])==osci_index_final_date[osci_counter+1] and capsule[i]==1:
            start=False
            osci_counter=osci_counter+2
            counter+=1
            if counter==max_counter:
                stop=True
        if stop==False and str(df.index[i])==osci_index_final_date[osci_counter] or start==True and capsule[i]==1: 
            start=True
            signal_seeq_osci.append(1)
        if start == False and capsule[i]==1:
                signal_seeq_osci.append(0)
    capsule=capsule.loc[capsule== 1]
    df_results_osci=pd.DataFrame(signal_seeq_osci,index=capsule.index)
    df_results_osci.columns=[name]
    spy.push(data=df_results_osci,workbook=worksheet_url,quiet=True)
    return df_results_osci

#Stiction Signal
def PushSignals(df,mean_stiction_list,worksheet_url,name):    
    signal_seeq=[]
    max_counter=len(mean_stiction_list)/5
    counter=0
    osci_counter=1
    start=False
    stop=False
    for i in range(len(df)):
        if stop ==False and str(df.index[i])==mean_stiction_list[osci_counter+1]:
            start=False
            osci_counter=osci_counter+5
            counter+=1
            if counter==max_counter:
                stop=True
        if stop==False and str(df.index[i])==mean_stiction_list[osci_counter] or start==True: 
            start=True
            signal_seeq.append(round(mean_stiction_list[osci_counter+2],2))

        if start == False:
                signal_seeq.append(0)
    df_results=pd.DataFrame(signal_seeq,index=df.index)
    df_results.columns=[name]
    spy.push(data=df_results,workbook=worksheet_url,quiet=True)
    return df_results

#Oscillation Signal
def PushSignalsOsci(df,osci_index_final_date,worksheet_url,name):   
    #------- Oscillation ---------
    signal_seeq_osci=[]
    max_counter=len(osci_index_final_date)/2
    counter=0
    osci_counter=0
    start=False
    stop=False
    for i in range(len(df)):
        if stop ==False and str(df.index[i])==osci_index_final_date[osci_counter+1]:
            start=False
            osci_counter=osci_counter+2
            counter+=1
            if counter==max_counter:
                stop=True
        if stop==False and str(df.index[i])==osci_index_final_date[osci_counter] or start==True: 
            start=True
            signal_seeq_osci.append(1)
        if start == False:
                signal_seeq_osci.append(0)
    df_results_osci=pd.DataFrame(signal_seeq_osci,index=df.index)
    df_results_osci.columns=[name]
    spy.push(data=df_results_osci,workbook=worksheet_url,quiet=True)
    return df_results_osci
