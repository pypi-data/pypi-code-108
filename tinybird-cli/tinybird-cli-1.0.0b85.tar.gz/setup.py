from pathlib import Path

from setuptools import setup, find_packages
import os


def package_files(directory):
    paths = []
    for (path, _directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


def requirements_from_file(path):
    return [
        line.strip()
        for line in Path(path).read_text().split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


extra_files = package_files('tinybird/templates') + package_files('tinybird/static') + \
    package_files('tinybird/default_tables') + package_files('tinybird/default_pipes') + \
    package_files('tinybird/sql')


setup(
    name='tinybird',
    version='1.0',
    description='tinybird',
    long_description='tinybird analytics',
    long_description_content_type='text/markdown',
    author='tinybird.co',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements_from_file('requirements.txt'),
    package_dir={"tinybird": "tinybird/"},
    package_data={
        # 'tinybird': ['../templates/*', '../static/*']
        'tinybird': extra_files
    },
    setup_requires=[
        'pytest-runner',
        'cffi==1.14.5'
    ],
    cffi_modules=[
        "tinybird/fast_leb128_build.py:ffibuilder",
        "tinybird/csv_importer_find_endline_build.py:ffibuilder"],  # "filename:global"
    extras_require={
        'test': requirements_from_file('requirements-test.txt') + requirements_from_file('requirements-linters.txt'),
        'deploy': [
            'ansible==2.10.7',
            'google-auth==1.27.1',
            'PyYAML==5.1',
        ],
        'doc': [
            'sphinx==4.2.0',
            'sphinx-autobuild==0.7.1',
            'Pallets-Sphinx-Themes',
            'sphinxcontrib-httpdomain'
        ],
        'devtools': [
            'matplotlib',
            'memory_profiler',
            'flameprof',
            'rope'
        ]
    },
    entry_points={
        'console_scripts': [
            'tinybird_server=tinybird.app:run',
            'tinybird_tool=tinybird.cli:cli',
            'tb=tinybird.tb_cli:cli',
        ],
    }
)
