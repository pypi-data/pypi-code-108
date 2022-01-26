from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class ModuleInput(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 1

    def serialize(self, stdin, arguments, files):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(len(stdin).to_bytes(8, 'big'))

        argument_len = sum([len(arg.encode()) for arg in arguments]) + (2 * len(arguments))
        bbf_data.extend(argument_len.to_bytes(4, 'big'))

        file_data_len = sum([len(data) + len(path.encode()) for path, data in files.items()]) + (12 * len(files))
        bbf_data.extend(file_data_len.to_bytes(8, 'big'))

        bbf_data.extend(stdin)

        for argument in arguments:
            bbf_data.extend(len(argument).to_bytes(2, 'big'))
            bbf_data.extend(argument.encode())

        for path, data in files.items():
            bbf_data.extend(len(path.encode()).to_bytes(4, 'big'))
            bbf_data.extend(len(data).to_bytes(8, 'big'))

            bbf_data.extend(path.encode())
            bbf_data.extend(data)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        stdin_len = self.get_data(8, output_type='int')
        argument_data_len = self.get_data(4, output_type='int')
        files_data_len = self.get_data(8, output_type='int')
        stdin = self.get_data(stdin_len)

        end_of_arguments = self.pointer + argument_data_len
        arguments = []
        while self.pointer != end_of_arguments:
            argument_len = self.get_data(2, output_type='int')
            argument = self.get_data(argument_len, output_type='str')
            arguments.append(argument)

        end_of_files = self.pointer + files_data_len
        files = {}
        while self.pointer < end_of_files:
            path_len = self.get_data(4, output_type='int')
            data_len = self.get_data(8, output_type='int')
            path = self.get_data(path_len, output_type='str')
            data = self.get_data(data_len)
            files[path] = bytes(data)

        return {'stdin': stdin, 'arguments': arguments, 'files': files}
