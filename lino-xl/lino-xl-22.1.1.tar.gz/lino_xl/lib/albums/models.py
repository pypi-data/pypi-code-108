# -*- coding: UTF-8 -*-
# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
from os.path import join, exists
import glob
from pathlib import Path
from datetime import datetime

from django.db import models
from django.db.models.fields.files import FieldFile
from django.conf import settings
from django.utils.text import format_lazy
# from lino.api import string_concat
from django.utils.translation import pgettext_lazy as pgettext
from django.template.defaultfilters import filesizeformat
from django.core.exceptions import ValidationError

from etgen.html import E, join_elems, tostring
from lino.api import dd, rt, _
from lino.core.gfks import gfk2lookup
from lino.core.utils import model_class_path
from lino import mixins
from lino.modlib.gfks.mixins import Controllable
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator
from lino.mixins import Hierarchical
from lino.mixins.sequenced import Sequenced
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.uploads.mixins import UploadBase, safe_filename, GalleryViewable

# class ShowGallery(dd.ShowTable):
#     # select_rows = False
#     pass


def filename_leaf(name):
    i = name.rfind('/')
    if i != -1:
        return name[i + 1:]
    return name


class Album(BabelDesignated, Hierarchical):

    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'Album')
        verbose_name = _("Album")
        verbose_name_plural = _("Albums")

class File(UploadBase, UserAuthored):

    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'File')
        verbose_name = _("Media file")
        verbose_name_plural = _("Media files")

    # show_gallery = ShowGallery()

    album = dd.ForeignKey("albums.Album", blank=True, null=True)

    description = models.CharField(
        _("Description"), max_length=200, blank=True)

    copyright = models.CharField(
        _("Copyright"), max_length=100, blank=True)

    def __str__(self):
        if self.description:
            s = self.description
        elif self.file:
            s = filename_leaf(self.file.name)
        else:
            s = str(self.id)
        return s

    def get_memo_command(self, ar=None):
        if dd.is_installed('memo'):
            cmd = f"[image {self.pk}"
            if self.description:
                cmd += " " + self.description + "]"
            else:
                cmd += "]"
            return cmd
        return None

    def get_gallery_item(self, ar):
        d = super(File, self).get_gallery_item(ar)
        d.update(title=str(self), id=self.pk)
        cmd = self.get_memo_command(ar)
        if cmd is not None:
            d.update(memo_cmd=cmd)
        return d

    @dd.displayfield(_("Description"))
    def description_link(self, ar):
        s = str(self)
        if ar is None:
            return s
        return self.get_file_button(s)

    @dd.htmlbox(_("Thumbnail"))
    def thumbnail(self, ar):
        url = settings.SITE.build_media_url(self.file.name)
        return '<img src="{}" style="height: 15ch; max-width: 22.5ch">'.format(url)

    @dd.htmlbox(_("Thumbnail Medium"))
    def thumbnail_medium(self, ar):
        url = settings.SITE.build_media_url(self.file.name)
        return '<img src="{}" style="width: 30ch;">'.format(url)

    @dd.htmlbox(_("Thumbnail Large"))
    def thumbnail_large(self, ar):
        url = settings.SITE.build_media_url(self.file.name)
        return '<img src="{}" style="width: 70ch;">'.format(url)

    @dd.chooser(simple_values=True)
    def library_file_choices(self, volume):
        if volume is None:
            return []
        return list(volume.get_filenames())

    def handle_uploaded_files(self, request, file=None):
        if file and file.content_type.split('/')[0] != 'image':
            raise ValidationError(
                _("Invalid Type: This is not an image! Please choose an image to upload."))
        super().handle_uploaded_files(request, file)


    def clean(self):
        if self.album == None:
            """
            If an album was not designated for the uploaded file then,
            if an album exists for current month, add the file to it,
            otherwise create one.
            """
            date = datetime.today()

            alb_y, _ = Album.objects.get_or_create(
                parent=None, designation=str(date.year))
            alb_m, _ = Album.objects.get_or_create(
                parent=alb_y, designation=('0'+str(date.month))[-2:])

            self.album = alb_m
        super().clean()


dd.update_field(File, 'user', verbose_name=_("Uploaded by"))


class UploadNewFileField(dd.VirtualField):

    """An editable virtual field needed for uploading new files.
    """
    editable = True

    def __init__(self, upload_to_model, label):
        self.upload_to_model = upload_to_model
        return_type = models.FileField(label)
        dd.VirtualField.__init__(self, return_type, None)

    def set_value_in_object(self, request, obj, value):
        if value is not None and value != "":
            target = self.upload_to_model(file=value)
            target.full_clean()
            target.save()
            obj.file = target

    def value_from_object(self, obj, ar):
        return None

class FileUsage(Sequenced, Controllable, GalleryViewable):
    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'FileUsage')
        verbose_name = _("Usage")
        verbose_name_plural = _("File usages")

    file = dd.ForeignKey("albums.File")
    upload_new_file = UploadNewFileField(File, _("Upload new file"))

    primary_image = models.BooleanField(default=False, verbose_name=_("Primary Image"))

    delete_old_primary_image_field = dd.VirtualBooleanField('delete_old_primary_image', _("Delete Old Primary Image"))
    delete_old_primary_image = False

    def handle_uploaded_files(self, request, file=None):
        if not file and not 'upload_new_file' in request.FILES:
            dd.logger.debug("No new file has been submitted.")
            return
        file = file or request.FILES['upload_new_file']
        if file.content_type.split('/')[0] != 'image':
            raise ValidationError(
                _("Invalid Type: This is not an image! Please choose an image to upload."))

        self.upload_new_file = file

    def get_gallery_item(self, ar):
        d = self.file.get_gallery_item(ar)
        d.update(id=self.pk)
        return d

    def clean(self):
        super().clean()
        if self.primary_image and self.owner is not None:
            qs = self.__class__.objects.filter(owner_type=self.owner_type,
                owner_id=self.owner_id, primary_image=True).exclude(file=self.file)
            assert qs.count() <= 1
            if qs.count():
                obj = qs[0]
                if self.delete_old_primary_image:
                    file = obj.file
                    obj.delete()
                    file.delete()
                else:
                    obj.primary_image = False
                    obj.save()


class Files(dd.Table):
    model = 'albums.File'
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    column_names = "file user album description thumbnail *"
    order_by = ['-id']

    detail_layout = dd.DetailLayout("""
    file album user
    description
    thumbnail_large copyright
    """, window_size=(80, 'auto'))

    insert_layout = """
    description
    album
    file
    """

    card_layout = """
    description
    thumbnail
    """

    parameters = mixins.ObservedDateRange(
        album=dd.ForeignKey(
            'albums.Album', blank=True, null=True))
    params_layout = "user album"

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        qs = super(Files, cls).get_request_queryset(ar, **filter)
        pv = ar.param_values
        if pv.user:
            qs = qs.filter(user=pv.user)
        return qs


class AllFiles(Files):
    use_as_default_table = False
    required_roles = dd.login_required(OfficeStaff)


class MyFiles(My, Files):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    column_names = "file thumbnail user album description *"


class AlbumDetail(dd.DetailLayout):
    main = """
    treeview_panel general
    """

    general = """
    designation id parent
    FilesByAlbum #AlbumsByAlbum
    """

class Albums(dd.Table):
    model = 'albums.Album'
    required_roles = dd.login_required(OfficeStaff)

    column_names = "designation parent *"
    detail_layout = "albums.AlbumDetail"
    insert_layout = "designation parent"


class FilesByAlbum(Files):
    master_key = "album"
    display_mode = "gallery"
    column_names = "file description thumbnail *"


class AlbumsByAlbum(Albums):
    label = "Albums"
    master_key = "parent"


class FileUsages(dd.Table):
    model = 'albums.FileUsage'
    required_roles = dd.login_required((OfficeUser, OfficeOperator))

    detail_layout = """
    file id
    file__file_size
    file__thumbnail
    owner seqno primary_image
    """

    insert_layout = """
    file
    upload_new_file
    seqno primary_image delete_old_primary_image_field
    """

    @classmethod
    def get_choices_text(cls, obj, request, field):
        if str(field) == 'albums.FileUsage.file':
            return str(obj) + "&nbsp;<span style=\"float: right;\">" + obj.thumbnail + "</span>"
        return str(obj)



class UsagesByController(FileUsages):
    label = _("Media files")
    master_key = 'owner'
    column_names = "seqno file file__thumbnail *"
    display_mode = "gallery"
    # display_mode = "summary"
    # summary_sep = lambda : ", "

@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`

    if not sender.is_installed('memo'):
        return

    mp = sender.plugins.memo.parser

    def manage_file_usage(ar, usages):
        if ar is None or len(ar.selected_rows) != 1: return

        usages = set(usages)
        owner = ar.selected_rows[0]
        FileUsage = rt.models.albums.FileUsage
        lookup = gfk2lookup(FileUsage.owner, owner)
        qs = set(FileUsage.objects.filter(**lookup))
        for obj in qs:
            if obj.file not in usages:
                qs.remove(obj)
                obj.delete()
        qs = {obj.file for obj in qs}
        for file in usages.difference(qs):
            fu = FileUsage(file=file, **lookup)
            fu.full_clean()
            fu.save()

    def render_img_thumbnail(ar, s, cmdname, usages):
        args = s.split(None, 1)
        if len(args) == 1:
            pk = s
            caption = None
        else:
            pk = args[0]
            caption = args[1]

        file = rt.models.albums.File.objects.get(pk=pk)

        if usages.get(cmdname, None) is None:
            usages[cmdname] = [file]
        else:
            usages[cmdname].append(file)

        thumbnail = file.thumbnail_large

        if file.description is not None and caption is None:
            caption = file.description

        elem = (f'<figure class="lino-memo-image">{thumbnail}<figcaption' +
            ' style="text-align: center;">{caption}</figcaption></figure>')

        return elem

    mp.register_django_model('image', rt.models.albums.File,
        cmd=render_img_thumbnail,
        manage_usage=manage_file_usage,
        title=lambda obj: obj.description)
