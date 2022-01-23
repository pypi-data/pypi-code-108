#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Last modified: 2018-01-04 20:16:00
'''

import copy
import io
import string
import urllib.parse
from functools import partial
from http.cookiejar import Cookie, MozillaCookieJar
from pathlib import Path
from urllib.parse import urlencode

import pycurl
import requests
from requests.cookies import MockRequest, MockResponse
from tornado import httputil
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.escape import native_str

from .base_utils import Dict, to_bytes, to_str, tqdm
from .http_utils import Aiohttp, AsyncRequest, BaseRequest, Requests, Response


class MockHeaders(httputil.HTTPHeaders):

    def get_all(self, name, default=[]):
        return super().get_list(name)


class Pycurl(BaseRequest):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = io.BytesIO()
        self.h = io.BytesIO()
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.HEADERFUNCTION, self.h.write)
        self.c.setopt(pycurl.WRITEFUNCTION, self.b.write)
        self.cookiejar = MozillaCookieJar(self.cookie)

    def __del__(self):
        self.b.close()
        self.h.close()
        self.c.close()

    def load_cookie(self, curl):
        if self.cookie:
            curl.setopt(pycurl.COOKIEFILE, self.cookie)
            curl.setopt(pycurl.COOKIEJAR, self.cookie)
            if Path(self.cookie).exists():
                self.cookiejar.load(ignore_discard=True, ignore_expires=True)
        else:
            curl.setopt(pycurl.COOKIEFILE, '')
            curl.setopt(pycurl.COOKIEJAR, '')

    def save_cookie(self, resp):
        req = MockRequest(resp.request)
        res = MockResponse(MockHeaders(resp.headers))
        self.cookiejar.extract_cookies(res, req)
        if self.cookie:
            self.cookiejar.save(ignore_discard=True, ignore_expires=True)

    def load_proxy(self, curl, proxy):
        if proxy:
            if proxy.startswith('socks4'):
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
            elif proxy.startswith('socks5'):
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            else:
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
            curl.setopt(pycurl.PROXY, proxy)
            # credentials = httputil.encode_username_password(proxy['username'], proxy['password'])
            # curl.setopt(pycurl.PROXYUSERPWD, credentials)
        else:
            curl.setopt(pycurl.PROXY, '')
            curl.unsetopt(pycurl.PROXYUSERPWD)

    def _curl_setup(self, curl, url, headers={}, cookies={}, data=[], files=[], **kwargs):
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.MAXREDIRS, 5)
        curl.setopt(pycurl.HEADER, 0)
        curl.setopt(pycurl.VERBOSE, 0)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        # curl.setopt(pycurl.AUTOREFERER, 1)
        # 导致未知的403错误 https://video.wanmeikk.me/hls/a02689e5-d0f6-4a55-a590-75119b142a21/d6MJXL_kK9bOc1cTqAs3vVOWDA6wepIKOln9hG_oIT2vMXt81bvAsSaNmOVnaXAcM2BsEd87CSN9VlFIrLZuSw==.ts
        curl.setopt(pycurl.URL, urllib.parse.quote(url, safe='#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
        curl.setopt(pycurl.TRANSFER_ENCODING, int(kwargs.get('chunked', False)))
        curl.setopt(pycurl.FOLLOWLOCATION, kwargs['allow_redirects'])
        curl.setopt(pycurl.CONNECTTIMEOUT, kwargs['timeout'])
        curl.setopt(pycurl.TIMEOUT, kwargs['timeout'])
        self.load_cookie(curl)
        self.load_proxy(curl, kwargs.get('proxy'))

        curl_options = {
            "GET": pycurl.HTTPGET,
            "POST": pycurl.POST,
            "PUT": pycurl.UPLOAD,
            "HEAD": pycurl.NOBODY,
        }
        custom_methods = set(["DELETE", "OPTIONS", "PATCH"])
        for o in curl_options.values():
            curl.setopt(o, False)
        if kwargs['method'] in curl_options:
            curl.unsetopt(pycurl.CUSTOMREQUEST)
            curl.setopt(curl_options[kwargs['method']], True)
        elif kwargs['method'] in custom_methods:
            curl.setopt(pycurl.CUSTOMREQUEST, kwargs['method'])
        else:
            raise KeyError('unknown method ' + kwargs['method'])

        if files:
            data = self.multipart(headers, data, files)
        elif isinstance(data, (dict, list, tuple)):
            data = urlencode(data)

        if kwargs['method'] in ("POST", "PATCH", "PUT"):
            request_buffer = io.BytesIO(to_bytes(data))
            curl.setopt(pycurl.READFUNCTION, request_buffer.read)
            curl.setopt(pycurl.IOCTLFUNCTION, lambda cmd: cmd == curl.IOCMD_RESTARTREAD and request_buffer.seek(0))
            if kwargs['method'] == 'POST':
                curl.setopt(pycurl.POSTFIELDSIZE, len(data))
            else:
                curl.setopt(pycurl.UPLOAD, True)
                curl.setopt(pycurl.INFILESIZE, len(data))
            '''
            fields = []
            if isinstance(data, collections.Iterable):
                for k, v in data:
                    fields.append((k, (pycurl.FORM_CONTENTS, to_str(v))))
            if isinstance(files, collections.Iterable):
                for k, v in files:
                    fields.append((k, (pycurl.FORM_FILE, to_str(v[1].name))))
            curl.setopt(pycurl.HTTPPOST, fields)
            curl.setopt(pycurl.POSTFIELDS, data)
            '''

        for key in ['Expect', 'Pragma']:
            headers.setdefault(key, '')

        header_list = [f'{to_str(k)}:{to_str(v)}' for k, v in headers.items()]
        curl.setopt(pycurl.HTTPHEADER, header_list)

        if cookies:
            cookie_str = ';'.join([f"{to_str(k)}={urllib.parse.quote(to_str(v), safe=string.printable)}" for k, v in cookies.items()])
            curl.setopt(pycurl.COOKIE, cookie_str)

        if kwargs['progress']:
            curl.setopt(pycurl.NOPROGRESS, 0)
            self._pbar = tqdm(unit='B', unit_scale=True)

            def update(a, b, c, d):
                download_total, downloaded, upload_total, uploaded = int(a), int(b), int(c), int(d)
                if kwargs['method'] == 'GET' and (self._pbar.total is None or download_total >= self._pbar.total):
                    self._pbar.update(downloaded, download_total)
                elif (self._pbar.total is None or upload_total >= self._pbar.total):
                    self._pbar.update(uploaded, upload_total)

            curl.setopt(pycurl.PROGRESSFUNCTION, update)
        else:
            curl.setopt(pycurl.NOPROGRESS, 1)
            curl.setopt(pycurl.PROGRESSFUNCTION, lambda: None)

    def _parse_cookies(self, curl):
        cookie_list = curl.getinfo_raw(pycurl.INFO_COOKIELIST)
        for item in cookie_list:
            domain, domain_specified, path, path_specified, expires, name, value = item.decode().split("\t")
            cookie = Cookie(0, name, value, None, False, domain,
                            domain_specified.lower() == "true",
                            domain.startswith("."), path,
                            path_specified.lower() == "true",
                            False, expires, False, None, None, {})
            self.cookiejar.set_cookie(cookie)

    def _parse_headers(self, text):
        reason = 'OK'
        headers = httputil.HTTPHeaders()
        for header_line in text.split(b'\r\n'):
            header_line = native_str(header_line.decode('latin1'))
            header_line = header_line.rstrip()
            if header_line.startswith("HTTP/"):
                headers.clear()
                try:
                    _, _, reason = httputil.parse_response_start_line(header_line)
                    header_line = "X-Http-Reason: %s" % reason
                except httputil.HTTPInputError:
                    continue
            if header_line:
                headers.parse_line(header_line)
        return reason, headers

    def _download(self, url, kwargs, fp, lock, start, end):
        with lock:
            kwargs = copy.copy(kwargs)
            kwargs['headers']['Range'] = f'bytes={start}-{end}'
            pbar = tqdm(total=end - start + 1, unit='B', unit_scale=True, desc=f'{start}')
            fp.seek(start)
            self._curl_setup(self.c, url, **kwargs)
            self.c.setopt(pycurl.WRITEFUNCTION, fp.write)
            self.c.setopt(pycurl.NOPROGRESS, 0)
            self.c.setopt(pycurl.PROGRESSFUNCTION, lambda a, b, c, d: pbar.update(int(b), int(a)))
            self.c.perform()
            pbar.close()
            return self.c.getinfo(pycurl.HTTP_CODE) == 206

    def _request(self, url, **kwargs):
        url, kwargs = self._prepare(url, kwargs)
        self._curl_setup(self.c, url, **kwargs)
        cookies = requests.utils.dict_from_cookiejar(self.cookiejar)
        cookies.update(kwargs['cookies'])
        request = Dict(
            url=url,
            headers=kwargs.get('headers'),
            data=kwargs.get('data'),
            cookies=cookies,
        )

        self.c.perform()

        reason, headers = self._parse_headers(self.h.getvalue())
        request_time = self.c.getinfo(pycurl.TOTAL_TIME)
        body = self.b.getvalue()
        code = self.c.getinfo(pycurl.HTTP_CODE)
        url = self.c.getinfo(pycurl.EFFECTIVE_URL)

        self.b.seek(0)
        self.b.truncate()
        self.h.seek(0)
        self.h.truncate()

        resp = Response(
            url=url,
            code=code,
            reason=reason,
            headers=headers,
            body=Response._decompress(headers, body),
            request=request,
            time=request_time,
        )
        self._finish(kwargs)
        self.save_cookie(resp)
        return resp


class TornadoClient(AsyncRequest, Pycurl):

    def __init__(self, max_clients=100, **kwargs):
        ''' This cannot handle 301/302 redirection cookies
        '''
        super().__init__(**kwargs)
        self.http = CurlAsyncHTTPClient(max_clients=max_clients)

    async def _request(self, url, **kwargs):
        url, kwargs = self._prepare(url, kwargs)
        curl_callback = partial(self._curl_setup, url=url, **kwargs)
        resp = await self.http.fetch(url, raise_error=False, prepare_curl_callback=curl_callback)
        resp = Response(resp)
        self._finish(kwargs)
        self.save_cookie(resp)
        return resp


def Request(lib='requests', **kwargs):
    module = {
        'pycurl': Pycurl,
        'tornado': TornadoClient,
        'requests': Requests,
        'aiohttp': Aiohttp,
    }
    return module[lib](**kwargs)
