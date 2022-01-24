import os, sys

from urllib.parse import urlparse, uses_netloc
from redis import Redis
from cc_py_commons.config.env import app_config

if not app_config.LOCATION_REDIS_URL:
  raise RuntimeError('Set up Location Redis first.')

if not app_config.DISTANCE_CACHE_URL:
  raise RuntimeError('Set up Distance Cache first.')

if not app_config.TIMEZONE_CACHE_URL:
  raise RuntimeError('Set up Timezone Redis first.')

uses_netloc.append('redis')
_location_redis_url = urlparse(app_config.LOCATION_REDIS_URL)
_distance_cache_url = urlparse(app_config.DISTANCE_CACHE_URL)
_timezone_redis_url = urlparse(app_config.TIMEZONE_CACHE_URL)

location_db_conn = Redis(host=_location_redis_url.hostname, port=_location_redis_url.port, db=0, password=app_config.LOCATION_REDIS_PWD)

distance_db_conn = Redis(host=_distance_cache_url.hostname, port=_distance_cache_url.port, password=app_config.DISTANCE_CACHE_PASSWORD)

timezone_db_conn = Redis(host=_timezone_redis_url.hostname, port=_timezone_redis_url.port, db=0, password=app_config.TIMEZONE_CACHE_PASSWORD)
