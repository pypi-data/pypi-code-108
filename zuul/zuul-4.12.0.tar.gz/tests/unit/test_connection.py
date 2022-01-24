# Copyright 2014 Rackspace Australia
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
import configparser
import os
import re
import textwrap
import time
import types

import sqlalchemy as sa

import zuul
from zuul.lib import yamlutil
from tests.base import ZuulTestCase, FIXTURE_DIR, \
    PostgresqlSchemaFixture, MySQLSchemaFixture, \
    BaseTestCase, AnsibleZuulTestCase


class TestConnections(ZuulTestCase):
    config_file = 'zuul-connections-same-gerrit.conf'
    tenant_config_file = 'config/zuul-connections-same-gerrit/main.yaml'

    def test_multiple_gerrit_connections(self):
        "Test multiple connections to the one gerrit"

        A = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'A')
        self.addEvent('review_gerrit', A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]['approvals']), 1)
        self.assertEqual(A.patchsets[-1]['approvals'][0]['type'], 'Verified')
        self.assertEqual(A.patchsets[-1]['approvals'][0]['value'], '1')
        self.assertEqual(A.patchsets[-1]['approvals'][0]['by']['username'],
                         'jenkins')

        B = self.fake_review_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test2', B)
        self.addEvent('review_gerrit', B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertEqual(len(B.patchsets[-1]['approvals']), 1)
        self.assertEqual(B.patchsets[-1]['approvals'][0]['type'], 'Verified')
        self.assertEqual(B.patchsets[-1]['approvals'][0]['value'], '-1')
        self.assertEqual(B.patchsets[-1]['approvals'][0]['by']['username'],
                         'civoter')


class TestSQLConnectionMysql(ZuulTestCase):
    config_file = 'zuul-sql-driver-mysql.conf'
    tenant_config_file = 'config/sql-driver/main.yaml'
    expected_table_prefix = ''

    def _sql_tables_created(self, connection_name):
        connection = self.scheds.first.connections.connections[connection_name]
        insp = sa.engine.reflection.Inspector(connection.engine)

        table_prefix = connection.table_prefix
        self.assertEqual(self.expected_table_prefix, table_prefix)

        buildset_table = table_prefix + 'zuul_buildset'
        build_table = table_prefix + 'zuul_build'

        self.assertEqual(16, len(insp.get_columns(buildset_table)))
        self.assertEqual(13, len(insp.get_columns(build_table)))

    def test_sql_tables_created(self):
        "Test the tables for storing results are created properly"
        self._sql_tables_created('database')

    def _sql_indexes_created(self, connection_name):
        connection = self.scheds.first.connections.connections[connection_name]
        insp = sa.engine.reflection.Inspector(connection.engine)

        table_prefix = connection.table_prefix
        self.assertEqual(self.expected_table_prefix, table_prefix)

        buildset_table = table_prefix + 'zuul_buildset'
        build_table = table_prefix + 'zuul_build'

        indexes_buildset = insp.get_indexes(buildset_table)
        indexes_build = insp.get_indexes(build_table)

        # Remove implicitly generated indexes by the foreign key.
        # MySQL creates an implicit index with the name if the column (which
        # is not a problem as in MySQL the index names are scoped within the
        # table). This is an implementation detail of the db engine so don't
        # check this.
        indexes_build = [x for x in indexes_build
                         if x['name'] != 'buildset_id']

        self.assertEqual(4, len(indexes_buildset))
        self.assertEqual(2, len(indexes_build))

        # check if all indexes are prefixed
        if table_prefix:
            indexes = indexes_buildset + indexes_build
            for index in indexes:
                self.assertTrue(index['name'].startswith(table_prefix))

    def test_sql_indexes_created(self):
        "Test the indexes are created properly"
        self._sql_indexes_created('database')

    def test_sql_results(self):
        "Test results are entered into an sql table"

        def check_results():
            # Grab the sa tables
            tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
            pipeline = tenant.layout.pipelines['check']
            reporter = self.scheds.first.connections.getSqlReporter(
                pipeline)
            conn = self.scheds.first.connections.getSqlConnection().\
                engine.connect()

            result = conn.execute(
                sa.sql.select([reporter.connection.zuul_buildset_table]))

            buildsets = result.fetchall()
            self.assertEqual(3, len(buildsets))
            buildset0 = buildsets[0]
            buildset1 = buildsets[1]
            buildset2 = buildsets[2]

            self.assertEqual('check', buildset0['pipeline'])
            self.assertEqual('org/project', buildset0['project'])
            self.assertEqual(1, buildset0['change'])
            self.assertEqual('1', buildset0['patchset'])
            self.assertEqual('SUCCESS', buildset0['result'])
            self.assertEqual('Build succeeded.', buildset0['message'])
            self.assertEqual('tenant-one', buildset0['tenant'])
            self.assertEqual(
                'https://review.example.com/%d' % buildset0['change'],
                buildset0['ref_url'])
            self.assertNotEqual(None, buildset0['event_id'])

            buildset0_builds = conn.execute(
                sa.sql.select([reporter.connection.zuul_build_table]).where(
                    reporter.connection.zuul_build_table.c.buildset_id ==
                    buildset0['id']
                )
            ).fetchall()

            # Check the first result, which should be the project-merge job
            self.assertEqual('project-merge', buildset0_builds[0]['job_name'])
            self.assertEqual("SUCCESS", buildset0_builds[0]['result'])
            self.assertEqual(None, buildset0_builds[0]['log_url'])
            self.assertEqual('check', buildset1['pipeline'])
            self.assertEqual('master', buildset1['branch'])
            self.assertEqual('org/project', buildset1['project'])
            self.assertEqual(2, buildset1['change'])
            self.assertEqual('1', buildset1['patchset'])
            self.assertEqual('FAILURE', buildset1['result'])
            self.assertEqual('Build failed.', buildset1['message'])

            buildset1_builds = conn.execute(
                sa.sql.select([reporter.connection.zuul_build_table]).where(
                    reporter.connection.zuul_build_table.c.buildset_id ==
                    buildset1['id']
                )
            ).fetchall()

            # Check the second result, which should be the project-test1 job
            # which failed
            self.assertEqual('project-test1', buildset1_builds[1]['job_name'])
            self.assertEqual("FAILURE", buildset1_builds[1]['result'])
            self.assertEqual(None, buildset1_builds[1]['log_url'])

            buildset2_builds = conn.execute(
                sa.sql.select([reporter.connection.zuul_build_table]).where(
                    reporter.connection.zuul_build_table.c.buildset_id ==
                    buildset2['id']
                )
            ).fetchall()

            # Check the first result, which should be the project-publish job
            self.assertEqual('project-publish',
                             buildset2_builds[0]['job_name'])
            self.assertEqual("SUCCESS", buildset2_builds[0]['result'])

        self.executor_server.hold_jobs_in_build = True

        # Add a success result
        self.log.debug("Adding success FakeChange")
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.orderedRelease()
        self.waitUntilSettled()

        # Add a failed result
        self.log.debug("Adding failed FakeChange")
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')

        self.executor_server.failJob('project-test1', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.orderedRelease()
        self.waitUntilSettled()

        # Add a tag result
        self.log.debug("Adding FakeTag event")
        C = self.fake_gerrit.addFakeTag('org/project', 'master', 'foo')
        self.fake_gerrit.addEvent(C)
        self.waitUntilSettled()
        self.orderedRelease()
        self.waitUntilSettled()

        check_results()

    def test_sql_results_retry_builds(self):
        "Test that retry results are entered into an sql table correctly"

        # Check the results
        def check_results():
            # Grab the sa tables
            tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")
            pipeline = tenant.layout.pipelines['check']
            reporter = self.scheds.first.connections.getSqlReporter(
                pipeline)

            with self.scheds.first.connections.getSqlConnection().\
                    engine.connect() as conn:

                result = conn.execute(
                    sa.sql.select([reporter.connection.zuul_buildset_table])
                )

                buildsets = result.fetchall()
                self.assertEqual(1, len(buildsets))
                buildset0 = buildsets[0]

                self.assertEqual('check', buildset0['pipeline'])
                self.assertEqual('org/project', buildset0['project'])
                self.assertEqual(1, buildset0['change'])
                self.assertEqual('1', buildset0['patchset'])
                self.assertEqual('SUCCESS', buildset0['result'])
                self.assertEqual('Build succeeded.', buildset0['message'])
                self.assertEqual('tenant-one', buildset0['tenant'])
                self.assertEqual(
                    'https://review.example.com/%d' % buildset0['change'],
                    buildset0['ref_url'])

                buildset0_builds = conn.execute(
                    sa.sql.select(
                        [reporter.connection.zuul_build_table]
                    ).where(
                        reporter.connection.zuul_build_table.c.buildset_id ==
                        buildset0['id']
                    )
                ).fetchall()

            # Check the retry results
            self.assertEqual('project-merge', buildset0_builds[0]['job_name'])
            self.assertEqual('SUCCESS', buildset0_builds[0]['result'])
            self.assertTrue(buildset0_builds[0]['final'])

            self.assertEqual('project-test1', buildset0_builds[1]['job_name'])
            self.assertEqual('RETRY', buildset0_builds[1]['result'])
            self.assertFalse(buildset0_builds[1]['final'])
            self.assertEqual('project-test2', buildset0_builds[2]['job_name'])
            self.assertEqual('RETRY', buildset0_builds[2]['result'])
            self.assertFalse(buildset0_builds[2]['final'])

            self.assertEqual('project-test1', buildset0_builds[3]['job_name'])
            self.assertEqual('SUCCESS', buildset0_builds[3]['result'])
            self.assertTrue(buildset0_builds[3]['final'])
            self.assertEqual('project-test2', buildset0_builds[4]['job_name'])
            self.assertEqual('SUCCESS', buildset0_builds[4]['result'])
            self.assertTrue(buildset0_builds[4]['final'])

        self.executor_server.hold_jobs_in_build = True

        # Add a retry result
        self.log.debug("Adding retry FakeChange")
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        # Release the merge job (which is the dependency for the other jobs)
        self.executor_server.release('.*-merge')
        self.waitUntilSettled()
        # Let both test jobs fail on the first run, so they are both run again.
        self.builds[0].requeue = True
        self.builds[1].requeue = True
        self.orderedRelease()
        self.waitUntilSettled()

        check_results()

    def test_multiple_sql_connections(self):
        "Test putting results in different databases"
        # Add a successful result
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Add a failed result
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')
        self.executor_server.failJob('project-test1', B)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        def check_results(connection_name_1, connection_name_2):
            # Grab the sa tables for resultsdb
            tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")
            pipeline = tenant.layout.pipelines['check']
            reporter1 = self.scheds.first.connections.getSqlReporter(
                pipeline)

            conn = self.scheds.first.connections.getSqlConnection().\
                engine.connect()
            buildsets_resultsdb = conn.execute(sa.sql.select(
                [reporter1.connection.zuul_buildset_table])).fetchall()
            # Should have been 2 buildset reported to the resultsdb (both
            # success and failure report)
            self.assertEqual(2, len(buildsets_resultsdb))

            # The first one should have passed
            self.assertEqual('check', buildsets_resultsdb[0]['pipeline'])
            self.assertEqual(
                'org/project', buildsets_resultsdb[0]['project'])
            self.assertEqual(1, buildsets_resultsdb[0]['change'])
            self.assertEqual('1', buildsets_resultsdb[0]['patchset'])
            self.assertEqual('SUCCESS', buildsets_resultsdb[0]['result'])
            self.assertEqual(
                'Build succeeded.', buildsets_resultsdb[0]['message'])

            buildsets_resultsdb_failures = conn.execute(sa.sql.select(
                [reporter1.connection.zuul_buildset_table])).fetchall()
            # The failure db should only have 1 buildset failed
            self.assertEqual(2, len(buildsets_resultsdb_failures))

            self.assertEqual(
                'check', buildsets_resultsdb_failures[1]['pipeline'])
            self.assertEqual('org/project',
                             buildsets_resultsdb_failures[1]['project'])
            self.assertEqual(2,
                             buildsets_resultsdb_failures[1]['change'])
            self.assertEqual(
                '1', buildsets_resultsdb_failures[1]['patchset'])
            self.assertEqual(
                'FAILURE', buildsets_resultsdb_failures[1]['result'])
            self.assertEqual('Build failed.',
                             buildsets_resultsdb_failures[1]['message'])

        check_results('database', 'resultsdb_failures')


class TestSQLConnectionPostgres(TestSQLConnectionMysql):
    config_file = 'zuul-sql-driver-postgres.conf'


class TestSQLConnectionPrefixMysql(TestSQLConnectionMysql):
    config_file = 'zuul-sql-driver-prefix-mysql.conf'
    expected_table_prefix = 'prefix_'


class TestSQLConnectionPrefixPostgres(TestSQLConnectionMysql):
    config_file = 'zuul-sql-driver-prefix-postgres.conf'
    expected_table_prefix = 'prefix_'


class TestRequiredSQLConnection(BaseTestCase):
    config = None
    connections = None

    def setUp(self):
        super().setUp()
        self.addCleanup(self.stop_connection)

    def setup_connection(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(FIXTURE_DIR, config_file))

        # Setup databases
        for section_name in self.config.sections():
            con_match = re.match(r'^connection ([\'\"]?)(.*)(\1)$',
                                 section_name, re.I)
            if not con_match:
                continue

            if self.config.get(section_name, 'driver') == 'sql':
                if (self.config.get(section_name, 'dburi') ==
                        '$MYSQL_FIXTURE_DBURI$'):
                    f = MySQLSchemaFixture()
                    self.useFixture(f)
                    self.config.set(section_name, 'dburi', f.dburi)
                elif (self.config.get(section_name, 'dburi') ==
                      '$POSTGRESQL_FIXTURE_DBURI$'):
                    f = PostgresqlSchemaFixture()
                    self.useFixture(f)
                    self.config.set(section_name, 'dburi', f.dburi)
        self.connections = zuul.lib.connections.ConnectionRegistry()

    def stop_connection(self):
        self.connections.stop()


class TestMultipleGerrits(ZuulTestCase):
    config_file = 'zuul-connections-multiple-gerrits.conf'
    tenant_config_file = 'config/zuul-connections-multiple-gerrits/main.yaml'

    def test_multiple_project_separate_gerrits(self):
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_another_gerrit.addFakeChange(
            'org/project1', 'master', 'A')
        self.fake_another_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertBuilds([dict(name='project-test2',
                                changes='1,1',
                                project='org/project1',
                                pipeline='another_check')])

        # NOTE(jamielennox): the tests back the git repo for both connections
        # onto the same git repo on the file system. If we just create another
        # fake change the fake_review_gerrit will try to create another 1,1
        # change and git will fail to create the ref. Arbitrarily set it to get
        # around the problem.
        self.fake_review_gerrit.change_number = 50

        B = self.fake_review_gerrit.addFakeChange(
            'org/project1', 'master', 'B')
        self.fake_review_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='project-test2',
                 changes='1,1',
                 project='org/project1',
                 pipeline='another_check'),
            dict(name='project-test1',
                 changes='51,1',
                 project='org/project1',
                 pipeline='review_check'),
        ])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

    def test_multiple_project_separate_gerrits_common_pipeline(self):
        self.executor_server.hold_jobs_in_build = True

        self.create_branch('org/project2', 'develop')
        self.fake_another_gerrit.addEvent(
            self.fake_another_gerrit.getFakeBranchCreatedEvent(
                'org/project2', 'develop'))

        self.fake_another_gerrit.addEvent(
            self.fake_review_gerrit.getFakeBranchCreatedEvent(
                'org/project2', 'develop'))
        self.waitUntilSettled()

        A = self.fake_another_gerrit.addFakeChange(
            'org/project2', 'master', 'A')
        self.fake_another_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertBuilds([dict(name='project-test2',
                                changes='1,1',
                                project='org/project2',
                                pipeline='common_check')])

        # NOTE(jamielennox): the tests back the git repo for both connections
        # onto the same git repo on the file system. If we just create another
        # fake change the fake_review_gerrit will try to create another 1,1
        # change and git will fail to create the ref. Arbitrarily set it to get
        # around the problem.
        self.fake_review_gerrit.change_number = 50

        B = self.fake_review_gerrit.addFakeChange(
            'org/project2', 'develop', 'B')
        self.fake_review_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='project-test2',
                 changes='1,1',
                 project='org/project2',
                 pipeline='common_check'),
            dict(name='project-test1',
                 changes='51,1',
                 project='org/project2',
                 pipeline='common_check'),
        ])

        # NOTE(avass): This last change should not trigger any pipelines since
        # common_check is configured to only run on master for another_gerrit
        C = self.fake_another_gerrit.addFakeChange(
            'org/project2', 'develop', 'C')
        self.fake_another_gerrit.addEvent(C.getPatchsetCreatedEvent(1))

        self.waitUntilSettled()

        self.assertBuilds([
            dict(name='project-test2',
                 changes='1,1',
                 project='org/project2',
                 pipeline='common_check'),
            dict(name='project-test1',
                 changes='51,1',
                 project='org/project2',
                 pipeline='common_check'),
        ])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()


class TestConnectionsMerger(ZuulTestCase):
    config_file = 'zuul-connections-merger.conf'
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_connections_merger(self):
        "Test merger only configures source connections"

        self.assertIn("gerrit", self.executor_server.connections.connections)
        self.assertIn("github", self.executor_server.connections.connections)
        self.assertNotIn("smtp", self.executor_server.connections.connections)
        self.assertNotIn("sql", self.executor_server.connections.connections)
        self.assertNotIn("timer", self.executor_server.connections.connections)
        self.assertNotIn("zuul", self.executor_server.connections.connections)


class TestConnectionsCgit(ZuulTestCase):
    config_file = 'zuul-connections-cgit.conf'
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_cgit_web_url(self):
        self.assertIn("gerrit", self.scheds.first.connections.connections)
        conn = self.scheds.first.connections.connections['gerrit']
        source = conn.source
        proj = source.getProject('foo/bar')
        url = conn._getWebUrl(proj, '1')
        self.assertEqual(url,
                         'https://cgit.example.com/cgit/foo/bar/commit/?id=1')


class TestConnectionsGitweb(ZuulTestCase):
    config_file = 'zuul-connections-gitweb.conf'
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_gitweb_url(self):
        self.assertIn("gerrit", self.scheds.first.connections.connections)
        conn = self.scheds.first.connections.connections['gerrit']
        source = conn.source
        proj = source.getProject('foo/bar')
        url = conn._getWebUrl(proj, '1')
        url_should_be = 'https://review.example.com/' \
                        'gitweb?p=foo/bar.git;a=commitdiff;h=1'
        self.assertEqual(url, url_should_be)


class TestMQTTConnection(ZuulTestCase):
    config_file = 'zuul-mqtt-driver.conf'
    tenant_config_file = 'config/mqtt-driver/main.yaml'

    def test_mqtt_reporter(self):
        "Test the MQTT reporter"
        # Add a success result
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        artifact = {'name': 'image',
                    'url': 'http://example.com/image',
                    'metadata': {
                        'type': 'container_image'
                    }}
        self.executor_server.returnData(
            "test", A, {"zuul": {"log_url": "some-log-url",
                                 'artifacts': [artifact],
                                 }}
        )
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        success_event = self.mqtt_messages.pop()
        start_event = self.mqtt_messages.pop()

        self.assertEquals(start_event.get('topic'),
                          'tenant-one/zuul_start/check/org/project/master')
        mqtt_payload = start_event['msg']
        self.assertEquals(mqtt_payload['project'], 'org/project')
        self.assertEqual(len(mqtt_payload['commit_id']), 40)
        self.assertEquals(mqtt_payload['owner'], 'username')
        self.assertEquals(mqtt_payload['branch'], 'master')
        self.assertEquals(mqtt_payload['buildset']['result'], None)
        self.assertEquals(mqtt_payload['buildset']['builds'][0]['job_name'],
                          'test')
        self.assertNotIn('result', mqtt_payload['buildset']['builds'][0])
        self.assertNotIn('artifacts', mqtt_payload['buildset']['builds'][0])

        self.assertEquals(success_event.get('topic'),
                          'tenant-one/zuul_buildset/check/org/project/master')
        mqtt_payload = success_event['msg']
        self.assertEquals(mqtt_payload['project'], 'org/project')
        self.assertEquals(mqtt_payload['branch'], 'master')
        self.assertEquals(mqtt_payload['buildset']['result'], 'SUCCESS')
        builds = mqtt_payload['buildset']['builds']
        test_job = [b for b in builds if b['job_name'] == 'test'][0]
        dependent_test_job = [
            b for b in builds if b['job_name'] == 'dependent-test'
        ][0]
        self.assertEquals(test_job['job_name'], 'test')
        self.assertEquals(test_job['result'], 'SUCCESS')
        self.assertEquals(test_job['dependencies'], [])
        self.assertEquals(test_job['artifacts'], [artifact])
        self.assertEquals(test_job['log_url'], 'some-log-url/')
        build_id = test_job["uuid"]
        self.assertEquals(
            test_job["web_url"],
            "https://tenant.example.com/t/tenant-one/build/{}".format(
                build_id
            ),
        )
        self.assertIn('execute_time', test_job)
        self.assertIn('timestamp', mqtt_payload)
        self.assertIn('enqueue_time', mqtt_payload)
        self.assertIn('trigger_time', mqtt_payload)
        self.assertIn('zuul_event_id', mqtt_payload)
        self.assertIn('uuid', mqtt_payload)
        self.assertEquals(dependent_test_job['dependencies'], ['test'])

    def test_mqtt_invalid_topic(self):
        in_repo_conf = textwrap.dedent(
            """
            - pipeline:
                name: test-pipeline
                manager: independent
                trigger:
                  gerrit:
                    - event: comment-added
                start:
                  mqtt:
                    topic: "{bad}/{topic}"
            """)
        file_dict = {'zuul.d/test.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('common-config', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertIn("topic component 'bad' is invalid", A.messages[0],
                      "A should report a syntax error")


class TestElasticsearchConnection(AnsibleZuulTestCase):
    config_file = 'zuul-elastic-driver.conf'
    tenant_config_file = 'config/elasticsearch-driver/main.yaml'

    # These tests are storing the reported index on the fake
    # elasticsearch backend which is a different instance for each
    # scheduler. Thus, depending on which scheduler reports the
    # item, the assertions in these test might pass or fail.
    scheduler_count = 1

    def _getSecrets(self, job, pbtype):
        secrets = []
        build = self.getJobFromHistory(job)
        for pb in getattr(build.jobdir, pbtype):
            if pb.secrets_content:
                secrets.append(
                    yamlutil.ansible_unsafe_load(pb.secrets_content))
            else:
                secrets.append({})
        return secrets

    def test_elastic_reporter(self):
        "Test the Elasticsearch reporter"
        # Add a success result
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        indexed_docs = self.scheds.first.connections.connections[
            'elasticsearch'].source_it
        index = self.scheds.first.connections.connections[
            'elasticsearch'].index

        self.assertEqual(len(indexed_docs), 2)
        self.assertEqual(index, ('zuul-index.tenant-one-%s' %
                                 time.strftime("%Y.%m.%d")))
        buildset_doc = [doc for doc in indexed_docs if
                        doc['build_type'] == 'buildset'][0]
        self.assertEqual(buildset_doc['tenant'], 'tenant-one')
        self.assertEqual(buildset_doc['pipeline'], 'check')
        self.assertEqual(buildset_doc['result'], 'SUCCESS')
        build_doc = [doc for doc in indexed_docs if
                     doc['build_type'] == 'build'][0]
        self.assertEqual(build_doc['buildset_uuid'], buildset_doc['uuid'])
        self.assertEqual(build_doc['result'], 'SUCCESS')
        self.assertEqual(build_doc['job_name'], 'test')
        self.assertEqual(build_doc['tenant'], 'tenant-one')
        self.assertEqual(build_doc['pipeline'], 'check')

        self.assertIn('job_vars', build_doc)
        self.assertDictEqual(
            build_doc['job_vars'], {'bar': 'foo', 'bar2': 'foo2'})

        self.assertIn('job_returned_vars', build_doc)
        self.assertDictEqual(
            build_doc['job_returned_vars'], {'foo': 'bar'})

        self.assertEqual(self.history[0].uuid, build_doc['uuid'])
        self.assertIn('duration', build_doc)
        self.assertTrue(type(build_doc['duration']) is int)

        doc_gen = self.scheds.first.connections.connections[
            'elasticsearch'].gen(indexed_docs, index)
        self.assertIsInstance(doc_gen, types.GeneratorType)
        self.assertTrue('@timestamp' in list(doc_gen)[0]['_source'])

    def test_elasticsearch_secret_leak(self):
        expected_secret = [{
            'test_secret': {
                'username': 'test-username',
                'password': 'test-password'
            }
        }]

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        indexed_docs = self.scheds.first.connections.connections[
            'elasticsearch'].source_it

        build_doc = [doc for doc in indexed_docs if
                     doc['build_type'] == 'build'][0]

        # Ensure that job include secret
        self.assertEqual(
            self._getSecrets('test', 'playbooks'),
            expected_secret)

        # Check if there is a secret leak
        self.assertFalse('test_secret' in build_doc['job_vars'])
