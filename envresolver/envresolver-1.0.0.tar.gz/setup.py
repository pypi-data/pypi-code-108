from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name="envresolver",
  packages=["envresolver"],
  version="1.0.0",
  license="apache-2.0",
  description="Pythonic parsing of environment variables",
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="Joni Lepistö",
  author_email="joni.m.lepisto@gmail.com",
  url="https://github.com/jjstoo/envresolver",
  download_url="https://github.com/jjstoo/envresolver/releases",
  keywords=["environment", "variable", "variables", "shell", "parsing"],
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
  ],
)
