from __future__ import absolute_import
import os
import collections
import csv
import operator
import functools
import warnings

from metaphone import doublemetaphone

__all__ = ['PyNameMatcher']


class PyNameMatcher(object):
    def __init__(self, data_file=None, use_metaphone=False):
        self.use_metaphone = use_metaphone
        if not data_file:
            # search for a datafile if one wasn't provided
            _dir = os.path.dirname(__file__)
            data_file = os.path.join(_dir, 'data', 'names.csv')
            if not os.path.exists(data_file):
                data_file = os.path.join(_dir, os.path.pardir, 'data', 'names.csv')

        if not os.path.exists(data_file):
            raise ValueError('Unable to find a datafile at {}.'.format(data_file))

        lookup = collections.defaultdict(list)
        with open(data_file) as f:
            reader = csv.reader(f)
            for line in reader:
                matches = set(line)
                for match in matches:
                    lookup[match].append(matches)

        self.lookup = lookup
        self.meta_map = {}

        if use_metaphone:
            for n in self.lookup.keys():
                primary, secondary = doublemetaphone(n)
                if primary:
                    if self.meta_map.get(primary):
                        self.meta_map[primary].append(n)
                    else:
                        self.meta_map[primary] = [n]

                if secondary:
                    if self.meta_map.get(secondary):
                        self.meta_map[secondary].append(n)
                    else:
                        self.meta_map[secondary] = [n]

    def match(self, name, use_metaphone=None, remove_match=True, empty_match_returns_none=False):
        name = name.lower()

        if use_metaphone is None:
            use_metaphone = self.use_metaphone

        try:
            names = functools.reduce(operator.or_, self.lookup[name])
            if name in names:
                names.remove(name)
        except TypeError:
            # name not in lookup
            names = set()

        if use_metaphone:
            primary, secondary = doublemetaphone(name)
            try:
                pos_names = self.meta_map.get(primary)
                for pn in pos_names:
                    pmatches = self.match(pn, use_metaphone=False, remove_match=False)
                    if pmatches:
                        names.update(pmatches)

                if len(names) < 1 and secondary:
                    pos_names = self.meta_map.get(secondary)
                    for pn in pos_names:
                        smatches = self.match(pn, use_metaphone=False, remove_match=False)
                        if smatches:
                            names.update(smatches)

            except (IndexError, KeyError, TypeError):
                pass

            if remove_match and name in names:
                names.remove(name)
        
        if len(names) < 1:
            if empty_match_returns_none:
                return None
            else:
                warnings.warn('No match found. (as of 0.2.0 the returned value is an empty set()')

        return names
