#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import os
import tempfile

import importlib_resources as pkg_resources
import requests
from rich.console import Console
from rich.table import Table

from aos_keys.key_manager import extract_cloud_domain_from_cert, pkcs12_to_pem_bytes

__ME_CERT_ENDPOINT = 'https://{}:10000/api/v1/users/me/'
__UPLOAD_USER_CERTIFICATE = 'https://{}/api/v3/user-certificates/'

__FILES_DIR = 'aos_keys'
__ROOT_CA_CERT_FILENAME = 'files/1rootCA.crt'


def print_user_info(pkcs12_path: str):
    user_info = get_user_info_by_cert(pkcs12_path)
    table = Table(padding=0, title='Cloud user info', show_header=False)
    table.add_column("", no_wrap=True, justify="left", style="", width=19)
    table.add_column("")
    table.add_row("User name: ", user_info.get('username'))
    table.add_row("email: ", user_info.get('email'))
    table.add_row("role: ", user_info.get('role'))
    if user_info.get('role') == 'oem':
        table.add_row("OEM Title: ", user_info.get('oem').get('title'))
    elif user_info.get('role') == 'service provider':
        table.add_row("SP Title: ", user_info.get('service_provider').get('title'))
    table.add_row("Is active: ", str(user_info.get('is_active')))
    table.add_row("Permissions: ", '\n'.join(user_info.get('permissions')))
    console = Console()
    console.print(table)


def get_user_info_by_cert(pkcs12_path: str):
    with open(pkcs12_path, 'rb') as pkcs12_file:
        cert_bytes, pk_bytes = pkcs12_to_pem_bytes(pkcs12_file.read())

    pem_cert_file = tempfile.NamedTemporaryFile(delete=False)
    pem_cert_file.write(cert_bytes)
    pem_cert_file.close()

    pem_key_file = tempfile.NamedTemporaryFile(delete=False)
    pem_key_file.write(pk_bytes)
    pem_key_file.close()

    session = requests.Session()
    session.cert = (pem_cert_file.name, pem_key_file.name)
    server_certificate = pkg_resources.files(__FILES_DIR) / __ROOT_CA_CERT_FILENAME
    with pkg_resources.as_file(server_certificate) as server_certificate_path:
        data = session.get(
            __ME_CERT_ENDPOINT.format(extract_cloud_domain_from_cert(pkcs12_path)),
            verify=server_certificate_path,
        )
        os.unlink(pem_cert_file.name)
        os.unlink(pem_key_file.name)
        data.raise_for_status()
        return data.json()


def receive_certificate_by_token(domain, token, csr):
    server_certificate = pkg_resources.files(__FILES_DIR) / __ROOT_CA_CERT_FILENAME
    with pkg_resources.as_file(server_certificate) as server_certificate_path:
        upload_response = requests.post(
            __UPLOAD_USER_CERTIFICATE.format(domain),
            json={"csr": csr},
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "Referer": 'https://{}'.format(domain),
                'Authorization': f'Token {token}'
            },
            verify=server_certificate_path,
        )

        upload_response.raise_for_status()
        return upload_response.json()['certificate']
