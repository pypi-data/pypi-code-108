import urllib3
import urllib3.exceptions as exceptions
from .others import *
def testInternet():
    http1=urllib3.PoolManager()
    try:
        r=http1.request("GET",'https://apple.com',timeout=3,retries=False)
    except:
        return -1
    return 0

def http(url:str,Method:str="GET",Header:dict={},Timeout:int=2000,ToJson:bool=True,Body:str="",Decode:bool=True):
    # status:  -1: 无网络  -2: 超时  -3: 域名不存在  -4: 其它问题, 主要是代理服务器设置错误(服务器上无此问题)
    # status:  1: 不是 UTF-8 编码, text 返回空字符串  2: 不是json格式(在toJSON=True的前提下)
    # status:  3: 对方网站不支持https, 但是却使用了https连接, 这种情况会自动切换为http连接, 若此次status不为0, 返回该status, 若为0, 返回3
    backup=[url,Method,Header,Timeout,ToJson,Body,Decode]
    http1=urllib3.PoolManager()
    r=0
    if(ToJson):
        text={}
    else:
        text=""
    try:
        r=http1.request(Method,url,headers=Header,timeout=Timeout/1000,body=Body,retries=False)
    except exceptions.NewConnectionError as err: # 无网络/域名不存在
        if(testInternet()==-1): # 无网络
            return {'status':-1,'code':0,'text':text,'header':{},'extra':''}
        return {'status':-3,'code':0,'text':text,'header':{},'extra':''}
    except exceptions.ConnectTimeoutError as err: # 无网络/超时
        if(testInternet()==-1): # 无网络
            return {'status':-1,'code':0,'text':text,'header':{},'extra':''}
        # 超时
        try:
            r=http1.request(Method,url,headers=Header,timeout=3*Timeout/1000,body=Body,retries=False)
        except:
            return {'status':-2,'code':0,'text':text,'header':{},'extra':''}
    except exceptions.ReadTimeoutError as err: # 无网络/超时
        if(testInternet()==-1): # 无网络
            return {'status':-1,'code':0,'text':text,'header':{},'extra':''}
        # 超时
        try:
            r=http1.request(Method,url,headers=Header,timeout=3*Timeout/1000,body=Body,retries=False)
        except:
            return {'status':-2,'code':0,'text':text,'header':{},'extra':''}
    except exceptions.SSLError: # 对方网站不支持https, 但是却使用了https连接
        n=backup[0].find('https://')
        newUrl='http://'+backup[0][n+8:]
        tryAgain=http(newUrl,Method=backup[1],Header=backup[2],Timeout=backup[3],ToJson=backup[4],BODY=backup[5],Decode=backup[6])
        if(tryAgain['status']==0):
            tryAgain['status']=3
        return tryAgain
    except Exception as err: # 其它错误，主要为代理服务器设置错误，服务器上一般无此问题
        return {'status':-4,'code':0,'text':text,'header':{},'extra':''}
    # 以下是正常情况
    resp={}
    resp['status']=0
    resp['code']=r.status
    respHeader=dict(r.headers)
    resp['header']=respHeader
    resp['extra']=''
    text=r.data
    if(not Decode):
        resp['text']=text
        return resp
    deco=''
    try:
        deco=text.decode('utf-8')
    except:
        resp['text']=''
        resp['status']=1
        resp['extra']=text
        return resp
    if(not ToJson):
        resp['text']=deco
        return resp
    js={}
    try:
        js=toJson(deco)
    except:
        resp['text']={}
        resp['status']=2
        resp['extra']=deco
        return resp
    resp['text']=js
    return resp

