#!/usr/bin/env python

__all__ = []

import json
import logging
import xml.etree.ElementTree as ET
import json

from .utils import JmmcAPI
from a2p2.ob import etree_to_dict

logger = logging.getLogger(__name__)


#
# first release done for SAMP interoperability with Aspro2
#

def modelsFromXml(xmlmodel):
    """ Returns a python object representing JSON LIKE model(s) from given XML."""
    # read xml models from Aspro2 and convert them to a JSON Model
    e = ET.fromstring(xmlmodel)
    _remove_namespace(e, "http://www.jmmc.fr/jmcs/models/0.1")
    container = etree_to_dict(e)
    modellist=container['model']['model']
    if not isinstance(modellist, list):
        modellist=[modellist]

    models=[]
    for m in modellist:
        model={}
        for p in m['parameter']:
            model[p['type']]=p['value']
        model['name']=m['name']
        model['type']=m['type']
        models.append(model)

    return json.dumps(models)


def _remove_namespace(doc, namespace):
    """Remove namespace in the passed document in place.
    from https://homework.nwsnet.de/releases/45be/"""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]


def _model(models, output_mode=None):
    """ Returns a serialisation of given model(s) to XML by default or another format given to output_mode value (only jsonlike at present time)."""

    # deserialize if models is a string
    if isinstance(models, str):
        models=json.loads(models)

    if output_mode:
        return models
    else :
        return _xml_model(models)

def _xml_model(models):
    """ Rough conversion of dict(s) to xml (Aspro2 namespaces)"""

    if isinstance(models, list):
        modellist=[]
        for m in models:
            modellist.append(_xml_model(m))
        return "".join(modellist)

    model = models # models is now a single element
    modeltype=model["type"]
    modelname=model["name"]

    params=""
    paramNames=[ k for k in model.keys() if not k in ("type", "name")]
    # at present time we must use Aspro2's approach with the same xml namespaces
    # see
    for p in paramNames:
        params+=f"""    <tm:parameter name="{modelname}_{p}" type="{p}"><value>{model[p]}</value></tm:parameter>\n"""

    return f"""<tm:model name="{modelname}" type="{modeltype}">\n{params}</tm:model>\n"""


class Models():
    """ Get analytical model's representations (in sync with Aspro2's ones).
    """
    SAMP_UCD_MODEL="meta.code.class;meta.modelled" # use it for colums that would be filled by models below

# generated code below from an Asprox file that contains a single star with list of all supported models
# cd a2p2/jmmc
# xml sel -o "from .models import _model" -n -n -b -t -m "//tm:model" -o "def " -v "@type" -o "( name, " -m "tm:parameter" -v "@type" -o "=" -v "value" -o ", " -b -o " output_mode=None):" -n -o '    """ ' -v "desc" -o ' """ ' -n -n -o '    return _model({' -m "tm:parameter" -o '"' -v "@type" -o '" : ' -v "@type" -o ", " -b -o '"name":name, "type":"' -v "@type" -o '"}, output_mode)' -n -n models_template.asprox > generated_models.py
# xml sel -t -o "    from .generated_models import " -m "//tm:model" -v "@type" -o ", "  -b -n models_template.asprox
# cd -
    from .generated_models import punct, disk, elong_disk, flatten_disk, circle, ring, elong_ring, flatten_ring, gaussian, elong_gaussian, flatten_gaussian, limb_quadratic
