# coding: utf-8
###########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################

import pkg_resources
import sysconfig


ICON = "../widgets/icons/tomwer.png"

BACKGROUND = "#C0CCFF"


# Entry point for main Orange categories/widgets discovery
def widget_discovery(discovery):
    dist = pkg_resources.get_distribution("tomwer")
    pkgs = [
        "orangecontrib.tomwer.widgets.cluster",
        "orangecontrib.tomwer.widgets.control",
        "orangecontrib.tomwer.widgets.debugtools",
        "orangecontrib.tomwer.widgets.edit",
        "orangecontrib.tomwer.widgets.reconstruction",
        "orangecontrib.tomwer.widgets.visualization",
        "orangecontrib.tomwer.widgets.other",
    ]
    for pkg in pkgs:
        discovery.process_category_package(pkg, distribution=dist)


WIDGET_HELP_PATH = (
    # Used for development.
    # You still need to build help pages using
    # make htmlhelp
    # inside doc folder
    ("/build/sphinx/htmlhelp/index.html", None),
    #
    # Documentation included in wheel
    # Correct DATA_FILES entry is needed in setup.py and documentation has to be built
    # # before the wheel is created.
    ("{}/help/tomwer/index.html".format(sysconfig.get_path("data")), None),
    ("http://www.silx.org/pub/doc/tomwer/htmlhelp/0.9/", None),
)
