#############################################################
#
#  Author: Sebastian Maurice, PhD
#  Copyright by Sebastian Maurice 2018
#  All rights reserved.
#  Email: Sebastian.maurice@otics.ca
#
#############################################################

import json, urllib
import requests
import csv
import os
import imp
import re
import urllib.request
import asyncio
import validators
from urllib.parse import urljoin
from urllib.parse import urlsplit
from aiohttp import ClientSession
import async_timeout



def formaturl(maindata,host,microserviceid,prehost,port):

    if len(microserviceid)>0:    
      mainurl=prehost + "://" + host +  ":" + str(port) +"/" + microserviceid + "/?hyperpredict=" + maindata
    else:
      mainurl=prehost + "://" + host + ":" + str(port) +"/?hyperpredict=" + maindata
        
    return mainurl
    
async def tcp_echo_client(message, loop,host,port,usereverseproxy,microserviceid):

    hostarr=host.split(":")
    hbuf=hostarr[0]
   # print(hbuf)
    hbuf=hbuf.lower()
    domain=''
    if hbuf=='https':
       domain=host[8:]
    else:
       domain=host[7:]
    host=domain  

    if usereverseproxy:
        geturl=formaturl(message,host,microserviceid,hbuf,port) #host contains http:// or https://
        message="GET %s\n\n" % geturl 

    reader, writer = await asyncio.open_connection(host, port, loop=loop)
    try:
      mystr=str.encode(message)
      writer.write(mystr)
      datam=''
      while True:
        data = await reader.read(1024)
      #  print(data)
        datam=datam+data.decode("utf-8")
       # print(datam)
        if not data:
           break
        
        await writer.drain()
   #   print(datam)  
      prediction=("%s" % (datam))
      writer.close()
    except Exception as e:
      print(e)
      return e
    
    return prediction

def hyperpredictions(maadstoken,pkey,theinputdata,host,port,usereverseproxy=0,microserviceid='',username='',password='',company='',email=''):
    if '_nlpclassify' not in pkey:
      theinputdata=theinputdata.replace(",",":")
    else:  
      buf2 = re.sub('[^a-zA-Z0-9 \n\.]', '', theinputdata)
      buf2=buf2.replace("\n", "").strip()
      buf2=buf2.replace("\r", "").strip()
      theinputdata=buf2

    if usereverseproxy:
       theinputdata=urllib.parse.quote(theinputdata)
  
    value="%s,[%s],%s" % (pkey,theinputdata,maadstoken)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_client(value, loop,host,port,usereverseproxy,microserviceid))
    loop.close()
    return val
#########################################################
#######################VIPER Functions

def formaturlviper(maindata,host,microserviceid,prehost,port):

    if len(microserviceid)>0:    
      mainurl=prehost + "://" + host +  ":" + str(port) +"/" + microserviceid + "/" + maindata
    else:
      mainurl=prehost + "://" + host + ":" + str(port) +"/" + maindata
        
    return mainurl


async def fetch(client,url):
    async with client.get(url) as resp:
        assert resp.status == 200
        return await resp.text()

#############################VIPER API CALLS ################    
async def tcp_echo_clientviper(message, loop,host,port,microserviceid,timeout=180):

    hostarr=host.split(":")
    hbuf=hostarr[0]
   # print(hbuf)
    hbuf=hbuf.lower()
    domain=''
    if hbuf=='https':
       domain=host[8:]
    else:
       domain=host[7:]
    host=domain  

    #if len(microserviceid)>0:
    geturl=formaturlviper(message,host,microserviceid,hbuf,port) #host contains http:// or https://
    message="%s" % geturl 
    try:
     with async_timeout.timeout(timeout):
      async with ClientSession() as session:
        html = await fetch(session,message)
        await session.close()
        return html
    except Exception as e:
     pass   


def viperstats(vipertoken,host,port=-999,brokerhost='',brokerport=-999,microserviceid=''):

    if len(vipertoken)==0 or len(host)==0 or port==-999:
       return "Please enter vipertoken,host and port"

    value="viperstats?vipertoken="+vipertoken + "&brokerhost="+brokerhost+"&brokerport="+str(brokerport)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val


def viperlisttopics(vipertoken,host,port=-999,brokerhost='',brokerport=-999,microserviceid=''):

    if len(vipertoken)==0 or len(host)==0 or port==-999:
       return "Please enter vipertoken,host and port"
    
    value="listtopics?vipertoken="+vipertoken + "&brokerhost="+brokerhost+"&brokerport="+str(brokerport)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipersubscribeconsumer(vipertoken,host,port,topic,companyname,contactname,contactemail,location,description,brokerhost='',brokerport=-999,groupid='',microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(companyname)==0 or len(contactname)==0 or len(contactemail)==0 or len(location)==0 or len(description)==0:
         return "Please enter host,port,vipertoken,topic, companyname,contactname,contactemail,location and description"
        
    value=("subscribeconsumer?vipertoken="+vipertoken + "&topic="+topic + "&companyname=" + companyname + "&contactname="+contactname +
           "&contactemail="+contactemail + "&location="+location+"&description="+description+ "&brokerhost="+brokerhost + "&brokerport="+str(brokerport) + "&groupid=" + groupid)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperdeletetopics(vipertoken,host,port,topic,microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0:
         return "Please enter host,port,vipertoken,topic"
        
    value=("deletetopics?vipertoken="+vipertoken + "&topic="+topic)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperunsubscribeconsumer(vipertoken,host,port,consumerid,brokerhost='',brokerport=-999,microserviceid=''):

    if len(vipertoken)==0 or len(consumerid)==0 or len(host)==0:
         return "Please enter vipertoken,consumerid,host and port"
        
    value=("unsubscribeconsumer?vipertoken="+vipertoken + "&consumerid="+consumerid + "&brokerhost="+brokerhost +"&brokerport="+str(brokerport))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperproducetotopic(vipertoken,host,port,topic,producerid,enabletls=0,delay=100,inputdata='',maadsalgokey='',maadstoken='',getoptimal=0,externalprediction='',brokerhost='',brokerport=-999,microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(producerid)==0:
         return "Please enter host,port,vipertoken,topic, producerid"
        
    value=("producetotopic?vipertoken="+vipertoken + "&topic="+topic + "&producerid=" + producerid + "&getoptimal="+str(getoptimal) +
          "&delay=" + str(delay) +  "&enabletls="+str(enabletls)+ "&externalprediction="+externalprediction + "&inputdata="+inputdata + "&maadsalgokey="+maadsalgokey +"&maadstoken="+maadstoken + "&brokerhost="+brokerhost+"&brokerport="+str(brokerport)) 
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperconsumefromtopic(vipertoken,host,port,topic,consumerid,companyname,partition=-1,enabletls=0,delay=100,offset=0,brokerhost='',brokerport=-999,microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(consumerid)==0 or len(companyname)==0:
         return "Please enter host,port,vipertoken,topic, consumerid,companyname"
        
    value=("consumefromtopic?vipertoken="+vipertoken + "&topic="+topic + "&consumerid=" + consumerid + "&offset="+str(offset) +
      "&partition=" + str(partition) +  "&delay=" + str(delay) +  "&enabletls=" + str(enabletls) + "&brokerhost="+brokerhost + "&brokerport="+str(brokerport)+"&companyname="+companyname)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperhpdepredict(vipertoken,host,port,consumefrom,produceto,companyname,consumerid,producerid,hpdehost,inputdata,algokey='',partition=-1,offset=-1,
                     enabletls=1,delay=1000,hpdeport=-999,brokerhost='',brokerport=9092,
                     timeout=120,usedeploy=0,microserviceid=''):

    #reads the fieldnames and gets latest data from each stream (or fieldname)
    
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(inputdata)==0 or len(produceto)==0 or len(companyname)==0 or len(consumerid)==0
                 or len(producerid)==0 or len(hpdehost)==0 or hpdeport==-999):
         return "Please enter host,port,vipertoken,consumefrom,inputdata,produceto,companyname,consumerid,producerid,hpdehost,hpdeport"
        
    value=("viperhpdepredict?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto=" + produceto + "&consumerid="+consumerid +
           "&delay=" + str(delay) + "&inputdata="+ inputdata + "&algokey="+algokey + "&partition="+str(partition)+"&offset="+str(offset)+ "&enabletls=" + str(enabletls) + "&producerid="+producerid + "&usedeploy=" +str(usedeploy) +"&companyname="+companyname + "&hpdehost=" +hpdehost +"&hpdeport="+str(hpdeport)+"&brokerhost="+brokerhost + "&brokerport="+str(brokerport))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperhpdeoptimize(vipertoken,host,port,consumefrom,produceto,companyname,consumerid,producerid,hpdehost,partition=-1,offset=-1,
                      enabletls=1,delay=1000,hpdeport=-999,usedeploy=0,
                      ismin=1,constraints='best',stretchbounds=20,constrainttype=1,epsilon=10,brokerhost='',brokerport=9092,
                      timeout=120,microserviceid=''):

    #reads the fieldnames and gets latest data from each stream (or fieldname)
    
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(produceto)==0 or len(companyname)==0 or len(consumerid)==0
                 or len(producerid)==0 or len(hpdehost)==0 or hpdeport==-999):
         return "Please enter host,port,vipertoken,consumefrom,produceto,companyname,consumerid,producerid,hpdehost,hpdeport"
        
    value=("viperhpdeoptimize?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto=" + produceto + "&consumerid="+consumerid +
         "&delay=" + str(delay) + "&enabletls=" + str(enabletls) + "&producerid="+producerid + "&companyname="+companyname +
         "&partition="+str(partition)+"&offset="+str(offset)+
         "&hpdehost=" +hpdehost +"&hpdeport="+str(hpdeport))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid,timeout))
    return val

def viperhpdetraining(vipertoken,host,port,consumefrom,produceto,companyname,consumerid,producerid,hpdehost,viperconfigfile,
                      enabletls=1,partition=-1,deploy=0,modelruns=50,hpdeport=-999,offset=-1,islogistic=0,
                      brokerhost='',brokerport=9092,timeout=120,microserviceid=''):

    #reads the fieldnames and gets latest data from each stream (or fieldname)
    
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(produceto)==0 or len(companyname)==0 or len(consumerid)==0
                 or len(producerid)==0 or len(hpdehost)==0 or hpdeport==-999):
         return "Please enter host,port,vipertoken,consumefrom,produceto,companyname,consumerid,producerid,hpdehost,hpdeport"
        
    value=("viperhpdetraining?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto=" + produceto + "&consumerid="+consumerid +
           "&producerid="+producerid + "&companyname="+companyname + "&partition="+str(partition)+"&modelruns="+str(modelruns) +"&hpdehost=" +hpdehost +
           "&hpdeport="+str(hpdeport)+"&brokerhost="+brokerhost+ "&offset="+str(offset) + "&viperconfigfile="+viperconfigfile +
           "&brokerport="+str(brokerport)+"&enabletls="+str(enabletls) +"&deploy="+str(deploy) + "&islogistic=" + str(islogistic) + "&timeout="+str(timeout) )
    loop = asyncio.get_event_loop()
#    future = asyncio.wait_for(loop.run_in_executor(None, time.sleep, 2), timeout)
#    try:
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid,timeout))
 #   except Exception as e:
  #     print(e) 
    return val

def viperanomalytrain(vipertoken,host,port,consumefrom,produceto,producepeergroupto,produceridpeergroup,consumeridproduceto,
                      streamstoanalyse,
                      companyname,consumerid,producerid,flags,hpdehost,viperconfigfile,
                      enabletls=1,partition=-1,hpdeport=-999,
                      brokerhost='',brokerport=9092,delay=1000,timeout=120,microserviceid=''):

    #reads the fieldnames and gets latest data from each stream (or fieldname)
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(produceto)==0 or len(companyname)==0 or len(consumerid)==0
                 or len(producerid)==0 or len(hpdehost)==0 or hpdeport==-999 or len(streamstoanalyse)==0 or len(producepeergroupto)==0
                 or len(produceridpeergroup)==0 or len(consumeridproduceto)==0 or len(flags)==0 or len(viperconfigfile)==0):
         return "Please enter host,port,vipertoken,consumefrom,produceto,companyname,streamstoanalyse,consumeridproduceto,flags,consumerid,producepeergroupto,produceridpeergroup,producerid,hpdehost,hpdeport"
    
    value=("viperanomalytrain?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto=" + produceto + "&consumerid="+consumerid +
           "&producepeergroupto=" + producepeergroupto + "&produceridpeergroup=" + produceridpeergroup + "&consumeridproduceto="+consumeridproduceto +
           "&streamstoanalyse="+streamstoanalyse + "&flags="+flags + "&delay=" +str(delay) + "&timeout=" + str(timeout) +
           "&producerid="+producerid + "&companyname="+companyname + "&partition="+str(partition) +"&hpdehost=" +hpdehost +
           "&hpdeport="+str(hpdeport)+"&brokerhost="+brokerhost + "&viperconfigfile="+viperconfigfile +
           "&brokerport="+str(brokerport)+"&enabletls="+str(enabletls))
    loop = asyncio.get_event_loop()
#    future = asyncio.wait_for(loop.run_in_executor(None, time.sleep, 2), timeout)
#    try:
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid,timeout))
 #   except Exception as e:
  #     print(e) 
    return val

#http://192.168.0.13:8000/viperanomalypredict?consumefrom=anomalypeergroup&produceto=anomalydataresults&consumeinputstream=joined-viper-test11
#&produceinputstreamtest=inputstreamdata&produceridinputstreamtest=ProducerId-l6hVEHUATxLrhSPT3aeVztPpr035oc&
#streamstoanalyse=viperdependentvariable,viperindependentvariable1,viperindependentvariable2&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&companyname=OTICS test&
#consumerid=ConsumerId-irbcZ5iGigW51bVD2Z1K0E2WsN9RuV&consumeridinputstream=ConsumerId-lehi50iuYXd1asafvQYyOd1b4Okrqa&
#producerid=ProducerId-haubDasU6pt8a6nyZ2BQAl1rXblm-p&enabletls=1&delay=10000&partition=-1&hpdehost=http://192.168.0.13&hpdeport=8001&viperconfigfile=viper.env&
#flags=riskscore=.8~complete=and~type=or,topic=viperdependentvariable,topictype=numeric,sc>1500~type=and,topic=viperindependentvariable1,topictype=numeric,v1<100,sc>200~type=or,topic=accountname3,topictype=string,stringcontains=1,v2=Failed Record^Failed Record^test record,sc>120~type=or,topic=viperindependentvariable2,topictype=numeric,v1<100,sc>2000

def viperanomalypredict(vipertoken,host,port,consumefrom,produceto,consumeinputstream,produceinputstreamtest,produceridinputstreamtest,
                      streamstoanalyse,consumeridinputstream,
                      companyname,consumerid,producerid,flags,hpdehost,viperconfigfile,
                      enabletls=1,partition=-1,hpdeport=-999,
                      brokerhost='',brokerport=9092,delay=1000,timeout=120,microserviceid=''):

    #reads the fieldnames and gets latest data from each stream (or fieldname)
    
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(produceto)==0 or len(companyname)==0 or len(consumerid)==0
                 or len(producerid)==0 or len(hpdehost)==0 or hpdeport==-999 or len(streamstoanalyse)==0 or len(produceinputstreamtest)==0
                 or len(produceridinputstreamtest)==0 or len(consumeridinputstream)==0 or len(flags)==0 or len(viperconfigfile)==0):
         return "Please enter host,port,vipertoken,consumefrom,produceto,companyname,streamstoanalyse,produceinputstreamtest,produceridinputstreamtest,consumeridinputstream,flags,consumerid,producerid,hpdehost,hpdeport"
        
    value=("viperanomalypredict?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto=" + produceto + "&consumerid="+consumerid +
           "&produceinputstreamtest="+produceinputstreamtest + "&produceridinputstreamtest="+produceridinputstreamtest + "&consumeridinputstream="+consumeridinputstream+
           "&streamstoanalyse="+streamstoanalyse + "&flags="+flags + "&delay=" +str(delay) + "&timeout=" + str(timeout) +
           "&producerid="+producerid + "&companyname="+companyname + "&partition="+str(partition) +"&hpdehost=" +hpdehost +
           "&hpdeport="+str(hpdeport)+"&brokerhost="+brokerhost + "&viperconfigfile="+viperconfigfile + "&consumeinputstream="+consumeinputstream+
           "&brokerport="+str(brokerport)+"&enabletls="+str(enabletls))
    loop = asyncio.get_event_loop()
#    future = asyncio.wait_for(loop.run_in_executor(None, time.sleep, 2), timeout)
#    try:
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid,timeout))
 #   except Exception as e:
  #     print(e) 
    return val

def viperproducetotopicstream(vipertoken,host,port,topic,producerid,offset,maxrows=0,enabletls=0,delay=100,brokerhost='',brokerport=-999,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(producerid)==0):
         return "Please enter host,port,vipertoken,topic,producerid"
        
    value=("producetotopicstream?vipertoken="+vipertoken + "&topicname="+topic + "&delay=" + str(delay) + "&maxrows=" +str(maxrows) + "&enabletls="+str(enabletls) +"&brokerhost="+brokerhost + "&brokerport="+str(brokerport) + "&producerid="+producerid + "&offset="+str(offset))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipercreatetrainingdata(vipertoken,host,port,consumefrom,produceto,dependentvariable,independentvariables,
                            consumerid,producerid,companyname,partition=-1,enabletls=0,delay=100,brokerhost='',brokerport=-999,microserviceid=''):

    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(consumefrom)==0 or len(produceto)==0 or len(dependentvariable)==0 or
        len(independentvariables)==0 or len(companyname)==0 or len(consumerid)==0 or len(producerid)==0):
         return "Please enter host,port,vipertoken,consumefrom,produceto,companyname,consumerid,producerid"
        
    value=("createtrainingdata?vipertoken="+vipertoken + "&consumefrom="+consumefrom + "&produceto="+produceto +
           "&dependentvariable="+dependentvariable+"&independentvariables="+independentvariables +
           "&delay=" + str(delay) + "&enabletls=" + str(enabletls) + "&partition="+str(partition)+"&consumerid="+consumerid + "&producerid="+producerid+"&companyname="+companyname + "&brokerhost="+brokerhost + "&brokerport="+str(brokerport))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipercreatetopic(vipertoken,host,port,topic,companyname,contactname,contactemail,location,description,enabletls=0,brokerhost='',brokerport=-999,numpartitions=1,replication=1,microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(companyname)==0 or len(contactname)==0 or len(contactemail)==0 or len(location)==0 or len(description)==0:
         return "Please enter host,port,vipertoken,topic, companyname,contactname,contactemail,location and description"
        
    value=("createtopics?vipertoken="+vipertoken + "&topic="+topic + "&companyname=" + companyname + "&contactname="+contactname +
           "&contactemail="+contactemail + "&location="+location+"&description="+description+ "&enabletls="+str(enabletls) + "&numpartitions="+str(numpartitions)+
           "&replicationfactor="+str(replication) + "&brokerhost="+brokerhost + "&brokerport=" + str(brokerport) )
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperconsumefromstreamtopic(vipertoken,host,port,topic,consumerid,companyname,partition=-1,enabletls=0,delay=100,offset=0,brokerhost='',brokerport=-999,microserviceid=''):

    if len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0 or len(consumerid)==0 or len(companyname)==0:
         return "Please enter host,port,vipertoken,topic, consumerid,companyname"
        
    value=("consumefromstreamtopic?vipertoken="+vipertoken + "&topic="+topic + "&consumerid=" + consumerid + "&offset="+str(offset) +
        "&partition=" + str(partition) + "&delay=" + str(delay) + "&enabletls=" + str(enabletls) + "&brokerhost="+brokerhost + "&brokerport="+str(brokerport)+ "&companyname="+companyname)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val


def vipercreatejointopicstreams(vipertoken,host,port,topic,topicstojoin,companyname,contactname,contactemail,description,
                                location,enabletls=0,brokerhost='',brokerport=-999,replication=1,numpartitions=1,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(contactname)==0 or len(contactemail)==0 or len(description)==0 or
        len(location)==0 ):
         return "Please enter host,port,vipertoken,contactname,contactemail,companyname,description,location"
        
    value=("createjointopicstreams?vipertoken="+vipertoken + "&topicname="+topic + "&topicstojoin="+topicstojoin +
           "&companyname="+companyname+"&contactname="+contactname +"&contactemail="+contactemail+"&brokerhost="+brokerhost+"&brokerport="+str(brokerport)+
           "&enabletls=" + str(enabletls) + "&description="+description + "&location="+location+"&replicationfactor="+str(replication)+"&numpartitions="+str(numpartitions))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipercreateconsumergroup(vipertoken,host,port,topic,groupname,companyname,contactname,contactemail,description,
                                location,enabletls=1,brokerhost='',brokerport=-999,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(contactname)==0 or len(contactemail)==0 or len(description)==0 or
        len(location)==0 or len(groupname)==0):
         return "Please enter host,port,vipertoken,contactname,contactemail,companyname,description,location,groupname"
        
    value=("createconsumergroup?vipertoken="+vipertoken + "&topic="+topic + "&groupname="+groupname +
           "&companyname="+companyname+"&contactname="+contactname +"&contactemail="+contactemail+ "&enabletls="+str(enabletls)+
           "&description="+description + "&location="+location+"&brokerhost="+brokerhost+"&brokerport="+str(brokerport))
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperconsumergroupconsumefromtopic(vipertoken,host,port,topic,consumerid,groupid,companyname,partition=-1,enabletls=1,delay=1000,offset=-1,brokerhost='',brokerport=-999,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(companyname)==0 or len(consumerid)==0 or len(groupid)==0):
         return "Please enter host,port,vipertoken,consumerid,companyname,groupid"
        
    value=("consumergroupconsumefromtopic?vipertoken="+vipertoken + "&topic="+topic + "&consumerid="+consumerid +
        "&partition=" + str(partition) +  "&delay=" + str(delay) + "&enabletls=" + str(enabletls) + "&brokerhost="+brokerhost+"&brokerport="+str(brokerport) +"&offset="+str(offset) +"&companyname="+companyname+"&groupid="+groupid)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipermodifyconsumerdetails(vipertoken,host,port,topic,companyname,consumerid,contactname='',contactemail='',location='',brokerhost='',brokerport=9092,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(companyname)==0 or len(consumerid)==0 ):
         return "Please enter host,port,vipertoken,consumerid,companyname,consumerid"
        
    value=("modifyconsumerdetails?vipertoken="+vipertoken + "&topic="+topic + "&consumerid="+consumerid +"&brokerhost="+brokerhost+"&brokerport="+str(brokerport)
            +"&companyname="+companyname+"&contactname="+contactname+"&contactemail="+contactemail+"&location="+location)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipermodifytopicdetails(vipertoken,host,port,topic,companyname,isgroup=0,contactname='',contactemail='',location='',brokerhost='',brokerport=9092,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(companyname)==0 or len(topic)==0):
         return "Please enter host,port,topic,vipertoken,consumerid,companyname"
        
    value=("modifytopicdetails?vipertoken="+vipertoken + "&topic="+topic +"&brokerhost="+brokerhost+"&brokerport="+str(brokerport)
          + "&isgroup=" + str(isgroup)  +"&companyname="+companyname+"&contactname="+contactname+"&contactemail="+contactemail+"&location="+location)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperactivatetopic(vipertoken,host,port,topic,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0  ):
         return "Please enter host,port,vipertoken,topic"
        
    value=("activatetopic?vipertoken="+vipertoken + "&topic="+topic )
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def viperdeactivatetopic(vipertoken,host,port,topic,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(topic)==0  ):
         return "Please enter host,port,vipertoken,topic"
        
    value=("deactivatetopic?vipertoken="+vipertoken + "&topic="+topic )
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipergroupactivate(vipertoken,host,port,groupname,groupid,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(groupname)==0   or len(groupid)==0 ):
         return "Please enter host,port,vipertoken,groupname,groupid"
        
    value=("activategroup?vipertoken="+vipertoken + "&groupname="+groupname +"&groupid="+groupid)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

def vipergroupdeactivate(vipertoken,host,port,groupname,groupid,microserviceid=''):
    if (len(host)==0 or len(vipertoken)==0 or port==-999 or len(groupname)==0   or len(groupid)==0 ):
         return "Please enter host,port,vipertoken,groupname,groupid"
        
    value=("deactivategroup?vipertoken="+vipertoken + "&groupname="+groupname +"&groupid="+groupid)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clientviper(value, loop,host,port,microserviceid))
    return val

#val = viperstats('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000)
#print(val)

#val = viperlisttopics('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000)
#print(val)


#val=vipergroupdeactivate('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'stream-group',
                       #'GroupId-GBFXtNW7z325Pq56AMlU4Lh9HedQwV')

#val=vipergroupactivate('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'stream-group',
 #                      'GroupId-GBFXtNW7z325Pq56AMlU4Lh9HedQwV')
#http://localhost:8000/activategroup?groupname=demouser_r6w1_csv-demouser_r1w3_csv-Min11&groupid=GroupId-GBFXtNW7z325Pq56AMlU4Lh9HedQwV&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#val=viperdeactivatetopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'kafka-test11')

#http://localhost:8000/deactivatetopic?topic=kafka-test11&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0
#val=viperactivatetopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'kafka-test11')
#http://localhost:8000/activatetopic?topic=kafka-test11&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

# vipermodifytopicdetails(vipertoken,host,port,topic,companyname,contactname='',contactemail='',location='',brokerhost='',brokerport=9092,microserviceid=''):
   
#val=vipermodifytopicdetails('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'kafka-test11','OTICS')
#print(val)
#http://localhost:8000/modifytopicdetails?topic=kafka-test11&companyname=OTICS 2&brokerport=1000&brokerhost=localhost&location=Canada&contactemail=sebastian.maurice@gmail.com&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0


#val=vipermodifyconsumerdetails('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'kafka-test11','OTICS',
 #                            'ConsumerId--OSSaepBXTLnehbqJ1aWlFuFCybX-2')


#http://localhost:8000/modifyconsumerdetails?topic=kafka-test11&companyname=OTICS 2&brokerport=1000&consumerid=
#ConsumerId--OSSaepBXTLnehbqJ1aWlFuFCybX-2&brokerhost=localhost&location=Canada&contactemail=sebastian.maurice@otics.ca&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#viperconsumergroupconsumefromtopic(vipertoken,host,port,topic,consumerid,groupid,companyname,offset=0,brokerhost='',brokerport=-999,microserviceid=''):
    
#val=viperconsumergroupconsumefromtopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'demouser_r6w1_csv-demouser_r1w3_csv-Min11',
 #                            'ConsumerId-HY0Du9QohdgHKgiRFEacYNmPsAdQuy','GroupId-GBFXtNW7z325Pq56AMlU4Lh9HedQwV','OTICS')

#print(val)
#val=vipercreateconsumergroup('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'demouser_r6w1_csv-demouser_r1w3_csv-Min11',
 #                            'stream-group 7','OTICS','Sebastian Maurice','sebastian.maurice@otics.ca','test group','Toronto','',-999)
#print(val)
#http://localhost:8000/consumergroupconsumefromtopic?topic=demouser_r6w1_csv-demouser_r1w3_csv-Min11&consumerid=
#ConsumerId-HY0Du9QohdgHKgiRFEacYNmPsAdQuy&protocol=tcp&offset=0&companyname=OTICS&vipertoken=
#hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&groupid=GroupId-GBFXtNW7z325Pq56AMlU4Lh9HedQwV

#http://localhost:8000/createconsumergroup?topic=demouser_r6w1_csv-demouser_r1w3_csv-Min11&groupname=stream-group 5&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&numpartitions=1&replicationfactor=1&
#companyname=OTICS test&contactname=sebastian maurice&
#contactemail=sebastian.maurice@otics.ca&description=This algorithm has optimal values for the topic&location=Toronto Ontario
#val=vipercreatejointopicstreams('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'joined-streamsmain10',
 #                               'dependentvariable,independentvariable1,independentvariable2,independentvariable3,independentvariable4,independentvariable5',\
  #                              'OTICS','Sebastian Maurice','sebastian.maurice@otics.ca','stream topics','Toronot','',-999,1,1)
#print(val)
#http://localhost:8000/createjointopicstreams?topicname=joined-streamsmain4&topicstojoin=dependentvariable,independentvariable1,independentvariable2,
#independentvariable3,independentvariable4,independentvariable5&companyname=OTICS advanced analytics&contactname=Sebastian Maurice&
#contactemail=sebastian.maurice@otics.ca&description=streamed topic&location=Toronto&replicationfactor=1&numpartitions=1&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#val=viperconsumefromstreamtopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'joined-streamsmain4',
 #                               'ConsumerId-y9PHKDxbMRCu5U5eX0CPbEVto7Mc7C','OTICS',0)
#print(val)
#http://localhost:8000/consumefromstreamtopic?topic=joined-streamsmain4&consumerid=ConsumerId-y9PHKDxbMRCu5U5eX0CPbEVto7Mc7C&offset=0&
#protocol=tcp&companyname=OTICS&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#vipercreatetopic(vipertoken,host,port,topic,companyname,contactname,contactemail,location,description,brokerhost='',brokerport=-999,numpartitions=1,replication=1,microserviceid=''):

#val=vipercreatetopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'python-topic2','OTICS',
 #                          'sebastian maurice','sebastian.maurice@otics.ca','Toronto','test subscription','',-999,1,1)

#print(val)

#http://localhost:8000/createtopics?topic=hpde-optimal2&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&
#numpartitions=1&replicationfactor=1&companyname=OTICS test&contactname=sebastian maurice&contactemail=sebastian.maurice@otics.ca&
#description=This holds the estimated parameter from HPDE for Real-time machine learning&location=Toronto Ontario


#val=vipercreatetrainingdata('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'joined-streamsmain4',
                            #  'training-datamain5','dependentvariable','independentvariable1,independentvariable2,independentvariable3,independentvariable4,independentvariable5','ConsumerId-y9PHKDxbMRCu5U5eX0CPbEVto7Mc7C','ProducerId-SqsojxPxXXtV4fcs-bSQsAZXDZV238',0,'OTICS')
#print(val)

#http://localhost:8000/createtrainingdata?consumefrom=joined-streamsmain4&produceto=training-datamain5&vipertoken=
#hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&dependentvariable=dependentvariable&
#independentvariables=independentvariable1,independentvariable2,independentvariable3,independentvariable4,
#independentvariable5&offset=5&companyname=OTICS test&consumerid=ConsumerId-y9PHKDxbMRCu5U5eX0CPbEVto7Mc7C&
#producerid=ProducerId-SqsojxPxXXtV4fcs-bSQsAZXDZV238

#val=viperproducetotopicstream('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'joined-streamsmain4',
                             # 'ProducerId-qKBZL9pfE6Vlu258nLd4nrIMw4ABDj',0)
#print(val)

#http://localhost:8000/producetotopicstream?topicname=joined-streamsmain4&producerid=ProducerId-qKBZL9pfE6Vlu258nLd4nrIMw4ABDj&offset=0&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#val=viperhpdetraining('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'training-datamain5',
 #                       'hpde-estimated-params3','OTICS','ConsumerId-gRy5mXjfEVYIyULprtyYE4RoCKcWUW','ProducerId-E2VObYiLwQ1szos42zjASD3K9YIZYP',
  #                      'http://localhost',8001,0,0,'localhost')

#http://localhost:8000/viperhpdetraining?consumefrom=training-datamain5&produceto=hpde-estimated-params3&timeout=120&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&offset=0&companyname=OTICS &brokerhost=localhost&brokerport=9092&
#consumerid=ConsumerId-gRy5mXjfEVYIyULprtyYE4RoCKcWUW&producerid=ProducerId-E2VObYiLwQ1szos42zjASD3K9YIZYP&hpdehost=http://localhost&hpdeport=8001

#val=viperhpdeoptimize('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'hpde-estimated-params3',
 #                       'hpde-predictions2','OTICS','ConsumerId-ArNNhxsy68wtQgOPE2p-JwpOELWVtg','ProducerId-mD6eZwVEPZZnHeAqwejgejDrg7WiQk',
  #                      'http://localhost',8001)

#http://localhost:8000/viperhpdeoptimize?consumefrom=hpde-estimated-params3&produceto=hpde-optimal2&timeout=120&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&companyname=OTICS &brokerhost=localhost&
#brokerport=9092&consumerid=ConsumerId-ArNNhxsy68wtQgOPE2p-JwpOELWVtg&producerid=ProducerId-6oSI2nINLgWFx2DkOcaJAfVr8LDJMD&
#hpdehost=http://localhost&hpdeport=8001


#val=viperhpdepredict('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'hpde-estimated-params3',
                       # 'hpde-predictions2','OTICS','ConsumerId-ArNNhxsy68wtQgOPE2p-JwpOELWVtg','ProducerId-mD6eZwVEPZZnHeAqwejgejDrg7WiQk',
                        #'http://localhost',8001,'',-999,120,0)
#print(val)

#http://localhost:8000/viperhpdepredict?consumefrom=hpde-estimated-params3&produceto=hpde-predictions2&timeout=120&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&companyname=OTICS &brokerhost=localhost&brokerport=9092&
#consumerid=ConsumerId-ArNNhxsy68wtQgOPE2p-JwpOELWVtg&producerid=ProducerId-mD6eZwVEPZZnHeAqwejgejDrg7WiQk&hpdehost=http://localhost&hpdeport=8001

#http://localhost:8000/viperhpdepredict?consumefrom=hpde-estimated-params3&produceto=hpde-predictions2&timeout=120&
#vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&companyname=OTICS &brokerhost=localhost&
#brokerport=9092&consumerid=ConsumerId-ArNNhxsy68wtQgOPE2p-JwpOELWVtg&producerid=ProducerId-mD6eZwVEPZZnHeAqwejgejDrg7WiQk&
#hpdehost=http://localhost&hpdeport=8001
#val=viperconsumefromtopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'demouser_r6w1_csv-demouser_r1w3_csv-Min11',
                     #   'ConsumerId-HY0Du9QohdgHKgiRFEacYNmPsAdQuy',"OTICS")

#print(val)
#http://localhost:8000/consumefromtopic?topic=demouser_r6w1_csv-demouser_r1w3_csv-Min11&consumerid=ConsumerId-HY0Du9QohdgHKgiRFEacYNmPsAdQuy&
#offset=4&protocol=tcp&companyname=OTICS&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#val=viperproducetotopic('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'demouser_r6w1_csv-demouser_r1w3_csv-Min11',
 #                       'ProducerId-V0FZEmkBj6rkyUbArgDSRH3uxapItJ',"",
  #                      'gAAAAABeXTRS0-qksslIbPqWUG1KXTdMmOAnSBe-JhrNUKhoSJ1I05zizDwilL4vKRBvq2ZaEAi2_RMG_YaVJ5g7bgqSRc0HyUhUSGj46ZbfpllR09K1zNhN65Zs0tOGLO_KBxeadrxGLWgeLvtHoHrEAyfF_ju-pg==',1)
#print(val)
#val=viperunsubscribeconsumer('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'ConsumerId-4UINvAP5dNRPACshoqktQn9rNtISvb','',-999)
#print(val)
#val=vipersubscribeconsumer('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000,'training-data','OTICS',
#                           'sebastian maurice','sebastian.maurice@otics.ca','Toronto','test subscription','',-999,'')
#print(val)
#http://localhost:8000/producetotopic?topic=demouser_r6w1_csv-demouser_r1w3_csv-Min11&producerid=ProducerId-V0FZEmkBj6rkyUbArgDSRH3uxapItJ&
#getoptimal=1&externalprediction=this is cool3mmmmm mmnnkllmlm;&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&
#maadstoken=gAAAAABeXTRS0-qksslIbPqWUG1KXTdMmOAnSBe-JhrNUKhoSJ1I05zizDwilL4vKRBvq2ZaEAi2_RMG_YaVJ5g7bgqSRc0HyUhUSGj46ZbfpllR09K1zNhN65Zs0tOGLO_KBxeadrxGLWgeLvtHoHrEAyfF_ju-pg==

#http://localhost:8000/unsubscribeconsumer?consumerid=ConsumerId-Eoa1ZHVORmmoaFpqqgUx0u1d8pNJX5
#&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0

#http://localhost:8000/createtopics?topic=training-data&vipertoken=hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0&
#numpartitions=1&replicationfactor=1&companyname=OTICS test&contactname=sebastian maurice&contactemail=sebastian.maurice@otics.ca&
#description=This algorithm has optimal values for the topic&location=Toronto Ontario

#val=viperlisttopics('hivmg1TMR1zS1ZHVqF4s83Zq1rDtsZKh9pEULHnLR0BXPlaPEMZBEAyC7TY0','http://localhost',8000)
#print(val)
#######################################################################################


#getpicklezip('demouser','demouser0828','OTICS','sebastian.maurice@otics.ml','demouser_acnstocksdatatest_csv','http://www.otics.ca/maadsweb','c:/maads')
