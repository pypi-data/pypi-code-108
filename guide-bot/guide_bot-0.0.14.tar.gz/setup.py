import os
from setuptools import setup, find_packages

# Get version number
here = os.path.abspath(os.path.dirname(__file__))
version_path = os.path.join(here, "guide_bot", "_version.py")
version = {}
with open(version_path) as fp:
    exec(fp.read(), version)
found_version = version['__version__']
print("Version read from file:", found_version)

with open("README.md", "r") as fh:
    long_description = fh.read()



setup(
    name='guide_bot',
    version=found_version,
    author="Mads Bertelsen",
    author_email="Mads.Bertelsen@ess.eu",
    description="Neutron guide optimization package",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.esss.dk/highness/guide_bot",
    install_requires=["pyswarm", "dill", "numpy", "matplotlib", "PyYAML", "mcstasscript", "ipywidgets", "ipympl", "scipy"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering"

    ])
