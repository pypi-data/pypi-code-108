from distutils.core import setup
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_descript = fh.read()
setup(
  name = "heisenbug",
  packages = ["heisenbug"],
  version = "0.0.1",
  license="",      
  description="Hello Quantum!",
  long_description=long_descript,
  long_description_content_type=" text/markdown",
  author="heisenbug.co",                 
  author_email="heisenbugco@gmail.com",
  url="https://github.com/heisenbugco/heisenbug",
  download_url="https://github.com/heisenbugco/heisenbug/archive/v_001.tar.gz", 
  keywords=["quantum", "machine", "learning"], 
  # install_requires=[],
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
	"Programming Language :: Python :: 3.7",
	"Programming Language :: Python :: 3.8",
	"Programming Language :: Python :: 3.9",
  ],
  
)
