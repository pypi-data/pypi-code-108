# -*- coding: utf-8 -*-
import urllib3
import base64
import json
import re
import random
import string
# import rsa
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

# product_id为产品ID，对应中性化安卓传屏接收端
# customerId为客户ID，对应TV客户
# public_key为公钥，对应TV客户的公钥
# !!!重要提醒：ID及公钥请勿对外泄露
# 2021.11.03 使用内网环境，以上信息对应 中性化安卓传屏接收端，李少敏自测
public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCpd+tGoHdUpcK4r26A1pAEvJfW
/57sZAWdcweqLsck1q6VHy7dlPWTAdLI1OSJr2sevsNEHPAAIqDoC2XKDN6rAy49
OJzeKTMIYMBFsy4TAuUz9WD/VuL6PMlVcPdMmPU4ebj4zQBXMxLjNG1U3LrQ90UR
PlApvAcU5u/eUjZewwIDAQAB
-----END PUBLIC KEY-----"""
product_id = "32d666d1-f63a-462d-995f-82415b497f24"
customer_id = "277b73c3-8000-4d70-b3d9-90dc4c878576"
net_url = "https://excshare.com"
range_api = "/api/v1/user/authunits/actions/import-range-with-key"
array_api = "/api/v1/user/authunits/actions/import-array-with-key"


# 生成长度为len的随机字符
def GenerateKey(len):
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, len))
    return ran_str


# 判断是否是无间隔符的MAC地址
def IsNoIntervalMac(mac):
    if re.match(r"^\s*([0-9A-F]{12})\s*$", mac):
        return True
    return False


# BASE64编码指定字符串
def Base64Str(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


# RSA加密指定字符串
# def RsaStr(data, public_key_str):
#     pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_str)
#     crypto = rsa.encrypt(data.encode("utf-8"), pub_key)
#     crypto1 = base64.b64encode(crypto)
#     return crypto1.decode("utf-8")


# RSA加密指定字符串
def RsaStr2(data, public_key_str):
    pub_key = RSA.importKey(public_key_str)
    cipher = PKCS1_cipher.new(pub_key)
    rsa_text = base64.b64encode(cipher.encrypt(bytes(data.encode("utf-8"))))
    return rsa_text.decode("utf-8")


# 加密指定字符串，加密方式：AES-128-CBC，填充方式：zeropadding
def AesCbcEncrypt(data, key, iv):
    def pad(s): return s + (16 - len(s) % 16) * chr(0)
    data = pad(data)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encryptedbytes = cipher.encrypt(data.encode('utf-8'))
    # 加密后得到的是bytes类型的数据
    encodestrs = base64.b64encode(encryptedbytes)
    # 使用Base64进行编码,返回byte字符串
    enctext = encodestrs.decode('utf-8')
    # 对byte字符串按utf-8进行解码
    return enctext


# 数组方式导入MAC地址，同步接口
# 返回HTTP状态码和response
def ImportArray(mac_address_array):
    if not isinstance(mac_address_array, list):
        return 404, ""
    for mac_address in mac_address_array:
        if not IsNoIntervalMac(mac_address):
            return 404, ""
    # A数据段 customer_part
    customer_part = Base64Str(customer_id)
    # B数据段 key_part
    aes_key = GenerateKey(16)
    aes_iv = GenerateKey(16)
    aes_key_iv = aes_key + aes_iv
    key_part = RsaStr2(aes_key_iv, public_key)
    array_data = {
        "productId": product_id,
        "customerId": customer_id,
        "machineIds": mac_address_array
    }
    mini_json = json.dumps(array_data)
    data_part = AesCbcEncrypt(mini_json, aes_key, aes_iv)

    encoded_data = customer_part + key_part + data_part
    http = urllib3.PoolManager()
    r = http.request(
        "POST",
        net_url + array_api,
        body=encoded_data,
        headers={
            'content-type': 'application/json;charset=UTF-8'
        }
    )
    return r.status, r.data.decode('utf-8')


# 范围方式导入数组，同步接口
# 返回HTTP状态码和response
def ImportRange(mac_address_from, mac_address_to):
    if (not isinstance(mac_address_from, str)) | (not isinstance(mac_address_to, str)):
        return 404, ""

    mac_address_from = mac_address_from.upper()
    mac_address_to = mac_address_to.upper()
    if IsNoIntervalMac(mac_address_from) & IsNoIntervalMac(mac_address_to):
        # A数据段 customer_part
        customer_part = Base64Str(customer_id)
        # B数据段 key_part
        aes_key = GenerateKey(16)
        aes_iv = GenerateKey(16)
        aes_key_iv = aes_key + aes_iv
        key_part = RsaStr2(aes_key_iv, public_key)

        # C数据段 data_part
        range_data = {
            "productId": product_id,
            "customerId": customer_id,
            "macAddressFrom": mac_address_from,
            "macAddressTo": mac_address_to
        }
        mini_json = json.dumps(range_data)
        data_part = AesCbcEncrypt(mini_json, aes_key, aes_iv)

        encoded_data = customer_part + key_part + data_part
        http = urllib3.PoolManager()
        r = http.request(
            "POST",
            net_url + range_api,
            body=encoded_data,
            headers={
                'content-type': 'application/json;charset=UTF-8'
            }
        )
        return r.status, r.data.decode('utf-8')
    return 404, ""