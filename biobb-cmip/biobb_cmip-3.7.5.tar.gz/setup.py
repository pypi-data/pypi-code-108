import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_cmip",
    version="3.7.5",
    author="Biobb developers",
    author_email="pau.andrio@bsc.es",
    description="biobb_cmip is the Biobb module collection to compute classical molecular interaction potentials.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_cmip",
    project_urls={
        "Documentation": "http://biobb_cmip.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/"
    },
    packages=setuptools.find_packages(exclude=['docs', 'test']),
    include_package_data=True,
    install_requires=['biobb_common==3.7.0', 'mdanalysis==2.0.0', 'biobb_structure_checking==3.9.9'],
    python_requires='==3.7.*',
    entry_points={
        "console_scripts": [
            "cmip = biobb_cmip.cmip.cmip:main",
            "titration = biobb_cmip.cmip.titration:main",
            "prepare_structure = biobb_cmip.cmip.prepare_structure:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
    ],
)
