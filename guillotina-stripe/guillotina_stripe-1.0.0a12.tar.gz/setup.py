# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


test_reqs = [
    "async_asgi_testclient",
    "pytest>=5.0",
    "pytest-asyncio",
    "pytest-docker-fixtures[pg]>=1.3.0",
    "prometheus-client>=0.9.0",
]


setup(
    name="guillotina_stripe",
    version=open("VERSION").read().strip(),
    description="guillotina stripe support",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGELOG.rst").read()),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="Ramon Navarro Bosch",
    author_email="ramon@plone.org",
    keywords="guillotina stripe ldap",
    url="https://pypi.python.org/pypi/guillotina_stripe",
    license="GPL version 3",
    setup_requires=["pytest-runner"],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=["ez_setup"]),
    package_data={"": ["*.txt", "*.rst"], "guillotina_stripe": ["py.typed"]},
    install_requires=[
        "setuptools",
        "guillotina>=6.0",
        "aiohttp",
        "retry",
        "pydantic"
    ],
    extras_require={"test": test_reqs},
    tests_require=test_reqs,
    entry_points={"guillotina": ["include = guillotina_stripe", ]},
)
