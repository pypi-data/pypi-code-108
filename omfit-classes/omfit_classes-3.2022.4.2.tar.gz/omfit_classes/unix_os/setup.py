import os
import setuptools

description = "Monkey patching of `os` builtin package to always use UNIX file conventions"

here = os.path.abspath(os.path.split(__file__)[0]) + os.sep
version = open(here + 'unix_os/version', 'r').read().strip()

setuptools.setup(
    name="unix_os",
    version=version,
    author="OMFIT developers",
    author_email="meneghini@fusion.gat.com",
    description=description,
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://omfit.io",
    classifiers=["Programming Language :: Python :: 2", "Programming Language :: Python :: 3", "Operating System :: OS Independent"],
    install_requires=[''],
    packages=['unix_os'],
    package_data={'unix_os': ['*.py', 'version']},
)
