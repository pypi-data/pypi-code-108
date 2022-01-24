# Copyright 2021 BMW Group
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

from zuul.lib.fingergw import FingerGateway
from zuul.zk.components import BaseComponent, ComponentRegistry

from tests.base import iterate_timeout, ZuulTestCase, ZuulWebFixture


class TestComponentRegistry(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setUp(self):
        super().setUp()

        self.component_registry = ComponentRegistry(self.zk_client)

    def assertComponentAttr(self, component_name, attr_name,
                            attr_value, timeout=10):
        for _ in iterate_timeout(
            timeout,
            f"{component_name} in cache has {attr_name} set to {attr_value}",
        ):
            components = list(self.component_registry.all(component_name))
            if (
                len(components) > 0 and
                getattr(components[0], attr_name) == attr_value
            ):
                break

    def assertComponentState(self, component_name, state, timeout=10):
        return self.assertComponentAttr(
            component_name, "state", state, timeout
        )

    def assertComponentStopped(self, component_name, timeout=10):
        for _ in iterate_timeout(
            timeout, f"{component_name} in cache is stopped"
        ):
            components = list(self.component_registry.all(component_name))
            if len(components) == 0:
                break

    def test_scheduler_component(self):
        self.assertComponentState("scheduler", BaseComponent.RUNNING)

    def test_executor_component(self):
        self.assertComponentState("executor", BaseComponent.RUNNING)

        self.executor_server.pause()
        self.assertComponentState("executor", BaseComponent.PAUSED)

        self.executor_server.unpause()
        self.assertComponentState("executor", BaseComponent.RUNNING)

        self.executor_server.unregister_work()
        self.assertComponentAttr("executor", "accepting_work", False)

        self.executor_server.register_work()
        self.assertComponentAttr("executor", "accepting_work", True)

        self.executor_server.zk_client.client.stop()
        self.assertComponentStopped("executor")

        self.executor_server.zk_client.client.start()
        self.assertComponentAttr("executor", "accepting_work", True)

    def test_merger_component(self):
        self._startMerger()
        self.assertComponentState("merger", BaseComponent.RUNNING)

        self.merge_server.pause()
        self.assertComponentState("merger", BaseComponent.PAUSED)

        self.merge_server.unpause()
        self.assertComponentState("merger", BaseComponent.RUNNING)

        self.merge_server.stop()
        self.merge_server.join()
        # Set the merger to None so the test doesn't try to stop it again
        self.merge_server = None

        try:
            self.assertComponentStopped("merger")
        except Exception:
            for kind, components in self.component_registry.all():
                self.log.error("Component %s has %s online", kind, components)
            raise

    def test_fingergw_component(self):
        config = configparser.ConfigParser()
        config.read_dict(self.config)
        config.read_dict({
            'fingergw': {
                'listen_address': '::',
                'port': '0',
                'hostname': 'janine',
            }
        })
        gateway = FingerGateway(
            config,
            command_socket=None,
            pid_file=None
        )
        gateway.start()

        try:
            self.assertComponentState("fingergw", BaseComponent.RUNNING)
            self.assertComponentAttr("fingergw", "hostname", "janine")
        finally:
            gateway.stop()

        self.assertComponentStopped("fingergw")

    def test_web_component(self):
        self.useFixture(
            ZuulWebFixture(
                self.changes, self.config, self.additional_event_queues,
                self.upstream_root, self.rpcclient, self.poller_events,
                self.git_url_with_auth, self.addCleanup, self.test_root
            )
        )

        self.assertComponentState("web", BaseComponent.RUNNING)
