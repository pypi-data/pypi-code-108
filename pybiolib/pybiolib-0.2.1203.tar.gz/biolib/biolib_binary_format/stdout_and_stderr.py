from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class StdoutAndStderr(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 10

    def serialize(self, stdout_and_stderr_bytes):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(len(stdout_and_stderr_bytes).to_bytes(8, 'big'))
        bbf_data.extend(stdout_and_stderr_bytes)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        stdout_and_stderr_length = self.get_data(8, output_type='int')
        stdout_and_stderr = self.get_data(stdout_and_stderr_length)

        return stdout_and_stderr
