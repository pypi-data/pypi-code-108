# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""HTML utilities."""

import html

import bleach
from ftfy import fix_text

#: Unwanted unicode characters
UNWANTED_CHARS = {
    # Zero-width space
    u'\u200b',
}


#: Allowed tags used for html sanitizing by bleach.
ALLOWED_HTML_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'br',
    'code',
    'div',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'i',
    'li',
    'ol',
    'p',
    'pre',
    'span',
    'strike',
    'strong',
    'sub',
    'sup',
    'u',
    'ul',
]


#: Allowed attributes used for html sanitizing by bleach.
ALLOWED_HTML_ATTRS = {
    '*': ['class'],
    'a': ['href', 'title', 'name', 'class', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
}


def strip_html(value):
    """Strip all HTML from text and remove unwanted unicode characters."""
    # Disallow all HTML tags and attributes
    value = sanitize_html(value, tags=[], attrs=[])
    # If value has already escaped HTML then return the unescaped value
    return html.unescape(value)


def sanitize_html(value, tags=None, attrs=None):
    """Sanitizes HTML using the bleach library.

    The default list of allowed tags and attributes is defined by
    ``ALLOWED_HTML_TAGS`` and ``ALLOWED_HTML_ATTRS``.

    You can override the defaults like this:

    .. code-block:: python

        class MySchema(Schema):
            html = fields.SanitizedHTML(tags=['a'], attrs={'a': ['href']})

    :param tags: List of allowed tags.
    :param attrs: Dictionary of allowed attributes per tag.
    """
    value = sanitize_unicode(value)

    if tags is None:
        tags = ALLOWED_HTML_TAGS

    if attrs is None:
        attrs = ALLOWED_HTML_ATTRS

    return bleach.clean(
        value,
        tags=tags,
        attributes=attrs,
        strip=True,
    ).strip()


def is_valid_xml_char(char):
    """Check if a character is valid based on the XML specification."""
    codepoint = ord(char)
    return (0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF)


def sanitize_unicode(value, unwanted_chars=None):
    """Sanitize and fix problematic unicode characters."""
    value = fix_text(value.strip())
    # NOTE: This `join` might be ineffiecient... There's a solution with a
    # large compiled regex lying around, but needs a lot of tweaking.
    value = ''.join(filter(is_valid_xml_char, value))

    if unwanted_chars is None:
        unwanted_chars = UNWANTED_CHARS

    for char in unwanted_chars:
        value = value.replace(char, '')
    return value
