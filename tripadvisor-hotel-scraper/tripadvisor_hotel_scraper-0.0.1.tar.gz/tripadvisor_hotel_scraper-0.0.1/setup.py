from setuptools import setup
from setuptools import find_packages

setup(
    name='tripadvisor_hotel_scraper',
    version='0.0.1',
    description='Mock package that scrap data of hotels from Tripadvisor',
    url='https://github.com/IvanYingX/Tripadvisor-Scraper-Project',
    author='dhaval_luqman_aicore',
    license='MIT',
    packages=find_packages(),
    install_requires=['selenium','sqlalchemy','tqdm','pandas','webdriver_manager'],




)