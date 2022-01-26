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

from .flowelement import FlowElement
from .elementdata_dictionary import ElementDataDictionary

class JSONBundlerElement(FlowElement):

    """!
    The JSONBundler aggregates all properties from FlowElements into a JSON object
    It is used for retrieving via an endpoint from the client
    side via the JavaScriptBuilder and also used inside the
    JavaScriptBuilder itself to pass properties to the client side.
    Both this and the JavaScriptBuilder element are automatically
    added to a Pipeline unless specifically ommited in the PipelineBuilder

    """

    def __init__(self):

        super(JSONBundlerElement, self).__init__()

        self.datakey = "jsonbundler"

        self.exclude_from_messages = True

        self.properties = {"json" : { "type": "dict"} }

        self.property_cache = {}

    def process_internal(self, flowdata):

        """!
        
        The JSONBundler extracts all properties from a FlowData and serializes them into JSON
        @type flowdata: FlowData
        @param flowdata: A FlowData
    
        """
   
        # Get every property on every FlowElement
        # Storing JavaScript properties in an extra section

        output = {"javascriptProperties": [] }

        if len(self.property_cache):
            property_cache_set = True
        else:
            property_cache_set = False
        
        for flow_element in flowdata.pipeline.flow_elements:

            if (flow_element.datakey == "jsonbundler" or
                flow_element.datakey == "sequence" or 
                flow_element.datakey == "javascriptbuilder" or
                flow_element.datakey == "set-headers"):
                continue
            
            properties = flow_element.get_properties()

            if not property_cache_set:

                delay_execution_list = []
                delayed_evidence_properties = {}

                # Loop over all properties and see if any have delay execution set to true

                for propertykey, propertymeta in properties.items():
                    
                    if "delayexecution" in propertymeta and propertymeta["delayexecution"] == True:
                        delay_execution_list.append(propertykey)

                """
                Loop over all properties again and see if any have evidenceproperties which
                have delayedExecution set to true
                """
                
                for propertykey, propertymeta in properties.items():

                    if("evidenceproperties" in propertymeta):

                        delayed_evidence_properties_list = list(filter(lambda x: x in delay_execution_list, propertymeta["evidenceproperties"]))

                        if len(delayed_evidence_properties_list):
                            
                            delayed_evidence_properties[propertykey] = list(map(lambda x:
                                flow_element.datakey + '.' + x, delayed_evidence_properties_list))


                self.property_cache[flow_element.datakey] = {
                    "delayExecutionList": delay_execution_list,
                    "evidenceProperties": delayed_evidence_properties
                }

            property_cache = self.property_cache[flow_element.datakey]

            # Create empty area for FlowElement properties to go

            output[flow_element.datakey] = {}

            for propertykey, propertymeta in properties.items():
                value = None
                null_reason = "Unknown"

                # Check if property has delayed execution and set in JSON if yes


                if propertykey in property_cache["delayExecutionList"]:
                    output[flow_element.datakey][propertykey.lower() + "delayexecution"] = True
                

                # Check if property has any delayed execution evidence properties and set in JSON if yes

                if propertykey in property_cache["evidenceProperties"]:
                    output[flow_element.datakey][propertykey.lower() + 'evidenceproperties'] = property_cache["evidenceProperties"][propertykey]
                

                try:

                    value_container = flowdata.get(flow_element.datakey).get(propertykey)

                    # Check if value is of the aspect property value type

                    if isinstance(value_container, object) and hasattr(value_container, "has_value" ):
                    
                        # Check if it has a value

                        if value_container.has_value():
                            value = value_container.value()
                        else:
                            value = None
                            null_reason = value_container.no_value_message()
                        
                    # Check if list of aspect property values

                    elif isinstance(value_container, list) and isinstance(value_container[0], object):

                        output = []

                        for item in value_container:
                            if item.has_value():
                                output.append(item.value())
                            else:
                                null_reason = item.no_value_message

                        value = output

                    else:

                        # Standard value
                        value = value_container
                    
                except:
                    # Catching missing property exceptions and other errors

                    continue
        
                output[flow_element.datakey.lower()][propertykey.lower()] = value
                if value is None:
                    output[flow_element.datakey.lower()][propertykey.lower() + "nullreason"] = null_reason

                sequence = flowdata.evidence.get("query.sequence")

                if sequence is None or sequence < 10: 

                    if "type" in propertymeta and propertymeta["type"].lower() == "javascript":

                        output["javascriptProperties"].append(flow_element.datakey.lower() + "." + propertykey.lower())
                 
        data = ElementDataDictionary(self, {"json": output})

        flowdata.set_element_data(data)

        return
