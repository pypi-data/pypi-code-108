#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# bs4 utility methods
# IMIO <support@imio.be>
#

from bs4.element import Comment


def remove_elements(element, to_remove=[]):
    """ Removes sub tags and all their content """
    for tagtr in to_remove:
        for tag in element.find_all(tagtr):
            tag.decompose()


def remove_attributes(element, attributes=[], recursive=True):
    """ Removes attributes on given element or recursively """
    elements = [element]
    if recursive:
        elements += element.find_all()
    for tag in elements:
        for attr in attributes:
            try:
                del tag[attr]
            except KeyError:
                pass


def remove_comments(element):
    """ Removes html comments """
    for comment in element.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()


def replace_entire_strings(element, replace=u'\n', by=u''):
    """ Replaces an entire string by another value. With default params, removes newlines """
    # reversed needed to avoid internal strings error
    strings = reversed([s for s in element.strings])
    for string in strings:
        if string == replace:
            string.replace_with(by)


def unwrap_tags(element, tags=[]):
    """ unwrap tags with content """
    for tagtu in tags:
        for tag in element.find_all(tagtu):
            tag.unwrap()
