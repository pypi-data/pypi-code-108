"""setup.py"""
from pathlib import Path
from setuptools import setup, find_packages
from jsonclasses_cli.version import version
# The text of the README file
README = (Path(__file__).parent / "README.md").read_text()

setup(
    name='jsonclasses-cli',
    version=version,
    description=('JSONClasses CLI'),
    long_description=README,
    long_description_content_type='text/markdown',
    author='Fillmula Inc.',
    author_email='victor.teo@fillmula.com',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    package_data={'jsonclasses_cli': ['py.typed']},
    zip_safe=False,
    url='https://github.com/fillmula/jsonclasses-cli',
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'click>=8.0.3,<9.0.0',
        'rich>=10.12.0,<11.0.0',
        'jsonclasses>=3.1.4,<4.0.0',
        'jsonclasses-server>=3.1.4,<4.0.0'
    ],
    entry_points={
        'console_scripts': [
            'jsonclasses = jsonclasses_cli:app',
        ],
    },
)
