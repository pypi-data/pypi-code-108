#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json

from setuptools import setup, find_packages

with open('package_info.json', 'r') as file:
    package_info = json.load(file)

package_name = package_info['package_name'].replace('-', '_')
package_version = package_info['package_version']

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
    name=package_name,
    version=package_version,
    description=package_name,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TH2-devs',
    author_email='th2-devs@exactprosystems.com',
    url='https://github.com/th2-net/th2-common-py',
    license='Apache License 2.0',
    python_requires='>=3.7',
    install_requires=[
        'pika==1.2.0',
        'th2-grpc-common~=3.8.0',
        'kubernetes==18.20.0',
        'prometheus_client==0.11.0'
    ],
    packages=[''] + find_packages(include=['th2_common', 'th2_common.*']),
    package_data={'': ['package_info.json'], 'th2_common.schema.log': ['config.conf']}
)
