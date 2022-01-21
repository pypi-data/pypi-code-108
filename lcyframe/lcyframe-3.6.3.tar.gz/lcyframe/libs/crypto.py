# -*- coding:utf-8 -*-
import base64
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import MD5
from lcyframe.libs import utils
from lcyframe.libs.aes import AES as sAES

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def openssl_evp_byte2key(password, salt, key_len, iv_len):
    """
    Derive the key and the IV from the given password and salt.

    see OpenSSL man:
    https://www.openssl.org/docs/crypto/EVP_BytesToKey.html
    """
    # from hashlib import md5
    # dtot = md5(password + salt).digest()
    # d = [ dtot ]
    # while len(dtot)<(iv_len+key_len):
    #     d.append( md5(d[-1] + password + salt).digest() )
    #     dtot += d[-1]
    # return dtot[:key_len], dtot[key_len:key_len+iv_len]
    dtot = MD5.new('{0}{1}'.format(password, salt)).digest()
    d = [dtot]
    while len(dtot) < (iv_len + key_len):
        d.append(MD5.new('{0}{1}{2}'.format(d[-1], password, salt)).digest())
        dtot += d[-1]
    return dtot[:key_len], dtot[key_len:key_len+iv_len]


def openssl_aes_decrypt(encoded_text, password_phase):
    """
    decode an openssl-compatible 256-bit AES cipher text
    :param encoded_text:
    :param password_phase:
    :return:
    """
    encrypted = base64.b64decode(encoded_text)
    # salt = encrypted[8:16]
    salt = encrypted[0:8]
    data = encrypted[8:]
    key, iv = openssl_evp_byte2key(password_phase, salt, 32, 16)
    dec = AES.new(key, AES.MODE_CBC, iv)
    plain_text = dec.decrypt(data)
    return unpad(plain_text)


def openssl_aes_encrypt(plain_text, password_phase):
    salt = Random.new().read(8)
    key, iv = openssl_evp_byte2key(password_phase, salt, 32, 16)
    enc = AES.new(key, AES.MODE_CBC, iv)
    plain_text = pad(plain_text)
    return base64.b64encode(salt + enc.encrypt(plain_text))

def salt_aes_decrypt(encoded_text, password_phase):
    """
    > * 1：随机生成30位由字母与数字组成的字符串，并转为小写，得到salt。
    > * 2：将Payload消息体，按照原来机器人的AES加密方法进行加密，得到plain_text
    > * 3：将salt + plain_text，得到最终密文。
    """

    salt = encoded_text[0:30]
    data = encoded_text[30:]
    plain_text = sAES(password_phase).decode(data.decode())

    return plain_text


def salt_aes_encrypt(plain_text, password_phase):
    """
    > * 1：将密文从第31位(含)开始，截取至末尾，得到字符串plain_text。
    > * 2：将plain_text消息体，按照原来机器人的AES加密方法进行解密，得到明文Payload。
    :param plain_text:
    :param password_phase:
    :return:
    """
    enc = sAES(password_phase).encode(plain_text)
    salt = utils.gen_random_sint(30).lower()

    return salt + enc


def encrypt(plain_text, password_phase, mod=1):
    if int(mod) == 1:
        return salt_aes_encrypt(plain_text, password_phase)
    else:
        return openssl_aes_encrypt(plain_text, password_phase)

def decrypt(plain_text, password_phase, mod=1):
    if int(mod) == 1:
        return salt_aes_decrypt(plain_text, password_phase)
    else:
        return openssl_aes_decrypt(plain_text, password_phase)
