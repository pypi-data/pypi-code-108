#! /usr/bin/env python3
"""
Module _UTILS -- PLIB3 Collection Utility Functions
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

These are some helpful utility functions for the PLIB3
collection classes. Currently provided are:

function inrange -- returns index forced to be >= low, <= high.

function normalize -- returns index with negative values normalized
    relative to count.

function normalize_slice -- returns a list of indexes "covered" by a
    slice (normalized relative to count), or an integer giving the
    index to which a zero-length slice refers (normalized relative
    to count).

function slice_len -- returns the "length" of a slice (meaning the
    number of indexes that would be affected if it were used as an
    index into a sequence).
"""


def inrange(index, v1, v2):
    """Force index to be within the range v1 to v2, and return result.
    """
    if v1 < v2:
        low = v1
        high = v2
    else:
        low = v2
        high = v1
    return min(max(index, low), high)


def normalize(count, index, noraise=False):
    """Return index with negative values normalized to count.
    
    Index values out of range after conversion will raise ``IndexError``
    unless ``noraise`` is true.
    """
    
    if index < 0:
        result = index + count
    else:
        result = index
    if ((result < 0) or (result > count - 1)) and not noraise:
        raise IndexError("sequence index out of range")
    return result


def normalize_slice(count, index):
    """Return slice index normalized to count.
    
    Return one of the following, depending on the type of slice index:
    
    - For a non-empty slice (e.g., [x:y] where x != y), return a list of
      indexes to be affected;
    
    - For an empty slice (e.g., [x:x]), return the slice location (x)
      as an int.
    
    - For extended slices, if start and stop are the same, return an
      empty list; otherwise treat as a non-empty slice.
    
    The index(es) returned will be normalized relative to count, and indexes
    out of range after normalization will be truncated to range(0, count + 1).
    The extra index at count is to allow for the possibility of an append
    (a zero-length slice with index == count). Note that this means that,
    unlike the normalize function above, this function will never throw an
    exception due to values being out of range; this is consistent with the
    observed semantics of Python slice syntax, where even values way out of
    range are accepted and truncated to zero or the end of the sequence.
    The only exception this routine will throw is ValueError for a zero
    slice step.
    
    Note that if ``count`` is ``None``, any slice parameters that would require
    normalization (such as a negative ``start`` or ``stop``, a ``stop`` of
    ``None``, or a ``start`` of ``None`` with a negative ``step``) will raise
    ``IndexError``; this allows this function to be used transparently by
    sequences that have no known length, while still checking and processing
    slice indexes that are valid.
    """
    
    if index.step is None:
        step = 1
    else:
        step = int(index.step)
    if step == 0:
        raise ValueError("Slice step cannot be zero.")
    if index.start is None:
        if step < 0:
            if count is None:
                raise IndexError("sequence index out of range")
            start = count - 1
        else:
            start = 0
    else:
        start = int(index.start)
        if start < 0:
            if count is None:
                raise IndexError("sequence index out of range")
            start += count
    if index.stop is None:
        if step < 0:
            stop = -1
        else:
            if count is None:
                raise IndexError("sequence index out of range")
            stop = count
    else:
        stop = int(index.stop)
        if stop < 0:
            if count is None:
                raise IndexError("sequence index out of range")
            stop += count
    if start == stop:
        if step != 1:
            return []
        if count is None:
            return start
        return inrange(start, 0, count)
    elif (count is not None) and (
            (count == 0) or
            ((step > 0) and ((start >= count) or (start > stop))) or
            ((step < 0) and ((start < 0) or (start < stop)))):
        return []
    else:
        if count is not None:
            start = inrange(start, 0, count - 1)
            if step < 0:
                stop = inrange(stop, -1, count - 1)
            else:
                stop = inrange(stop, 0, count)
        return list(range(start, stop, step))


def slice_len(s):
    """Return the number of indexes referenced by a slice.
    
    Note that we do not normalize the slice indexes, since we don't
    have a sequence length to reference them to. Also note that,
    because of this, we have to return None if there is no stop value,
    or if start or stop are negative.
    """
    
    if s.start is None:
        start = 0
    else:
        start = int(s.start)
    if start < 0:
        return None
    if s.stop is None:
        return None
    stop = int(s.stop)
    if stop < 0:
        return None
    if s.step is None:
        step = 1
    else:
        step = int(s.step)
    if step == 0:
        raise ValueError("Slice step cannot be zero.")
    if start == stop:
        return 0
    else:
        return (stop - start) // step
