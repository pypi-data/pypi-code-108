#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import socket  # 导入 socket 模块

s = socket.socket()         # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 8888

s.connect((host, port))

sentMsg = "我是Client"
bytes = bytes(sentMsg, "UTF-8")
s.send(bytes)
print("Client发送：", sentMsg)
receivedBytes = s.recv(1024)
print("Client收到：", str(receivedBytes, "UTF-8"))

s.close()
