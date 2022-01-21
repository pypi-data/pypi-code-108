'''
Created on 12 Jul 2021

@author: -
'''

from setuptools import setup

with open("README.md", "r") as fh:
    description = fh.read()
    
setup(
    name="pyserialgateway",
    version="1.3.18",
    author="ljyee",
    author_email="joeyee@senatraffic.com.my",
    packages=["pyserialgateway"],
    include_package_data=True,
    description="Classes dedicated for multi-functioned processes which includes DB, mapping, data and connection capabilities.",
#     long_description=description,
#     long_description_content_type='text/markdown',
    url='https://github.com/joeyee-senatraffic/pyserialgateway.git',
    license='MIT',
    python_requires='>=3.5',
    install_requires=[
        'pyserial>=3.5',
        'psycopg2>=2.8.5',
        'pykml>=0.2.0',
        'psutil>=5.6.7'
    ]
)