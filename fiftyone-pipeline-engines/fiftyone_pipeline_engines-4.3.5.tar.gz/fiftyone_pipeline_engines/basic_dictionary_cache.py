from fiftyone_pipeline_engines.datakeyed_cache import DataKeyedCache

class BasicDictionaryCache(DataKeyedCache):

    """!
    A simple cache that stores its results in a dictionary
        
    """
    
    def __init__(self):

        self.cache = {}

    def get_cache_value(self, key):
       
        """!
        Get the result stored in the cache or None
        @type key : string
        @param key : The cache key to lookup
        @rtype mixed
        @return None or the data stored in the cache
        
        """

        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def set_cache_value(self, key, value):

        """!
        Add data to the cache under a key
        @type key : string
        @param key : The cache key to store data under
        @type value : mixed
        @param key : The value to save in the cache
        
        """

        self.cache[key] = value
