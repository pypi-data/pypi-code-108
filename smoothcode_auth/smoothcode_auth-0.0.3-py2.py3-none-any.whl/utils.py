import hashlib
import hmac


def generate_hmac(secret, base_string, hash_function=hashlib.sha256):
    """
    Generated HMAC for the given base_string and sign it using the given secret using the hash_function as the digest
    :param secret:
    :param base_string:
    :param hash_function:
    :return:
    """
    if isinstance(secret, str):
        secret = secret.encode('UTF-8')

    if isinstance(base_string, str):
        base_string = base_string.encode('UTF-8')

    return hmac.new(secret, base_string, hash_function).hexdigest()
