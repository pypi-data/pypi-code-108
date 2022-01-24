# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2021-04-21 12:03:16
:LastEditors: ChenXiaolei
:Description: 加密帮助类
"""
import base64
from Crypto.Cipher import AES


class CryptoHelper:
    """
    :Description: 加密帮助类
    """
    @classmethod
    def md5_encrypt(self, source, salt="", encoding="utf-8"):
        """
        :Description: md5加密，支持加盐算法
        :param source: 需加密的字符串
        :param salt: 加盐算法参数值
        :param encoding: 字符串编码
        :return: md5加密后的字符串
        :last_editors: ChenXiaolei
        """
        if not isinstance(source, str) or not isinstance(salt, str):
            return ""
        return self.md5_encrypt_bytes((source + salt).encode(encoding))

    @classmethod
    def md5_encrypt_bytes(self, source):
        """
        :Description: md5字节流加密
        :param source: 字节流
        :return: md5加密后的字符串
        :last_editors: ChenXiaolei
        """
        if not isinstance(source, bytes):
            return ""
        import hashlib
        encrypt = hashlib.md5()
        encrypt.update(source)
        md5value = encrypt.hexdigest()
        return md5value

    @classmethod
    def md5_encrypt_int(self, source, salt="", encoding="utf-8"):
        """
        :Description: md5加密，返回数值
        :param source: 需加密的字符串
        :param salt: 加盐算法参数值
        :return: md5加密后的数值
        :last_editors: ChenXiaolei
        """
        md5_16 = self._convert_md5(self.md5_encrypt(source, salt, encoding))
        hash_code_start = int.from_bytes(md5_16[0:8],
                                         byteorder='little',
                                         signed=True)
        hash_code_end = int.from_bytes(md5_16[8:16],
                                       byteorder='little',
                                       signed=True)
        return hash_code_start ^ hash_code_end

    @classmethod
    def _convert_md5(self, origin):
        """
        :Description: md5字符串转16进制数组
        :param origin: 原md5字符串
        :return: 16进制数组
        :last_editors: ChenXiaolei
        """
        result = []
        s = ""
        for i in range(len(origin)):
            s += origin[i]
            if i % 2 != 0:
                int_hex = int(s, 16)
                result.append(int_hex)
                s = ""

        return result

    @classmethod
    def sha1_encrypt(self, source, encoding="utf-8"):
        """
        :Description: sha1加密
        :param source: 需加密的字符串
        :return: sha1加密后的字符串
        :last_editors: ChenXiaolei
        """
        from hashlib import sha1
        sha1_sign = sha1()
        if isinstance(source, str):
            sha1_sign.update(source.encode(encoding))
        elif isinstance(source, bytes):
            sha1_sign.update(source)
        return sha1_sign.hexdigest()

    @classmethod
    def sha256_encrypt(self, source, encoding="utf-8"):
        """
        :Description: sha256加密
        :param source: 需加密的字符串
        :return: sha256加密后的字符串
        :last_editors: ChenXiaolei
        """
        import hashlib
        sha256 = hashlib.sha256()
        if isinstance(source, str):
            sha256.update(source.encode(encoding))
        elif isinstance(source, bytes):
            sha256.update(source)
        result = sha256.hexdigest()
        return result

    @classmethod
    def base64_encode(self, source, encoding="utf-8"):
        """
        :Description: base64加密
        :param source: 需加密的字符串
        :return: 加密后的bytes
        :last_editors: ChenXiaolei
        """
        if not source.strip():
            return ""
        import base64
        encode_string = base64.b64encode(source.encode(encoding=encoding))
        return encode_string.decode(encoding=encoding)

    @classmethod
    def base64_decode(self, source, encoding="utf-8"):
        """
        :Description: base64解密
        :param source: 需加密的字符串
        :return: 解密后的字符串
        :last_editors: ChenXiaolei
        """
        if not source.strip():
            return ""
        import base64
        decode_string = base64.b64decode(source)
        return decode_string.decode(encoding=encoding)

    @classmethod
    def _aes_pad(self, text, encoding="utf-8"):
        """
        :Description: 填充函数，使被加密数据的字节码长度是block_size的整数倍
        :param text: 填充字符串
        :return: 填充后的字符串
        :last_editors: ChenXiaolei
        """
        length = AES.block_size
        count = len(text.encode(encoding))
        add = length - (count % length)
        entext = text + (chr(add) * add)
        return entext

    @classmethod
    def aes_encrypt(self, source, password, encoding="utf-8"):
        """
        :Description: AES加密,ECB & PKCS7
        :param source: 待加密字符串
        :param password: 密钥 必须为16位或32位
        :return: 加密后的字符串
        :last_editors: ChenXiaolei
        """
        if isinstance(password, str):
            password = password.encode(encoding)

        aes = AES.new(password, AES.MODE_ECB)  # 初始化AES,ECB模式的实例

        resource = aes.encrypt(self._aes_pad(
            source, encoding).encode(encoding))
        result = str(base64.b64encode(resource), encoding=encoding)
        return result

    @classmethod
    def aes_decrypt(self, source, password, encoding="utf-8"):
        """
        :Description: AES解密,ECB & PKCS7
        :param source: 待解密字符串
        :param password: 密钥 必须为16位或32位
        :return: 解密后的明文
        :last_editors: ChenXiaolei
        """
        if isinstance(password, str):
            password = password.encode(encoding)

        aes = AES.new(password, AES.MODE_ECB)  # 初始化AES,ECB模式的实例

        # 截断函数，去除填充的字符
        def unpad(date): return date[0:-ord(date[-1])]

        resource = base64.decodebytes(source.encode(encoding))
        result = aes.decrypt(resource).decode(encoding)
        return unpad(result)
