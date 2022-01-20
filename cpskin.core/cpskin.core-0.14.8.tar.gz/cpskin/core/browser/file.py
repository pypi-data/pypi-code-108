# -*- coding: utf-8 -*-

from plone import api
from plone.app.contenttypes.browser.file import FileView as BaseFileView


class FileView(BaseFileView):

    def __call__(self):
        context = self.context
        if api.user.is_anonymous():
            pdf_url = context.absolute_url()
            self.request.response.redirect(pdf_url)
            return ''
        return super(FileView, self).__call__()
