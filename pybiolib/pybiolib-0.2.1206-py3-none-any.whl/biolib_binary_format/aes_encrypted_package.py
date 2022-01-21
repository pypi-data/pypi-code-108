from Crypto.Cipher import AES

from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class AesEncryptedPackage(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 7
        self.iv_len = 12
        self.tag_len = 16

    def decrypt(self, aes_key_buffer):
        iv, _, encrypted_data = self.deserialize()
        aes_key = AES.new(aes_key_buffer, AES.MODE_GCM, iv)
        return aes_key.decrypt(encrypted_data)

    def serialize(self, iv, tag, encrypted_data):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(iv)
        bbf_data.extend(tag)

        bbf_data.extend(len(encrypted_data).to_bytes(8, 'big'))
        bbf_data.extend(encrypted_data)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        iv = self.get_data(self.iv_len)
        tag = self.get_data(self.tag_len)

        encrypted_data_len = self.get_data(8, output_type='int')
        encrypted_data = self.get_data(encrypted_data_len)

        return iv, tag, encrypted_data
