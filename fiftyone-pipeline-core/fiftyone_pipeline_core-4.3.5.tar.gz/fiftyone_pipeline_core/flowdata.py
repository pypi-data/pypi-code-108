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

from .evidence import Evidence
from .flowerror import FlowError
from .messages import Messages	
import traceback
import sys

class FlowData:

    """!
    FlowData is created by a specific Pipeline
    It collects evidence set by the user
    It passes evidence to FlowElements in the Pipeline
    These elements can return ElementData or populate an errors object

    """

    def __init__(self, pipeline):

        """!
        FlowData constructor.

        @type pipeline: Pipeline
        @param pipeline: parent pipeline

        """

        self.data = {}
        self.errors = {}
        self.pipeline = pipeline
        self.processed = False
        self.stopped = False
        self.evidence = Evidence(self)

    def process(self):

        """!
        Runs the process function on every attached flowElement allowing data to be changed based on evidence.
        This can only be run once per FlowData instance.

        @rtype: FlowData
        @return: Returns flowdata

        """

        if not self.processed:

            for flow_element in self.pipeline.flow_elements:
                if self.stopped is not True:
                    # All errors are caught and stored in an errors array keyed by the
                    # flowElement that set the error

                    try:
                        flow_element.process(self)

                    except Exception:
	
                        flow_error = FlowError(flow_element.datakey, sys.exc_info()[1], traceback.format_exc())
                        self.set_error(flow_error)

            # Set processed flag to true. flowdata can only be processed once

            self.processed = True

        else:
            flow_error = FlowError("global", Exception(Messages.FLOW_DATA_PROCESSED), Messages.FLOW_DATA_PROCESSED)
            self.set_error(flow_error)

        if self.errors and self.pipeline.suppress_process_exceptions is False:
            errored_flow_element_key = next(iter(self.errors))
            flowErrorObj = self.errors[errored_flow_element_key]             
            raise flowErrorObj.exception_instance 

        return self

    def get_from_element(self, flow_element):

        """!
        Retrieve data by FlowElement object.

        @type flow_element: FlowElement
        @param flow_element: FlowElement that created the data of interest

        @rtype: ElementData
        @return: Returns data that was created by the flowElement held in the FlowData

        """

        try:
            return self.get(flow_element.datakey)

        except Exception:
            return None


    def get(self, flow_element_key):

        """!
        Retrieve data by flowElement key.
        Called by FlowData.get_from_element method.

        @type flow_element_key: string
        @param flow_element_key: FlowElement.datakey of the FlowElement that created the data of interest

        @rtype: ElementData
        @return: Returns data in the FlowData instance that is under the specified key

        """

        try:
            return self.data[flow_element_key.lower()]

        except Exception:

            return self.pipeline.element_not_found(flow_element_key, self)

    def __getattr__(self, flow_element_key):

        """!
        Magic getter to allow retrieval of data from FlowData.data[flowElementKey] by flowElement name.
        For example, instead of `flowdata.get("device")` you can use `flowdata.device`

        @type flow_element_key: string
        @param flow_element_key: datakey of the FlowElement that created the data of interest

        @rtype: ElementData
        
        """

        return self.get(flow_element_key)

    def __getitem__(self, flow_element_key):

        """!
        Magic method in Python, which when used in a class, allows its instances to use the [] (indexer) operators.
        For example, instead of `flowdata.get("device")` you can use `flowdata["device"]`

        @type flow_element_key: string
        @param flow_element_key: datakey of the FlowElement that created the data of interest

        @rtype: ElementData
        
        """

        return self.get(flow_element_key)
		
    def set_element_data(self, element_data):

        """!
        Set data (used by flowElement) within FlowData.data

        @type element_data: ElementData
        @param element_data: elementData to be added to flowdata

        """

        self.data[element_data.flow_element.datakey] = element_data


    def set_error(self, flow_error):
    
        """!
        Set error (should be keyed by flowElement datakey)

        @type error: FlowError
        @param error: Flow Error

        """

        self.errors[flow_error.flow_element] = flow_error

        log_message = "Error occurred during processing"

        if flow_error.flow_element:
            
            log_message = log_message + " of " + flow_error.flow_element + ". \n" + flow_error.exception_traceback

        self.pipeline.log("error", log_message)


    def get_evidence_datakey(self):

        """!
        Get a list of evidence stored in the flowdata, filtered by
        its flowElements' evidenceKeyFilters

        @rtype: list
        @return: Returns filtered evidence

        """
        requestedEvidence = list()

        for flow_element in self.pipeline.flow_elements:
            requested_evidence = requestedEvidence.extend(flow_element.filter_evidence(self))

        return requested_evidence


    def stop(self):

        """!
        Stop processing any subsequent flowElements
        @return void
        
        """

        self.stopped = True

    def get_where(self, metakey, metavalue):

        """!
        Get data from flowElement based on property meta data

        @type metakey: str
        @param metakey: metakey shared by all data of interest

        @type metavalue: mixed
        @param metavalue: meta value shared by all data of interest

        @rtype: dict
        @return: Returns dictionary of data created by the flowElement that have the specified meta property

        """

        meta_query_output = {}

        properties = self.pipeline.get_properties()

        for flow_element, flow_element_properties in properties.items():
            for propertykey, propertymeta in flow_element_properties.items():
                if metakey.lower() in propertymeta:
                    if propertymeta[metakey.lower()] == metavalue:
                        try:
                            meta_query_output[propertykey] = self.get(flow_element).get(propertykey)                
                        # We are ignoring errors in getWhere as properties could be missing on purpose
                        # They shouldn't throw an error breaking the whole getWhere.
                        except Exception:
                            pass
                        
        return meta_query_output
                        
