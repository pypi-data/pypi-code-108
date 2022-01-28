from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.5'
DESCRIPTION = 'DIRAI API'


# Setting up
setup(
    name="dirai",
    version=VERSION,
    author="SOMMA Investimentos",
    author_email="<vitor.alves@sommainvestimentos.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['pymysql', 'cryptography', 'pandas'],
    keywords=['python', 'dirai'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)