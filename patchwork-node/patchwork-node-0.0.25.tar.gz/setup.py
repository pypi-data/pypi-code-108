import os

from pip._internal.req import parse_requirements
from setuptools import setup, find_namespace_packages

version = os.environ.get('CI_COMMIT_TAG', f"0.0.dev{os.environ['CI_JOB_ID']}")
if '-' in version:
    # version tag should be like: node-1.0.0
    version = version.split('-')[1]

last_part = version.split('.')[-1]
version_classifier = "5 - Production/Stable"

if 'dev' in last_part:
    version_classifier = "2 - Pre-Alpha"
elif 'a' in last_part:
    version_classifier = "3 - Alpha"
elif 'b' in last_part:
    version_classifier = "4 - Beta"

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = parse_requirements('requirements.txt', session=None)

setup(
    name='patchwork-node',
    version=version,
    packages=['patchwork.node'] + find_namespace_packages(include="patchwork.node.*"),
    url='',
    author='Pawel Pecio',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='Worker node for Patchwork - The distributed asynchronous microframework',
    zip_safe=False,
    install_requires=[str(ir.requirement) for ir in dependencies],
    classifiers=[
        f"Development Status :: {version_classifier}",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)
