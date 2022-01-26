from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='skepeUtilities',
  version='0.0.1',
  description='A basic library for basic stuff',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Benjamin Joensen',
  author_email='businessskepe@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='random', 
  packages=find_packages(),
  install_requires=['']
)
