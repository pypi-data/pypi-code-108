import setuptools


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()



setuptools.setup(
    name="LavaAPI",
    version="1.0.1",
    author="billiedark",
    author_email="hhxx213@gmail.com",
    description="A simple library for accepting payments and using the LAVA Wallet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/billiedark/LavaAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)