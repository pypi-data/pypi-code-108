# Copyright 2019 Splunk Inc. All rights reserved.
"""
Splunk AppInspect certification events listeners base class module
"""


class Listener(object):
    """
    Splunk AppInspect certification events listeners base class
    """

    def handle_event(self, event, *args):
        """
        Entry point to call event handler
        """
        eventname = "on_" + event
        if hasattr(self, eventname):
            getattr(self, eventname)(*args)
