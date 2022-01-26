from setuptools import setup, find_packages


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    with open(join(dirname(__file__), module_name, "__init__.py")) as f:
        return match(r".*__version__.*('|\")(.*?)('|\")", f.read(), S).group(2)


def get_dependencies():
    from sys import version_info

    if version_info[:2] < (3, 5):
        yield "typing"
    yield "requests"


setup(
    name="smsit",
    version=read_version("smsit"),
    author="Meyti",
    description="A simple wrapper to send SMS through available gateways.",
    long_description=open("README.rst").read(),
    packages=find_packages(),
    install_requires=list(get_dependencies()),
    license="MIT License",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
