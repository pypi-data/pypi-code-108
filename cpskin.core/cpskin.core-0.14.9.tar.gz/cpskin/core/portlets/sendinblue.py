# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from collective.sendinblue.browser.portlet import PortletSubscribeForm
from collective.sendinblue.browser.portlet import Renderer
from collective.sendinblue.interfaces import INewsletterSubscribe
from cpskin.locales import CPSkinMessageFactory as _
from plone.app.portlets.portlets import base
from plone import api
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from plone.z3cform import z2
from plone.z3cform.interfaces import IWrappedForm
from z3c.form import button
from z3c.form import field
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import alsoProvides


class IGDPRSubscribe(Interface):

    legal_conditions = schema.Bool(
        title=_(u'I Accept Legal terms and conditions'),
        description=_(u''),
        required=True,
    )


class GDPRRenderer(Renderer):

    def update(self):
        base.Renderer.update(self)
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = GDPRPortletSubscribeForm(aq_inner(self.context), self.request, self.data)
        portal_url = api.portal.get_navigation_root(self.context).absolute_url()
        gpdr_url = '/'.join([portal_url, 'gdpr-view'])
        msgid = _(
            u'see_legal_conditions',
            default=u'See <a href="${legal_conditions_url}">legal terms and conditions</a>.',  # NOQA
            mapping={u'legal_conditions_url': gpdr_url},
        )
        legal_description = self.context.translate(msgid)
        gdpr_field = self.form.fields.get('legal_conditions')
        gdpr_field.field.description = legal_description
        alsoProvides(self.form, IWrappedForm)
        self.form.update()


class GDPRPortletSubscribeForm(PortletSubscribeForm):
    base_fields = field.Fields(INewsletterSubscribe)
    gdpr_fields = field.Fields(IGDPRSubscribe)
    fields = base_fields + gdpr_fields
    ignoreContext = True
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    @button.buttonAndHandler(_('Subscribe'), name='subscribe')
    def handle_subscribe(self, action):
        data, errors = self.extractData()
        if not data.get('legal_conditions'):
            raise WidgetActionExecutionError(
                'legal_conditions',
                Invalid(_(u'You need to accept our legal terms and conditions.'))
            )

        return super(GDPRPortletSubscribeForm, self).handle_subscribe(
            self,
            action,
        )
