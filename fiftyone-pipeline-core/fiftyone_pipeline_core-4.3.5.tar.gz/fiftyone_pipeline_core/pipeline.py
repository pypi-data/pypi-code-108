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

from .flowdata import FlowData
from .logger import Logger

class Pipeline:

    """!
    Pipeline holding a list of FlowElements for processing,
    can create FlowData that will be passed through these,
    collecting ElementData
    Should be constructed through the PipelineBuilder class

    """

    def __init__(self, flow_elements, logger=Logger(), suppress_process_exceptions = False):

        """!
        Pipeline constructor.

        @type flow_elements: list[FlowElement]
        @param flow_elements: A list of flowElements

        @type logger: Logger
        @param logger: A logger to attach to the pipeline

        @type suppress_process_exceptions: boolean
        @param suppress_process_exceptions: If true then pipeline will suppress 
        exceptions added to FlowData.errors otherwise will throw the exception
        occurred during the processing of first element.

        @rtype: Pipeline
        @return: Returns a Pipeline

        """

        self.flow_elements = flow_elements

        self.logger = logger

        self.flow_elements_list = {}

        self.flow_elements_display_list = []

        self.suppress_process_exceptions = suppress_process_exceptions
        
        for flow_element in flow_elements:

            # Notify element that it has been registered in the pipeline
            flow_element.on_registration(self)

            self.flow_elements_list[flow_element.datakey] = flow_element

            flow_element.pipelines.append(self)

            if not flow_element.exclude_from_messages:
                self.flow_elements_display_list.append(flow_element.datakey)

    def create_flowdata(self):

        """!
        Create a FlowData based on what's in the pipeline
        
        @rtype: FlowData
        @return: Return a FlowData

        """

        return FlowData(self)

    def log(self, level, message):

        """!
        Log a message using the Logger.log of the pipeline's Logger.

        @type level: string
        @param level: level of log message

        @type message: string
        @param message: Returns content of log message

        """

        self.logger.log(level, message)

    def get_element(self, key):

        """!
        Get a flowElement by its name.

        @type key: string
        @param key: name of flowElement

        @rtype: FlowElement
        @return: Returns the FlowElement indicated

        """

        return self.flow_elements_list[key]

    def element_not_found(self, element, flowdata):
        """!
        Trigger error when an element cannot be found in the pipeline

        @type element: string
        @param element: name of flowelement 
        @type flowdata: flowdata
        @param element: flowdata being processsed 
        @rtype: Exception
        @return: Returns exception

        """

        raise Exception("There is no element data for " + element + " against this flow data. Available element data keys are: " + str(flowdata.pipeline.flow_elements_display_list))


    def get_properties(self):

        """!
        Get all properties of all flowElements in the pipeline.

        @rtype: dict of {string : DataPropertyDictionary}
        @return: Returns dictionary of all properties in a pipeline keyed by each flowElement's FlowElement.datakey.

        """

        output = {}

        for flow_element in self.flow_elements:
            properties = flow_element.get_properties()

            output[flow_element.datakey] = properties

        return output
