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

from .evidence_keyfilter import EvidenceKeyFilter


class FlowElement(object):

    """!
    A FlowElement is placed inside a Pipeline
    It receives Evidence via a FlowData object
    It uses this to optionally create ElementData on the FlowData
    Any errors in processing are caught in the FlowData's errors object
    
    """

    def __init__(self):

        """!
        List of Pipelines the FlowElement has been added to 

        """
        self.pipelines = []
        self.properties = {}
        self.datakey = ""

        # Allow elements to be excluded from messages listing
        # all flowelements. For system elements like the JavaScriptBuilder
        
        self.exclude_from_messages = False

    def process(self, flowdata):

        """!
        Function for getting the FlowElement's EvidenceKeyFilter
        Used by the filterEvidence method

        @type flowdata: FlowData
        @param flowdata: FlowData to be processed

        @rtype: mixed
        @return: Returns whatever the self.processInternal method is set to return

        """

        return self.process_internal(flowdata)

    def on_registration(self, pipeline):

        """!
        Function called when an element is added to the pipeline. 
        Used for example, for elements that depend on other elements in a pipeline

        @type pipeline: Pipeline
        @param pipeline: Pipeline the element has been added to

        """

        pass

    def get_evidence_key_filter(self):

        """!
        Filter FlowData evidence using the FlowElement's EvidenceKeyFilter

        @rtype: EvidenceKeyFilter
        @return: Returns an EvidenceKeyFilter

        """

        return EvidenceKeyFilter()

    def filter_evidence(self, flowdata):

        """!
        Filter FlowData evidence using the FlowElement's EvidenceKeyFilter

        @type flowdata: FlowData
        @param flowdata: a FlowData that has some Evidence set

        @rtype: dict
        @return: Returns a dictionary of evidence that has passed the filter

        """

        filter = self.get_evidence_key_filter()

        return filter.filter_evidence(flowdata.evidence.get_all())

    def filter_evidence_key(self, key):

        """!
        Filter FlowData.evidence using the flowElement's EvidenceKeyFilter
        with the property key of evidence of interest.

        @type key: string
        @param key: the property key being sought within FlowData.evidence

        @rtype: dict
        @return: Returns a dictionary containing the property key and the evidence related to it as its value

        """

        filter = self.get_evidence_key_filter()

        return filter.filter_evidence_key(key)

    def process_internal(self, flowdata):

        """!
        The method behind FlowElement.Process - it is called by the process() function.
        It is usually overridden by specific flowElements to do their core work.

        @type flowdata: FlowData
        @param flowdata: FlowData to be processed

        @rtype: bool
        @return: Returns True

        """

        return True

    def get_properties(self):

        """!
        Get the FlowElement.properties of a FlowElement.
        
        This is usually overridden by specific flowElements.

        @rtype: DataPropertyDictionary
        @return: Returns dictionary of the FlowElement's properties

        """

        return {k.lower(): v for k, v in self.properties.items()}
