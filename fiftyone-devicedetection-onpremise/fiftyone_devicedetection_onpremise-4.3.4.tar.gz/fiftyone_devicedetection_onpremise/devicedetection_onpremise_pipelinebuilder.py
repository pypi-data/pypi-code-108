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
from fiftyone_pipeline_core.pipelinebuilder import PipelineBuilder
from .devicedetection_onpremise import DeviceDetectionOnPremise
from fiftyone_devicedetection_shared.utils import merge_two_dicts

from fiftyone_pipeline_engines_fiftyone.share_usage import ShareUsage

class DeviceDetectionOnPremisePipelineBuilder(PipelineBuilder):
    """!
    The Device Detection Pipeline Builder allows you to easily
    Construct a pipeline containing the device detection cloud engine

    Internal function for getting evidence keys used by cloud engines
    
    """
    def __init__(self, settings = None, usage_sharing = True, **kwargs):

        """!

        Constructor for Device Detection Pipeline Builder
        Depending on parameters passed through, builds a pipeline
        with either the cloud or on premise device detection engines

        General pipeline settings:

        @type javascript_builder_settings: dict
        @param javascript_builder_settings: parameters for the pipeline's JavaScript builder to populate additional evidence from the clientside.
            - obj_name: the name of the client side object 
            with the JavaScript properties in it ('fod' by default)
            - protocol: The protocol ("http" or "https") used by 
            the client side callback url. This can be overridden 
            with header.protocol evidence
            - host The host of the client side callback url. 
            This can be overridden with header.host evidence.
            - endpoint The endpoint of the client side callback url
            * enable_cookies - whether cookies should be enabled
            * minify: Whether to minify the JavaScript
        @type cache: Cache
        @param cache: An instance of the fiftyone.pipeline.engines.cache
        class

        Cloud Engine Settings:

        @type resource_key: string
        @param resource_key: the 51Degrees cloud resource key

        On Premise Engine Settings

        @type usage_sharing : bool
        @param usage_sharing : Whether to enable usage sharing if using the on premise engine
        @type data_file_path: string
        @param data_file_path: path to the data file
        @type auto_update: bool
        @param auto_update: whether to automatically update the datafile when required
        @type restricted_properties: list
        @param restricted_properties: List of property keys to limit the engine to
        @type license_keys: string
        @param licence_keys: licencekeys to use for the data file update service
        @type download: bool
        @param download: whether to download the datafile or keep it in memory when it is returned from the datafile update service
        @type max_matched_useragents_length : int
        @param Number of characters to consider in the matched User-Agent. Ignored if update_matched_useragent is false
        @type update_matched_useragent: 
        @param: update_matched_useragent: True if the detection should record the matched characters from the target User-Agent
        @type drift: int
        @param drift: Set maximum drift in hash position to allow when processing HTTP headers
        @type difference: int
        @param difference: set the maximum difference to allow when processing HTTP headers. The difference is the difference in hash value between the hash that was found, and the hash that is being searched for. By default this is 0.
        @type allow_unmatched : bool
        @param allow_unmatched:  True if there should be at least one matched node in order for the results to be considered valid. By default, this is false
        @type performance_profile: string
        @param performance_profile: options are: LowMemory, MaxPerformance, Balanced, BalancedTemp, HighPerformance
        @type reuse_temp_file: bool
        @param reuse_temp_file: Indicates that an existing temp file may be used. This should be selected if multiple instances wish to use the same file to prevent high disk usage.
        @type concurrency: int
        @param concurrency: defaults to the number of cpus in the machine
        @type update_on_start : bool
        @param update_on_start : When this is set to true the datafile is updated / downloaded immediately on initialisation. This is useful if no initial datafile is present.
        @type file_system_watcher: bool
        @param file_system_watcher: whether to check the datafile's path for changes and update the connected FlowElement's data 
        @type polling_interval: int
        @param polling_interval: How often to poll for updates to the datafile (minutes)
        @type update_time_maximum_randomisation : int
        @param update_time_maximum_randomisation :
        Maximum randomisation offset in seconds to polling time interval
        @type verify_md5 : bool
        @type create_temp_copy: bool
        @param create_temp_copy: whether to copy datafile to temporary location when updating
        @type data_file_update_base_url: string
        @param data_file_update_base_url: base url for the datafile update service

        """
        if settings is None:
            settings = {}
            
        settings = merge_two_dicts(dict(**kwargs), locals())

        settings = merge_two_dicts(settings, settings["settings"])

        del settings["self"]

        super(DeviceDetectionOnPremisePipelineBuilder, self).__init__(settings)

        # Add specific engines


        del settings["settings"]
        device = DeviceDetectionOnPremise(**settings)
        
        # If usage sharing enabled, add usage sharing engine

        if usage_sharing:
            self.add(ShareUsage())

        if "cache" in settings:
            device.set_cache(settings["cache"])
        
        self.add(device)