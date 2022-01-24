# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.contact.facetednav.browser.view import PreviewItem
from cpskin.core import utils

import six


class FacetedPreviewItem(PreviewItem):

    @property
    def phones(self):
        phones = getattr(self.context, 'phone', [])
        if isinstance(phones, six.string_types):
            phones = [phones]
        return [utils.format_phone(v) for v in phones]

    @property
    def cell_phones(self):
        cell_phones = getattr(self.context, 'cell_phone', [])
        if isinstance(cell_phones, six.string_types):
            cell_phones = [cell_phones]
        return [utils.format_phone(v) for v in cell_phones]

    @property
    def fax(self):
        fax = getattr(self.context, 'fax', None)
        if fax:
            return utils.format_phone(fax)
