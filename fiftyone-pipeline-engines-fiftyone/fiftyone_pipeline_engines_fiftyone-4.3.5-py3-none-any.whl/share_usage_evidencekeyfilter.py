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

from fiftyone_pipeline_core.basiclist_evidence_keyfilter import BasicListEvidenceKeyFilter

class ShareUsageEvidenceKeyFilter(BasicListEvidenceKeyFilter):
    """
    The ShareUsageEvidenceKeyFilter filters out all evidence 
    not needed by the 51Degrees ShareUsage service.
    It allows for a specific whitelist of query strings,
    a blacklist of headers and a specific cookie used for 
    session information
    """

    def __init__(self, cookie = None, query_whitelist = [], header_blacklist = []):
        """!
        Constructor for ShareUsageEvidenceKeyFilter
        @type cookie: string
        @param cookie: which cookie is used to track evidence
        @type query_whitelist: list
        @param query_whitelist: list of query string whitelist evidence to keep
        @type query_blacklist: list
        @param query_blacklist: list of header evidence to exclude
        @type 
        @param
        """
        self.query_whitelist = query_whitelist

        self.header_blacklist = header_blacklist

        self.cookie = cookie

    
    def filter_evidence_key(self, key):

        """!
        Check if a specific key should be filtered.

        @type key: string
        @param key: to check in the filter

        @rtype: bool
        @return: Is this key in the filter's keys list?

        """

        #  get prefix and key of evidence

        key_parts = key.lower().split(".")

        prefix = key_parts[0]
        body = key_parts[1]

        # First filter out prefixes not in allowed list

        allowed = ['header', 'cookie', 'query']

        if prefix not in allowed:
            return False
        
        # Filter out cookies that aren't 51D or the tracking cookie

        if prefix == "cookie":
            if "51D" not in prefix or body != self.cookie:
                return False

        # Filter out any query evidence not in the whitelist

        if prefix == "query":
            if body not in self.query_whitelist:
                return False

        # Filter out any header evidence in blacklist

        if prefix == "header":
            if body in self.header_blacklist:
                return False
                
        # Passed through filter, should be tracked
        
        return True