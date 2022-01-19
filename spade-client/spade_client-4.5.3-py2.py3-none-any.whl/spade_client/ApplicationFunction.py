#
# Module: ApplicationFunction
#
# Description: A class that class binds a set of application to a function execution call.
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

APPLICATION_XML = "application/gov.lbl.nest.spade.rs.Application+xml"

from spade_client import Display, ItemsFunction, FatalError

class ApplicationFunction(ItemsFunction):
    """
    This class binds an application to a function execution call.
    
    :param application: the collection of application over which the function should be executed.
    """
    def __init__(self, session, xml = False):
        ItemsFunction.__init__(self, session, xml)


    def _display_report(self,
                        action,
                        report):
        if "bundles" == report.tag:
            section = action.find('name').text.title()
            Display.bundles_result(report,
                                   section)
            return
        if "digest" == report.tag:
            section = action.find('name').text.title()
            Display.digest_result(report,
                                  section)
            return
        if "registry" == report.tag:
            section = action.find('name').text.title()
            Display.registry_result(report,
                                    section)
            return
        if "spade_config" == report.tag:
            section = action.find('name').text.title()
            Display.configuration_result(report,
                                         section)
            return
        if "tickets" == report.tag:
            section = action.find('name').text.title()
            Display.registry_result(report,
                                    section)
            return
        Display.status(report)
