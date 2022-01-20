# -*- coding: utf-8 -*-
from datetime import datetime
from email.utils import formataddr
from itsdangerous.exc import SignatureExpired, BadSignature
from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone.api.exc import InvalidParameterError
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces.store import ISubscriptionsStore
from zope.component import getUtility
from zope.globalrequest import getRequest

try:
    # rer.agidtheme overrides site tile field
    from rer.agidtheme.base.interfaces import IRERSiteSchema as ISiteSchema
    from rer.agidtheme.base.utility.interfaces import ICustomFields

    RER_THEME = True
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema

    RER_THEME = False

import json
import logging
import six
import premailer

logger = logging.getLogger(__name__)


def defaultLegislature():
    try:
        legislatures = json.loads(
            api.portal.get_registry_record(
                "legislatures", interface=IRerUfficiostampaSettings
            )
        )
    except (KeyError, InvalidParameterError, TypeError) as e:
        logger.exception(e)
        return u""

    if not legislatures:
        return u""
    current = legislatures[-1]
    return current.get("legislature", "")


def get_site_title():
    registry = getUtility(IRegistry)
    site_settings = registry.forInterface(
        ISiteSchema, prefix="plone", check=False
    )
    site_title = getattr(site_settings, "site_title") or ""
    if RER_THEME:
        site_subtitle_style = (
            getattr(site_settings, "site_subtitle_style") or ""
        )
        fields_value = getUtility(ICustomFields)
        site_title = fields_value.titleLang(site_title)
        site_subtitle = fields_value.subtitleLang(
            getattr(site_settings, "site_subtitle") or "{}"
        )
        if site_subtitle and site_subtitle_style == "subtitle-normal":
            site_title += " {}".format(site_subtitle)

    if six.PY2:
        site_title = site_title.decode("utf-8")
    return site_title


def decode_token():
    request = getRequest()
    secret = request.form.get("secret", "")
    if not secret:
        return {
            "error": _(
                "unsubscribe_confirm_secret_null",
                default=u"Unable to manage subscriptions. Token not present.",  # noqa
            )
        }
    try:
        token_secret = api.portal.get_registry_record(
            "token_secret", interface=IRerUfficiostampaSettings
        )
        token_salt = api.portal.get_registry_record(
            "token_salt", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        return {
            "error": _(
                "unsubscribe_confirm_secret_token_settings_error",
                default=u"Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    if not token_secret or not token_salt:
        return {
            "error": _(
                "unsubscribe_confirm_secret_token_settings_error",
                default=u"Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    serializer = URLSafeTimedSerializer(token_secret, token_salt)
    try:
        data = serializer.loads(secret, max_age=86400)
    except SignatureExpired:
        return {
            "error": _(
                "unsubscribe_confirm_secret_expired",
                default=u"Unable to manage subscriptions. Token expired.",
            )
        }
    except BadSignature:
        return {
            "error": _(
                "unsubscribe_confirm_secret_invalid",
                default=u"Unable to manage subscriptions. Invalid token.",
            )
        }
    record_id = data.get("id", "")
    email = data.get("email", "")
    if not record_id or not email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_parameters",
                default=u"Unable to manage subscriptions. Invalid parameters.",
            )
        }
    tool = getUtility(ISubscriptionsStore)
    record = tool.get_record(record_id)
    if not record:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_id",
                default=u"Unable to manage subscriptions. Invalid id.",
            )
        }
    if record.attrs.get("email", "") != email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_email",
                default=u"Unable to manage subscriptions. Invalid email.",
            )
        }
    return {"data": record}


def prepare_email_message(context, template, parameters):
    mail_template = context.restrictedTraverse(template)
    try:
        css = api.portal.get_registry_record(
            "css_styles", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        css = ""
    if css:
        parameters["css"] = css
    html = mail_template(**parameters)
    # convert it
    html = premailer.transform(html)

    try:
        frontend_url = api.portal.get_registry_record(
            "frontend_url", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        frontend_url = ""

    if frontend_url:
        source_link = api.portal.get().absolute_url()
        html = html.replace(source_link, frontend_url)
    return html


def mail_from():
    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix="plone")
    return formataddr(
        (mail_settings.email_from_name, mail_settings.email_from_address)
    )


def get_next_comunicato_number():
    comunicato_year = api.portal.get_registry_record(
        "comunicato_year", interface=IRerUfficiostampaSettings
    )
    comunicato_number = api.portal.get_registry_record(
        "comunicato_number", interface=IRerUfficiostampaSettings
    )
    current_year = datetime.now().year

    if comunicato_year < current_year:
        # first comunicato of new year
        comunicato_year = current_year
        comunicato_number = 1
        # update value
        api.portal.set_registry_record(
            "comunicato_year",
            current_year,
            interface=IRerUfficiostampaSettings,
        )
        api.portal.set_registry_record(
            "comunicato_number",
            comunicato_number,
            interface=IRerUfficiostampaSettings,
        )
    else:
        comunicato_number += 1
        # update value
        api.portal.set_registry_record(
            "comunicato_number",
            comunicato_number,
            interface=IRerUfficiostampaSettings,
        )

    return "{}/{}".format(comunicato_number, comunicato_year)
