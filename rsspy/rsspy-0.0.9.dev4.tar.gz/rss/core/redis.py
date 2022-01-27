from redis  import Redis
from authc import authc
from typing import List, Dict, Tuple, Set, Optional, Union

class RedisClient(Redis):
    def __init__(self, host, port, password):
        super().__init__(host=host, port=port, password=password)
    
    def get_key(self, key)->str:
        return self.get(key)

    def set_key(self, key:str, value:str, *args, **kwargs):
        return self.set(key, value, *args, **kwargs)
    
    def get_keys(self, pattern)->List[str]:
        return self.keys(pattern)

    def get_keys_with_scores(self, pattern)->List[Tuple[str, float]]:
        return self.zrange(pattern, 0, -1, withscores=True)


