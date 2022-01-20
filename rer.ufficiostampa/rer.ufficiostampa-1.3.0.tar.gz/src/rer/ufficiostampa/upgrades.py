# -*- coding: utf-8 -*-
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from plone import api

import logging

logger = logging.getLogger(__name__)


def to_1100(context):
    tool = getUtility(ISubscriptionsStore)
    subscription_channels = api.portal.get_registry_record(
        "subscription_channels", interface=IRerUfficiostampaSettings,
    )
    for record in tool.search():
        channels = []
        updated = False
        for channel in record._attrs.get("channels", []):
            channel = channel.strip()
            if channel not in subscription_channels:
                updated = True
                continue
            if channel in channels:
                updated = True
                continue
            channels.append(channel)

        if updated:
            logger.info(
                "{}: {} => {}".format(
                    record._attrs["email"], record._attrs["channels"], channels
                )
            )

            record._attrs["channels"] = channels
            tool.soup.reindex(records=[record])
