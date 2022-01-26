from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding='utf-8') as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.3"

setup(
    name="ml-solutions",
    version=VERSION,
    author="Debadrito Dutta",
    author_email="dipalidutta312@gmail.com",
    description='A Python Pacakage for Ready Made Machine Learning Solutions.',
    packages=find_packages(),
    install_requires=["pandas", "sklearn", "numpy", "tensorflow", "opencv-python", "torch"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["ml-solutions", "Machine Learning", "machine learning", "machine learning python", "image python", "image"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)