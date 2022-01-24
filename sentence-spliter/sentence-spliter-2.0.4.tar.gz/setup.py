import setuptools
from setuptools import setup, find_packages

setup(
    name="sentence-spliter",
    version="2.0.4",
    author="jianwei zhao",
    author_email="zhaojianwei@163.com",
    description="This is a sentence cutting tool, currently support English & Chinese",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    # package_dir={"":"sentence_spliter"},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    REQUIRES_PYTHON='>=3.6.0',
    install_requires=['attrd==0.0.3', 'attrdict==2.0.1', 'attrs==19.3.0', 'importlib-metadata==1.6.0', 'loguru==0.5.3',
                      'more-itertools==8.2.0', 'packaging==20.3', 'pluggy==0.13.1', 'py==1.8.1', 'pyparsing==2.4.7',
                      'pytest==5.4.1', 'six==1.14.0', 'wcwidth==0.1.9', 'zipp==3.1.0',
                      ]
)
