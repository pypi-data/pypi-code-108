"""Setup for MQTT hass base."""
import sys

import setuptools
from distutils.util import convert_path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if sys.version_info < (3, 7):
    sys.exit("Sorry, Python < 3.7 is not supported")

install_requires = list(val.strip() for val in open("requirements.txt"))
tests_require = list(val.strip() for val in open("test_requirements.txt"))

main_ns = {}
ver_path = convert_path('src/hydroqc/__version__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setuptools.setup(
    version=main_ns['VERSION'],
    install_requires=install_requires,
    tests_require=tests_require,
)
