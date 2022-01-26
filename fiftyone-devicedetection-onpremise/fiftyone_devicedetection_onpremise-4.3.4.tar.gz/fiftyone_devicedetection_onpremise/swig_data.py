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

from fiftyone_pipeline_engines.aspectdata import AspectData
from fiftyone_pipeline_core.aspectproperty_value import AspectPropertyValue

from fiftyone_pipeline_engines.missingproperty_service import MissingPropertyService

class OnPremiseMissingPropertyService(MissingPropertyService):

    def check(self, key, flow_element):

        if key in flow_element.properties:
            datafiles = flow_element.properties[key]["datafiles"]
            if(not flow_element.engine.getProduct() in datafiles):
                raise Exception('Property ' + key + ' not found in data for element ' + flow_element.datakey + '. This is because your datafile does not contain the property. The property is available in' + str(datafiles))
        else:
            raise Exception('Property ' + key + ' not found in data for element ' + flow_element.datakey + '. Please check that the element and property names are correct.')

class SwigData(AspectData):

    """!
    Extention of AspectData made for retrieving results
    created by the SWIG wrapper of the On Premise Device Detection engine
    """

    def __init__(self, flow_element, swig_results):
        
        """!
        Constructor for swig_data
        @type flow_element: FlowElement
        @param flow_element: FlowElement / Engine the data is keyed under
        @type swig_results: ResultsHashSwig
        @param swig_results: Results from the SWIG wrapper's process method
        """

        super(SwigData, self).__init__(flow_element)

        self.swig_results = swig_results

        self.missing_property_service = OnPremiseMissingPropertyService()

    def get_internal(self, key):

        """!
        Get property values out of the SWIG wrapper
        @type key: string
        @param key: The key of the property to retrieve
        @returns mixed
        """

        #   start with special properties

        # Lowercase key

        key = key.lower()

        if key == "deviceid":
            return AspectPropertyValue(value = self.swig_results.getDeviceId())

        if key == 'useragents':
            return AspectPropertyValue(value = self.swig_results.getUserAgents())

        if key == 'difference':
            return AspectPropertyValue(value = self.swig_results.getDifference())

        if key == 'method':
            return AspectPropertyValue(value = self.swig_results.getMethod())

        if key == 'matchednodes':
            return AspectPropertyValue(value = self.swig_results.getMatchedNodes())

        if key == 'drift':
            return AspectPropertyValue(value = self.swig_results.getDrift())

        if key == 'iterations':
            return AspectPropertyValue(value = self.swig_results.getIterations())
            
        # End special properties

        this_property = self.flow_element.properties[key]

        if this_property:

            value = None

            if this_property["type"] == "bool":
                value = self.swig_results.getValueAsBool(this_property["name"])

            if this_property["type"] == "string":
                value = self.swig_results.getValueAsString(this_property["name"])

            if this_property["type"] == "javascript":
                value = self.swig_results.getValueAsString(this_property["name"])
            
            if this_property["type"] == "int":
                value = self.swig_results.getValueAsInteger(this_property["name"])

            if this_property["type"] == "double":
                value = self.swig_results.getValueAsDouble(this_property["name"])

            if this_property["type"] == "string[]":
                value = self.swig_results.getValues(this_property["name"])
   

            # Check for value / no value message

            if value.hasValue():
                
                # Convert value to list if needed
                if this_property["type"] == 'string[]':
                    return AspectPropertyValue(value=list(value.getValue()))

                return AspectPropertyValue(value=value.getValue())
            
            else:

                return AspectPropertyValue(no_value_message=value.getNoValueMessage())
