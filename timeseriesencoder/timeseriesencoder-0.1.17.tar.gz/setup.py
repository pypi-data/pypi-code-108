import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeseriesencoder",
    version="0.1.17",
    author="Keith Dyer",
    author_email="kilaxen@gmail.com",
    description=" package for encoding and decoding time series in JSON files into embedded base 16, 64, or 91 encodings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires= [
        "numpy",
        "ciso8601",
        "numpyencoder"
    ]
)