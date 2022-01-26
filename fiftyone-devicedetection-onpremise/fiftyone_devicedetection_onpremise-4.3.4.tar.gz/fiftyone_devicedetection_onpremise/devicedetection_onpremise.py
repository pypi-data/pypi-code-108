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
import multiprocessing
import os.path

from .constants import *

from fiftyone_pipeline_engines.engine import Engine
from fiftyone_pipeline_engines.aspectdata_dictionary import AspectDataDictionary

from fiftyone_pipeline_core.basiclist_evidence_keyfilter import BasicListEvidenceKeyFilter

from .DeviceDetectionHashEngineModule import *

from .swig_data import SwigData
from .devicedetection_datafile import DeviceDetectionDataFile

class DeviceDetectionOnPremise(Engine):
    """!
    The Device Detection On Premise engine uses a datafile to
    generate a list of properties about a device based on evidence
    supplied to it
    """

    def __init__(self, data_file_path = None, data= None, auto_update = None, cache = None, restricted_properties = None, licence_keys = None, download = True, max_matched_useragent_length = None, drift = None, difference = None, allow_unmatched = None, file_system_watcher = False, polling_interval = 30, update_time_maximum_randomisation = 10, create_temp_data_copy = True,  update_matched_useragent = False, performance_profile = 'LowMemory', reuse_temp_file = False, concurrency = multiprocessing.cpu_count(), update_on_start = False, data_file_update_base_url = 'https://distributor.51degrees.com/api/v2/download', use_predictive_graph = None, use_performance_graph = None, **kwargs):

        """!
            
        Constructor for the DeviceDetection On Premise Engine.

        @type data_file_path: string
        @param data_file_path: path to the data file
        @type data: binary
        @param data: in memory version of datafile
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
        @param update_on_start : When this is set to true the datafile is updated / downloaded immediately on initialization. This is useful if no initial datafile is present.
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
        @type use_performance_graph: bool
        @param use_performance_graph: True if the performance optimized graph should be used for processing 
        @type use_predictive_graph: bool
        @param use_predictive_graph: True if the predictive optimized graph should be used for processing
            
        """

        super(DeviceDetectionOnPremise, self).__init__()

        self.datakey = "device"

        if not data_file_path and not data:
            raise Exception("data_file_path or data is required") 
        
        if data_file_path:
            if os.path.isfile(data_file_path) == False and not update_on_start:
                raise Exception("There is no file at " + data_file_path) 

            extention = os.path.splitext(data_file_path)[1]

            if extention != ".hash":
                raise Exception("Data file name must end in .hash")
        else:
            self.data = data

        if not licence_keys and licence_keys != "":
            raise Exception("licence key is required. A key can be obtained from the 51Degrees website: https://51degrees.com/pricing. If you do not wish to use a key then you can specify an empty string, but this will cause automatic updates to be disabled.")

        #   Create SWIG wrapper vector for restricted properties and add

        restricted_properties_vector = VectorStringSwig()

        if restricted_properties:
            for restricted_property in restricted_properties:
                restricted_properties_vector.append(restricted_property)
            self.set_restricted_properties(restricted_properties)

        properties_list = RequiredPropertiesConfigSwig(restricted_properties_vector)
        
        #  Assemble configuration

        config = ConfigHashSwig()

        available_performance = ["LowMemory", "MaxPerformance", "Balanced", "BalancedTemp", "HighPerformance"]

        if performance_profile not in available_performance:
            raise Exception("Not a valid performance profile") 

        if performance_profile == "LowMemory":
            config.setLowMemory()
        if performance_profile == "MaxPerformance":
            config.setMaxPerformance()
        if performance_profile == "Balanced":
            config.setBalanced()
        if performance_profile == "BalancedTemp":
            config.setBalancedTemp()
        if performance_profile == "HighPerformance":
            config.setHighPerformance()

        # Don't set an http_ prefix on evidence keys

        config.setUseUpperPrefixHeaders(False)

        # Set performance graph of predictive graph if specified

        if(use_performance_graph):
            config.setUsePerformanceGraph(True)
        
        if(use_predictive_graph):
            config.setUsePredictiveGraph(True)

        # If auto update is enabled then we must use a temporary copy of the file

        if auto_update == True:
            config.setUseTempFile(True)

        if create_temp_data_copy == True:
            config.setUseTempFile(True)

        config.setReuseTempFile(reuse_temp_file)
        config.setUpdateMatchedUserAgent(update_matched_useragent)

        if allow_unmatched == True or allow_unmatched == False:
            config.setAllowUnmatched(allow_unmatched)

        if max_matched_useragent_length:
            config.setMaxMatchedUserAgentLength(max_matched_useragent_length)

        if drift:
            config.setDrift(drift)

        if (difference):
            config.setDifference(difference)

        config.setConcurrency(concurrency)

        # Make engine

        self.config = config
        self.properties_list = properties_list
        self.data_file_path = data_file_path

        # Disable features that require a licence key if one was not supplied.
    
        if licence_keys:
            auto_update = auto_update and (len(licence_keys) > 0)
            update_on_start = update_on_start and (len(licence_keys) > 0)
        else:
            auto_update = False
            update_on_start = False

        if auto_update or update_on_start or file_system_watcher:
            
            # Construct DataFile

            update_url_params = {
                "type": "HashV41",
                "base_url": data_file_update_base_url
            }

            if licence_keys:
                update_url_params["license_keys"] = licence_keys

            data_file = DeviceDetectionDataFile(flow_element=self,identifier="HashV41", verify_md5 = True, auto_update = auto_update, update_on_start = update_on_start, decompress= True, path = data_file_path, download=download, file_system_watcher=file_system_watcher, polling_interval=polling_interval, update_time_maximum_randomisation=update_time_maximum_randomisation, update_url_params = update_url_params)

            self.register_data_file(data_file)

        self.data_file_path = data_file_path
        self.config = config
        self.properties_list = properties_list

    def init_engine(self):

        """!
            
        Function for initialising the engine, wrapped like this so that an engine can be initialised once the datafile is retrieved if update_on_start is set to true. If this is the case, processing is held until the data file is downloaded and available.

        """

        if(self.data_file_path):
            data = self.data_file_path
        else:
            data = self.data

        engine = EngineHashSwig(data, self.config, self.properties_list)

        self.engine = engine

        # Get keys and add to evidenceKey filter

        evidence_keys = engine.getKeys()

        evidence_keys_list = []

        for x in range(evidence_keys.size()):
            evidence_keys_list.append(evidence_keys.__getitem__(x).lower())

        self.evidence_keys_list = evidence_keys_list

        # Get properties list

        properties_internal = engine.getMetaData().getProperties()

        properties = {}

        for x in range(properties_internal.getSize()):
            current_property = properties_internal.getByIndex(x)
            if current_property.getAvailable():
                properties[current_property.getName().lower()] = {
                "name": current_property.getName(),
                "type": current_property.getType(),
                "datafiles": list(current_property.getDataFilesWherePresent()),
                "category": current_property.getCategory(),
                "description": current_property.getDescription()
            }
        
        self.properties = properties

        # Special properties

        self.properties["deviceid"] = {
          "name": 'DeviceId',
          "type": 'string',
          "category": 'Device metrics',
          "description": DEVICE_ID_DESCRIPTION
        }

        self.properties["useragents"] = {
          "name": 'UserAgents',
          "type": 'string',
          "category": 'Device metrics',
          "description": USER_AGENTS_DESCRIPTION
        }

        self.properties["difference"] = {
          "name": 'Difference',
          "type": 'int',
          "category": 'Device metrics',
          "description": DIFFERENCE_DESCRIPTION
        }

        self.properties["matchednodes"] = {
            "name": 'MatchedNodes',
            "type": 'int',
            "category": 'Device metrics',
            "description": MATCHED_NODES_DESCRIPTION
        }

        self.properties["drift"] = {
            "name": 'Drift',
            "type": 'int',
            "category": 'Device metrics',
            "description": DRIFT_DESCRIPTION
        }

        self.properties["iterations"] = {
            "name": 'Iterations',
            "type": 'int',
            "category": 'Device metrics',
            "description": ITERATIONS_DESCRIPTION
        }
        
        self.properties["method"] = {
            "name": 'Method',
            "type": 'string',
            "category": 'Device metrics',
            "description": METHOD_DESCRIPTION
        }

    def get_evidence_key_filter(self):
        """!
        Returns evidence key filter for the on premise engine.
        Generated via a list of evidence keys from the swig engine
        
        """
        
        return BasicListEvidenceKeyFilter(self.evidence_keys_list)

    
    def on_registration(self, pipeline):

        """!
            
        Function called after the engine is registered with a pipeline
        the engine base class registers the datafile but we also need
        to initialise the SWIG wrapper so call self.init_engine() here
        after the datafile is registered.

        """

        super(DeviceDetectionOnPremise, self).on_registration(pipeline)
        self.init_engine()

    def process_internal(self, flow_data):

        """!
        
        Internal process method of the Device Detection On Premise engine
        Gets properties through the SWIG wrapper and stores them in a
        SwigData extension of the ElementData class. Each property value (or lack of) is returned in an AspectPropertyData wrapper from
        the core Pipeline library.

        """

        evidence = EvidenceDeviceDetectionSwig()

        for key, value in flow_data.evidence.get_all().items():
            evidence.__setitem__(key, value)

        result = self.engine.process(evidence)

        data = SwigData(self, result)

        flow_data.set_element_data(data)
