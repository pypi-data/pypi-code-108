# -*- coding: utf-8 -*-
from collective.anysurfer.interfaces import ILayerSpecific as IAnysurferLayer
from cpskin.locales import CPSkinMessageFactory as _
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.event.interfaces import IBrowserLayer
from sc.social.like.interfaces import ISocialLikeLayer
from zope import schema
from zope.interface import Interface


class ICPSkinCoreLayer(ISocialLikeLayer, IPloneAppContenttypesLayer, IAnysurferLayer, IBrowserLayer):
    """
    Marker interface that defines a ZTK browser layer.
    """


class ICPSkinCoreWithMembersLayer(Interface):
    """
    Marker interface that defines a ZTK browser layer.
    """


class IBannerActivated(Interface):
    """
    Marker interface to enable / disable banner viewlet
    """


class ILocalBannerActivated(Interface):
    """
    Marker interface to enable / disable banner viewlet
    """


class IMediaActivated(Interface):
    """
    Marker interface to enable / disable (multi)media viewlet
    """


class IFolderViewSelectedContent(Interface):
    """
    Marker interface to add / remove content to / from folder view
    """


class IFolderViewWithBigImages(Interface):
    """
    Marker interface to use big images on folder view
    """


class IElectedContentForTopMenu(Interface):
    """
    Marker interface to select content for action top menu
    """


class ICPSkinSettings(Interface):
    """
    Settings for CPSkin
    """
    load_page_menu = schema.Bool(
        title=_(u'Load page menu'),
        description=_(u'Is level 1 menu load page at click?'),
        required=False,
        default=False
    )

    sub_menu_persistence = schema.Bool(
        title=_(u'Sub menu persistence'),
        description=_(u'Is level 2 menu persist?'),
        required=False,
        default=False
    )

    auto_play_slider = schema.Bool(
        title=_(u'Auto play slider'),
        description=_(u'Is the front page slider automatically play?'),
        required=False,
        default=False
    )

    slider_timer = schema.Int(
        title=_(u'Slider timer'),
        description=_(u'Number of milliseconds between each transition.'),
        required=False,
        default=5000
    )

    city_name = schema.TextLine(
        title=_(u'City name'),
        description=_(u'Name of city is used in some templates.'),
        required=True,
        default=u'City name'
    )

    contents_in_action_menu = schema.Tuple(
        title=_(u'Content to show in special action menu (top)'),
        description=_(u'Please select which contents should be taken to this menu.'),  # noqa
        required=False,
        value_type=schema.Choice(
            vocabulary=u'cpskin.core.vocabularies.action_menu_eligible'
        )
    )

    show_leadimage_in_action_menu = schema.Bool(
        title=_(u'Show leadimage in action menu'),
        description=_(u'Show leadimage (if any) in the top action menu with content selected in the field before.'),  # noqa
        required=False,
        default=False
    )

    person_contact_core_fallback = schema.Bool(
        title=_(u'Contact properties fallback?'),
        description=_(u'Do you want than contact properties fallback? Sample :If no tel on a person, so we get phone thanks to person\'f function.'),  # noqa
        required=False,
        default=False
    )

    show_slogan = schema.Bool(
        title=_(u'Show slogan with banner'),
        description=_(u'Show banner title and description as homepage slogan.'),  # noqa
        required=False,
        default=False
    )

    show_portlets_in_right_actions_panel = schema.Bool(
        title=_(u'Show (right) portlets in right actions panel'),
        description=_(u'Show (right) portlets (if any) in right actions panel after related contents.'),  # noqa
        required=False,
        default=False
    )

    media_viewlet_visible_albums = schema.Int(
        title=_(u'Viewlet media : Visible albums'),
        description=_(u'Number of visible albums on media viewlet.'),
        required=False,
        min=0,
        default=5
    )

    media_viewlet_visible_videos = schema.Int(
        title=_(u'Viewlet media : Visible videos'),
        description=_(u'Number of visible videos on media viewlet.'),
        required=False,
        min=0,
        default=2
    )

    show_description_on_themes = schema.Bool(
        title=_(u'Show description on themes'),
        description=_(u'Add content description after every portal tab menu title.'),
        required=False,
        default=False
    )

    search_position = schema.Choice(
        title=_(u'Search position'),
        description=_(u'Search box position in eligible themes.'),
        required=True,
        values=[
            u'default_position',
            u'always_in_navigation',
            u'always_in_actions',
        ],
        default=u'default_position'
    )

    collapse_minisite_menu = schema.Bool(
        title=_(u'Collapse menu on minisites'),
        description=_(u'Automatically collapse portal main menu on minisites.'),  # noqa
        required=False,
        default=False
    )

    show_footer_sitemap = schema.Bool(
        title=_(u'Show footer sitemap'),
        description=_(u'Automatically generate sitemap footer.'),
        required=False,
        default=True
    )

    header_class = schema.Choice(
        title=_(u'Header related class'),
        description=_(u'CSS header class that will be applied to body.'),
        required=False,
        values=[
            u'header-1',
            u'header-2',
            u'header-3',
            u'header-4',
        ],
        default=None
    )

    columns_class = schema.Choice(
        title=_(u'Content columns related class'),
        description=_(u'CSS content columns class that will be applied to body.'),
        required=False,
        values=[
            u'content-1',
            u'content-2',
            u'content-3',
            u'content-4',
        ],
        default=None
    )

    navigation_class = schema.Choice(
        title=_(u'Navigation related class'),
        description=_(u'CSS navigation class that will be applied to body.'),
        required=False,
        values=[
            u'navigation-1',
            u'navigation-2',
            u'navigation-3',
            u'navigation-4',
        ],
        default=None
    )

    footer_class = schema.Choice(
        title=_(u'Footer related class'),
        description=_(u'CSS footer class that will be applied to body.'),
        required=False,
        values=[
            u'footer-1',
            u'footer-2',
            u'footer-3',
            u'footer-4',
        ],
        default=None
    )

    indexed_taxonomies = schema.Text(
        title=_(u'Taxonomies to index'),
        description=_(u'List of taxonomy IDs (one per line) that should be indexed.'),
        required=False,
        default=u'types_activites\n'
    )

    use_slick = schema.Bool(
        title=_(u'Use slick for slider'),
        description=_(u'Do you want to use slick instead of flexslider ?'),
        required=False,
        default=False
    )

    enable_accessibility_link_in_footer = schema.Bool(
        title=_(u"Enable accessibility link in footer"),
        description=_(u"Enable a link to the accessibility text in footer."),
        required=False,
        default=False,
    )


class IVideoCollection(Interface):
    """
    Marker interface for video collection used to viewlet multimedia
    """


class IAlbumCollection(Interface):
    """
    Marker interface for album collection used to viewlet multimedia
    """
