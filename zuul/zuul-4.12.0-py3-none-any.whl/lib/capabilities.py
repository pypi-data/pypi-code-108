# Copyright 2020 OpenStack Foundation
# Copyright 2020 Red Hat, Inc.
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


import logging


"""Simple Capabilities registry, to be used by Zuul Web."""


class CapabilitiesRegistry(object):

    log = logging.getLogger("Zuul.CapabilitiesRegistry")

    def __init__(self):
        self.capabilities = {}
        self.set_default_capabilities()

    def set_default_capabilities(self):
        self.capabilities['job_history'] = False
        self.capabilities['auth'] = {
            'realms': {},
            'default_realm': None,
        }

    def register_capabilities(self, capability_name, capabilities):
        is_set = self.capabilities.setdefault(capability_name, None)
        if is_set is None:
            action = 'registered'
        else:
            action = 'updated'
        if isinstance(is_set, dict) and isinstance(capabilities, dict):
            self.capabilities[capability_name].update(capabilities)
        else:
            self.capabilities[capability_name] = capabilities
        self.log.debug('Capabilities "%s" %s' % (capability_name, action))


capabilities_registry = CapabilitiesRegistry()
