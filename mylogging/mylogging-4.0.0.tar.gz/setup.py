#%%
from setuptools import setup, find_packages
import pkg_resources
import mylogging

version = mylogging.__version__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    myreqs = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

setup(
    author_email="malachovd@seznam.cz",
    author="Daniel Malachov",
    description="Small library for printing warnings and creating logs.",
    include_package_data=True,
    install_requires=myreqs,
    license="mit",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="mylogging",
    packages=find_packages(exclude=("tests",)),
    platforms="any",
    project_urls={
        "Documentation": "https://mylogging.readthedocs.io/",
        "Home": "https://github.com/Malachov/mylogging",
    },
    python_requires=">=3.7",
    url="https://github.com/Malachov/mylogging",
    version=version,
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "Environment :: Other Environment",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    extras_require={},
)
