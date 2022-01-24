# coding:utf-8
try:
    import urllib.parse as parse  # for Python 3
except ImportError:
    import urllib as parse  # for Python 2

try:
    from hashlib import sha1 as sha
    from hashlib import sha256 as sha256
except ImportError:
    import sha
    sha256 = None

import hmac
import datetime

def url_encode(key):
    if not key:
        return ""
    encode_key = parse.quote_plus(key.encode('utf-8'))
    if '%20' in encode_key:
        encode_key = encode_key.replace('%20', '+')

    if '%2A' in encode_key:
        encode_key = encode_key.replace('%2A', '*')

    if '%7E' in encode_key:
        encode_key = encode_key.replace('%7E', '~')

    if '%2F' in encode_key:
        encode_key = encode_key.replace('%2F', '/')

    return encode_key


def encode_params(query_args):
    if not query_args:
        return ""
    map_args = {}
    if isinstance(query_args, dict):
        map_args = query_args
    else:
        for param in query_args.split("&"):
            kv = param.split("=", 1)
            k = kv[0]
            if len(kv) == 1:
                map_args[k] = ""
            else:
                v = kv[1]
                map_args[k] = v
    if not map_args:
        return ""
    sorted_keys = list(map_args.keys())
    sorted_keys.sort()
    buf_list = []
    for k in sorted_keys:
        v = map_args.get(k)
        if v:
            buf_list.append("%s=%s" % (k, v))
        else:
            buf_list.append("%s" % k)
    return "&".join(buf_list)

# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def getCanonicalRequest(host, method, signed_headers, amzdate, request_parameters, body=""):
    # 正规化 uri；use '/' if no path
    canonical_uri = '/'
    # 正规化 headers
    canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
    # must be URL-encoded (space=%20)
    canonical_querystring = request_parameters
    # Create payload hash (hash of the request body content). For GET
    # requests, the payload is an empty string ("").
    payload_hash = sha256(body.encode('utf-8')).hexdigest()

    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    return canonical_request

def add_auth_header(access_key_id, secret_access_key, region, service, host, method, query_args, body, headers = {}, tm=datetime.datetime.utcnow()):
    # "Host" and "x-amz-date" are always required.
    signed_headers = 'host;x-amz-date'
    if not access_key_id:
        return
    amzdate = tm.strftime('%Y%m%dT%H%M%SZ')
    if 'x-amz-date' not in headers:
        headers['x-amz-date'] = amzdate

    datestamp = tm.strftime('%Y%m%d')
    signing_key = getSignatureKey(secret_access_key, datestamp, region, service)
    # print('signing_key: ', signing_key)
    canonical_request = getCanonicalRequest(host, method, signed_headers, amzdate, encode_params(query_args), body)

    # print('canonical_request', canonical_request)
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + sha256(
        canonical_request.encode('utf-8')).hexdigest()
    # print('string_to_sign', string_to_sign)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), sha256).hexdigest()
    # print('signature: ', signature)
    headers['Authorization'] = algorithm + ' ' + 'Credential=' + access_key_id + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    # print('authorization: ', algorithm + ' ' + 'Credential=' + access_key_id + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature)
    return headers