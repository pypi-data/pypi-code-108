 ##********************************************************************
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

 # Messages which may be reused for various property exceptions.

class Messages():

    # Property does not start with SetHeader. This takes the name of a property
    # as a format argument.

    PROPERTY_NOT_SET_HEADER = "Property Name '{}' does not start with 'SetHeader'."

    # Property Name is not in the valid format. This takes the property name 
    # as format argument.

    WRONG_PROPERTY_FORMAT = \
        "Property Name '{}' is not in the expected format i.e. SetHeader[Component][HeaderName]. "
    
    # Element not found in flowData. This takes the element datakey 
    # as format argument.
    ELEMENT_NOT_FOUND = \
        "Element '{}' is not present in the FlowData. "

    # Property not found in flowData. This takes the element datakey
    # and property names as format arguments.
    PROPERTY_NOT_FOUND = \
        "Property '{}' is not present in the FlowData against '{}' ElementData. "

    # FlowData already processed.
    FLOW_DATA_PROCESSED = "FlowData already processed"