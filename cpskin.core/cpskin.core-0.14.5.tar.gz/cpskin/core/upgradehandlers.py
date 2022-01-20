# -*- coding: utf-8 -*-
from Acquisition import aq_get
from collective.dexteritytextindexer.behavior import IDexterityTextIndexer
from cpskin.core.behaviors.booking import IBooking
from cpskin.core.behaviors.directory import ICpskinDirectoryViewSettings
from cpskin.core.behaviors.eventview import ICpskinEventViewSettings
from cpskin.core.behaviors.indexview import ICpskinIndexViewSettings
from cpskin.core.behaviors.metadata import IAdditionalSearchableText
from cpskin.core.behaviors.organization import IOrganizationImages
from cpskin.core.faceted.interfaces import ICPSkinPossibleFacetedNavigable
from cpskin.core.interfaces import IFolderViewSelectedContent
from cpskin.core.setuphandlers import addAutoPlaySliderToRegistry
from cpskin.core.setuphandlers import addCityNameToRegistry
from cpskin.core.setuphandlers import addCollapseMinisiteMenuToRegistry
from cpskin.core.setuphandlers import addFooterSitemapToRegistry
from cpskin.core.setuphandlers import addContentClassesToRegistry
from cpskin.core.setuphandlers import addDescriptionOnThemesOptionToRegistry
from cpskin.core.setuphandlers import addIndexedTaxonomiesToRegistry
from cpskin.core.setuphandlers import addLoadPageMenuToRegistry
from cpskin.core.setuphandlers import addMediaViewletOptionsToRegistry
from cpskin.core.setuphandlers import addPortletsInRightActionsToRegistry
from cpskin.core.setuphandlers import addShowSloganToRegistry
from cpskin.core.setuphandlers import addSliderTimerToRegistry
from cpskin.core.setuphandlers import addSliderTypeToRegistry
from cpskin.core.setuphandlers import addSubMenuPersistenceToRegistry
from cpskin.core.setuphandlers import addTopMenuContentsToRegistry
from cpskin.core.setuphandlers import addTopMenuLeadImageToRegistry
from cpskin.core.setuphandlers import addPersonContactCoreFallbackToRegistry
from cpskin.core.setuphandlers import add_other_xhtml_valid_tags
from cpskin.core.setuphandlers import configCollectiveQucikupload
from cpskin.core.utils import add_behavior
from cpskin.core.utils import remove_behavior
from cpskin.locales import CPSkinMessageFactory as _
from eea.facetednavigation.subtypes.interfaces import IPossibleFacetedNavigable
from plone import api
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from plone.schemaeditor.interfaces import IEditableSchema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import noLongerProvides

import logging


logger = logging.getLogger("cpskin.core")


def remove_slider_type_to_registry(context):
    registry = getUtility(IRegistry)
    records = registry.records
    key = "cpskin.core.interfaces.ICPSkinSettings.slider_type"
    if key in records:
        logger.info(
            "Remove cpskin.core.interfaces.ICPSkinSettings.slider_type from registry"
        )  # noqa
        records.__delitem__(key)


def install_imiogdpr(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-imio.gdpr:default")


def migrate_hide_title_for_sliders(context):
    index_collections_brains = api.content.find(
        portal_type="Collection",
        object_provides=ICpskinIndexViewSettings.__identifier__,
    )
    for brain in index_collections_brains:
        obj = brain.getObject()
        display_type = getattr(obj, "display_type") or ""
        if "slider" in display_type:
            obj.hide_title = True


def split_show_day_and_month(context):
    index_collections_brains = api.content.find(
        portal_type="Collection",
        object_provides=ICpskinIndexViewSettings.__identifier__,
    )
    for brain in index_collections_brains:
        obj = brain.getObject()
        show_day_and_month = getattr(obj, "show_day_and_month")
        obj.show_lead_image = not (show_day_and_month)


def upgrade_js_registry(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "jsregistry")


def install_fancybox(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-collective.js.fancybox:default")


def upgrade_organization_gallery(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "cssregistry")
    context.runImportStepFromProfile("profile-cpskin.core:default", "jsregistry")
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")


def add_images_behavior(context):
    add_behavior("organization", IOrganizationImages.__identifier__)


def enable_directory_versioning(context):
    add_behavior("directory", IVersionable.__identifier__)
    add_behavior("organization", IVersionable.__identifier__)
    add_behavior("person", IVersionable.__identifier__)
    add_behavior("position", IVersionable.__identifier__)
    context.runImportStepFromProfile("profile-cpskin.core:default", "repositorytool")
    context.runImportStepFromProfile("profile-cpskin.core:default", "difftool")


def set_other_xhtml_valid_tags(context):
    add_other_xhtml_valid_tags()


def use_sc_social_like_instead_of_bookmarks(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-sc.social.like:default")
    from sc.social.like.interfaces import ISocialLikeSettings

    api.portal.set_registry_record(
        "plugins_enabled", ("Facebook",), interface=ISocialLikeSettings
    )
    api.portal.set_registry_record(
        "sc.social.like.interfaces.ISocialLikeSettings.fbbuttons", (u"Share",)
    )
    api.portal.set_registry_record(
        "sc.social.like.interfaces.ISocialLikeSettings.fbshowlikes", False
    )
    portal_properties = api.portal.get_tool("portal_properties")
    sc_social_bookmarks_properties = portal_properties.get(
        "sc_social_bookmarks_properties"
    )

    if sc_social_bookmarks_properties:
        enabled_portal_types = sc_social_bookmarks_properties.enabled_portal_types

        api.portal.set_registry_record(
            "enabled_portal_types", enabled_portal_types, interface=ISocialLikeSettings
        )
        bookmark_providers = sc_social_bookmarks_properties.bookmark_providers
        if "Google Bookmarks" in bookmark_providers:
            lst = list(bookmark_providers)
            index = lst.index("Google Bookmarks")
            lst[index] = "Google+"
            bookmark_providers = tuple(lst)
        api.portal.set_registry_record(
            "plugins_enabled", bookmark_providers, interface=ISocialLikeSettings
        )
        # clean up
        portal_properties.manage_delObjects(sc_social_bookmarks_properties.id)
        portal_setup.runAllImportStepsFromProfile(
            "profile-sc.social.bookmarks:uninstall"
        )


def upgrade_registry_for_themes_descriptions(context):
    addDescriptionOnThemesOptionToRegistry()


def upgrade_registry_for_media_viewlet(context):
    addMediaViewletOptionsToRegistry(upgrade=True)


def add_right_actions(context):
    addPortletsInRightActionsToRegistry()
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")
    context.runImportStepFromProfile("profile-cpskin.core:default", "jsregistry")


def upgrade_registry_for_slogan(context):
    addShowSloganToRegistry()


def upgrade_registry_for_minisite_menu(context):
    addCollapseMinisiteMenuToRegistry()


def upgrade_registry_for_show_footer_sitemap(context):
    addFooterSitemapToRegistry()


def upgrade_registry_for_content_classes(context):
    addContentClassesToRegistry()


def update_types(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "typeinfo")


def clean_portal_setup(context):
    """
    Force uninstall of packages that are not marked as installed but were
    imported in portal_setup : #17714
    """
    ps = api.portal.get_tool("portal_setup")
    qi = api.portal.get_tool("portal_quickinstaller")
    quick_installed = [p["id"] for p in qi.listInstalledProducts()]
    all_profiles = [
        p["id"] for p in context.listContextInfos() if p["type"] == "extension"
    ]
    cpskin_profiles = [
        p for p in all_profiles if p.startswith("profile-cpskin.diazotheme.")
    ]
    for profile_id in cpskin_profiles:
        if "uninstall" in profile_id:
            continue
        if ps.getLastVersionForProfile(profile_id) == "unknown":
            # profile is not installed
            logger.info("{0} is not installed - skipping".format(profile_id))
            continue
        package_id = profile_id.split("-")[1].split(":")[0]
        if package_id in quick_installed:
            # profile is installed, product is also installed in quickinstaller
            logger.info("{0} is well installed - skipping".format(profile_id))
            continue
        logger.warn("{0} is NOT installed correctly".format(profile_id))
        uninstall_profile_id = "profile-{0}:uninstall".format(package_id)
        if uninstall_profile_id in all_profiles:
            # install lesscss because uninstall profiles need it.
            if not qi.isProductInstalled("collective.lesscss"):
                context.runAllImportStepsFromProfile(
                    "profile-collective.lesscss:default"
                )
                qi.installProduct("collective.lesscss")
            context.runAllImportStepsFromProfile(uninstall_profile_id)
            ps.unsetLastVersionForProfile(profile_id)
            qi.uninstallProducts(products=[str(package_id)])
            logger.info("{0} uninstalled successfully !".format(package_id))
        else:
            logger.warn("No uninstall profile for {0}".format(package_id))

    psk = api.portal.get_tool("portal_skins")
    selected_skin = "Sunburst Theme"
    if psk.default_skin != selected_skin:
        psk.default_skin = selected_skin
        request = aq_get(context, "REQUEST", None)
        portal = api.portal.get()
        portal.changeSkin(selected_skin, request)
        logger.info("Restored default_skin : {0}".format(selected_skin))


def upgrade_viewlets(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")


def upgrade_registry_for_top_menu(context):
    addTopMenuContentsToRegistry()
    addTopMenuLeadImageToRegistry()


def upgrade_registry_for_contact_core_fallback(context):
    addPersonContactCoreFallbackToRegistry()


def migrate_a_la_une_sliders(context):
    brains = api.content.find(id="a-la-une", portal_type="Collection")
    for brain in brains:
        obj = brain.getObject()
        obj.display_type = u"slider-with-carousel"


def update_theme_variables(context):
    context.runAllImportStepsFromProfile("profile-cpskin.theme:default")
    key = "plone.app.theming.interfaces.IThemeSettings.parameterExpressions"
    params = {}
    params["globalnavsetting"] = "python: 'always'"
    params["isinminisitemode"] = "context/@@isInMinisiteMode"
    params["is_homepage"] = "context/@@is_homepage"
    params["environment"] = "context/@@environment"
    params["login_message"] = "context/@@get_login_message"
    api.portal.set_registry_record(key, params)


def empty_value_of_link_text(context):
    for brain in api.content.find(portal_type="Collection"):
        obj = brain.getObject()
        path = "/".join(obj.getPhysicalPath())
        logger.info("set link_text empty for {0}".format(path))
        setattr(obj, "link_text", "")


def upgrade_to_nineteen(context):
    context.runImportStepFromProfile("profile-cpskin.core:to19", "jsregistry")
    pc = api.portal.get_tool("portal_catalog")
    for brain in pc.unrestrictedSearchResults(
        object_provides=IPossibleFacetedNavigable.__identifier__
    ):
        obj = brain.getObject()
        if obj:
            alsoProvides(obj, ICPSkinPossibleFacetedNavigable)


def clean_old_keyword_homepage(context):
    behavior_name = "cpskin.core.behaviors.metadata.IUseKeywordHomepage"
    types = [
        "Folder",
        "Collection",
        "Document",
        "Event",
        "News Item",
        "organization",
        "person",
    ]
    for type_name in types:
        remove_behavior(type_name, behavior_name)


def move_cpskin_actions(context):
    context.runImportStepFromProfile("profile-cpskin.core:to17", "actions")
    context.runImportStepFromProfile("profile-cpskin.core:default", "actions")


def add_navigation_toggle_action(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "actions")


def add_directory_view_behavior(context):
    add_behavior("directory", ICpskinDirectoryViewSettings.__identifier__)


def add_index_view_behavior(context):
    registry = getUtility(IRegistry)
    del registry.records["cpskin.core.interfaces.ICPSkinSettings.homepage_keywords"]
    add_behavior("Collection", ICpskinIndexViewSettings.__identifier__)


def add_banner_view_behavior(context):
    add_behavior("Event", ICpskinEventViewSettings.__identifier__)


def upgrade_homepage_keywords(context):
    # add_homepage_keywords()
    pass


def upgrade_minisite_menu(context):
    # add new viewlet cpskin.minisite
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")
    context.runImportStepFromProfile("profile-cpskin.menu:default", "jsregistry")
    context.runImportStepFromProfile("profile-cpskin.minisite:default", "actions")


def upgrade_city_name(context):
    addCityNameToRegistry()


def upgrade_slider_type(context):
    addSliderTypeToRegistry()


def upgrade_indexed_taxonomies(context):
    addIndexedTaxonomiesToRegistry()


def upgrade_search_position(context):
    registry = getUtility(IRegistry)
    records = registry.records
    if "cpskin.core.interfaces.ICPSkinSettings.search_position" in records:
        return

    logger.info(
        "Adding cpskin.core.interfaces.ICPSkinSettings.search_position to registry"
    )  # noqa
    record = Record(
        field.TextLine(
            title=_(u"Search position"),
            description=_(u"Search box position in eligible themes."),
            required=True,
            default=u"default_position",
        ),
        value=u"default_position",
    )
    records["cpskin.core.interfaces.ICPSkinSettings.search_position"] = record


def upgrade_footer_viewlet(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")


def upgrade_to_eleven(context):
    addSubMenuPersistenceToRegistry()


def upgrade_to_eight(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "rolemap")


def upgrade_to_seven(context):
    addAutoPlaySliderToRegistry()
    addSliderTimerToRegistry()


def upgrade_to_six(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "rolemap")
    context.runImportStepFromProfile("profile-cpskin.core:default", "sharing")
    portal = api.portal.get()
    portal.manage_permission(
        "CPSkin: Edit keywords",
        roles=["Portlets Manager", "Manager", "Site Administrator"],
        acquire=True,
    )
    site_properties = api.portal.get_tool("portal_properties").site_properties
    site_properties.allowRolesToAddKeywords = (
        "Manager",
        "Site Administrator",
        "Portlets Manager",
    )


def upgrade_to_five(context):
    interfaces = [
        "cpskin.core.viewlets.interfaces.IViewletMenuToolsBox",
        "cpskin.core.viewlets.interfaces.IViewletMenuToolsFaceted",
    ]
    catalog = api.portal.get_tool("portal_catalog")
    for interface in interfaces:
        brains = catalog({"object_provides": interface})
        for brain in brains:
            obj = brain.getObject()
            provided = directlyProvidedBy(obj)
            cleanedProvided = [i for i in provided if i.__identifier__ != interface]
            directlyProvides(obj, cleanedProvided)  # noqa
            obj.reindexObject()

    portal_javascripts = api.portal.get_tool("portal_javascripts")
    portal_javascripts.unregisterResource("++resource++cpskin.core.menutools.js")


def upgrade_to_four(context):
    addLoadPageMenuToRegistry()


def upgrade_to_three(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "actions")
    context.runImportStepFromProfile("profile-cpskin.core:default", "rolemap")
    context.runImportStepFromProfile("profile-cpskin.core:default", "sharing")
    portal = api.portal.get()
    portal.manage_permission(
        "Portlets: Manage portlets",
        roles=["Editor", "Portlets Manager", "Manager", "Site Administrator"],
        acquire=True,
    )


def upgrade_to_two(context):
    context.runAllImportStepsFromProfile("profile-cpskin.policy:default")
    portal_catalog = api.portal.get_tool("portal_catalog")
    portal_atct = api.portal.get_tool("portal_atct")
    attrs = ("IAmTags", "HiddenTags", "ISearchTags")
    for attr in attrs:
        if attr in portal_catalog.indexes():
            portal_catalog.delIndex(attr)
        if attr in portal_atct.topic_indexes:
            portal_atct.removeIndex(attr)
    for brain in portal_catalog.searchResults():  # noqa
        obj = brain.getObject()
        for attr in attrs:
            if hasattr(obj, attr):
                try:
                    delattr(obj, attr)
                except AttributeError:
                    logger.info("No {0} on: {1}".format(attr, obj))


def upgrade_add_booking_behavior(context):
    portal_types = api.portal.get_tool(name="portal_types")
    event_type = portal_types.get("Event")
    fields = event_type.lookupSchema().names()

    if "tarifs" not in fields and "reservation" not in fields:
        # This upgrade step is specific to Liege, where those fields have been
        # added TTW.
        return

    add_behavior("Event", IBooking.__identifier__)
    for brain in api.content.find(portal_type="Event"):
        obj = brain.getObject()
        if getattr(obj, "tarifs") is not None:
            obj.booking_price = getattr(obj, "tarifs")
        if getattr(obj, "reservation") is not None:
            has_booking = getattr(obj, "reservation")
            if has_booking:
                obj.booking_type = "mandatory"
            else:
                obj.booking_type = "no_booking"
    schema = IEditableSchema(event_type.lookupSchema())
    schema.removeField("tarifs")
    schema.removeField("reservation")


def upgrade_add_specific_typesUseViewActionInListings(context):
    site_properties = api.portal.get_tool("portal_properties").site_properties
    site_properties.typesUseViewActionInListings = ("File", "Image")


def upgrade_add_default_page_types_document(context):
    site_properties = api.portal.get_tool("portal_properties").site_properties
    site_properties.default_page_types = ("Topic", "FormFolder", "Document")


def upgrade_limit_plone_site_portal_type(context):
    portal_types = api.portal.get_tool("portal_types")
    types = ["Plone Site", "LRF"]
    for t in types:
        plone_type = portal_types.get(t)
        if plone_type:
            plone_type.filter_content_types = True
            plone_type.allowed_content_types = ("Document", "Folder", "Image")


def upgrade_footer_minisite(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "viewlets")
    brains = api.content.find(id="footer-mini-site")
    for b in brains:
        obj = b.getObject()
        noLongerProvides(obj, IFolderViewSelectedContent)
        obj.reindexObject()
        logger.info("Removed %s from minisite index view" % obj.absolute_url())


def upgrade_css_js_registry(context):
    context.runImportStepFromProfile("profile-cpskin.core:default", "cssregistry")
    context.runImportStepFromProfile("profile-cpskin.core:default", "jsregistry")


def set_quickupload_properties(context):
    configCollectiveQucikupload()


def add_searchable_on_organization(context):
    add_behavior("organization", IAdditionalSearchableText.__identifier__)
    add_behavior("organization", IDexterityTextIndexer.__identifier__)


def to_65_use_slick(context):
    registry = getUtility(IRegistry)
    records = registry.records

    if "cpskin.core.interfaces.ICPSkinSettings.use_slick" in records:
        return

    logger.info("Adding cpskin.core.interfaces.ICPSkinSettings.use_slick to registry")
    record = Record(
        field.Bool(
            title=_(u"Use slick for slider"),
            description=_(u"Do you want to use slick instead of flexslider ?"),
            required=False,
            default=False,
        ),
        value=False,
    )
    records["cpskin.core.interfaces.ICPSkinSettings.use_slick"] = record


def upgrade_limit_plone_site_portal_type_2(context):
    portal_types = api.portal.get_tool("portal_types")
    types = ["Plone Site", "LRF"]
    for t in types:
        plone_type = portal_types.get(t)
        if plone_type:
            plone_type.filter_content_types = True
            plone_type.allowed_content_types = ("Document", "Folder", "Image", "Link")


def upgrade_enable_accessibility_link_in_footer(context):
    registry = getUtility(IRegistry)
    records = registry.records
    if "cpskin.core.interfaces.ICPSkinSettings.enable_accessibility_link_in_footer" in records:  # noqa
        return

    logger.info(
        "Adding cpskin.core.interfaces.ICPSkinSettings.enable_accessibility_link_in_footer to registry"  # noqa
    )  # noqa
    record = Record(
        field.Bool(
            title=_(u"Enable accessibility link in footer"),
            description=_(u"Enable a link to the accessibility text in footer."),
            required=False,
            default=True,
        ),
        value=True,
    )
    records["cpskin.core.interfaces.ICPSkinSettings.enable_accessibility_link_in_footer"] = record  # noqa


def install_privacy(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-iaweb.privacy:default")
    portal_setup.runAllImportStepsFromProfile("profile-collective.cookiecuttr:uninstall")
