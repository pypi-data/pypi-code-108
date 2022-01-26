import argparse
import os
import shutil
import sys

from .camanager import CAManager
from .models import DATABASE_FILENAME, DATABASE_FILENAME_BACKUP
from .utils import confirm

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, prog='camanager')

    subparsers = parser.add_subparsers(dest='actions', help='The action')
    setup_subparsers = subparsers.add_parser('setup', help='Initialize the vault')
    backup_subparsers = subparsers.add_parser('backup', help='Backup the vault')
    restore_subparsers = subparsers.add_parser('restore', help='Restore the vault from the backup')
    newcert_subparsers = subparsers.add_parser('newcert', help='Create a new certificate')
    sign_subparsers = subparsers.add_parser('sign', help='Sign a certificate')
    renew_subparsers = subparsers.add_parser('renew', help='Renew a certificate')
    list_subparsers = subparsers.add_parser('list', help='List certificates')
    export_subparsers = subparsers.add_parser('export', help='Export a certificate')
    subparsers.required = True

    newcert_subparsers.add_argument('--cn', help=argparse.SUPPRESS)
    newcert_subparsers.add_argument('--san', help=argparse.SUPPRESS)
    newcert_subparsers.add_argument('--keysize', help=argparse.SUPPRESS)
    newcert_subparsers.add_argument('--hash', help=argparse.SUPPRESS)

    sign_subparsers.add_argument('--cn', help=argparse.SUPPRESS)
    sign_subparsers.add_argument('--san', help=argparse.SUPPRESS)
    sign_subparsers.add_argument('csr_file', nargs='?', help='The CSF filepath')

    renew_subparsers.add_argument('certificate', help='The certificate # or Common Name')

    list_group = list_subparsers.add_mutually_exclusive_group()
    list_group.add_argument('--all_certificates', action='store_true', help='Also the revoked/renewed/expired '
                                                                            'certificates')
    list_group.add_argument('--soon-expired', action='store_true', help='Only the soon expired (> 1 month)')

    export_group = export_subparsers.add_mutually_exclusive_group(required=True)
    export_group.add_argument('--pem', action='store_true', help='PEM output')
    export_group.add_argument('--p12', action='store_true', help='P12 output')
    export_subparsers.add_argument('--out', nargs='?', help='The output file')
    export_subparsers.add_argument('certificate', help='The certificate # or Common Name')

    args = parser.parse_args()

    cam = CAManager()

    if args.actions == 'setup':
        try:
            os.remove(DATABASE_FILENAME)
        except FileNotFoundError:
            pass

        if os.path.isfile(DATABASE_FILENAME):
            msg = f'Error : the database "{DATABASE_FILENAME}" already exists.\n\n' \
                  f'You can remove this file BUT YOU ARE GOING TO LOST EVERYTHING RELATED TO THE CURRENT CERTIFICATE ' \
                  f'AUTHORITY. Be sure of the consequence of your action.'

            sys.stderr.write(f'The database "{DATABASE_FILENAME}" already exists. ')
            exit(-1)

        cam.create_vault()

    elif args.actions == 'backup':
        if not os.path.isfile(DATABASE_FILENAME):
            msg = f'Error : the database "{DATABASE_FILENAME}" not found.' \

            print(msg)
            exit(-1)

        if os.path.isfile(DATABASE_FILENAME_BACKUP):
            msg = f'Error : the database backup "{DATABASE_FILENAME_BACKUP}" already exists.\n\n' \
                  f'You can remove this file BUT YOU ARE GOING TO LOST EVERYTHING RELATED TO THE BACKUP.'

            print(msg)

            if not confirm('Do you to ERASE the previous backup'):
                print('No backup was done')
                exit(0)
            else:
                os.remove(DATABASE_FILENAME_BACKUP)

        shutil.copy(DATABASE_FILENAME, DATABASE_FILENAME_BACKUP)
        print('Backup done successfully')

    elif args.actions == 'restore':
        if not os.path.isfile(DATABASE_FILENAME_BACKUP):
            sys.stderr.write(f'No backup found')
            exit(-1)

        if os.path.isfile(DATABASE_FILENAME):
            msg = f'Warning : YOU ARE GOING TO LOST EVERYTHING RELATED TO THE CURRENT CERTIFICATE AUTHORITY. ' \
                  f'Be sure of the consequence of your action.\n'

            print(msg)

            if not confirm('Do you you want to restore the backup'):
                print('The backup has NOT been restored')
                exit(0)
            else:
                os.remove(DATABASE_FILENAME)

        shutil.copy(DATABASE_FILENAME_BACKUP, DATABASE_FILENAME)

        print('Backup restored successfully')

        if not confirm('Do you want to keep the backup'):
            os.remove(DATABASE_FILENAME_BACKUP)
            print('Backup file deleted successfully')

    elif args.actions == 'newcert':
        cam.load()
        cam.generate_new_cert()

    elif args.actions == 'sign':
        cam.load()
        cam.sign_csr(args.csr_file, args.cn, args.san)

    elif args.actions == 'renew':
        cam.load()
        cam.renew(args.certificate)
        # cam.sign_csr(args.csr_file)

    elif args.actions == 'list':
        cam.load()
        cam.list(args.all_certificates, args.soon_expired)

    elif args.actions == 'export':
        cam.load()
        cam.export(args.certificate, "p12" if args.p12 else "pem", args.out)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n*** Interrupted by user ***')
