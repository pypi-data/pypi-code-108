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

from fiftyone_pipeline_core.elementdata import ElementData

from fiftyone_pipeline_engines.missingproperty_service import MissingPropertyService


class AspectData(ElementData):

    """!
    AspectData extends elementData by adding the option of a missing property service
    It also allows properties to be explicitly excluded by a flowElement / engine
    """

    def __init__(self, flow_element):

        """!
        Constructor for element data
        Adds default missing property service if not available
        
        @type FlowElement: 
        @param FlowElement
            
        """

        # Default missing property service
        if not hasattr(flow_element,"missing_property_service"):
            self.missing_property_service = MissingPropertyService()
        

        super(AspectData, self).__init__(flow_element)


    def get(self, key):

        """!
        get - Get a value (unless in a flowElement's restrictedProperties list)
        If property not found, call the attached missing property service
        @type key: string
        @param key: the key to get
        @rtype mixed
        @return The value stored under the chosen key
        """
        
        if hasattr(self.flow_element, "restricted_properties"):

            if not key in self.flow_element.restricted_properties:
                raise Exception("Property " + key + " was excluded from " + self.flow_element.datakey)  

        try:
            if self.get_internal(key) == None:
                return self.missing_property_service.check(key, self.flow_element)
            else:
                return self.get_internal(key)

        except:
            return self.missing_property_service.check(key, self.flow_element)
