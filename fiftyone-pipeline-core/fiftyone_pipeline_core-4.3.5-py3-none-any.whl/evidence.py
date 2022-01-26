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


class Evidence:

    def __init__(self, flowdata):

        """!
        Constructor for Evidence container on a FlowData

        @type flowdata: FlowData
        @param flowdata: Parent FlowData

        """
        self.evidence = {}

        self.flowdata = flowdata

    def add(self, key, value):

        """!
        Add a single piece of evidence by its element and value

        @type key: string
        @param key: a flowElement's datakey

        @type value: mixed
        @param value: a piece of evidence

        """

        keep = False

        for flow_element in self.flowdata.pipeline.flow_elements:

            if flow_element.filter_evidence_key(key):
                keep = True

        if keep:
            self.evidence[key] = value

    def add_from_dict(self, evidence_dictionary):

        """!
        Helper function to set multiple pieces of evidence from a dict

        @type evidence_dictionary: dict
        @param evidence_dictionary: Dict of evidence

        """

        if not type(evidence_dictionary) is dict:
            self.flowdata.set_error("core", "Must pass valid dictionary.")

        for key, value in evidence_dictionary.items():
            self.add(key, value)

    def get(self, key):

        """!
        Get a piece of evidence by key

        @type key: string
        @param key: A FlowElement's datakey

        @rtype: dict
        @return: A piece of evidence

        """

        if key in self.evidence:

            return self.evidence[key]

        else:

            return

    def get_all(self):

        """!
        Get all evidence

        @rtype: dict
        @return: Returns everything in this Evidence.evidence
        """

        return self.evidence

