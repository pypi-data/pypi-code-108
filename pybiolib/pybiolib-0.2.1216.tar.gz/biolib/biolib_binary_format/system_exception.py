from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class SystemException(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 9

    def serialize(self, error_code):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(error_code.to_bytes(2, 'big'))

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        error_code = self.get_data(2, output_type='int')

        return error_code
