# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.portlets.portlets import base
from plone.autoform.widgets import ParameterizedWidget
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from plone.z3cform.interfaces import IWrappedForm
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Invalid
from zope.interface import alsoProvides
from zope.interface import implementer
import logging

from collective.sendinblue import _
from collective.sendinblue.exceptions import SendinblueException
from collective.sendinblue.interfaces import INewsletterSubscribe
from collective.sendinblue.interfaces import ISendinblueAPI


logger = logging.getLogger('collective.sendinblue')


class ISendinbluePortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True
    )

    description = schema.TextLine(
        title=_(u"Portlet description"),
        description=_(u"Description of the rendered portlet"),
        required=False
    )

    newsletter_list = schema.Choice(
        title=_(u'List'),
        description=_(u'Select list to enable subscriptions to'),
        required=True,
        vocabulary='collective.sendinblue.vocabularies.AvailableLists'
    )

    archive_url = schema.TextLine(
        title=_(u"Archive link"),
        description=_(u"Link to a page where you store previous newsletters"),
        required=False
    )

    use_captcha = schema.Bool(
        title=_(u"Use captcha"),
        description=_(u"Use a captcha to protect your subscription form against robots"),
        default=True
    )


@implementer(ISendinbluePortlet)
class Assignment(base.Assignment):

    def __init__(self,
                 header=u'',
                 description=u'',
                 newsletter_list=u'',
                 archive_url=u'',
                 use_captcha=True):
        self.header = header
        self.description = description
        self.newsletter_list = newsletter_list
        self.archive_url = archive_url
        self.use_captcha = use_captcha

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portlet.pt')
    form = None

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

    def header(self):
        return self.data.header

    def description(self):
        return self.data.description

    def archive_url(self):
        return self.data.archive_url

    def update(self):
        super(Renderer, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = PortletSubscribeForm(aq_inner(self.context), self.request, self.data)
        alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):

    schema = ISendinbluePortlet

    label = _(u"Add Sendinblue Portlet")
    description = _(
        u"This portlet displays a subscription form for a Sendinblue newsletter.")

    def update(self):
        sendinblue = getUtility(ISendinblueAPI)
        sendinblue.updateCache()
        super(AddForm, self).update()

    def create(self, data):
        return Assignment(
            header=data.get('header', u''),
            description=data.get('description', u''),
            newsletter_list=data.get('newsletter_list', u''),
            archive_url=data.get('archive_url', u''),
            use_captcha=data.get('use_captcha', True),
        )


class EditForm(base.EditForm):

    schema = ISendinbluePortlet

    label = _(u"Edit Sendinblue Portlet")
    description = _(
        u"This portlet displays a subscription form for a Sendinblue newsletter.")

    def update(self):
        sendinblue = getUtility(ISendinblueAPI)
        sendinblue.updateCache()
        super(EditForm, self).update()


class Captcha(object):
    subject = u""
    captcha = u""

    def __init__(self, context):
        self.context = context


class PortletSubscribeForm(Form):
    fields = field.Fields(INewsletterSubscribe)
    ignoreContext = True
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget
    fields["email"].widgetFactory = ParameterizedWidget(
        None,
        placeholder=_(u"Email address"),
    )

    def __init__(self, context, request, data=None):
        super(PortletSubscribeForm, self).__init__(context, request)
        self.data = data

    def update(self):
        if not self.data.use_captcha:
            self.fields = self.fields.omit("captcha")
        super(PortletSubscribeForm, self).update()

    @button.buttonAndHandler(_('Subscribe'), name='subscribe')
    def handle_subscribe(self, action):
        if self.data.use_captcha:
            captcha = getMultiAdapter(
                (aq_inner(self.data), self.request),
                name='recaptcha'
            )
            if not captcha.verify():
                raise WidgetActionExecutionError(
                    'captcha',
                    Invalid(_(u"Please check the captcha to prove you're a human"))
                )

        data, errors = self.extractData()
        if errors:
            return

        email = data.get('email')
        account_id, list_id = self.data.newsletter_list.split('-')
        sendinblue = getUtility(ISendinblueAPI)
        try:
            success = sendinblue.subscribe(account_id, list_id, email)
        except SendinblueException as error:
            logger.error("Could not subscribe user %s : %s" % (email,
                                                               str(error)))
            success = False
        if success:
            api.portal.show_message(
                _(u'You are successfully subscribed to the newsletter !'),
                request=self.request,
                type='info',
            )
        else:
            api.portal.show_message(
                _(u'An error occured while triyng to subscribe to the newsletter'),
                request=self.request,
                type='error',
            )
        url = self.request.ACTUAL_URL
        self.request.response.redirect(url)
