# -*- coding: utf-8 -*-
from cpskin.core.utils import image_scale
from plone import api
from Products.Five.browser import BrowserView


class DescriptionView(BrowserView):

    def extra_output_and_no_folderish(self):
        return self.context.text.output_relative_to(self.context)
