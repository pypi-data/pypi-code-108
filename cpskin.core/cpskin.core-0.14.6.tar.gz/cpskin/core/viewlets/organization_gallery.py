# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.contact.core.content.organization import IOrganization
from collective.folderishtypes.interfaces import IFolderishType
from plone import api
from plone.app.layout.viewlets import common


class OrganizationGalleryViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('organization_gallery.pt')

    def available(self):
        """
        Condition on the content types wanted for the gallery viewlet
        (it was first meant only for Organizations), now it is also used for
        folderish content types (collective.folderish)
        """
        context = self.context
        return IOrganization.providedBy(context) or IFolderishType.providedBy(context)

    def get_photos(self):
        brains = api.content.find(
            context=self.context,
            depth=1,
            portal_type='Image'
        )
        return [b.getObject() for b in brains]

    def image_url(self, obj, default_scale='preview'):
        url = ''
        images = obj.restrictedTraverse('@@images')
        image = images.scale('image', scale=default_scale)
        if image:
            url = image.url
        return url
