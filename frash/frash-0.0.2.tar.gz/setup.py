import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="frash",
    version="0.0.2",
    description="Juggling with hex",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/0xflotus/frash",
    author="0xflotus",
    author_email="0xflotus+pypi@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["frash"],
    include_package_data=True,
    install_requires=["argparse"],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [
            'frash=frash.__main__:main'
        ]
    }
)

