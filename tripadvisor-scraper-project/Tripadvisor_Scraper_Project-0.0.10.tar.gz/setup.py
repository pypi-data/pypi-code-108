from setuptools import setup
from setuptools import find_packages

setup(
    name='Tripadvisor_Scraper_Project',
    version='0.0.10',
    description='Mock package that scrap data of hotels from Tripadvisor',
    #url='https://github.com/IvanYingX/Tripadvisor-Scraper-Project',
    author='dhaval, luqman, aicore',
    license='MIT',
    packages=find_packages(),
    install_requires=['selenium','sqlalchemy','tqdm','pandas','webdriver_manager'],


)