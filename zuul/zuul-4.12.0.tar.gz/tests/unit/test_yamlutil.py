# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from zuul.lib import yamlutil
from tests.base import BaseTestCase

import testtools


class TestYamlDumper(BaseTestCase):
    def test_load_normal_data(self):
        expected = {'foo': 'bar'}
        data = 'foo: bar\n'
        out = yamlutil.safe_load(data)
        self.assertEqual(out, expected)

        out = yamlutil.encrypted_load(data)
        self.assertEqual(out, expected)

    def test_load_encrypted_data(self):
        expected = {'foo': yamlutil.EncryptedPKCS1_OAEP('YmFy')}
        self.assertEqual(expected['foo'].ciphertext, b'bar')
        data = "foo: !encrypted/pkcs1-oaep YmFy\n"

        out = yamlutil.encrypted_load(data)
        self.assertEqual(out, expected)

        with testtools.ExpectedException(
                yamlutil.yaml.constructor.ConstructorError):
            out = yamlutil.safe_load(data)

    def test_dump_normal_data(self):
        data = {'foo': 'bar'}
        expected = 'foo: bar\n'
        out = yamlutil.safe_dump(data, default_flow_style=False)
        self.assertEqual(out, expected)

        out = yamlutil.encrypted_dump(data, default_flow_style=False)
        self.assertEqual(out, expected)

    def test_dump_encrypted_data(self):
        data = {'foo': yamlutil.EncryptedPKCS1_OAEP('YmFy')}
        self.assertEqual(data['foo'].ciphertext, b'bar')
        expected = "foo: !encrypted/pkcs1-oaep YmFy\n"

        out = yamlutil.encrypted_dump(data, default_flow_style=False)
        self.assertEqual(out, expected)

        with testtools.ExpectedException(
                yamlutil.yaml.representer.RepresenterError):
            out = yamlutil.safe_dump(data, default_flow_style=False)

    def test_ansible_dumper(self):
        data = {'foo': 'bar'}
        data = yamlutil.mark_strings_unsafe(data)
        expected = "foo: !unsafe 'bar'\n"
        yaml_out = yamlutil.ansible_unsafe_dump(data, default_flow_style=False)
        self.assertEqual(yaml_out, expected)

        data = {'foo': {'bar': 'baz'}, 'list': ['bar', 1, 3.0, True, None]}
        data = yamlutil.mark_strings_unsafe(data)
        expected = """\
foo:
  bar: !unsafe 'baz'
list:
- !unsafe 'bar'
- 1
- 3.0
- true
- null
"""
        yaml_out = yamlutil.ansible_unsafe_dump(data, default_flow_style=False)
        self.assertEqual(yaml_out, expected)

    def test_ansible_dumper_with_aliases(self):
        foo = {'bar': 'baz'}
        data = {'foo1': foo, 'foo2': foo}
        expected = """\
foo1: &id001
  bar: baz
foo2: *id001
"""
        yaml_out = yamlutil.ansible_unsafe_dump(data, default_flow_style=False)
        self.assertEqual(yaml_out, expected)

    def test_ansible_dumper_ignore_aliases(self):
        foo = {'bar': 'baz'}
        data = {'foo1': foo, 'foo2': foo}
        expected = """\
foo1:
  bar: baz
foo2:
  bar: baz
"""
        yaml_out = yamlutil.ansible_unsafe_dump(
            data,
            ignore_aliases=True,
            default_flow_style=False)
        self.assertEqual(yaml_out, expected)
