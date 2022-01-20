# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from rer.ufficiostampa.interfaces import IComunicatoStampa

import six


@indexer(IComunicatoStampa)
def arguments(comunicato, **kw):
    arguments = getattr(comunicato, "arguments", [])
    if not arguments:
        return []
    if six.PY2:
        return [x.encode("utf-8") for x in arguments]
    return arguments


@indexer(IComunicatoStampa)
def legislature(comunicato, **kw):
    legislature = getattr(comunicato, "legislature", "")
    if six.PY2:
        return legislature.encode("utf-8")
    return legislature
