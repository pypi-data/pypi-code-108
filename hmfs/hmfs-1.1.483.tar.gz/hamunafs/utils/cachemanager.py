
import os
import json
from diskcache import Cache
from hamunafs.utils.redisutil import XRedis
from hamunafs.utils.singleton_wrapper import Singleton


class CacheManager(Singleton):
    def __init__(self, host, password, port, db=2, local_cache='../cache'):
        if not self.need_init():
            return
        self.client = XRedis(host, password, port, db=db)
        
        if local_cache is not None:
            os.makedirs(local_cache, exist_ok=True)
            self.local_cache = Cache(local_cache)
        self._inited = True
    
    def cache(self, key, val, enable_local_cache=True, expired=7200, encode=True):
        if not isinstance(val, str) and encode:
            cache_val = json.dumps(val)
        else:
            cache_val = val
        
        if enable_local_cache and hasattr(self, 'local_cache'):
            self.local_cache.set(key, cache_val, expired)
        
        self.client.set(key, cache_val, expired)

    def refresh_time(self, key, expired):
        self.client.set_expire_time(key, expired)
    
    def remove(self, key):
        self.client.delkey(key)
        self.local_cache.delete(key, retry=True)

    def get_cache(self, key, return_obj=True):
        cache_str = self.local_cache.get(key) if hasattr(self, 'local_cache') else None
        if cache_str is None:
            cache_str = self.client.get(key)
            if return_obj and cache_str is not None:
                return json.loads(cache_str)
        else:
            if isinstance(cache_str, str):
                if return_obj:
                    return json.loads(cache_str)
        return cache_str
    
    async def get_cache_async(self, key, return_obj=True):
        cache_str = self.local_cache.get(key) if hasattr(self, 'local_cache') else None
        if cache_str is None:
            cache_str = self.client.get(key)
            if return_obj and cache_str is not None:
                return json.loads(cache_str)
        else:
            if isinstance(cache_str, str):
                if return_obj:
                    return json.loads(cache_str)
        return cache_str
    
    def set_cache_reload_tag(self, tag):
        self.client.hash_set('cache_reload_tags', tag, '1')

    def lock(self, lock_key, ttl=60):
        return self.client.lock(lock_key, ttl)
    
    def zset(self, z_name, key, val):
        self.client.zadd(z_name, key, val)
    
    def zrange(self, z_name, min, max):
        return self.client.zrange(z_name, min, max)
    
    def zcount(self, z_name, min, max):
        return self.client.zcount(z_name, min, max)
    
    def zrem(self, z_name, key):
        self.client.zrem(z_name, key)
        
    def zscore(self, z_name, key):
        return self.client.zscore(z_name, key)
    
    def get_pipeline(self):
        return self.client._get_connection(pipeline=True)

