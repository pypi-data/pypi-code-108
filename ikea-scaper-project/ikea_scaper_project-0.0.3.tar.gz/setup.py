from setuptools import setup
from setuptools import find_packages

setup(
    name='ikea_scaper_project',
    version='0.0.3', 
    description='Package that allows you to scape data samples from the Ikea website',
    url='https://github.com/IvanYingX/Ikea-Scraper-Project', 
    author='Darrel Anderson, Euan Wrigglesworth, Regina Aiken', 
    license= 'Public Domain Dedication (CC Zero)',
    packages=find_packages(), 
    install_requires=['requests',
    'selenium>=4',
    'typing>=3',
    'time>=3',
    'boto3>=1',
    'json>=3',
    'tkinter>=3',
    'pandas>=1',
    'uuid>=3',
    'urllib>=1',
    'tqdm>=4',
    'tempfile>=3',
    'urllib>=1',
    'unittest>=3',
    'sqlalchemy>=1'
    ],
)
