from biolib.biolib_binary_format.base_bbf_package import BioLibBinaryFormatBasePackage


class AttestationDocument(BioLibBinaryFormatBasePackage):
    def __init__(self, bbf=None):
        super().__init__(bbf)
        self.package_type = 4

    def serialize(self, attestation_document_bytes):
        bbf_data = bytearray()
        bbf_data.extend(self.version.to_bytes(1, 'big'))
        bbf_data.extend(self.package_type.to_bytes(1, 'big'))

        bbf_data.extend(len(attestation_document_bytes).to_bytes(4, 'big'))
        bbf_data.extend(attestation_document_bytes)

        return bbf_data

    def deserialize(self):
        version = self.get_data(1, output_type='int')
        package_type = self.get_data(1, output_type='int')
        self.check_version_and_type(version=version, package_type=package_type, expected_package_type=self.package_type)

        attestation_document_len = self.get_data(4, output_type='int')
        attestation_document = self.get_data(attestation_document_len)

        return attestation_document
