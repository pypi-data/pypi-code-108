# -*- coding: utf-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# How to test this document:
#
#  $ python setup.py test -s tests.UtilsTests.test_tidy

r"""Defines the :func:`html2xhtml` function which converts HTML to
valid XHTML.

It uses Jason Stitt's `pytidylib
<http://countergram.com/open-source/pytidylib/docs/index.html>`__
module. This module requires the `HTML Tidy library
<http://tidy.sourceforge.net/>`__ to be installed on the system::

    $ sudo apt-get install tidy

Some examples in :doc:`/topics/formatting`.

"""

# from __future__ import print_function, unicode_literals

WRAP_BEFORE = """\
<html>
<head>
<title></title>
</head>
<body>
"""

try:

    from tidylib import tidy_fragment

    # http://tidy.sourceforge.net/docs/quickref.html

    def html2xhtml(html, **options):
        options.update(doctype='omit')
        options.update(show_warnings=0)
        options.update(indent=0)
        # options.update(output_xml=1)
        options.update(output_xhtml=1)
        document, errors = tidy_fragment(html, options=options)
        if False:  # errors:
            # LS 20190905 disabled error checking, see my blog
            #~ raise Exception(repr(errors))
            raise Exception("Errors while processing %s\n==========\n%s" %
                            (html, errors))
        # if document.startswith(WRAP_BEFORE):
        #     document = document[len(WRAP_BEFORE):]
        #     document = document[:-15]
        return document.strip()

    HAS_TIDYLIB = True

except OSError:
    # happens on readthedocs.org and Travis CI: OSError: Could not
    # load libtidy using any of these names:
    # libtidy,libtidy.so,libtidy-0.99.so.0,cygtidy-0-99-0,tidylib,
    # libtidy.dylib,tidy

    # We can simply ignore it since it is just for building the docs.
    from lino.utils.mytidylib import html2xhtml
    # TODO: emulate it well enough so that at least the test suite passes

    HAS_TIDYLIB = False


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
