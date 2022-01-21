from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class SavedJob(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 5

    def serialize(self, saved_job_json_string):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(len(saved_job_json_string).to_bytes(4, 'big'))
        bbf_data.extend(saved_job_json_string.encode())

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        saved_job_json_string_len = self.get_data(4, output_type='int')
        saved_job_json_string = self.get_data(saved_job_json_string_len, output_type='str')

        return saved_job_json_string
