#!/usr/bin/env python3
# coding: utf-8

import re


class RegexTester(object):
    def __init__(self, regexes=None, strings=None):
        self.regexes = regexes or []
        self.strings = strings or []

    def check_all_regexes(self, string):
        return [r.search(string) for r in self.regexes]

    def check_all_strings(self, pattern):
        return [re.search(pattern, s) for s in self.strings]


RegexGroup = RegexTester
