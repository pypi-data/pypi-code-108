# This file is part of Sympathy for Data.
# Copyright (c) 2018 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import re


_regex_escape = '()[].*\\+${}^-,*?|'


def highlight_patterns(pattern, flags=re.IGNORECASE):
    pattern_list = _pattern_list(pattern)
    if pattern_list:
        pattern = '.*?\\b[^\\b]*?'.join(f'({p})' for p in pattern_list)
        pattern = f'^.*?{pattern}.*?$'
    else:
        pattern = '.*'
    return re.compile(pattern, flags)


def highlight_word_patterns(pattern, flags=re.IGNORECASE):
    pattern_list = _pattern_list(pattern)
    if pattern_list:
        pattern = '.*?\\b[^\\b]*?'.join(f'\\b(\w*?{p}\w*)\\b' for p in pattern_list)
        pattern = f'^.*?{pattern}.*?$'
    else:
        pattern = '.*'
    return re.compile(pattern, flags)


def _pattern_list(pattern):
    patterns = []

    if pattern:
        words = pattern

        if isinstance(pattern, str):
            words = pattern.split(' ')
        for word in [w for w in words if w]:
            sub_patterns = []

            for c in word:
                if c in _regex_escape:
                    sub_patterns.append(f'\\{c}')
                else:
                    sub_patterns.append(c)
            patterns.append(''.join(sub_patterns))
    return patterns


def fuzzy_pattern(pattern, flags=re.IGNORECASE):
    """Fuzzy word based partern."""
    pattern_list = _pattern_list(pattern)
    if pattern_list:
        pattern = '.*?\\b[^\\b]*?'.join(pattern_list)
        pattern = f'^.*?{pattern}.*?$'
    else:
        pattern = '.*'
    return re.compile(pattern, flags)


def fuzzy_free_pattern(pattern, flags=re.IGNORECASE):
    """
    Fuzzy free partern.

    Pattern similar to fuzzy_pattern, differs in that it does not
    consider word boundaries, this makes it useful to match strings
    such as variable names that are are only one word long.
    """
    pattern_list = _pattern_list(pattern)
    if pattern_list:
        pattern = '(.*)'.join(pattern_list)
        pattern = f'^.*{pattern}.*$'
    else:
        pattern = '.*'
    return re.compile(pattern, flags)


def matches(compiled_pattern, text):
    res = True
    if compiled_pattern:
        res = False
        if compiled_pattern.match(text):
            res = True
    return res
