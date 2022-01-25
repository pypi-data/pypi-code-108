import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="umnet_ncs_instances",
    version="0.0.10",
    author="University of Michigan",
    author_email="amylieb@umich.edu",
    description="Python object representing NSO service or device instances.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.umich.edu/its-inf-net/umnet-ncs-instances",
    packages=setuptools.find_packages(),
    install_requires=[
        'lxml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
