#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextTokenization class allows to tokenize a part of a string into a context.
The context is the left and right parts around a token.
"""

from tokenspan import Span
from .base_tokenizer import BaseTokenizer
from . import NGrams
from . import RegexDetector

class ContextDetector(BaseTokenizer, Span):
    """
ContextDetector class allows splitting of a big text into chunks given by the `splitter` REGEX parameter of the `tokenize` method, then it detects the `selector` REGEX  inside each chunk, and associates the context to each of the detection. The context are given by the sub-strings in between different detections. By default `ContextDetector` detects digits inside sentence (or paragraph, that is, part of the string separated by newline character).
    """

    def __init__(self,
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,
                 ):
        """
ContextDetector has all the parameters of a Span object, namely `string` (the string to be tokenized), a `subtoksep` that will be inserted between the different sub-tokens of a Span object (default is a free space), and a `ranges` list of range objects. 
        """        
        Span.__init__(self,string=string,subtoksep=subtoksep,ranges=ranges)
        self.context_left = None
        self.context_right = None
        self.context_parent = None
        self.context_tokens = list()
        self.context = None
        self._name_ = 'ContextDetector'
        return None
    
    @property
    def _subtokens_(self,):
        return self.context_tokens
    
    def __call__(self, 
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,
                 splitter='\n+', 
                 selector='\d+',
                 splitter_flags=0,
                 selector_flags=0):
        """
Apply the `.tokenize` method to a new string. Returns a new `ContextDetector` instance. All parameters from `ContextDetector` and/or `ContextDetector.tokenize` are available, except `inplace`, which is always `False`.
        """
        ct = ContextDetector(string=str(string),
                              subtoksep=subtoksep,
                              ranges=ranges)
        return ct.tokenize(splitter=splitter,
                           selector=selector,
                           splitter_flags=0,
                           selector_flags=0,
                           inplace=False)

    def tokenize(self, 
                 splitter='\n+', 
                 selector='\d+', 
                 inplace=True,
                 splitter_flags=0,
                 selector_flags=0):
        """
Detects the `selector` REGEX inside the parent string and associate a context to each detection, the context being given by the remaining parts of the tokens given by the `splitter` REGEX expressions.
`selector` uses the `RegexDetector` tokenization, and `splitter` uses the `NGrams` tokenization.

Parameters | Type | Details
--- | --- | --- 
`splitter` | str | the REGEX that will be used to split the complete string into context sub-strings.
`splitter_flags` | some REGEX flags | The flags that will be transmitted to the `NGrams.tokenize` method of the splitting. flags are inherited from `re` package, and can be combined using a pipe symbol, for instance `flags=re.DOTALL|re.MULTILINE` apply both DOTALL (special character '.' also accepts new line) and MULTILINE (special characters '^' and '$' match begining and end of each new line). By default `splitter_flags=0`.
`selector` | str | the REGEX that will be used to detect a part of the context string.
`selector_flags` | some REGEX flags | The flags that will be transmmitted to the `RegexDetector.tokenize` method of the detection. flags are inherited from `re` package, and can be combined using a pipe symbol, for instance `flags=re.DOTALL|re.MULTILINE` apply both DOTALL (special character '.' also accepts new line) and MULTILINE (special characters '^' and '$' match begining and end of each new line). By default `selector_flags=0`.
`inplace` | boolean | whether the method changes the object in place (`inplace=True`, by default) or returns a new object
        """
        if not inplace:
            self = ContextDetector(string=self.string,
                                    ranges=self.ranges,
                                    subtoksep=self.subtoksep)
        contexts = NGrams(string=self.string, 
                          ranges=self.ranges,
                          subtoksep=self.subtoksep)
        self.context = contexts.tokenize(regex=splitter, 
                                         inplace=False, 
                                         flags=splitter_flags)
        ranges_ = []
        for i,context in enumerate(self.context):
            atoms = RegexDetector(string=context.string,
                                  ranges=context.ranges,
                                  subtoksep=context.subtoksep)
            atoms = atoms.tokenize(regex=selector, 
                                   inplace=False, 
                                   flags=selector_flags)
            ranges_.extend(atoms.ranges)
            if not atoms:
                continue
            if len(atoms.subspans) == 1:
                ct = ContextDetector(string=context.string, 
                                      ranges=atoms.ranges,
                                      subtoksep=atoms.subtoksep,)
                ct.context_parent = i
                ct.context_left = NGrams(string=context.string,
                                         ranges=[range(context.start, atoms.start),],
                                         subtoksep=context.subtoksep)
                ct.context_right = NGrams(string=context.string,
                                          ranges=[range(atoms.stop, context.stop),],
                                          subtoksep=context.subtoksep)
                self.context_tokens.append(ct)
                continue
            start = context.start
            for atom1, atom2 in zip(atoms[:-1], atoms[1:]):
                ct = ContextDetector(string=context.string, 
                                      ranges=atom1.ranges,
                                      subtoksep=context.subtoksep)
                ct.context_parent = i
                ct.context_left = NGrams(string=context.string,
                                         ranges=[range(start, atom1.start),],
                                         subtoksep=context.subtoksep)
                ct.context_right = NGrams(string=context.string,
                                          ranges=[range(atom1.stop, atom2.start),],
                                          subtoksep=context.subtoksep)
                self.context_tokens.append(ct)
                start = atom1.stop
            ct = ContextDetector(string=context.string, 
                                  ranges=atom2.ranges,
                                  subtoksep=context.subtoksep)
            ct.context_parent = i
            ct.context_left = NGrams(string=context.string,
                                     ranges=[range(atom1.stop, atom2.start),],
                                     subtoksep=context.subtoksep)
            ct.context_right = NGrams(string=context.string,
                                      ranges=[range(atom2.stop, context.stop),],
                                      subtoksep=context.subtoksep)
            self.context_tokens.append(ct)
        if ranges_:
            self.ranges = ranges_
        return self.context_tokens
