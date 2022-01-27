import uuid
import hashlib
import os


def create_uuid():
    """ create a uuid (universally unique ID) """
    md5_hash = hashlib.md5(uuid.uuid1().bytes)
    return md5_hash.hexdigest()


def get_hash_code(file):
    """ get the md5 hash code of a given file """
    assert os.path.exists(file)
    md5_hash = hashlib.md5()
    with open(file, "rb") as fid:
        md5_hash.update(fid.read())
        digest = md5_hash.hexdigest()
    return digest


def is_black_distribution(distribution):
    """ Check if the distribution is implying a black instance (used in data.update()) """
    return all([x < 0 for x in distribution])

