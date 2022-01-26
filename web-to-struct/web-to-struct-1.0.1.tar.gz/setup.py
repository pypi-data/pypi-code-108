from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="web-to-struct",
    version="1.0.1",
    description="A tool for data structuring, mainly for web data.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/BD777/web-to-struct",
    author="BD777",
    author_email="mis_tletoe@foxmail.com",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.6, <4",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "bs4",
    ]
)
