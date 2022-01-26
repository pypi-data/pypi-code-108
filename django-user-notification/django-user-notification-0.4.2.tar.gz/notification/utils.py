from base64 import b64encode
from decorator import wraps


def make_etag(*args):
    """
    Generate custom etag
    """
    return "-".join(b64encode(tag.encode("utf-8")).decode("utf-8") for tag in args)

