from typing import List
from setuptools import setup, find_packages
import os
import sys

# From https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-package-version
def read_project_file(relative_file_path: str):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, relative_file_path), 'r') as file_pointer:
        return file_pointer.read()


def installation_requirements() -> List[str]:
    install_requires = [
        "requests>=2.0",
        "ConfigArgParse>=1.0,<2",
        "anytree>=2.0",
        "art>=2.0",
        "mdfrag==0.1.0",
    ]
    if sys.version_info.minor < 7:
        install_requires.append('dataclasses>=0.6')
    return install_requires


setup(
    name="ntsbuildtools",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    version='4.0.3',  # We attempt to follow 'semantic versioning', i.e. https://semver.org/ 
    license='MIT',
    description="CLI toolset that supports CICD processes.",
    long_description_content_type='text/markdown',
    long_description=read_project_file('docs/user-guide.md'),
    author='Network & Telecom Svcs (University of Oregon)',
    author_email='rleonar7@uoregon.edu',
    url='https://git.uoregon.edu/projects/ISN/repos/buildtools/browse',
    keywords=['Jenkins', 'NTS', 'UO', 'CLI', 'Integrations', 'API'],
    entry_points={
        'console_scripts': [
            'buildtools=ntsbuildtools.main:main'
        ]
    },
    install_requires=installation_requirements(),
    classifiers=[  # Classifiers selected from https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers', 
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
