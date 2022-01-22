from os.path import join, dirname, abspath

from setuptools import setup, find_namespace_packages

curdir = abspath(dirname(__file__))
readme = open(join(curdir, 'README.md')).read()

setup(
    name             = 'setux_repl',
    version          = '0.22.03.0',
    description      = 'System deployment',
    long_description = readme,
    long_description_content_type='text/markdown',
    keywords         = ['utility', ],
    url              = 'https://framagit.org/louis-riviere-xyz/setux_repl',
    author           = 'Louis RIVIERE',
    author_email     = 'louis@riviere.xyz',
    license          = 'MIT',
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    python_requires='>3.6',
    install_requires = [
        'setux>=0.22.03.0',
    ],
    packages = find_namespace_packages(
        include=['setux.*']
    ),
    entry_points = dict(
        console_scripts = (
            'setux=setux.cli.main:main',
        ),
    ),
)
