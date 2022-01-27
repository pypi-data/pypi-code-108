import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="featureform",
    version="0.0.14",
    author="Featureform",
    author_email="simba@featureform.com",
    description="Data infrastructure for machine learning embeddings and other features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/featureform/embeddinghub",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "protobuf",
        "hnswlib",
        "numpy",
        "grpcio-tools",
    ],
    python_requires=">=3.6",
)
