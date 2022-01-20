# -*- coding: utf-8 -*-

# imprint: a program for creating documents from data and content templates
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
:py:mod:`imprint.handlers.figure.images` contains basic built-in
:ref:`plugins-handlers` for inserting images into a document. All the
handlers in this module are compatible with the
:ref:`plugin interface <plugins-figures-signature>` used by the
:ref:`xml-spec-tags-figure` tag.
"""

import errno
from io import BytesIO
import logging
from os import strerror
from os.path import exists, samefile, splitext
from shutil import copyfile, copyfileobj

from haggis.files.pdf import pdf_to_image

from ..utilities import get_file


__all__ = ['ImageFile',]


#: Private logger for this module
_logger = logging.getLogger(__name__)


def ImageFile(config, kwds, output=None):
    """
    Generate `python-docx`_ compatible images from image files.

    Copy image files as-is, or load them into memory. Output must be
    to a file of the same type as the input (except for PDFs): no
    conversion is done, only direct copy. PDFs (identified by the
    ``'.pdf'`` extension) get special handling to convert them into
    usable images.

    The following :ref:`plugins-data-configuration` keys are used:

        file
            The (mandatory) file name containing the image.
        formatted
            Whether or not ``file`` is a format string that has keyword
            replacements in it. Defaults to truthy. Set to falsy if
            the name contains random opening braces.

    Notes
    -----
    Using this plugin with PDF files requires the `poppler`_ library
    mentioned in the :ref:`dependencies-plugins-external`.

    .. include:: /link-defs.rst
    """
    input_path = get_file(config, kwds)

    if not exists(input_path):
        # http://stackoverflow.com/a/36077407/2988730
        # has instructions on how to raise FNFE properly
        raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT),
                                input_path)
    _, input_ext = splitext(input_path)

    # PDFs get special treatment
    if input_ext == '.pdf':
        if isinstance(output, str):
            if not output.endswith('.png'):
                output += '.png'
            desc = '"%s"' % output
        elif output is None:
            desc = 'in-memory PNG'
        else:
            desc = 'existing PNG stream'

        _logger.info('Converting PDF "%s" to %s', input_path, desc)
        output = pdf_to_image(input_path, output, format='png')

    elif isinstance(output, str):
        # file is a string path name
        if not output.endswith(input_ext):
            output += input_ext
        if not exists(output) or not samefile(input_path, output):
            _logger.info('Copying "%s" to "%s"', input_path, output)
            copyfile(input_path, output)
        else:
            _logger.info('Input and output image are the same path: "%s"',
                         input_path)

    else:
        if output is None:
            # Load file into memory
            _logger.trace('Loading "%s" into memory', input_path)
            output = BytesIO()
            rewind = True
        else:
            # file is a file-like object
            _logger.info('Copying "%s" to file-like object', input_path)
            rewind = False

        with open(input_path, 'rb') as f:
            copyfileobj(f, output)

        if rewind:
            output.seek(0)

    return output
