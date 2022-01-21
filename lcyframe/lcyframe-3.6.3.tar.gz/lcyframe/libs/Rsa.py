#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import rsa as _rsa


class RSA(object):
    """
    # 公钥加密
    # str = rsa.encrypt(self.params, publicKey)

    # 私钥解密
    # str = rsa.decrypt(self.params, privateKey).decode()

    # 私钥签名
    # signature = rsa.sign(message, privkey, 'SHA-1')

    # 公钥验证
    s = rsa.verify(message, sign, public_key)

    # =================================
    # 场景〇：密钥保存导入
    # =================================
    # 保存密钥
    with open('public.pem','w+', encoding='utf-8') as f:
        print(pubkey.save_pkcs1().decode())
        f.write(pubkey.save_pkcs1().decode())

    with open('private.pem','w+') as f:
        print(privkey.save_pkcs1().decode())
        f.write(privkey.save_pkcs1().decode())

    # 导入密钥
    with open('public.pem','r') as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())

    with open('private.pem','r') as f:
        privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())

    """

    @classmethod
    def gen_rsa_key(cls, nbits=1024):
        """
        生成key
        :param nbits:
        :return:
        """
        cls.pubkey, cls.privkey = _rsa.newkeys(int(nbits))
        return cls.save_pkcs(cls.pubkey), cls.save_pkcs(cls.privkey)

    @classmethod
    def encode(cls, str, pubkey):
        """
        公钥加密
        :param str:
        :param pubkey:
        :return:
        """
        str = str.encode() if not isinstance(str, bytes) else str
        return _rsa.encrypt(str, cls.load_pkcs(pubkey, "pub"))

    @classmethod
    def decode(cls, str, privkey):
        """
        公钥加密
        :param str:
        :param pubkey:
        :return:
        """
        str = str.encode() if not isinstance(str, bytes) else str
        return _rsa.decrypt(str, cls.load_pkcs(privkey, "pri")).decode()

    @classmethod
    def sign(cls, str, privkey):
        """
        私钥签名
        :param str:
        :param privkey:
        :return:
        """
        str = str.encode() if not isinstance(str, bytes) else str
        return _rsa.sign(str, cls.load_pkcs(privkey, "pri"), 'SHA-1')

    @classmethod
    def verify(cls, str, sign, pubkey):
        """
        公钥验签
        :param str:
        :param pubkey:
        :return:
        """
        str = str.encode() if not isinstance(str, bytes) else str
        try:
            result = _rsa.verify(str, sign, cls.load_pkcs(pubkey, "pub"))
        except Exception as e:
            return False
        else:
            return True


    @classmethod
    def load_pkcs(cls, str, t):
        """
        转为rsa对象
        :param key:
        :return:
        """
        if t == "pub":
            return _rsa.PublicKey.load_pkcs1(str)
        else:
            return _rsa.PrivateKey.load_pkcs1(str)

    @classmethod
    def save_pkcs(cls, key):
        """
        rsa对象转为字节码，便于存储、阅读
        转为rsa对象
        :param key:
        :return:
        """

        return key.save_pkcs1()


    @classmethod
    def save_to_file(cls, path=None):
        """
        生成公钥私钥并保存
        """
        import os
        pubkey, privkey = r.gen_rsa_key()
        p = os.path.join(path, "privkey.pem") if path else "privkey.pem"
        with open(p, "wb") as x:  # 保存私钥
            x.write(privkey)

        p = os.path.join(path, "pubkey.pem") if path else "pubkey.pem"
        with open(p, "wb") as x:  # 保存公钥
            x.write(pubkey)

    @classmethod
    def read_from_file(cls, filename, t):
        """
        读取公钥私钥
        """
        with open(filename, "rb") as x:
            str = x.read()

        return cls.save_pkcs(cls.load_pkcs(str, t))

if __name__ == '__main__':
    r = RSA()
    str = """$#5qead"""

    pubkey, privkey = r.gen_rsa_key()

    # 加密
    encode_str = r.encode(str, pubkey)

    # 解密
    decode_str = r.decode(encode_str, privkey)

    print(decode_str == str)


    # 签名
    s = r.sign(str, privkey)

    # 验签
    result = r.verify(str, s, pubkey)

    print(result)

    # 生成公钥私钥
    r.save_to_file()