# -*- coding:utf-8 -*-
"""
该脚本为客户端脚本

作用：
    将数据信息发送给服务端

参数：
    Client(HOST,PORT,BUFFER,timeout=0.55)
    其中：
        HOST,PORT,BUFFER为服务脚本所开ip,端口与缓存大小，其中ip与端口要与服务脚本一致
        timeout为客户端请求结束持续时间总长度,单位s.如果从服务器传回来的数据量较大，或者网速较慢可以适当加大该值。


例：
    >>> from cgai_socket.cgai_client import Client
    >>>
    >>> my_client = Client('192.168.1.88',24601,1024)
    >>> msg = {'a':1,'b':2,'c':3}
    >>> my_client.send(msg)

"""
from http import client
import socket
import json
import base64

class Client(object):
    def __init__(self,HOST,PORT,BUFFER,timeout=0.55):
        super(Client, self).__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(timeout)
        self.HOST = HOST
        self.PORT = PORT
        self.BUFFER = BUFFER

    def send(self,msg):
        """
        发送信息
        :param msg:
        :return:
        """
        result = None
        all_backs = b''
        try:
            self.client.connect((self.HOST, self.PORT))
            data = {'msg':msg}
            self.client.sendall(base64.b64encode(json.dumps(data).encode('utf8')) + b'#cgai')
            while True:
                back = self.client.recv(self.BUFFER)
                if len(back)>0:
                    if back[-5:] ==b'#cgai':
                        all_backs += back[:-5]
                        break
                    else:
                        all_backs += back
                else:
                    break
        except Exception as request_from_222_ERR:
            if str(request_from_222_ERR) != 'timed out':
                print(str(request_from_222_ERR))

        finally:
            all_backs = base64.b64decode(all_backs).decode('utf8')
            data = json.loads(all_backs) if all_backs else {}
            result = data.get('back',None)

            self.client.close()
        return result



