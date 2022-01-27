#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CharGrams class cuts a text on the characters (or any other regular expression pattern), and returns the associated tokens in a list of Span objects, or a list of strings, or a Tokens instance.
"""

import re
from tokenspan import Span
from .base_tokenizer import BaseTokenizer

class CharGrams(BaseTokenizer,Span):
    """
CharGrams is a sub-class of Span. It allows cutting the text (given as string parameter) in a collection of sub-string that are characterized by their size.
                                                                                                                                         Basic examples are 

```python
s = "ABCDEF"
CharGrams(s).tokenize().toStrings()
# -> ['A', 'B', 'C', 'D', 'E', 'F']
CharGrams(s).tokenize(size=2).toStrings()
# -> ['AB', 'BC', 'CD', 'DE', 'EF']
CharGrams(s).tokenize(size=2,step=2).toStrings()
# -> ['AB', 'CD', 'EF']
CharGrams(s,ranges=[range(1,3),range(4,6)],subtoksep='@').tokenize(size=2).toTokens()
# -> Tokens(4 Token) : BC  C@  @E  EF # a Tokens object
```

The main interests in the CharGrams class is to extract into Tokens objects, or Span objects the different tokens, in order to continue working on them.
    """
    def __init__(self,
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,):
        """
CharGrams has all the parameters of a Span object, namely `string` (the string to be tokenized), a `subtoksep` that will be inserted between the different sub-tokens of a Span object (default is a free space), and a `ranges` list of range objects. 
        """
        Span.__init__(self,string=string,subtoksep=subtoksep,ranges=ranges)
        self.chargrams = list()
        self._name_ = 'CharGrams'
        return None
    
    @property
    def _subtokens_(self,):
        return self.chargrams
    
    def __call__(self, 
                 string=str(),
                 subtoksep=chr(32),
                 ranges=None,
                 size=1,
                 step=1):
        """
Apply the `.tokenize` method to a new string. Returns a new `CharGrams` instance. All parameters from `CharGrams` and/or `CharGrams.tokenize` are available, except `inplace`, which is always `False`.        
        """
        cg = CharGrams(string=string,
                       subtoksep=subtoksep,
                       ranges=ranges)
        return cg.tokenize(size=size, step=step, inplace=False)
    
    def tokenize(self,size=1,step=1,inplace=True):
        """
Tokenize the parent string into tokens, that are themselves instances of CharGrams.
Returns the CharGrams object itself (tokenize is an in-place operation if `inplace=True`), or a new CharGrams object. The different tokens are then stored in CharGrams.chargrams list.

Parameters : 
    - `size`, an integer (default is 1), the size of the token, in characters
    - `step`, an integer (default is 1), the number of characters that are escaped from one token to the next one
    - `inplace`, a boolean (default is True), whether the method changes the object in place or returns a new object.

By default `CharGrams.tokenize().toStrings()` returns a list of characters.
        """
        if not inplace:
            self = CharGrams(string=self.string,
                             subtoksep=self.subtoksep,
                             ranges=self.ranges)
        chargrams = self.slice(start=0,stop=None,size=size,step=step)
        self.chargrams = [CharGrams(self.string,
                                    ranges=span.ranges,
                                    subtoksep=self.subtoksep,)
                          for span in chargrams]
        return self
