import setuptools

__version__ = '1.5.10'

with open("README.md", "r") as fh:
    readme = fh.read()

requirements = [
    "matplotlib",
    "numpy",
    "tifffile",
    "scikit-image>=0.15.0",
    "aicsimageio==3.0.7",
    "quilt3",
    "bumpversion",
    "twine",
    "setuptools>=42",
    "wheel",
    "pandas",
    "multipledispatch"
]


setuptools.setup(
    author="Lion Ben Nedava",
    author_email="lionben89@gmail.com",
    install_requires=requirements,
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="cell_imaging_utils",
    name="cell_imaging_utils",
    packages=setuptools.find_packages(exclude=["images"]),
    python_requires=">=3.6",
    test_suite="tests",
    url="https://github.com/lionben89/BGU_cell_imaging_utils",
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version=__version__,
    zip_safe=False
)
