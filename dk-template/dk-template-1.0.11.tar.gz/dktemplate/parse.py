# -*- coding: utf-8 -*-
from __future__ import print_function
import re


from dktemplate.ast import (
    IfTag, ForTag, WithTag, NoOpTag, Tag, Block, Value, IncludeTag,
    RegroupTag, GetCommentForm, AsTag
)
from dktemplate.tokenize import name, content, tokenize, is_tag, is_endtag


def parse_file(fname):
    return parse(open(fname).read(), fname)


def parse(txt, fname=None):
    """Parse template text.
    """
    txt = re.sub(r'{#\s*dk-template:\s*noparse\s*#}.*?{#\s*dk-template:\s*end-noparse\s*#}', "", txt)
    return nest(tokenize(txt), fname)


def make_tag(input_queue, name, content=None, fname=None):
    tag_cls = {
        'if': IfTag,
        'elif': IfTag,
        'for': ForTag,
        'with': WithTag,
        'load': NoOpTag,
        'block': NoOpTag,
        'include': IncludeTag,
        'regroup': RegroupTag,
        'get_comment_form': GetCommentForm,
        'get_comment_list': GetCommentForm,
    }.get(name)

    if tag_cls is None:
        if AsTag.is_as_tag(content):
            tag_cls = AsTag
        else:
            tag_cls = Tag

    tag = tag_cls(name, content, fname)
    # if tag_cls in [NoOpTag]:
    #     print "TAG:SCLS", tag_cls, tag.fvars(), tag.dvars()

    # tags that modify the context from their location to the end of
    # the document.
    rest_of_doc_tags = ['regroup']  # , 'get_comment_form', 'get_comment_list']
    if name in rest_of_doc_tags:
        # add in dummy end tags (so the shift/reduce algorithm knows when
        # to create blocks.
        input_queue.append("{%% end%s %%}" % name)

    return tag


def nest(words, fname):
    """Nest start/end tags into blocks recursively.
    """
    # stack = [Tag('-program')]
    stack = []

    def prstack():  # pragma: nocover
        """Print stack contents.
        """
        print("STACK:....")
        for _item in stack:
            print(_item)

    while words:
        word = words.pop(0)
        # print "\WORD:", word
        # prstack()

        if is_endtag(word):
            # tagname = name(word)[3:]
            # print "REDUCE", tagname
            block = []
            while 1:
                item = stack.pop()
                found = isinstance(item, Tag) and item.matches(word)
                # print '    POPPED', item, 'FOUND' if found else ""
                if found:
                    stack.append(Block(item.name, item, block[::-1]))
                    break
                else:
                    block.append(item)
        elif is_tag(word):
            # print "SHIFT TAG", name(word)
            tag = make_tag(words, name(word), content(word), fname)
            stack.append(tag)
        else:
            # print "SHIFT VAL", word
            stack.append(Value(content(word)))

    return Block('program', Tag('program'), stack)
