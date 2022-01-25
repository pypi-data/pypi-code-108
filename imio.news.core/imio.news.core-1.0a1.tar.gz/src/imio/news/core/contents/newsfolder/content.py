# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import implementer


class INewsFolder(model.Schema):
    """Marker interface and Dexterity Python Schema for NewsFolder"""

    populating_newsfolders = RelationList(
        title=_(u"Populating news folders"),
        description=_(
            u"News folders that automatically populates this news folder with their news."
        ),
        value_type=RelationChoice(
            title=u"Items selection",
            source=CatalogSource(),
        ),
        default=[],
        required=False,
    )
    directives.widget(
        "populating_newsfolders",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["imio.news.NewsFolder"],
            "favorites": [],
        },
    )


@implementer(INewsFolder)
class NewsFolder(Container):
    """NewsFolder class"""
