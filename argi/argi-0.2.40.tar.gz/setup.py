import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='argi',  
     version='0.2.40',
     author="Sergio Iglesias",
     author_email="trakuo@gmail.com",
     description="graph dimension reduction using timeseries",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/trakuo/argi",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
