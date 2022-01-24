# -*- coding: utf-8 -*-
from cpskin.core.interfaces import IAlbumCollection
from cpskin.core.interfaces import IVideoCollection
from cpskin.core.utils import image_scale
from imio.media.browser import utils
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

import logging


logger = logging.getLogger('cpskin.core media viewlet')


class MediaViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('media.pt')

    def available(self):
        context = self.context
        media_view = getMultiAdapter((context, self.request),
                                     name='media_activation')
        return media_view.is_enabled

    @property
    def portal_catalog(self):
        return api.portal.get_tool(name='portal_catalog')

    def get_videos_collection(self):
        return self.get_collection(IVideoCollection)

    def get_videos(self):
        videos = []
        collection = self.get_videos_collection()
        if not collection:
            return None
        limit = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.media_viewlet_visible_videos')  # noqa
        brains = [b for b in collection.queryCatalog()][:limit]
        for brain in brains:
            video = brain.getObject()
            videos.append(utils.embed(video, self.request))
        return videos

    def get_albums_collection(self):
        return self.get_collection(IAlbumCollection)

    def get_albums(self):
        albums = []
        collection = self.get_albums_collection()
        if not collection:
            logger.debug('{0} has no album collection'.format(self.context))
            return ''
        for gallery_brain in collection.queryCatalog():
            gallery = gallery_brain.getObject()
            imagescale = self.context.unrestrictedTraverse(
                gallery.getPhysicalPath() + ('@@images',))
            if imagescale:
                scale = image_scale(
                    gallery,
                    'image',
                    'multimedia',
                    with_uid=False)
                if not scale:
                    logger.debug(
                        '{0} has no album collection'.format(self.context))
                else:
                    html = '<a href="{0}">'.format(gallery.absolute_url())
                    html += scale.tag()
                    html += '</a>'
                    albums.append(html)
            else:
                logger.debug('{0} has no lead image'.format(
                    gallery_brain.getURL()))
        limit = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.media_viewlet_visible_albums')  # noqa
        return albums[:limit]

    def get_collection(self, object_provide):
        queryDict = {}
        queryDict['object_provides'] = object_provide.__identifier__
        queryDict['path'] = {
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': 1
        }
        queryDict['sort_limit'] = 1
        brains = self.portal_catalog(queryDict)
        if len(brains) == 0:
            return None
        brain = brains[0]
        folder = brain.getObject()
        collection = getattr(folder, 'index', None)
        if not collection:
            return None
        return collection
