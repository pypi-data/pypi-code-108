# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from cpskin.core.browser.common import CommonView
from cpskin.core.interfaces import IFolderViewSelectedContent
from cpskin.core.interfaces import IFolderViewWithBigImages
from cpskin.core.utils import image_scale
from cpskin.core.vocabulary import DISPLAY_TYPES
from cpskin.locales import CPSkinMessageFactory as _
from datetime import datetime
from DateTime import DateTime
from imio.media.browser import utils
from plone import api
from plone.app.contenttypes.browser.folder import FolderView as FoldV
from plone.app.event.base import expand_events
from plone.app.event.base import filter_and_resort
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.interfaces import IEventSettings
from plone.app.event.recurrence import RecurrenceSupport
from plone.app.querystring import queryparser
from plone.event.interfaces import IEvent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import json
import logging
import pytz

logger = logging.getLogger("cpskin.core")

ADDABLE_TYPES = ["Collection", "Document", "Folder", "rss_feed"]


class FolderView(FoldV, CommonView):
    def _redirect(self, msg=""):
        if self.request:
            if msg:
                api.portal.show_message(message=msg, request=self.request, type="info")
            self.request.response.redirect(self.context.absolute_url())
        return msg

    def _get_real_context(self):
        context = self.context
        plone_view = getMultiAdapter((context, self.request), name="plone")
        if plone_view.isDefaultPageInFolder():
            context = aq_parent(context)
        context = aq_inner(context)
        return context

    def isFolderViewActivated(self, context=None):
        """Check if folderview is activated on context"""
        if context is None:
            context = self.context
        layout = context.getLayout()
        if layout == "folderview":
            return True
        return False

    def can_configure(self):
        """Check if folderview can be configured on context"""
        context = self.context
        if not IFolderish.providedBy(context):
            return False
        already_activated = self.isFolderViewActivated()
        return not already_activated

    def configure(self):
        """Configure folders and collections for folderview"""
        context = self.context
        configure_folderviews(context)
        api.portal.show_message(
            message=_(u"Vue index avec collections configurée."),
            request=self.request,
            type="info",
        )
        self.request.response.redirect(context.absolute_url())
        return ""

    def is_event_collection(self, brains):
        if len(brains) > 0:
            obj = brains[0].getObject()
            return IEvent.providedBy(obj)
        return False

    def getResults(self, content, with_sticky=True):
        """Content is a Collection"""
        # Make a copy of the query to avoid modifying it
        query = list(content.query)
        index_view_keywords = getattr(content, "index_view_keywords", False)
        # set query for homepage
        if index_view_keywords:
            homepage_keywords = content.index_view_keywords
            query.append(
                {
                    "i": "hiddenTags",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": homepage_keywords,
                }
            )
        sort_on = getattr(content, "sort_on", None)
        sort_order = (
            "reverse" if getattr(content, "sort_reversed", False) else "ascending"
        )  # noqa
        sort_reversed = getattr(content, "sort_reversed", False)
        parsedquery = queryparser.parseFormquery(content, query, sort_on, sort_order)
        portal_catalog = api.portal.get_tool("portal_catalog")
        brains = portal_catalog(parsedquery)
        item_count_homepage = getattr(content, "item_count_homepage", 8)
        if self.is_event_collection(brains):
            start = DateTime()
            sort_on = getattr(content, "sort_on", "start")
            if sort_on in ("start", "end"):
                filter_and_resort_brains = filter_and_resort(
                    content, brains, start, None, sort_on, sort_reversed
                )
                brains = filter_and_resort_brains[:item_count_homepage]

        brains = brains[:item_count_homepage]
        if not with_sticky:
            return brains
        portal_catalog = api.portal.get_tool(name="portal_catalog")
        results = {"sticky-results": [], "standard-results": []}
        for brain in brains:
            if portal_catalog.getIndexDataForRID(brain.getRID())["is_sticky"]:
                results["sticky-results"].append(brain)
            else:
                results["standard-results"].append(brain)
        if not results["sticky-results"] and not results["standard-results"]:
            return None
        return results

    def getContents(self):
        brains = self.searchSelectedContent()
        objects = [brain.getObject() for brain in brains]
        realObjects = []
        for obj in objects:
            if obj.portal_type == "Folder":
                if obj.getDefaultPage() is not None:
                    realObject = getattr(obj, obj.getDefaultPage())
                    # check if realObject is a collection :
                    if getattr(realObject, "results", None):
                        if len(realObject.results()) > 0:
                            realObjects.append(realObject)
                else:
                    continue
            elif obj.portal_type == "rss_feed":
                realObjects.append(obj)
            elif obj.portal_type == "Link":
                try:
                    realObjects.append(
                        type(
                            "Link",
                            (object,),
                            {
                                "id": obj.id,
                                "render": self.context.unrestrictedTraverse(
                                    str(obj.remoteUrl)
                                ),
                                "portal_type": obj.portal_type,
                            },
                        )()
                    )
                except:
                    pass
            else:
                realObjects.append(obj)
        return realObjects

    def isBigImage(self, number, results, resultType):
        """
        Check if image should be big depending on position and result type
        (sticky / non-sticky)
        """
        if not self.bigImagesAreUsed():
            return False
        if resultType == "sticky-results" and number < 5:
            return True
        elif resultType == "standard-results" and number < 5 - len(
            results["sticky-results"]
        ):
            return True
        return False

    def getThumbSize(self, obj, isBigImage=False):
        prefix = "image"
        thumbSize = "thumb"
        if getattr(obj, "hasContentLeadImage", None):
            prefix = "leadImage"
        if isBigImage:
            thumbSize = "mini"
        return "%s_%s" % (prefix, thumbSize)

    def searchSelectedContent(self):
        path = "/".join(self.context.getPhysicalPath())
        portal_catalog = api.portal.get_tool("portal_catalog")
        queryDict = {}
        queryDict["path"] = {"query": path, "depth": 1}
        queryDict["portal_type"] = ADDABLE_TYPES
        queryDict["object_provides"] = IFolderViewSelectedContent.__identifier__  # noqa
        queryDict["sort_on"] = "getObjPositionInParent"
        queryDict["review_state"] = (
            "published_and_hidden",
            "published_and_shown",
            "published",
        )
        results = portal_catalog.searchResults(queryDict)
        return results

    def getSliderType(self, collection=""):
        if collection:
            return getattr(collection, "display_type", None)
        return None

    def hasFlexSlider(self):
        """Check if flexslider is available and installed"""
        try:
            from cpskin.slider.interfaces import ICPSkinSliderLayer
        except ImportError:
            return False
        else:
            request = getattr(self.context, "REQUEST", None)
            if ICPSkinSliderLayer.providedBy(request):
                return True
            return False

    def has_slick_slider(self):
        if self.hasFlexSlider() is True:
            return api.portal.get_registry_record(
                "cpskin.core.interfaces.ICPSkinSettings.use_slick",
                default=False,
            )
        return False

    def show_image(self, collection):
        slider_type = self.getSliderType(collection)
        return DISPLAY_TYPES[slider_type]["show-image"]

    def show_carousel(self, collection):
        slider_type = self.getSliderType(collection)
        return DISPLAY_TYPES[slider_type]["show-carousel"]

    def addContent(self):
        """Mark content to add it to folder view"""
        context = self._get_real_context()
        alsoProvides(context, IFolderViewSelectedContent)
        catalog = api.portal.get_tool("portal_catalog")
        catalog.reindexObject(context)
        self._redirect(_(u"Contenu ajouté à la vue index."))

    def removeContent(self):
        """Unmark content to remove it from folder view"""
        context = self._get_real_context()
        noLongerProvides(context, IFolderViewSelectedContent)
        catalog = api.portal.get_tool("portal_catalog")
        catalog.reindexObject(context)
        self._redirect(_(u"Contenu retiré de la vue index."))

    def isEligibleContent(self):
        context = self._get_real_context()
        if context.portal_type not in ADDABLE_TYPES:
            return False
        parent = aq_parent(context)
        if not self.isFolderViewActivated(parent):
            return False
        return True

    def canAddContent(self):
        if not self.isEligibleContent():
            return False
        context = self._get_real_context()
        if IFolderViewSelectedContent.providedBy(context):
            return False
        return True

    def canRemoveContent(self):
        if not self.isEligibleContent():
            return False
        context = self._get_real_context()
        if not IFolderViewSelectedContent.providedBy(context):
            return False
        return True

    def canUseBigImages(self):
        """Check if big images can be used on folder view"""
        if not self.isFolderViewActivated():
            return False
        context = self._get_real_context()
        return not IFolderViewWithBigImages.providedBy(context)

    def bigImagesAreUsed(self):
        context = self._get_real_context()
        return IFolderViewWithBigImages.providedBy(context)

    def canStopBigImagesUse(self):
        """Check if big images are used on folder view"""
        if not self.isFolderViewActivated():
            return False
        return self.bigImagesAreUsed()

    def useBigImages(self):
        """Use big images for first elements on folder view"""
        context = self._get_real_context()
        alsoProvides(context, IFolderViewWithBigImages)
        catalog = api.portal.get_tool("portal_catalog")
        catalog.reindexObject(context)
        self._redirect(_(u"Big images are now used on this folder view."))

    def stopBigImagesUse(self):
        """Use using big images for first elements on folder view"""
        context = self._get_real_context()
        noLongerProvides(context, IFolderViewWithBigImages)
        catalog = api.portal.get_tool("portal_catalog")
        catalog.reindexObject(context)
        self._redirect(_(u"Big images are not used anymore on this folder view."))

    def slick_config(self, content):
        portal_registry = getToolByName(self.context, "portal_registry")
        slider_timer = portal_registry[
            "cpskin.core.interfaces.ICPSkinSettings.slider_timer"
        ]
        min_items, max_items = self.get_items_number(content)
        slider_type = self.getSliderType(content)
        slider_config = DISPLAY_TYPES[slider_type]
        config = {
            "slidesToScroll": getattr(content, "slide_to_scroll", False),
            "dots": getattr(content, "show_dots", True),
            "arrows": getattr(content, "show_arrows", False),
            "speed": getattr(content, "speed", 300),
            "easing": slider_config.get("easing", "ease"),
            "autoplay": getattr(content, "autoplay_mode", False),
            "autoplaySpeed": getattr(content, "autoplay_speed", False),
            "centerMode": getattr(content, "use_center_mode", False),
            "centerPadding":str(getattr(content, "center_padding", False)) + "px",
            "fade": getattr(content, "fade", False),
        }
        if slider_config.get("variable-width", False):
            config["variableWidth"] = True
        else:
            config["responsive"] = [
                {
                    "breakpoint": getattr(content, "breakpoint_full", False),
                    "settings": {
                        "slidesToShow": getattr(content, "slides_to_show_full", False),
                        "slidesToScroll":getattr(content, "slides_to_scroll_full", False)
                    }
                },
                {
                    "breakpoint": getattr(content, "breakpoint_medium", False),
                    "settings": {
                        "slidesToShow": getattr(content, "slides_to_show_medium", False),
                        "slidesToScroll":getattr(content, "slides_to_scroll_medium", False)
                    }
                },
                {
                    "breakpoint": getattr(content, "breakpoint_small", False),
                    "settings": {
                        "slidesToShow": getattr(content, "slides_to_show_small", False),
                        "slidesToScroll":getattr(content, "slides_to_scroll_small", False)
                    }
                }
            ]
            config["slidesToShow"] = min_items
        return json.dumps(config)

    def slider_config(self, content):
        content_id = content.id
        portal_registry = getToolByName(self.context, "portal_registry")
        slider_timer = portal_registry[
            "cpskin.core.interfaces.ICPSkinSettings.slider_timer"
        ]
        auto_play_slider = portal_registry[
            "cpskin.core.interfaces.ICPSkinSettings.auto_play_slider"
        ]
        min_items, max_items = self.get_items_number(content)
        slider_type = self.getSliderType(content)
        show_control_nav = DISPLAY_TYPES[slider_type]["control-nav"]
        config = """
        (function($) {
            "use strict";
            var animation = "slide";
            // IE 9 does not support 'slide' animation
            if (navigator.sayswho === 'MSIE 9' || navigator.sayswho === 'IE 9')
            {
            animation = "fade";
            }
            $('.slider_multiple_link').click(function() {
                var href = $(this).attr('href');
                if ($(this).attr('target') == '_blank') window.open(href);
                else window.location.href = href;
            });
            function SlideShow(autoplayslider, content_id) {
                if ($('#slider-' + content_id).parents('.slider-unique-titre').length) {
                    return false;
                }
                else {
                    return autoplayslider;
                }
            }
            function ChangeSlideCurrent(content_id) {
                if ($('#carousel-evenements').parents('.slider-unique-titre').length) {
                    var slides = $('#carousel-evenements').find('.slides');
                    var len = slides.find('li').length;
                    var current = (Math.ceil(len/2) - 1);
                    return current;
                }
            }
            function deplaceSlideCurrent(content_id) {
                $('.slider-unique-titre').each(function (){
                    var carousel = $(this).find('#carousel-%(content_id)s');
                    var carousel_slide = carousel.find('ul.slides');
                    var carousel_slide_active = carousel_slide.find('li.flex-active-slide');
                    var carousel_slide_width = carousel_slide_active.outerWidth(true);
                    var slide_current = carousel_slide_active.index();
                    if (slide_current != 0) {
                        var translate3D_px = -(slide_current * carousel_slide_width) + carousel_slide_width;
                        carousel_slide.css('transform', 'translate3d(' + translate3D_px + 'px, 0px, 0px)');
                    }
                    else {
                        var translate3D_px = carousel_slide_width;
                        carousel_slide.css('transform', 'translate3d(' + translate3D_px + 'px, 0px, 0px)');
                    }
                    carousel_slide.css('transition-duration', '0.2s');
                });
            }
            $('#carousel-%(content_id)s').flexslider({
              animation: animation,
              controlNav: %(show_control_nav)s,
              animationLoop: false,
              slideshow: false,
              itemWidth: 210,
              itemMargin: 5,
              minItems: %(min_items_in_slider)s,
              maxItems: %(max_items_in_slider)s,
              asNavFor: '#slider-%(content_id)s',
              startAt: ChangeSlideCurrent('%(content_id)s'),
              start: function(slider) {
                slider.find('.current-slide').text(slider.currentSlide+1);
                slider.find('.total-slides').text(slider.count);
                deplaceSlideCurrent('%(content_id)s');
              },
              after: function(slider) {
                slider.find('.current-slide').text(slider.currentSlide+1);
                deplaceSlideCurrent('%(content_id)s');
              }
            });
            $('#slider-%(content_id)s').flexslider({
              animation: animation,
              controlNav: %(show_control_nav)s,
              animationLoop: true,
              slideshow: SlideShow(%(auto_play_slider)s, '%(content_id)s'),
              slideshowSpeed: %(slider_timer)s,
              sync: "#carousel-%(content_id)s",
              start: function(slider) {
                  deplaceSlideCurrent('%(content_id)s');
              },
              after: function(slider) {
                deplaceSlideCurrent('%(content_id)s');
              }
            });
         })(jQuery);
        """ % {
            "auto_play_slider": auto_play_slider and "true" or "false",
            "slider_timer": slider_timer,
            "show_control_nav": show_control_nav and "true" or "false",
            "content_id": content_id,
            "min_items_in_slider": min_items,
            "max_items_in_slider": max_items,
        }
        return config

    def scaled_image_url(self, context, obj, isBigImage):
        image = self.collection_image_scale(context, obj)
        return image and image.url or ""

    def collection_image_scale(self, collection, obj):
        scale = getattr(collection, "collection_image_scale", "collection")
        if self.use_new_template(collection):
            return image_scale(obj, "newsImage", scale, generate_tag=False)
        else:
            return image_scale(obj, "newsImage", scale)

    def see_all(self, collection):
        voirlensemble = _(u"Voir l'ensemble des")
        coll_lang = getattr(collection, "language")
        lang = coll_lang if (coll_lang != "" and "-" not in coll_lang) else "fr"  # noqa
        trans = translate(
            voirlensemble, domain=voirlensemble.domain, target_language=lang
        )
        if getattr(collection, "link_text", ""):
            return collection.link_text.encode("utf-8")
        return "{0} {1}".format(trans, collection.Title().lower())

    def get_video(self, video):
        result = utils.embed(video, self.request)
        return result

    def get_class(self, classe):
        if classe == "Media Link":
            return "medialink"
        else:
            return None

    def toLocalizedTime(
        self, time=None, long_format=None, time_only=None, event=None, startend="start"
    ):
        if not event:
            return self.context.restrictedTraverse("@@plone").toLocalizedTime(
                time, long_format, time_only
            )
        if ICatalogBrain.providedBy(event):
            event = event.getObject()
        if not IEvent.providedBy(event):
            return self.context.restrictedTraverse("@@plone").toLocalizedTime(
                time, long_format, time_only
            )
        rs = RecurrenceSupport(event)
        occurences = [occ for occ in rs.occurrences(datetime.today()) if IEvent.providedBy(occ)]
        if len(occurences) >= 1:
            # do not get object which started in the past
            if startend == "start":
                time = getattr(occurences[0], "start")
            elif startend == "end":
                time = getattr(occurences[-1], "end")
        return self.context.restrictedTraverse("@@plone").toLocalizedTime(
            time, long_format, time_only
        )

    def get_portal_timezone(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        return settings.portal_timezone

    def get_event_dates(self, result):
        timezone = self.get_portal_timezone()
        occurences = expand_events([result], RET_MODE_ACCESSORS)
        start_date = getattr(occurences[0], "start")
        end_date = getattr(occurences[-1], "end")

        if not start_date:
            return {"start": "", "end": ""}
        if getattr(start_date, "astimezone", False):
            start_date = start_date.astimezone(pytz.timezone(timezone))
        formated_start = start_date.strftime("%d/%m")
        if not end_date:
            return {"start": formated_start, "end": ""}
        if getattr(end_date, "astimezone", False):
            end_date = end_date.astimezone(pytz.timezone(timezone))
        formated_end = end_date.strftime("%d/%m")
        if formated_start != formated_end:
            return {"start": formated_start, "end": formated_end}
        return {"start": formated_start, "end": ""}

    def is_one_day(self, event):
        occurences = expand_events([event], RET_MODE_ACCESSORS)
        if not occurences:
            start_date = event.start
            end_date = event.end
        else:
            start_date = getattr(occurences[0], "start")
            end_date = getattr(occurences[-1], "end")
        return self.toLocalizedTime(start_date, long_format=0) == self.toLocalizedTime(
            end_date, long_format=0
        )

    def is_with_hours(self, event):
        if getattr(event, "whole_day", False):
            return not (event.whole_day)
        else:
            return (
                self.toLocalizedTime(event.start, long_format=1)[11:] != "00:00"
                or self.toLocalizedTime(event.end, long_format=1)[11:] != "00:00"
            )  # noqa

    def is_open_end(self, event):
        return getattr(event, "open_end", False)

    def see_start_end_date(self, brain, collection):
        if getattr(brain, "start", False) and getattr(brain, "end", False):
            if not getattr(collection, "hide_date", False):
                return True
            else:
                return False
        else:
            return False

    def hide_title(self, collection):
        return getattr(collection, "hide_title", False)

    def hide_see_all_link(self, collection):
        return getattr(collection, "hide_see_all_link", False)

    def hide_date(self, brain, collection):
        """Check if object has a correct effective date.
        If None, you get 01/01/1000 and strftime cannot convert it.
        Also check if collection is checked to see publication date.
        """
        if not getattr(brain, "start", None) and not getattr(
            brain, "end", None
        ):  # noqa
            return getattr(collection, "hide_date", True)
        else:
            # always hide effective date for events
            return True

    def show_day_and_month(self, collection):
        return getattr(collection, "show_day_and_month", False)

    def show_lead_image(self, collection):
        return getattr(collection, "show_lead_image", True)

    def show_descriptions(self, collection):
        return getattr(collection, "show_descriptions", False)

    def use_new_template(self, collection):
        return getattr(collection, "use_new_template", False)

    def use_slider(self, collection):
        display_type = getattr(collection, "display_type", "")
        if not display_type or display_type not in DISPLAY_TYPES:
            return False
        return DISPLAY_TYPES[display_type]["slider"]

    def use_slick(self, collection):
        if self.use_slider(collection) is True:
            return api.portal.get_registry_record(
                "cpskin.core.interfaces.ICPSkinSettings.use_slick",
                default=False,
            )
        return False

    def get_items_number(self, collection):
        display_type = getattr(collection, "display_type", "")
        if display_type != "slider-with-elements-count-choice" and display_type != "slider-slick":
            return 0, 0
        min_items = getattr(collection, "minimum_items_in_slider", 0)
        max_items = getattr(collection, "maximum_items_in_slider", 0)
        return min_items, max_items

    def get_block_class(self, collection):
        display_type = getattr(collection, "display_type", "")
        if not display_type or display_type not in DISPLAY_TYPES:
            return ""
        return DISPLAY_TYPES[display_type]["class"]

    def show_publication_date(self, collection, result):
        if self.hide_date(result, collection):
            return False
        display_type = getattr(collection, "display_type", "")
        return display_type == "slider-with-elements-count-choice"

    def show_event_category_below_image(self, collection):
        return getattr(collection, "show_event_category_below_image", False)


def configure_folderviews(context):
    """
    """
    existingIds = context.objectIds()
    portalPath = api.portal.get().getPhysicalPath()
    contextPath = "/".join(context.getPhysicalPath()[len(portalPath) :])
    if "a-la-une" not in existingIds:
        folder = api.content.create(
            container=context, type="Folder", id="a-la-une", title=_(u"À la une")
        )
        alsoProvides(folder, IFolderViewSelectedContent)
        collection = api.content.create(
            container=folder, type="Collection", id="a-la-une", title=_(u"À la une")
        )
        query = [
            {
                "i": "hiddenTags",
                "o": "plone.app.querystring.operation.selection.is",
                "v": "a-la-une",
            },
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/%s" % contextPath,
            },
        ]
        collection.setQuery(query)
        collection.setSort_on("effective")
        collection.setSort_reversed(True)
        collection.setLayout("summary_view")
        folder.setDefaultPage("a-la-une")
        folder.reindexObject()
    if "actualites" not in existingIds:
        folder = api.content.create(
            container=context, type="Folder", id="actualites", title=_(u"Actualités")
        )
        collection = api.content.create(
            container=folder, type="Collection", id="actualites", title=_(u"Actualités")
        )
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["News Item"],
            },
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/%s" % contextPath,
            },
        ]
        collection.setQuery(query)
        collection.setSort_on("effective")
        collection.setSort_reversed(True)
        collection.setLayout("summary_view")
        folder.setDefaultPage("actualites")
    else:
        folder = context["actualites"]
    alsoProvides(folder, IFolderViewSelectedContent)
    folder.reindexObject()

    if "evenements" not in existingIds:
        folder = api.content.create(
            container=context, type="Folder", id="evenements", title=_(u"Événements")
        )
        collection = api.content.create(
            container=folder, type="Collection", id="evenements", title=_(u"Événements")
        )
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["Event"],
            },
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/%s" % contextPath,
            },
        ]
        collection.setQuery(query)
        collection.setSort_on("effective")
        collection.setSort_reversed(True)
        collection.setLayout("summary_view")
        folder.setDefaultPage("evenements")
    else:
        folder = context["evenements"]
    alsoProvides(folder, IFolderViewSelectedContent)
    folder.reindexObject()
    context.setLayout("folderview")
