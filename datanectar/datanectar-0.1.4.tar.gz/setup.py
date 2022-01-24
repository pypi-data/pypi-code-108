# pylint: disable=C0103, C0111, C0326, W0122

from setuptools import setup

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()


def get_version():
    version = {}
    with open("datanectar/version.py") as fp:
        exec(fp.read(), version)
    return version['__version__']


def get_readme():
    #try:
    #    import pypandoc
    #    readme_data = pypandoc.convert('README.md', 'rst')
    #except(IOError, ImportError):
    #    readme_data = open('README.md').read()
    readme_data = 'datanectar'
    return readme_data


setup(
    name = 'datanectar',
    packages = ['datanectar'],
    url = 'https://github.com/madconsulting/datanectar',
    version = get_version(),
    description = 'Artifact tracking for luigi',
    long_description = get_readme(),
    author = 'Wes Madrigal, Caleb Madrigal',
    author_email = 'admin@madconsulting.ai',
    license = 'MIT',
    keywords = ['data', 'luigi', 'ml'],
    install_requires = requirements,
    tests_require = requirements,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS'
    ],
)
