from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="masonite-package-sync",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.5.0",
    package_dir={"": "src"},
    description="Masonite package synchronisation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/girardinsamuel/masonite-package-sync",
    # Author details
    author="Samuel Girardin",
    author_email="sam@masoniteproject.com",
    # Choose your license
    license="MIT",
    # List run-time dependencies here
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        "cleo>=0.8.1,<0.9",
    ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Web Environment",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # What does your project relate to?
    keywords="Masonite, MasoniteFramework, Python, Packages",
    extras_require={
        "test": [
            "coverage",
            "black",
            "flake8",
            "pytest",
            "twine",
            "bump2version",
        ],
    },
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "masonite-package = masonite_package_sync.main:application.run",
        ],
    },
)
