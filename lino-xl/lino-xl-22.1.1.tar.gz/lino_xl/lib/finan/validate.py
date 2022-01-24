# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


USAGE = """
Validate a XML file against the XSD for a SEPA payment order.

Usage::

  python -m lino_xl.lib.finan.validate XMLFILE

Arguments:

XMLFILE : the name of the xml file to validate, or '-' to read from stdin


- What is a SEPA Payments Initiation?
  https://www.febelfin.be/sites/default/files/2019-04/standard-credit_transfer-xml-v32-en_0.pdf
- XSD files are from https://www.iso20022.org/catalogue-messages

"""


import sys
from os.path import join, dirname
from lino.utils.xml import validate_xml

def validate_pain001(xmlfile):
    xsdfile = join(dirname(__file__), 'XSD', 'pain.001.001.02.xsd')
    # xsdfile = join(dirname(__file__), 'XSD', 'pain.001.001.03.xsd')
    validate_xml(xmlfile, xsdfile)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(-1)

    validate_pain001(sys.argv[1])
