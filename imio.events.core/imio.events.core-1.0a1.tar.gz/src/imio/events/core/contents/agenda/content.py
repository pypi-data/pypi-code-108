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


class IAgenda(model.Schema):
    """Marker interface and Dexterity Python Schema for Agenda"""

    populating_agendas = RelationList(
        title=_(u"Populating agendas"),
        description=_(
            u"Agendas that automatically populates this agenda with their events."
        ),
        value_type=RelationChoice(
            title=u"Items selection",
            source=CatalogSource(),
        ),
        default=[],
        required=False,
    )
    directives.widget(
        "populating_agendas",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["imio.events.Agenda"],
            "favorites": [],
        },
    )


@implementer(IAgenda)
class Agenda(Container):
    """Agenda class"""
