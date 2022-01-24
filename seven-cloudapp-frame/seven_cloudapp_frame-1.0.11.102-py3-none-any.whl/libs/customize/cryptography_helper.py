# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-08 22:01:47
@LastEditTime: 2021-10-15 14:59:20
@LastEditors: HuangJianYi
@Description: 
"""
import json
from Crypto.Cipher import AES
import base64
from seven_cloudapp_frame.libs.customize.seven_helper import *


class CryptographyHelper:
    """
    :description: 加密帮助类
    :return: 
    :last_editors: HuangJianYi
    """
    @classmethod
    def base64_encrypt(self, source, encoding="utf-8"):
        """
        :Description: base64加密
        :param source: 需加密的字符串
        :return: 加密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        cipher_text = str(base64.b64encode(source.encode(encoding=encoding)), 'utf-8')
        return cipher_text

    @classmethod
    def base64_decrypt(self, source):
        """
        :Description: base64解密
        :param source: 需加密的字符串
        :return: 解密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        plain_text = str(base64.b64decode(source), 'utf-8')
        return plain_text

    @classmethod
    def aes_encrypt(self, source, password, iv, mode=AES.MODE_CBC, pad_char='\0', encoding="utf-8"):
        """
        :Description: AES加密,默认CBC & ZeroPadding
        :param source: 待加密字符串
        :param password: 密钥
        :param iv: 偏移量
        :param mode: AES加密模式
        :param pad_char: 填充字符
        :param encoding: 编码
        :return: 加密后的字符串
        :last_editors: HuangJianYi
        """
        source = source.encode(encoding)
        password = password.encode(encoding)
        iv = iv.encode(encoding)
        cryptor = AES.new(password, mode, iv)
        # 这里密钥password 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        length = 16
        count = len(source)
        if count < length:
            add = (length - count)
            source = source + (pad_char * add).encode(encoding)
        elif count > length:
            add = (length - (count % length))
            source = source + (pad_char * add).encode(encoding)
        cipher_text = cryptor.encrypt(source)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为base64
        return str(base64.b64encode(cipher_text), encoding)

    @classmethod
    def aes_decrypt(self, source, password, iv, mode=AES.MODE_CBC, encoding="utf-8"):
        """
        :Description: AES解密,默认CBC
        :param source: 待解密字符串
        :param password: 密钥
        :param iv: 偏移量
        :param mode: AES加密模式
        :param encoding: 编码
        :return: 解密后的明文
        :last_editors: HuangJianYi
        """
        try:
            encry_text = base64.b64decode(source)
            password = password.encode(encoding)
            iv = iv.encode(encoding)
            cryptor = AES.new(password, mode, iv)
            plain_text = cryptor.decrypt(encry_text)
            plain_text = str(plain_text, encoding)
            index = plain_text.rindex('}') + 1
            return plain_text[0:index]
        except Exception as ex:
            return ""
