# -*- coding: utf-8 -*-
from zope.component import adapter
from zope.interface import implementer
from rer.sitesearch.interfaces import ISiteSearchCustomFilters
from zope.interface import Interface
from rer.sitesearch import _
from zope.i18n import translate


@adapter(Interface, Interface)
@implementer(ISiteSearchCustomFilters)
class EventsAdapter(object):
    """ """

    label = _("event_adapter_label", default=u"Events")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {
            "start": {
                "type": "date",
                "label": translate(
                    _("filter_start_label", default=u"Start date"),
                    context=self.request,
                ),
            },
            "end": {
                "type": "date",
                "label": translate(
                    _("filter_end_label", default=u"End date"),
                    context=self.request,
                ),
            },
        }
