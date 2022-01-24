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

import re
import subprocess

from zuul.driver.sql import SQLDriver
from zuul.zk import ZooKeeperClient
from tests.base import (
    BaseTestCase, MySQLSchemaFixture, PostgresqlSchemaFixture
)


class DBBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.setupZK()

        self.zk_client = ZooKeeperClient(
            self.zk_chroot_fixture.zk_hosts,
            tls_cert=self.zk_chroot_fixture.zookeeper_cert,
            tls_key=self.zk_chroot_fixture.zookeeper_key,
            tls_ca=self.zk_chroot_fixture.zookeeper_ca
        )
        self.addCleanup(self.zk_client.disconnect)
        self.zk_client.connect()


class TestMysqlDatabase(DBBaseTestCase):
    def setUp(self):
        super().setUp()

        f = MySQLSchemaFixture()
        self.useFixture(f)

        config = dict(dburi=f.dburi)
        driver = SQLDriver()
        self.connection = driver.getConnection('database', config)
        self.connection.onLoad(self.zk_client)
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        self.connection.onStop()

    def compareMysql(self, alembic_text, sqlalchemy_text):
        alembic_lines = alembic_text.split('\n')
        sqlalchemy_lines = sqlalchemy_text.split('\n')
        self.assertEqual(len(alembic_lines), len(sqlalchemy_lines))
        alembic_constraints = []
        sqlalchemy_constraints = []
        for i in range(len(alembic_lines)):
            if alembic_lines[i].startswith("  `"):
                # Column
                self.assertEqual(alembic_lines[i], sqlalchemy_lines[i])
            elif alembic_lines[i].startswith("  "):
                # Constraints can be unordered
                # strip trailing commas since the last line omits it
                alembic_constraints.append(
                    re.sub(',$', '', alembic_lines[i]))
                sqlalchemy_constraints.append(
                    re.sub(',$', '', sqlalchemy_lines[i]))
            else:
                self.assertEqual(alembic_lines[i], sqlalchemy_lines[i])
        alembic_constraints.sort()
        sqlalchemy_constraints.sort()
        self.assertEqual(alembic_constraints, sqlalchemy_constraints)

    def test_migration(self):
        # Test that SQLAlchemy create_all produces the same output as
        # a full migration run.
        sqlalchemy_tables = {}
        with self.connection.engine.begin() as connection:
            connection.exec_driver_sql("set foreign_key_checks=0")
            for table in connection.exec_driver_sql("show tables"):
                table = table[0]
                sqlalchemy_tables[table] = connection.exec_driver_sql(
                    f"show create table {table}").one()[1]
                connection.exec_driver_sql(f"drop table {table}")
            connection.exec_driver_sql("set foreign_key_checks=1")

        self.connection.force_migrations = True
        self.connection.onLoad(self.zk_client)
        with self.connection.engine.begin() as connection:
            for table in connection.exec_driver_sql("show tables"):
                table = table[0]
                create = connection.exec_driver_sql(
                    f"show create table {table}").one()[1]
                self.compareMysql(create, sqlalchemy_tables[table])

    def test_buildsets(self):
        tenant = 'tenant1',
        buildset_uuid = 'deadbeef'
        change = 1234
        buildset_args = dict(
            uuid=buildset_uuid,
            tenant=tenant,
            pipeline='check',
            project='project',
            change=change,
            patchset='1',
            ref='',
            oldrev='',
            newrev='',
            branch='master',
            zuul_ref='Zdeadbeef',
            ref_url='http://example.com/1234',
            event_id='eventid',
        )

        # Create the buildset entry (driver-internal interface)
        with self.connection.getSession() as db:
            db.createBuildSet(**buildset_args)

        # Verify that worked using the driver-external interface
        self.assertEqual(len(self.connection.getBuildsets()), 1)
        self.assertEqual(self.connection.getBuildsets()[0].uuid, buildset_uuid)

        # Update the buildset using the internal interface
        with self.connection.getSession() as db:
            db_buildset = db.getBuildset(tenant=tenant, uuid=buildset_uuid)
            self.assertEqual(db_buildset.change, change)
            db_buildset.result = 'SUCCESS'

        # Verify that worked
        db_buildset = self.connection.getBuildset(
            tenant=tenant, uuid=buildset_uuid)
        self.assertEqual(db_buildset.result, 'SUCCESS')


class TestPostgresqlDatabase(DBBaseTestCase):
    def setUp(self):
        super().setUp()

        f = PostgresqlSchemaFixture()
        self.useFixture(f)
        self.db = f

        config = dict(dburi=f.dburi)
        driver = SQLDriver()
        self.connection = driver.getConnection('database', config)
        self.connection.onLoad(self.zk_client)
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        self.connection.onStop()

    def test_migration(self):
        # Test that SQLAlchemy create_all produces the same output as
        # a full migration run.
        sqlalchemy_out = subprocess.check_output(
            f"pg_dump -h {self.db.host} -U {self.db.name} -s {self.db.name}",
            shell=True,
            env={'PGPASSWORD': self.db.passwd}
        )

        with self.connection.engine.begin() as connection:
            tables = [x[0] for x in connection.exec_driver_sql(
                "select tablename from pg_catalog.pg_tables "
                "where schemaname='public'"
            ).all()]

            self.assertTrue(len(tables) > 0)
            for table in tables:
                connection.exec_driver_sql(f"drop table {table} cascade")

        self.connection.force_migrations = True
        self.connection.onLoad(self.zk_client)

        alembic_out = subprocess.check_output(
            f"pg_dump -h {self.db.host} -U {self.db.name} -s {self.db.name}",
            shell=True,
            env={'PGPASSWORD': self.db.passwd}
        )
        self.assertEqual(alembic_out, sqlalchemy_out)
