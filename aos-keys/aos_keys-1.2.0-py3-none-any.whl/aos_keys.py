import datetime
import sys
from datetime import datetime
from pathlib import Path

import OpenSSL
from OpenSSL import crypto
from rich.console import Console
from rich.table import Table


def __cert_time_to_time(cert_time: bytes) -> datetime:
    return datetime.strptime(cert_time.decode('ascii'), '%Y%m%d%H%M%SZ')


def __generate_pairs(crypto_type=crypto.TYPE_RSA, bits=2048):
    """Generates keys (public/private) based on type and bits."""
    key = crypto.PKey()
    key.generate_key(crypto_type, bits)

    public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, key)
    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

    return public_key, private_key


def extract_cloud_domain_from_cert(cert_file_path: str) -> str:
    """Get the Cloud domain name from user certificate"""
    with open(cert_file_path, "rb") as cert:
        return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert.read()).get_subject().organizationName


def show_cert_info(cert_file_path):
    try:
        with open(cert_file_path, "rb") as cert:
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert.read())
    except FileNotFoundError:
        print('File not found')
        sys.exit(1)

    table = Table(padding=0, title='Certificate info', show_header=False)
    table.add_column("", no_wrap=True, justify="left", style="bold", width=19)
    table.add_column("", style="bold")
    table.add_row("File: ", cert_file_path)
    table.add_row("Aos domain: ", cert.get_subject().organizationName)
    table.add_row("User: ", cert.get_subject().title)
    table.add_row("Serial number: ", f'{cert.get_serial_number():X}')
    table.add_row("Valid not before: ", str(__cert_time_to_time(cert.get_notBefore())))
    table.add_row("Valid not after: ", str(__cert_time_to_time(cert.get_notAfter())))

    console = Console()
    console.print(table)


def create_keys(output_directory, public_file_name, private_file_name):
    """Creates and saves a key pair content in files."""
    p = Path(output_directory)
    p.mkdir(parents=True, exist_ok=True)

    public_key, private_key = __generate_pairs()
    console = Console()
    file_name = p / public_file_name
    with open(file_name, 'wb') as cert:
        cert.write(public_key)
        console.print(f'File {file_name} created', style='green')

    file_name = p / private_file_name
    with open(file_name, 'wb') as key:
        key.write(private_key)
        console.print(f'File {file_name} created', style='green')


def validate_key_certificate(cert_file_path: str, key_file_path: str):
    """ Validate presence and format of user credential files

        Raises:
            UserCredentialsError: If credentials files are in wrong format or with errors
        Returns:
            None
    """
    with open(cert_file_path, "rb") as c, open(key_file_path, "r") as k:
        cert_content = c.read()
        key_content = k.read()

    try:
        private_key_obj = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, key_content.encode("ascii"))
    except OpenSSL.crypto.Error:
        raise Exception('private key is not correct')

    try:
        cert_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_content)
    except OpenSSL.crypto.Error:
        raise Exception('Certificate is not correct: %s' % cert_content)

    context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)
    context.use_privatekey(private_key_obj)
    context.use_certificate(cert_obj)
    try:
        context.check_privatekey()
    except OpenSSL.SSL.Error:
        raise Exception('User private key does not match certificate')
