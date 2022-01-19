#
# Module: BundlesFunction
#
# Description: A class that class binds a set of bundles to a function execution call.
#

from __future__ import print_function

import sys

# This code is needed is pyxml if installed
pyxml=None
index = 0
for p in sys.path:
    if -1 != p.find('pyxml'):
         pyxml = p
    index += 1
if None != pyxml:
    sys.path.remove(pyxml)

import xml.etree.ElementTree as ET

BUNDLES_XML = 'application/gov.lbl.nest.spade.rs.Bundles+xml'
LOCATIONS_XML = 'application/gov.lbl.nest.spade.rs.Locations+xml'

from spade_client import Display, ItemsFunction, FatalError

class BundlesFunction(ItemsFunction):
    """
    This class binds a set of bundles to a function execution call.
    
    :param array bundles: the collection of bundles over which the function should be executed.
    """
    def __init__(self, bundles, session, xml = False):
        self.bundles = bundles
        ItemsFunction.__init__(self, session, xml)


    def _display_report(self,
                        action,
                        report):
        section = action.find('name').text.title()
        if "digests" == report.tag:
            Display.digests_result(report,
                                   section)
            return
        Display.bundles_result(report,
                               section)


    def _prepare_document(self, media_type):
        """
        Prepares a Bundles document contains the specified bundle identities
        """
        if BUNDLES_XML != media_type and LOCATIONS_XML != media_type :
            raise FatalError('Can not handle "' + media_type + '" requested for this action"', -5, None)
        document = ET.Element('bundles')
        if None != self.bundles:
            for bundle in self.bundles:
                bundleElement = ET.Element('bundle')
                nameElement = ET.Element('name')
                nameElement.text = bundle
                bundleElement.append(nameElement)
                document.append(bundleElement)
        return document
