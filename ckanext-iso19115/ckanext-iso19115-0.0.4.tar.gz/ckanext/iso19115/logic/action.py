from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.iso19115.converter as c
from ckanext.iso19115.interfaces import IIso19115

if TYPE_CHECKING:
    import ckanext.iso19115.types as t


def get_actions():
    return {
        "iso19115_package_show": package_show,
    }


def package_show(context, data_dict):
    implementations = iter(p.PluginImplementations(IIso19115))
    conv: c.Converter = next(implementations).iso19115_metadata_converter(
        data_dict
    )

    pkg = tk.get_action("package_show")(context, data_dict)
    conv.initialize(pkg)
    conv.process()
    conv.finalize()

    result = conv.build()

    return result
