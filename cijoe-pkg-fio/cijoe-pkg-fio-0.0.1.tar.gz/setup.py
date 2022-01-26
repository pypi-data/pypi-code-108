"""
    Definition of CIJOE fio extractor distribution package
"""
import codecs
import os
import glob
from setuptools import setup


def read(*parts):
    """Read parts to use a e.g. long_description"""

    here = os.path.abspath(os.path.dirname(__file__))

    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as pfp:
        return pfp.read()


setup(
    name="cijoe-pkg-fio",
    version="0.0.1",
    description="CIJOE: extract data from fio dumps",
    long_description=read('README.rst'),
    author="Michael Bang",
    author_email="mi.bang@samsung.com",
    url="https://github.com/refenv/cijoe-pkg-fio",
    license="Apache License 2.0",
    packages=["cijoe_extractors"],
    install_requires=[
        "cijoe (>=0.2.3)"
    ],
    zip_safe=False,
    data_files=[
        ("share/cijoe/envs", glob.glob("envs/*")),

        ("share/cijoe/testfiles", glob.glob("testfiles/*")),
        ("share/cijoe/testcases", glob.glob("testcases/*")),
        ("share/cijoe/testsuites", glob.glob("testsuites/*")),
        ("share/cijoe/testplans", glob.glob("testplans/*")),
        ("share/cijoe/hooks", glob.glob("hooks/*"))
    ],
    options={'bdist_wheel': {'universal': True}},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing"
    ],
)
