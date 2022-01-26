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

from __future__ import absolute_import
from fiftyone_pipeline_engines.engine import Engine

from .share_usage_evidencekeyfilter import ShareUsageEvidenceKeyFilter
from .share_usage_tracker import ShareUsageTracker

import json
import requests
import zlib
import sys
import platform
import datetime

class ShareUsage(Engine):
    def __init__(self, interval = 1200, requested_package_size = 10, cookie = None, query_whitelist = [], header_blacklist = [], share_percentage = 100):
        """!
        Constructor for ShareUsage element
        
        @type interval: int
        @param interval: If exactly the same evidence values are seen 
        multiple times within this time limit (in seconds) then they 
        will only be shared once.
        @type requested_package_size: int
        @param requested_package_size: The usage element will group data into 
        single requests before sending it. This setting controls the minimum 
        number of entries before data is sent. If you are sharing large 
        amounts of data, increasing this value is recommended in order to 
        reduce the overhead of sending HTTP messages.
        For example, the 51Degrees cloud service uses a value of 2500.
        @type cookie: string
        @param cookie: If a cookie is being used to identify user 
        sessions, it can be specified here in order to reduce the 
        sharing of duplicated data.
        @type query_whitelist: list
        @param query_whitelist: By default query string and HTTP form 
        parameters are not shared unless prefixed with '51D_'.
        If you need to share query string parameters, a list can be 
        specified here.
        @type query_blacklist: list
        @param query_blacklist: By default, all HTTP headers 
        (except a few, such as Cookies) are shared. 
        Individual headers can be excluded from sharing by adding them 
        to this list.
        @type share_percentage : int
        @param share_percentage: Percentage of requests to share.        
        """

        super(ShareUsage, self).__init__()

        self.query_whitelist = query_whitelist

        self.header_blacklist = header_blacklist

        self.datakey = "shareusage"

        self.interval = interval
        self.requested_package_size = requested_package_size
        self.cookie = cookie
        self.share_percentage = share_percentage

        # Add the share usage tracker which detects when
        # to send up sharing data

        self.tracker = ShareUsageTracker(interval = interval)

        # Start share percentage counter at 0
        self.share_percentage_counter = 0

        # Initialise share data list 
        self.share_data = []
    
    def get_evidence_key_filter(self):

        """!

        The share useage element comes with its own evidence
        key filter that uses the whitelists and blacklists to
        determine which evidence to share    
    
        """

        return ShareUsageEvidenceKeyFilter(
            cookie = self.cookie,
            query_whitelist = self.query_whitelist,
            header_blacklist = self.header_blacklist
        )

    def share_send_usage(self):
        """!
        Internal method to send the share usage bundle to the 51Degrees servers
        """

        data = '<devices>' + "".join(self.share_data) + '</devices>'

        data = zlib.compress(bytearray("b" + json.dumps(data), encoding='utf8'))

        requests.post("https://devices-v4.51degrees.com/new.ashx", headers={"Content-Encoding": "gzip", "Content-Type": "text/xml"}, data=data)
                
        # Reset share data list
        self.shareData = []

    def add_to_share_usage(self, key):
        """!
        Internal method which adds to the share usage bundle (generating XML)
        @type key: dict
        @param key: key value store of current
        evidence in FlowData (filtered by the ShareUsageEvidenceKeyFilter)
        """

        xml = ""
        xml += "<device>"
        xml += "<Version>4</Version>"
        xml += "<Language>Python</Language>"
        xml += "<LanguageVersion>" + sys.version + "</LanguageVersion>"
        xml += "<Platform>" + platform.system() + " " + platform.release() + "</Platform>"

        key = json.loads(key)

        # Loop over keys in evidence and push them into the xml

        for item, value in key.items():
            parts = item.split(".")
            
            prefix = parts[0]
            name = parts[1]

            xml += '<' + prefix + 'name="' + name + '>' + value + '</' + prefix + '>'

        date = datetime.datetime.now().isoformat() 

        xml += "<dateSent>" +  date + "</dateSent>"
        
        xml += "</device>"
 
        self.share_data.append(xml)

        # Send share usage data if data size greater than requested
        # package size

        if len(self.share_data) > self.requested_package_size:
            self.share_send_usage()

    def process_internal(self, flow_data):

        """!

        Internal process method which uses the ShareUsageTracker
        to determine whether to add usage data to a batch and adds it if necessary.
        @type flow_data: FlowData
        @param flow_data: FlowData to process

        """

        # First increment the share_percentage_counter

        self.share_percentage_counter += 1

        # Reset counter if matches share_percentage setting

        if self.share_percentage_counter == int(100 / self.share_percentage):
            self.share_percentage_counter = 0

        # Don't store if share percentage counter

        if (self.share_percentage_counter != 0):
            return

        cachekey = self.get_evidence_key_filter().filter_evidence(flow_data.evidence.get_all())

        cachekey = json.dumps(cachekey)

        share = self.tracker.track(cachekey) 

        if(share):
            self.tracker.set_cache_value(cachekey)
            self.add_to_share_usage(cachekey)
