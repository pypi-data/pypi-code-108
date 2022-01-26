#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class MatchResult:
    def __init__(self, index=-1, data=None):
        self.index = index
        self.data = data


def first_match(match_function, iterable) -> MatchResult:
    i = 0
    for item in iterable:
        if match_function(item):
            return MatchResult(i, item)
        i += 1

    return MatchResult()


def all_matches(match_function, iterable) -> [MatchResult]:
    i = 0
    results = []
    for item in iterable:
        if match_function(item):
            results.append(MatchResult(i, item))
        i += 1

    return results
