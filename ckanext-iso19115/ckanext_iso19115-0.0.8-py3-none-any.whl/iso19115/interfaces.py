from __future__ import annotations

import ckan.plugins as p

import ckanext.iso19115.converter as c


class IIso19115(p.Interface):
    def iso19115_metadata_converter(self, data_dict) -> c.Converter:
        return c.Converter(data_dict)
