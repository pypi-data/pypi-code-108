# -*- coding: utf-8 -*-
from redturtle.chefcookie import _
from redturtle.chefcookie.defaults import HEADER_LABELS
from redturtle.chefcookie.defaults import GENERAL_LABELS
from redturtle.chefcookie.defaults import TECHNICAL_COOKIES_LABELS
from redturtle.chefcookie.defaults import FUNCTIONAL_COOKIES_LABELS
from redturtle.chefcookie.defaults import IFRAMES_MAPPING
from redturtle.chefcookie.defaults import ANCHOR_MAPPING
from redturtle.chefcookie.defaults import ANALYTICS_COOKIES_LABELS
from redturtle.chefcookie.defaults import PROFILING_COOKIES_LABELS
from redturtle.chefcookie.defaults import PROFILING_COOKIES_SPECIFIC_LABELS
from zope import schema
from zope.interface import Invalid
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

try:
    from plone.supermodel.model import Schema
except ImportError:
    from zope.interface import Interface

    Schema = Interface

import json


def validate_cfg_json(value):
    """check that we have at least valid json and its a dict"""
    try:
        jv = json.loads(value)
    except ValueError as e:
        raise Invalid(
            _(
                "invalid_json",
                "JSON is not valid, parser complained: ${message}",
                mapping={"message": "{msg} {pos}".format(msg=e.msg, pos=e.pos)},
            )
        )
    if not isinstance(jv, dict):
        raise Invalid(_("invalid_cfg_no_dict", "JSON root must be a mapping (dict)"))
    return True


class IRedturtleChefcookieLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IChefCookieSettingsConfigs(Schema):
    analytics_id = schema.TextLine(
        title=_("chefcookie_analytics_id_label", default=u"Analytics Id"),
        description=_(
            "chefcookie_analytics_id_help",
            default=u"If set and the user has accepted the Analytics cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    facebook_id = schema.TextLine(
        title=_("chefcookie_facebook_id_label", default=u"Facebook Id"),
        description=_(
            "chefcookie_facebook_id_help",
            default=u"If set and the user has accepted the Facebook cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    hotjar_id = schema.TextLine(
        title=_("chefcookie_hotjar_id_label", default=u"HotJar Id"),
        description=_(
            "chefcookie_hotjar_id_help",
            default=u"If set and the user has accepted the HotJar cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    linkedin_id = schema.TextLine(
        title=_("chefcookie_linkedin_id_label", default=u"LinkedIn Id"),
        description=_(
            "chefcookie_linkedin_id_help",
            default=u"If set and the user has accepted the LinkedIn cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    only_technical_cookies = schema.Bool(
        title=_(
            "chefcookie_only_technical_cookies_label",
            default=u"Only technical cookies",
        ),
        description=_(
            "chefcookie_only_technical_cookies_help",
            default=u"Select if your website only provide technical cookies.",
        ),
        required=False,
    )

    policy_url = schema.TextLine(
        title=_("chefcookie_policy_url_label", default=u"Policy URL"),
        description=_(
            "chefcookie_policy_url_help",
            default='Insert the cookie policy page URL. This can be used in "Banner header" field as "{policy_url}" to dynamically replace it with the given URL.',
        ),
        required=False,
    )

    iframes_mapping = schema.List(
        title=_("chefcookie_iframes_mapping_labels", default=u"Iframes mapping"),
        description=_(
            "chefcookie_iframes_mapping_labels_help",
            default=u"Insert a list of mappings between a provider and a list of possible domains for their iframes. If the user blocks their cookies, the iframes will be blocked as well.",
        ),
        default=IFRAMES_MAPPING,
        missing_value=[],
        value_type=schema.TextLine(),
        required=False,
    )
    links_mapping = schema.List(
        title=_("chefcookie_links_mapping_labels", default=u"Links mapping "),
        description=_(
            "chefcookie_links_mapping_labels_help",
            default=u"Insert a list of mappings between a provider and a list of possible links xpath selector for their anchor. If the user blocks their cookies, the provider will be blocked as well.",
        ),
        default=ANCHOR_MAPPING,
        missing_value=[],
        value_type=schema.TextLine(),
        required=False,
    )


class IChefCookieSettingsLabels(Schema):
    header_labels = schema.SourceText(
        title=_("chefcookie_header_label", default=u"Banner header"),
        description=_(
            "chefcookie_header_help",
            default=u"Insert the text of the banner header. Once per each site "
            "languages. If you want to insert a link to the policy page, use "
            "the placeholder {policy_url}.",
        ),
        default=HEADER_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    general_labels = schema.SourceText(
        title=_("chefcookie_general_labels", default=u"General labels"),
        description=_(
            "chefcookie_general_labels_help",
            default=u"",
        ),
        default=GENERAL_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    technical_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_technical_cookies_labels",
            default=u"Technical cookies labels",
        ),
        description=_(
            "chefcookie_technical_cookies_labels_help",
            default=u"",
        ),
        default=TECHNICAL_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=False,
    )
    functional_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_functional_cookies_labels",
            default=u"Functional cookies labels",
        ),
        description=_(
            "chefcookie_functional_cookies_labels_help",
            default='If compiled, this will enable the "Functional cookies" flag in the banner.',
        ),
        default=FUNCTIONAL_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=False,
    )

    analytics_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_analytics_cookies_labels",
            default=u"Analytics cookies labels",
        ),
        description=_(
            "chefcookie_analytics_cookies_labels_help",
            default='If compiled, this will enable the "Analytics cookies" flag in the banner.',
        ),
        default=ANALYTICS_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    profiling_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_profiling_cookies_labels",
            default=u"Profiling cookies labels",
        ),
        description=_(
            "chefcookie_profiling_cookies_labels_help",
            default=u"",
        ),
        default=PROFILING_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    profiling_cookies_specific_labels = schema.SourceText(
        title=_(
            "chefcookie_profiling_cookies_specific_labels",
            default=u"Profiling cookies specific labels",
        ),
        description=_(
            "chefcookie_profiling_cookies_specific_labels_help",
            default=u"Labels for specific providers. If the relative id/flag is set, this will enable the flag in the banner.",
        ),
        default=PROFILING_COOKIES_SPECIFIC_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )


class IChefCookieSettings(IChefCookieSettingsConfigs, IChefCookieSettingsLabels):
    """"""
