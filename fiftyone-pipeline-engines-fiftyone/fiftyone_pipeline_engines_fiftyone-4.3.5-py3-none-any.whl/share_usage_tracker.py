 # *********************************************************************
 # This Original Work is copyright of 51 Degrees Mobile Experts Limited.
 # Copyright 2019 51 Degrees Mobile Experts Limited, 5 Charlotte Close,
 # Caversham, Reading, Berkshire, United Kingdom RG4 7BY.
 #
 # This Original Work is licensed under the European Union Public Licence (EUPL) 
 # v.1.2 and is subject to its terms as set out below.
 #
 # If a copy of the EUPL was not distributed with this file, You can obtain
 # one at https://opensource.org/licenses/EUPL-1.2.
 #
 # The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
 # amended by the European Commission) shall be deemed incompatible for
 # the purposes of the Work and the provisions of the compatibility
 # clause in Article 5 of the EUPL shall not apply.
 # 
 # If using the Work as, or as part of, a network application, by 
 # including the attribution notice(s) required under Article 5 of the EUPL
 # in the end user terms of the application under an appropriate heading, 
 # such notice(s) shall fulfill the requirements of that article.
 # ********************************************************************

from fiftyone_pipeline_engines.tracker import Tracker
from cachetools import LRUCache

import time

class ShareUsageTracker(Tracker):
    """!
    The ShareUsageTracker is used by the ShareUsageElement to determine
    whether to put evidence into a bundle to be sent to the 51Degrees
    Share Usage service.
    """

    def __init__(self, size = 100, interval = 1000):
        """!
        Constructor for ShareUsageTracker
        @type size: int
        @param size: size of the share usage lru cache
        @type interval: int
        @param interval: how often to put evidence into the cache

        """

        self.interval = interval
        
        self.cache = LRUCache(maxsize=size)

    def match(self, key, value):
        """!
        The track method calls the dataKeyedCache get method,
        if it receives a result it sends it onto a match function
        
        @type key : cache key to run through tracker
        @rtype bool 
        @return result of tracking

        """

        difference = time.time() - value

        if difference > self.interval:
            self.set_cache_value(key, value)
            return True
        else:
            return False


    def get_cache_value(self, cachekey):
        
        """!
        Get data from the cache
        @type key : string
        @param key : The cache key to lookup
        @type value : mixed
        @param key : None , or the stored data
        """

        return self.cache.get(cachekey)

    def set_cache_value(self, cachekey, value = None):

        """!
        Place data in the cache
        @type key : string
        @param key : The cache key to store data under
        @type value : mixed
        @param key : Not used here as value is set to the date

        """
        
        self.cache.__setitem__(cachekey, time.time())
