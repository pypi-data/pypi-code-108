import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="publiscord",
    version="0.0.1",
    author="Nemu627",
    author_email="nemu.otoyume@gmail.com",
    description="Automatically publish news.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nemu627/Publiscord",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
