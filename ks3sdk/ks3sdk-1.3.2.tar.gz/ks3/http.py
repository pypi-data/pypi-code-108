# coding:utf-8
import time
import re

try:
    import http.client as httpcli  # for Python 3
    import urllib.parse as parse
    from urllib import parse as urlparse
except ImportError:
    import httplib as httpcli # for Python 2
    import urllib as parse
    import urlparse

from ks3.auth import canonical_string, add_auth_header, url_encode, encode
from ks3.authV4 import add_auth_header as add_auth_header_v4

class CallingFormat:
    PATH = 1
    SUBDOMAIN = 2
    VANITY = 3

class AuthingFormat:
    V2 = 1
    V4 = 2

def merge_meta(headers, metadata):
    final_headers = headers.copy()
    for k in list(metadata.keys()):
        final_headers["x-kss-" + "meta-" + k] = metadata[k]

    return final_headers


def query_args_hash_to_string(query_args):    
    pairs = []
    for k, v in list(query_args.items()):
        piece = k
        if v != None:
            piece += "=%s" % parse.quote_plus(str(v).encode('utf-8'))
            # piece += "=%s" % v
        pairs.append(piece)

    return '&'.join(pairs)


def get_object_url(age, bucket="", key="", secret_access_key="", access_key_id="", query_args={}):
    expire = str(int(time.time()) + age)
    headers = {"Date": expire}
    c_string = canonical_string("GET", bucket, key, query_args, headers)    
    path = c_string.split("\n")[-1]
    
    signature = parse.quote_plus(encode(secret_access_key, c_string))
    if "?" in path:
        url = "http://kss.ksyun.com%s&Expires=%s&AccessKeyId=%s&Signature=%s" % \
            (path, expire, access_key_id, signature)
    else:
        url = "http://kss.ksyun.com%s?Expires=%s&AccessKeyId=%s&Signature=%s" % \
            (path, expire, access_key_id, signature)        
    return url


def make_request(server, port, access_key_id, access_key_secret, method, 
                 bucket="", key="", query_args=None, headers=None, data="", 
                 metadata=None, call_fmt=CallingFormat.SUBDOMAIN, is_secure=False,domain_mode=False,need_auth_header=True, timeout = 10):
    if not headers:
        headers = {}
    #if not query_args:
    #    query_args = {}
    if not metadata:
        metadata = {}

    path = ""
    if bucket and not domain_mode:
        if call_fmt == CallingFormat.SUBDOMAIN:
            server = "%s.%s" % (bucket, server)
        elif call_fmt == CallingFormat.VANITY:
            server = bucket
        elif call_fmt == CallingFormat.PATH:
            path += "/%s" % bucket

    path += "/%s" % url_encode(key)
    path = path.replace('//', '/%2F')

    if query_args:
        if isinstance(query_args, dict):
            path += "?" + query_args_hash_to_string(query_args)
        else:
            path += "?" + query_args

    host = "%s:%d" % (server, port)
    
    if (is_secure):
        connection = httpcli.HTTPSConnection(host)
    else:
        connection = httpcli.HTTPConnection(host)

    connection.timeout = timeout
    final_headers = merge_meta(headers, metadata)
    if method == "PUT" and "Content-Length" not in final_headers and not data:
        final_headers["Content-Length"] = "0"
    if method.upper() == "POST" and "Content-Length" not in final_headers and not data:
        final_headers["Content-Length"] = str(len(data))
    if need_auth_header:
        add_auth_header(access_key_id, access_key_secret, final_headers, method,
                        bucket, key, query_args)

    connection.request(method, path, data, final_headers)
    resp = connection.getresponse()
    if resp.status >= 300 and resp.status < 400 :
        loc = resp.getheader('location')
        if loc:
            reg = re.findall('http[s]?://(.*?)(:\d+)?/', loc)
            if reg:
                new_server = reg[0][0]
                loc_parse = urlparse.urlparse(loc)
                if 'Signature' in loc_parse.query:
                    connection_temp = httpcli.HTTPSConnection(new_server)
                    connection_temp.request('GET',loc_parse.path+'?'+loc_parse.query)
                    try:
                        resp_temp = connection_temp.getresponse()
                        return resp_temp
                    except Exception as err:
                        print(str(err))
                else:
                    return make_request(new_server, port, access_key_id, access_key_secret, method, bucket, key, query_args,
                                    headers, data, metadata, call_fmt, is_secure,need_auth_header=False)
    return resp

# 发送awsv4的请求
def make_request_v4(access_key_id, access_key_secret, method='', service='', region='', query_args=None, headers={}, body="", is_secure=False, timeout = 10):
    host = service + '.api.ksyun.com'

    if (is_secure):
        connection = httpcli.HTTPSConnection(host)
    else:
        connection = httpcli.HTTPConnection(host)
    connection.timeout = timeout

    path = "/"
    if query_args:
        if isinstance(query_args, dict):
            query_args = query_args_hash_to_string(query_args)
        else:
            query_args = query_args
    path += "?" + query_args

    headers = add_auth_header_v4(access_key_id, access_key_secret, region, service, host, method, query_args, body,
                                 headers)

    connection.request(method, path, body, headers)
    resp = connection.getresponse()
    return resp