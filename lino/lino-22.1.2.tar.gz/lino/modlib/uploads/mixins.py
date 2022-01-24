# -*- coding: UTF-8 -*-
# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import shutil
from pathlib import Path

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage

from etgen.html import E
from lino.api import dd, rt, _
from .choicelists import UploadAreas


def safe_filename(name):
    name = name.encode('ascii', 'replace').decode('ascii')
    name = name.replace('?', '_')
    name = name.replace('/', '_')
    name = name.replace(' ', '_')
    return name


def needs_update(src, dest):
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return False
    return True

def make_uploaded_file(filename, src=None, upload_date=None):
    """
    Create a dummy file that looks as if a file had really been uploaded.

    """
    if src is None:
        src = Path(__file__).parent / "dummy_upload.pdf"
    if upload_date is None:
        upload_date = dd.demo_date()
    assert src.exists()
    filename = default_storage.generate_filename(safe_filename(filename))
    upload_to = Path(upload_date.strftime(settings.SITE.upload_to_tpl))
    upload_filename = default_storage.generate_filename(str(upload_to / filename))
    dest = Path(settings.MEDIA_ROOT) / upload_filename
    if needs_update(src, dest):
        print("cp {} {}".format(src, dest))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    return upload_filename

def demo_upload(filename, src=None, upload_date=None, **kw):
    """
    Return an upload entry that looks as if a file had really been uploaded.

    """
    kw['file'] = make_uploaded_file(filename, src, upload_date)
    return rt.models.uploads.Upload(**kw)


class UploadController(dd.Model):

    class Meta(object):
        abstract = True

    def get_upload_area(self):
        return UploadAreas.general

    def get_uploads_volume(self):
        return None

    if dd.is_installed("uploads"):

        show_uploads = dd.ShowSlaveTable(
            'uploads.UploadsByController',
            react_icon_name= "pi-upload",
            button_text="❏")  # 274f
            # button_text="⍐")  # 2350
            # button_text="🖿")  # u"\u1F5BF"


class GalleryViewable(dd.Model):

    class Meta(object):
        abstract = True

    def get_gallery_item(self, ar):
        return {}


class UploadBase(GalleryViewable):

    class Meta(object):
        abstract = True

    file = models.FileField(
        _("File"), blank=True, upload_to=settings.SITE.upload_to_tpl)
    mimetype = models.CharField(
        _("MIME type"), blank=True, max_length=255, editable=False)
    file_size = models.IntegerField(_("File size"), editable=False, null=True)

    def handle_uploaded_files(self, request, file=None):
        #~ from django.core.files.base import ContentFile
        if not file and not 'file' in request.FILES:
            dd.logger.debug("No 'file' has been submitted.")
            return
        uf = file or request.FILES['file']  # an UploadedFile instance

        self.save_newly_uploaded_file(uf)

    def save_newly_uploaded_file(self, uf):
        #~ cf = ContentFile(request.FILES['file'].read())
        #~ print f
        #~ raise NotImplementedError
        #~ dir,name = os.path.split(f.name)
        #~ if name != f.name:
            #~ print "Aha: %r contains a path! (%s)" % (f.name,__file__)
        self.size = uf.size
        self.mimetype = uf.content_type

        if self.size > settings.SITE.max_file_size:
            raise ValidationError(
                _("File size is {}! Must be below {}.").format(
                    filesizeformat(self.size),
                    filesizeformat(settings.SITE.max_file_size)))

        # Certain Python versions or systems don't manage non-ascii filenames,
        # so we replace any non-ascii char by "_". In Py3, encode() returns a
        # bytes object, but we want the name to remain a str.

        #~ dd.logger.info('20121004 handle_uploaded_files() %r',uf.name)
        name = safe_filename(uf.name)

        # Django magics:
        self.file = name  # assign a string
        ff = self.file  # get back a FileField instance !
        #~ print 'uf=',repr(uf),'ff=',repr(ff)

        #~ if not ispure(uf.name):
            #~ raise Exception('uf.name is a %s!' % type(uf.name))

        ff.save(name, uf, save=False)

        # The expression `self.file`
        # now yields a FieldFile instance that has been created from `uf`.
        # see Django FileDescriptor.__get__()

        dd.logger.info("Wrote uploaded file %s", ff.path)

    def full_clean(self, *args, **kw):
        super(UploadBase, self).full_clean(*args, **kw)
        self.file_size = self.get_real_file_size()

    def get_gallery_item(self, ar):
        return dict(
            image_src=settings.SITE.build_media_url(self.file.name))

    def get_real_file_size(self):
        if self.file:
            return self.file.size
        if hasattr(self, 'volume_id') and self.volume_id and self.library_file:
            pth = os.path.join(self.volume.root_dir, self.library_file)
            return os.path.get_size(pth)

    def get_file_button(self, text=None):
        if text is None:
            text = str(self)
        if self.file.name:
            url = settings.SITE.build_media_url(self.file.name)
            return E.a(text, href=url, target="_blank")
        return text
