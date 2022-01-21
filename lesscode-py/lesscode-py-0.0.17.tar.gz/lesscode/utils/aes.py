# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/4 4:39 下午
# Copyright (C) 2021 The lesscode Team

import binascii
import base64
from Crypto.Cipher import AES as _AES


class AES:
    @staticmethod
    def encrypt(key, text):
        """
        :param key: 密钥
        :param text: 需要被加密的数据
        """
        text = str(text)
        aes = _AES.new(AES.add_to_16(key), _AES.MODE_ECB)
        encrypt_aes = aes.encrypt(AES.add_to_16(text))
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        return bytes.decode(binascii.b2a_hex(bytes(encrypted_text, encoding="utf8")))

    @staticmethod
    def decrypt(key, text):
        """
        :param key: 密钥
        :param text: 需要被加密的数据
        """
        text = bytes.decode(binascii.a2b_hex(bytes(text, encoding="utf8")))
        # 密文
        # 初始化加密器
        aes = _AES.new(AES.add_to_16(key), _AES.MODE_ECB)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        # 执行解密密并转码返回str
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
        return decrypted_text

    @staticmethod
    def add_to_16(value):
        """
        :param value: 待处理的数据
        """
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)  # 返回bytes
