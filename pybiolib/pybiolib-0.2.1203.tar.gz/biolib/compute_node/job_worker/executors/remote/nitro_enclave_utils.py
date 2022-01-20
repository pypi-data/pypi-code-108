import cbor2  # type: ignore
import cose  # type: ignore

from cose import EC2, CoseAlgorithms, CoseEllipticCurves
from Crypto.Util.number import long_to_bytes
from OpenSSL import crypto

from biolib import utils
from biolib.biolib_errors import BioLibError


class NitroEnclaveUtils:
    def attest_enclave_and_get_rsa_public_key(self, expected_pcrs_and_aws_cert, attestation_document_bytes):
        cbor_data = cbor2.loads(attestation_document_bytes)
        cbor_document = cbor2.loads(cbor_data[2])
        expected_pcrs_list = expected_pcrs_and_aws_cert['pcrObjectArray']
        aws_nitro_root_cert_pem = "-----BEGIN CERTIFICATE-----\n" + \
                                  expected_pcrs_and_aws_cert['awsNitroRootCertificateBase64'] + \
                                  "\n-----END CERTIFICATE-----"
        actual_pcrs = {str(k): v.hex() for k, v in cbor_document['pcrs'].items()}

        if not utils.BIOLIB_CLOUD_SKIP_PCR_VERIFICATION:
            self._assert_pcr_validity(actual_pcrs, expected_pcrs_list)

        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cbor_document['certificate'])
        self._assert_certificate_chain_validity(cbor_document['cabundle'], cert, aws_nitro_root_cert_pem)
        self._assert_cose_signature_validity(cert, cbor_data)
        return cbor_document['public_key']

    def _assert_pcr_validity(self, actual_pcrs, expected_pcrs_list):
        for expected_pcrs in expected_pcrs_list:
            if self._does_pcr_object_match_actual(actual_pcrs, expected_pcrs):
                return True

        # Raise error if no match was fund
        raise BioLibError('Failed to verify PCRs')

    def _does_pcr_object_match_actual(self, actual_pcrs, expected_pcrs):
        for pcr_key in expected_pcrs.keys():
            if actual_pcrs[pcr_key] != expected_pcrs[pcr_key]:
                return False
            # If all matched return True
            return True

    def _assert_certificate_chain_validity(self, cabundle, cert, aws_nitro_root_cert_pem):
        store = crypto.X509Store()
        _cert = crypto.load_certificate(crypto.FILETYPE_PEM, aws_nitro_root_cert_pem)
        store.add_cert(_cert)

        for _cert_binary in cabundle[1:]:
            _cert = crypto.load_certificate(crypto.FILETYPE_ASN1, _cert_binary)
            store.add_cert(_cert)

        store_ctx = crypto.X509StoreContext(store, cert)
        try:
            store_ctx.verify_certificate()
        except Exception as exception:
            raise BioLibError('Failed to verify certificates') from exception

    def _assert_cose_signature_validity(self, cert, cbor_data):
        phdr = cbor2.loads(cbor_data[0])
        uhdr = cbor_data[1]
        signature = cbor_data[3]

        cert_public_numbers = cert.get_pubkey().to_cryptography_key().public_numbers()
        x_long = cert_public_numbers.x
        y_long = cert_public_numbers.y

        x_bytes = long_to_bytes(x_long)
        y_bytes = long_to_bytes(y_long)

        # Create the EC2 key from public key parameters
        key = EC2(alg=CoseAlgorithms.ES384, x=x_bytes, y=y_bytes, crv=CoseEllipticCurves.P_384)

        # Construct the Sign1 message
        msg = cose.Sign1Message(phdr=phdr, uhdr=uhdr, payload=cbor_data[2])
        msg.signature = signature

        # Verify the signature using the EC2 key
        if not msg.verify_signature(key):
            raise Exception('Failed to verify signature in attestation document')
