from setuptools import setup, find_packages
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='simpfast',
  version='0.0.1',
  description='A simple liberary to use fastai in easy way',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Israr Ahmad',
  author_email='israrbuaa@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords='', 
  packages=find_packages(),
  install_requires=[''] 
)