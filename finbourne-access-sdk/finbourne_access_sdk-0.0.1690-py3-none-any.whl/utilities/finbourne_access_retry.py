import functools
from time import sleep

from finbourne_access import ApiException


def finbourne_accessretry(fn):

    @functools.wraps(fn)
    def __retry(*args, **kwargs):

        retries = kwargs.get("finbourne_access_retries", 3)
        if not isinstance(retries, int):
            retries = 3

        tries = 0
        while tries < retries:
            try:
                return fn(*args, **kwargs)
            except ApiException as ex:

                tries += 1
                retry_after = ex.headers.get("Retry-After")

                # have done max number of retries
                if tries == retries:
                    raise

                # try after delay
                elif retry_after is not None:
                    sleep(retry_after)

                # no retry header
                else:
                    raise

    return __retry
