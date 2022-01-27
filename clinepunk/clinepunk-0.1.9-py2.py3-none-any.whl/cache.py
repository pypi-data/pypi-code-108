import datetime
import logging

import diskcache


def cache(cache_path, fcn_refresh, key) -> str:
    with diskcache.Cache(cache_path) as reference:
        logging.debug(f"fetching cache from {key}")
        if not reference.get(key):
            logging.debug("setting cache")
            buffer = fcn_refresh()
            reference.set(
                key,
                buffer,
                expire=datetime.timedelta(days=365 * 2).total_seconds(),
            )
        logging.debug("cache is still fresh, using it")
        return reference.get(key)
