import functools
from time import sleep

from lusid_drive import ApiException


def lusid_drive_retry(fn):
    @functools.wraps(fn)
    def __retry(*args, **kwargs):

        retries = kwargs.get("lusid_drive_retries", 3)
        if not isinstance(retries, int):
            retries = 3

        tries = 0
        while tries < retries:
            try:
                return fn(*args, **kwargs)
            except ApiException as ex:

                tries += 1

                retry_after = ex.headers.get("Retry-After") if ex.headers else None

                if ex.status == 423:
                    retry_after = 10

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
