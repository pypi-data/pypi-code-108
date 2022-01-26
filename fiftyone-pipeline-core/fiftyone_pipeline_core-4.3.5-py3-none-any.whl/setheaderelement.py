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
from .messages import Messages
import re

class SetHeaderElement(FlowElement):

    """!
    Set response headers element class. This is used to get response
    headers based on what the browser supports. For example, newer
    Chrome browsers support the Accept-CH header.

    """

    def __init__(self):

        super(SetHeaderElement, self).__init__()

        self.datakey = "set-headers"

        self.properties = {"responseheaderdictionary" : { "type": "dict"} }

        self.setheader_properties = {}
		
        self.exclude_from_messages = True

    def process_internal(self, flowdata):
    
        """!
        
        Add the response header dictionary to the FlowData.
        @type flowdata: FlowData
        @param flowdata: A FlowData
    
        """

        if not self.setheader_properties:
            self.setheader_properties = self.get_setheader_properties_pipeline(flowdata.pipeline)
        
        response_headers = self.get_response_header_value(flowdata, self.setheader_properties)

        data = ElementDataDictionary(self, {"responseheaderdictionary": response_headers})

        flowdata.set_element_data(data)

        return

    def get_setheader_properties_pipeline(self, pipeline):
        
        """!
        Get All the properties starting with SetHeader string from pipeline
        
        @param pipeline: A Pipeline object
        @rtype dict
        @return A dictionary object containing SetHeader properties list against flowElement

        """
        
        setHeader_properties_dict = {}

        # Loop over each flowElement in pipeline to check SetHeader properties
        for flow_element in pipeline.flow_elements:

            # Get the properties against the flowElement
            properties = flow_element.get_properties()

            setHeader_element_list = []

            # Loop over each flowElement property
            for propertykey, propertymeta in properties.items():

                # Check if the property starts with SetHeader
                if("setheader" in propertykey):
                    setHeader_element_list.append(propertymeta["name"])

            # Add SetHeader element list in dict against flowElement.datakey as key
            if setHeader_element_list:
                setHeader_properties_dict[flow_element.datakey] = setHeader_element_list
        
        return setHeader_properties_dict

    def get_response_header_value(self, flowData, setHeader_properties_dict):

        """!
        Get response header value using set header properties from FlowData
        
        @type flowdata: FlowData 
        @param flowdata: A processed FlowData object containing setheader properties
        @param setHeader_properties_dict: A processed FlowData object containing setheader properties
        @rtype dict
        @return A dictionary object containing SetHeader properties list against flowElement

        """

        response_headers_dict = {}

        # Loop over all the flowElements to process Set Header properties for User Agent Client Hints
        for element_datakey, setHeader_element_list in setHeader_properties_dict.items():

            # Loop over each setHeader property of the element  
            for setHeader_property in setHeader_element_list:

                # Get response header key to be set in response
                response_header = self.get_response_header_name(setHeader_property)

                # Get SetHeader property value from elementData
                setHeader_value = self.get_property_value(flowData, element_datakey, setHeader_property)

                # Process and Add property in the dict against response header key
                if(response_header in response_headers_dict):
                    response_header_value = response_headers_dict[response_header]
                    if(response_header_value == ""):
                        response_header_value = setHeader_value
                    else:
                        if(setHeader_value != ""):
                            response_header_value = response_header_value + "," + setHeader_value
                    response_headers_dict[response_header] = response_header_value
                else:
                    response_headers_dict[response_header] = setHeader_value

        return response_headers_dict

    def get_property_value(self, flowData, element_key, property_key):

        """!
        Try to get the value for the given element and property.
        If the value cannot be found or is null/unknown, then ""
        will be returned.

        @param flowData: A processed FlowData instance to get the value from.
        @param element_key: Key for the element data to get the value from
        @param property_key: Name of the property to get the value for.
        @rtype String
        @return value or empty string

        """

        value = ""
        
        try:
            # Get the elementData from flowData that contains required property.
            element_data = flowData.get(element_key)
        except Exception:
            print(Messages.ELEMENT_NOT_FOUND.format(element_key))
            return ""

        try:
            property = element_data[property_key.lower()]
        except:
            print(Messages.PROPERTY_NOT_FOUND.format(property_key, element_key))
            return ""

        if(property.has_value() and property.value() not in ["Unknown", "noValue"]):
            value = property.value()
        else:
            value = ""

        return value

    def get_response_header_name(self, property_key):
        
        """!
        Determines which response header the property value will be appended to by 
        stripping the 'SetHeader' string and the 'Component Name' from the property name.
        
        @param property_key: Key for SetHeaderAcceptCH property
        @rtype String
        @return Response Header name

        """

        actual_property_name = property_key
        response_header = ""

		# Check if property name starts with SetHeader.
		# If Yes, Discard SetHeader from property name.
        if ("SetHeader" not in property_key[0:9]):
            raise Exception(Messages.PROPERTY_NOT_SET_HEADER.format(actual_property_name))
        else:
            # Discard SetHeader from property_key
            property_key = property_key.replace("SetHeader", "", 1)

		# Check if the first letter of Component name is in Uppercase
		# If Yes, Split the propertyKey based on Uppercase letters
        if(property_key[0].isupper() is False):
            raise Exception(Messages.WRONG_PROPERTY_FORMAT.format(actual_property_name))
        else:
            # Get the Component name string to be removed from the key    
            parts = re.findall(r'([A-Z][^A-Z]*)', property_key)
            discard_letter = parts[0]
        
		# Check if property name contains the header name that starts with upper case
		# If Yes, Remove the previously found Component Name to get the Header Name
        if len(parts)<=1 :
            raise Exception(Messages.WRONG_PROPERTY_FORMAT.format(actual_property_name))

        else:
            # Replace the first letter with the empty string.
            response_header = property_key.replace(discard_letter, "")

        return response_header
