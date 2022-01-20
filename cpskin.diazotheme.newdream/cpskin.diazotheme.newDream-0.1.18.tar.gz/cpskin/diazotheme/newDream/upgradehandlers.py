# -*- coding: utf-8 -*-

from cpskin.locales import CPSkinMessageFactory as _
from cpskin.theme.upgradehandlers import add_theme_parameter_expression
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import logging

logger = logging.getLogger("cpskin.diazotheme.newDream")


def add_breadcrumbs_below_title_option(context):
    registry = getUtility(IRegistry)
    records = registry.records
    logger.info(
        "Adding cpskin.diazotheme.newDream.interfaces.INewDreamSettings.breadcrumbs_below_title to registry"
    )  # noqa
    record = Record(
        field.Bool(
            title=_(u"Breadcrumbs below title"),
            description=_(u"Show breadcrumbs below page title?"),
            required=False,
            default=False,
        ),
        value=False,
    )
    records[
        "cpskin.diazotheme.newDream.interfaces.INewDreamSettings.breadcrumbs_below_title"
    ] = record  # noqa

    add_theme_parameter_expression(
        'is_breadcrumbs_below_title',
        'context/@@is_breadcrumbs_below_title'
    )


def add_missing_parameters(context):
    add_theme_parameter_expression(
        'is_folder_view',
        'context/@@is_folder_view'
    )
    add_theme_parameter_expression(
        'is_in_portal_mode',
        'context/@@isInPortalMode'
    )
