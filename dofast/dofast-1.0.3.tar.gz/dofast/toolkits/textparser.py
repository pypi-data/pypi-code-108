#!/usr/bin/env python
import re
from typing import List, Union


class TextParser(object):
    def __init__(self):
        ...

    @staticmethod
    def _string_match(pattern: str, text: str) -> bool:
        return True if re.search(re.compile(pattern, re.IGNORECASE), text) else False

    @staticmethod
    def match(pattern: Union[str, List], text: str) -> bool:
        '''whether text matches any of item from pattern'''
        if isinstance(pattern, str):
            return TextParser._string_match(pattern, text)

        assert isinstance(pattern, list), 'Pattern is either list or str'
        return any(TextParser._string_match(e, text) for e in pattern)

    @staticmethod
    def is_parcel_arrived(text: str) -> bool:
        return '丰巢' in text
