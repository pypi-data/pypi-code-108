from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import os
import sys
import time
import requests

class PyocsRsa:



    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    def rsa_gen_key():
        # 伪随机数生成器
        # rsa算法生成实例
        rsa = RSA.generate(2048)

        # 秘钥对的生成
        private_pem = rsa.exportKey()
        timestr = time.strftime("%Y%m%d", time.localtime()) 
        with open("private_"+timestr+".pem", "w") as f:
            f.write(private_pem.decode('utf-8'))

        public_pem = rsa.publickey().exportKey()
        with open("public_" + timestr + ".pem", "w") as f:
            f.write(public_pem.decode('utf-8'))


    def rsa_encrypt(file_name):
        afterEnText = []

        home_dir = os.environ['HOME'];
        pubKeyPath = home_dir + "/.ssh/public.pem"
        if os.path.exists(pubKeyPath):
            os.remove(pubKeyPath)

        pubKeyUrl = "https://cstore-public.seewo.com/knowledge/2af1cbdd5c0c4a6bb7d48876eb162229"
        res = requests.get(pubKeyUrl)
        with open (pubKeyPath, 'wb') as f:
            f.write(res.content)

        with open(pubKeyPath, "r") as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            cipher = Cipher_pkcs1_v1_5.new(rsakey)

            encrypt_text = ""
            maxLength = 245#2048长算的key最多只能加密245个字节
            with open(file_name, "r") as fe:
                encrypt_text = fe.read().encode('utf-8')
            print(type(encrypt_text))
            length = len(encrypt_text)
            startIdx = 0
            while length-startIdx > 0 :
                if length - startIdx <= maxLength :
                    afterEnText.append( cipher.encrypt(encrypt_text[startIdx:]))
                    break;
                else :
                    print(type(encrypt_text[startIdx:startIdx+maxLength]))
                    afterEnText.append( cipher.encrypt(encrypt_text[startIdx:startIdx+maxLength]))
                    startIdx += maxLength
        with open("afterEn_"+file_name, "w") as fd:
            key = fd.write(base64.b64encode(b''.join(afterEnText)).decode('utf-8'))
            
        
    def rsa_decrypt(file_name):
        afterDeText = []
        home_dir = os.environ['HOME'];
        priKeyPath = home_dir + "/.ssh/private.pem"
        if os.path.exists(priKeyPath):
            os.remove(priKeyPath)

        priKeyUrl = "https://cstore-public.seewo.com/knowledge/b2941f0c5c1248cfb74b1de8a951bfb9"
        res = requests.get(priKeyUrl)

        
        with open (priKeyPath, 'wb') as f:
            f.write(res.content)

        with open(priKeyPath, "r") as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            cipher = Cipher_pkcs1_v1_5.new(rsakey)

            encrypt_text = ""
            maxLength = 256#2048长度的key，最多只能解密256个字节
            with open(file_name, "r") as fe:
                encrypt_text = fe.read()
            encrypt_text = base64.b64decode(encrypt_text)
            length = len(encrypt_text)
            startIdx = 0
            while length-startIdx > 0 :
                if length - startIdx <= maxLength :
                    afterDeText.append( cipher.decrypt(encrypt_text[startIdx:], Random.new().read))
                    break;
                else :
                    afterDeText.append( cipher.decrypt(encrypt_text[startIdx:startIdx+maxLength], Random.new().read))
                    startIdx += maxLength
                    
            
        with open("afterDe_"+file_name, "w") as fd:
            key = fd.write(b''.join(afterDeText).decode('utf-8'))
        os.remove(priKeyPath)

            


