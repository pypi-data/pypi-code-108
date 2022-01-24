import setuptools

with open("../customer-docs/Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlmorph_api",
    version="2.4.0",
    author="phData Internal Engineering",
    author_email="sqlmorph-support@phdata.io",
    description="SQLMorph translates from legacy SQL dialects to modern SQL dialects. This tool runs the translation in batch.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.phdata.io/sqlmorph/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.2',
)
