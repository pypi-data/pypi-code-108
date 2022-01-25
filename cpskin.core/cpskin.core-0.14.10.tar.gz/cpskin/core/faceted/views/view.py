# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.contact.core.browser.address import get_address
from cpskin.core.browser.common import CommonView
from cpskin.core.browser.contactdetails import ContactDetailsView
from zope.component import getMultiAdapter


class PreviewItem(ContactDetailsView, CommonView):

    def address(self):
        dict_address = get_address(self.context)
        template_path = 'address.pt'
        template = ViewPageTemplateFile(template_path)
        return template(self, dict_address)

    def city(self):
        dict_address = get_address(self.context)
        city = dict_address.get('city')
        return city

    def scaled_image_url(self, field):
        obj = self.context
        directory = self.request.get('directory')
        scale = getattr(directory, 'organization_image_scale', 'mini')
        url = ''
        images = obj.restrictedTraverse('@@images')
        if getattr(obj, field, False):
            image = images.scale(field, scale=scale)
            if image:
                url = image.url
        return url

    def show_photos_previews(self):
        directory = self.context
        return getattr(directory, 'show_organization_images', False)

    def render_contact_photo_preview(self, obj):
        context = self.context
        request = self.request
        request['directory'] = context
        render_view = u'faceted-preview-contact-photos'
        view = getMultiAdapter((obj, request), name=render_view)
        return view and view() or ''

    def render_item_preview(self, obj):
        context = self.context
        request = self.request
        scale = getattr(context, 'collection_image_scale', 'thumb')
        request['scale'] = scale
        request['collection'] = context
        render_view = u'faceted-preview-item'
        view = getMultiAdapter((obj, request), name=render_view)
        return view and view() or ''
