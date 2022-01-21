import pytz
from typing import Callable
from c27cache.datetime_support import (
    end_of_day,
    tz_now,
    asia_kolkata,
    end_of_week,
)
from c27cache.config import C27Cache


class C27CacheExpiry:
    @staticmethod
    async def get_ttl(
        ttl_in_seconds: int = None,
        end_of_day: bool = True,
        end_of_week: bool = None,
        ttl_func: Callable = None,
        tz: pytz.timezone = asia_kolkata,
    ) -> int:
        """Return the seconds till expiry of cache. Defaults to one day"""
        tz = C27Cache.tz or tz
        
        if ttl_func:
            return await ttl_func()

        if ttl_in_seconds:
            return ttl_in_seconds

        if end_of_day:
            return await C27CacheExpiry.expires_end_of_day(tz=tz)

        if end_of_week:
            return await C27CacheExpiry.expires_end_of_week(tz=tz)
        return 86400

    @staticmethod
    async def expires_end_of_week(tz=asia_kolkata) -> int:
        """Returns the seconds till expiry at the end of the week"""
        now = tz_now()
        local_time = now.astimezone(tz=tz)
        eow = end_of_week(dt=local_time)
        return int((eow - local_time).total_seconds())

    @staticmethod
    async def expires_end_of_day(tz=asia_kolkata) -> int:
        """Returns the seconds till expiry at the end of the day"""
        now = tz_now()
        local_time = now.astimezone(tz=tz)
        eod = end_of_day(dt=local_time)
        return int((eod - local_time).total_seconds())
