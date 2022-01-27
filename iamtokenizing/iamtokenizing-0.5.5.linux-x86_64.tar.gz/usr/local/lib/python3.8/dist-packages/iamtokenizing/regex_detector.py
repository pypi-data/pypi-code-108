#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RegexDetector class cuts a text on any regular expression pattern, and returns the associated tokens in a list of Span objects, or a list of strings, or a Tokens instance.
"""

import re
from tokenspan import Span
from .base_tokenizer import BaseTokenizer

class RegexDetector(BaseTokenizer,Span):
    """
RegexDetector is a sub-class of Span. It allows cutting the text (given as string parameter) on any regular expression (REGEX), and extracting the resulting tokens from the parent string. The tokenized objects are themselves instances of RegexDetector, and one can thus applies REGEX expression recursively in the parent string.
    """
    def __init__(self,
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,):
        """
RegexDetector has all the parameters of a Span object, namely `string` (the string to be tokenized), a `subtoksep` that will be inserted between the different sub-tokens of a Span object (default is a free space), and a `ranges` list of range objects. 
        """
        Span.__init__(self,string=string,subtoksep=subtoksep,ranges=ranges)
        self.detections = list()
        self._name_ = 'RegexDetector'
        return None

    @property
    def _subtokens_(self,):
        return self.detections
    
    def __call__(self, 
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,
                 regex='\w+',
                 flags=0):
        """
Apply the `.tokenize` method to a new string. Returns a new `RegexDetector` instance. All parameters from `RegexDetector` and/or `RegexDetector.tokenize` are available, except `inplace`, which is always `False`.    
        """
        rd = RegexDetector(string=string,
                           subtoksep=substoksep,
                           ranges=ranges)
        return rd.tokenize(regex=regex, flags=flags, inplace=False)
    
    def tokenize(self,regex='\w+',flags=0,inplace=True):
        """
Tokenize the parent string into tokens, that are themselves instances of RegexDetector (so for instance each of these instance can be searched by REGEX as well).
Returns the RegexDetector object itself (tokenize is an in-place operation if `inplace=True`), or a new RegexDetector object. The different tokens are then stored in RegexDetector.subSpans list.

Parameters | Type | Details
--- | --- | --- 
`regex` | a REGEX (string) | a regular expression (REGEX) that will serve to identify the Token to be find
`flags` | some REGEX flags | flags are inherited from `re` package, and can be combined using a pipe symbol, for instance `flags=re.DOTALL|re.MULTILINE` apply both DOTALL (special character '.' also accepts new line) and MULTILINE (special characters '^' and '$' match begining and end of each new line)
`inplace` | boolean | whether the method changes the object in place (`inplace=True`, by default) or returns a new object.

By default there is no flags (that is `flags=0`) and the `regex` is on contiguous alpha-numeric characters (that is `regex='\w+'`). In that case, `RegexDetector.tokenize().toStrings()` return words in a list.
        """
        if not inplace:
            self = RegexDetector(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=self.ranges)
        ranges = [range(r_.start+r.start(),r_.start+r.end())
                  for r_ in self.ranges
                  for r in re.finditer(regex,
                                       self.string[r_.start:r_.stop],
                                       flags=flags)]
        self.ranges = ranges
        self.detections = []
        for span in self.subspans:
            self.detections.append(RegexDetector(string=self.string,
                                                 subtoksep=self.subtoksep,
                                                 ranges=span.ranges))
        return self
