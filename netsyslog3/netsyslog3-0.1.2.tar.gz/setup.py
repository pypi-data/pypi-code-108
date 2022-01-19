# Copyright (C) 2005 Graham Ashton <ashtong@users.sourceforge.net>
#
# $Id: setup.py,v 1.3 2006/02/13 01:53:56 ashtong Exp $

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setuptools.setup(py_modules=["netsyslog3"],
          name="netsyslog3",
          version="0.1.2",
          author="Graham Ashton",
          author_email="ashtong@users.sourceforge.net",
          url="https://github.com/ptrktn/python-netsyslog3",
          description="Send log messages to remote syslog servers",
          long_description=long_description,
          project_urls={
              "Bug Tracker": "https://github.com/ptrktn/python-netsyslog3/issues",
          },
          classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
          package_dir={"": "src"},
          packages=setuptools.find_packages(where="src"),
          python_requires=">=3.6",
          )
