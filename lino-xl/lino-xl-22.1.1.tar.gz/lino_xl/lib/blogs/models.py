# -*- coding: UTF-8 -*-
# Copyright 2009-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime
from io import StringIO
from lxml import etree

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from django.utils import timezone

from lino.api import dd, rt
from lino import mixins
from lino.core import constants
from lino.core.gfks import gfk2lookup
from lino.modlib.gfks.mixins import Controllable
from lino_xl.lib.topics.models import AddInterestField
from lino.modlib.users.mixins import My, UserAuthored
from lino.modlib.comments.mixins import Commentable
from lino.modlib.publisher.mixins import Publishable, PreviewPublication
# from lino.modlib.printing.mixins import PrintableType, TypedPrintable
from lino.mixins.periods import CombinedDateTime
from lino.core.requests import BaseRequest
from lino.modlib.memo.mixins import Previewable
from lino.utils import join_elems
from etgen.html import E, tostring

from .roles import BlogsReader

html_parser = etree.HTMLParser()



class EntryType(mixins.BabelNamed):

    templates_group = 'blogs/Entry'

    class Meta:
        app_label = 'blogs'
        verbose_name = _("Blog Entry Type")
        verbose_name_plural = _("Blog Entry Types")

    #~ name = models.CharField(max_length=200)
    important = models.BooleanField(
        verbose_name=_("important"),
        default=False)
    remark = models.TextField(verbose_name=_("Remark"), blank=True)

    def __str__(self):
        return self.name


class EntryTypes(dd.Table):
    model = 'blogs.EntryType'
    # column_names = 'name build_method template *'
    order_by = ["name"]

    detail_layout = """
    id name
    # build_method template
    remark:60x5
    blogs.EntriesByType
    """


class Entry(UserAuthored, Controllable, CombinedDateTime,
            Previewable, Publishable, Commentable):

    class Meta:
        app_label = 'blogs'
        verbose_name = _("Blog Entry")
        verbose_name_plural = _("Blog Entries")

    title = models.CharField(_("Heading"), max_length=200, blank=True)
    pub_date = models.DateField(
        _("Publication date"), blank=True, null=True)
    pub_time = dd.TimeField(
        _("Publication time"), blank=True, null=True)
    entry_type = dd.ForeignKey('blogs.EntryType', blank=True, null=True)
    language = dd.LanguageField()

    publisher_location = "bl"
    publisher_page_template = "blogs/entry_page.html"
    publisher_item_template = "blogs/entry_item.html"
    preview_publication = PreviewPublication(label=_("Static View"))

    def __str__(self):
        if self.title:
            return self.title
        if self.pub_date:
            return _("{} by {}").format(self.pub_date, self.user)
        return u'%s #%s' % (self._meta.verbose_name, self.pk)

    def on_create(self, ar):
        # Sets the :attr:`pub_date` and :attr:`pub_time` to now.
        if not settings.SITE.loading_from_dump:
            self.set_datetime('pub', timezone.now())
            self.language = ar.get_user().language
        super(Entry, self).on_create(ar)

    add_interest = AddInterestField()

    def get_detail_action(self, ar):
        user = ar.get_user()
        if user.user_type.has_required_roles([BlogsReader]) and \
            user == self.user:
            return super().get_detail_action(ar)
        return rt.models.blogs.PublicEntries.detail_action

    @dd.htmlbox()
    def preview(self, ar):
        if ar is None:
            return
        return self.render_from(self.publisher_page_template, ar)

    def get_item_preview(self, ar):
        if ar is None:
            return
        return self.render_from(self.publisher_item_template, ar)

    @dd.htmlbox()
    def item_preview(self, ar):
        return self.get_item_preview(ar)

    def as_story_item(self, ar):
        return self.get_item_preview(ar)

    def get_preview_context(self, ar):
        context = super().get_preview_context(ar)
        FileUsage = rt.models.albums.FileUsage
        qs = FileUsage.objects.filter(
            **gfk2lookup(FileUsage.owner, self), primary_image=True)
        if qs.count() == 1:
            primary_image = qs[0].file
            context.update(pi=primary_image)

        if ar.__class__ == BaseRequest:
            return context

        if ar.get_user() == self.user:
            button = ('<span style="float: right;">' +
                tostring(ar.row_action_button(self,
                    rt.models.blogs.MyEntries.detail_action, label='edit',
                    icon_name=None, CLASS='pi pi-pencil')) +
                '</span>')
            context.update(editable=True, edit_button=button)

        return context

    @classmethod
    def get_dashboard_items(cls, user):
        qs = cls.objects.filter(pub_date__isnull=False).order_by("-pub_date")
        return qs[:5]

    @classmethod
    def get_dashboard_objects(cls, ar):
        # qs = cls.objects.filter(pub_date__isnull=False).order_by('-pub_date')
        # return qs[:5]
        return cls.get_dashboard_items(ar.get_user())


    # @classmethod
    # def latest_entries(cls, ar, max_num=10, **context):
    #     context = ar.get_printable_context(**context)
    #     qs = cls.objects.filter(pub_date__isnull=False)
    #     qs = qs.order_by("-pub_date")
    #     s = ''
    #     render = dd.plugins.jinja.render_jinja
    #     for num, e in enumerate(qs):
    #         if num >= max_num:
    #             break
    #         context.update(obj=e)
    #         s += render(ar, 'blogs/entry.html', context)
    #     return s


# class Tagging(dd.Model):
#     """A **tag** is the fact that a given entry mentions a given topic.

#     """
#     class Meta:
#         app_label = 'blogs'
#         verbose_name = _("Tagging")
#         verbose_name_plural = _('Taggings')

#     allow_cascaded_delete = ['entry', 'topic']

#     topic = dd.ForeignKey(
#         'topics.Topic',
#         related_name='tags_by_topic')

#     entry = dd.ForeignKey(
#         'blogs.Entry',
#         related_name='tags_by_entry')


class EntryDetail(dd.DetailLayout):
    main = """
    title entry_type:12 id
    # summary
    pub_date pub_time user:10 language:10 owner add_interest"""

    if dd.is_installed('albums'):
        main += "\nalbums.UsagesByController"

    main += "\nbody:60 topics.InterestsByController:20 comments.CommentsByRFC:20 #TaggingsByEntry:20"

class ItemLayout(dd.DetailLayout):
    main = "layout"

    layout = "meta:30 body_short_preview:70"

    meta = """
    user
    pub_date
    """


class Entries(dd.Table):
    required_roles = set([BlogsReader])

    model = 'blogs.Entry'
    column_names = "id pub_date user entry_type title *"
    order_by = ["-id"]

    hide_top_toolbar = False

    display_mode = 'list'
    disabled_display_mode = None # Something to play with (TODO)

    insert_layout = """
    title
    entry_type
    """

    detail_layout = EntryDetail()
    item_layout = ItemLayout()

    @classmethod
    def collect_extra_actions(cls):
        yield dd.WrappedAction(
            rt.models.blogs.PublicEntries.detail_action,
            label=_("Preview"),
            icon_name=None)


class PublicEntries(Entries):
    required_roles = set()  # also for anonymous
    hide_top_toolbar = True
    detail_layout = """
    preview
    comments.CommentsByRFC
    """

    display_mode = constants.DISPLAY_MODE_STORY

    item_layout = "item_preview"

    @classmethod
    def collect_extra_actions(cls):
        return []


class MyEntries(My, Entries):
    required_roles = dd.login_required((BlogsReader, dd.SiteStaff))
    #~ master_key = 'user'
    column_names = "id pub_date entry_type title body *"
    # order_by = ["-modified"]

class AllEntries(Entries):
    required_roles = dd.login_required(dd.SiteStaff)

#~ class NotesByProject(Notes):
    #~ master_key = 'project'
    #~ column_names = "date subject user *"
    #~ order_by = "date"

#~ class NotesByController(Notes):
    #~ master_key = 'owner'
    #~ column_names = "date subject user *"
    #~ order_by = "date"


class EntriesByType(Entries):
    master_key = 'entry_type'
    column_names = "pub_date title user *"
    order_by = ["pub_date-"]
    #~ label = _("Notes by person")


class EntriesByController(Entries):
    master_key = 'owner'
    column_names = "pub_date title user *"
    order_by = ["-pub_date"]
    display_mode = "summary"

    @classmethod
    def get_table_summary(self, mi, ar):
        if ar is None:
            return ''
        sar = self.request_from(ar, master_instance=mi)

        def fmt(obj):
            return str(obj)

        elems = []
        for obj in sar:
            # if len(elems) > 0:
            #     elems.append(', ')

            lbl = fmt(obj)
            # if obj.state.button_text:
            #     lbl = "{0}{1}".format(lbl, obj.state.button_text)
            elems.append(ar.obj2html(obj, lbl))
        elems = join_elems(elems, sep=', ')
        toolbar = []
        ar2 = self.insert_action.request_from(sar)
        if ar2.get_permission():
            btn = ar2.ar2button()
            toolbar.append(btn)

        if len(toolbar):
            toolbar = join_elems(toolbar, sep=' ')
            elems.append(E.p(*toolbar))

        return ar.html_text(E.div(*elems))



class LatestEntries(PublicEntries):
    """Show the most recent blog entries."""
    label = _("Latest blog entries")
    column_names = "pub_date title user *"
    order_by = ["-pub_date"]
    filter = models.Q(pub_date__isnull=False)

    @classmethod
    def get_table_summary(cls, obj, ar, max_num=10, **context):

        context = ar.get_printable_context(**context)
        qs = rt.models.blogs.Entry.objects.filter(pub_date__isnull=False)
        qs = qs.order_by("-pub_date")
        render = dd.plugins.jinja.render_jinja
        elems = []
        for num, e in enumerate(qs):
            if num >= max_num:
                break
            context.update(obj=e)
            # s = render(ar, 'blogs/entry.html', context)
            elems.append(E.h2(e.title or str(e), " ", e.obj2href(
                ar, u"⏏", **{'style': "text-decoration:none"})))
            # s = ar.parse_memo(e.body_short_preview)
            s = e.body_short_preview
            tree = etree.parse(StringIO(s), html_parser)
            # elems.extend(tree.iter())
            # elems.append(tree.iter().next())
            elems.append(tree.getroot())
            elems.append(E.p(
                _("{} by {}").format(dd.fdf(e.pub_date), e.user)))
            # elems.append(E.p(
            #     _("{} by {}").format(dd.fdf(e.pub_date), e.user),
            #     " ", e.obj2href(ar, "(edit)")))

        return E.div(*elems)



# class Taggings(dd.Table):
#     model = 'blogs.Tagging'

# class AllTaggings(Taggings):
#     required_roles = dd.login_required(dd.SiteStaff)

# class TaggingsByEntry(Taggings):
#     master_key = 'entry'
#     column_names = 'topic *'

# class TaggingsByTopic(Taggings):
#     master_key = 'topic'
#     column_names = 'entry *'
