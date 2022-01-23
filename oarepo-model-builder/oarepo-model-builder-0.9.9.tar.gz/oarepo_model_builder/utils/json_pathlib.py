import re
from collections import OrderedDict, namedtuple
from functools import cached_property
from typing import List, Iterable

"""
A path is a sequence of names separated by '/' with an optional 
condition applied to the subtree.

The condition is a function taking current:PathCondition as a single parameter
which can be used for example as: 
current.a.b == "data" or current["a"]["b"] == "data" 

Any expression with the current should return an iterator or list of results (matched subtrees).
If any is truish, the condition is interpreted as matching.
"""

JSONPathRecord = namedtuple('JSONPathRecord', 'path, condition, value')


class JSONPaths:
    def __init__(self):
        self.path_regex_list = []
        self.path_to_index = {}
        self.paths: List[List[JSONPathRecord]] = []

    def register(self, path, condition=None, value=None):
        """
        paths should be registered from longest to shortest

        :param path:        a path to register
        :param condition:   a condition applied to the node on the path
        :param value:       the value to return if path & condition match
        """

        if path not in self.path_to_index:
            self.path_to_index[path] = len(self.path_to_index)
            self.paths.append([])
            self.path_regex_list.append(path_to_regex(path))
        path_locators = self.paths[self.path_to_index[path]]
        path_locators.append(JSONPathRecord(
            path=path,
            condition=condition,
            value=value
        ))

    @cached_property
    def path_regex(self):
        return re.compile('|'.join(f'({x})' for x in self.path_regex_list))

    def match(self, path=None, subtree=None, extra_data=None):
        """
        Matches a path and subtree against stored paths. Returns iterator of matched values

        :param path:        the path that should match
        :param subtree:     teh subtree against which to match stored conditions
        :return:            iterator of matched values
        """
        match = self.path_regex.match(path)
        if not match:
            return None
        for idx, grp in enumerate(match.groups()):
            if grp:
                matched = False
                for rec in self.paths[idx]:
                    if rec.condition:
                        condition_result = rec.condition(PathCondition(subtree), **(extra_data or {}))
                        if isinstance(condition_result, Iterable):
                            condition_result = any(condition_result)
                        if condition_result:
                            matched = True
                            yield rec.value
                    else:
                        matched = True
                        yield rec.value

                if matched:
                    break


def path_to_regex(path):
    split_path = [x for x in re.split('(/)', path) if x]

    def fragment_to_regex(f):
        if f == '**':
            return '.+'
        return f.replace('*', '[^/]+')

    return ''.join(fragment_to_regex(x) for x in split_path)


class PathCondition:
    def __init__(self, start=None, subtree_list=()):
        self._subtree_list = [*subtree_list]
        if start:
            self._subtree_list.append(start)

    def _apply(self, p, subtree_list):
        if subtree_list:
            if p == '*':
                for subtree in subtree_list:
                    itr = []
                    if isinstance(subtree, dict):
                        itr = subtree.values()
                    elif isinstance(subtree, list):
                        itr = subtree
                    yield from itr
            elif p == '**':
                first_level = list(self._apply('*', subtree_list))
                yield from first_level
                yield from self._apply('**', first_level)
            else:
                for subtree in subtree_list:
                    # match the path element and descend if found
                    if isinstance(subtree, dict):
                        if p in subtree:
                            yield subtree[p]
                    elif isinstance(subtree, list):
                        if isinstance(p, int) and 0 <= p < len(subtree):
                            yield subtree[p]

    def __getattr__(self, item):
        try:
            item = int(item)
        except:
            pass
        return PathCondition(subtree_list=list(self._apply(item, self._subtree_list)))

    def __getitem__(self, item):
        return PathCondition(subtree_list=list(self._apply(item, self._subtree_list)))

    def __eq__(self, other):
        if isinstance(other, PathCondition):
            # TODO: deep equals maybe
            return [subtree for subtree in self._subtree_list for o in other._subtree_list if subtree == o]

        # TODO: deep equals maybe
        return [subtree for subtree in self._subtree_list if subtree == other]
