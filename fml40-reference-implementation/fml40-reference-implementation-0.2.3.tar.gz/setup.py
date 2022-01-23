import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fml40-reference-implementation",
    version="0.2.3",
    author="Kompetenzzentrum Wald und Holz 4.0",
    author_email="s3i@kwh40.de",
    description="fml40 reference implementation basic functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.kwh40.de/",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
        "jsonschema",
        "s3i==0.6.0",
        #"s3i@https://git.rwth-aachen.de/kwh40/s3i/-/jobs/artifacts/master/raw/public/s3i-0.5.3-py3-none-any.whl?job=wheel"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ]
)
