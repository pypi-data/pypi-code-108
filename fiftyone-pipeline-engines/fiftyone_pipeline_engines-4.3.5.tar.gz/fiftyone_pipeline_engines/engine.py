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

from fiftyone_pipeline_core.flowelement import FlowElement
from fiftyone_pipeline_engines.datafile_update_service import DataFileUpdateService

import json

class Engine(FlowElement):

    """!
    
    An engine is an extension of the FlowElement class that adds
    extra functionality

    """

    
    def __init__(self, data_file = None):

        """!
        Constructor for an engine

        """

        self.data_file = data_file

        super(Engine, self).__init__()
    
    def set_cache(self, cache):

        """!
        Add a cache to an engine
        @type cashe: Cache
        @param cache: Cache with get and set methods

        """
        
        self.cache = cache


    def set_restricted_properties(self, properties_list):

        """!
        Add a subset of properties
        
        @type properties_list: string[] 
        @param properties_list: An array of properties to include
        
        """
 
        self.restricted_properties = properties_list
  

    def in_cache(self, flowdata):

        """!
        A method to check if a flowdata's evidence is in the cache
        
        @type FlowData: FlowData
        @param FlowData:

        @rtype: bool
        @return: True or false: a flowdata's evidence is in the cache

        """
    
        keys = self.filter_evidence(flowdata)

        cacheKey = json.dumps(keys)

        cached = self.cache.get_cache_value(cacheKey)

        if cached is not None:
            flowdata.set_element_data(cached)

            return True
        else:
            return False
  
  
    """!
    
    Function called to refresh the engine with a new datafile
    @type identifier: string
    @param identifier: identifier of the datafile
    
    """
    def refresh(self, identifier):
        pass

    def process(self, flowdata):

        """!
        
        Engine's core process function.
        Calls specific overriden processInternal methods but wraps it in a cache check
        and a cache put
        
        @type flowdata: FlowData
        @param flowdata:
        
        """

        if hasattr(self, "cache"):

            if self.in_cache(flowdata):
                return True
            else:
                self.process_internal(flowdata)
                cacheKey = json.dumps(self.filter_evidence(flowdata))
                self.cache.set_cache_value(cacheKey, flowdata.get(self.datakey))

        else:

            self.process_internal(flowdata)

    def on_registration(self, pipeline):

        """!
        
        Called when an engine is registered with a pipeline 
        and if there is a data file, a data file update service is attached to the parent pipeline.
        @type pipeline: Pipeline
        @param pipeline: The pipeline the engine has been attached to
        
        """

        if(self.data_file):
            if not hasattr(pipeline, "data_file_update_service"):
                pipeline.data_file_update_service = DataFileUpdateService(pipeline)
            pipeline.data_file_update_service.register_data_file(self.data_file)

    def register_data_file(self, data_file):

        """!
        
        Register a data_file of the DataFile class with the engine
        @type data_file: DataFile
        @param data_file: DataFile (such as for an on premise engine)
        
        """
        
        self.data_file = data_file
