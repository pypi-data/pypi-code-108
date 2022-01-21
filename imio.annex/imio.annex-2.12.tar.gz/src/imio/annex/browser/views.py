# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions import _ as _CEBA
from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm
from collective.iconifiedcategory.utils import calculate_filesize
from imio.annex.content.annex import IAnnex
from io import BytesIO
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.i18n import translate

import zipfile

# gives a human readable size of "50.0 Mb"
MAX_TOTAL_SIZE = 52400000


class DownloadAnnexesBatchActionForm(BaseBatchActionForm):

    label = _CEBA("Download annexes")
    button_with_icon = True
    apply_button_title = _CEBA('download-annexes-batch-action-but')
    section = "annexes"

    @property
    def description(self):
        """ """
        descr = super(DownloadAnnexesBatchActionForm, self).description
        descr = translate(descr, domain=descr.domain, context=self.request)
        readable_total_size = calculate_filesize(self.total_size)
        readable_max_size = calculate_filesize(MAX_TOTAL_SIZE)
        if self.total_size > MAX_TOTAL_SIZE:
            descr += translate(
                '<p class="warn_filesize">The maximum size you may download at one '
                'time is ${max_size}, here your download size is ${total_size}. '
                'Please unselect some elements, especially large elements for which '
                'size is displayed in red, download it separately.<p>',
                mapping={'max_size': readable_max_size,
                         'total_size': readable_total_size},
                domain="collective.eeafaceted.batchactions",
                context=self.request)
            self.do_apply = False
        else:
            descr += translate(
                '<p>This will download the selected elements as a Zip file.</p>'
                '<p>The total file size is <b>${total_size}</b>, when clicking on '
                '"${button_title}", you will have a spinner, wait until the Zip file '
                'is available.</p>',
                mapping={
                    'total_size': readable_total_size,
                    'button_title': translate(
                        'download-annexes-batch-action-but',
                        domain="collective.eeafaceted.batchactions",
                        context=self.request)},
                domain="collective.eeafaceted.batchactions",
                context=self.request)
        return descr

    def _total_size(self):
        """ """
        total = 0
        for brain in self.brains:
            obj = brain.getObject()
            primary_field = IPrimaryFieldInfo(obj)
            size = primary_field.value.size
            total += size
        return total

    def _update(self):
        """Can not apply action if total size exceeded."""
        self.total_size = self._total_size()
        if self.total_size > MAX_TOTAL_SIZE:
            self.do_apply = False

    def available(self):
        """ """
        return True

    def zipfiles(self, content):
        """Return zipped content."""
        fstream = BytesIO()
        zipper = zipfile.ZipFile(fstream, 'w', zipfile.ZIP_DEFLATED)
        for obj in content:
            if not IAnnex.providedBy(obj):
                continue
            primary_field = IPrimaryFieldInfo(obj)
            data = primary_field.value.data
            filename = primary_field.value.filename
            # can not do without a filename...
            if not filename:
                continue
            zipper.writestr(filename, data)
            created = obj.created()
            zipper.NameToInfo[filename].date_time = (
                created.year(), created.month(), created.day(), created.hour(), created.minute(),
                int(created.second()))
        zipper.close()
        return fstream.getvalue()

    def _apply(self, **data):
        """ """
        try:
            return self.do_zip()
        except zipfile.LargeZipFile:
            message = "Too much annexes to zip, try selecting fewer annexes..."
            api.portal.show_message(message, self.request, type="error")
            return self.request.response.redirect(self.context.absolute_url())

    def do_zip(self):
        """ Zip all of the content in this location (context)"""
        self.request.response.setHeader('Content-Type', 'application/zip')
        self.request.response.setHeader('Content-disposition', 'attachment;filename=%s.zip'
                                        % self.context.getId())
        content = [brain.getObject() for brain in self.brains]
        zipped_content = self.zipfiles(content)
        self.request.set('zip_file_content', zipped_content)
        return zipped_content

    def render(self):
        """ """
        if 'zip_file_content' in self.request:
            return self.request['zip_file_content']
        else:
            return super(DownloadAnnexesBatchActionForm, self).render()
