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

from .elementdata import ElementData


class ElementDataDictionary(ElementData):

    """!
    An extension of ElementData with dictionary object storage / lookup

    """

    def __init__(self, flow_element, contents):
        
        """!
        Constructor for Element Data Dictionary

        @type flowElement: FlowElement
        @param flowElement: FlowElement that creates the data to be stored

        @type contents: dict
        @param contents: Dictionary contents

        """

        super(ElementDataDictionary, self).__init__(flow_element)
        self.contents = {}

        for key, value in contents.items():
            self.contents[key.lower()] = value

        self.flow_element = flow_element

        ElementData(flow_element)

    def as_dictionary(self):
        
        """!
        Get the values contained in the ElementData instance as a dictionary
        of keys and values.

        @rtype: dict
        @return: Returns a dictionary of items in an ElementData

        """

        return self.contents

    def get_internal(self, key):

        """!
        Internal getter for ElementDataDictionary.contents

        @type key: string
        @param key: Key of an item in the ElementDataDictionary.

        @rtype: mixed
        @return: The data keyed under that property

        """

        if key in self.contents:

            return self.contents[key]

        else:

            return
