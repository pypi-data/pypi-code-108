import os
import base64

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

from ..config.config_client import ConfigClient


__all__ = ["CookieRsa"]


class CookieRsa:
    def __init__(self):
        app_id = os.environ.get("APP_ID", "NOT_EXIST")
        if app_id == "NOT_EXIST":
            app_id = "winhye_common"
        ConfigClient.init(app_id)
        ras_conf = ConfigClient.get_configger("winhye_software.common")
        self.ras_config = ras_conf.get_group("ras")

    # 初始化公钥私钥
    @staticmethod
    def __init_key():
        key_dir = "/data/log/rsa_key"
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)

        # 初始化RSA对象， 伪随机数生成器
        rsa = RSA.generate(1024, Random.new().read)

        # 私钥
        private_key = rsa.exportKey()
        private_key_path = os.path.join(key_dir, "private_key.pem")

        # 公钥
        public_key = rsa.publickey().exportKey()
        public_key_path = os.path.join(key_dir, "public_key.pem")

        with open(private_key_path, 'w') as f:
            f.write(private_key.decode())

        with open(public_key_path, 'w') as f:
            f.write(public_key.decode())

        return private_key, public_key

    # 获取私钥
    def __get_private_key(self):
        return self.ras_config.private_key

    # 获取公钥
    def __get_public_key(self):
        return self.ras_config.public_key

    # 加密
    def rsa_encrypt(self, content: str) -> str:
        public = RSA.importKey(self.__get_public_key())
        cipher = PKCS1_v1_5.new(public)
        return base64.b64encode(cipher.encrypt(content.encode('utf-8'))).decode('utf-8')

    # 解密
    def rsa_decrypt(self, content: str) -> str:
        private = RSA.importKey(self.__get_private_key())
        cipher = PKCS1_v1_5.new(private)
        return cipher.decrypt(base64.b64decode(content), b'error: decrypt fail').decode('utf-8')
