from __future__ import absolute_import, division, print_function, unicode_literals

import os

from publisher.processing.data_sources.utils import YamlObject, copy_assets
import publisher.settings as settings


def get_overview_and_devices(code, asset_directory):
    yaml_overview_dir = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, code, "build_assets", "overview")
    yaml_devices_dir = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, code, "build_assets", "devices")

    yaml_overview_file = os.path.join(yaml_overview_dir, "overview.yml")
    yaml_overview_asset_dir = os.path.join(yaml_overview_dir, "assets")

    yaml_devices_file = os.path.join(yaml_devices_dir, "devices.yml")
    yaml_devices_asset_dir = os.path.join(yaml_devices_dir, "assets")

    # Overview
    if os.path.isfile(yaml_overview_file):
        print("-- Found overview yaml file: %s --" % yaml_overview_file)
        overview_data = read_yaml_data(yaml_overview_file)
    else:
        overview_data = []

    # Key Instruments
    if os.path.isfile(yaml_devices_file):
        print("-- Found devices yaml file: %s --" % yaml_devices_file)
        devices_data = read_yaml_data(yaml_devices_file)
        copy_assets(yaml_devices_asset_dir, asset_directory)
    else:
        devices_data = []

    copy_assets(yaml_overview_asset_dir, asset_directory)

    return overview_data, devices_data


def read_yaml_data(overview_file):
    yaml = YamlObject()

    with open(overview_file, "r") as overview_file:
        overview_data = yaml.load(overview_file)
        return overview_data
