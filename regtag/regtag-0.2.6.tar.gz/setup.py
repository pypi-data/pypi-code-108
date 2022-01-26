import pathlib
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="regtag",
    version="0.2.6",
    description="Regex Tagging",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nguyenvulebinh/regtag",
    author="Binh Nguyen",
    author_email="nguyenvulebinh@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["regtag"],
    package_dir={"": "src"},   # tell distutils packages are under src
    include_package_data=True,
    install_requires=["nltk>=3.6.5"],
    package_data={
        # If any package contains *.txt files, include them:
        "": ["*.txt"],
        # And include any *.dat files found in the "data" subdirectory
        # of the "mypkg" package, also:
        "regtag": ["vidict.txt", 'abb_dict.json', 'oov_datasets.json'],
    }
    # entry_points={
    #     "console_scripts": [
    #         "realpython=visen.__main__:main",
    #     ]
    # },

)