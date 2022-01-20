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
:py:mod:`imprint.code.defaults` defines the defaults used by the engine,
in the absence of a
:ref:`user-defaults file <future-work-user-defaults>`.

This is the last fallback for all the default values used to style
elements without explicit styles set. All the styles defined here exist
in the baseline document created by `python-docx`_ by default.

Importing this module sets up all the attributes based on the user
defaults file.


.. include:: /link-defs.rst
"""

from docx.shared import Inches


__all__ = [
    'paragraph_style', 'run_style',
    'figure_paragraph_style', 'figure_run_style',
    'figure_label_style', 'figure_width',
    'table_paragraph_style',
    'table_run_style', 'table_style',
    'toc_title_style', 'toc_min_level',
    'toc_max_level',
    'latex_paragraph_style', 'latex_run_style',
    'latex_format', 'latex_dpi',
    'numbered_list_paragraph_style', 'bulleted_list_paragraph_style',
    'alt_paragraph_style', 'alt_run_style',
]

#: Default style to apply to unspecified paragraphs.
paragraph_style = 'Normal'

#: Default style to apply to unspecified runs.
run_style = 'Default Paragraph Font'

figure_paragraph_style = 'Quote'
figure_run_style = 'Default Paragraph Font'
figure_label_style = 'Subtitle'
#: The width to make stand-alone figures occupy on the page if one is
#: not specified explicitly in the configuration with a 'width' key.
figure_width = Inches(6.5)

table_style = 'Table Grid'
table_paragraph_style = 'Quote'
table_run_style = 'Default Paragraph Font'

toc_title_style = 'TOC Heading'
toc_min_level = 1
toc_max_level = 3

latex_run_style = 'Default Paragraph Font'
latex_paragraph_style = 'Quote'
latex_format = 'jpg'
latex_dpi = 96

#: The style that will determine which paragraphs are handled specially
#: as list elements.
numbered_list_paragraph_style = 'List Number'
bulleted_list_paragraph_style = 'List Bullet'

alt_paragraph_style = 'Subtitle'
alt_run_style = 'Subtitle Char'

reference_level_sep = '.'
reference_sep = '-'
reference_depth = 3
