# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.layout import FacetedLayout
from zope.component import queryAdapter
from zope.globalrequest import getRequest


class FacetedMultipleLayout(FacetedLayout):

    def __init__(self, *args, **kwargs):
        super(FacetedMultipleLayout, self).__init__(*args, **kwargs)
        self.request = getattr(self.context, 'REQUEST', getRequest())

    @property
    def layout(self):
        cid, criterion = self.get_criterion()
        default = criterion and criterion.default or None
        layout = self.request.form.get('%s[]' % cid, default)  # noqa
        if not layout:
            return super(FacetedMultipleLayout, self).layout
        return layout

    def get_criterion(self):
        criteria = queryAdapter(self.context, ICriteria)
        criterion = [(cid, c) for cid, c in criteria.items()
                     if c.widget == 'layout']
        return len(criterion) > 0 and criterion[0] or (None, None)
