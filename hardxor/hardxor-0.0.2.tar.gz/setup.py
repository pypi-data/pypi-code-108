import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="hardxor",
    version="0.0.2",
    description="Xor any file byte by byte",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/0xflotus/hardxor",
    author="0xflotus",
    author_email="0xflotus+pypi@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["hardxor"],
    include_package_data=True,
    install_requires=["argparse"],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [
            'hardxor=hardxor.__main__:main'
        ]
    }
)

