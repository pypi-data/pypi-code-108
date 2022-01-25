# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
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
# ###########################################################################*/
"""Set of icons for buttons.

Use :func:`getQIcon` to create Qt QIcon from the name identifying an icon.
"""

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "06/09/2017"


import os
import logging
import weakref
from silx.gui import qt
import tomwer.resources


_logger = logging.getLogger(__name__)
"""Module logger"""


_cached_icons = weakref.WeakValueDictionary()
"""Cache loaded icons in a weak structure"""


_supported_formats = None
"""Order of file format extension to check"""


def getQIcon(name):
    """Create a QIcon from its name.

    The resource name can be prefixed by the name of a resource directory. For
    example "silx:foo.png" identify the resource "foo.png" from the resource
    directory "silx".

    If no prefix are specified, the file with be returned from the silx
    resource directory with a specific path "gui/icons".

    See also :func:`silx.resources.register_resource_directory`.

    :param str name: Name of the icon, in one of the defined icons
                     in this module.
    :return: Corresponding QIcon
    :raises: ValueError when name is not known
    """
    qfile = getQFile(name)
    pixmap = qt.QPixmap(qfile.fileName())
    icon = qt.QIcon(pixmap)
    return icon


def getQPixmap(name):
    """Create a QPixmap from its name.

    The resource name can be prefixed by the name of a resource directory. For
    example "silx:foo.png" identify the resource "foo.png" from the resource
    directory "silx".

    If no prefix are specified, the file with be returned from the silx
    resource directory with a specific path "gui/icons".

    See also :func:`silx.resources.register_resource_directory`.

    :param str name: Name of the icon, in one of the defined icons
                     in this module.
    :return: Corresponding QPixmap
    :raises: ValueError when name is not known
    """
    qfile = getQFile(name)
    if qfile is None:
        raise ValueError("Not an illustration name: %s" % name)
    return qt.QPixmap(qfile.fileName())


def getQFile(name):
    """Create a QFile from an icon name. Filename is found
    according to supported Qt formats.

    The resource name can be prefixed by the name of a resource directory. For
    example "silx:foo.png" identify the resource "foo.png" from the resource
    directory "silx".

    If no prefix are specified, the file with be returned from the silx
    resource directory with a specific path "gui/icons".

    See also :func:`silx.resources.register_resource_directory`.

    :param str name: Name of the icon, in one of the defined icons
                     in this module.
    :return: Corresponding QFile
    :rtype: qt.QFile
    :raises: ValueError when name is not known
    """
    # if the extension is given in the name, skip the supported_formats
    _name = name.replace(" ", "_")
    if "." in _name:
        return _getQFile(_name)
    global _supported_formats
    if _supported_formats is None:
        _supported_formats = []
        supported_formats = qt.supportedImageFormats()
        order = ["mng", "gif", "svg", "png", "jpg"]
        for format_ in order:
            if format_ in supported_formats:
                _supported_formats.append(format_)
        if len(_supported_formats) == 0:
            _logger.error("No format supported for icons")
        else:
            _logger.debug("Format %s supported", ", ".join(_supported_formats))

    for format_ in _supported_formats:
        format_ = str(format_)
        out = _getQFile("%s.%s" % (_name, format_))
        if out and out.exists():
            return out
    raise ValueError("Not an illustration name: %s" % _name)


def getResourceFileName(name):
    return tomwer.resources._resource_filename(
        name, default_directory=os.path.join("gui", "illustrations")
    )


def _getQFile(name):
    filename = tomwer.resources._resource_filename(
        name, default_directory=os.path.join("gui", "illustrations")
    )
    qfile = qt.QFile(filename)
    if qfile.exists():
        return qfile
    else:
        return None
