import six
from clarus import api

class PartWrapper(object):
    def __init__(self, part, response):
        self.__part = part
        self.__response = response
        
        #The requests-toolbelt multipart parser creates headers as byte strings (b'...') but the requests library
        #uses ordinary strings ('...'). To get around this we convert any non-string headers to strings by calling convert_to_str.
        #Both sets of headers are converted this way in case the behaviour of the requests library varies between versions
        response_headers = PartWrapper.convert_to_str(response.headers)
        part_headers = PartWrapper.convert_to_str(part.headers)
        
        self.headers = response_headers.copy()
        self.headers.update(part_headers)
        
        stats = PartWrapper.merge_stats(part_headers, response_headers)
        self.headers[api.STATS] = stats
    
    def __getattr__(self, name):
        if (hasattr(self.__part, name)):
            return getattr(self.__part, name)
        else:
            return getattr(self.__response, name)
       
    @staticmethod 
    def convert_to_str(d):
        return {  k if isinstance(k, six.string_types) else str(k, 'utf-8') 
                : v if isinstance(v, six.string_types) else str(v, 'utf-8') 
                        for (k,v) in d.items()}
        
    @staticmethod
    def merge_stats(part_headers, response_headers):
        if api.STATS in part_headers:
            part_stats = PartWrapper.parse_stats_header(part_headers.get(api.STATS))
        else:
            part_stats = {}
            
        if api.STATS in response_headers:
            response_stats = PartWrapper.parse_stats_header(response_headers.get(api.STATS))
        else:
            response_stats = {}
            
        merged_stats = response_stats
        merged_stats.update(part_stats)
        
        return ';'.join([k+'='+merged_stats[k] for k in merged_stats])
     
    @staticmethod       
    def parse_stats_header(header):
        return dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in header.split(';')))
    