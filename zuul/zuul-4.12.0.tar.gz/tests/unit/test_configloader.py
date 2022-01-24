# Copyright 2017 Red Hat, Inc.
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
import fixtures
import logging
import textwrap
import testtools
import voluptuous as vs
from collections import defaultdict
from configparser import ConfigParser

from zuul import model
from zuul.lib.ansible import AnsibleManager
from zuul.configloader import (
    AuthorizationRuleParser, ConfigLoader, safe_load_yaml
)
from zuul.model import Abide, MergeRequest, SourceContext
from zuul.zk.locks import tenant_read_lock

from tests.base import ZuulTestCase


class TestConfigLoader(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_update_system_config(self):
        """Test if the system config can be updated without a scheduler."""
        sched = self.scheds.first.sched

        # Get the current system config before instantiating a ConfigLoader.
        unparsed_abide, zuul_globals = sched.system_config_cache.get()
        ansible_manager = AnsibleManager(
            default_version=zuul_globals.default_ansible_version)
        loader = ConfigLoader(
            sched.connections, self.zk_client, zuul_globals, sched.statsd,
            keystorage=sched.keystore)
        abide = Abide()
        loader.loadTPCs(abide, unparsed_abide)
        loader.loadAdminRules(abide, unparsed_abide)

        for tenant_name in unparsed_abide.tenants:
            tlock = tenant_read_lock(self.zk_client, tenant_name)
            # Consider all caches valid (min. ltime -1)
            min_ltimes = defaultdict(lambda: defaultdict(lambda: -1))
            with tlock:
                tenant = loader.loadTenant(
                    abide, tenant_name, ansible_manager, unparsed_abide,
                    min_ltimes=min_ltimes)

                self.assertEqual(tenant.name, tenant_name)


class TenantParserTestCase(ZuulTestCase):
    create_project_keys = True

    CONFIG_SET = set(['pipeline', 'job', 'semaphore', 'project',
                      'project-template', 'nodeset', 'secret', 'queue'])
    UNTRUSTED_SET = CONFIG_SET - set(['pipeline'])

    def setupAllProjectKeys(self, config: ConfigParser):
        for project in ['common-config', 'org/project1', 'org/project2']:
            self.setupProjectKeys('gerrit', project)


class TestTenantSimple(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/simple.yaml'

    def test_tenant_simple(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2'],
                         [x.name for x in tenant.untrusted_projects])

        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET, tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET, tpc.load_classes)
        self.assertTrue('common-config-job' in tenant.layout.jobs)
        self.assertTrue('project1-job' in tenant.layout.jobs)
        self.assertTrue('project2-job' in tenant.layout.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertTrue('common-config-job' in
                        project1_config[0].pipelines['check'].job_list.jobs)
        self.assertTrue('project1-job' in
                        project1_config[1].pipelines['check'].job_list.jobs)
        project2_config = tenant.layout.project_configs.get(
            'review.example.com/org/project2')
        self.assertTrue('common-config-job' in
                        project2_config[0].pipelines['check'].job_list.jobs)
        self.assertTrue('project2-job' in
                        project2_config[1].pipelines['check'].job_list.jobs)

    def test_variant_description(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        job = tenant.layout.jobs.get("project2-job")
        self.assertEqual(job[0].variant_description, "")
        self.assertEqual(job[1].variant_description, "stable")

    def test_merge_anchor(self):
        to_parse = textwrap.dedent(
            """
            - job:
                name: job1
                vars: &docker_vars
                  registry: 'registry.example.org'

            - job:
                name: job2
                vars:
                  <<: &buildenv_vars
                    image_name: foo
                  <<: *docker_vars

            - job:
                name: job3
                vars:
                  <<: *buildenv_vars
                  <<: *docker_vars
            """)
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        project = tenant.config_projects[0]
        source_context = SourceContext(
            project.canonical_name, project.name, project.connection_name,
            'master', 'zuul.yaml', True)

        data = safe_load_yaml(to_parse, source_context)
        self.assertEqual(len(data), 3)
        job_vars = [i['job']['vars'] for i in data]
        # Test that merging worked
        self.assertEqual(job_vars, [
            {'registry': 'registry.example.org'},
            {'registry': 'registry.example.org', 'image_name': 'foo'},
            {'registry': 'registry.example.org', 'image_name': 'foo'},
        ])

    def test_deny_localhost_nodeset(self):
        in_repo_conf = textwrap.dedent(
            """
            - nodeset:
                name: localhost
                nodes:
                  - name: localhost
                    label: ubuntu
            """)
        file_dict = {'zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # No job should have run due to the change introducing a config error
        self.assertHistory([])
        self.assertTrue(A.reported)
        self.assertTrue("Nodes named 'localhost' are not allowed."
                        in A.messages[0])

        in_repo_conf = textwrap.dedent(
            """
            - nodeset:
                name: localhost-group
                nodes:
                  - name: ubuntu
                    label: ubuntu
                groups:
                  - name: localhost
                    nodes: ubuntu
            """)
        file_dict = {'zuul.yaml': in_repo_conf}
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # No job should have run due to the change introducing a config error
        self.assertHistory([])
        self.assertTrue(B.reported)
        self.assertTrue("Groups named 'localhost' are not allowed."
                        in B.messages[0])


class TestTenantOverride(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/override.yaml'

    def test_tenant_override(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2', 'org/project4'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET - set(['project']),
                         tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set(['job']), tpc.load_classes)
        self.assertTrue('common-config-job' in tenant.layout.jobs)
        self.assertTrue('project1-job' in tenant.layout.jobs)
        self.assertTrue('project2-job' in tenant.layout.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertTrue('common-config-job' in
                        project1_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project1-job' in
                         project1_config[0].pipelines['check'].job_list.jobs)
        project2_config = tenant.layout.project_configs.get(
            'review.example.com/org/project2')
        self.assertTrue('common-config-job' in
                        project2_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project2-job' in
                         project2_config[0].pipelines['check'].job_list.jobs)


class TestTenantGroups(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/groups.yaml'

    def test_tenant_groups(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET - set(['project']),
                         tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET - set(['project']),
                         tpc.load_classes)
        self.assertTrue('common-config-job' in tenant.layout.jobs)
        self.assertTrue('project1-job' in tenant.layout.jobs)
        self.assertTrue('project2-job' in tenant.layout.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertTrue('common-config-job' in
                        project1_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project1-job' in
                         project1_config[0].pipelines['check'].job_list.jobs)
        project2_config = tenant.layout.project_configs.get(
            'review.example.com/org/project2')
        self.assertTrue('common-config-job' in
                        project2_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project2-job' in
                         project2_config[0].pipelines['check'].job_list.jobs)


class TestTenantGroups2(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/groups2.yaml'

    def test_tenant_groups2(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2', 'org/project3'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET - set(['project']),
                         tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.UNTRUSTED_SET - set(['project', 'job']),
                         tpc.load_classes)
        self.assertTrue('common-config-job' in tenant.layout.jobs)
        self.assertTrue('project1-job' in tenant.layout.jobs)
        self.assertFalse('project2-job' in tenant.layout.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertTrue('common-config-job' in
                        project1_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project1-job' in
                         project1_config[0].pipelines['check'].job_list.jobs)
        project2_config = tenant.layout.project_configs.get(
            'review.example.com/org/project2')
        self.assertTrue('common-config-job' in
                        project2_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project2-job' in
                         project2_config[0].pipelines['check'].job_list.jobs)


class TestTenantGroups3(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/groups3.yaml'

    def test_tenant_groups3(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(False, tenant.exclude_unprotected_branches)
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set(['job']), tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set(['project', 'job']), tpc.load_classes)
        self.assertTrue('common-config-job' in tenant.layout.jobs)
        self.assertTrue('project1-job' in tenant.layout.jobs)
        self.assertTrue('project2-job' in tenant.layout.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertTrue('common-config-job' in
                        project1_config[0].pipelines['check'].job_list.jobs)
        self.assertFalse('project1-job' in
                         project1_config[0].pipelines['check'].job_list.jobs)
        project2_config = tenant.layout.project_configs.get(
            'review.example.com/org/project2')
        self.assertTrue('common-config-job' in
                        project2_config[0].pipelines['check'].job_list.jobs)
        self.assertTrue('project2-job' in
                        project2_config[1].pipelines['check'].job_list.jobs)


class TestTenantGroups4(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/groups4.yaml'

    def test_tenant_groups(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set([]),
                         tpc.load_classes)
        project = tenant.untrusted_projects[1]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set([]),
                         tpc.load_classes)
        # Check that only one merger:cat job was requested
        # org/project1 and org/project2 have an empty load_classes
        self.assertEqual(1, len(self.merge_job_history.get(MergeRequest.CAT)))
        old_layout = tenant.layout

        # Check that creating a change in project1 doesn't cause a
        # reconfiguration (due to a mistaken belief that we need to
        # load config from it since there is none in memory).
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        new_layout = tenant.layout

        self.assertEqual(old_layout, new_layout)


class TestTenantGroups5(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/groups5.yaml'

    def test_tenant_single_projet_exclude(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1'],
                         [x.name for x in tenant.untrusted_projects])
        project = tenant.config_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(self.CONFIG_SET, tpc.load_classes)
        project = tenant.untrusted_projects[0]
        tpc = tenant.project_configs[project.canonical_name]
        self.assertEqual(set([]),
                         tpc.load_classes)
        # Check that only one merger:cat job was requested
        # org/project1 and org/project2 have an empty load_classes
        self.assertEqual(1, len(self.merge_job_history.get(MergeRequest.CAT)))


class TestTenantFromScript(TestTenantSimple):
    tenant_config_file = None
    tenant_config_script_file = 'config/tenant-parser/tenant_config_script.py'

    def test_tenant_simple(self):
        TestTenantSimple.test_tenant_simple(self)


class TestTenantUnprotectedBranches(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/unprotected-branches.yaml'

    def test_tenant_unprotected_branches(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertEqual(True, tenant.exclude_unprotected_branches)

        self.assertEqual(['common-config'],
                         [x.name for x in tenant.config_projects])
        self.assertEqual(['org/project1', 'org/project2'],
                         [x.name for x in tenant.untrusted_projects])

        tpc = tenant.project_configs
        project_name = tenant.config_projects[0].canonical_name
        self.assertEqual(False, tpc[project_name].exclude_unprotected_branches)

        project_name = tenant.untrusted_projects[0].canonical_name
        self.assertIsNone(tpc[project_name].exclude_unprotected_branches)

        project_name = tenant.untrusted_projects[1].canonical_name
        self.assertIsNone(tpc[project_name].exclude_unprotected_branches)


class TestTenantExcludeAll(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/exclude-all.yaml'

    def test_tenant_exclude_all(self):
        """
        Tests that excluding all configuration of project1 in tenant-one
        doesn't remove the configuration of project1 in tenant-two.
        """
        # The config in org/project5 depends on config in org/project1 so
        # validate that there are no config errors in that tenant.
        tenant_two = self.scheds.first.sched.abide.tenants.get('tenant-two')
        self.assertEquals(
            len(tenant_two.layout.loading_errors), 0,
            "No error should have been accumulated")


class TestTenantConfigBranches(ZuulTestCase):
    tenant_config_file = 'config/tenant-parser/simple.yaml'

    def _validate_job(self, job, branch):
        tenant_one = self.scheds.first.sched.abide.tenants.get('tenant-one')
        jobs = tenant_one.layout.getJobs(job)
        self.assertEquals(len(jobs), 1)
        self.assertIn(jobs[0].source_context.branch, branch)

    def test_tenant_config_load_branch(self):
        """
        Tests that when specifying branches for a project only those branches
        are parsed.
        """
        # Job must be defined in master
        common_job = 'common-config-job'
        self._validate_job(common_job, 'master')

        self.log.debug('Creating branches')
        self.create_branch('common-config', 'stable')
        self.create_branch('common-config', 'feat_x')
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'common-config', 'stable'))
        self.fake_gerrit.addEvent(
            self.fake_gerrit.getFakeBranchCreatedEvent(
                'common-config', 'feat_x'))
        self.waitUntilSettled()

        # Job must be defined in master
        self._validate_job(common_job, 'master')

        # Reconfigure with load-branch stable for common-config
        self.newTenantConfig('config/tenant-parser/branch.yaml')
        self.scheds.execute(lambda app: app.sched.reconfigure(app.config))

        # Now job must be defined on stable branch
        self._validate_job(common_job, 'stable')

        # Now try to break the config in common-config on stable
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: base
                parent: non-existing
            """)
        file_dict = {'zuul.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('common-config', 'stable', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # No job should have run due to the change introducing a config error
        self.assertHistory([])
        self.assertTrue(A.reported)
        self.assertTrue('Job non-existing not defined' in A.messages[0])


class TestSplitConfig(ZuulTestCase):
    tenant_config_file = 'config/split-config/main.yaml'

    def test_split_config(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertIn('project-test1', tenant.layout.jobs)
        self.assertIn('project-test2', tenant.layout.jobs)
        test1 = tenant.layout.getJob('project-test1')
        self.assertEqual(test1.source_context.project_name, 'common-config')
        self.assertEqual(test1.source_context.branch, 'master')
        self.assertEqual(test1.source_context.path, 'zuul.d/jobs.yaml')
        self.assertEqual(test1.source_context.trusted, True)
        test2 = tenant.layout.getJob('project-test2')
        self.assertEqual(test2.source_context.project_name, 'common-config')
        self.assertEqual(test2.source_context.branch, 'master')
        self.assertEqual(test2.source_context.path, 'zuul.d/more-jobs.yaml')
        self.assertEqual(test2.source_context.trusted, True)

        self.assertNotEqual(test1.source_context, test2.source_context)
        self.assertTrue(test1.source_context.isSameProject(
            test2.source_context))

        project_config = tenant.layout.project_configs.get(
            'review.example.com/org/project')
        self.assertIn('project-test1',
                      project_config[0].pipelines['check'].job_list.jobs)
        project1_config = tenant.layout.project_configs.get(
            'review.example.com/org/project1')
        self.assertIn('project1-project2-integration',
                      project1_config[0].pipelines['check'].job_list.jobs)

        # This check ensures the .zuul.ignore flag file is working in
        # the config directory.
        self.assertEquals(
            len(tenant.layout.loading_errors), 0)

    def test_dynamic_split_config(self):
        in_repo_conf = textwrap.dedent(
            """
            - project:
                name: org/project1
                check:
                  jobs:
                    - project-test1
            """)
        file_dict = {'.zuul.d/gate.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        # project1-project2-integration test removed, only want project-test1
        self.assertHistory([
            dict(name='project-test1', result='SUCCESS', changes='1,1')])

    def test_config_path_conflict(self):
        def add_file(project, path):
            new_file = textwrap.dedent(
                """
                - job:
                    name: test-job
                """
            )
            file_dict = {path: new_file}
            A = self.fake_gerrit.addFakeChange(project, 'master', 'A',
                                               files=file_dict)
            self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
            self.waitUntilSettled()
            return A

        log_fixture = self.useFixture(
            fixtures.FakeLogger(level=logging.WARNING))

        log_fixture._output.truncate(0)
        A = add_file("common-config", "zuul.yaml")
        self.assertIn("Configuration in common-config/zuul.d/jobs.yaml@master "
                      "ignored because project-branch is already configured",
                      log_fixture.output)
        self.assertIn("Configuration in common-config/zuul.d/jobs.yaml@master "
                      "ignored because project-branch is already configured",
                      A.messages[0])

        log_fixture._output.truncate(0)
        add_file("org/project1", ".zuul.yaml")
        self.assertIn("Configuration in org/project1/.zuul.d/gate.yaml@master "
                      "ignored because project-branch is already configured",
                      log_fixture.output)


class TestConfigConflict(ZuulTestCase):
    tenant_config_file = 'config/conflict-config/main.yaml'

    def test_conflict_config(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        jobs = sorted(tenant.layout.jobs.keys())
        self.assertEqual(
            ['base', 'noop', 'trusted-zuul.yaml-job',
             'untrusted-zuul.yaml-job'],
            jobs)


class TestUnparsedConfigCache(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_config_caching(self):
        sched = self.scheds.first.sched
        cache = sched.unparsed_config_cache
        tenant = sched.abide.tenants["tenant-one"]

        common_cache = cache.getFilesCache("review.example.com/common-config",
                                           "master")
        upb_common_cache = sched.abide.getUnparsedBranchCache(
            "review.example.com/common-config", "master")
        tpc = tenant.project_configs["review.example.com/common-config"]
        self.assertTrue(common_cache.isValidFor(tpc, min_ltime=-1))
        self.assertEqual(len(common_cache), 1)
        self.assertIn("zuul.yaml", common_cache)
        self.assertTrue(len(common_cache["zuul.yaml"]) > 0)
        self.assertEqual(upb_common_cache.ltime, common_cache.ltime)

        project_cache = cache.getFilesCache("review.example.com/org/project",
                                            "master")
        upb_project_cache = sched.abide.getUnparsedBranchCache(
            "review.example.com/org/project", "master")
        # Cache of org/project should be valid but empty (no in-repo config)
        tpc = tenant.project_configs["review.example.com/org/project"]
        self.assertTrue(project_cache.isValidFor(tpc, min_ltime=-1))
        self.assertEqual(len(project_cache), 0)
        self.assertEqual(upb_project_cache.ltime, project_cache.ltime)

    def test_cache_use(self):
        sched = self.scheds.first.sched
        # Stop cleanup jobs so it's not removing projects from
        # the cache during the test.
        sched.apsched.shutdown()
        tenant = sched.abide.tenants['tenant-one']
        _, project = tenant.getProject('org/project2')

        cache = self.scheds.first.sched.unparsed_config_cache
        files_cache = cache.getFilesCache(
            "review.example.com/org/project2", "master")
        zk_initial_ltime = files_cache.ltime
        upb_cache = sched.abide.getUnparsedBranchCache(
            "review.example.com/org/project2", "master")
        self.assertEqual(zk_initial_ltime, upb_cache.ltime)

        # Get the current ltime from Zookeeper and run a full reconfiguration,
        # so that we know all items in the cache have a larger ltime.
        ltime = self.zk_client.getCurrentLtime()
        self.scheds.first.fullReconfigure()
        self.assertGreater(files_cache.ltime, zk_initial_ltime)
        upb_cache = sched.abide.getUnparsedBranchCache(
            "review.example.com/org/project2", "master")
        self.assertEqual(files_cache.ltime, upb_cache.ltime)

        # Clear the unparsed branch cache so all projects (except for
        # org/project2) are retrieved from the cache in Zookeeper.
        sched.abide.unparsed_project_branch_cache.clear()
        del self.merge_job_history

        # Create a tenant reconfiguration event with a known ltime that is
        # smaller than the ltime of the items in the cache.
        event = model.TenantReconfigureEvent(
            tenant.name, project.canonical_name, branch_name=None)
        event.zuul_event_ltime = ltime
        sched.management_events[tenant.name].put(event, needs_result=False)
        self.waitUntilSettled()

        # As the cache should be valid (cache ltime of org/project2 newer than
        # event ltime) we don't expect any cat jobs.
        self.assertIsNone(self.merge_job_history.get(MergeRequest.CAT))

        # Set canary value so we can detect if the configloader used
        # the cache in Zookeeper (it shouldn't).
        common_cache = cache.getFilesCache("review.example.com/common-config",
                                           "master")
        common_cache.setValidFor({"CANARY"}, set(), common_cache.ltime)
        del self.merge_job_history

        # Create a tenant reconfiguration event with a known ltime that is
        # smaller than the ltime of the items in the cache.
        event = model.TenantReconfigureEvent(
            tenant.name, project.canonical_name, branch_name=None)
        event.zuul_event_ltime = ltime
        sched.management_events[tenant.name].put(event, needs_result=False)
        self.waitUntilSettled()

        upb_cache = sched.abide.getUnparsedBranchCache(
            "review.example.com/common-config", "master")
        self.assertEqual(common_cache.ltime, upb_cache.ltime)
        self.assertNotIn("CANARY", upb_cache.extra_files_searched)

        # As the cache should be valid (cache ltime of org/project2 newer than
        # event ltime) we don't expect any cat jobs.
        self.assertIsNone(self.merge_job_history.get(MergeRequest.CAT))
        sched.apsched.start()


class TestAuthorizationRuleParser(ZuulTestCase):
    tenant_config_file = 'config/tenant-parser/authorizations.yaml'

    def test_rules_are_loaded(self):
        rules = self.scheds.first.sched.abide.admin_rules
        self.assertTrue('auth-rule-one' in rules,
                        self.scheds.first.sched.abide)
        self.assertTrue('auth-rule-two' in rules,
                        self.scheds.first.sched.abide)
        claims_1 = {'sub': 'venkman'}
        claims_2 = {'sub': 'gozer',
                    'iss': 'another_dimension'}
        self.assertTrue(rules['auth-rule-one'](claims_1))
        self.assertTrue(not rules['auth-rule-one'](claims_2))
        self.assertTrue(not rules['auth-rule-two'](claims_1))
        self.assertTrue(rules['auth-rule-two'](claims_2))

    def test_parse_simplest_rule_from_yaml(self):
        rule_d = {'name': 'my-rule',
                  'conditions': {'sub': 'user1'}
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))
        claims = {'iss': 'my-2nd-idp',
                  'sub': 'user2',
                  'groups': ['admin', 'ghostbusters']}
        self.assertFalse(rule(claims))

    def test_parse_AND_rule_from_yaml(self):
        rule_d = {'name': 'my-rule',
                  'conditions': {'sub': 'user1',
                                 'iss': 'my-idp'}
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))
        claims = {'iss': 'my-2nd-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertFalse(rule(claims))

    def test_parse_OR_rule_from_yaml(self):
        rule_d = {'name': 'my-rule',
                  'conditions': [{'sub': 'user1',
                                  'iss': 'my-idp'},
                                 {'sub': 'user2',
                                  'iss': 'my-2nd-idp'}
                                ]
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))
        claims = {'iss': 'my-2nd-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertFalse(rule(claims))
        claims = {'iss': 'my-2nd-idp',
                  'sub': 'user2',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))

    def test_parse_rule_with_list_claim_from_yaml(self):
        rule_d = {'name': 'my-rule',
                  'conditions': [{'groups': 'ghostbusters',
                                  'iss': 'my-idp'},
                                 {'sub': 'user2',
                                  'iss': 'my-2nd-idp'}
                                ],
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))
        claims = {'iss': 'my-idp',
                  'sub': 'user1',
                  'groups': ['admin', 'ghostbeaters']}
        self.assertFalse(rule(claims))
        claims = {'iss': 'my-2nd-idp',
                  'sub': 'user2',
                  'groups': ['admin', 'ghostbusters']}
        self.assertTrue(rule(claims))

    def test_check_complex_rule_from_yaml_jsonpath(self):
        rule_d = {'name': 'my-rule',
                  'conditions': [{'hello.this.is': 'a complex value'},
                                ],
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'hello': {
                      'this': {
                          'is': 'a complex value'
                      },
                      'and': {
                          'this one': 'too'
                      }
                  }
                 }
        self.assertTrue(rule(claims))

    def test_check_complex_rule_from_yaml_nested_dict(self):
        rule_d = {'name': 'my-rule',
                  'conditions': [{'hello': {'this': {'is': 'a complex value'
                                                    }
                                           }
                                 },
                                ],
                 }
        rule = AuthorizationRuleParser().fromYaml(rule_d)
        self.assertEqual('my-rule', rule.name)
        claims = {'iss': 'my-idp',
                  'hello': {
                      'this': {
                          'is': 'a complex value'
                      },
                      'and': {
                          'this one': 'too'
                      }
                  }
                 }
        self.assertTrue(rule(claims))


class TestAuthorizationRuleParserWithTemplating(ZuulTestCase):
    tenant_config_file = 'config/tenant-parser/authorizations-templating.yaml'

    def test_rules_are_loaded(self):
        rules = self.scheds.first.sched.abide.admin_rules
        self.assertTrue('tenant-admin' in rules, self.scheds.first.sched.abide)
        self.assertTrue('tenant-admin-complex' in rules,
                        self.scheds.first.sched.abide)

    def test_tenant_substitution(self):
        claims_1 = {'group': 'tenant-one-admin'}
        claims_2 = {'group': 'tenant-two-admin'}
        rules = self.scheds.first.sched.abide.admin_rules
        tenant_one = self.scheds.first.sched.abide.tenants.get('tenant-one')
        tenant_two = self.scheds.first.sched.abide.tenants.get('tenant-two')
        self.assertTrue(rules['tenant-admin'](claims_1, tenant_one))
        self.assertTrue(rules['tenant-admin'](claims_2, tenant_two))
        self.assertTrue(not rules['tenant-admin'](claims_1, tenant_two))
        self.assertTrue(not rules['tenant-admin'](claims_2, tenant_one))

    def test_tenant_substitution_in_list(self):
        claims_1 = {'group': ['tenant-one-admin', 'some-other-tenant']}
        claims_2 = {'group': ['tenant-two-admin', 'some-other-tenant']}
        rules = self.scheds.first.sched.abide.admin_rules
        tenant_one = self.scheds.first.sched.abide.tenants.get('tenant-one')
        tenant_two = self.scheds.first.sched.abide.tenants.get('tenant-two')
        self.assertTrue(rules['tenant-admin'](claims_1, tenant_one))
        self.assertTrue(rules['tenant-admin'](claims_2, tenant_two))
        self.assertTrue(not rules['tenant-admin'](claims_1, tenant_two))
        self.assertTrue(not rules['tenant-admin'](claims_2, tenant_one))

    def test_tenant_substitution_in_dict(self):
        claims_2 = {
            'path': {
                'to': {
                    'group': 'tenant-two-admin'
                }
            }
        }
        rules = self.scheds.first.sched.abide.admin_rules
        tenant_one = self.scheds.first.sched.abide.tenants.get('tenant-one')
        tenant_two = self.scheds.first.sched.abide.tenants.get('tenant-two')
        self.assertTrue(not rules['tenant-admin-complex'](claims_2,
                                                          tenant_one))
        self.assertTrue(rules['tenant-admin-complex'](claims_2, tenant_two))


class TestTenantExtra(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/extra.yaml'

    def test_tenant_extra(self):
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        self.assertTrue('project2-extra-file' in tenant.layout.jobs)
        self.assertTrue('project2-extra-dir' in tenant.layout.jobs)

    def test_dynamic_extra(self):
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: project2-extra-file2
                parent: common-config-job
            - project:
                name: org/project2
                check:
                  jobs:
                    - project2-extra-file2
            """)
        file_dict = {'extra.yaml': in_repo_conf, '.zuul.yaml': ''}
        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A',
                                           files=file_dict)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='common-config-job', result='SUCCESS', changes='1,1'),
            dict(name='project2-extra-file2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    def test_extra_reconfigure(self):
        in_repo_conf = textwrap.dedent(
            """
            - job:
                name: project2-extra-file2
                parent: common-config-job
            - project:
                name: org/project2
                check:
                  jobs:
                    - project2-extra-file2
            """)
        file_dict = {'extra.yaml': in_repo_conf}
        A = self.fake_gerrit.addFakeChange('org/project2', 'master', 'A',
                                           files=file_dict)
        A.setMerged()
        self.fake_gerrit.addEvent(A.getChangeMergedEvent())
        self.waitUntilSettled()
        self.fake_gerrit.addEvent(A.getRefUpdatedEvent())
        self.waitUntilSettled()

        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='common-config-job', result='SUCCESS', changes='2,1'),
            dict(name='project2-job', result='SUCCESS', changes='2,1'),
            dict(name='project2-extra-file2', result='SUCCESS', changes='2,1'),
        ], ordered=False)


class TestTenantExtraConfigsInvalidType(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/extra_invalid_type.yaml'

    # This test raises a config error during the startup of the test
    # case which makes the first scheduler fail during its startup.
    # The second (or any additional) scheduler won't even run as the
    # startup is serialized in tests/base.py.
    # Thus it doesn't make sense to execute this test with multiple
    # schedulers.
    scheduler_count = 1

    def setUp(self):
        err = "Expected str or list of str for extra-config-paths.*"
        with testtools.ExpectedException(vs.MultipleInvalid, err):
            super().setUp()

    def test_tenant_extra_configs_invalid_type(self):
        # The magic is in setUp
        pass


class TestTenantExtraConfigsInvalidValue(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/extra_invalid_value.yaml'

    # This test raises a config error during the startup of the test
    # case which makes the first scheduler fail during its startup.
    # The second (or any additional) scheduler won't even run as the
    # startup is serialized in tests/base.py.
    # Thus it doesn't make sense to execute this test with multiple
    # schedulers.
    scheduler_count = 1

    def setUp(self):
        err = "Default zuul configs are not allowed in extra-config-paths.*"
        with testtools.ExpectedException(vs.MultipleInvalid, err):
            super().setUp()

    def test_tenant_extra_configs_invalid_value(self):
        # The magic is in setUp
        pass


class TestTenantDuplicate(TenantParserTestCase):
    tenant_config_file = 'config/tenant-parser/duplicate.yaml'

    # This test raises a config error during the startup of the test
    # case which makes the first scheduler fail during its startup.
    # The second (or any additional) scheduler won't even run as the
    # startup is serialized in tests/base.py.
    # Thus it doesn't make sense to execute this test with multiple
    # schedulers.
    scheduler_count = 1

    def setUp(self):
        with testtools.ExpectedException(Exception, 'Duplicate configuration'):
            super().setUp()

    def test_tenant_dupe(self):
        # The magic is in setUp
        pass
