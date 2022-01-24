# Copyright 2018 Red Hat, Inc.
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

import io
import os
import sys
import subprocess
import time

import configparser
import fixtures
import jwt
import testtools
from kazoo.exceptions import NoNodeError

from zuul.zk import ZooKeeperClient

from tests.base import BaseTestCase, ZuulTestCase
from tests.base import FIXTURE_DIR


class BaseClientTestCase(BaseTestCase):
    config_file = 'zuul.conf'
    config_with_zk = True

    def setUp(self):
        super(BaseClientTestCase, self).setUp()
        self.test_root = self.useFixture(fixtures.TempDir(
            rootdir=os.environ.get("ZUUL_TEST_ROOT"))).path
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(FIXTURE_DIR, self.config_file))
        if self.config_with_zk:
            self.config_add_zk()

    def config_add_zk(self):
        self.setupZK()
        self.config.add_section('zookeeper')
        self.config.set('zookeeper', 'hosts', self.zk_chroot_fixture.zk_hosts)
        self.config.set('zookeeper', 'session_timeout', '30')
        self.config.set('zookeeper', 'tls_cert',
                        self.zk_chroot_fixture.zookeeper_cert)
        self.config.set('zookeeper', 'tls_key',
                        self.zk_chroot_fixture.zookeeper_key)
        self.config.set('zookeeper', 'tls_ca',
                        self.zk_chroot_fixture.zookeeper_ca)


class TestTenantValidationClient(BaseClientTestCase):
    config_with_zk = True

    def test_client_tenant_conf_check(self):
        self.config.set(
            'scheduler', 'tenant_config',
            os.path.join(FIXTURE_DIR, 'config/tenant-parser/simple.yaml'))
        with open(os.path.join(self.test_root, 'tenant_ok.conf'), 'w') as f:
            self.config.write(f)
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', os.path.join(self.test_root, 'tenant_ok.conf'),
             'tenant-conf-check'], stdout=subprocess.PIPE)
        p.communicate()
        self.assertEqual(p.returncode, 0, 'The command must exit 0')

        self.config.set(
            'scheduler', 'tenant_config',
            os.path.join(FIXTURE_DIR, 'config/tenant-parser/invalid.yaml'))
        with open(os.path.join(self.test_root, 'tenant_ko.conf'), 'w') as f:
            self.config.write(f)
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', os.path.join(self.test_root, 'tenant_ko.conf'),
             'tenant-conf-check'], stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.assertEqual(p.returncode, 1, "The command must exit 1")
        self.assertIn(
            b"expected a dictionary for dictionary", out,
            "Expected error message not found")


class TestWebTokenClient(BaseClientTestCase):
    config_file = 'zuul-admin-web.conf'

    def test_no_authenticator(self):
        """Test that token generation is not possible without authenticator"""
        old_conf = io.StringIO()
        self.config.write(old_conf)
        self.config.remove_section('auth zuul_operator')
        with open(os.path.join(self.test_root,
                               'no_zuul_operator.conf'), 'w') as f:
            self.config.write(f)
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', os.path.join(self.test_root, 'no_zuul_operator.conf'),
             'create-auth-token',
             '--auth-config', 'zuul_operator',
             '--user', 'marshmallow_man',
             '--tenant', 'tenant_one', ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        old_conf.seek(0)
        self.config = configparser.ConfigParser()
        self.config.read_file(old_conf)
        self.assertEqual(p.returncode, 1, 'The command must exit 1')

    def test_unsupported_driver(self):
        """Test that token generation is not possible with wrong driver"""
        old_conf = io.StringIO()
        self.config.write(old_conf)
        self.config.add_section('auth someauth')
        self.config.set('auth someauth', 'driver', 'RS256withJWKS')
        with open(os.path.join(self.test_root, 'JWKS.conf'), 'w') as f:
            self.config.write(f)
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', os.path.join(self.test_root, 'JWKS.conf'),
             'create-auth-token',
             '--auth-config', 'someauth',
             '--user', 'marshmallow_man',
             '--tenant', 'tenant_one', ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        old_conf.seek(0)
        self.config = configparser.ConfigParser()
        self.config.read_file(old_conf)
        self.assertEqual(p.returncode, 1, 'The command must exit 1')

    def test_token_generation(self):
        """Test token generation"""
        with open(os.path.join(self.test_root, 'good.conf'), 'w') as f:
            self.config.write(f)
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', os.path.join(self.test_root, 'good.conf'),
             'create-auth-token',
             '--auth-conf', 'zuul_operator',
             '--user', 'marshmallow_man',
             '--tenant', 'tenant_one', ],
            stdout=subprocess.PIPE)
        now = time.time()
        out, _ = p.communicate()
        self.assertEqual(p.returncode, 0, 'The command must exit 0')
        self.assertTrue(out.startswith(b"Bearer "), out)
        # there is a trailing carriage return in the output
        token = jwt.decode(out[len("Bearer "):-1],
                           key=self.config.get(
                               'auth zuul_operator',
                               'secret'),
                           algorithms=[self.config.get(
                               'auth zuul_operator',
                               'driver')],
                           audience=self.config.get(
                               'auth zuul_operator',
                               'client_id'),)
        self.assertEqual('marshmallow_man', token.get('sub'))
        self.assertEqual('zuul_operator', token.get('iss'))
        self.assertEqual('zuul.example.com', token.get('aud'))
        admin_tenants = token.get('zuul', {}).get('admin', [])
        self.assertTrue('tenant_one' in admin_tenants, admin_tenants)
        # allow one minute for the process to run
        self.assertTrue(580 <= int(token['exp']) - now < 660,
                        (token['exp'], now))


class TestKeyOperations(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_export_import(self):
        # Test a round trip export/import of keys
        export_root = os.path.join(self.test_root, 'export')
        config_file = os.path.join(self.test_root, 'zuul.conf')
        with open(config_file, 'w') as f:
            self.config.write(f)

        # Save a copy of the keys in ZK
        old_data = self.getZKTree('/keystorage')

        # Export keys
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'export-keys', export_root],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        # Delete keys from ZK
        self.zk_client.client.delete('/keystorage', recursive=True)

        # Make sure it's really gone
        with testtools.ExpectedException(NoNodeError):
            self.getZKTree('/keystorage')

        # Import keys
        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'import-keys', export_root],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        # Make sure the new data matches the original
        new_data = self.getZKTree('/keystorage')
        self.assertEqual(new_data, old_data)

    def test_copy_delete(self):
        config_file = os.path.join(self.test_root, 'zuul.conf')
        with open(config_file, 'w') as f:
            self.config.write(f)

        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'copy-keys',
             'gerrit', 'org/project',
             'gerrit', 'neworg/newproject',
             ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        data = self.getZKTree('/keystorage')
        self.assertEqual(
            data['/keystorage/gerrit/org/org%2Fproject/secrets'],
            data['/keystorage/gerrit/neworg/neworg%2Fnewproject/secrets'])
        self.assertEqual(
            data['/keystorage/gerrit/org/org%2Fproject/ssh'],
            data['/keystorage/gerrit/neworg/neworg%2Fnewproject/ssh'])

        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'delete-keys',
             'gerrit', 'org/project',
             ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        data = self.getZKTree('/keystorage')
        self.assertIsNone(
            data.get('/keystorage/gerrit/org/org%2Fproject/secrets'))
        self.assertIsNone(
            data.get('/keystorage/gerrit/org/org%2Fproject/ssh'))
        self.assertIsNone(
            data.get('/keystorage/gerrit/org/org%2Fproject'))
        # Ensure that deleting one project in a tree doesn't remove other
        # projects in that tree.
        self.assertIsNotNone(
            data.get('/keystorage/gerrit/org/org%2Fproject1'))
        self.assertIsNotNone(
            data.get('/keystorage/gerrit/org/org%2Fproject2'))
        self.assertIsNotNone(
            data.get('/keystorage/gerrit/org'))

        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'delete-keys',
             'gerrit', 'org/project1',
             ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'delete-keys',
             'gerrit', 'org/project2',
             ],
            stdout=subprocess.PIPE)
        out, _ = p.communicate()
        self.log.debug(out.decode('utf8'))
        self.assertEqual(p.returncode, 0)

        data = self.getZKTree('/keystorage')
        # Ensure that the last project being removed also removes its
        # org prefix entry.
        self.assertIsNone(
            data.get('/keystorage/gerrit/org/org%2Fproject1'))
        self.assertIsNone(
            data.get('/keystorage/gerrit/org/org%2Fproject2'))
        self.assertIsNone(
            data.get('/keystorage/gerrit/org'))


class TestZKOperations(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def shutdown(self):
        pass

    def assertFinalState(self):
        pass

    def test_delete_state(self):
        # Shut everything down (as much as possible) to reduce
        # logspam and errors.
        ZuulTestCase.shutdown(self)

        # Re-start the client connection because we need one for the
        # test.
        self.zk_client = ZooKeeperClient.fromConfig(self.config)
        self.zk_client.connect()

        config_file = os.path.join(self.test_root, 'zuul.conf')
        with open(config_file, 'w') as f:
            self.config.write(f)

        # Save a copy of the keys in ZK
        old_data = self.getZKTree('/keystorage')

        p = subprocess.Popen(
            [os.path.join(sys.prefix, 'bin/zuul'),
             '-c', config_file,
             'delete-state',
             ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        out, _ = p.communicate(b'yes\n')
        self.log.debug(out.decode('utf8'))

        # Make sure the keys are still around
        new_data = self.getZKTree('/keystorage')
        self.assertEqual(new_data, old_data)

        # Make sure we really deleted everything
        with testtools.ExpectedException(NoNodeError):
            self.getZKTree('/zuul')

        self.zk_client.disconnect()
