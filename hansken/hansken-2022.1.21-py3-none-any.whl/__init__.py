# encoding=utf-8

"""
Copyright 2015 Netherlands Forensic Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pkg_resources import resource_string


try:
    # read the resource VERSION as binary data to determine value for __version__
    __version__ = resource_string(__name__, 'VERSION').decode('utf-8').strip()
except Exception:
    __version__ = '0.0+unknown'


class envvars:  # noqa: N801
    """
    `hansken.envvars` contains the names of all :ref:`environment variables
    <command_line>` used by the commands available from the command line and
    functions like `auth.from_env <hansken.auth.from_env>` to read
    configuration values from environment variables.
    """
    pass


envvars = envvars()
for key, envvar in {'endpoint': 'HANSKEN_ENDPOINT',
                    'project': 'HANSKEN_PROJECT',
                    'keystore': 'HANSKEN_KEYSTORE_ENDPOINT',
                    'preference': 'HANSKEN_PREFERENCE_ENDPOINT',
                    'log': 'HANSKEN_LOG',
                    'idp': 'HANSKEN_IDP',
                    'idp_url': 'HANSKEN_IDP_ENDPOINT',
                    'idp_realm': 'HANSKEN_IDP_REALM',
                    'sso_url': 'HANSKEN_SSO_ENDPOINT',
                    'hdfs': 'HANSKEN_HDFS_ENDPOINT'}.items():
    setattr(envvars, key, envvar)


class fetch:  # noqa: N801
    """
    `hansken.fetch` is a sentinel value that is used to indicate that a
    resource should be automatically fetched, if possible. Resources mostly
    concern keys used to access data or metadata. `key` parameters for methods
    like `Trace.open <hansken.trace.Trace.open>` will have this value as the
    default, allowing you to manually specify a value if needed.
    """
    def __repr__(self):
        return '<auto-fetch>'  # help() shows this when fetch occurs as a default for an argument

    __str__ = __repr__


fetch = fetch()
