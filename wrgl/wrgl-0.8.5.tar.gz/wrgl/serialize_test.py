# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

import typing
from unittest import TestCase

import attr

from wrgl.serialize import json_loads, json_dumps, field_transformer


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Person(object):
    name: str
    birth_date: str
    height: int
    scores: typing.List[int]


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Remote(object):
    url: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Branch(object):
    fetch: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Config(object):
    user: Person
    remotes: typing.List[Remote]
    branch: typing.Dict[str, Branch]


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Receive(object):
    deny_non_fast_forwards: bool
    deny_deletes: bool


class JSONTestCase(TestCase):
    def test_loads_simple(self):
        obj1 = Person(name='John Doe', birth_date='10/02/2000',
                      height=170, scores=[7, 8, 9])
        json_str = json_dumps(obj1)
        self.assertEqual(
            json_str, '{"name": "John Doe", "birthDate": "10/02/2000", "height": 170, "scores": [7, 8, 9]}'
        )
        obj2 = json_loads(json_str, Person)
        self.assertEqual(obj1, obj2)

    def test_loads_with_null(self):
        self.assertEqual(
            json_loads(
                '{"user": null, "remotes": null, "branch": null, "nonExistentKey": null}', Config
            ),
            Config()
        )

    def test_loads_nested(self):
        self.maxDiff = None
        obj1 = Config(
            user=Person(name='John Doe', birth_date='10/02/2000', height=170),
            remotes=[
                Remote(url='https://url1'),
                Remote(url='https://url2'),
            ],
            branch={
                'main': Branch(fetch='refs/heads/main'),
                'test': Branch(fetch='refs/heads/test')
            }
        )
        json_str = json_dumps(obj1, indent=4)
        self.assertEqual(
            json_str, '\n'.join([
                '{',
                '    "user": {',
                '        "name": "John Doe",',
                '        "birthDate": "10/02/2000",',
                '        "height": 170',
                '    },',
                '    "remotes": [',
                '        {',
                '            "url": "https://url1"',
                '        },',
                '        {',
                '            "url": "https://url2"',
                '        }',
                '    ],',
                '    "branch": {',
                '        "main": {',
                '            "fetch": "refs/heads/main"',
                '        },',
                '        "test": {',
                '            "fetch": "refs/heads/test"',
                '        }',
                '    }',
                '}',
            ])
        )
        obj2 = json_loads(json_str, Config)
        self.assertEqual(obj1, obj2)

    def test_loads_ignore_empty(self):
        obj = json_loads('{"denyNonFastForwards": true}', Receive)
        self.assertEqual(obj, Receive(deny_non_fast_forwards=True))
