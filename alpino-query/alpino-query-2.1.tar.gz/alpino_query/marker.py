#!/usr/bin/env python3
# mark the matched tokens in the tree with include/exclude attributes
import re
from typing import List
from lxml import etree


def mark(twig, tokens, attributes) -> None:
    # add info annotation matrix to alpino parse
    for begin, token in enumerate(tokens):
        if (re.match(r"([_<>\.,\?!\(\)\"\'])|(\&quot;)|(\&apos;)", token)):
            xp = twig.xpath(f"//node[@begin='{begin}']")
        else:
            xp = twig.xpath(f"//node[@word='{token}' and @begin='{begin}']")
        if begin < len(attributes):
            attrs = attributes[begin].split(',')
            for x in xp:
                include = set()
                exclude = set()
                case_insensitive = None
                for attr in attrs:
                    if attr[0] == '-':
                        target = exclude
                        attr = attr[1:]
                    else:
                        target = include

                    if attr == 'cs':
                        # cs: case sensitive
                        # -cs: case insensitive
                        case_insensitive = target is exclude
                    elif attr == 'word':
                        target.add('word')
                        if case_insensitive is None:
                            case_insensitive = True
                    else:
                        target.add(attr)

                if case_insensitive:
                    x.attrib['caseinsensitive'] = 'yes'

                if include:
                    x.attrib['include'] = str.join(',', sorted(include))
                if exclude:
                    x.attrib['exclude'] = str.join(',', sorted(exclude))


def main(inputxml: str, tokens: List[str], attributes: List[str]) -> etree._Element:
    twig = etree.fromstring(bytes(inputxml, encoding='utf-8'))
    mark(twig, tokens, attributes)
    return twig
