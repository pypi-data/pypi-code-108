#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import subprocess
from enum import Enum
from pathlib import Path
import platform

import importlib_resources as pkg_resources
from rich.console import Console

from aos_keys import DEFAULT_OEM_FILE_NAME, DEFAULT_SP_FILE_NAME
from aos_keys.cloud_api import receive_certificate_by_token, __FILES_DIR, __ROOT_CA_CERT_FILENAME
from aos_keys.key_manager import generate_pair, save_pkcs_container, generate_pair_rsa, pkcs12_to_pem_bytes
from aos_keys.errors import AosKeysError


class UserType(Enum):
    SP = 'sp'
    OEM = 'oem'
    ADMIN = 'admin'


def install_root_ca():
    if platform.system() == 'Windows':
        server_certificate = pkg_resources.files(__FILES_DIR) / __ROOT_CA_CERT_FILENAME
        with pkg_resources.as_file(server_certificate) as server_certificate_path:
            command = f'certutil -addstore -f "ROOT" {server_certificate_path}'
            completed_process = subprocess.run(command, shell=True)
    elif platform.system() == 'Linux':
        command = f'dpkg -s update-ca-certificates'
        completed_process = subprocess.run(command, shell=True)
        if completed_process.returncode > 0:
            print('Install update-ca-certificates first with command: sudo apt install ca-certificates')
            return 1

        server_certificate = pkg_resources.files(__FILES_DIR) / __ROOT_CA_CERT_FILENAME
        with pkg_resources.as_file(server_certificate) as server_certificate_path:
            if not Path('/usr/local/share/ca-certificates/').exists():
                command = f'sudo mkdir /usr/local/share/ca-certificates/'
                completed_process = subprocess.run(command, shell=True)
            if not Path('/usr/local/share/ca-certificates/1rootCA.crt').exists():
                command = f'sudo cp {server_certificate_path} /usr/local/share/ca-certificates/1rootCA.crt'
                completed_process = subprocess.run(command, shell=True)
            command = f'sudo update-ca-certificates'
            completed_process = subprocess.run(command, shell=True)


def new_token_user(domain: str, output_directory: str, auth_token: str, user_type: UserType, create_ecc_key):
    console = Console()
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    if user_type == UserType.SP.value:
        file_path = Path(output_directory) / DEFAULT_SP_FILE_NAME
    elif user_type == UserType.OEM.value:
        file_path = Path(output_directory) / DEFAULT_OEM_FILE_NAME
    else:
        raise AosKeysError('Unsupported user role!')

    if file_path.exists():
        raise AosKeysError(f'File [{file_path}] exists. Cannot proceed!')

    if create_ecc_key:
        private_key_bytes, csr = generate_pair()
    else:
        private_key_bytes, csr = generate_pair_rsa()

    user_certificate = receive_certificate_by_token(domain, token=auth_token, csr=csr)
    save_pkcs_container(private_key_bytes, user_certificate, file_path)
    console.print(f'Done!', style='green')


def convert_pkcs12_file_to_pem(pkcs12_path: str, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    console = Console()
    cert_file_name = Path(output_dir) / 'user-certificate.pem'
    key_file_name = Path(output_dir) / 'user-key.pem'

    if not Path(pkcs12_path).exists():
        raise AosKeysError(f'File {pkcs12_path} not found. Cannot proceed!')

    for file_name in (cert_file_name, key_file_name):
        if file_name.exists():
            raise AosKeysError(f'Destination file {file_name} exists. Cannot proceed!')

    with open(pkcs12_path, 'rb') as pkcs12_file:
        cert_bytes, key_bytes = pkcs12_to_pem_bytes(pkcs12_file.read())

    with open(cert_file_name, "wb") as cert:
        cert.write(cert_bytes)
        console.print(f'File created: {cert_file_name}!', style='green')

    with open(key_file_name, "wb") as key:
        key.write(key_bytes)
        console.print(f'File created: {key_file_name}!', style='green')

    console.print(f'Done!', style='green')
