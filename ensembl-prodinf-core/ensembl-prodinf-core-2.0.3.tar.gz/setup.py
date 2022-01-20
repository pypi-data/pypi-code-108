#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import pathlib
from setuptools import setup, find_namespace_packages

here = pathlib.Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')
version = (here / 'VERSION').read_text(encoding='utf-8').strip()


def import_requirements():
    """Import ``requirements.txt`` file located at the root of the repository."""
    with (here / 'requirements.txt').open(encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]


setup(
    name='ensembl-prodinf-core',
    description='Ensembl Production infrastructure core package',
    long_description=readme,
    version=version,
    namespace_packages=['ensembl'],
    packages=find_namespace_packages(where='src', include=['ensembl*'], exclude=['test']),
    package_dir={'': 'src'},
    include_package_data=True,
    url='https://github.com/Ensembl/ensembl-prodinf-core',
    license='Apache 2.0',
    author='Marc Chakiachvili,James Allen,Luca Da Rin Fioretto,Vinay Kaikala',
    author_email='mchakiachvili@ebi.ac.uk,jallen@ebi.ac.uk,ldrf@ebi.ac.uk,vkaikala@ebi.ac.uk',
    maintainer='Ensembl Production Team',
    maintainer_email='ensembl-production@ebi.ac.uk',
    python_requires='>=3.7',
    install_requires=import_requirements(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Operating System :: POSIX',
        'Natural Language :: English',
    ]
)
