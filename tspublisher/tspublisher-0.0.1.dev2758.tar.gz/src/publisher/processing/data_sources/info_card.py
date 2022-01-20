from __future__ import absolute_import, division, print_function, unicode_literals

import os.path

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import YamlObject
import publisher.settings as settings


def get_more_info_data(info_id, code):
    yaml_dir = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, code, "build_assets", "moreInfo", info_id)

    yaml_file = os.path.join(yaml_dir, info_id + ".yml")
    source_asset_dir = os.path.join(yaml_dir, "assets")

    if not os.path.isfile(yaml_file):
        raise ContentMissingError("Yaml infocard not found in {0}".format(yaml_file))

    print("-- Found more info card: %s --" % info_id)
    return read_yaml_data(yaml_file), source_asset_dir


def read_yaml_data(yaml_file):
    yaml = YamlObject()

    with open(yaml_file, "r") as overview_file:
        overview_data = yaml.load(overview_file)
        return overview_data
