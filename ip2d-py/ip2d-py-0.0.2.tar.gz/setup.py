import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="ip2d-py",
    version="0.0.2",
    description="Convert IP addresses to integers on cli",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/0xflotus/ip2d-py",
    author="0xflotus",
    author_email="0xflotus+pypi@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["ip2d-py"],
    include_package_data=True,
    install_requires=["ipy2d==0.0.6", "argparse"],
)
