from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='ftpx',  # Required
    version="0.0.0",  # Required
    author="Paulo Sergio dos Santo Junior",
    author_email="paulossjuniort@gmail.com",
    description="A lib with basic operations of FTP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/integration_seon/libs/util/ftpx",
    packages=find_packages(),
    
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    setup_requires=['wheel'],
    
)
