#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import pycurl
from enum import IntEnum


__author__ = 'James Iter'
__date__ = '2021/4/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2021 by James Iter.'


class Downloader(object):

    def __init__(self, **kwargs):
        self.url = kwargs.get('url', None)
        self.dir = kwargs.get('dir', '/tmp')
        self.filename = kwargs.get('filename', None)
        self.overwrite = kwargs.get('overwrite', False)
        # absolute path
        self.abs_path = kwargs.get('abs_path', None)
        self.pc = pycurl.Curl()
        self.progress = kwargs.get('progress', None)
        self.debugger = kwargs.get('debugger', None)
        self.user_agent = kwargs.get('user_agent', 'JDownloader/1.0')
        self.ca_info = kwargs.get('ca_info', None)
        self.proxy_type = kwargs.get('proxy_type', None)
        self.proxy_gate = kwargs.get('proxy_gate', None)
        self.proxy_port = kwargs.get('proxy_port', None)
        self.proxy_user = kwargs.get('proxy_user', None)
        self.proxy_password = kwargs.get('proxy_password', None)
        self.proxy_ssl_verify_host = kwargs.get('proxy_ssl_verify_host', 0)
        self.proxy_ssl_verify_peer = kwargs.get('proxy_ssl_verify_host', 0)
        self.last_update_time = 0

    def prepare(self):
        if self.filename is None:
            if isinstance(self.url, bytes):
                self.url = self.url.decode()

            self.filename = self.url.split('?')[0].split('/')[-1].strip()

        if self.abs_path is None:
            self.abs_path = '/'.join([self.dir, self.filename])

        if not os.path.exists(self.dir):
            os.makedirs(self.dir, 0o0755)

    def set_opts(self):
        # https://curl.haxx.se/libcurl/c/curl_easy_setopt.html
        self.pc.setopt(pycurl.URL, self.url)
        self.pc.setopt(pycurl.FOLLOWLOCATION, 1)
        self.pc.setopt(pycurl.MAXREDIRS, 5)
        self.pc.setopt(pycurl.CONNECTTIMEOUT, 5)
        self.pc.setopt(pycurl.AUTOREFERER, 1)
        self.pc.setopt(pycurl.VERBOSE, 1)
        self.pc.setopt(pycurl.NOPROGRESS, 1)
        self.pc.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.pc.setopt(pycurl.SSL_VERIFYHOST, 0)

        if self.progress is not None:
            self.pc.setopt(pycurl.NOPROGRESS, 0)
            if sys.version_info >= (3, 8):
                self.pc.setopt(pycurl.XFERINFOFUNCTION, self.progress)
            else:
                self.pc.setopt(pycurl.PROGRESSFUNCTION, self.progress)

        if self.debugger is not None:
            self.pc.setopt(pycurl.DEBUGFUNCTION, self.debugger)

        if not self.overwrite and os.path.exists(self.abs_path):
            fd = open(self.abs_path, "ab")
            self.pc.setopt(pycurl.RESUME_FROM, os.path.getsize(self.abs_path))
        else:
            fd = open(self.abs_path, "wb")

        if self.ca_info is not None:
            self.pc.setopt(pycurl.CAINFO, self.ca_info)

        if isinstance(self.user_agent, str):
            self.pc.setopt(pycurl.USERAGENT, self.user_agent)

        if isinstance(self.proxy_gate, str) and \
                self.proxy_type in [item.value for item in DownloaderProxyType.__members__.values()]:
            # Ref: https://curl.se/libcurl/c/CURLOPT_PROXY.html
            self.pc.setopt(pycurl.PROXY, self.proxy_gate)
            self.pc.setopt(pycurl.PROXYTYPE, self.proxy_type)
            self.pc.setopt(pycurl.PROXY_SSL_VERIFYHOST, self.proxy_ssl_verify_host)
            self.pc.setopt(pycurl.PROXY_SSL_VERIFYPEER, self.proxy_ssl_verify_peer)

            # cURL 会自动根据 PROXYTYPE 填入默认端口。如 HTTPS 为 443，socket 为 1080。
            if isinstance(self.proxy_port, int):
                self.pc.setopt(pycurl.PROXYPORT, self.proxy_port)

            if isinstance(self.proxy_user, str) and isinstance(self.proxy_password, str):
                assert self.proxy_user.__len__() > 0
                assert self.proxy_password.__len__() > 0

                self.pc.setopt(pycurl.PROXYUSERPWD, f"{self.proxy_user}:{self.proxy_password}")

        self.pc.setopt(pycurl.WRITEDATA, fd)

    def perform(self):
        self.prepare()
        self.set_opts()
        self.pc.perform()


class DownloaderProxyType(IntEnum):
    """
    Ref: https://curl.se/libcurl/c/CURLOPT_PROXYTYPE.html
    """
    HTTP = 0
    HTTP_1_0 = 1
    HTTPS = 2
    SOCKS4 = 4
    SOCKS4A = 6
    SOCKS5 = 5
    SOCKS5_HOSTNAME = 7

