# -*- coding: utf-8 -*-
from imio.gdpr import _
from imio.gdpr import get_default_text
from imio.gdpr import get_default_cookies_text
from imio.gdpr import IS_PLONE4
from plone.autoform import directives as form
from plone.supermodel import model
from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IImioGdprLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IGDPRSettings(model.Schema):
    """Schema for the control panel form."""

    if IS_PLONE4:
        # IS_PLONE4: remove on deprecation of Plone 4.3
        from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
        form.widget('text', WysiwygFieldWidget)
        form.widget('cookies_text', WysiwygFieldWidget)
    else:
        form.widget('text', klass='pat-tinymce')
        form.widget('cookies_text', klass='pat-tinymce')

    text = schema.Text(
        title=_(u'title_text', default=u'Body text'),
        description=_(
            u'help_text',
            default=u'The text of the GDPR explanation.'),
        required=True,
        defaultFactory=get_default_text,
    )

    is_text_ready = schema.Bool(
        title=_(u'is_text_ready_text', default=u'Is text ready ?'),
        description=_(
            u'help_is_text_ready',
            default=u'Is text is not ready, it should not be visible'),
        required=True,
        default=False,
    )

    cookies_text = schema.Text(
        title=_(u'title_cookies_text', default=u'Cookies text'),
        description=_(
            u'help_cookies_text',
            default=u'The text of the Cookies Policy page.'),
        required=True,
        defaultFactory=get_default_cookies_text,
    )
