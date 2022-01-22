import setuptools
from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name="pyfiji",

    version='1.0.0',

    author='Varun Kapoor',
    author_email='randomaccessiblekapoor@gmail.com',
    url='https://github.com/kapoorlab/pyfiji/',
    description='Python scripts as precursor to Fiji plugins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        
        "pandas",
        "numpy",
        "scipy",
        "tifffile",
        "matplotlib",
        "opencv-python"
       
    ],
 
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
    ],
)
