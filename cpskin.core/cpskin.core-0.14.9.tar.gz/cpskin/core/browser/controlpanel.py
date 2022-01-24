# -*- coding: utf-8 -*-
from cpskin.core.interfaces import ICPSkinSettings
from cpskin.core.interfaces import IElectedContentForTopMenu
from cpskin.core.utils import is_plone_app_multilingual_installed
from cpskin.locales import CPSkinMessageFactory as _
from plone import api
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.multilingual.interfaces import ITranslationManager
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides
from zope.schema.interfaces import IVocabularyFactory


class CPSkinControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ICPSkinSettings)

    def __init__(self, context):
        super(CPSkinControlPanelAdapter, self).__init__(context)
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ICPSkinSettings, False)

    def getLoadPageMenu(self):
        return self.settings.load_page_menu

    def setLoadPageMenu(self, value):
        self.settings.load_page_menu = value

    load_page_menu = property(getLoadPageMenu, setLoadPageMenu)

    def getSubMenuPersistence(self):
        return self.settings.sub_menu_persistence

    def setSubMenuPersistence(self, value):
        self.settings.sub_menu_persistence = value

    sub_menu_persistence = property(getSubMenuPersistence, setSubMenuPersistence)

    def getAutoPlaySlider(self):
        return self.settings.auto_play_slider

    def setAutoPlaySlider(self, value):
        self.settings.auto_play_slider = value

    auto_play_slider = property(getAutoPlaySlider, setAutoPlaySlider)

    def getSliderTimer(self):
        return self.settings.slider_timer

    def setSliderTimer(self, value):
        self.settings.slider_timer = value

    slider_timer = property(getSliderTimer, setSliderTimer)

    def getCityName(self):
        return self.settings.city_name

    def setCityName(self, value):
        self.settings.city_name = value

    city_name = property(getCityName, setCityName)

    def getContentsInActionMenu(self):
        return self.settings.contents_in_action_menu

    def setContentsInActionMenu(self, value):
        self.settings.contents_in_action_menu = value
        portal = root = api.portal.get()
        if "fr" in root.objectIds():
            fr = getattr(root, "fr")
            root = api.portal.get_navigation_root(fr)
        catalog = api.portal.get_tool("portal_catalog")
        name = "cpskin.core.vocabularies.action_menu_eligible"
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(portal)
        all_values = vocabulary.by_value.keys()
        for content_id in all_values:
            content = getattr(root, content_id, None)
            if not content:
                continue
            translations = {"fr": content}
            request = getattr(self.context, "REQUEST", None)
            if is_plone_app_multilingual_installed(request):
                translations = ITranslationManager(content).get_translations()
            if content_id in value:
                for t in translations.values():
                    if IElectedContentForTopMenu.providedBy(t):
                        continue
                    alsoProvides(t, IElectedContentForTopMenu)
                    catalog.reindexObject(t)
            else:
                for t in translations.values():
                    if not IElectedContentForTopMenu.providedBy(t):
                        continue
                    noLongerProvides(t, IElectedContentForTopMenu)
                    catalog.reindexObject(t)

    contents_in_action_menu = property(
        getContentsInActionMenu, setContentsInActionMenu,
    )

    def getShowLeadimageInActionMenu(self):
        return self.settings.show_leadimage_in_action_menu

    def setShowLeadimageInActionMenu(self, value):
        self.settings.show_leadimage_in_action_menu = value

    show_leadimage_in_action_menu = property(
        getShowLeadimageInActionMenu, setShowLeadimageInActionMenu,
    )

    def getPersonContactCoreFallback(self):
        return self.settings.person_contact_core_fallback

    def setPersonContactCoreFallback(self, value):
        self.settings.person_contact_core_fallback = value

    person_contact_core_fallback = property(
        getPersonContactCoreFallback, setPersonContactCoreFallback,
    )

    def getShowSlogan(self):
        return self.settings.show_slogan

    def setShowSlogan(self, value):
        self.settings.show_slogan = value

    show_slogan = property(getShowSlogan, setShowSlogan,)

    def getshowPortletsInRightActionsPanel(self):
        return self.settings.show_portlets_in_right_actions_panel

    def setshowPortletsInRightActionsPanel(self, value):
        self.settings.show_portlets_in_right_actions_panel = value

    show_portlets_in_right_actions_panel = property(
        getshowPortletsInRightActionsPanel, setshowPortletsInRightActionsPanel,
    )

    def getMediaViewletVisibleAlbums(self):
        return self.settings.media_viewlet_visible_albums

    def setMediaViewletVisibleAlbums(self, value):
        self.settings.media_viewlet_visible_albums = value

    media_viewlet_visible_albums = property(
        getMediaViewletVisibleAlbums, setMediaViewletVisibleAlbums,
    )

    def getMediaViewletVisibleVideos(self):
        return self.settings.media_viewlet_visible_videos

    def setMediaViewletVisibleVideos(self, value):
        self.settings.media_viewlet_visible_videos = value

    media_viewlet_visible_videos = property(
        getMediaViewletVisibleVideos, setMediaViewletVisibleVideos,
    )

    def getShowDescriptionOnThemes(self):
        return self.settings.show_description_on_themes

    def setShowDescriptionOnThemes(self, value):
        self.settings.show_description_on_themes = value

    show_description_on_themes = property(
        getShowDescriptionOnThemes, setShowDescriptionOnThemes,
    )

    def getSearchPosition(self):
        return self.settings.search_position

    def setSearchPosition(self, value):
        self.settings.search_position = value

    search_position = property(getSearchPosition, setSearchPosition)

    def getCollapseMinisiteMenu(self):
        return self.settings.collapse_minisite_menu

    def setCollapseMinisiteMenu(self, value):
        self.settings.collapse_minisite_menu = value

    collapse_minisite_menu = property(getCollapseMinisiteMenu, setCollapseMinisiteMenu,)

    def getShowFooterSitemap(self):
        return self.settings.show_footer_sitemap

    def setShowFooterSitemap(self, value):
        self.settings.show_footer_sitemap = value

    show_footer_sitemap = property(getShowFooterSitemap, setShowFooterSitemap,)

    def getHeaderClass(self):
        return self.settings.header_class

    def setHeaderClass(self, value):
        self.settings.header_class = value

    header_class = property(getHeaderClass, setHeaderClass)

    def getNavigationClass(self):
        return self.settings.navigation_class

    def setNavigationClass(self, value):
        self.settings.navigation_class = value

    navigation_class = property(getNavigationClass, setNavigationClass)

    def getColumnsClass(self):
        return self.settings.columns_class

    def setColumnsClass(self, value):
        self.settings.columns_class = value

    columns_class = property(getColumnsClass, setColumnsClass)

    def getFooterClass(self):
        return self.settings.footer_class

    def setFooterClass(self, value):
        self.settings.footer_class = value

    footer_class = property(getFooterClass, setFooterClass)

    def getIndexedTaxonomies(self):
        return self.settings.indexed_taxonomies

    def setIndexedTaxonomies(self, value):
        self.settings.indexed_taxonomies = value

    indexed_taxonomies = property(getIndexedTaxonomies, setIndexedTaxonomies)

    def getEnable_accessibility_link_in_footer(self):
        return self.settings.enable_accessibility_link_in_footer

    def setEnable_accessibility_link_in_footer(self, value):
        self.settings.enable_accessibility_link_in_footer = value

    enable_accessibility_link_in_footer = property(
        getEnable_accessibility_link_in_footer, setEnable_accessibility_link_in_footer
    )

    @property
    def use_slick(self):
        return self.settings.use_slick

    @use_slick.setter
    def use_slick(self, value):
        self.settings.use_slick = value


class CPSkinControlPanel(ControlPanelForm):

    label = _("CPSkin settings")
    description = _("Lets you change the settings of CPSkin")
    form_fields = form.FormFields(ICPSkinSettings)
