print('This is N1Ez\'s setup.py file.')

import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="example-pkg-n1ez",
  version="0.0.2",
  author="N1Ez",
  author_email="N1Ez@163.com",
  description="A small example package, it\'s own N1Ez.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)