# -*- coding: utf-8 -*-
from cpskin.core.utils import has_lat_lng
from cpskin.core.utils import set_coord
from cpskin.locales import CPSkinMessageFactory as _
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.directives import form
from z3c.form import button
from zope import schema

import logging


logger = logging.getLogger('cpskin.core.encode_lat_lng')


class IGeoForm(form.Schema):
    """ Define form fields """

    content_types = schema.List(
        title=_(u'Content type'),
        description=_(
            u'Which content type should be set latitude and longitude'),
        value_type=schema.Choice(
            title=_(u'Content types'),
            vocabulary='cpskin.core.vocabularies.geo_types',
        ),
        required=False,
    )


class GeoForm(form.SchemaForm):

    schema = IGeoForm
    ignoreContext = True

    label = u"What's object do you want to update ?"
    description = u'This script will update latitude and longitude for objects \
                    selected'

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        # Do something with valid data here

        # Set status on this form page (this status message
        # is not bind to the session and does not go thru redirects)
        results = []
        if 'content_types' not in data.keys():
            pass
        else:
            for portal_type in data['content_types']:
                list_updated = set_lat_lng(portal_type, self.request)
                results.extend(list_updated)
                message = '{1} {0} are updated'.format(
                    portal_type, len(list_updated))
                api.portal.show_message(message=message, request=self.request)
        # self.status = "\n".join(results)

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


def set_lat_lng(portal_type, request):
    catalog = api.portal.get_tool('portal_catalog')
    query = {}
    query['portal_type'] = portal_type
    brains = catalog(query)
    nbre = len(brains)
    results = []
    i = 0
    for brain in brains:
        obj = brain.getObject()
        i += 1
        if not has_lat_lng(obj):
            message = set_coord(obj, request)
            if message:
                results.append(message)
        logger.info('{0}/{1}'.format(i, nbre))
    return results


class IReplaceRichtextForm(form.Schema):
    """ Define form fields """

    old_text = schema.TextLine(
        title=_(u'Old text'),
        description=_(
            u'Text to be replaced in all your RichTextValue'),
        required=False,
    )

    new_text = schema.TextLine(
        title=_(u'New text'),
        description=_(
            u'Text which will replace all your old_text into RichTextValue'),
        required=False,
    )


class ReplaceRichtextForm(form.SchemaForm):
    schema = IReplaceRichtextForm
    ignoreContext = True

    label = u'What text do you want to change ?'
    description = u'This script will update old_text value with new_text value'

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        # Do something with valid data here

        # Set status on this form page (this status message
        # is not bind to the session and does not go thru redirects)
        old_text = data['old_text']
        new_text = data['new_text']
        if not old_text:
            old_text = u''
        if not new_text:
            new_text = u''
        catalog = api.portal.get_tool('portal_catalog')
        query = {}
        query['object_provides'] = 'plone.app.contenttypes.behaviors.richtext.IRichText'  # noqa
        results = catalog(**query)
        for result in results:
            obj = result.getObject()
            text = getattr(obj, 'text', None)
            if text:
                clean_text = text.raw.replace(old_text, new_text)
                if clean_text != text.raw:
                    obj.text = RichTextValue(
                        raw=clean_text,
                        mimeType=text.mimeType,
                        outputMimeType=text.outputMimeType,
                        encoding=text.encoding
                    )
                    obj.reindexObject()
                    message = '{0} is updated'.format(obj.absolute_url())
                    logger.info(message)
                    api.portal.show_message(
                        message=message, request=self.request)
