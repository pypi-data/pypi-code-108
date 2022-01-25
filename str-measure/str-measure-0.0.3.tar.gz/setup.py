import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="str-measure",
    version="0.0.3",
    author="Nemu627",
    author_email="nemu.otoyume@gmail.com",
    description="Measure the length of a string.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nemu627/str-measure",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)