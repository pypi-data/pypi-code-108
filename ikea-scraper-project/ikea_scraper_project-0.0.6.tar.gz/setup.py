from setuptools import setup
from setuptools import find_packages

setup(
    name='ikea_scraper_project',
    version='0.0.6', 
    description='Package that allows you to scape data samples from the Ikea website',
    url='https://github.com/IvanYingX/Ikea-Scraper-Project', 
    author='Darrel Anderson, Euan Wrigglesworth, Regina Aiken', 
    license= 'Public Domain Dedication (CC Zero)',
    packages=find_packages(), 
    install_requires=['requests',
    'selenium>=4',
    'typing>=3',
    'boto3>=1',
    'pandas>=1',
    'urllib3>=1',
    'tqdm>=4',
    'urllib3>=1',
    'sqlalchemy>=1'],
    )