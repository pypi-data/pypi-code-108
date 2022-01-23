from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='randomCoordinates',
  version='0.1.7',
  description='A very basic Random Coordinates Generator',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='scruffysnake',
  author_email='scruffysnake@scruffysnake.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='RNG', 
  packages=find_packages(),
  install_requires=[''] 
)
