from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from messenger2.common.security.keys import get_server_private_key, get_private_key


def get_info(key, data):
    """
    decrypt data with private key
    :param key: rsa key
    :param data: encrypted data
    :return: decrypted data
    """
    enc_session_key, nonce, tag, enc_text = data[:key.size_in_bytes()], data[key.size_in_bytes(
    ):][:16], data[key.size_in_bytes():][16:][:16], data[key.size_in_bytes():][16:][16:]
    rsa = PKCS1_v1_5.new(key=key)
    session_key = rsa.decrypt(enc_session_key, sentinel=None)
    print(session_key)
    aes = AES.new(session_key, AES.MODE_EAX, nonce)
    text = aes.decrypt_and_verify(enc_text, tag)

    return text


def decript_data(username, data):
    """
    decrypt data on client side
    :param username: user login
    :param data: encrypted data
    :return: decrypted data
    """
    username_pk = get_private_key(username)
    return get_info(username_pk, data)


def decript_server_data(data):
    """
    decrypt data on server side
    :param data: encrypted data
    :return: decrypted data
    """
    server_pk = get_server_private_key()
    return get_info(server_pk, data)


if __name__ == "__main__":
    pass
