#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from base64 import b64decode
from Crypto.PublicKey import RSA
# key = RSA.generate(1024)
# f = open('myPrivateKey.pem','w')
# myPrivateKey = key.exportKey('PEM', pkcs=8)   # 支持pkcs1 pkcs8
# f.write(myPrivateKey)
# f.close()

def encrypt(message):
    externKey="./myPublicKey.pem"
    privatekey = open(externKey, "r", encoding='utf-8')
    encryptor = RSA.importKey(privatekey,)
    encriptedData=encryptor.encrypt(message, 0)
    file = open("./cryptThingy.txt", "wb", encoding='utf-8')
    file.write(encriptedData[0])
    file.close()

def decrypt():
    externKey="./myPrivateKey.pem"
    publickey = open(externKey, "r", encoding='utf-8')
    decryptor = RSA.importKey(publickey)
    retval=None
    file = open("./cryptThingy.txt", "rb", encoding='utf-8')
    retval = decryptor.decrypt(file.read())
    file.close()
    return retval


def rsa_sign(message):
    private_key_file = open('./myPrivateKey.pem', 'r', encoding='utf-8')
    private_key = RSA.importKey(private_key_file)
    hash_obj = SHA.new(message)
    signer = PKCS1_v1_5.new(private_key)
    d = b64encode(signer.sign(hash_obj))
    file = open('./signThing.txt', 'wb', encoding='utf-8')
    file.write(d)
    file.close()

def rsa_verify(message):
    public_key_file = open('./myPublicKey.pem', 'r', encoding='utf-8')
    public_key = RSA.importKey(public_key_file)
    sign_file = open('./signThing.txt', 'r', encoding='utf-8')
    sign = b64decode(sign_file.read())
    h = SHA.new(message)
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(h, sign)

if '__main__' == __name__:
    pass
    # encryptedThingy = encrypt("Loren ipsum")
    # decryptedThingy = decrypt()
    # print("Decrypted: %s" % decryptedThingy)
    #
    rsa_sign('zhangshibo')
    print(rsa_verify('zhangshibo'))