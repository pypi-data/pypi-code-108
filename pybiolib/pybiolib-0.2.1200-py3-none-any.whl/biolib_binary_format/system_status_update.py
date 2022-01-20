from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class SystemStatusUpdate(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 8

    def serialize(self, progress, log_message):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(progress.to_bytes(2, 'big'))
        bbf_data.extend(len(log_message).to_bytes(4, 'big'))
        bbf_data.extend(log_message.encode())

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        progress = self.get_data(2, output_type='int')
        log_message_string_len = self.get_data(4, output_type='int')
        log_message_string = self.get_data(log_message_string_len).decode()

        return progress, log_message_string
