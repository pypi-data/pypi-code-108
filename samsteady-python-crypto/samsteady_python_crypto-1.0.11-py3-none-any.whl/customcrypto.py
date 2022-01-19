import hashlib

from AesEverywhere import aes256
from aws_encryption_sdk.exceptions import DecryptKeyError
from python_crypto.awscrypto import encrypt, decrypt
from shutil import copyfile, copytree, rmtree
import os


def hash_value(v):
    return hashlib.sha224(bytes(v, 'utf-8')).hexdigest()

def password_encrypt(plaintext, password):
    safe_pass = password.strip()
    return aes256.encrypt(plaintext, safe_pass)

def password_decrypt(ciphertext, password):
    safe_pass = password.strip()
    return aes256.decrypt(ciphertext, safe_pass).decode("utf-8")

def _replace_in_bytes(byte_str, old, new):
    start_ind = byte_str.find(old)
    return byte_str[:start_ind] + new + byte_str[start_ind+len(old):]

def double_encrypt(plaintext, password, context={}):
    safe_pass = password.strip()
    hashed_pass = hash_value(safe_pass)
    aws_cipher = encrypt(plaintext, encryption_context={
        'pass': hashed_pass,
        **context,
    })
    stripped_cipher = _replace_in_bytes(aws_cipher, bytes(hashed_pass, 'utf-8'), b'{PASS}')
    return stripped_cipher

class BadEncryptionPassword(Exception):
    pass

def double_decrypt(stripped_ciphertext, password):
    safe_pass = password.strip()
    hashed_pass = hash_value(safe_pass)
    ciphertext = _replace_in_bytes(stripped_ciphertext, b'{PASS}', bytes(hashed_pass, 'utf-8'))
    try:
        plaintext = decrypt(ciphertext)
    except DecryptKeyError as e:
        raise BadEncryptionPassword
    return plaintext


def _get_encryption_method(method_name):
    method_name = method_name.lower()
    if method_name == "double_encrypt":
        return double_encrypt
    elif method_name == "double_decrypt":
        return double_decrypt
    elif method_name == "password_encrypt":
        return password_encrypt
    elif method_name == "password_decrypt":
        return password_decrypt
    elif method_name == "aws_encrypt":
        return encrypt
    elif method_name == "aws_decrypt":
        return decrypt

def file_encrypt(from_path, to_path, password=None, method="double_encrypt", **kwargs):
    method = _get_encryption_method(method)
    from_file = open(from_path, 'r')
    lines = ''.join(from_file.readlines())
    from_file.close()
    if password:
        ciphertext = method(lines, password, **kwargs)
    else:
        ciphertext = method(lines, **kwargs)
    to_file = open(to_path, 'wb')
    to_file.write(ciphertext)
    to_file.close()

def file_decrypt(from_path, to_path, password=None, method="double_decrypt", **kwargs):
    method = _get_encryption_method(method)
    from_file = open(from_path, 'rb')
    ciphertext = from_file.read()
    from_file.close()
    if password:
        plaintext = method(ciphertext, password, **kwargs)
    else:
        plaintext = method(ciphertext, **kwargs)
    to_file = open(to_path, 'w')
    to_file.write(plaintext)
    to_file.close()



def dir_encrypt(password, dir_name, **kwargs):
    status_file = f'{dir_name}/.status'
    state = "decrypted"
    try:
        status = open(status_file, "r")
        state = status.readline().strip()
        status.close()
    except:
        pass
    if state == "decrypted":
        status = open(status_file, "w")
        status.write("encrypted\n")
        status.close()
        backup_dir = f'{dir_name}.backup'
        copytree(dir_name, backup_dir)
        try:
            for dirpath, subdirs, files in os.walk(dir_name):
                for filename in files:
                    from_path = os.path.join(dirpath, filename)
                    if ".DS_Store" in from_path or '.status' in from_path or '.git' in from_path:
                        continue
                    print(from_path)
                    to_path = f'{from_path}.temp'
                    file_encrypt(from_path, to_path, password, **kwargs)
                    os.remove(from_path)
                    copyfile(to_path, from_path)
                    os.remove(to_path)
        except Exception as e:
            rmtree(dir_name)
            copytree(backup_dir, dir_name)
            rmtree(backup_dir)
            status = open(status_file, "w")
            status.write("decrypted\n")
            status.close()
            raise e
        rmtree(backup_dir)


def dir_decrypt(password, dir_name, **kwargs):
    status_file = f'{dir_name}/.status'
    state = "decrypted"
    try:
        status = open(status_file, "r")
        state = status.readline().strip()
        status.close()
    except:
        pass
    if state == "encrypted":
        backup_dir = f'{dir_name}.backup'
        copytree(dir_name, backup_dir)
        try:
            for dirpath, subdirs, files in os.walk(dir_name):
                for filename in files:
                    to_path = os.path.join(dirpath, filename)
                    if ".DS_Store" in to_path or '.status' in to_path or '.git' in to_path:
                        continue
                    print(to_path)
                    from_path = f'{to_path}.temp'
                    copyfile(to_path, from_path)
                    os.remove(to_path)
                    file_decrypt(from_path, to_path, password, **kwargs)
                    os.remove(from_path)
            status = open(status_file, "w")
            status.write("decrypted\n")
            status.close()
        except Exception as e:
            rmtree(dir_name)
            copytree(backup_dir, dir_name)
            rmtree(backup_dir)
            raise e
        rmtree(backup_dir)

