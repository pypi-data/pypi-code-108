from cachetools import cached, TTLCache
from cachetools.keys import hashkey

from random import randint

import os

CACHE_MAXSIZE = int(os.environ.get('TOKEN_CACHE_MAXSIZE', "1024"))
CACHE_TTL = int(os.environ.get('TOKEN_CACHE_TTL', "300"))

# @cached(TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL), key=lambda db_handle, query: hashkey(query))
# def find_object(db_handle, query):
#     print("processing {0} {1}".format(db_handle, query))
#     return query


# @cachetools.func.ttl_cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
@cached(TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL), key=lambda table_id, root_id, token: hashkey(table_id, root_id))
def is_root_public(table_id, root_id, token):
  print("is_root_public", table_id, root_id, token)
  return True

queries = list(range(5))
queries.extend(range(5))
for q in queries:
    print("result: {0}".format(is_root_public(q, q, randint(0, 1000))))


print("result: {0}".format(is_root_public(3, 3, randint(0, 1000))))