from __future__ import absolute_import, division, print_function, unicode_literals

import os

import shutil

import publisher.settings as settings


def copy_eula_to_procedure(procedure_code, asset_directory):
    eula_file_name = "{0}_eula".format(procedure_code)

    source_file_path = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, procedure_code, "build_assets", "eula",
                                    "eula.txt")

    dest_file_path = os.path.join(asset_directory, eula_file_name + ".txt")

    if os.path.isfile(source_file_path):
        print("-- Found eula for procedure: %s --" % source_file_path)
        shutil.copyfile(source_file_path, dest_file_path)
        return eula_file_name

    return ""
