#!/usr/bin/env python

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

import argparse
from zuul.lib import encryption
import zuul.configloader
import zuul.model


DESCRIPTION = """Decrypt a Zuul secret.
"""


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('private_key',
                        help="The path to the private key")
    parser.add_argument('file',
                        help="The YAML file with secrets")
    args = parser.parse_args()

    (private_secrets_key, public_secrets_key) = \
        encryption.deserialize_rsa_keypair(open(args.private_key, 'rb').read())
    parser = zuul.configloader.SecretParser(None)
    sc = zuul.model.SourceContext('project', 'master', 'path', False)

    data = zuul.configloader.safe_load_yaml(open(args.file).read(), sc)
    for element in data:
        if 'secret' not in element:
            continue
        s = element['secret']
        secret = parser.fromYaml(s)
        print(secret.name)
        print(secret.decrypt(private_secrets_key).secret_data)


if __name__ == '__main__':
    main()
