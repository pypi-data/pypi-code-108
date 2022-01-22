import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vallaris", # Replace with your own username
    version="1.0.10",
    author="Sattawat Arab",
    author_email="support@vallarismaps.com",
    description="A package to processing Vallaris Maps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://v2k.vallarismaps.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires= ['jsonschema','ndjson','geojson','requests','geopandas','pandas','numpy','shapely','tqdm', 'python-dotenv'],
    python_requires='>=3.6',
)