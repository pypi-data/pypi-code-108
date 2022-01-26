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

from .pipeline import Pipeline
from .logger import Logger
from .javascriptbuilder import JavascriptBuilderElement
from .jsonbundler import JSONBundlerElement
from .sequenceelement import SequenceElement
from .setheaderelement import SetHeaderElement
import importlib


class PipelineBuilder(object):
    """
    A PipelineBuilder generates a Pipeline object
    Before construction of the Pipeline, FlowElements are added to it
    There are also options for how JavaScript is output from the Pipeline

    """

    def __init__(self, settings= {}):
        """
        Pipeline Builder constructor.
        @type settings: dictionary
        @param settings : settings for the pipeline builder including:
        `add_javascript_builder (Bool)` - Whether to add the JavaScriptBuilder to the pipeline
        (default true)
        `javascript_builder_settings (dict)` - Settings for the JavaScriptBuilder engine 
        @rtype: PipelineBuilder
        `use_setheader_properties (Bool)` - Whether to add the SetHeaderElement to the pipeline
        (default true)
        @return: Returns a Pipeline Builder

        """

        self.flow_elements = []
        self.logger = Logger()

        if "add_javascript_builder" in settings:
            self.add_javaScriptbuilder = settings["add_javascript_builder"]
        else:
            self.add_javaScriptbuilder = True
          
        if "javascript_builder_settings" in settings:
            self.javascriptbuilder_settings = settings["javascript_builder_settings"]

        if "use_setheader_properties" in settings:
            self.use_setheader_properties = settings["use_setheader_properties"]
        else:
            self.use_setheader_properties = True


    def get_javascript_elements(self):
        """
        Adds the JavaScriptBuilder, JSONBundler and SequenceElement to the pipeline if
        If add_javascript_builder is set to true (the default)
        @rtype: list
        @return: Returns a list of FlowElements     
        """
        
        flow_elements = []

        if (self.add_javaScriptbuilder):

            flow_elements.append(SequenceElement())
            flow_elements.append(JSONBundlerElement())
    
            if (hasattr(self, "javascriptbuilder_settings")):
                flow_elements.append(JavascriptBuilderElement(self.javascriptbuilder_settings))
            else:
                flow_elements.append(JavascriptBuilderElement())
   
        return flow_elements

    def get_setheader_elements(self):
        """
        Adds the SetHeaderElement to the pipeline if
        If use_setheader_properties is set to true (the default)
        @rtype: list
        @return: Returns a list of FlowElements     
        """
        
        flow_elements = []

        if (self.use_setheader_properties):
            flow_elements.append(SetHeaderElement())
   
        return flow_elements

    def add(self, flow_element):
        """
        Add a flow_element to a list of flowElements be used in a pipeline.
        
        @type flow_element: FlowElement
        @param flow_element: flowElement to be added to the pipeline

        @rtype: PipelineBuilder
        @return: Returns the pipleine builder with the specified flowElement added to it's list of flowElements.

        """

        self.flow_elements.append(flow_element)

        return self

    def build(self):
        """
        Construct an immutable Pipeline using the list of flowElements, (Engines) and (Logger) currently in this Pipeline Builder.
        Call build after all items to be included in the pipeline have been added.

        @rtype: Pipeline
        @return: Returns a Pipeline

        """

        self.flow_elements.extend(self.get_javascript_elements())
        self.flow_elements.extend(self.get_setheader_elements())
        
        return Pipeline(self.flow_elements, logger=self.logger)

    def add_logger(self, logger):
        """
        Add an instance of the logger class to the pipeline.

        @type logger: Logger
        @param logger: Logger to be added to the pipeline

        @rtype: PipelineBuilder
        @return: Returns the pipeline builder with the specified Logger added.
        
        """

        self.logger = logger

        return self

    def build_from_configuration(self, config):
        """
        Build a pipeline from a configuration file

        @type config: dict
        @param config: pipeline configuration

        @rtype: Pipeline
        @return: Returns built pipeline
        
        """

        flow_elements = []

        for element in config["PipelineOptions"]["Elements"]:
            flow_element = importlib.import_module(element["elementPath"]).__getattribute__(element["elementName"])
            if("elementParameters" in element):
                flow_element = flow_element(**element["elementParameters"])
            else:
                flow_element = flow_element()
            flow_elements.append(flow_element)

        return Pipeline(flow_elements)

