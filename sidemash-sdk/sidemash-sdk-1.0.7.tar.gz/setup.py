import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sidemash-sdk",
    version="1.0.7",
    author="Sidemash Cloud Services",
    author_email="opensource@sidemash.com",
    description="Official SDK to use Sidemash Cloud Services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sidemash/sdk-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
