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

from fiftyone_pipeline_engines.aspectdata_dictionary import AspectDataDictionary

from fiftyone_pipeline_engines.missingproperty_service import MissingPropertyService

class OnPremiseMissingPropertyService(MissingPropertyService):

    def check(self, key, flow_element):

        raise Exception("Property " + key + " not found in data for element " + flow_element.datakey + ". This is because your resource key does not include access to this property. Properties that are included for this key under device are " + ', '.join(list(flow_element.get_properties().keys())) + ". For more details on resource keys, see our explainer: https://51degrees.com/documentation/_info__resource_keys.html")

class CloudData(AspectDataDictionary):

    """!
    Extention of AspectData made for retrieving cloud engine results
    """

    def __init__(self, flow_element, contents):
        
        """!
        Constructor for cloud_data
        @type flow_element: FlowElement
        @param flow_element: FlowElement / Engine the data is keyed under
        @type contents: dict
        @param contents: Results from cloud engine's process method
        """

        super(CloudData, self).__init__(flow_element, contents)

        self.missing_property_service = OnPremiseMissingPropertyService()
