# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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


class TagType(object):
    def __init__(self, key, desc, name=None):
        self._key = key
        assert(key.isalpha())
        self._name = name
        self._desc = desc

    def __repr__(self):
        return repr(self._key)

    def __str__(self):
        return repr(self._key)

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name or self._key

    @property
    def desc(self):
        return self._desc

    @property
    def term(self):
        return True

    def to_dict(self):
        return ['T', self._key, self._desc, self._name]


class GroupTagType(TagType):
    def __init__(self, key, tags, desc=None, name=None):
        super().__init__(key, desc, name)
        self._tags = tuple(tags)

    def __getitem__(self, key):
        for tag in self._tags:
            if tag.key == key:
                return tag

        raise KeyError(u'No tag: "{}" in tag group: {}'.format(key, self))

    @property
    def term(self):
        return False

    def __iter__(self):
        for tag in self._tags:
            yield tag

    def to_dict(self):
        return ['G', self._key, self._desc, self._name,
                [tag.to_dict() for tag in self._tags]]


def from_dict(data):
    def inner():
        pass

    if data is None:
        return None

    kind = data[0]
    if kind == 'T':
        key, desc, name = data[1:]
        return TagType(key, desc, name)
    elif kind == 'G':
        key, desc, name, tags = data[1:]
        return GroupTagType(key, tuple([from_dict(tag) for tag in tags]), desc,
                            name)


class LibraryTags:
    def __init__(self):
        self._root = None

    def __getitem__(self, key):
        root = self._root
        parts = key.split('.')
        partiter = iter(parts)
        group = root[next(partiter)]

        for part in partiter:
            group = group[part]

        assert(group.term())
        return group

    def to_dict(self):
        return self._root.to_dict()

    @staticmethod
    def from_dict(data):
        tags = LibraryTags()
        tags._root = from_dict(data)
        return tags

    @staticmethod
    def merge(tagslist):

        def inner(tag1, tag2):
            term1 = tag1.term
            term2 = tag2.term

            if not term1 and not term2:
                tags = []
                mapping1 = {}
                mapping2 = {}
                keys = set()

                for tag in tag1:
                    mapping1[tag.key] = tag
                    keys.add(tag.key)

                for tag in tag2:
                    mapping2[tag.key] = tag
                    keys.add(tag.key)

                for key in keys:
                    if key in set(mapping1).intersection(mapping2):
                        tag1 = mapping1[key]
                        tag2 = mapping2[key]

                        tags.append(inner(tag1, tag2))

                for key in keys - set(mapping2):
                    tags.append(mapping1[key])

                for key in keys - set(mapping1):
                    tags.append(mapping2[key])

                return GroupTagType(tag1.key, tuple(tags), desc=tag1.desc,
                                    name=tag1.name)

            elif not term1 and term2:
                assert(False)
            elif term1 and not term2:
                assert(False)
            else:
                # Both define the same term key, use the first one.
                return tag1

        tagslist = [tags for tags in tagslist if tags.valid]

        if tagslist:
            tagsiter = iter(tagslist)
            root = next(tagsiter)._root

            for tags in tagsiter:
                root = inner(root, tags._root)

            result = LibraryTags()
            result._root = root
            assert(result.valid)
            return result
        else:
            return NullLibraryTags()

    @property
    def valid(self):
        def inner(level, tag):
            if level == 2:
                return tag.term

            if not tag.term:
                return all(inner(level + 1, tag_) for tag_ in tag)

            return False

        return inner(0, self._root)

    @property
    def root(self):
        return self._root


class Tag(object):
    def __init__(self, key):
        self._key = key

    def __getattr__(self, key):
        # Workaround for ipython messing around.
        if key == '_ipython_display_':
            return self._key
        key_ = self._key
        self._key = '.'.join([key_, key])
        return self

    def to_dict(self):
        return self.key

    @property
    def key(self):
        return self._key

    def __str__(self):
        return self._key

    def __repr__(self):
        return repr(str(self))


class TagBuilder(object):
    def __getattribute__(self, key):
        return Tag(key)


class Tags(object):
    def __init__(self, *tags):
        self._tags = tuple(tags)

    def __iter__(self):
        for tag in self._tags:
            yield tag

    def to_dict(self):
        return [tag.to_dict() for tag in self._tags]


class NullLibraryTags(LibraryTags):
    class_tags = (
        GroupTagType(
            'Root',
            []))

    def __init__(self):
        super().__init__()
        self._root = self.class_tags


tag_builder = TagBuilder()
