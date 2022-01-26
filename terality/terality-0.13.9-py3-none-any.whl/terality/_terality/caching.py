from terality._terality.globals import global_client
from contextlib import contextmanager


@contextmanager
def disable_cache():
    terality_client = global_client()
    terality_client.disable_cache()
    try:
        yield
    finally:
        terality_client.enable_cache()
