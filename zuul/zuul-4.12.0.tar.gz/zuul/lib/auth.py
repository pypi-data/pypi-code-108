# Copyright 2019 OpenStack Foundation
# Copyright 2019 Red Hat, Inc.
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
import re
import jwt

from zuul import exceptions
import zuul.driver.auth.jwt as auth_jwt
import zuul.lib.capabilities as cpb


"""AuthN/AuthZ related library, used by zuul-web."""


class AuthenticatorRegistry(object):
    """Registry of authenticators as they are declared in the configuration"""

    log = logging.getLogger("Zuul.AuthenticatorRegistry")

    def __init__(self):
        self.authenticators = {}
        self.default_realm = None

    def configure(self, config):
        capabilities = {'realms': {}}
        first_realm = None
        for section_name in config.sections():
            auth_match = re.match(r'^auth ([\'\"]?)(.*)(\1)$',
                                  section_name, re.I)
            if not auth_match:
                continue
            auth_name = auth_match.group(2)
            auth_config = dict(config.items(section_name))

            if 'driver' not in auth_config:
                raise Exception("Auth driver needed for %s" % auth_name)

            auth_driver = auth_config['driver']
            try:
                driver = auth_jwt.get_authenticator_by_name(auth_driver)
            except IndexError:
                raise Exception(
                    "Unknown driver %s for auth %s" % (auth_driver,
                                                       auth_name))
            # TODO catch config specific errors (missing fields)
            self.authenticators[auth_name] = driver(**auth_config)
            caps = self.authenticators[auth_name].get_capabilities()
            # TODO there should be a bijective relationship between realms and
            # authenticators. This should be enforced at config parsing.
            capabilities['realms'].update(caps)
            if first_realm is None:
                first_realm = auth_config.get('realm', None)
            if auth_config.get('default', 'false').lower() == 'true':
                self.default_realm = auth_config.get('realm', 'DEFAULT')
        # do we have any auth defined ?
        if len(capabilities['realms'].keys()) > 0:
            if self.default_realm is None:
                # pick arbitrarily the first defined realm
                self.default_realm = first_realm
        capabilities['default_realm'] = self.default_realm
        cpb.capabilities_registry.register_capabilities('auth', capabilities)

    def authenticate(self, rawToken):
        unverified = jwt.decode(rawToken, options={'verify_signature': False})
        for auth_name in self.authenticators:
            authenticator = self.authenticators[auth_name]
            if authenticator.issuer_id == unverified.get('iss', ''):
                return authenticator.authenticate(rawToken)
        # No known issuer found, use default realm
        raise exceptions.IssuerUnknownError(self.default_realm)
