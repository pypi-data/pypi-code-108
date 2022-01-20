from __future__ import absolute_import, division, print_function, unicode_literals

import os

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import YamlObject
import publisher.settings as settings


def get_organisation_from_channel(channel):
    channel_data = get_data_from_channel(channel)
    return channel_data["name"]


def get_data_from_channel(channel):
    channel = channel.replace("channel-", "")

    channel_file = os.path.join(settings.CHANNELS_INFO_DIR, channel + ".yml")

    if not os.path.exists(channel_file):
        raise ContentMissingError('Yaml file for channel {0} is missing'.format(channel))

    yaml = YamlObject()

    channel_file = open(channel_file, "r")
    channel_data = yaml.load(channel_file)

    return channel_data
