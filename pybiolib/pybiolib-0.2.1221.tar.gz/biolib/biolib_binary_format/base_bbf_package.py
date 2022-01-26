class BioLibBinaryFormatBasePackage:

    def __init__(self, bbf=None):
        self.version = 1
        self.bbf = bbf if bbf else bytearray()
        self.pointer = 0

    def get_data(self, offset, output_type='bytes'):
        bbf_bytes = self.bbf[self.pointer:self.pointer + offset]
        self.pointer += offset
        if output_type == 'str':
            return bbf_bytes.decode()
        elif output_type == 'int':
            return int.from_bytes(bbf_bytes, 'big')
        else:
            return bbf_bytes

    def check_version_and_type(self, version, package_type, expected_package_type):
        if version != self.version:
            raise Exception(f'Unsupported BioLib Binary Format version: Got {version} expected {self.version}')

        if package_type != expected_package_type:
            raise Exception(f'Unsupported BioLib Binary Format type: Got {package_type} expected '
                            f'{expected_package_type}')
