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

from fiftyone_pipeline_core.pipelinebuilder import PipelineBuilder
from fiftyone_pipeline_cloudrequestengine.cloudrequestengine import CloudRequestEngine
from .location_cloud import LocationCloud

class LocationPipelineBuilder(PipelineBuilder):
    """!
    The Location Pipeline Builder allows you to easily
    Construct a pipeline containing the location cloud engine
    
     Internal function for getting evidence keys used by cloud engines
     
      @type resource_key: string
      @param resource_key: The 51Degrees cloud service resource key
      @type cloud_request_origin: string
      @param cloud_request_origin: The value to set the Origin header to when making requests to the cloud service
      @type location_provider: string
      @param location_provider: fiftyonedegrees or digitalelement
      @type settings: dict
      @param settings: Settings for the pipeline. 
      Can contain a `cloud_endpoint` url
      if overriding the default one. An optional cache can be added by passing an instance of 
      the DataKeyedCache class as a `cache` setting 
      The pipeline builder can also contain javascript_builder_settings settings
      see the documentation for the base PipelineBuilder and JavaScriptBuilder class 
      
    """
    def __init__(self, resource_key, location_provider="fiftyonedegrees", settings={}):
        
        super(LocationPipelineBuilder, self).__init__(settings)

        # Add specific engines

        settings["resource_key"] = resource_key

        self.add(CloudRequestEngine(settings))

        location = LocationCloud(location_provider=location_provider)

        if "cache" in settings:
            location.set_cache(settings["cache"])
        
        self.add(location)

