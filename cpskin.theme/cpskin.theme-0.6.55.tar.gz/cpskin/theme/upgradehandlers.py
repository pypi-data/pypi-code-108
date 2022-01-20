# -*- coding: utf-8 -*-
from cpskin.theme.setuphandlers import addCustomLessFiles
from cpskin.theme.setuphandlers import CUSTOM_FOLDER_NAME
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api
from plone.app.theming.interfaces import IThemeSettings
from plone.resource.interfaces import IResourceDirectory
from six import StringIO
from zope.component import getUtility

import logging


logger = logging.getLogger('cpskin.theme')


def allow_diazo_remote_access(context):
    portal_setup = api.portal.get_tool('portal_setup')
    api.portal.set_registry_record(
        'plone.app.theming.interfaces.IThemeSettings.readNetwork',
        True
    )


def set_faceted_list_items(context):
    portal_catalog = api.portal.get_tool('portal_catalog')
    brains = portal_catalog.unrestrictedSearchResults(
                    object_provides=IFacetedNavigable.__identifier__)
    for brain in brains:
        obj = brain.getObject()
        if IFacetedLayout(obj).layout == 'faceted-preview-items':
            IFacetedLayout(obj).update_layout('faceted-list-items')
            logger.info('{0} faceted layout update'.format(
                '/'.join(obj.getPhysicalPath())))


def add_theme_parameter_expression(key, value):
    params = api.portal.get_registry_record(
        'parameterExpressions',
        interface=IThemeSettings
    )
    if key not in params.keys():
        params[key] = value
        api.portal.set_registry_record(
            'parameterExpressions',
            params,
            interface=IThemeSettings
        )


def add_ms_horizontal_navigation_any_mode_variable(context):
    add_theme_parameter_expression(
        'ms_horizontal_navigation_any_mode',
        'context/@@horizontalNavActivated'
    )


def add_search_position_variables(context):
    add_theme_parameter_expression(
        'is_search_in_navigation',
        'context/@@is_search_in_navigation'
    )
    add_theme_parameter_expression(
        'is_search_in_actions',
        'context/@@is_search_in_actions'
    )


def clean_portal_skins(context):
    """
    Clean up all (unused) cpskin skins
    """
    psk = api.portal.get_tool('portal_skins')
    cpskin_skins = [
        'classic theme',
        'dream theme',
        'dreamRightPortlet theme',
        'dreamRightPortletBasic theme',
        'dreambasic theme',
        'modern theme',
        'retro theme',
        'slab theme',
        'smart theme',
        'trendy theme',
        'trendybasic theme',
    ]
    installed_skins = psk.getSkinSelections()
    for skin in cpskin_skins:
        if skin not in installed_skins:
            continue
        psk.manage_skinLayers(chosen=[skin], del_skin=1)
        logger.info('Deleted unused skin in portal_skins : {0}'.format(skin))

    cpskin_skins_folders = [
        'classic_images',
        'dream_images',
        'dreamRightPortlet_images',
        'dreamRightPortletBasic_images',
        'dreambasic_images',
        'modern_images',
        'retro_images',
        'slab_images',
        'smart_images',
        'trendy_images',
        'trendybasic_images',
    ]
    for folder in cpskin_skins_folders:
        if folder not in psk.objectIds():
            continue
        psk._delObject(folder)
        logger.info('Deleted unused folder in portal_skins : {0}'.format(folder))


def upgrade_to_less(context):
    context.runAllImportStepsFromProfile('profile-collective.lesscss:default')
    context.runImportStepFromProfile(
        'profile-cpskin.theme:default',
        'plone.app.registry'
    )
    added = addCustomLessFiles()
    if added:
        migrate_existing_custom_to_less()
        context.runImportStepFromProfile(
            'profile-cpskin.theme:default',
            'lessregistry'
        )
    logger.info('LESS files installed and configurations done !')


def migrate_existing_custom_to_less():
    portal_resources = getUtility(IResourceDirectory, name='persistent')
    portal_skins = api.portal.get_tool('portal_skins')
    custom = getattr(portal_skins, 'custom', None)
    if not custom:
        return
    if not 'ploneCustom.css' in custom.objectIds():
        # getattr() doesn't work here : FSDTMLMethod is always returned for
        # ploneCustom.css even if it doesn't exist.
        return
    ploneCustom = getattr(custom, 'ploneCustom.css', None)
    title = ploneCustom.title
    if hasattr(ploneCustom, 'data') and getattr(ploneCustom, 'update_data', False):
        # File
        customCSS = ploneCustom.data
        ploneCustom.update_data('/*\nMigrated to LESS.\n*/')
    elif hasattr(ploneCustom, 'read'):
        # DTML method
        customCSS = ploneCustom.read()
        ploneCustom.manage_edit(
            data='/*\nMigrated to LESS.\n*/',
            title=title
        )
    folder = portal_resources[CUSTOM_FOLDER_NAME]
    folder.writeFile(
        'styles.less',
        StringIO(customCSS),
    )
    logger.info('ploneCustom.css migrated to styles.less in portal_resources')
