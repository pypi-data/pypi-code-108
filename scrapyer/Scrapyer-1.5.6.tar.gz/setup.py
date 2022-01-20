from os.path import dirname, join
import io,os
from pkg_resources import parse_version
from setuptools import setup, find_packages, __version__ as setuptools_version
import sys


with open(join(dirname(__file__), 'scrapy/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

here = os.path.abspath(os.path.dirname(__file__))

magic_package_choice = 'python-magic-bin==0.4.14' if sys.platform.startswith("win") else 'python-magic==0.4.24' 

def has_environment_marker_platform_impl_support():
    """Code extracted from 'pytest/setup.py'
    https://github.com/pytest-dev/pytest/blob/7538680c/setup.py#L31

    The first known release to support environment marker with range operators
    it is 18.5, see:
    https://setuptools.readthedocs.io/en/latest/history.html#id235
    """
    return parse_version(setuptools_version) >= parse_version('18.5')

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = ''

install_requires = [
    'Twisted>=17.9.0',
    'cryptography>=2.0',
    'cssselect>=0.9.1',
    'itemloaders>=1.0.1',
    'parsel>=1.5.0',
    'pyOpenSSL>=16.2.0',
    'queuelib>=1.4.2',
    'service_identity>=16.0.0',
    'w3lib>=1.17.0',
    'zope.interface>=4.1.3',
    'protego>=0.1.15',
    'itemadapter>=0.1.0',
    'setuptools==49.2.1',
    "oss2==2.14.0",
    "openpyxl==3.0.5",
    "PyPDF2==1.26.0",
    "pymysql==0.9.3",
    "pymongo==3.12",
    "redis==3.5.3",
    "pdfplumber==0.5.28",
    "pillow==8.0.1",
    "js2py==0.71",
    "pandas==1.1.4",
    magic_package_choice,
    "scrapyer-rabbitmq-scheduler",
    "scrapyer-redis",
]
extras_require = {}
cpython_dependencies = [
    'lxml>=3.5.0',
    'PyDispatcher>=2.0.5',
]
if has_environment_marker_platform_impl_support():
    extras_require[':platform_python_implementation == "CPython"'] = cpython_dependencies
    extras_require[':platform_python_implementation == "PyPy"'] = [
        # Earlier lxml versions are affected by
        # https://foss.heptapod.net/pypy/pypy/-/issues/2498,
        # which was fixed in Cython 0.26, released on 2017-06-19, and used to
        # generate the C headers of lxml release tarballs published since then, the
        # first of which was:
        'lxml>=4.0.0',
        'PyPyDispatcher>=2.1.0',
    ]
else:
    install_requires.extend(cpython_dependencies)


setup(
    name='Scrapyer',
    version=version,
    url='https://scrapy.org',
    project_urls={
        'Documentation': 'https://docs.scrapy.org/',
        'Source': 'https://github.com/buliqioqiolibusdo/scrapyer',
        'Tracker': 'https://github.com/buliqioqiolibusdo/scrapyer/issues',
    },
    description='Based on scrapy framework, combined with common component tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='buliqioqiolibusdo',
    author_email = 'dingyeran@163.com',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*','Scrapyer.egg-info','extras','docs')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['scrapy = scrapy.cmdline:execute']
    },
    # classifiers=[
    #     'Framework :: Scrapy',
    #     'Development Status :: 5 - Production/Stable',
    #     'Environment :: Console',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: BSD License',
    #     'Operating System :: OS Independent',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.6',
    #     'Programming Language :: Python :: 3.7',
    #     'Programming Language :: Python :: 3.8',
    #     'Programming Language :: Python :: 3.9',
    #     'Programming Language :: Python :: 3.10',
    #     'Programming Language :: Python :: Implementation :: CPython',
    #     'Programming Language :: Python :: Implementation :: PyPy',
    #     'Topic :: Internet :: WWW/HTTP',
    #     'Topic :: Software Development :: Libraries :: Application Frameworks',
    #     'Topic :: Software Development :: Libraries :: Python Modules',
    # ],
    python_requires='>=3.6',
    install_requires=install_requires,
    extras_require=extras_require,
)
