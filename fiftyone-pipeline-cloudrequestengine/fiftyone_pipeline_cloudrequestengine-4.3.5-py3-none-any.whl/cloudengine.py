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

from fiftyone_pipeline_engines.engine import Engine
from fiftyone_pipeline_core.aspectproperty_value import AspectPropertyValue

from .clouddata import CloudData

import json

from fiftyone_pipeline_engines.missingproperty_service import MissingPropertyService

class OnPremiseMissingPropertyService(MissingPropertyService):

    def check(self, key, flow_element):

        raise Exception('Property ' + key + ' not found in data for element ' + flow_element.datakey + '. Please check that the element and property names are correct.')

class CloudEngine(Engine):

    """!
    This is a template for all 51Degrees cloud engines.
    It requires the 51Degrees cloudRequestEngine to be placed in a
    pipeline before it. It takes that raw JSON response and
    parses it to extract the device part.
    It also uses this data to generate a list of properties and an evidence key filter

    """

    def __init__(self):

        super(CloudEngine, self).__init__()

        self.datakey = "CloudEngineBase" # This should be overriden

    def on_registration(self, pipeline):
 
        """!
        Callback called when an engine is added to a pipeline
        In this case sets up the properties list for the element from
        data in the CloudRequestEngine

        @type pipeline: Pipeline
        @param pipeline

        """

        if not "cloud" in pipeline.flow_elements_list:
            raise Exception("CloudRequestEngine needs to be placed before cloud elements in Pipeline")

        # Add properties from the CloudRequestEngine which should already have them

        if not self.datakey in pipeline.flow_elements_list["cloud"].flow_element_properties:
            raise Exception("Your resource key does not include access to any properties under the engine with key " + self.datakey +  " that was added to the pipeline. For more details on resource keys, see our explainer: https://51degrees.com/documentation/_info__resource_keys.html " + "Available engine data keys are: " + str([e for e in pipeline.flow_elements_list["cloud"].flow_element_properties]))

        self.properties = pipeline.flow_elements_list["cloud"].flow_element_properties[self.datakey]

        # Add a special message to the pipeline 
        # when requesting an element that does not exist

        pipeline.element_not_found = self.pipeline_element_not_found

    def pipeline_element_not_found(self, element, flowdata):
        """!
        Custom error when an element cannot be found in the pipeline

        @type element: string
        @param element: name of flowelement 
        @type flowdata: flowdata
        @param element: flowdata being processsed 
        @rtype: Exception
        @return: Returns exception

        """

        raise Exception("Your resource key does not include access to any properties under " + element +  ". For more details on resource keys, see our explainer: https://51degrees.com/documentation/_info__resource_keys.html " + "Available element data keys are: " + str([e for e in flowdata.pipeline.flow_elements_display_list]))


    def process_internal(self, flowdata):

        """!
        Process function of a cloud engine.
        This organises and parses data returned from the Cloud Request Engine
        and adds it to the FlowData

        @type flowdata: FlowData
        @param flowdata: FlowData to process 

        """
  
        cloud_data = flowdata.get("cloud").get("cloud")

        cloud_data = json.loads(cloud_data)

        engineData = cloud_data[self.datakey]

        result = {}

        for key, value in engineData.items():

            if key + "nullreason" in cloud_data[self.datakey]:
                result[key] = AspectPropertyValue(no_value_message=cloud_data[self.datakey][key + "nullreason"])
            else:
                result[key] = AspectPropertyValue(None, value)

        data = CloudData(self, result)
            
        flowdata.set_element_data(data)
