# -*- coding: utf-8 -*-

from collective.documentviewer.settings import GlobalSettings
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.iconifiedcategory.interfaces import IIconifiedPreview
from collective.iconifiedcategory.interfaces import IIconifiedCategorySettings
from collective.iconifiedcategory.browser.tabview import AuthorColumn as IconifiedAuthorColumn
from collective.iconifiedcategory.browser.tabview import CategoryColumn as IconifiedCategoryColumn
from collective.iconifiedcategory.browser.tabview import CreationDateColumn as IconifiedCreationDateColumn
from collective.iconifiedcategory.browser.tabview import FilesizeColumn as IconifiedFilesizeColumn
from collective.iconifiedcategory.browser.tabview import LastModificationColumn as IconifiedLastModificationColumn
from imio.annex import _
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import ActionsColumn as DashboardActionsColumn
from collective.eeafaceted.z3ctable.columns import PrettyLinkColumn as DashboardPrettyLinkColumn
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate


class PrettyLinkColumn(DashboardPrettyLinkColumn):
    header = _(u'Title')
    weight = 20

    def getPrettyLink(self, obj):
        """Display the description just under the pretty link."""
        pl = super(PrettyLinkColumn, self).getPrettyLink(obj)
        # if preview is enabled, display a specific icon if element is converted
        preview = ''
        portal = api.portal.get()
        gsettings = GlobalSettings(portal)
        if gsettings.auto_convert and IIconifiedPreview(obj).converted:
            preview = self._preview_html(obj)

        # simple blank space
        blank = u'<p class="discreet"></p>'

        # display description if any
        description = safe_unicode(obj.Description() or u'').replace('\n', '<br/>')
        if description:
            description = u'<p class="discreet">{0}</p>'.format(description)

        # display filename if any
        filename = obj.file.filename
        field_name = translate(
            'File',
            domain='imio.annex',
            context=obj.REQUEST)
        filename = u'<div class="discreet"><label class="horizontal">{0}</label>' \
            '<div class="type-text-widget">{1}</div></div>'.format(
                field_name, filename)

        # display scan_id if any
        scan_id = getattr(obj, "scan_id", '') or ''
        if scan_id:
            field_name = translate(
                'scan_id',
                domain='collective.dms.scanbehavior',
                context=obj.REQUEST)
            scan_id = u'<div class="discreet"><label class="horizontal">{0}</label>' \
                '<div class="type-textarea-widget">{1}</div></div>'.format(
                    field_name, scan_id)
        return pl + preview + blank + description + filename + scan_id

    def _preview_html(self, obj):
        """ """
        portal = api.portal.get()
        return u"""<a href="{0}"
           title="{1}"
           target="_blank">
          <img src="{2}" />
        </a>""".format(obj.absolute_url() + '/documentviewer#document/p1',
                       translate('Preview',
                                 domain='collective.iconifiedcategory',
                                 context=obj.REQUEST),
                       portal.absolute_url() + '/file_icon.png')


class AuthorColumn(MemberIdColumn):
    """ """
    weight = IconifiedAuthorColumn.weight
    header = IconifiedAuthorColumn.header


class CategoryColumn(IconifiedCategoryColumn, BaseColumn):
    """ """


class CreationDateColumn(IconifiedCreationDateColumn, DateColumn):
    """ """


class LastModificationColumn(IconifiedLastModificationColumn, DateColumn):
    """ """


class FilesizeColumn(IconifiedFilesizeColumn, BaseColumn):
    """ """


class ActionsColumn(DashboardActionsColumn):
    header = _(u'Actions')
    weight = 100
    params = {'showHistory': True, 'showActions': True, 'showArrows': True}

    def _showArrows(self):
        sort_categorized_tab = api.portal.get_registry_record(
            'sort_categorized_tab',
            interface=IIconifiedCategorySettings,
        )
        return not(bool(sort_categorized_tab))

    def renderCell(self, item):
        """ """
        self.params['showArrows'] = self._showArrows()
        return super(ActionsColumn, self).renderCell(item)
