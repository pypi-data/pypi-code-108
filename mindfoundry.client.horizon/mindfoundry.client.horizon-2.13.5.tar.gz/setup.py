import os

from setuptools import find_namespace_packages, setup

# Must be set by CI
version = os.environ["VERSION"]

# It's necessary to pin the httpx version, otherwise it will break file upload.
# Newer version throw an error when getting StringIO instead of a bytes-like object.
# See datasets_client.py:100 (_upload_csv function)
# See job: https://gitlab.mflocal.com/research/horizon/-/jobs/907935
install_requires = [
    "numpy",
    "pandas",
    "requests",
    "attrs",
    "httpx>=0.16.1,<0.19",
    "python-dateutil"
]

dev_extras = [
    "black==20.8b1",
    "check-manifest==0.46",
    "coverage==5.5",
    "isort==5.8.0",
    "mypy==0.812",
    "pre-commit==2.11.1",
    "pylint==2.7.2",
    "pytest==6.2.4",
    "pytest-httpx==0.12.0",
    "pytest-timeout==1.4.2",
    "pytest-tldr==0.2.4",
    "pytest-asyncio==0.14.0",
    "bandit==1.7.0",
]

extras_require = {
    "dev": dev_extras,
    "all": install_requires + dev_extras,
}

with open("README.md", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="mindfoundry.client.horizon",
    version=version,
    license="MIT",
    description="Mind Foundry Horizon Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://mindfoundry.ai/horizon",
    author="Mind Foundry Ltd",
    author_email="support@mindfoundry.ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    namespace_packages=["mindfoundry"],
)
