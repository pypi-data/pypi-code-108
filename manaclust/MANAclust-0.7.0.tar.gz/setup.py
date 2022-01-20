
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read()

setuptools.setup(
     name='MANAclust',  
     version='0.7.0',
     author="Scott Tyler",
     author_email="scottyler89@gmail.com",
     description="Multi Affinity Network Association",
     long_description=long_description,
     long_description_content_type="text/markdown",
     install_requires = install_requires,
     url="https://scottyler892@bitbucket.org/scottyler892/manaclust",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU Affero General Public License v3",
         "Operating System :: OS Independent",
     ],
 )
