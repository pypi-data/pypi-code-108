from hashlib import sha256
from collections import OrderedDict


def get_image_hash(image):
    """
    Get the hash value of the `image`.

    Args:
        image (np.ndarray): image in uint8, range [0..255]
    Returns:
        image_hash (str): the hexadecimal hashed value for the image
    """
    return sha256(image).hexdigest()


def get_styling_config_hash(styling_config):
    """
    Get the hash value of the `styling_config`.

    Args:
        styling_config (Bunch): an instance of styling configurations
    Returns:
        styling_config_hash (str): the hexadecimal hashed value for the config
    """
    ordered_config = OrderedDict(sorted(styling_config.items()))

    hasher = sha256()
    for key, value in ordered_config.items():
        hasher.update(bytes(str(key), 'utf-8'))
        hasher.update(bytes(str(value), 'utf-8'))

    return hasher.hexdigest()
