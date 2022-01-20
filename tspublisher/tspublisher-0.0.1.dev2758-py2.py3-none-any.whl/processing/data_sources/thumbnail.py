from __future__ import absolute_import, division, print_function, unicode_literals

import os
from shutil import copyfile

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import copy_assets
import publisher.settings as settings


def create_procedure_thumbnails(dest_directory, card_file, icon_file):
    if not card_file:
        card_file = os.path.join(settings.TEMPLATE_DIRECTORY, "card.jpg")

    if not icon_file:
        icon_file = os.path.join(settings.TEMPLATE_DIRECTORY, "icon.jpg")

    copyfile(card_file, os.path.join(dest_directory, "card.jpg"))
    copyfile(icon_file, os.path.join(dest_directory, "icon.jpg"))


def create_phase_thumbnail(dest_directory, icon_file):
    if not icon_file:
        icon_file = os.path.join(settings.TEMPLATE_DIRECTORY, "icon.jpg")

    copyfile(icon_file, os.path.join(dest_directory, "icon.jpg"))


def update_thumbnails(procedure, asset_directory):
    print("-- Getting updated icon for procedure --")
    source_asset_dir = _get_thumbnail(procedure.code, procedure.vbs)
    copy_assets(source_asset_dir, asset_directory)


def update_phase_thumbnails(phase, asset_directory):
    phase_icon = os.path.join(asset_directory, "icon.jpg")

    print("-- Getting updated icon for phase --")
    thumbnail_directory = _get_thumbnail(phase.code, phase.vbs)
    thumbnail = os.path.join(thumbnail_directory, "icon.jpg")
    copyfile(thumbnail, phase_icon)


def _get_thumbnail(item_code, vbs=False):
    if not vbs:
        thumbnail_dir = os.path.join(settings.CG_APP5_ROOT, item_code, "thumbnails")
    else:
        thumbnail_dir = os.path.join(settings.VBS_ROOT, item_code, "thumbnails")

    if not os.path.isdir(thumbnail_dir):
        raise ContentMissingError('Expected {} to exist for {}'.format(thumbnail_dir, item_code))

    return thumbnail_dir
