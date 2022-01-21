import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="speck",
    version="0.0.0",
    author="Todd Gamblin",
    author_email="tgamblin@llnl.gov",
    description="coming soon.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/speckpm/speck.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
)
