# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.app.textfield import RichText
from plone.autoform.widgets import ParameterizedWidget
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from plone.z3cform.interfaces import IWrappedForm
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from z3c.form.interfaces import IFormLayer
from zope import schema
from zope.component import getUtility

from zope.interface import alsoProvides
from zope.interface import implementer
import logging

from collective.sendinblue import _
from collective.sendinblue.interfaces import INewsletterRedirectionSubscribe
from collective.sendinblue.interfaces import ISendinblueAPI


logger = logging.getLogger("collective.sendinblue")


class IRedirectionSendinbluePortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True,
    )

    description = schema.TextLine(
        title=_(u"Portlet description"),
        description=_(u"Description of the rendered portlet"),
        required=False,
    )

    url = schema.TextLine(
        title=_(u"Base url to redirect to"),
        description=_(u"Base url of the registration form to redirect to"),
        required=True,
    )

    text = RichText(
        title=_(u"Text"),
        description=_(u"Others informations and descriptions"),
        required=False,
    )


@implementer(IRedirectionSendinbluePortlet)
class Assignment(base.Assignment):
    def __init__(self, header=u"", description=u"", text=u"", url=u""):
        self.header = header
        self.description = description

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile("redirection_portlet.pt")
    form = None

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

    def header(self):
        return self.data.header

    def description(self):
        return self.data.description

    def text(self):
        return self.data.text.output if self.data.text else ""

    def url(self):
        return self.data.url

    def update(self):
        super(Renderer, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = PortletSubscribeForm(
            aq_inner(self.context), self.request, self.data
        )
        alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):

    schema = IRedirectionSendinbluePortlet

    label = _(u"Add redirect Sendinblue Portlet")
    description = _(
        u"This portlet displays a redirect form to a Sendinblue list subscribe form."
    )

    def update(self):
        sendinblue = getUtility(ISendinblueAPI)
        sendinblue.updateCache()
        super(AddForm, self).update()

    def create(self, data):
        return Assignment(
            header=data.get("header", u""),
            description=data.get("description", u""),
            text=data.get("text", u""),
            url=data.get("url", u""),
        )


class EditForm(base.EditForm):

    schema = IRedirectionSendinbluePortlet

    label = _(u"Edit redirect Sendinblue Portlet")
    description = _(
        u"This portlet displays a redirect form to a Sendinblue list subscribe form."
    )

    def update(self):
        sendinblue = getUtility(ISendinblueAPI)
        sendinblue.updateCache()
        super(EditForm, self).update()


class PortletSubscribeForm(Form):
    fields = field.Fields(INewsletterRedirectionSubscribe)
    ignoreContext = True
    fields["email"].widgetFactory = ParameterizedWidget(
        None,
        placeholder=_(u"Email address"),
    )

    def __init__(self, context, request, data=None):
        super(PortletSubscribeForm, self).__init__(context, request)
        self.data = data

    @button.buttonAndHandler(_("Subscribe"), name="subscribe")
    def handle_subscribe(self, action):
        data, errors = self.extractData()
        if errors:
            return

        email = data.get("email")
        url = self.data.url
        self.request.response.redirect("{}{}".format(url, email))
