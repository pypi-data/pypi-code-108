#!/usr/bin/env python
from python_crypto.customcrypto import dir_encrypt, dir_decrypt
import sys
from getpass import getpass

DEFAULT_DIR = '.secrets'

def run_command():
    command = sys.argv[1].lower()
    dir = sys.argv[2].lower() if len(sys.argv) >= 3 else DEFAULT_DIR
    if command == 'decrypt':
        password = getpass()
        dir_decrypt(password, dir)
    elif command == 'encrypt':
        password = getpass()
        dir_encrypt(password, dir)
    else:
        print("bad command.")

if __name__ == "__main__":
    run_command()