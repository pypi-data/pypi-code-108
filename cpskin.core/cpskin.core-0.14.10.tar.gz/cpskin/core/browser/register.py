# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.users.browser.register import RegistrationForm
from zope import schema
from zope.formlib import form
from zope.formlib.interfaces import WidgetInputError
from zope.interface import Interface

from cpskin.locales import CPSkinMessageFactory as _


class ICustomRegisterSchema(Interface):

    legal_conditions = schema.Bool(
        title=_(u'I Accept Legal terms and conditions'),
        description=_(u''),
        required=True,
    )


class CustomRegistrationForm(RegistrationForm):
    correct_captcha = None
    template = ViewPageTemplateFile('templates/register_form.pt')

    @property
    def form_fields(self):
        base_fields = super(CustomRegistrationForm, self).form_fields
        custom_fields = form.Fields(ICustomRegisterSchema)
        portal_url = api.portal.get().absolute_url()
        gpdr_url = '/'.join([portal_url, 'gdpr-view'])
        msgid = _(
            u'see_legal_conditions',
            default=u'See <a href="${legal_conditions_url}">legal terms and conditions</a>.',  #NOQA
            mapping={u'legal_conditions_url': gpdr_url},
        )
        legal_description = self.context.translate(msgid)
        custom_fields['legal_conditions'].field.description = legal_description
        return base_fields + custom_fields

    def validate_registration(self, action, data):
        errors = super(CustomRegistrationForm, self).validate_registration(
            action,
            data,
        )
        if not data.get('legal_conditions'):
            err_str = _(u'You need to accept our legal terms and conditions.')
            error = WidgetInputError(
                'legal_conditions',
                _(u'I Accept Legal terms and conditions'),
                err_str,
            )
            errors.append(error)
            self.widgets['legal_conditions'].error = err_str
        correct_captcha = self.context.restrictedTraverse('@@captcha').verify()
        if not correct_captcha:
            error = WidgetInputError(
                'captcha',
                'Captcha',
                _(u'Incorrect captcha')
            )
            errors.append(error)
        self.correct_captcha = correct_captcha
        return errors
