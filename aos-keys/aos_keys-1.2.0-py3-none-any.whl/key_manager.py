#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives._serialization import NoEncryption, Encoding, PrivateFormat
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates, \
    load_key_and_certificates
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from rich.console import Console
from rich.table import Table

from aos_keys.errors import AosKeysError

__CERTIFICATE_START = b'-----BEGIN CERTIFICATE-----'


def split_certificate_chain(pem_bytes: bytes):
    pem_certs_split = pem_bytes.split(__CERTIFICATE_START)
    pem_certs_split = list(filter(None, pem_certs_split))
    user_certificate = load_pem_x509_certificate(__CERTIFICATE_START + pem_certs_split[0])
    other_certificates = []
    for single_pem_cert in pem_certs_split[1:]:
        cert = load_pem_x509_certificate((__CERTIFICATE_START + single_pem_cert))
        other_certificates.append(cert)

    return user_certificate, other_certificates


def generate_pair():
    """Generates private key and CSR."""
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    pem_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([])).sign(private_key, hashes.SHA256())
    return pem_key, csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def generate_pair_rsa():
    """Generates private key and CSR."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([])).sign(private_key, hashes.SHA256())
    return pem_private_key, csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def save_pkcs_container(private_key_pem, certificate_pem, save_file_name):
    key = load_pem_private_key(private_key_pem, None)
    user_cert, other_certs = split_certificate_chain(certificate_pem.encode("utf-8"))
    pkcs12 = serialize_key_and_certificates(
        name='aos user certificate'.encode("utf-8"),
        key=key,
        cert=user_cert,
        cas=other_certs,
        encryption_algorithm=NoEncryption()
    )

    with open(save_file_name, 'wb') as save_file:
        save_file.write(pkcs12)

    console = Console()
    console.print(f'File {save_file_name} created', style='green')


def extract_cloud_domain_from_cert(cert_file_path: str) -> str:
    """Get the Cloud domain name from user certificate"""
    with open(cert_file_path, "rb") as cert:
        private_key, certificate, additional_certificates = load_key_and_certificates(cert.read(), None)
        return certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value


def show_cert_info(cert_file_path):
    try:
        with open(cert_file_path, "rb") as cert:
            private_key, certificate, additional_certificates = load_key_and_certificates(cert.read(), None)
    except FileNotFoundError:
        raise AosKeysError('File not found')

    table = Table(padding=0, title='Certificate info', show_header=False)
    table.add_column("", no_wrap=True, justify="left", style="bold", width=19)
    table.add_column("", style="bold")
    table.add_row("File: ", cert_file_path)

    if certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME):
        table.add_row("Aos domain: ", certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value)

    table.add_row("Serial number: ", f'{certificate.serial_number:X}')

    if certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME):
        table.add_row("User: ", certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)

    if certificate.subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS):
        table.add_row("e-mail: ", certificate.subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value)

    if certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME):
        table.add_row(
            "Company name: ",
            certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
        )

    table.add_row("Valid not before: ", str(certificate.not_valid_before))
    table.add_row("Valid not before: ", str(certificate.not_valid_after))
    console = Console()
    console.print(table)


def pkcs12_to_pem_bytes(pkcs12_bytes: bytes):
    """Get PKCS12 bytes and return PEM certificates chain and key"""
    private_key, certificate, additional_certificates = \
        load_key_and_certificates(pkcs12_bytes, ''.encode('utf8'), default_backend())

    cert_bytes = bytearray(certificate.public_bytes(Encoding.PEM))
    for add_cert in additional_certificates:
        cert_bytes += add_cert.public_bytes(Encoding.PEM)
    key_bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    cert_bytes = bytes(cert_bytes)
    return cert_bytes, key_bytes
