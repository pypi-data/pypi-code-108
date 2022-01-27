

import setuptools


#with open("README.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="kosmos-client",
    version="0.8.1",
    author="Jan Janssen",
    author_email="Jan.Janssen@dfki.de",
    description="Client to connect to the KosmoS Platform",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    url="https://kosmos-lab.de/python-client/",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)