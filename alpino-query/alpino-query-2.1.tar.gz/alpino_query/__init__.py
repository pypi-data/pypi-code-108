#!/usr/bin/env python3
from typing import List
from lxml import etree

from .marker import main as mark
from .subtree import generate_subtree
from .xpath_generator import main as generate_xpath


class AlpinoQuery:
    @property
    def marked_xml(self):
        return self.__get_xml(self.marked)

    @property
    def subtree_xml(self):
        return self.__get_xml(self.subtree)

    def mark(self, inputxml: str, tokens: List[str], attributes: List[str]) -> etree._Element:
        self.marked = mark(inputxml, tokens, attributes)
        return self.marked

    def generate_subtree(self, remove: List[str]) -> etree._Element:
        """
        Generate subtree, removes the top "rel" and/or "cat"
        """
        self.subtree = generate_subtree(self.marked, remove)
        return self.subtree

    def generate_xpath(self, order: bool) -> str:
        self.xpath = generate_xpath(self.subtree_xml, order)
        return self.xpath

    def __get_xml(self, twig) -> str:
        return etree.tostring(twig, pretty_print=True).decode()
