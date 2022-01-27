# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2020 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

__all__ = '''
assert_xml_elements_equal
check_xml_elements_equal
HAS_AVM
test_path
'''.split()

import os.path


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

def test_path(*pieces):
    return os.path.join(TESTS_DIR, *pieces)


try:
    import pyavm
    HAS_AVM = True
except ImportError:
    HAS_AVM = False

def check_xml_elements_equal(observed, expected):
    """See if two XML elements are equal through recursive comparison. We do *not*
    check the "tail" text item, and we strip whitespace in "text".

    Derived om `StackExchange <https://stackoverflow.com/a/24349916/3760486>`_.

    """
    if observed.tag != expected.tag:
        return 'expected tag {}, observed tag {}'.format(expected.tag, observed.tag)

    if observed.text is None:
        otext = ''
    else:
        otext = observed.text.strip()

    if expected.text is None:
        etext = ''
    else:
        etext = expected.text.strip()

    if otext != etext:
        return 'expected text {!r} in tag {}, observed {!r}'.format(etext, expected.tag, otext)
    if observed.attrib != expected.attrib:
        return 'expected attrs {!r} in tag {}, observed {!r}'.format(expected.attrib, expected.tag, observed.attrib)
    if len(observed) != len(expected):
        return 'expected {} children of in tag {}, observed {}'.format(len(expected), expected.tag, len(observed))

    for c1, c2 in zip(observed, expected):
        reason = check_xml_elements_equal(c1, c2)
        if reason is not None:
            return reason

    return None

def assert_xml_elements_equal(observed, expected):
    reason = check_xml_elements_equal(observed, expected)
    if reason is not None:
        raise Exception('unequal XML elements: {}'.format(reason))
