#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions support for the Token and Tokens classes.
"""

from typing import List, Tuple
import warnings

class BoundaryWarning(Warning):
    pass

def _startstop(obj, start:int, stop:int) -> Tuple[int, int]:
    """
    Tool function to catch the edge of the constructed string in the following methods.
    Works for both the Token and Tokens classes, if obj is passed as self.
    Recast start and stop inside the Token.string coordinates in case obj is a Token.string.
    
    Raise a BoundaryWarning in case at least one of the the start or stop has been changed.
    """
    start_, stop_ = start, stop
    if not stop and stop!=0: stop = len(obj)
    if stop < 0 or stop > len(obj): stop = len(obj)
    if start > stop: start = stop
    if start < 0: start = 0
    if start_!=start or stop_!=stop:
        mess = "At least one of the boundaries has been modified"
        warnings.warn(mess, category=BoundaryWarning)
    return start, stop

def _isSpan(span) -> bool:
    """Returns True if `span` has all the attributes of a Span instance. False if not."""
    bools = [hasattr(span,attr) for attr in ['string','ranges','subtoksep']]
    return all(bools)

def _checkSpan(span):
    """Raises a ValueError in case `span` is not a proper Span instance"""
    if not _isSpan(span):
        raise ValueError("Accepts only Span instance")
    return None

def _isToken(token):
    """Returns True if `token` has all the attributes of a Token instance. False if not."""
    bools = [hasattr(token,attr)
             for attr in ['string','ranges','_extra_attributes',
                          'subtoksep','carry_attributes']]
    return all(bools)

def _checkToken(token):
    """Raises a ValueError in case `token` is not a proper Token instance"""
    if not _isToken:
        raise ValueError("Accepts only Token instance")
    return None

def _isTokens(tokens):
    """Returns True if all elements of `tokens` is a Token instance according to `_isToken`, otherwise returns False"""
    # to handle a non iterable
    if not any([hasattr(tokens,'tokens'),isinstance(tokens,(list,tuple))]):
        bools = [False,]
    else:
        bools = [_isToken(tok) for tok in tokens]
    return all(bools)

def _checkTokens(tokens):
    """Raises a ValueError in case `tokens` is not a proper Tokens instance."""
    if not _isTokens(tokens):
        raise ValueError("Accepts only Tokens instance")
    return None

def _checkRange(r):
    """Raises a ValueError in case r is not a compatible range object."""
    if not isinstance(r, range):
        raise ValueError("r is not an instance of Range")
    if r.start > r.stop:
        raise ValueError("r must be compatible : start<=stop")
    if r.step != 1:
        raise ValueError("r must have a step of 1")
    return None

def _checkRanges(ranges):
    """Raises a ValueError in case one range in `ranges` is not suitable for the `Span` or `Token` classes."""
    for r in ranges:
        _checkRange(r)
    return None

def _checkSameString(obj1, obj2):
    """Raises a TypeError in case the two objects have not the same .string attribute. raises an AttributeError in case at least one of the objects has no attribute .string."""
    if str(obj1.string) != str(obj2.string):
        s = obj1.__class__.__name__
        mess = "can only compare {} objects having same {}.string".format(s,s)
        raise TypeError(mess)
    return None

def _areOverlapping(r1: range, r2: range) -> bool:
    """Take two range objects, and return True if they are disjoint, otherwise return False if they overlap on some range"""
    min_ = max(r1.start,r2.start)
    max_ = min(r1.stop,r2.stop)
    return bool(max(max_-min_,0))

def _isInside(r1: range, r2: range) -> bool:
    """Take two range objects r1 and r2, and return True if r2 is in r1, otherwise return False."""
    return r1.start<=r2.start and r1.stop>=r2.stop

def _combineRanges(ranges: List[range]) -> List[range]:
    """
Take a list of range objects, and transform it such that overlapping ranges and consecutive ranges are combined. 

Exemple:
```python
_combineRanges([(12,25),(35,40)]) # -> [(12,25),(35,40),]
_combineRanges([(12,25),(26,40)]) # -> [(12,25),(26,40),]
_combineRanges([(12,26),(26,40)]) # -> [(12,40),]
_combineRanges([(12,25),(15,40)]) # -> [(12,40),]
_combineRanges([(12,25),(15,16)]) # -> [(12,25),]
```
Where all range objects have been transformed in tuples `(12,25)==range(12,25)` for illustration purpose.
The overlapping information is lost in the process.

`ranges` is a list of `range` object, all with `range.step==1` (not verified by this function, but required for the algorithm to work properly)..
    """
    if len(ranges) < 2:
        return ranges
    sorted_ranges = sorted(ranges, key=lambda x: x.start)
    combined_ranges = [sorted_ranges[0],]
    for next_range in sorted_ranges[1:]:
        previous_range = combined_ranges[-1]
        # overlapping ranges
        if previous_range.stop >= next_range.start:
            # avoid next_range inside previous_range
            if next_range.stop >= previous_range.stop:
                # extend the previous_range to next_range
                combined_ranges[-1] = range(previous_range.start,
                                            next_range.stop)
        # remain only distinct ranges since ranges are sorted
        else:
            # overwrite the next previous_range
            combined_ranges.append(next_range)
    return combined_ranges

def _findCut(ranges: List[range], cut: int, step: int=0) -> Tuple[int, int, bool]:
    """
Find the index i_ and absolute position cut_ of the cuting of ranges at relative position cut. Handle the case where the cut is inside some separator of size given by the step parameter, in which case a flag_ is raised.

Returns a tuple `(i_,cut_,flag_)` : 
    - `i_` index of the ranges element onto which the cut applies
    - `cut_` absolute position where the cut applies in the coordinates of the ranges
    - `flag_` True if the cut appears inside the separator

Raises an IndexError in case the cut is outside the range of the ranges.

Examples:
```python
ranges = [range(10,20), range(30,40)]
_findCut(ranges,5,step=0)   # -> (0, 15, False)
_findCut(ranges,10,step=0)  # -> (1, 30, False)
_findCut(ranges,10,step=1)  # -> (0, 20, False)
_findCut(ranges,11,step=1)  # -> (1, 30, False)
_findCut(ranges,10,step=2)  # -> (0, 20, False)
_findCut(ranges,11,step=2)  # -> (0, 20, True)
_findCut(ranges,12,step=2)  # -> (1, 30, False)
_findCut(ranges,20,step=1)  # -> (1, 39, False)
_findCut(ranges,21,step=1)  # -> (1, 40, False)
_findCut(ranges,22,step=1)  # -> IndexError
```

This function is the main tool to cut ranges in sub-ranges, see `_cutRanges` below.

Warning, this function does not sort the ranges, but they must be sorted for the algorithm to work properly.
    """
    cursor, i_, cut_, flag_ = 0, 0, None, False
    for i,r in enumerate(ranges):
        temp = range(cursor,cursor+step+len(r))
        if cut in temp: 
            cut_, i_ = r.start+cut-cursor, i
            if cut_ > r.stop: # cut in the separator
                cut_, flag_ = r.stop, True
            break
        cursor += len(r)+step
    if cut_ is None:
        raise IndexError("cut not found in ranges")
    return i_, cut_, flag_

def _cutRanges(ranges: List[range], cut: int, step: int=0) -> Tuple[List[range], List[range]]:
    """
Cut the ranges (given in absolute positions) at the cut (given in relative position). Handle the case where the cut is inside some separator of size given by the step parameter, in which case the entire separator length is on the left list of range objects. 

Returns two lists of range objects. The first list will correspond to the left Token (before the cut), and the second one to the right Token (after the cut).

Warnings:
    - some of the returned ranges might be empty. This is the case when the cut appears at a boundary of the range. It allows the Token instance to handle the size of the `subtoksep` separator in a smart way. This is the reason for the introduction of the `flag_` parameter in the `_findCut` function.
    - the `ranges` must be sorted for this function to work properly.

Examples:
```python
ranges = [range(10,20), range(30,40)]
_cutRanges(ranges,5,step=0)   # -> ([range(10, 15)], [range(15, 20), range(30, 40)])
_cutRanges(ranges,10,step=0)  # -> ([range(10, 20), range(30, 30)], [range(30, 40)])
_cutRanges(ranges,11,step=0)  # -> ([range(10, 20), range(30, 31)], [range(31, 40)])

# note the position of the empty range in the two exemples to come
_cutRanges(ranges,10,step=1)  # -> ([range(10, 20)], [range(20, 20), range(30, 40)])
_cutRanges(ranges,11,step=1)  # -> ([range(10, 20), range(30, 30)], [range(30, 40)])

_cutRanges(ranges,10,step=2)  # -> ([range(10, 20)], [range(20, 20), range(30, 40)])
# flag_ = True, separator is on the left : 
_cutRanges(ranges,11,step=2)  # -> ([range(10, 20), range(20, 20)], [range(30, 40)])
_cutRanges(ranges,12,step=2)  # -> ([range(10, 20), range(30, 30)], [range(30, 40)])

_cutRanges(ranges,20,step=1)  # -> ([range(10, 20), range(30, 39)], [range(39, 40)])
_cutRanges(ranges,21,step=1)  # -> ([range(10, 20), range(30, 40)], [range(40, 40)])
_cutRanges(ranges,22,step=1)  # -> IndexError
```
    """
    i_, cut_, flag_ = _findCut(ranges,cut,step)
    if not flag_:
        r1 = ranges[:i_] + [range(ranges[i_].start,cut_),]
        r2 = [range(cut_,ranges[i_].stop),] + ranges[i_+1:]
    else: # cut in the separator: the entire separator is on the left
          # range(cut_,cut_) is required to give the correct length of the string
          # in Token instance, which knows the size of subtoksep
        r1 = ranges[:i_] + [range(ranges[i_].start,cut_),range(cut_,cut_),]
        r2 = ranges[i_+1:]
    return r1,r2

def _removeRange(ranges: List[range], r: range) -> List[range]:
    """
Remove the range r from the list of ranges.

Examples:
```python
ranges = [range(10,20), range(30,40)]
_removeRange(ranges,range(0,10))   # -> [range(10, 20), range(30, 40)]
_removeRange(ranges,range(0,11))  # -> [range(11, 20), range(30, 40)]
_removeRange(ranges,range(11,15))  # -> [range(10, 11), range(15, 20), range(30, 40)]

_removeRange(ranges,range(25,30))  # -> [range(10, 20), range(30, 40)]
_removeRange(ranges,range(0,25))  # -> [range(30, 40)]

_removeRange(ranges,range(11,11))  # ->[range(10, 20), range(30, 40)]

_removeRange(ranges,range(30,31))  # -> [range(10, 20), range(31, 40)]
_removeRange(ranges,range(100))  # -> []

_removeRange(ranges,range(15,35))  # -> [range(10, 15), range(35, 40)]
```
    """
    new_ranges = []
    for r_ in ranges:
        r_temp = [r_,]
        if r.start in r_ and r.stop in r_:
            if r_.start==r.start:
                r_temp = [range(r.stop,r_.stop),]
                # if r.stop==r_.stop, one has r.stop not in r_
            else:
                r_temp = [range(r_.start,r.start),range(r.stop,r_.stop),]
        elif r.start in r_:
            r_temp = [range(r_.start,r.start),]
        elif r.stop in r_:
            r_temp = [range(r.stop,r_.stop),]
        elif r.start < r_.start:
            if r.stop > r_.stop:
                r_temp = []
            elif r.stop in r_:
                r_temp = [range(r_.start,r.stop),]
        new_ranges += r_temp
    return [r for r in _combineRanges(new_ranges) if r]

def _fusionAttributesList(attributesList):
    """Take a list of dictionnaries, and return a dictionnary of lists"""
    attributesKeys_ = set(k for d in attributesList for k in d.keys())
    attributesDict_ = {k:list() for k in attributesKeys_}
    for attributes in attributesList:
        for attr in attributesKeys_.intersection(attributes.keys()):
            attributesDict_[attr].append(attributes[attr])
        for attr in attributesKeys_.difference(attributes.keys()):
            attributesDict_[attr].append({})
    return attributesDict_

def _fusionAttributesDict(attributesDict):
    """Take a dictionnaries of lists, and return a dictionnary of dictionnaries of lists"""
    attributesDictDict_ = {}
    for key,attributeslist in attributesDict.items():
        attributesDictDict_[key] = _fusionAttributesList(attributeslist)
    return attributesDictDict_

def _fusionAttributes(attributes):
    """Apply the two above methods in a raw"""
    attributesDict_ = _fusionAttributesList(attributes)
    return _fusionAttributesDict(attributesDict_)
