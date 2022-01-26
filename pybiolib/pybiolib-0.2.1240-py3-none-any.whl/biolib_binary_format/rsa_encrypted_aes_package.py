from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class RsaEncryptedAesPackage(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 6
        self.iv_len = 12
        self.aes_key_len = 32
        self.tag_len = 16

    def create(self, rsa_public_key_der, unencrypted_bytes):
        public_key = RSA.import_key(rsa_public_key_der)
        rsa_cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)

        iv = get_random_bytes(self.iv_len)
        aes_key_buffer = get_random_bytes(self.aes_key_len)
        aes_key = AES.new(aes_key_buffer, AES.MODE_GCM, iv)
        rsa_encrypted_aes_key_buffer = rsa_cipher.encrypt(aes_key_buffer)
        aes_encrypted_data, tag = aes_key.encrypt_and_digest(bytes(unencrypted_bytes))

        return self.serialize(rsa_encrypted_aes_key_buffer, iv, tag, aes_encrypted_data), aes_key_buffer

    def serialize(self, encrypted_aes_key, iv, tag, encrypted_data):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(len(encrypted_aes_key).to_bytes(2, 'big'))
        bbf_data.extend(encrypted_aes_key)
        bbf_data.extend(iv)
        bbf_data.extend(tag)

        bbf_data.extend(len(encrypted_data).to_bytes(8, 'big'))
        bbf_data.extend(encrypted_data)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        encrypted_aes_key_len = self.get_data(2, output_type='int')
        encrypted_aes_key = self.get_data(encrypted_aes_key_len)
        iv = self.get_data(self.iv_len)
        tag = self.get_data(self.tag_len)

        encrypted_data_len = self.get_data(8, output_type='int')
        encrypted_data = self.get_data(encrypted_data_len)

        return encrypted_aes_key, iv, tag, encrypted_data
