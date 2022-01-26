"""Setup file"""
from setuptools import setup  # type: ignore

VERSION = "0.1.5"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="fnv1a",
      packages=["fnv1a"],
      version=VERSION,
      description="64 bit Fnv-1a hash module",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="plasticuproject",
      author_email="plasticuproject@pm.me",
      url="https://github.com/plasticuproject/fnv1a",
      download_url=("https://github.com/plasticuproject/fnv1a/archive/v" +
                    VERSION + ".tar.gz"),
      keywords=["fnv", "fnv1a", "64 bit", "hash"],
      classifiers=[
          "Development Status :: 4 - Beta", "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3", "Topic :: Utilities"
      ],
      license="MIT",
      zip_safe=False,
      include_package_data=True)
