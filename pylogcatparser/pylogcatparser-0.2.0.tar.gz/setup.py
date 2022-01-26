import setuptools
from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pylogcatparser',
    description='LogCatParser: A simple Android logcat parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rui Rua',
    author_email='rui.rrua@gmail.com',
    url='https://github.com/RRua/logcatparser',
    license='MIT',
    packages=setuptools.find_packages(),
    use_incremental=True,
    install_requires=required,
    setup_requires=['incremental'],
    include_package_data=True,
    scripts=['bin/logcatparser'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
    ],
    project_urls={
        'Bug Tracker':  'https://github.com/RRua/logcatparser/issues'
        },
    python_requires=">=3.6",
)
