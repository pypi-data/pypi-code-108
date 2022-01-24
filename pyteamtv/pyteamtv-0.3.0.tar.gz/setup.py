import setuptools
import builtins
from distutils.core import setup


builtins.__PYTEAMTV_SETUP__ = True
import pyteamtv


def setup_package():
    with open("README.md", "r") as f:
        readme = f.read()

    setup(
        name="pyteamtv",
        version=pyteamtv.__version__,
        author="Koen Vossen",
        author_email="info@koenvossen.nl",
        url="https://github.com/teamtv/pyteamtv",
        packages=setuptools.find_packages(exclude=["tests"]),
        license="GPL-3",
        description="API for TeamTV Platform",
        long_description=readme,
        long_description_content_type="text/markdown",
        classifiers=[
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved",
            "Topic :: Scientific/Engineering",
        ],
        install_requires=[
            "requests>=2.0.0",
            "PyJWT>=1.7.1",
            "pyjwt[crypto]>=1.7.1",
            "tuspy==0.2.5"
        ],
        extras_require={
            "test": ["pytest", "pandas>=1.0.0"],
        },
    )


if __name__ == "__main__":
    setup_package()

    del builtins.__PYTEAMTV_SETUP__