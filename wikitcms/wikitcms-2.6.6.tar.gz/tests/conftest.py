# Copyright Red Hat
#
# This file is part of python-wikitcms.
#
# python-wikitcms is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=no-init, protected-access, no-self-use, unused-argument
# pylint: disable=invalid-name

"""Test fixtures, etc."""

from __future__ import unicode_literals
from __future__ import print_function

import json
import os
from unittest import mock

import pytest

DATAPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


@pytest.fixture
def fakemwp(request):
    """Fixture that mocks out mwclient.page.Page.__init__ as long
    as it's active.
    """

    def fakemwpinit(self, site, name, *args, **kwargs):
        """Stub init for mwclient.Page, we can't just mock it out as we
        need to set site and name (and for category generator testing,
        _info, though it can be None).
        """
        self.site = site
        # this is for testing TcmsGeneratorList's capability to handle
        # getting a page by its id
        if name == 80736:
            name = "Test Day:2019-12-09 Kernel 5.4 Test Week"
        self.name = name
        self._info = None

    with mock.patch("mwclient.page.Page.__init__", fakemwpinit):
        yield


@pytest.fixture
def fakeapisections(request):
    """Fixture that mocks out the API to give a response that's
    appropriate for a 'sections' call on a test result page, and
    yields the mock for modifications. Based on the real response for
    Test Results:Fedora 32 Branched 20200322.n.0 Server on 2020-03-25.
    """
    sectpath = os.path.join(
        DATAPATH, "Test_Results:Fedora_32_Branched_20200322.n.0_Server.sections.json"
    )
    with open(sectpath, "r") as sectfh:
        sectjson = json.load(sectfh)
    with mock.patch("wikitcms.wiki.Wiki.api", autospec=True) as fakeapi:
        fakeapi.return_value = {"parse": {"sections": sectjson}}
        yield fakeapi


@pytest.fixture
def fakepages(request):
    """Fixture that mocks out various Page attributes, methods etc.
    with return values read from data files based on the page name.
    The backing files contain real data from the real wiki.
    """

    def faketext(self, section=None, expandtemplates=False, cache=True, slot="main"):
        textpath = os.path.join(DATAPATH, self.name.replace(" ", "_")) + ".txt"
        with open(textpath, "r") as textfh:
            text = textfh.read()
        return text

    @property
    def fakesections(self):
        sectpath = os.path.join(DATAPATH, self.name.replace(" ", "_")) + ".sections.json"
        with open(sectpath, "r") as sectfh:
            sectjson = json.load(sectfh)
        return sectjson

    with mock.patch("mwclient.page.Page.text", faketext):
        with mock.patch("wikitcms.page.Page.sections", fakesections):
            yield


@pytest.fixture
def fakeimages(request):
    """Fixture that mocks out fedfind all_images with an appropriate
    value (from backing data) for the compose. Used when we need an
    event to have authentic image data.
    """

    @property
    def fakeallimages(self):
        imagespath = os.path.join(DATAPATH, self.cid) + ".images.json"
        with open(imagespath, "r") as imagesfh:
            imagesjson = json.load(imagesfh)
        return imagesjson

    with mock.patch("fedfind.release.Release.all_images", fakeallimages):
        yield
