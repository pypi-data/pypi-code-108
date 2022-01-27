#!/usr/bin/env python

from setuptools import setup
import re
import os
import sys

from docums.commands.setup import babel_cmdclass

with open('README.md') as f:
    long_description = f.read()


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep Babel"):
        print("babel not installed.\nUse `pip install babel`.\nExiting.")
        sys.exit()
    for locale in os.listdir("docums/themes/docums/locales"):
        os.system(f"python setup.py compile_catalog -t docums -l {locale}")
        os.system(f"python setup.py compile_catalog -t readthedocs -l {locale}")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(get_version("docums")))
    print("  git push --tags")
    sys.exit()


setup(
    name="docums",
    version=get_version("docums"),
    url='https://khanhduy1407.github.io/docums',
    license='BSD',
    description='Open source documentation website',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='NKDuy',
    author_email='kn145660@gmail.com',  # SEE NOTE BELOW (*)
    packages=get_packages("docums"),
    include_package_data=True,
    install_requires=[
        'click>=3.3',
        'Jinja2>=2.10.1',
        'Markdown>=3.2.1',
        'PyYAML>=3.10',
        'watchdog>=2.0',
        'ghp-import>=1.0',
        'pyyaml_env_tag>=0.1',
        'importlib_metadata>=3.10',
        'packaging>=20.5',
        'mergedeep>=1.3.4'
    ],
    extras_require={"i18n": ['babel>=2.9.0']},
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'docums = docums.__main__:cli',
        ],
        'docums.themes': [
            'docums = docums.themes.docums',
            'readthedocs = docums.themes.readthedocs',
        ],
        'docums.plugins': [
            'search = docums.contrib.search:SearchPlugin',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Documentation',
        'Topic :: Text Processing',
    ],
    zip_safe=False,
    cmdclass=babel_cmdclass,
)
