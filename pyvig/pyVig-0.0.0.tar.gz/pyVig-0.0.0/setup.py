import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyVig",
    version="0.0.0",
    author="ALIASGAR - ALI",
    author_email="aholo2000@gmail.com",
    description="python based Visio Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alias1978/pyVig",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['pandas', 'xlrd', 'openpyxl', 'nettoolkit']
)

