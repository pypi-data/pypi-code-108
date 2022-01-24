# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lxml import etree

def validate_xml(xmlfile, xsdfile):
    # doc = etree.parse(open(xmlfile))
    doc = etree.parse(xmlfile)
    # xsd = etree.XMLSchema(etree.parse(open(xsdfile)))
    xsd = etree.XMLSchema(etree.parse(xsdfile))
    xsd.assertValid(doc)
