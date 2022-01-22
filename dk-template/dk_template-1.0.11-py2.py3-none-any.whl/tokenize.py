# -*- coding: utf-8 -*-
import re


def name(t):
    """The name of the tag.
    """
    txt = t.strip(' {%').split()[0]
    return txt


def content(t):
    """The content of the tag.
    """
    if is_tag(t):
        try:
            return ' '.join(t.strip(' {%}').split()[1:])
        except IndexError:  # pragma:nocover
            return ""
    else:
        return t.strip(' {}')


def tokenize(t):
    tag_and_vals = []
    txt = re.sub(r'{#.*?#}', '', t)
    tag_and_vals += re.findall(r'{(?:%|{).*?(?:}|%)}', txt)
    return tag_and_vals


def is_tag(t):
    """Is `t` a tag?
    """
    return t.strip().startswith('{%')


def is_endtag(t):
    """Is `t` an end-tag?
    """
    if not is_tag(t):
        return False
    return name(t).startswith('end')
