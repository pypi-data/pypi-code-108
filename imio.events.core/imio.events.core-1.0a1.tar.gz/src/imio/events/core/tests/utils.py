# -*- coding: utf-8 -*-

import os


def get_leadimage_filename():
    leadimage = os.path.join(
        os.path.dirname(__file__),
        "resources/plone.png",
    )
    return leadimage
