# -*- coding:utf-8 -*-
"""

关于回调函数：
    回调函数的目的就是与客户端传来的数据进行交互，因此在自定义回调函数时:
    1.需要使用有data参数作为占位形参
    2.每个回调函数需要一个返回值，该可以为空，不为空时，当成功执行回调函数后会将该值传回给客户端，实现即时通信的效果

回调函数定义格式如下为：

    >>> def func(data,*args):
    >>>     xxxx
    >>>     return None
    其中data为从客户端传送过来的数据，这里只是一个占位参数。

    假如我们知道从客户端传送的数据是{"a":1,"b":2}，那么我们可以如此创建回调函数来使用数据：
    >>> def myfunc(data,_id,_name):
    >>>     if data:
    >>>         print("my data : ",data)
    >>>         print("a : ",data.get('a'))
    >>>         print("_id : ",_id)
    >>>         print("_name : ",_name)
    >>>         return None

使用add_callback添加回调函数：
    添加回调函数时可以传入参数，但是不需要传入data。比如
    >>> from cgai_socket.cgai_server import Server
    >>>
    >>> def myfunc(data,_id,_name):
    >>>     print(data.get('a',''))
    >>>     print(_id,_name)
    >>>
    >>> my_server = Server('192.168.1.88',24601,1024)
    >>> my_id = 12
    >>> my_name = 'CGAI'
    >>> my_server.add_callback(myfunc,args=(my_id,my_name))
    >>> my_server.listening()

    如果还有其他回调函数需要添加，可以继续使用add_callback,比如：
    >>> def func1(data):xxx return None
    >>> def func2(data):xxx return None
    >>> ...
    >>> my_server.add_callback(func1)
    >>> my_server.add_callback(func2)
    >>> ...

    注意：只有当所有回调函数添加完成后，最后执行listening


初始化创建server时添加多个回调函数
    再初始化server时，是可以直接一次性添加多个回调函数的，使用关键字参数 call_backs,
    call_backs是一个字典，它使用结构是:
    >>> {func1_name:(func1_args),func2_name:(func2_args),...}

    例：
    >>> def func1(data):xxx return None
    >>> def func2(data,_id,_name):xxx return None
    >>> def func3(data,_id1,_name2):xxx return None
    >>> call_backs = {func1:None,func2:(_id,_name),fun3:(_id1,_name2)}
    >>> my_server = Server('192.168.1.88',24601,1024,call_backs={})

"""
import os
import time
import socket
import json
import base64

class Server(object):
    def __init__(self,HOST,PORT,BUFFER,call_backs={}):
        super(Server, self).__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(150)
        self.BUFFER = BUFFER

        self.__call_backs = call_backs

    def add_callback(self,func_name,args=None):
        """
        添加回调函数
        :param func_name: 函数名称
        :param args: 函数参数，tuple类型，没有则无需输入
        :return: 
        """
        self.__call_backs[func_name] = args

    def delete_callback(self,func_name):
        """
        删除回调函数
        :param func_name: 函数名称
        :return:
        """
        self.__call_backs.pop(func_name)

    def _get_recv(self,client):
        msg = b''
        while True:
            rec = client.recv(self.BUFFER)
            if len(rec) > 0:
                if rec[-5:] == b'#cgai':
                    msg += rec[:-5]
                    break
                else:
                    msg += rec
            else:
                break
        msg = base64.b64decode(msg)
        msg = json.loads(msg.decode('utf8'))
        data = msg.get('msg')
        return data

    def listening(self):
        """
        开启服务监听
        :return:
        """
        if self.__call_backs:
            print('listening')
            while True:
                time.sleep(0.3)
                try:
                    client_sock, client_addr = self.server.accept()
                    data = self._get_recv(client_sock)
                    for func,args in self.__call_backs.items():
                        try:
                            result = func(data,*args) if args else func(data)
                            back = {'back':result}
                            # print('result:',result)
                            client_sock.sendall(base64.b64encode(json.dumps(back).encode('utf8'))+b'#cgai')
                        except Exception as func_ERR:
                            print('{}  执行失败'.format(func.__name__),str(func_ERR))

                except Exception as listening_ERR:
                    print('listening_ERR:', str(listening_ERR))
        else:
            print('请先添加回调函数,以对客户端传来的信息进行处理')