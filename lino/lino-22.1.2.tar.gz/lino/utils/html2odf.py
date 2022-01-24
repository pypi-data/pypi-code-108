# -*- coding: UTF-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""This module contains mainly a utility function :func:`html2odf`
which converts an ElementTree object generated using
:mod:`etgen.html` to a fragment of ODF.

.. This is part of the Lino test suite. To test it individually, run:

    $ python lino/utils/html2odf.py

This is not trivial. The challenge is that HTML and ODF are quite
different document representations. But something like this seems
necessary. Lino uses it in order to generate .odt documents which
contain (among other) chunks of html that have been entered using
TinyMCE and stored in database fields.

TODO: is there really no existing library for this task? I saw
approaches which call libreoffice in headless mode to do the
conversion, but this sounds inappropriate for our situation where we
must glue together fragments from different sources. Also note that we
use :mod:`appy.pod` to do the actual generation.

More about the usage of this module is in :doc:`/topics/formatting`.

"""

# from future import standard_library
# standard_library.install_aliases()

import logging
logger = logging.getLogger(__name__)

from io import StringIO
from lxml import etree
from etgen.html import E, tostring

def toxml(node):
    """Convert an ODF node to a string with its XML representation."""
    buf = StringIO()
    node.toXml(0, buf)
    return buf.getvalue()


from odf import text


#~ PTAGS = ('p','td','li')
PTAGS = ('p', 'td', 'div', 'table', 'tr')


def html2odf(e, ct=None, **ctargs):
    """
    Convert a :mod:`etgen.html` element to an ODF text element.
    Most formats are not implemented.
    There's probably a better way to do this...

    :ct: the root element ("container"). If not specified, we create one.

    """
    sections_counter = 1
    #~ print "20120613 html2odf()", e.tag, e.text
    if ct is None:
        ct = text.P(**ctargs)
        #~ if e.tag in PTAGS:
            #~ oe = text.P(**ctargs)
        #~ else:
            #~ oe = text.P(**ctargs)
            #~ logger.info("20130201 %s", tostring(e))
            #~ raise NotImplementedError("<%s> without container" % e.tag)
    if isinstance(e, str):
        ct.addText(e)
        #~ oe = text.Span()
        #~ oe.addText(e)
        #~ yield oe
        return ct

    if e.tag == 'ul':
        ct = text.List(stylename='podBulletedList')
        ctargs = dict(stylename='podBulletItem')
        #~ ctargs = dict()

    text_container = None

    if e.tag in ('b', 'strong'):
        #~ oe = text.Span(stylename='Bold Text')
        oe = text.Span(stylename='Strong Emphasis')
    elif e.tag == 'a':
        oe = text.Span(stylename='Strong Emphasis')
        #~ oe = text.Span(stylename='Bold Text')
    elif e.tag in ('i', 'em'):
        oe = text.Span(stylename='Emphasis')
    elif e.tag == 'span':
        oe = text.Span()
    elif e.tag == 'br':
        oe = text.LineBreak()

    elif e.tag == 'h1':
        """
        <text:h text:style-name="Heading_20_1" text:outline-level="1">
        """
        oe = ct = text.H(stylename="Heading 1", outlinelevel=1)
    elif e.tag == 'h2':
        oe = ct = text.H(stylename="Heading 2", outlinelevel=2)
    elif e.tag == 'h3':
        oe = ct = text.H(stylename="Heading 3", outlinelevel=3)
    elif e.tag == 'div':
        oe = ct = text.Section(name="S" + str(sections_counter))

    elif e.tag == 'img':
        return  # ignore images
    elif e.tag == 'ul':
        oe = ct
    #~ elif e.tag in ('ul','ol'):
        #~ oe = text.List(stylename=e.tag.upper())
        #~ ctargs = dict(stylename=e.tag.upper()+"_P")
    elif e.tag == 'li':
        #~ oe = ct
        oe = text.ListItem()
        text_container = text.P(**ctargs)
        oe.appendChild(text_container)

    elif e.tag in PTAGS:
        oe = ct
        #~ if ct.tagName == 'p':
            #~ oe = ct
        #~ else:
            #~ oe = text.P(**ctargs)
    else:
        logger.info("20130201 %s", tostring(e))
        raise NotImplementedError("<%s> inside <%s>" % (e.tag, ct.tagName))
        #~ oe = text.Span()

    if text_container is None:
        text_container = oe
    if e.text:
        text_container.addText(e.text)
    for child in e:
        #~ html2odf(child,oe)
        html2odf(child, text_container, **ctargs)
        #~ for oc in html2odf(child,oe):
            # ~ # oe.addElement(oc)
            #~ oe.appendChild(oc)
    #~ if not True:
        #~ if e.tail:
            #~ oe.addText(e.tail)
    if oe is not ct:
        ct.appendChild(oe)
        #~ yield oe
    #~ if True:
    if e.tail:
        #~ yield e.tail
        #~ yield text.Span(text=e.tail)
        #~ yield Text(e.tail)
        ct.addText(e.tail)
    return ct


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
