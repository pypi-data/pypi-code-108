# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from cpskin.locales import CPSkinMessageFactory as _
from interfaces import ISendToManagerForm
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from plone.z3cform import layout
from Products.CMFPlone.utils import pretty_title_or_id
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.interfaces import IMailHost
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import WidgetActionExecutionError
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.component import getUtility

from zope.interface import Invalid


import logging

logger = logging.getLogger("Plone")


class SendToManagerForm(form.Form):
    label = _(
        u"report_error_to_site_manager", default=u"Report an error to the site manager"
    )

    description = _(
        u"provide_maximum_informations",
        default=u"Merci de fournir le maximum d'information ainsi que tout renseignement qui permette de la valider (source).",
    )

    fields = field.Fields(ISendToManagerForm)
    fields["captcha"].widgetFactory = ReCaptchaFieldWidget
    ignoreContext = True

    mail_template = ViewPageTemplateFile("templates/sendtomanager_mail_template.pt")

    @button.buttonAndHandler(_(u"label_send", default="Send"), name="send")
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).addStatusMessage(
                self.formErrorsMessage, type=u"error"
            )
            return

        portal_state = getMultiAdapter(
            (self.context, self.request), name=u"plone_portal_state"
        )
        site = portal_state.portal()

        send_from_address = data.get("send_from_address")
        send_to_address = site.getProperty("email_from_address", None)
        subject = _(u"error_reported", default=u"Error reported")
        title = pretty_title_or_id(self, self.context)
        description = self.context.Description()
        comment = data.get("comment", None)

        captcha = getMultiAdapter(
            (aq_inner(self.context), self.request), name="recaptcha"
        )
        if not captcha.verify():
            raise WidgetActionExecutionError(
                "captcha",
                Invalid(_(u"Please check the captcha to prove you're a human")),
            )

        try:
            # Sends a link of a page to someone.
            host = getUtility(IMailHost)
            encoding = site.getProperty("email_charset")

            # Cook from template
            message = self.mail_template(
                self,
                send_to_address=send_to_address,
                send_from_address=send_from_address,
                comment=comment,
                subject=subject,
                title=title,
                description=description,
            )

            message = message.encode(encoding)

            host.send(
                message,
                mto=send_to_address,
                mfrom=send_from_address,
                subject=subject,
                charset="utf-8",
            )

        except ConflictError:
            raise
        except Exception as e:
            # TODO To many things could possibly go wrong. So we catch all.
            logger.info("Unable to send mail: " + str(e))
            IStatusMessage(self.request).addStatusMessage(
                _(u"Unable to send mail."), type=u"error"
            )
            return

        IStatusMessage(self.request).addStatusMessage(_(u"Mail sent."), type=u"info")

        self.request.response.redirect(self.context.absolute_url())
        return ""


send_to_form = layout.wrap_form(SendToManagerForm)
