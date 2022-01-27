"""
abserdes
A Basic Serializer and Deserializer that makes XML serialization and
deserialization in Python absurdly easy.
"""

import sys
import os
from setuptools import setup, find_packages, Extension


setup(
    name='abserdes',
    author='Andy Stokely',
    author_email='amstokely@ucsd.edu',
    license='MIT',
    description="A Basic Serializer and Deserializer that makes XML"
        + "serialization and deserialization in Python absurdly easy.",
    keywords='xml, serialize, deserialize, serializer',
    url='https://github.com/astokely/abserdes',
    packages=find_packages(),
    install_requires=[
		"numpy", "pytest", 
		"data-science-types", "cython"
	],              
    platforms=['Linux',
                'Unix',],
    python_requires=">=3.8",          
)
