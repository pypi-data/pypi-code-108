import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kaskada",
    version="0.0.10",
    author="Kaskada",
    author_email="support@kaskada.com",
    description="A client library for the Kaskada time travel machine learning service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://kaskada.com",
    project_urls={
        "Documentation": "https://docs.kaskada.com/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Jupyter",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
    package_dir={"": "src"},
    packages=["kaskada"],
    python_requires=">=3.6",
    install_requires=[
        'googleapis-common-protos',
        'grpcio-status',
        'grpcio~=1.34.0',
        'kaskada_grpc',
        'pandas',
        'protobuf',
        'pyarrow',
        'requests',
        'certifi'
    ],
)
