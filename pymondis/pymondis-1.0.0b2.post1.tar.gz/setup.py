from setuptools import setup

from pymondis import metadata

with open("README.md", encoding="utf-8") as readme_file:
    README = readme_file.read()

with open("requirements.txt", "r") as requirements_file:
    REQUIREMENTS = requirements_file.read().splitlines()

setup(
    name=metadata.__title__,
    url="https://github.com/Asapros/pymondis",
    project_urls={
        "Tracker": "https://github.com/Asapros/pymondis/issues",
        "Source": "https://github.com/Asapros/pymondis"
    },
    version=metadata.__version__,
    packages=("pymondis",),
    license=metadata.__license__,
    author=metadata.__author__,
    description=metadata.__description__,
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=REQUIREMENTS,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: Polish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"
    ],
    keywords=("quatromondis", "yorck", "API", "HTTP", "async", "hugo")
)
