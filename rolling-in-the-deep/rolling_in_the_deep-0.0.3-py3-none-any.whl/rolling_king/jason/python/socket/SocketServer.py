#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import socket  # 导入 socket 模块

s = socket.socket()  # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 8888  # 设置端口
s.bind((host, port))  # 绑定主机与端口

s.listen(5)  # 等待客户端连接
print("开始监听Socket...")
while True:
    socketObj, addr = s.accept()  # 接受客户端连接
    print("Addr = ", addr)
    serverRecvBytes = socketObj.recv(1024)
    print("Server端收到：", str(serverRecvBytes, "UTF-8"))
    socketObj.send(bytes("Socket响应。", "UTF-8"))
    print("Server端发送: ", "Socket响应。")
    socketObj.close()  # 关闭连接


