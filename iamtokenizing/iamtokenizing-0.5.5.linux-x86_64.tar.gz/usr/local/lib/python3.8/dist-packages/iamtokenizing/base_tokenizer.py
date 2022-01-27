#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BaseTokenizer is a generic class making tools for later definition of more elaborated tokenizers. It deals only with the representation, and the way
"""

from tokenspan import Span, Token, Tokens

class BaseTokenizer():
    """
Define some standard functions for conversion from elaborated Tokenizer to Span, Token and Tokens classes. In sub-classes that inherits from this one, one should define a `_name_` attribute (that will be displayed on __repr__) and a `_subtokens_` entity that consists in a list of sub-entities that can be converted to Token, Span or String. 

Then the methods 
    - toTokens
    - toSpans
    - toStrings
are automatically imported in the sub-classes.
    """
    
    def __repr__(self):
        """Return the two main arguments (namely the `string` and the `ranges`) of the tokenizer constructed from this class instance. Requires that the tokenizer has the attribute `_name_`."""
        mess = "{}('{}', ".format(self._name_,str(self))
        mess += '['+','.join('('+str(r.start)+','+str(r.stop)+')' 
                             for r in self.ranges)
        mess += "])"
        return mess
    
    def __getitem__(self,n):
        """Returns the n element (eventually a slice) of the tokenizer, once the method `tokenize` has been applied. Requires that the tokenizer has the attribute `_subtokens_`."""
        return self._subtokens_[n]

    def toSpans(self,):
        """Alias for to_spans method."""
        return self.to_spans()
    
    def to_spans(self):
        """
Once `tokenize` method has been applied, this method transforms the `_subtokens_` list into a list of Span objects. 

Returns a tuple of Span objects.
        """
        spans = [Span(string=subtok.string,
                      ranges=subtok.ranges,
                      subtoksep=subtok.subtoksep)
                 for subtok in self]
        return tuple(spans)
    
    def toTokens(self, carry_attributes=True):
        """Alias for to_tokens method."""
        return self.to_tokens(carry_attributes=carry_attributes)
    
    def to_tokens(self, carry_attributes=True):
        """
Once `tokenize` method has been applied, this method transforms the `_subtokens_` list into a Tokens instance, that is, a container for Token objects, each Token being one of the `_subtokens_`. The attribute `carry_attributes` is given to the Token and Tokens instances.

Returns a Tokens object.
        """
        tokens = [Token(string=subtok.string,
                        ranges=subtok.ranges,
                        subtoksep=subtok.subtoksep,
                        carry_attributes=carry_attributes)
                  for subtok in self]
        return Tokens(tokens)

    def toStrings(self):
        """Alias for to_strings method."""
        return self.to_strings()
    
    def to_strings(self):
        """
Once `tokenize` method has been applied, this method transforms the `_subtokens_` list into a list of strings. 

Returns a list of strings.
        """
        return tuple(str(subtok) for subtok in self)
