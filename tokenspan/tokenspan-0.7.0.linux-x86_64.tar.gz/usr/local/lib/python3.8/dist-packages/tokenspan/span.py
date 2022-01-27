#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
`Span` class

Its main original methods are
 - `partition(range(start,stop))` : which partitions the initial `Span` in three
 new `Span` instance, collected in a unique `Spans` instance (see below)
 - `split([range(start,end),range(start2,end2), ...])` : which splits the `Span`
 in several instances grouped in a a list of `Span` objects
 - `slice(start,stop,size,step)` : which slices the initial string from position 
`start` to position `stop` by `step` in sub-strings of size `size`, all grouped 
in a list of Span objects

In addition, one can compare two `Span` using the non-overlapping order `<` and `>` or the overlapping-order `<=` and `>=` when two `Span`s overlap.

Finally, since a `Span` can be seen as a selection of a set of character positions from the parent string, one can apply the basic set operations to two `Span`s, in order to construct more elaborated `Span` instance. 

"""

import warnings

from hashlib import sha1
from .tools import _checkRange, _checkRanges, _startstop, _removeRange
from .tools import _checkSpan, _checkSameString
from .tools import _combineRanges, _cutRanges

class Span():
    """
`Span` object is basically a collection of a parent string named `string`, and a `ranges` collection (list of range) of positions. Its basic usage is its `str` method, which consists in a string extracted from all intervals defined in the `ranges` list, and joined by the `subtoksep` separator.
    """ 
    
    def __init__(self,
                 string='',
                 ranges=None,
                 subtoksep=chr(32),
                 encoding='utf-8'):
        """
`Span` attributes are
 - `Span.string`	 -> a string, default is empty
 - `Span.ranges`	 -> a list of ranges, default is None, in which case the ranges are calculated to contain the entire string
 - `Span.subtoksep`  -> a string, preferably of length 1, default is a white space ' '
 - `Span.encoding`   -> a string, representing the encoding, default is `'utf-8'`
         """
        self.string = str(string)
        self.subtoksep = str(subtoksep)
        self.encoding = str(encoding)
        # construct the ranges only when it is not passed as argument
        # keep empty list in case it is a list
        if ranges is None:
            self.ranges = [range(len(self.string)),] if len(self.string) else []
            return None
        self.ranges = ranges
        # check if ranges are correct
        _checkRanges(self.ranges)
        # correct ranges in case some are over the string size
        ranges_ = [range(*_startstop(self.string,r.start,r.stop))
                   for r in self.ranges]
        # withdraw overlapping ranges
        self.ranges = _combineRanges(ranges_)
        return None

    def _append_range(self, r):
        """Utility that appends a range in self.ranges"""
        _checkRange(r)
        # recasts r.start and r.stop inside the range(0,len(self.string))
        start, stop = _startstop(self.string,r.start,r.stop)
        self.ranges.append(range(start,stop))
        return None

    def append_range(self, r):
        """
Append a range object to self.ranges. The range r must be given in absolute coordinates.
Return self (append in place).
Raise a `ValueError` in case r is not a range object.
Raise a `BoundaryWarning` in case r has start or stop attributes outside the size of Span.string, in which case thse parameters are recalculated to fit Span.string (being either 0 for start or len(Span.string) for stop).
        """
        self._append_range(r)
        self.ranges = [r for r in _combineRanges(self.ranges) if r]
        return self
    
    def append_ranges(self, ranges):
        """
Append a list of range objects to self.ranges. This method applies `append_range` several times, so please see its documentation for more details.
        """
        for r in ranges:
            self._append_range(r)
        self.ranges = [r for r in _combineRanges(self.ranges) if r]
        return self

    def _remove_range(self,r):
        """Utility that removes a range from self.ranges"""
        _checkRange(r)
        self.ranges = _removeRange(self.ranges,r)
        return None

    def remove_range(self,r):
        """
Remove the range r from Span.ranges. The range r must be given in absolute coordinates.
Return self (remove in place).
In case the range r encompass the complete string, there is no more Span.ranges associated to the outcome of this method.
        """
        self._remove_range(r)
        return self

    def remove_ranges(self,ranges):
        """
Remove a list of range objects toself.ranges. This method applies `remove_range` several times, so please see its documentation for more details.
        """
        for r in ranges:
            self._remove_range(r)
        return self

    def __len__(self):
        """Return the length of the string associated with the Span"""
        l = sum(r.stop-r.start for r in self.ranges) 
        l += (len(self.ranges)-1)*len(self.subtoksep)
        return max(l,0) # in case ranges=[], l<0
    
    def __repr__(self):
        """Return the two main elements (namely the `string` and the `ranges` attributes) of a `Span` instance in a readable way."""
        mess = '{}'.format(self.__class__.__name__)
        mess += "('{}', ".format(str(self))
        mess += '['+','.join('('+str(r.start)+','+str(r.stop)+')' 
                             for r in self.ranges)
        mess += "])"
        return mess   
    
    def __str__(self):
        """
`str(Span)` method returns the recombination of the extract of each `Span.subSpan` from the `Span.string` attribute corresponding to all its `Span.ranges` attribute, and joined by the `Span.subtoksep` character.
        """
        return self.subtoksep.join(self.string[r.start:r.stop] 
                                   for r in self.ranges)

    def __hash__(self,):
        """
Make the Span object hashable, such that it can serve for set and dict.keys. Span is constructed on the unicity of the Span object, that is, this is the hash of the string made of the parent string, plus the string representation of the instance, including subtoksep. Everything is then converted to hashlib.sha1.hexdigest
        """
        _bytes_ = bytes(repr(self) + self.string + self.subtoksep,
                        encoding=self.encoding)
        return int(sha1(_bytes_).hexdigest(), 16)
        
    
    def __contains__(self,s):
        """If the object to be compared with is a Span related to the same string as this instance, check whether the ranges are overlapping. Otherwise, check whether the string str(s) (which transforms the other Span instance in a string in case s is not related to the same string) is a sub-string of the `Span` instance."""
        try:
            _checkSpan(s)
        except ValueError:
            b = str(s) in str(self)
        else:
            if s.string==self.string:
                b = any(r1.start<=r2.start and r1.stop>=r2.stop 
                        for r1 in self.ranges for r2 in s.ranges)
            else:
                b = False
        return b
    
    def __bool__(self):
        """Return `True` if the `Span.ranges` is non-empty, otherwise return `False`"""
        return bool(len(self))
    
    def __getitem__(self,n):
        """
Allow slice and integer catch of the elements of the string of `Span`.
Return a string.

Note: As for the usual Python string, a slice with positions outside str(Span) will outcome an empty string, whereas Span[x] with x>len(Span) would results in an IndexError.
        """
        return str(self)[n]

    def get_subSpan(self, n):
        """Alias for get_subspan"""
        warnings.warn("prefer using get_subspan, this method will disapear after version 1.0",
                      DeprecationWarning)
        return self.get_subspan(n)
    
    def get_subspan(self, n):
        """
Get the Span associated to the ranges elements n (being an integer or a slice).
Return a Span object.
Raise an IndexError in case n is larger than the number of ranges in self.ranges.
        """
        span = self.__class__(string=self.string,
                              ranges=[self.ranges[n],],
                              subtoksep=self.subtoksep)          
        return span
    
    @property
    def subSpans(self,):
        """Alias for subspans"""
        warnings.warn("prefer using subspan, this method will disapear after version 1.0",
                      DeprecationWarning)
        return self.subspans
    
    @property
    def subspans(self,):
        """
Get the Span associated to each Span.ranges in a Span object.
Return a list of Span objects.  
        """
        return [self.get_subspan(i) for i in range(len(self.ranges))]

    def __eq__(self, span):
        """
Verify whether the actual instance of Span and an extra ones have the same attributes. 

Returns a boolean.

Raise a ValueError when one object is not a Span instance
        """
        _checkSpan(span)
        bools = [span.string==self.string,
                 span.ranges==self.ranges,
                 span.subtoksep==self.subtoksep,]
        return all(bools)

    def __neq__(self, span):
        """
Verify whether the actual instance of Span and an extra have any differing attribute. 

Returns a boolean.

Raise a ValueError when one object is not a Span instance
        """
        _checkSpan(span)
        bools = [span.string!=self.string,
                 span.ranges!=self.ranges,
                 span.subtoksep!=self.subtoksep,]
        return any(bools)

    def __add__(self, span):
        """If the two Span objects have same strings, returns a new Span object with combined ranges of the initial ones."""
        return self.union(span)

    def __sub__(self, span):
        """If the two Span objects have same strings, returns a new Span object with ranges of self with Span ranges removed. Might returns an empty Span."""
        return self.difference(span)

    def __mul__(self, span):
        """If the two Span objects have same strings, returns a new Span object with ranges of self having intersection with Span ranges removed. Might returns an empty Span."""
        return self.intersection(span)

    def __truediv__(self, span):
        """If the two Span objects have same strings, returns a new Span object with ranges of self having symmetric_difference with Span ranges removed. Might returns an empty Span."""
        return self.symmetric_difference(span)
    
    @property
    def start(self,):
        """Returns the starting position (an integer) of the first ranges. Make sense only for contiguous Span."""
        return self.ranges[0].start
    @property
    def stop(self,):
        """Returns the ending position (an integer) of the last ranges. Make sense only for contiguous Span."""
        return self.ranges[-1].stop
    
    def __lt__(self, span):
        """Returns True if Span is entirely on the left of span (the Span object given as parameter). Make sense only for contiguous Span and non-empty ones."""
        _checkSpan(span)
        _checkSameString(self, span)
        return self.stop <= span.start
    
    def __gt__(self, span):
        """Returns True if Span is entirely on the right of span (the Span object given as parameter). Make sense only for contiguous Span and non-empty ones."""
        _checkSpan(span)
        _checkSameString(self, span)
        return span.stop <= self.start
    
    def __le__(self, span):
        """Returns True if Span is partly on the left of span (the Span object given as parameter). Make sense only for contiguous Span and non-empty ones."""
        _checkSpan(span)
        _checkSameString(self, span)
        exception = self.start == span.start and self.stop < span.stop
        return self.start < span.start < self.stop or exception
    
    def __ge__(self, span):
        """Returns True if Span is partly on the right of span (the Span object given as parameter). Make sense only for contiguous Span and non-empty ones."""
        _checkSpan(span)
        _checkSameString(self, span)
        exception = self.start == span.start and span.stop < self.stop
        return span.start < self.start < span.stop or exception 

    def union(self, span):
        """
Takes a Span object as entry, and returns a new Span instance, with Span.ranges given by the union of the actual Span.ranges with the span.ranges, when one sees the `ranges` attributes as sets of positions of each instance.

| Parameters | Type | Details |
| --- | --- | --- | 
| `span` | `Span` object | A Span object with same mother string (Span.string) and eventually different ranges that the actual instance. |

| Returns | Type | Details |
| --- | --- | --- | 
| `newSpan` | `Span` object | A `Span` object with `newSpan.ranges` = union of `Span.ranges` and `span.ranges` |

| Raises | Details | 
| --- | --- |
| ValueError | in case the entry is not a Span instance. |
| TypeError | in case the span.string is not the same as Span.string. |
        """
        _checkSpan(span)
        _checkSameString(self,span)        
        newSpan = self.__class__(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=self.ranges).append_ranges(span.ranges)
        return newSpan

    def difference(self, span):
        """
Takes a Span object as entry, and returns a new Span instance with Span.ranges given by the difference of the actual Span.ranges with the span.ranges, when one sees the `ranges` attributes as sets of positions of each instance.

| Parameters | Type | Details |
| --- | --- | --- | 
| `span` | `Span` object | A Span object with same mother string (Span.string) and eventually different ranges that the actual instance. |

| Returns | Type | Details |
| --- | --- | --- | 
| `newSpan` | `Span` object | A `Span` object with `newSpan.ranges` = difference of `Span.ranges` and `span.ranges`. |

| Raises | Details | 
| --- | --- |
| ValueError | in case the entry is not a Span instance. |
| TypeError | in case the span.string is not the same as Span.string. |
        """
        _checkSpan(span)
        _checkSameString(self,span)
        newSpan = self.__class__(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=self.ranges).remove_ranges(span.ranges)
        return newSpan
    
    def intersection(self, span):
        """
Takes a Span object as entry and returns a new Span whose Span.ranges given by the intersection of the actual Span.ranges with the span.ranges, when one sees the `ranges` attributes as sets of positions of each instance..

| Parameters | Type | Details |
| --- | --- | --- | 
| `span` | `Span` object | A Span object with same mother string (Span.string) and eventually different ranges that the actual instance. |

| Returns | Type | Details |
| --- | --- | --- | 
| `newSpan` | `Span` object | A `Span` object with `newSpan.ranges` = intersection of `Span.ranges` and `span.ranges` |

| Raises | Details | 
| --- | --- |
| ValueError | in case the entry is not a Span instance. |
| TypeError | in case the span.string is not the same as Span.string. |
        """
        _checkSpan(span)
        _checkSameString(self,span)
        # one uses the fact that AxB = A+B-(A-B)-(B-A)
        # A-B
        AmB = self.__class__(string=self.string,
                             subtoksep=self.subtoksep,
                             ranges=self.ranges).remove_ranges(span.ranges)
        # B-A
        BmA = self.__class__(string=self.string,
                             subtoksep=self.subtoksep,
                             ranges=span.ranges).remove_ranges(self.ranges)
        # A+B
        newSpan = self.__class__(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=span.ranges).append_ranges(self.ranges)
        # A+B - (A-B)
        newSpan.remove_ranges(AmB.ranges)
        # A+B - (A-B) - (B-A)
        newSpan.remove_ranges(BmA.ranges)
        ranges_ = [r for r in _combineRanges(newSpan.ranges) if r]
        newSpan = self.__class__(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=ranges_)
        # withdraw ranges attribute in case it's an empty list
        if not ranges_:
            newSpan.ranges = ranges_
        return newSpan
    
    def symmetric_difference(self, span):
        """
Takes a Span object as entry, and return a new Span instance whose Span.ranges given by the symmetric difference of the actual Span.ranges with the span.ranges, when one sees the `ranges` attributes as sets of positions of each instance.

| Parameters | Type | Details |
| --- | --- | --- | 
| `span` | `Span` object | A Span object with same mother string (Span.string) and eventually different ranges that the actual instance. |

| Returns | Type | Details |
| --- | --- | --- | 
| `newSpan` | `Span` object | A `Span` object with `newSpan.ranges` = symmetric difference of `Span.ranges` and `span.ranges` |

| Raises | Details | 
| --- | --- |
| ValueError | in case the entry is not a Span instance. |
| TypeError | in case the span.string is not the same as Span.string. |
        """
        _checkSpan(span)
        _checkSameString(self,span)
        # one uses the fact that A/B = (A-B)+(B-A)
        # A-B
        AmB = self.__class__(string=self.string,
                             subtoksep=self.subtoksep,
                             ranges=self.ranges).remove_ranges(span.ranges)
        # B-A
        BmA = self.__class__(string=self.string,
                             subtoksep=self.subtoksep,
                             ranges=span.ranges).remove_ranges(self.ranges)
        # does the union of ranges: (A-B)+(B-A)
        ranges_ = []
        ranges_.extend(AmB.ranges)
        ranges_.extend(BmA.ranges)
        ranges_ = [r for r in _combineRanges(ranges_) if r]
        newSpan = self.__class__(string=self.string,
                                 subtoksep=self.subtoksep,
                                 ranges=ranges_)
        return newSpan
      
    def _prepareSpans(self,ranges,remove_empty):
        """Utility that removes empty ranges and constructs a list of Span objects."""
        if remove_empty:
            ranges = [r for r in ranges if any(r_ for r_ in r) or len(r)==2]
        spans = [self.__class__(string=self.string,
                                ranges=r,
                                subtoksep=self.subtoksep)
                  for r in ranges]
        return spans
    
    def partition(self, start, stop, remove_empty=False):
        """
Split the `Span.string` in three `Span` objects : 
 - `string[:start]`
 - `string[start:stop]`
 - `string[stop:]`
and put all non-empty `Span` objects in a list of `Span` instances.

It acts a bit like the `str.partition(s)` method of the Python
`string` object, but `Span.partition` takes `start` and `stop` 
argument instead of a string. 

| Parameters | Type | Details |
| --- | --- | --- | 
| `start` | int | Starting position of the splitting sequence. |
| `stop` | int | Ending position of the splitting sequence. |
| `remove_empty` | bool. Default is `False` | If `True`, returns a `list of Span` instance with only non-empty `Span` objects. see `__bool__()` method for non-empty `Span` |

| Returns | Type | Details |
| --- | --- | --- | 
| `spans` | `list` of `Span` objects | The `list` object containing the different `Span` objects. |
        """
        start,stop = _startstop(self,start,stop)
        r1,temp_ranges = _cutRanges(self.ranges,start,step=len(self.subtoksep))
        r2,r3 = _cutRanges(temp_ranges,stop-start,step=len(self.subtoksep))
        ranges = [r1,r2,r3]
        spans = self._prepareSpans(ranges,remove_empty)
        return spans
    
    def split(self, cuts, remove_empty=False):
        """
Split a text as many times as there are range entities in the cuts list.
Return a list of `Span` instances.

This is a bit like `str.split(s)` method from Python `string`
object, except one has to feed `Span.split` with a full list
of `range(start,stop)` range objects instead of the string 's' in `str.split(s)`
If the `range(start,stop)` tuples in cuts are given by a regex re.finditer
search on `str(Span)`, the two methods give the same thing. 

| Parameters | Type | Details |
| --- | --- | --- | 
| `cuts` | a list of `range(start,stop,)` range objects. start/stop are integer | Basic usage is to take these cuts from [`re.finditer`](https://docs.python.org/3/library/re.html#re.finditer). The start/end integers are given in the relative coordinate system, that is, in terms of the position in `str(Span)`. |
| `remove_empty` | bool. Default is `False` | If `True`, returns a `list of Span` instance with only non-empty `Span` objects. see `__bool__()` method for non-empty `Span` |

| Return | Type | Details |
| --- | --- | --- | 
| `spans` | `list` of `Span` objects | The `list` object containing the different `Span` objects. |

        """
        _checkRanges(cuts)
        split_ranges = list()
        r1,r_temp = _cutRanges(self.ranges,cuts[0].start,step=len(self.subtoksep))
        r2,r_temp = _cutRanges(r_temp,len(cuts[0]),step=len(self.subtoksep))
        cursor = cuts[0].stop
        split_ranges += [r1,r2,]
        if len(cuts) < 2:
            return self._prepareSpans(split_ranges + [r_temp,], remove_empty)
        for r in cuts[1:]:
            r1,r_temp = _cutRanges(r_temp,r.start-cursor,step=len(self.subtoksep))
            r2,r_temp = _cutRanges(r_temp,len(r),step=len(self.subtoksep))
            split_ranges += [r1,r2,]
            cursor = r.stop
        split_ranges.append(r_temp)
        spans = self._prepareSpans(split_ranges, remove_empty)      
        return spans

    def slice(self, start=0, stop=None, size=1, step=1, remove_empty=False):
        """
Cut the `Span.string` in overlapping sequences of strings of size `size` by `step`,
put all these sequences in separated `Span` objects, and finally 
put all theses objects in a list of `Span` instances.

| Parameters | Type | Details |
| --- | --- | --- | 
| `start` | int | The relative position where to start slicing the Span. |
| `stop` | int | The relative position where to stop slicing the Span. |
| `size` | int | The size of the string in each subsequent Span objects. |
| `step` | int | The number of characters skipped from one Span object to the next one. A character is given by `str(Span)` (called relative position) |

| Returns | Type | Details |
| --- | --- | --- | 
| `spans` | `list` of `Span` objects | The `list` object containing the different `Span` objects. |
        """
        start, stop = _startstop(self,start,stop)
        cuts = [(i,i+size) for i in range(start,stop-size+1,step)]
        slice_ranges = list()
        for start,end in cuts:
            r1,temp_ranges = _cutRanges(self.ranges,start,step=len(self.subtoksep))
            r2,r3 = _cutRanges(temp_ranges,end-start,step=len(self.subtoksep))
            slice_ranges.append(r2)
        spans = self._prepareSpans(slice_ranges,remove_empty)
        return spans
