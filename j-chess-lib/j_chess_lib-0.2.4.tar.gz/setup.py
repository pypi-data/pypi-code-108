#!/usr/bin/env python

"""The setup script."""
import os
from distutils.command import build_py, install_lib, sdist, bdist, upload
from distutils.dist import Distribution
from typing import Any, Type

from setuptools import setup, find_packages, Command

schema_package = os.environ.get("j-chess-schema-package", "j_chess_lib.communication.schema")
os.makedirs(schema_package.replace(".", "/"), exist_ok=True)

_installed_schema = [False]


def install_schema_package():
    if not _installed_schema[0]:
        print("-" * 10, "schema install", "-" * 10)
        xsd_url = os.environ.get("j-chess-xsd-url",
                                 "https://raw.githubusercontent.com/JoKrus/j-chess-xsd/master/jChessMessage.xsd")
        import subprocess
        try:
            subprocess.run(["rm", "-rf", "j_chess_lib/communication/schema"], check=True)
            print("Removed old schema data")
        except subprocess.CalledProcessError:
            pass
        print("Load schema data from %s and install them" % xsd_url)
        subprocess.run(["xsdata", xsd_url, "--package", schema_package], check=True)
        print("Installed new schema data")
        print("-" * 10, "schema install", "-" * 10)
    else:
        print("-" * 10, "schema already installed", "-" * 10)
    _installed_schema[0] = True


class InstallSchema(Command):
    key = "install_schema"
    description = "Create classes from the j-chess schema"
    user_options = []

    def __init__(self, dist: Distribution, **kw: Any):
        super().__init__(dist, **kw)

    def finalize_options(self) -> None:
        pass

    def initialize_options(self) -> None:
        pass

    def run(self):
        install_schema_package()


def install_schema_wrapper(class_type) -> Type[Command]:
    class Wrapper(class_type):

        def run(self) -> None:
            install_schema_package()
            super(Wrapper, self).run()

    return Wrapper


cmd_classes = {
    InstallSchema.key: InstallSchema,
    "build_py": install_schema_wrapper(build_py.build_py),
    "install_lib": install_schema_wrapper(install_lib.install_lib),
    "sdist": install_schema_wrapper(sdist.sdist),
    "bdist": install_schema_wrapper(bdist.bdist),
    "upload": install_schema_wrapper(upload.upload),
}

try:
    from wheel.bdist_wheel import bdist_wheel

    cmd_classes["bdist_wheel"] = install_schema_wrapper(bdist_wheel)
except ImportError:
    pass

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["xsdata[cli,lxml,soap]"]
test_requirements = []

setup(
    author="RedRem95",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python library for a j-chess bot. Beep Boop",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='j_chess_lib',
    name='j_chess_lib',
    packages=find_packages(include=['j_chess_lib', 'j_chess_lib.*']) + [schema_package],
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/RedRem95/j_chess_lib',
    version='0.2.4',
    zip_safe=True,
    cmdclass=cmd_classes,
)
