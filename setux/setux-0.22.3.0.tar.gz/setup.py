from os.path import join, dirname, abspath

from setuptools import setup, find_namespace_packages

from setux.main import __version__

curdir = abspath(dirname(__file__))
readme = open(join(curdir, 'README.md')).read()

setup(
    name             = 'setux',
    version          = __version__,
    description      = 'System deployment',
    long_description = readme,
    long_description_content_type='text/markdown',
    keywords         = ['utility', ],
    url              = 'https://framagit.org/louis-riviere-xyz/setux',
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
        'setux_core>=0.22.03.0',
        'setux_distros>=0.22.02.0',
        'setux_logger>=0.21.50.0',
        'setux_managers>=0.22.03.0',
        'setux_mappings>=0.21.52.0',
        'setux_modules>=0.22.02.0',
        'setux_targets>=0.22.02.0',
    ],
    packages = find_namespace_packages(
        include=['setux.*']
    ),
)
