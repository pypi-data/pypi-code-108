import socket
import time
import random
import uuid
import os
import re

"""
获取主机或指定ip的电脑ip，MAC，主机名及当前时间，捣乱提取指定数量生成一个专属id
return string
"""
class Newid:
    def __init__(self,num:int,hostip=False,username=False):
        self.hostip=hostip
        self.username=username
        self.num=num
    def newfileid(self):
        if self.hostip == False:
            user=socket.gethostname()
            ip=[]
            for rep in socket.gethostbyname(user).split('.'):
                ip.append(rep)
            _hostip_="".join(ip)
        else:
            try:
                ip_and=[]
                for resp in socket.gethostbyname(self.hostip).split('.'):
                    ip_and.append(resp)
                _hostip_="".join(ip_and)
            except:
                raise ValueError(f"目标地址{self.hostip}不存在")
        if self.username == False:
            name=[]
            for rep in socket.gethostname().split('-'):
                name.append(rep)
                _username_="".join(name)
        else:
            _username_=self.username
        _MAC_=uuid.UUID(int=uuid.getnode()).hex[-12:]
        _time_=time.strftime("%Y_%m_%d_%H_%M_%S",time.gmtime())
        _random_=random.choice([i for i in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"])
        ID=[]
        for i in [_hostip_,_username_,_MAC_,_time_,_random_]:
            for ia in i:
                ID.append(ia)
        try:
            _key_=''.join(random.sample(ID,self.num))
        except:
            raise ValueError(f"num数值过大，最大可设置为：{len(_hostip_+_username_+_MAC_+_time_+_random_)}")
        return _key_
