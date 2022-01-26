#
# Module: TimingFunction
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

from spade_client import Display, ItemsFunction, FatalError

class TimingFunction(ItemsFunction):
    """
    This class binds an application to a function execution call.
    
    :param application: the collection of application over which the function should be executed.
    """
    def __init__(self, after, before, limit, neighbor, registrations, session, xml = False):
        ItemsFunction.__init__(self, session, xml)
        self.after = after
        self.before = before
        self.limit = limit
        self.neighbor = neighbor
        self.registrations = registrations


    def _prepare_query(self):
        query_string = ''
        conjunction = ''
        if None != self.after:
            query_string = query_string + 'after=' + self.after.replace('+', '%2B')
            conjunction = '&'
        if None != self.before:
            query_string = query_string + conjunction +  'before=' + self.before.replace('+', '%2B')
            conjunction = '&'
        if None != self.limit:
            query_string = query_string + conjunction +  'max=' + str(self.limit)
            conjunction = '&'
        if None != self.neighbor:
            query_string = query_string + conjunction +  'neighbor=' + self.neighbor
            conjunction = '&'
        if None != self.registrations:
            for registration in self.registrations:
                query_string = query_string + conjunction +  'registration=' + registration
                conjunction = '&'
        if '' == query_string:
            return None
        return query_string


    def _display_report(self,
                        action,
                        report):
        section = action.find('name').text.title()
        Display.digests_result(report, section)
