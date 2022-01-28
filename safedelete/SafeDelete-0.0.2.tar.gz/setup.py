'''
Author: Cheryl Li
Date: 2022-01-28 14:17:54
LastEditTime: 2022-01-28 15:06:23
FilePath: /undefined/Users/licheryl/Desktop/test/setup.py
'''
import setuptools
setuptools.setup(
    name="SafeDelete",
    version="0.0.2",
    author="cheryl",
    author_email="cheryllee626@gmail.com",
    description="A small package for delecting files safely",
    url="https://github.com/cherylLbt/SafeDelete.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
     install_requires=[
        'datetime',
        'pytest-shutil'
    ],
)