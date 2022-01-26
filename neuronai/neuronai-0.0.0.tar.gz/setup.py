from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.0'
DESCRIPTION = 'Neuron AI implementations and designs'
LONG_DESCRIPTION = 'Neuron AI implementations and designs'

# Setting up
setup(
    name="neuronai",
    version=VERSION,
    author="Neuron AI",
    author_email="user@example.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'AI', 'ML', 'machine learning', 'neuronai', 'neuron-ai', 'easyneuron', 'easyNeuron'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)