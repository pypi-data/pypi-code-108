#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/12 8:06 下午
# @Author  : lance.txl
# @Site    : 
# @File    : oss_utils.py
# @Software: PyCharm

import re
import time
import socket
import requests

import oss2
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from pprint import pprint
from urllib import request

OSS_DIR = "public/OSS_Python_API_20150707"
if not os.path.isdir(os.path.abspath(OSS_DIR)):
    OSS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/" + OSS_DIR
print(OSS_DIR)
class OssUtils:
    def __init__(self,bucketname):
        self.bucketname = bucketname
        if not os.path.isdir(OSS_DIR):
            print("Not Found {} Directly,Please Assign later by use set_ossenv".format(OSS_DIR))
        else:
            self.upload_cmd = "python2 " + OSS_DIR + "/osscmd upload {} oss://" + bucketname + "/{}"
            print(self.upload_cmd)
    def set_ossenv(self,ossdir):
        self.upload_cmd = "python2 " + ossdir + "/osscmd upload {} oss://" + self.bucketname + "/{}"
        print(self.upload_cmd)
    def upload_oss_file(self,file,filename=None,delete_file=False):
        if not filename:
            filename = file.split("/")[-1]
        cmd = self.upload_cmd.format(file,filename)
        print(cmd)
        lines = os.popen(cmd).readlines()
        pprint(lines)
        download_url = ""
        for index in range(len(lines)):
            if lines[index].startswith("Object URL"):
                download_url = lines[index].strip().split("is:")[-1].strip()
        if download_url and delete_file:
            print("upload success,remove screenshot")
            os.remove(file)
        return download_url
    def download_file(self,url,filename=None):
        if not filename:
            filename = url.split("/")[-1]
        request.urlretrieve(url,filename)
    def download_file_multithread(self,p):
        url,filename = p.split("~")
        if not filename:
            filename = url.split("/")[-1]
        request.urlretrieve(url,filename)
    def download_file_withtimeout(self,url,filename=None,timeout=10):
        socket.setdefaulttimeout(timeout)
        if not filename:
            filename = url.split("/")[-1]
        count = 0
        while count < 3:
            try:
                r = requests.get(url,timeout=timeout)
            except requests.exceptions.RequestException as e:
                print(e)
                count = count + 1
                continue
            else:
                with open(filename, "wb") as fo:
                    fo.write(r.content)
                break



if __name__ == '__main__':
    pass