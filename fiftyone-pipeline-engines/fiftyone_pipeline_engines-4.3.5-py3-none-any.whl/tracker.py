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

from .datakeyed_cache import DataKeyedCache

class Tracker(DataKeyedCache):
    
    """!
    A tracker is an instance of datakeyed cache which,
    if a result is found in the cache, calls an additional
    boolean match method
    """
    
    def track(self, key):

        """!
        The track method calls the DataKeyedCache get method,
        if it receives a result it sends it onto a match function
        
        @type key : cache key to run through tracker
        @rtype bool 
        @return result of tracking

        """

        if self.get_cache_value(key) is None:

            return True

        else:

            return self.match(key, self.get_cache_value(key)) # pylint: disable=E1121

    def match(self, result):

        """!
        If object is found in cache, the match function is called
        
        @type key : result of the track function
        @rtype bool 
        @return whether a match has been made

        """

        return True

