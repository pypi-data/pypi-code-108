from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class ModuleOutput(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 2

    def serialize(self, stdout, stderr, exit_code, files):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        # Length of stdout and stderr
        bbf_data.extend(len(stdout).to_bytes(8, 'big'))
        bbf_data.extend(len(stderr).to_bytes(8, 'big'))

        file_data_len = sum([len(data) + len(path.encode()) for path, data in files.items()]) + (12 * len(files))
        bbf_data.extend(file_data_len.to_bytes(8, 'big'))

        bbf_data.extend(exit_code.to_bytes(2, 'big'))
        bbf_data.extend(stdout)
        bbf_data.extend(stderr)

        for path, data in files.items():
            # Path length and data length
            bbf_data.extend(len(path.encode()).to_bytes(4, 'big'))
            bbf_data.extend(len(data).to_bytes(8, 'big'))

            bbf_data.extend(path.encode())
            # The file data
            bbf_data.extend(data)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        stdout_len = self.get_data(8, output_type='int')
        stderr_len = self.get_data(8, output_type='int')
        files_data_len = self.get_data(8, output_type='int')
        exit_code = self.get_data(2, output_type='int')
        stdout = self.get_data(stdout_len)
        stderr = self.get_data(stderr_len)

        end_of_files = self.pointer + files_data_len
        files = {}

        while self.pointer < end_of_files:
            path_len = self.get_data(4, output_type='int')
            data_len = self.get_data(8, output_type='int')
            path = self.get_data(path_len, output_type='str')
            data = self.get_data(data_len)
            files[path] = bytes(data)

        return {'stdout': stdout, 'stderr': stderr, 'exit_code': exit_code, 'files': files}
