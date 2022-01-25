# -*- coding: utf-8 -*-

from collective.privacy.browser.consent import ConsentForm
from cpskin.locales import CPSkinMessageFactory as _
from plone import api
from Products.Five import BrowserView
from z3c.form import button
from zope.i18n import translate

import json


def get_all_consent_reasons(privacy_tool):
    for reason in privacy_tool.getAllReasons().values():
        if reason.lawful_basis.__name__ == "consent":
            yield reason


class PrivacyView(BrowserView):
    """ """

    def allow_iframes(self):
        self.request.response.setHeader("Content-type", "application/json")
        portal_privacy = api.portal.get_tool("portal_privacy")
        return json.dumps(portal_privacy.processingIsAllowed("show_genetic_embed"))

    def allow_languages(self):
        self.request.response.setHeader("Content-type", "application/json")
        portal_privacy = api.portal.get_tool("portal_privacy")
        return json.dumps(portal_privacy.processingIsAllowed("language_preference"))

    def accept_or_refuse_all(self):
        form = self.request.form
        came_from = form.get("came_from")
        if not came_from:
            came_from = api.portal.get_navigation_root(self.context).absolute_url()
        accept_all = True if "consent" in form else False
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            if accept_all:
                privacy_tool.consentToProcessing(reason.__name__)
            else:
                privacy_tool.objectToProcessing(reason.__name__)
        self.request.response.redirect(came_from)
        return ""


class ConsentFormWithPolicy(ConsentForm):

    label = _(u"Cookies choice")
    id = "cookies-form"

    def update(self):
        super(ConsentFormWithPolicy, self).update()
        root = api.portal.get_navigation_root(self.context)
        current_lang = api.portal.get_current_language()[:2]
        policy_url = u"{}/@@cookies-view".format(root.absolute_url())
        description = _(
            u"Choose to opt in or out of cookies use.<br/>"
            u'Our <a href="${policy_url}">cookies policy</a> can help you choose.',
            mapping={u"policy_url": policy_url},
        )
        self.description = translate(description, target_language=current_lang)

    def _redirect(self):
        if "ajax_load" in self.request.form:
            # the form was loaded via an overlay, we need to redirect to
            # an existing page to close it
            portal = api.portal.get()
            self.request.response.redirect("{}/@@ok".format(portal.absolute_url()))
            return ""

    @button.buttonAndHandler(_(u"Save my choices"))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        privacy_tool = self.context.portal_privacy
        for topic, answer in data.items():
            answer = answer == "Allowed"
            if answer:
                privacy_tool.consentToProcessing(topic)
            else:
                privacy_tool.objectToProcessing(topic)
        self.status = _(u"Your preferences have been saved.")
        self._redirect()

    @button.buttonAndHandler(_(u"Accept all"))
    def handleAcceptAll(self, action):
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            privacy_tool.consentToProcessing(reason.__name__)
        self._redirect()

    @button.buttonAndHandler(_(u"Refuse all"))
    def handleRefuseAll(self, action):
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            privacy_tool.objectToProcessing(reason.__name__)
        self._redirect()
