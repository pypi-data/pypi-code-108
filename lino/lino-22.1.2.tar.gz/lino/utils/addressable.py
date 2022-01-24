# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""See :doc:`/utils/addressable`.

"""

from etgen.html import E, lines2p, tostring


class Addressable(object):
    """
    General mixin (not only for Django models) to encapsulate the
    generating of "traditional" ("snail") mail addresses.

    Usable subclasses must implement at least
    :meth:`address_person_lines` and :meth:`address_location_lines`.
    """

    def address_person_lines(self):
        """Yield one or more text lines, one for each line
        of the person part.

        """
        raise NotImplementedError()

    def address_location_lines(self):
        """Yield one or more text lines, one for each line
        of the location part.

        """
        raise NotImplementedError()

    def get_address_lines(self):
        """Yield a series of text lines, one for each line of the address."""
        for ln in self.address_person_lines():
            yield ln
        for ln in self.address_location_lines():
            yield ln

    def get_address(self, linesep="\n"):
        """The plain text full postal address (person and location).  Lines
        are separated by `linesep`, which defaults to a newline.
        """
        return linesep.join(
            list(self.address_person_lines())
            + list(self.address_location_lines()))
    address = property(get_address)

    def get_address_html(self, *args, **kwargs):
        """Return the full postal address as a text containing simple html
        markup with a single paragraph (``<p>``).

        """
        lines = list(self.get_address_lines())
        return tostring(lines2p(lines, **kwargs))

    address_html = property(get_address_html)

    def has_address(self):
        """
        Checks whether the address is non empty and returns a boolean value.
        """
        return len(list(self.address_location_lines())) > 0


class TestAddress(Addressable):
    """Used only for testing."""
    def __init__(self, *lines):
        self.lines = lines

    def address_person_lines(self):
        return []

    def address_location_lines(self):
        return self.lines
