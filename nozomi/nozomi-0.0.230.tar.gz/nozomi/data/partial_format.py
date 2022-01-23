"""
Nozomi
Partial Query Formatting Module
author: hugh@blinkybeach.com
"""


class PartialFormat(dict):

    def __missing__(self, key: str) -> str:
        return '{' + key + '}'
