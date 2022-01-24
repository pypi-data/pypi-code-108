'''
Created on 15. 4. 2020

@author: ppavlu
'''
import requests
import time
import datetime
import pathlib

MONTHMAP={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
          'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

def GetURLContent (URL,USERNAME,USERPWD):
    '''
    Gives back the web-response structure from the URL
    '''
    r=None
    try:
        r=requests.get(URL, auth=(USERNAME,USERPWD))
    except (IOError):
        print ("Access to network server failed: ",URL)
    return r

def GetTimeStamp():
    ts=time.time()
    return ts

def AddToLogFile(folder,log,text):
    #Create the log directory in case it does not exist
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    #write one-line entry to the logfile. If not existing, create it
    fname=folder+"\\"+log
    with open(fname,"a") as fh:
        fh.write(text+"\n")
        
def GetDateFromString(dts):
    #returns a datetime.date structure from dt string of format "Wed Apr 22 17:28:15 2020"
    if ("" in dts.split(" ")):
        dt=[]
        for t in dts.split(" "):
            if (t != ""):
                dt.append(t)
    else:
        dt=dts.split(" ")
    dtyear=int(dt[4].strip())
    dtmonthname=dt[1].strip()
    dtmonth=MONTHMAP[dtmonthname]
    dtday=int(dt[2].strip())
    datedt=datetime.date(dtyear,dtmonth,dtday)
    return datedt

def ReadLogFile(folder,log,miss,ndays):
    #read text file of value series by date into two lists of text strings
    #missing values are replaced by "miss" character
    d=None #structure for returning the file data
    fname=folder+"\\"+log
    if pathlib.Path(fname).exists():
        with open(fname,"r") as fh:
            d=[[],[]] #list of two data sets (one for date/time, one for value, all strings)
            datetoday=GetDateFromString(time.ctime(time.time()))
            if (ndays <= 0):
                anyDate=True #date does not matter
            else:
                anyDate=False #date matters
            for line in fh:
                datestr=line.split(sep=";")[0].strip()
                if not anyDate:
                    datetime=GetDateFromString(datestr)
                    delta=datetoday-datetime
                    if (delta.days <= ndays-1):
                        isDateMatch=True
                    else:
                        isDateMatch=False
                if (anyDate or isDateMatch):
                        d[0].append(datestr)
                        value=line.split(sep=";")[1].strip()
                        if value.startswith("No Access"):
                            d[1].append(miss) #missing data point
                        else:
                            d[1].append(value)
        return d
    else: #specified file does not exist
        return d

def GetValue(line):
    valueSegmentStart=line.find('value=')
    valueSegmentEnd=line.find('Code=')
    valueSegment=line[valueSegmentStart:valueSegmentEnd-1]
    #print('>>'+valueSegment+'<<')
    valStart=valueSegment.find('"')+1
    #valEnd=valueSegment.rfind('"')-2
    valEnd=len(valueSegment)
    while not valueSegment[valEnd-1].isdigit():
        valEnd=valEnd-1
    valString=valueSegment[valStart:valEnd]
    #print('>>'+valString+'<<')
    if valString.isalnum():
        value=int(valString)
    else:
        value=float(valString)
    return value

def GetData(MINISERVERREADURL, DATAID, USERNAME, USERPWD, verb):
    if verb:
        print("Reading current value for: ", DATAID)
    buildURL=MINISERVERREADURL+"io/"+DATAID
    # print(buildURL)
    result=GetURLContent(buildURL, USERNAME, USERPWD)
    response=None
    if (result != None):
        if result.ok:
            #data=GetValue(DATAID, result.text)
            #print(result.ok, result.text)
            response=(GetTimeStamp(),GetValue(result.text))
        else:
            print("Error reading data from server")
    return response

if __name__ == '__main__':
    pass