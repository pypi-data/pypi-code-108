import base64
import hashlib
from Crypto.Cipher import AES

try:
    import secrets
    HAVE_SECRETS = True
except ImportError:
    from Crypto import Random
    HAVE_SECRETS = False


class AESCipher(object):
    def __init__(self, key="677d3cfc-dd28-4a4e-94d5-7c3b99a24a2a"):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        if HAVE_SECRETS:
            iv = secrets.token_bytes(16)
        else:
            iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.urlsafe_b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

from mobio.libs.caching import LRUCacheDict
from mobio.libs.ciphers import MobioCrypt2
from mobio.libs.Singleton import Singleton
from .config import SystemConfigKeys, LicenseFormat, PathDir
import os
import time
import json
from .date_utils import get_timestamp_utc_now


@Singleton
class CryptUtil:
    def __init__(self):
        self.license_server = LRUCacheDict(expiration=300)

    @staticmethod
    def get_content_from_file(file_path):
        content_file = None
        if not os.path.exists(file_path):
            return content_file
        i = 0
        while True:
            try:
                if i >= 10:
                    break
                with open(file_path, "r") as fout:
                    content_file = fout.read().replace("\r", "").replace("\n", "")
                    fout.close()
                break
            except IOError as ex:
                print("admin_sdk::get_content_from_file():message: %s" % ex)
                time.sleep(0.1)
                i += 1
        print("admin_sdk::content file license: {}".format(content_file))
        return content_file

    @staticmethod
    def get_license_info():
        license_info = None
        try:
            license_encrypt = CryptUtil.get_license_encrypt(SystemConfigKeys.LICENSE_SERVER)
            license_dec = MobioCrypt2.d1(license_encrypt, enc="utf-8")
            print("admin_sdk::get_license_info():license_dec: {}".format(license_dec))
            if license_dec:
                license_info = json.loads(license_dec)
        except Exception as ex:
            print("admin_sdk::get_license_info():message: {}".format(ex))
        return license_info

    @staticmethod
    def get_license_encrypt(key_cache):
        license_encrypt = ""
        try:
            try:
                license_encrypt = CryptUtil().license_server.getitem(key_cache)
            except Exception as ex:
                print(
                    "admin_sdk::get_license_encrypt():get cache none for key: {}".format(
                        ex
                    )
                )
            print("admin_sdk::license_encrypt cache: {}".format(license_encrypt))
            if not license_encrypt:
                print("admin_sdk::license_encrypt no cache")
                print("admin_sdk::license_encrypt path file license: {}".format(PathDir.PATH_FILE_LICENSE_SERVER))
                license_encrypt = CryptUtil.get_content_from_file(PathDir.PATH_FILE_LICENSE_SERVER)
                if license_encrypt:
                    CryptUtil().license_server.set_item(key_cache, license_encrypt)
        except Exception as ex:
            print("admin_sdk::get_license_encrypt():message: {}".format(ex))
        return license_encrypt

    @staticmethod
    def check_license_format(license_info):
        result = False
        try:
            if isinstance(license_info, dict):
                if all(name in license_info for name in LicenseFormat.ALL_FIELD):
                    if isinstance(license_info.get(LicenseFormat.time_expire), int) and \
                        isinstance(license_info.get(LicenseFormat.version), int):
                        result = True
        except Exception as ex:
            print("admin_sdk::check_license_format():message: {}".format(ex))
        return result

    @staticmethod
    def license_server_valid():
        license_valid = False
        try:
            license_info = CryptUtil.get_license_info()
            if CryptUtil.check_license_format(license_info):
                time_expire = license_info.get(LicenseFormat.time_expire)
                if time_expire < 0 or time_expire > get_timestamp_utc_now():
                    license_valid = True
        except Exception as ex:
            print("admin_sdk::license_server_valid():message: {}".format(ex))
        return license_valid
