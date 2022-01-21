#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Crypto.Cipher import AES as _AES
from binascii import b2a_hex, a2b_hex
from base64 import b64decode, b64encode
import json

class AES():
    def __init__(self, key=None,
                 iv=b'3eddc41dd41239c8',
                 mode=_AES.MODE_ECB,
                 padding="zeropadding",
                 print_model="hex"):
        # 这里密钥key 长度必须为16（AES-128）, 24（AES-192）,或者32 （AES-256）Bytes 长度
        self.key = key if key else "ODQJmzxHP83YTV5aysc90bUMon1GqhKF" # "054eda8889ea6240"
        self.mode = mode                    # 模式
        self.iv = iv                        # 偏移量
        self.padding = padding              # 填充方式： 默认 zeropadding： 0补全；pkcs7padding；pkcs5padding；等
        self.print_model = print_model      # 输出格式 hex：十六进制 base64：base64格式

    def encode(self, text):
        if not isinstance(text, str):
            text = json.dumps(text)
        try:
            cryptor = _AES.new(self.key.encode('utf-8'), self.mode, self.iv)
        except:
            cryptor = _AES.new(self.key.encode('utf-8'), self.mode)
        length = 16     # 如果text不足16位就用空格补足为16位， 如果大于16当时不是16的倍数，那就补足为16的倍数
        count = len(text)
        if count < length:
            add = (length - count)
            # \0 backspace
            text = text + ('\0' * add)
        elif count > length and count % length != 0:
            add = (length - (count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text.encode('utf-8'))
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串格式化输出
        if self.print_model == "hex":
            return b2a_hex(self.ciphertext).decode()
        else:
            return b64encode(self.ciphertext).decode()

    # 解密后，去掉补足的空格用strip() 去掉
    def decode(self, text):
        text = text if type(text) == bytes else text.encode('utf-8')
        try:
            cryptor = _AES.new(self.key.encode('utf-8'), self.mode, self.iv)
        except:
            cryptor = _AES.new(self.key.encode('utf-8'), self.mode)
        if self.print_model == "hex":
            plain_text = cryptor.decrypt(a2b_hex(text)).decode()
        else:
            plain_text = cryptor.decrypt(b64decode(text)).decode()

        try:
            return json.loads(plain_text.rstrip('\0'))
        except ValueError:
            return plain_text.rstrip('\0')

if __name__ == '__main__':
    pc = AES("debe8e44b8b68d3a528da563e147e7bb")  #  054eda8889ea6240 初始化密钥
    s = "a:b"
    d = pc.encode(s)
    print("加密:", d)

    d = pc.decode(d)  # 解密
    print("解密:", d)