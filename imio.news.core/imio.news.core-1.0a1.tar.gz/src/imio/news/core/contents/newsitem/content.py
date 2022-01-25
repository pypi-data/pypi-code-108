# -*- coding: utf-8 -*-

from imio.smartweb.common.adapters import BaseCroppingProvider
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.content.namechooser import NormalizingNameChooser
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.container.interfaces import INameChooser
from zope.interface import implementer


class NewsItemCroppingProvider(BaseCroppingProvider):
    def get_scales(self, fieldname, request=None):
        if fieldname == "image":
            # scales used for lead image field
            return ["vignette", "slide", "affiche"]
        return []


class INewsItem(model.Schema):
    """Marker interface and Dexterity Python Schema for NewsItem"""

    site_url = schema.URI(
        title=_(u"Website"),
        description=_(u"NewsItem website url"),
        required=False,
    )

    video_url = schema.URI(
        title=_(u"Video url"),
        description=_(u"Video url from youtube, vimeo"),
        required=False,
    )

    facebook = schema.URI(
        title=_(u"Facebook"),
        description=_(u"Facebook url for this news"),
        required=False,
    )

    twitter = schema.URI(
        title=_(u"Twitter"),
        description=_(u"Twitter url for this news"),
        required=False,
    )

    instagram = schema.URI(
        title=_(u"Instagram"),
        description=_(u"Instagram url for this news"),
        required=False,
    )

    model.fieldset(
        "categorization", fields=["selected_news_folders", "category", "local_category"]
    )
    directives.widget(selected_news_folders=SelectFieldWidget)
    selected_news_folders = schema.List(
        title=_(u"Selected news folders"),
        description=_(
            u"Select news folders where this news item will be displayed. Current news folder is always selected."
        ),
        value_type=schema.Choice(vocabulary="imio.news.vocabulary.NewsFoldersUIDs"),
        default=[],
        required=False,
    )

    category = schema.Choice(
        title=_(u"Category"),
        description=_(
            u"Important! These categories are used to supplement the information provided by the topics"
        ),
        source="imio.news.vocabulary.NewsCategories",
        required=False,
    )

    local_category = schema.Choice(
        title=_(u"Specific category"),
        description=_(
            u"Important! These categories allow you to use criteria that are specific to your organization"
        ),
        source="imio.news.vocabulary.NewsLocalCategories",
        required=False,
    )

    read_permission(selected_news_folders="imio.news.core.AddEntity")
    write_permission(selected_news_folders="imio.news.core.AddEntity")


@implementer(INewsItem)
class NewsItem(Container):
    """NewsItem class"""


@implementer(INameChooser)
class NewsItemNameChooser(NormalizingNameChooser):
    def chooseName(self, name, obj):
        if INewsItem.providedBy(obj):
            return obj.UID()
        return super(NewsItemNameChooser, self).chooseName(name, obj)
