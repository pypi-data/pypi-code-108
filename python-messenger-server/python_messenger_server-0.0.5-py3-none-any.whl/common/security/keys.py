from Crypto.PublicKey import RSA
import os
from messenger2.protocols.JIM import JIM
from messenger2 import config

SERVER_KEYS_DIR = os.path.join(config.SERVER_DIR, "server_keys")
CLIENT_KEYS_DIR = os.path.join(config.CLIENT_DIR, "client_keys")


def generate_pair(username, is_client=True):
    """
    generate rsa keys if they are not created
    :param username: login
    :param is_client: bool value if we check on server or client side
    :return: None
    """
    dir = CLIENT_KEYS_DIR
    if not is_client:
        dir = SERVER_KEYS_DIR
        username = "server"
    try:
        files = os.listdir(dir)
    except FileNotFoundError:
        os.mkdir(dir)
        files = os.listdir(dir)
    if f"public_{username}.pem" and f"private_{username}.pem" in files:
        print("keys are already exists")
    else:
        key = RSA.generate(2048)
        with open(os.path.join(dir, f"private_{username}.pem"), "wb") as f:
            f.write(key.export_key())

        with open(os.path.join(dir, f"public_{username}.pem"), "wb") as f:
            f.write(key.public_key().export_key())


def get_public_key(username, to_str=False):
    """
    get public key from client side
    :param username: login
    :param to_str: bool to get str instead of rsa object
    :return: rsa object, string or None if there is no key
    """
    try:
        key = RSA.import_key(
            open(
                os.path.join(
                    CLIENT_KEYS_DIR,
                    f"public_{username}.pem")).read())
        if to_str:
            key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
        return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_private_key(username, to_str=False):
    """
    get private key from client side
    :param username: login
    :param to_str: bool to get str instead of rsa object
    :return: rsa object, string or None if there is no key
    """
    try:
        key = RSA.import_key(
            open(
                os.path.join(
                    CLIENT_KEYS_DIR,
                    f"private_{username}.pem")).read())
        if to_str:
            key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
        return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_server_public_key(to_str=False):
    """
    get public key from server
    :param to_str: bool to get str instead of rsa object
    :return: rsa object, string or None if there is no key
    """
    try:
        with open(os.path.join(SERVER_KEYS_DIR, "public_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_client_server_public_key(to_str=False):
    """
    get public server key from client side
    :param to_str: bool to get str instead of rsa object
    :return: rsa object, string or None if there is no key
    """
    try:
        with open(os.path.join(CLIENT_KEYS_DIR, "public_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_server_private_key(to_str=False):
    """
    get private server key from server side
    :param to_str: bool to get str instead of rsa object
    :return: rsa object, string or None if there is no key
    """
    try:
        with open(os.path.join(SERVER_KEYS_DIR, "private_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def save_server_public_key(server_pk):
    """
    save public server key onn client side
    :param server_pk: public rsa server key string
    :return: None
    """
    with open(os.path.join(CLIENT_KEYS_DIR, "public_server.pem"), "wb") as server_key:
        server_key.write(bytes(server_pk, encoding=JIM.ENCODING))


if __name__ == "__main__":
    generate_pair("server")
