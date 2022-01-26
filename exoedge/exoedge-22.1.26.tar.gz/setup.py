"""
Installer for ExoSense Client
"""
import os
from setuptools import setup, find_packages
from exoedge import __version__

DOCS_URL = 'https://github.com/exosite/lib_exoedge_python'

INSTALL_REQUIRES = [
    'appdirs',
    'docopt>=0.6.2',
    'jsonschema==3.2.0',
    'pureyaml',
    'murano-client>=19.5.8',
    'ruamel.yaml',
    'six',
    'urllib3==1.26.7'
]


def read(fname):
    """ Primarily used to open README file. """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    README = read('README.rst')
except:
    README = ''

setup(
    name="exoedge",
    version=__version__,
    author="Exosite LLC",
    author_email="support@exosite.com",
    description="""ExoEdge is the Python library for interacting with Exosite's ExoSense Industrial IoT Solution.""",
    license="Apache 2.0",
    keywords="murano exosite iot iiot gateway edge exoedge exosense",
    url="https://github.com/exosite/lib_exoedge_python",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'edged = exoedge.edged:main'
        ]
    },
    install_requires=INSTALL_REQUIRES,
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Internet",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
    ],
    data_files=[],
    package_data={'exoedge': ['config_io_schema.yaml']}
    )
