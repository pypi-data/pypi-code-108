#!/usr/bin/env python

__all__ = []

import logging
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple, OrderedDict

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary-in-python
# see comment below for our custom mods on attributes naming
def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        # print("add d=%s"%str(d))
    if t.attrib:
        d[t.tag].update(('' + k, v)
                        for k, v in t.attrib.items())  # was '@' but can't be serialized by namedtuple
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


class OB():
    """
    Give access to OBs sent by Aspro2 and provide some helper functions.
    You can use attributes to walk to associated configurations values, e.g.:
    - ob.interferometerConfiguration.name
    - ob.instrumentConfiguration
    - ob.observationConfiguration[]
    - ob.observationSchedule

    every values are string (must be converted for numeric values).

    """

    def __init__(self, url):
        # extract XML in elementTree

        e = ET.parse(url)
        d = etree_to_dict(e.getroot())
        # keep only content of subelement to avoid schema version change
        # '{http://www.jmmc.fr/aspro-ob/0.1}observingBlockDefinition'
        ds = d[list(d)[0]]  # -> version and name are lost
        # store attributes
        for e in ds.keys():
            # parse JSON into an object with attributes corresponding to dict keys.
            # We should probably avoid json use...
            o = json.loads(
                json.dumps(ds[e]), object_hook=lambda d: namedtuple(e, d.keys())(*d.values()))
            # observationConfiguration may be uniq but force it to be a list
            if "observationConfiguration" in e and not isinstance(o, list):
                setattr(self, e, [o])
            else:
                setattr(self, e, o)
        self.ds = ds

    def getFluxes(self, target):
        """
        Return a flux mesurements as dict (ordered dict by BVRIJHK ).
        """
        order = "BVRIJHK"
        fluxes = {}
        els = target._asdict()
        for k in els.keys():
            if k.startswith("FLUX_"):
                fluxes[k[5:]] = els[k]  # remove FLUX_ prefix for dict key

        return OrderedDict(sorted(fluxes.items(), key=lambda t: order.find(t[0])))

    def get(self, obj, fieldname, defaultvalue=None):
        if fieldname in obj._fields:
            return getattr(obj, fieldname)
        else:
            return defaultvalue

    def __str__(self):
        if True:
            import json
            return json.dumps(self.ds, indent=2)
        else:
            return str(self.ds)
