# -*- coding: UTF-8 -*-

import sys
#sys.path.append(r'E:\algo_text\nn_csdk\cmake_py36\Release')
from nn_sdk.engine_csdk import sdk_aes_encode_decode

def test_string():
    data1 = {
        "mode":0,# 0 加密 ， 1 解密
        "key": bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
        "iv": bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
        "data": bytes([1,2,3,5,255])
    }

    code,encrypt = sdk_aes_encode_decode(data1)
    print(code,encrypt)

    data2 = {
        "mode":1,
        "key": bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
        "iv": bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
        "data": encrypt
    }

    code,plain = sdk_aes_encode_decode(data2)
    print(code,plain)

def test_encode_file(in_filename,out_filename):

    with open(in_filename,mode='rb') as f:
        data = f.read()
    if len(data) == 0 :
        return -1
    data1 = {
        "mode": 0,  # 0 加密 ， 1 解密
        "key": bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        "iv": bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        "data": bytes(data)
    }

    code, encrypt = sdk_aes_encode_decode(data1)
    if code != 0:
        return code
    with open(out_filename, mode='wb') as f:
        f.write(encrypt)
    return code
def test_decode_file(in_filename,out_filename):
    with open(in_filename, mode='rb') as f:
        data = f.read()
    if len(data) == 0:
        return -1
    data1 = {
        "mode": 1,  # 0 加密 ， 1 解密
        "key": bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        "iv": bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        "data": bytes(data)
    }

    code, plain = sdk_aes_encode_decode(data1)
    if code != 0:
        return code
    with open(out_filename, mode='wb') as f:
        f.write(plain)
    return code

test_encode_file(r'C:\Users\acer\Desktop\img\a.txt',r'C:\Users\acer\Desktop\img\a.txt.encode')
test_decode_file(r'C:\Users\acer\Desktop\img\a.txt.encode',r'C:\Users\acer\Desktop\img\a.txt.decode')