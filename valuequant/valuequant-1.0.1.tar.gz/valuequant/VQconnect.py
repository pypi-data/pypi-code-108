# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

import requests
import json

vqdomain='https://valuequant.boomevolve.com/'

class VQconnect:
    def login(self,name,pswd):
        url=vqdomain+'login'
        params={'name':name,'pswd':pswd}
        try:
            res=requests.post(url=url,data=params)
            resInfo = json.loads(res.text)
            if res.status_code==200:
                self.token=resInfo['token']
                print(resInfo['msg'])
            else:
                print(resInfo['msg'])
        except:
            print("登录出错！")

    def logout(self):
        try:
            self.tokencheck()
            url = vqdomain + 'logout'
            params={}
            res = requests.post(url=url, data=params, headers={'BOOM-TOKEN': self.token})
            resInfo = json.loads(res.text)
            if res.status_code == 200:
                print(resInfo['msg'])
                del self.token
            else:
                print('注销登录失败')
        except:
            print('注销登录失败')

    def tokencheck(self):
        if hasattr(self,'token')==False:
            print("请先登录。若需注册，请登陆www.boomevolve.com。")
            raise Exception("请先登录。")

    def service(self,params):
        self.tokencheck()
        url=vqdomain+'service'
        try:
            params['params']=json.dumps(params['params'],ensure_ascii=False)
            res=requests.post(url=url,data=params,headers={'BOOM-TOKEN':self.token})
            resInfo=json.loads(res.text)
            if 'token' in resInfo.keys():
                self.token = resInfo['token']
            if res.status_code==200:
                return resInfo['res']
            else:
                print(resInfo['msg'])
                return None
        except Exception as e:
            print(e)
            print("请求错误")
            return None

    def data(self,params):
        self.tokencheck()
        url=vqdomain+'data'
        try:
            params['params'] = json.dumps(params['params'],ensure_ascii=False)
            res=requests.post(url=url,data=params,headers={'BOOM-TOKEN':self.token})
            resInfo=json.loads(res.text)
            if 'token' in resInfo.keys():
                self.token = resInfo['token']
            if res.status_code==200:
                return resInfo['res']
            else:
                print(resInfo['msg'])
                return None
        except:
            print("请求错误")
            return None

VQC=VQconnect()