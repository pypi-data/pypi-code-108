# -*- coding: utf-8 -*-

import os
import hmac
import socket
import time
import json
import mimetypes
import functools
import hashlib
from urllib.parse import urlparse, urlencode
from base64 import urlsafe_b64encode
from tornado import gen, httpclient
from retry_class import RetryPolicy, CallWithRetryAsync
from tornado.httpclient import HTTPError


import requests

"""
Usage:
cow = Cow(ACCESS_KEY, SECRET_KEY)
b = cow.get_bucket(BUCKET)
b.put('a')
b.stat('a')
b.delete('a')
b.copy('a', 'c')
b.move('a', 'c')
"""




class QiniuRetryPolicy(RetryPolicy):
    """Define a retry policy that is adapted to the Amazon S3 service.
    Retries will only be attempted for HTTP 500-level errors, or if there
    was a basic network failure of some kind. By default, a request
    against S3 will be retried three times, with retries starting after
    at least 1/2 second, and exponentially backing off from there to a
    maximum of 10 seconds.
    """

    def __init__(self, max_tries=3, timeout=30, min_delay=.5, max_delay=10):
        RetryPolicy.__init__(self, max_tries=max_tries, timeout=timeout, min_delay=min_delay, max_delay=max_delay,
                             check_exception=RetryPolicy.AlwaysRetryOnException,
                             check_result=self._ShouldRetry)

    def _ShouldRetry(self, response):
        """Retry on:
          1. HTTP error codes 500 (Internal Server Error) and 503 (Service
             Unavailable).
          2. Tornado HTTP error code 599, which typically indicates some kind
             of general network failure of some kind.
          3. Socket-related errors.
        """
        if response.error:
            # Check for socket errors.

            if type(response.error) == socket.error or type(response.error) == socket.gaierror:
                return True

            # Check for HTTP errors.
            if isinstance(response.error, HTTPError):
                code = response.error.code
                if code in (500, 503, 599):
                    return True

        return False



class CowException(Exception):
    def __init__(self, url, status_code, content):
        self.url = url
        self.status_code = status_code
        self.content = content
        Exception.__init__(self, content)



def signing(secret_key, data):
    return urlsafe_b64encode(
        hmac.new(secret_key, data, hashlib.sha1).digest()
    )

def requests_error_handler(func):
    @functools.wraps(func)
    def deco(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as e:
            req = e.args[0]
            raise CowException(
                    req.url, req.status_code, req.content
                )
    return deco


class UploadToken(object):
    def __init__(self, access_key, secret_key, scope, ttl=3600, ops=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.scope = scope  # buket:filename
        self.ttl = ttl
        self._token = None
        self.generated_at = int(time.time())
        self.ops = ops      # 额外处理策略（预转换/持久换处理/视频裁图/音视频分片）

    @property
    def token(self):
        if int(time.time()) - self.generated_at > self.ttl - 60:
            # 还有一分钟也认为过期了， make new token
            self._token = None

        if not self._token:
            self._token = self._make_token()

        return self._token

    def _make_token(self):
        self.generated_at = int(time.time())
        info = {
            'scope': self.scope,
            'deadline': self.generated_at + self.ttl
        }

        if self.ops:
            info.update(self.ops)

        info = urlsafe_b64encode(json.dumps(info))
        token = signing(self.secret_key, info)
        return '%s:%s:%s' % (self.access_key, token, info)


class AccessToken(object):
    def __init__(self, access_key, secret_key, url, params=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.url = url
        self.params = params

        self.token = self.build_token()

    def build_token(self):
        uri = urlparse(self.url)
        token = uri.path
        if uri.query:
            token = '%s?%s' % (token, uri.query)
        token = '%s\n' % token
        if self.params:
            if isinstance(self.params, str):
                token += self.params
            else:
                token += urlencode(self.params)
        return '%s:%s' % (self.access_key, signing(self.secret_key, token))



class Cow(object):
    def __init__(self, **kwargs):
        self.up_host = kwargs["up_host"]
        self.rs_host = kwargs["rs_host"]
        self.rsf_host = kwargs["rsf_host"]
        self.access_key = kwargs["access_key"]
        self.secret_key = kwargs["secret_key"]

        self.retry_policy = kwargs.get("retry_policy", QiniuRetryPolicy())
        self.upload_tokens = {}

        self.stat = functools.partial(self._stat_rm_handler, 'stat')
        self.delete = functools.partial(self._stat_rm_handler, 'delete')
        self.copy = functools.partial(self._cp_mv_handler, 'copy')
        self.move = functools.partial(self._cp_mv_handler, 'move')

        # self.ops = {}

    def get_bucket(self, bucket):
        """对一个bucket的文件进行操作，
        推荐使用此方法得到一个bucket对象,
        然后对此bucket的操作就只用传递文件名即可
        """
        return Bucket(self, bucket)

    def generate_access_token(self, url, params=None):
        return AccessToken(self.access_key, self.secret_key, url, params=params).token


    def generate_upload_token(self, scope, ttl=3600, ops=None):
        """上传文件的uploadToken"""
        # if scope not in self.upload_tokens:     #　TODO 注意，同一个文件第一次生成后，token在进程内永久保留一个小时，如果在这个时间内上传同一个文件，获得的token是一样的，导致某些操作不能生效，请在获取后清掉这个self.upload_tokens[scope]
        #     self.upload_tokens[scope] = UploadToken(self.access_key, self.secret_key, scope, ttl=ttl, ops=self.ops)
        # return self.upload_tokens[scope].token

        # self.upload_tokens[scope] = UploadToken(self.access_key, self.secret_key, scope, ttl=ttl, ops=ops)
        # return self.upload_tokens[scope].token
        return UploadToken(self.access_key, self.secret_key, scope, ttl=ttl, ops=ops).token

    def build_requests_headers(self, token):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'QBox %s' % token
        }

    @gen.coroutine
    @requests_error_handler
    def api_call(self, url, params=None):
        token = self.generate_access_token(url, params=params)
        res = yield gen.Task(CallWithRetryAsync, self.retry_policy, self._post, url, headers=self.build_requests_headers(token), params=params)
        if res.code == 200:
            raise gen.Return(res.body)
        else:
            raise gen.Return(None)

    @gen.coroutine
    def list_buckets(self):
        """列出所有的buckets"""
        url = '%s/buckets' % self.rs_host
        result = yield self.api_call(url)
        raise gen.Return(result)

    def drop_bucket(self, bucket):
        """删除整个bucket"""
        url = '%s/drop/%s' % (self.rs_host, bucket)
        result = yield self.api_call(url)
        raise gen.Return(result)

    def list_files(self, bucket, marker=None, limit=None, prefix=None):
        """列出bucket中的文件"""
        query = ['bucket=%s' % bucket]
        if marker:
            query.append('marker=%s' % marker)
        if limit:
            query.append('limit=%s' % limit)
        if prefix:
            query.append('prefix=%s' % prefix)
        url = '%s/list?%s' % (self.rsf_host, '&'.join(query))
        result = yield self.api_call(url)
        raise gen.Return(result)

    @gen.coroutine
    @requests_error_handler
    def put(self, scope, data, filename=None, keep_name=True, override=True, content_type=None):
        """
        上传文件
        :param scope: bucket name
        :param filename: file name
        :param data: file data
        :param keep_name: if True, use file name, otherwise use the file data's md5 value
        :param override: if True, override the same key file.
        :return:
        """

        if not data:
            with open(filename, 'rb', encoding='utf-8') as f:
                data = f.read()

        if keep_name and filename:
            upload_name = filename
        else:
            upload_name = hashlib.md5(data).hexdigest()
            _, ext = os.path.splitext(filename)
            upload_name += ext


        if override:
            token = self.generate_upload_token('%s:%s' % (scope, upload_name))
        else:
            token = self.generate_upload_token(scope)

        files = {'file': data}
        action = '/rs-put/%s' % urlsafe_b64encode(
            '%s:%s' % (scope, upload_name)
        )
        if content_type:
            action += '/mimeType/%s' % urlsafe_b64encode(content_type)

        data = {
            'auth': token,
            'action': action,
        }

        a = requests.Request(url='%s/upload' % self.up_host, files=files, data=data)
        prepare = a.prepare()
        content_type = prepare.headers.get('Content-Type')

        res = yield gen.Task(CallWithRetryAsync, self.retry_policy, self._upload, prepare.body, content_type)
        raise gen.Return(res)

    @gen.coroutine
    def _upload(self, body, content_type):

        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        http = httpclient.AsyncHTTPClient()
        response = yield http.fetch('%s/upload' % self.up_host,
                                    method='POST', body=body,
                                    headers={"Content-Type": content_type},
                                    connect_timeout=600,
                                    request_timeout=600)
        raise gen.Return(response)

    @gen.coroutine
    def _post(self, url, headers, params):

        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        http = httpclient.AsyncHTTPClient()
        response = yield http.fetch(url,
                                    headers=headers,
                                    method='POST', body=params or "")
        raise gen.Return(response)

    def _cp_mv_handler(self, action, args):
        src_bucket, src_filename, des_bucket, des_filename = args
        url = '%s/%s/%s/%s' % (
            self.rs_host,
            action,
            urlsafe_b64encode('%s:%s' % (src_bucket, src_filename)),
            urlsafe_b64encode('%s:%s' % (des_bucket, des_filename)),
        )
        return self.api_call(url)


    def _stat_rm_handler(self, action, bucket, filename):
        url = '%s/%s/%s' % (
            self.rs_host, action, urlsafe_b64encode('%s:%s' % (bucket, filename))
        )
        return self.api_call(url)

class Bucket(object):
    def __init__(self, cow, bucket):
        self.cow = cow
        self.bucket = bucket

    def put(self, filename, data=None, keep_name=False, override=True, content_type=None):
        return self.cow.put(self.bucket, filename, data=data, keep_name=keep_name, override=override, content_type=content_type)

    def stat(self, filename):
        return self.cow.stat(self.bucket, filename)

    def delete(self, filename):
        return self.cow.delete(self.bucket, filename)

    def copy(self, *args):
        return self.cow.copy(self._build_cp_mv_args(*args))

    def move(self, *args):
        return self.cow.move(self._build_cp_mv_args(*args))

    def list_files(self, marker=None, limit=None, prefix=None):
        return self.cow.list_files(self.bucket, marker=marker, limit=limit, prefix=prefix)

    def _build_cp_mv_args(self, *args):
        return [self.bucket, args[0], self.bucket, args[1]]



class AdvanceUploadToken(UploadToken):
    def __init__(self, access_key, secret_key, info):
        self.access_key = access_key
        self.secret_key = secret_key
        self.info = info
        self._token = None

    @property
    def token(self):
        self.generated_at = int(time.time())
        info = urlsafe_b64encode(json.dumps(self.info))
        token = signing(self.secret_key, info)
        return '%s:%s:%s' % (self.access_key, token, info)