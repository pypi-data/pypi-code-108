#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

import argparse
import logging
import sys
from pathlib import Path, PurePath

from rich.console import Console

from aos_keys import __version__, DEFAULT_OEM_PATH, DEFAULT_SP_PATH
from aos_keys.actions import UserType, new_token_user, convert_pkcs12_file_to_pem, install_root_ca
from aos_keys.cloud_api import print_user_info
from aos_keys.key_manager import show_cert_info
from aos_keys.errors import AosKeysError

logger = logging.getLogger(__name__)

__COMMAND_INFO = 'info'
__COMMAND_NEW_USER = 'new-user'
__COMMAND_TO_PEM = 'to-pem'
__COMMAND_INSTALL_ROOT_CA = 'install-root'


def _parse_args():
    parser = argparse.ArgumentParser(description="Work with keys. Create new keys, receive certificates, show info",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sub_parser = parser.add_subparsers(title='Commands')

    new_user_command = sub_parser.add_parser(__COMMAND_NEW_USER, help='Create new key pairs and receive certificate')
    new_user_command.set_defaults(which=__COMMAND_NEW_USER)
    new_user_command.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=str(Path.home() / '.aos' / 'security'),
        help="Output directory to save certificate."
    )

    new_user_command.add_argument(
        "-d", "--domain",
        dest="register_domain",
        default='aoscloud.io',
        help="Aos Cloud domain to register user keys"
    )

    new_user_command.add_argument(
        "-t", "--token",
        dest="token",
        help="Authorization token. If token is given you will not be prompted for user name and password"
    )

    new_user_command.add_argument(
        "-oem", "--oem",
        action='store_true',
        help="Create only OEM user key/certificate"
    )

    new_user_command.add_argument(
        "-s", "--sp",
        action='store_true',
        help="Create only Service Provider user key/certificate"
    )

    new_user_command.add_argument(
        "-e", "--ecc",
        action='store_true',
        help="Create ECC key instead of RSA"
    )

    info_command = sub_parser.add_parser(__COMMAND_INFO, help='Show certificate / user information')
    info_command.set_defaults(which=__COMMAND_INFO)
    info_command.add_argument("-c", "--certificate", dest="cert_file_name", help="Certificate file to inspect")
    info_command.add_argument("-s", "--sp", action='store_true',
                              help="Show info of default Service Provider user certificate")
    info_command.add_argument("-o", "--oem", action='store_true', help="Show info of default OEM user certificate")

    pem_command = sub_parser.add_parser(
        __COMMAND_TO_PEM,
        help='Convert pkcs12 container to PEM key and certificates chain'
    )
    pem_command.set_defaults(which=__COMMAND_TO_PEM)
    pem_command.add_argument("-c", "--certificate", dest="cert_file_name", required=True, help="pkcs12 file to convert")
    pem_command.add_argument("-o", "--output-dir", dest="output_dir",
                             default=str(Path.home() / '.aos' / 'security'),
                             help="Output directory to save certificate.")

    ca_command = sub_parser.add_parser(__COMMAND_INSTALL_ROOT_CA, help='Install root CA')
    ca_command.set_defaults(which=__COMMAND_INSTALL_ROOT_CA)

    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    return parser.parse_args()


def main():
    args = _parse_args()
    console = Console()

    try:
        if not hasattr(args, 'which'):
            sys.exit(0)
        elif args.which == __COMMAND_INSTALL_ROOT_CA:
            install_root_ca()
        elif args.which == __COMMAND_INFO:
            if args.sp:
                cert_file_name = DEFAULT_SP_PATH
                console.print(f'Info about default SP user:', style="bold")
                console.print(f'Path to certificate: [bold]{cert_file_name}[/bold]\n')
            elif args.oem:
                cert_file_name = DEFAULT_OEM_PATH
                console.print(f'Info about default OEM user:', style="bold")
                console.print(f'Path to certificate: [bold]{cert_file_name}[/bold]\n')
            elif args.cert_file_name:
                cert_file_name = args.cert_file_name
            else:
                console.print(f'User certificates in the default path not found', style="bold")
                console.print(f'Issue new certificate or or set path to certificate with -c key')
                sys.exit(1)
            show_cert_info(cert_file_name)
            print_user_info(cert_file_name)
            sys.exit(0)
        elif args.which == __COMMAND_NEW_USER:
            if args.oem:
                user_type = UserType.OEM.value
            elif args.sp:
                user_type = UserType.SP.value
            else:
                print('Set one of --sp or --oem param')
                sys.exit(1)
            new_token_user(args.register_domain, args.output_dir, args.token, user_type, args.ecc)
            sys.exit(0)
        elif args.which == __COMMAND_TO_PEM:
            convert_pkcs12_file_to_pem(args.cert_file_name, args.output_dir)
            sys.exit(0)
    except AosKeysError as ake:
        ake.print_message()
        sys.exit(1)
    except Exception as sce:
        print('Process failed with error: ' + str(sce))
        print(sce)
        sys.exit(1)


if __name__ == '__main__':
    main()
