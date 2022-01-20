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
Contains most of the code that actually runs imprint.

The this module is executed publicly by the `imprint` script.
"""

# Set up matplotlib environment before doing anything else.
import matplotlib
matplotlib.use('ps')  # This line currently has some OS-specific implications

import logging
from os.path import abspath, join, split, splitext
from pathlib import Path
from pprint import pformat
from warnings import warn
from xml import sax

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from haggis.files import ensure_extension
from haggis.load import module_as_dict, load_object
from haggis.logs import configure_logger
from haggis.os import chdir_context

from .core.parsers import ReferenceProcessor, TemplateProcessor
from .core.tags import tag_registry
from .core.utilities import substitute_headers_and_footers, trigger_fail_state


#: Private logger for this module
_logger = logging.getLogger(__name__)


def load_extensions(config):
    """
    Loads all the user-defined
    :py:class:`~imprint.core.tags.TagDescriptor`\ s
    laid out in the config.

    The key ``tags`` is expected to contain a mapping of custom tag
    names to either tag descriptor objects, or the fully qualified names
    of such objects, which will be imported in the usual manner.

    Here is an example of some possibilities for ``tags``::

        tags = {
            'custom-tag1': 'repgen.demo.custom1',
            'custom-tag2': custom2,
        }

    The non-string values in tags will be registered in
    :py:data:`imprint.core.tags.tag_registry` directly. String values are
    treated as a package/module path followed by an object name, all dot
    delimited. The object will be imported and registered. The
    package/module that contains it must be on the path.
    """
    for tag, descriptor in config.get('tags', {}).items():
        if isinstance(descriptor, str):
            descriptor = load_object(descriptor)
        tag_registry[tag] = descriptor


def create_output_document(config, fail='warn'):
    """
    Create an output document object based on the configuration.

    The input :ref:`configuration-docx` will contain any styles that the
    output document will use. If the stub has any content, that content
    will appear before the generated content of the to the output
    document.

    The name of the input file is expected to be found in the `config`
    dictionary under :ref:`keywords-system-input_docx`. If the key is
    missing or the value is `None`, a new document is created. If the
    requested stub document is not found, one of the following occurs
    depending on the value of `fail`:

      - ``'ignore'``: Silently create and return an empty document. All
        the styles named in the :ref:`configuration-xml` must match the
        ones contained in the :ref:`configuration-docx`. 
      - ``'warn'``: Raise a warning and return an empty document.
      - ``'raise'``: Raise an :py:exc:`IOError`.

    Any other value for `fail` will trigger a :py:exc:`ValueError`.
    """
    doc_name = config.get('input_docx', None)
    try:
        return Document(doc_name)
    except PackageNotFoundError:
        trigger_fail_state(fail, f'Document file {doc_name} not found',
                           errorClass=IOError)
        return Document()


def save_output_document(document, config):
    """
    Save the specified document to a location given in the
    configuration.

    Two keys are used: :ref:`keywords-system-output_docx` and
    :ref:`keywords-system-overwrite_output`. The former is the file
    name. The latter determines what happens if the file already exists:

      - ``'raise'``: Raise an error.
      - ``'rename'``: Display a prompt and request that the user type in a
        new file name.
      - ``'silent'``: Ignore the issue and overwrite.
      - ``'warn'``: Ignore the issue, overwrite, but raise a warning
        nonetheless.

    If :ref:`keywords-system-overwrite_output` is missing, ``'raise'``
    is the default behavior.
    """
    output_docx = config['output_docx']
    overwrite_output = config.get('overwrite_output', 'raise').casefold()

    if overwrite_output not in ('raise', 'rename', 'warn', 'silent'):
        raise ValueError(
            'Invalid value for config key "overwrite_output". '
            'Must be one of ("raise", "rename", "silent", "warn")'
        )

    mode = 'wb' if overwrite_output == 'silent' else 'xb'

    try:
        output_file = open(output_docx, mode)
    except FileExistsError as err:
        if overwrite_output == 'raise':
            raise
        elif overwrite_output == 'rename':
            while True:
                path, file = split(output_docx)
                base_name, ext = splitext(file)
                def_name = base_name + '-1' + ext
                output_file = input('Refusing to overwrite file.\n'
                                    f'Enter a new name [{def_name}]: ')
                if not output_file.strip():
                    output_file = def_name
                output_file = join(path, output_file)
                try:
                    output_docx = open(output_file, mode)
                except FileExistsError:
                    pass
                else:
                    break
        elif overwrite_output == 'warn':
            warn(f'Overwriting existing file {output_docx!r}', RuntimeWarning)
            output_file = output_docx

    document.save(output_file)
    return output_docx


def post_process_document(file_name, config):
    """
    Apply final touchup to the output document after it has been saved.

    The document object can be assumed to have been destroyed at this
    point. The only access to it is through `file_name`. The current
    implementation filters the headers and footers of the document and
    does a keyword repacement on them.
    """
    substitute_headers_and_footers(file_name, config)


def build_document(config):
    """
    Output a document based on the specifed configuration.

    This is the main method of the :py:mod:`imprint` package. It creates
    the output by using instructions from the :ref:`configuration-xml`
    to append formatted content to the :ref:`configuration-docx`. The
    configuration dictionary directs both the I/O as well as keyword
    parameter replacements in the XML.
    """
    document = create_output_document(config)
    xml_template = abspath(config['input_xml'])

    ref_proc = ReferenceProcessor(config.get('caption_counter_depth', 1))
    sax.parse(xml_template, ref_proc)
    references = ref_proc.state.references
    _logger.debug('Anchor Map:\n%s', references)
    sax.parse(xml_template, TemplateProcessor(config, document, references))
    file_name = save_output_document(document, config)
    post_process_document(file_name, config)


def run(config_name):
    """
    Run the driver for a named configuration file.

    This wrapper loads the configuration and sets up logging before
    calling :py:func:`build_document` in earnest. All of the
    :ref:`logging-configuration` keywords are used here except
    :ref:`keywords-system-log_images`.
    """
    def get_lvl(name, default):
        level = config.get(name, default)
        if isinstance(level, str):
            level = level.upper()
        return level

    config_path = Path(config_name)
    with chdir_context(config_path.parent):
        config = module_as_dict(
            config_path.name, name='config', include_var='includes'
        )
        log_file = config.get('log_file', None)
        if log_file is True:
            log_file = ensure_extension(config['output_docx'], '.log',
                                        partial_policy='replace')
        configure_logger(
            log_file, get_lvl('file_level', 'NOTSET'),
            config.get('log_stderr', False), get_lvl('stderr_level', 'ERROR'),
            config.get('log_stdout', True), get_lvl('stdout_level', 'WARNING'),
            config.get('log_format', None)
        )
        _logger.debug('Loaded config:\n%s',
                      pformat(config, indent=4, width=255))
        load_extensions(config)
        build_document(config)
