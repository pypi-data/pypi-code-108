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


class ElementData(object):

    """!
    Core ElementData class
    Stores information created by a FlowElement based on FlowData.
    Stored in FlowData

    """

    def __init__(self, flow_element):

        """!
        Constructor for ElementData

        @type flow_element: FlowElement
        @param flow_element: FlowElement that data has been created by

        """

        self.flow_element = flow_element

    def get(self, key):

        """!
        Get a value from the elementData contents
        Proxy for the ElementData.getInternal method

        @type key: str
        @param: key

        @rtype: mixed
        @return: Returns specified property from the data

        """

        return self.get_internal(key.lower())

    def __getattr__(self, key):

        """!
        Magic getter for a property from the data
        Allowing  user to write for example Data.IsMobile rather than Data.get("IsMobile)

        @type key: str
        @param key: property

        @rtype: mixed
        @return: Returns specified property from the data
        """

        return self.get(key)

    def __getitem__(self, flow_element_key):
    
        """!
        Magic method in Python, which when used in a class, allows its instances to use the [] (indexer) operators.
        For example, instead of `flowdata.get("device")` you can use `flowdata["device"]`

        @type flow_element_key: string
        @param flow_element_key: datakey of the FlowElement that created the data of interest

        @rtype: ElementData
        
        """

        return self.get(flow_element_key)
		
    def get_internal(self, key):
        
        """!
        Returns the requested property from the data
        Overridden by specific ElementData instances.

        @type key: str
        @param key: property

        @rtype: mixed
        @return: Returns Requested property from data
        """

        return

    def get_properties(self):

        """!
        Proxy to the data's flowElement properties.
        Gets the FlowElement.properties of the parent FlowElement.

        @rtype: DataPropertyDictionary
        @return: Returns dictionary of the parent FlowElement's properties
        """

        return self.flow_element.get_properties()
