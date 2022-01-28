# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022 University of Münster.
#
# invenio-subjects-gnd is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""GND term loader."""
import re


class RetainedMatch:
    """Retained Match. More convenient API around matching."""

    _prev_match = None  # act as short lived memento pattern

    @classmethod
    def match(cls, pattern, text):
        """Return re.match but save result until next `match` call."""
        cls._prev_match = re.match(pattern, text)
        return cls._prev_match

    @classmethod
    def group(cls, index):
        """Return matched group from saved match."""
        return cls._prev_match.group(index) if cls._prev_match else None


class GND:
    """GND term extractor."""

    filter_to_dc = {
        'all': r'\d',
        'topics': '1',
        'types': '2',
        'check_tags': '3',
        'geographics': '4'
    }

    @classmethod
    def _pattern(cls, key):
        return r'{} = (.+)'.format(key)

    @classmethod
    def load(cls, filepath, filter='all'):
        """Return array of GND dict."""
        with open(filepath, 'r') as f:
            term = {}

            for line in f.readlines():
                if RetainedMatch.match(GND._pattern('MH'), line):
                    term['MH'] = RetainedMatch.group(1).strip()
                elif RetainedMatch.match(GND._pattern('DC'), line):
                    term['DC'] = RetainedMatch.group(1).strip()
                elif RetainedMatch.match(GND._pattern('UI'), line):
                    term['UI'] = RetainedMatch.group(1).strip()

                    if re.match(term['DC'], GND.filter_to_dc[filter]):
                        yield term

                    term = {}


class GNDReader:
    """GND Reader."""

    def __init__(self, filepath, filter='all'):
        """Constructor."""
        self._filepath = filepath
        self._filter = filter

    def __iter__(self):
        """Iterate over terms."""
        yield from GND.load(self._filepath, self._filter)
