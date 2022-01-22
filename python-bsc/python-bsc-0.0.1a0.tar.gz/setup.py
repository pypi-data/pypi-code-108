from distutils.core import setup
from setuptools import find_packages
from setuptools import setup
import bsc.__init__

with open('requirements.txt') as req:
    requirements = list(filter(None, req.read().split('\n')))

version = bsc.__init__.__version__
setup(
    name='python-bsc',
    packages=['bsc'],
    version='0.0.1alpha',
    license='MIT',
    description='A python based balanced scorecard implementation for managing objectives, tracking KPIs and improving organisation performance',
    author='Carl du Plessis',
    author_email='',
    url='https://github.com/PandaCarl/python-bsc',  #
    download_url='https://github.com/PandaCarl/python-bsc/archive/refs/tags/1.0.0-alpha.tar.gz',
    keywords=['Balanced Scorecard', "KPI's", 'Performance management'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3'
    ],
)
