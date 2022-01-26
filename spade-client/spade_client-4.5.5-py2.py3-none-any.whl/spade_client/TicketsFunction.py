#
# Module: TicketsFunction
#
# Description: A class that class binds a set of tickets to a function execution call.
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

TICKETS_XML = "application/gov.lbl.nest.spade.rs.Tickets+xml"

from spade_client import Display, ItemsFunction, FatalError

class TicketsFunction(ItemsFunction):
    """
    This class binds a set of tickets to a function execution call.
    
    :param array tickets: the collection of tickets over which the function should be executed.
    """
    def __init__(self, tickets, session, xml = False):
        self.tickets = tickets
        ItemsFunction.__init__(self, session, xml)


    def _display_report(self,
                        action,
                        report):
        section = action.find('name').text.title()
        if "digests" == report.tag:
            Display.digests_result(report,
                                   section)
            return
        Display.tickets_result(report,
                               section)


    def _prepare_document(self, media_type):
        """
        Prepares a Bundles document contains the specified bundle identities
        """
        if TICKETS_XML != media_type:
            raise FatalError('Can not handle "' + media_type + '" requested for this action"', -5, None)
        document = ET.Element('tickets')
        if None != self.tickets:
            for ticket in self.tickets:
                ticketElement = ET.Element('ticket')
                ticketElement.text = ticket
                document.append(ticketElement)
        return document
