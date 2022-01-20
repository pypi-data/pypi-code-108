# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from plone.supermodel import model
from rer.ufficiostampa import _
from zope import schema


class IRerUfficiostampaSettings(model.Schema):
    legislatures = schema.SourceText(
        title=_("legislatures_label", default=u"List of legislatures",),
        description=_(
            "legislatures_help",
            default=u"This is a list of all legislatures. The last one is the"
            u" one used to fill fields in a new Comunicato.",
        ),
        required=True,
    )

    subscription_channels = schema.List(
        title=_(
            u"subscription_channels_label", default=u"Subscription Channels"
        ),
        description=_(
            u"subscription_channels_description",
            default=u"List of available subscription channels."
            u"One per line."
            u"These channels will be used for users subscriptions "
            u"and for select to which channel send a Comunicato.",
        ),
        required=True,
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
    )

    token_secret = schema.TextLine(
        title=_("token_secret_label", default=u"Token secret"),
        description=_(
            "token_secret_help",
            default=u"Insert the secret key for token generation.",
        ),
        required=True,
    )
    token_salt = schema.TextLine(
        title=_("token_salt_label", default=u"Token salt"),
        description=_(
            "token_salt_help",
            default=u"Insert the salt for token generation. This, in "
            u"conjunction with the secret, will generate unique tokens for "
            u"subscriptions management links.",
        ),
        required=True,
    )

    frontend_url = schema.TextLine(
        title=_("frontend_url_label", default=u"Frontend URL"),
        description=_(
            "frontend_url_help",
            default=u"If the frontend site is published with a different URL "
            u"than the backend, insert it here. All links in emails will be "
            u"converted with that URL.",
        ),
        required=False,
    )
    external_sender_url = schema.TextLine(
        title=_("external_sender_url_label", default=u"External sender URL"),
        description=_(
            "external_sender_url_help",
            default=u"If you want to send emails with an external tool "
            u"(rer.newsletterdispatcher.flask), insert the url of the service "
            u"here. If empty, all emails will be sent from Plone.",
        ),
        required=False,
    )

    css_styles = schema.SourceText(
        title=_("css_styles_label", default=u"Styles",),
        description=_(
            "css_styles_help",
            default=u"Insert a list of CSS styles for received emails.",
        ),
        required=True,
    )
    comunicato_number = schema.Int(
        title=_("comunicato_number_label", default=u"Comunicato number",),
        description=_(
            "comunicato_number_help",
            default=u"The number of last sent Comunicato. You don't have to "
            "edit this. It's automatically updated when a Comunicato is published.",  # noqa
        ),
        required=True,
        default=0,
    )
    comunicato_year = schema.Int(
        title=_("comunicato_year_label", default=u"Comunicato year",),
        description=_(
            "comunicato_year_help",
            default=u"You don't have to edit this. It's automatically updated"
            u" on every new year.",
        ),
        required=True,
        default=2021,
    )


class ILegislaturesRowSchema(model.Schema):
    legislature = schema.SourceText(
        title=_("legislature_label", default=u"Legislature",),
        description=_(
            "legislature_help", default=u"Insert the legislature name.",
        ),
        required=True,
    )
    arguments = schema.List(
        title=_("legislature_arguments_label", default=u"Arguments",),
        description=_(
            "legislature_arguments_help",
            default=u"Insert a list of arguments related to this legislature."
            u" One per line.",
        ),
        required=True,
        value_type=schema.TextLine(),
    )
