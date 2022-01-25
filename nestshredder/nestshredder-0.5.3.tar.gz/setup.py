from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='nestshredder',
   version='0.5.3',
   license='MIT',
   description='A useful thing that will take nested JSONS and output something a touch more SQL-sensible',
   long_description_content_type='text/markdown',
   long_description=long_description,
   author='Chris Woodward',
   author_email='chriswoodward77@googlemail.com',
   packages=['nestshredder'],  
   install_requires=['pandas','pyarrow'],
   url='https://github.com/Gadz00ks77/nestshredder/',
   download_url='https://github.com/Gadz00ks77/nestshredder/archive/refs/tags/v0.5.3.tar.gz'
)